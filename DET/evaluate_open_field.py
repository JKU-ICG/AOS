import os
import cv2
import numpy as np
import json
import pandas as pd
from numbers import Number
import sys
import glob

yolo_path = os.environ.get('YOLO_PATH')
if yolo_path is None:
    print( 'SET YOLO PATH!' )
# BB evaluation
print(yolo_path)
#if not os.path.join(yolo_path) in sys.path:
sys.path.insert(1, os.path.join(yolo_path))
sys.path.insert(1, os.path.join(yolo_path,'lib', 'metrics'))
print(sys.path)
#from darknet_images import add_detections_to_BBs
import darknet 
from lib.metrics.BoundingBox import  *
from lib.metrics.BoundingBoxes import *
from lib.metrics.utils import *
from lib.metrics.Evaluator import *

from site_util import getSiteInfo


def ReadJsonPosesFiles(PosesFilePath):
        with open(PosesFilePath) as PoseFile:
            PoseFileData = json.load(PoseFile)
            NoofPoses = len(PoseFileData['images'])
            PoseFileImagesData = PoseFileData['images']
            HalfValue = int(round(len(PoseFileData['images'])/2))
            center_camera = None
            #print('HalfValue',HalfValue)
            if len(PoseFileData['images']) > 0:
                for i in range (0,len(PoseFileData['images'])):
                    ImageName = PoseFileImagesData[i]['imagefile']
                    #Convert List of List to Np array
                    PoseMatrix = PoseFileImagesData[i]['M3x4']
                    PoseMatrixNumpyArray = np.array([], dtype=np.double)
                    for k in range(0,len(PoseMatrix)):
                        PoseMatrixNumpyArray = np.append(PoseMatrixNumpyArray, np.asarray(PoseMatrix[k],dtype=np.double))
                    ViewMatrixArray = PoseMatrixNumpyArray
                    ViewMatrixArrayfrompy = ViewMatrixArray
                    ViewMatrixArrayfrompy = np.reshape(ViewMatrixArrayfrompy,(3,4))
                    ViewMatrixArrayfrompy = np.vstack((ViewMatrixArrayfrompy, np.array([0.0,0.0,0.0,1.0])))
                    InverseViewMatrix = np.linalg.inv(ViewMatrixArrayfrompy)                  
                    if ( i == HalfValue):
                        print('AddingCameraValue')
                        center_camera = {   
                                'pos': (InverseViewMatrix[0][3], InverseViewMatrix[1][3], InverseViewMatrix[2][3]),
                                'up': (ViewMatrixArrayfrompy[1][0], ViewMatrixArrayfrompy[1][1], ViewMatrixArrayfrompy[1][2]),
                                'left': (ViewMatrixArrayfrompy[0][0], ViewMatrixArrayfrompy[0][1], ViewMatrixArrayfrompy[0][2]),
                                'forward': (ViewMatrixArrayfrompy[2][0], ViewMatrixArrayfrompy[2][1], ViewMatrixArrayfrompy[2][2]),
                                'matrix': ViewMatrixArrayfrompy,
                            }
        return PosesFilePath, center_camera, HalfValue

def prepareDarknetFiles( aug, yoloversion, trainversion="vL.56/APall" ):
    # todo relative!!
    yolo_path = os.getenv( 'yolo_path' )
    if yolo_path is None: # Indrajit's computer?
        yolo_path = "D:/RESILIO/darknet_AlexeyAB_synced/"

    cfgfile =  os.path.join( yolo_path, "cfg", yoloversion+"-NAOS.cfg" )
    datafile = os.path.join( yolo_path, "data/NAOS/vL.0/NAOS-vL.0-noAHE.data" )
    weightsfolder = os.path.join( yolo_path, "weights/NAOS", trainversion, yoloversion, aug ) # open-field is included in training set
    #weightsfolder = os.path.join( "D:/RESILIO/darknet_AlexeyAB_synced/weights/NAOS/vL.2noTest/APall", yoloversion, aug ) # NO open-field dataset in training set
    filename = None
    for file in os.listdir(os.path.join( weightsfolder )):
        if file.endswith(".weights"):
            filename = file
    assert filename, "weightsfile empty"
    weightsfile = os.path.join( weightsfolder, filename )

    return weightsfile, cfgfile, datafile

def image_detection(image, network, class_names, class_colors, thresh, hier_thresh=.5, nms_thresh=.25):
    # Darknet doesn't accept numpy images.
    # Create one with image we reuse for each detect
    width = darknet.network_width(network)
    height = darknet.network_height(network)
    darknet_image = darknet.make_image(width, height, 3)

    #image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_resized = cv2.resize(image_rgb, (width, height),
                               interpolation=cv2.INTER_LINEAR)

    darknet.copy_image_from_bytes(darknet_image, image_resized.tobytes())
    detections = darknet.detect_image(network, class_names, darknet_image, thresh=thresh, hier_thresh=hier_thresh, nms=nms_thresh)
    image = darknet.draw_boxes(detections, image_resized, class_colors)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB), detections

def add_gt_to_BBs(bbs, image_name, tl, br ):
    bb = BoundingBox(
                image_name,
                'person',
                tl[0], tl[1], br[0], br[1],
                CoordinatesType.Absolute,
                bbType=BBType.GroundTruth,
                format=BBFormat.XYX2Y2)
    bbs.addBoundingBox(bb)
    return bbs

def load_gt_to_BBs(bbs, image_name, image_path, image_size ):
    
    #print( "IMAGE path: " + image_path )
    file_name = os.path.splitext(image_path)[0] + ".txt"
    #print( "LABEL path: " + file_name )
    with open(file_name, "r") as f:
        for line in f:
            line = line.replace("\n", "")
            if line.replace(' ', '') == '':
                continue
            splitLine = line.split(" ")
            idClass = int(splitLine[0])  # class
            assert( idClass == 0 )
            cx = float(splitLine[1])  # coordinates (relative)
            cy = float(splitLine[2])
            w = float(splitLine[3])
            h = float(splitLine[4])
            bb = BoundingBox(
                image_name,
                'person',
                cx, cy, w, h,
                CoordinatesType.Relative, (image_size[0], image_size[1]),
                BBType.GroundTruth,
                format=BBFormat.XYWH)
            bbs.addBoundingBox(bb)

    return bbs

def add_detections_to_BBs(bbs, image_name, detections, flip_x=False):
    
    for label, confidence, bbox in detections:
        x, y, w, h = darknet.bbox2points( bbox ) # converts to absolut left, top, right, bottom
        if flip_x:
            w,x = 512-x,512-w
        bb = BoundingBox(image_name,label,
            x,y,w,h,
            CoordinatesType.Absolute, 
            bbType=BBType.Detected, 
            format=BBFormat.XYX2Y2,
            classConfidence=float(confidence)/100.0) # input confidence in the range 0 to 1
        bbs.addBoundingBox(bb)

    return bbs

def projection_matrix( flip_images=False ):
    new_size = (512,512)
    f_factor = .95
    px = new_size[0]/2.0
    py = new_size[1]/2.0
    fx = new_size[0]/f_factor
    fy = new_size[1]/f_factor

    # projection matrix:
    if flip_images:
        new_K = np.array( [
                [fx, 0,  px, 0], 
                [0, fy, py, 0],
                [0, 0, 1.0, 0],
                [0, 0,   0, 1]
            ] )
    else:
        new_K = np.array( [
                [-fx, 0,  px, 0], # x needs to be flipped!
                [0, fy, py, 0],
                [0, 0, 1.0, 0],
                [0, 0,   0, 1]
            ] )

    return new_K

def putBBText( img, min_coord, max_coord, text, fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=1.5, color=(0,0,0), thickness=2 ):
    x,y = min_coord[0],min_coord[1]-10
    if y > 50 : # place text on top of BB
        pass
    else: #place text on bottom
        x,y = min_coord[0], max_coord[1] + round(25*fontScale)

    cv2.putText(img, text, (x,y),  fontFace, fontScale, color=color, thickness=thickness )
    return img



def evaluate_site( sitename, fp_threshold = .05, ap_threshold = 0.0001, iou_threshold=0.25, show_results=True, use_simulation=True, write_results=True, flip_images=True, 
        label_color=(0,0,0), border_color=(255,255,255), fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=1.5, fontThickness=2, add_scale_bar=True, show_confidence=False ):
    lbl_stats = {}
    lbl_found = {}
    try:
        lbl_map = getSiteInfo(sitename)['lbl_map'] # maps from our labels I,K,A, ... to anyonymous labels A,B,C,D...
    except:
        lbl_map = {} # we cannot use a predefined label map, so we use our own!
        anonymous_lbl = ord('A')


    lbl_count = 0
    tp_count = 0
    fp_count = 0
    ip_count = 0 #incorrect person
    cp_count = 0 #correct person (differs from tp, because we consider a detection in any gt BB to be correct; so multiple detections of the same GT are allowed!)

    #sitename = 'Test20201020F1'
    anaos_path = os.environ.get('ANAOS_DATA')
    print(os.path.join(anaos_path, 'SITES', sitename, 'Pose_absolute'))
    #PosesFilePath = '../data/T20200207F2/thermal_GPS_Corr_30.json'
    #ImageLocation = '../data/T20200207F2/thermal_hdr512'
    #ObjModelPath = '../data/T20200207F2/dem.obj'
    #ObjModelImagePath = '../data/T20200207F2/dem.png'
    PosesFilePath = os.path.join(anaos_path, 'SITES', sitename, 'Pose_absolute')
    LabelFilePath = os.path.join(anaos_path, 'SITES', sitename, 'Labels')
    LabeledImagePath = os.path.join(anaos_path, 'SITES', sitename, 'LabeledImages')
    ImageLocation = os.path.join(anaos_path, 'SITES', sitename, 'Image')
    ObjModelPath = os.path.join(anaos_path, 'SITES', sitename, 'LFR','dem.obj')
    ObjModelImagePath = os.path.join(anaos_path, 'SITES', sitename, 'LFR','dem.png')
    SaveImagePath = os.path.join(anaos_path, 'SITES', sitename, 'Pose_Rendered_Images')
    SaveProjImagePath = os.path.join(anaos_path, 'SITES', sitename, 'ProjectedImages')
    ResultsFolder = os.path.join( anaos_path, 'SITES', sitename, 'EvaluationResults' )
    CloseupsFolder = os.path.join( ResultsFolder, 'Closeups' )
    dem_info_path = os.path.join(anaos_path, 'SITES', sitename, 'NewNormalization','SimulationPoses_CPURenderedImages')


    if use_simulation:
        SaveImagePath = os.path.join(anaos_path, 'SITES', sitename, 'NewNormalization', 'RenderedResults' )
        PosesFilePath = os.path.join(anaos_path, 'SITES', sitename, 'NewNormalization', 'SimulationPoses' )
        count_images = 0

    if write_results and not os.path.isdir(ResultsFolder):
        os.mkdir( ResultsFolder )
    if write_results and not os.path.isdir(CloseupsFolder):
        os.mkdir( CloseupsFolder )


    new_K = projection_matrix(flip_images)
    closeup_size = (56,56)
    closeup_scale = 3
    closeup_border = 3 # pixels

    img = None
    image_count = 0

    bbs_to_evaluate = BoundingBoxes()

    scene_poses = { 'images': [] }

    for i in range(99):

        PathsIdentifier = i #[4,*range(6, 19, 1)] # make this better!!!
        image_name = 'Site{}_Line{}'.format(sitename,PathsIdentifier)

        pose_file = os.path.join( PosesFilePath, "{}.json".format(PathsIdentifier))
        if not os.path.isfile(pose_file):
            continue # skip the rest of the loop!
        poses, center_cam, center_id = ReadJsonPosesFiles(pose_file)
        image_count = image_count + 1

        

        cam = center_cam.copy()
        cam['matrix'] = cam['matrix'].tolist()
        K = new_K.tolist()
        results = { 'K': K, 'camera': cam, 'detections':[], 'gt_labels':[] }

        dem_cam = center_cam.copy()
        dem_cam['pos'] = (0,0,dem_cam['pos'][2]-250)
        dem_cam['up'] = (0,1,0)
        #dem_cam['forwad'] = (0,0,1)
        dem_cam['matrix'] = np.eye(4,4) # rotation matrix is eye matrix for our case!!
        inv_dem_matrix = np.linalg.inv(dem_cam['matrix'] )
        inv_dem_matrix[0][3],inv_dem_matrix[1][3],inv_dem_matrix[2][3] = dem_cam['pos'][0],dem_cam['pos'][1],dem_cam['pos'][2]
        dem_cam['matrix'] = np.linalg.inv(inv_dem_matrix)

        if use_simulation:
            img_file = os.path.join( SaveImagePath, "{}.png".format(count_images) )
            count_images += 1
        else:
            img_file = os.path.join( SaveImagePath, "{}.png".format(PathsIdentifier) )


        label_file = os.path.join( LabelFilePath, "Label{}.json".format(PathsIdentifier) )
        with open(label_file) as labels_fid:
            labels = json.load(labels_fid)
            if labels:
                labels = labels['Labels']
        #print(labels)

        #print(center_cam)

        img = cv2.imread( img_file, cv2.IMREAD_COLOR )

        # read raw file:
        #img_raw_file = os.path.join( SaveImagePath, "{}.raw.npy".format(PathsIdentifier) )
        #img_raw = np.load( img_raw_file )
        #img = img_raw

        # run inference with yolo!
        dimg, detections = image_detection( img, network, class_names, class_colors, ap_threshold, nms_thresh=iou_threshold )
        #cv2.imshow( 'Line {}'.format(PathsIdentifier), dimg ) 

        if flip_images:
            img = cv2.flip(img, 1) # flip image left right!
            digm = cv2.flip(dimg,1)

        oimg = img.copy()
        if write_results: # write original image
            cv2.imwrite( os.path.join(ResultsFolder, "{}.png".format(PathsIdentifier)), img ) 

        
        add_detections_to_BBs(bbs_to_evaluate, image_name, detections, flip_images)

        # check if a label is in the detections
        det_bbs = bbs_to_evaluate.getBoundingBoxesByImageName(image_name)

        # filter to only contain detections above a threshold:
        det_bbs = [ bb for bb in det_bbs if bb.getBBType() == BBType.Detected and bb.getConfidence() >= fp_threshold ]
        fp_count += len(det_bbs) # assume that every detection is a false positive!
        ip_count += len(det_bbs)

        # detections:
        for bb in det_bbs:
            x,y,x2,y2= bb.getAbsoluteBoundingBox(format=BBFormat.XYX2Y2)
            cv2.rectangle( img, (x,y), (x2,y2), fp_color, thickness=3 )
            if show_confidence:
                cv2.putText(img, "{:5.2f}".format(bb.getConfidence()*100), (x,y2), cv2.FONT_HERSHEY_PLAIN, 2, color=text_color, thickness=2 )


        if add_scale_bar and image_count==1: # add a scale bar to the first image!
            dem_info = np.load(os.path.join(dem_info_path,"{}_xyz.npy".format(PathsIdentifier)))
            dem_info = np.flip(dem_info,1)
            dem_pts = dem_info[dem_info.shape[0]-10,10:12,:] # corner point
            dem_vect = dem_info[dem_info.shape[0]-10,-1] - dem_pts[0,:]
            dem_vect = dem_vect / np.linalg.norm(dem_vect) * 10 # meters
            print(dem_pts)
            dem_pts[1,:] = dem_pts[0,:]+dem_vect
            #print(dem_pts)
            #print(dem_pts.shape)
            pts = np.zeros( (dem_pts.shape[0],2), np.int32)
            print(dem_pts)
            for i_pt in range(dem_pts.shape[0]):
                pt_ = np.matmul( new_K, np.matmul( center_cam['matrix'], dem_pts[i_pt,:] ) )
                pt_ = pt_[0:2] / pt_[2]
                pts[i_pt,:] = pt_[0:2]
            #print(pts)
            #print(len(pts))
            print(pts.shape)
            cv2.polylines( img, [pts], True, color=border_color, thickness=fontThickness )
            cv2.putText( img, "10m", tuple(pts[0,:]-[5,10]),  fontFace, fontScale, color=border_color, thickness=int(fontThickness) )

        
        # gt lables
        for lbl in labels:
            pts = []
            for pt in lbl['polyDEM']:
                pt_ = [*pt, 1.0]
                #view_space = np.matmul( center_cam['matrix'] , pt_ )
                projected_points = np.matmul( new_K, np.matmul( center_cam['matrix'] , pt_ ) )
                projected_points = projected_points / projected_points[2]
                #print(projected_points)
                pts.append(projected_points)

            min_coord = np.rint(np.min(pts,axis=0)).astype(int)
            max_coord = np.rint(np.max(pts,axis=0)).astype(int)
            

            if lbl["Label"].upper() in lbl_stats.keys():
                lbl_stats[lbl["Label"].upper()] += 1
            else: # otherwise add it
                lbl_stats[lbl["Label"].upper()] = 1
            if not lbl["Label"].upper() in lbl_map.keys():
                lbl_map[lbl["Label"].upper()] = chr(anonymous_lbl)
                anonymous_lbl += 1
            lbl_count += 1

            gt_bb = BoundingBox(
                        image_name,
                        'person',
                        min_coord[0], min_coord[1], max_coord[0], max_coord[1],
                        CoordinatesType.Absolute,
                        bbType=BBType.GroundTruth,
                        format=BBFormat.XYX2Y2)
            gt_bb_found = False
            x,y,x2,y2= gt_bb.getAbsoluteBoundingBox(format=BBFormat.XYX2Y2)
            results["gt_labels"].append( {'XYX2Y2': (int(x),int(y),int(x2),int(y2)), 'label':lbl["Label"].upper() } )

            #extract closeup
            cx = np.amax([int((x+x2)/2 - closeup_size[0]/2),0])
            cy = np.amax([int((y+y2)/2 - closeup_size[1]/2),0])
            cx = cx if cx+closeup_size[1] < oimg.shape[1] else oimg.shape[1]-closeup_size[1]
            cy = cy if cy+closeup_size[0] < oimg.shape[0] else oimg.shape[0]-closeup_size[0]

            closeup = oimg[cy:cy+closeup_size[1],cx:cx+closeup_size[0],:]
            #closeup = cv2.normalize(closeup, None, norm_type=cv2.NORM_MINMAX )
            closeup = cv2.resize(closeup, tuple([z * closeup_scale for z in closeup_size]) )
            #print(cx,cy)
            cv2.putText(closeup, "{}".format(lbl_map[lbl["Label"].upper()]), (10,40),  fontFace, fontScale, color=text_color, thickness=int(fontThickness) )
            if closeup_border > 0:
                closeup = cv2.copyMakeBorder( closeup, closeup_border, closeup_border, closeup_border, closeup_border, cv2.BORDER_CONSTANT, value=border_color )

            cv2.imwrite( os.path.join(CloseupsFolder,"{}_{}.png".format(PathsIdentifier,lbl_map[lbl["Label"].upper()])),closeup)

            cv2.rectangle( img, (x,y), (x2,y2), boundingbox_color, thickness=3 )

            ious = Evaluator._getAllIOUs(gt_bb, det_bbs)
            ious = sorted(ious, key=lambda i: i[2].getConfidence(), reverse=True)  # sort by confidence (from highest to lowest)
            assert( len(det_bbs) == len(ious) )

            for iou in ious:
                x,y,x2,y2= iou[2].getAbsoluteBoundingBox(format=BBFormat.XYX2Y2)
                # iou has the format iou, gt, det
                if iou[2].getConfidence() >= fp_threshold:
                    if iou[0] >= iou_threshold and not gt_bb_found:
                        # label got found!
                        #print( "{} in image {} found!".format( lbl["Label"], image_name ) )
                        if lbl["Label"].upper() in lbl_found.keys(): # if label was detected already before
                            lbl_found[lbl["Label"].upper()] += 1
                        else: # otherwise add a new dection starting with 1
                            lbl_found[lbl["Label"].upper()] = 1
                        tp_count += 1
                        fp_count -= 1
                        cp_count += 1
                        ip_count -= 1
                        gt_bb_found = True # only count once as true positive!
                        x,y,x2,y2= iou[2].getAbsoluteBoundingBox(format=BBFormat.XYX2Y2)
                        cv2.rectangle( img, (x,y), (x2,y2), tp_color, thickness=3 )

                        results["detections"].append( {'XYX2Y2': (int(x),int(y),int(x2),int(y2)), 'conf': iou[2].getConfidence(), 'isTP':True, 'closeToLabel':lbl["Label"].upper() } )
                    elif iou[0] >= iou_threshold :
                        results["detections"].append( {'XYX2Y2': (int(x),int(y),int(x2),int(y2)), 'conf': iou[2].getConfidence(), 'isTP':False, 'closeToLabel':lbl["Label"].upper()  } )
                        cv2.rectangle( img, (x,y), (x2,y2), tp_color, thickness=3 )
                        cp_count += 1
                        ip_count -= 1
                    else:
                        results["detections"].append( {'XYX2Y2': (int(x),int(y),int(x2),int(y2)), 'conf': iou[2].getConfidence(), 'isTP':False, 'closeToLabel':""  } )
                        #cv2.rectangle( img, (x,y), (x2,y2), fp_color, thickness=3 )
                        #pass
                else:
                    raise "this should never happen!"



            # add to GT to evaluator
            add_gt_to_BBs(bbs_to_evaluate, image_name, min_coord, max_coord )

            # put label text last so it is on top!
            putBBText( img, min_coord, max_coord, "{}".format(lbl_map[lbl["Label"].upper()]), fontFace, fontScale, color=text_color, thickness=fontThickness )
            #cv2.putText(img, "{}".format(lbl_map[lbl["Label"].upper()]), (x,y-10),  fontFace, fontScale, color=text_color, thickness=fontThickness )

        # place a label with the image number in the corner
        cv2.putText(img, "{}".format(image_count), (10,40), fontFace, fontScale, color=border_color,  thickness=fontThickness )
        
        if show_results:
            cv2.imshow( image_name, img ) 

        if write_results:
            cv2.imwrite( os.path.join(ResultsFolder, "Detections{}.png".format(PathsIdentifier)), img ) 
            with open( os.path.join(ResultsFolder,"Detections{}.json".format(PathsIdentifier)), 'w' ) as det_file:
                json.dump( results, det_file )

        scene_poses['images'].append( {'imagefile':"{}.png".format(PathsIdentifier),
                "M3x4": center_cam['matrix'][0:3,:].tolist() })

    if write_results:
        with open( os.path.join(ResultsFolder,"centerPoses.json"), 'w' ) as pose_file:
            json.dump( scene_poses, pose_file )
    


    print( "Persons: {} (total {})".format(lbl_stats,len(lbl_stats)) )
    print( "How often Found: {} (missed {})".format(lbl_found,len(lbl_stats)-len(lbl_found)) )
    print( "#Persons (labels): ", len(lbl_stats.keys()) )
    print( "Total Labels: ", lbl_count )
    print( "TPs: ", tp_count )
    print( "FPs: ", fp_count )
    #print(lbl_map)


    evaluator = Evaluator()
    metricsPerClass = evaluator.GetPascalVOCMetrics(
        bbs_to_evaluate, IOUThreshold=iou_threshold,
        method=MethodAveragePrecision.EveryPointInterpolation )
    #print("Average precision (EveryPointInterpolation):")
    # Loop through classes to obtain their metrics
    for mc in metricsPerClass:
        # Get metric values per each class
        c = mc['class']
        assert( c == 'person')
        precision = mc['precision']
        recall = mc['recall']
        average_precision = mc['AP']
        ipre = mc['interpolated precision']
        irec = mc['interpolated recall']
        # FP/TP 'total positives': 13, 'total TP': 8.0, 'total FP': 53.0
        # Print AP per class
        print('AP %s: %f' % (c, average_precision))
        #print('FP: %f' % (mc['total FP']))
        global mAP_interPts
        mAP_interPts = average_precision # assing global variable

    #assert len(lbl_found) == cp_count
    return  bbs_to_evaluate, {'site': sitename, 'ID': getSiteInfo(sitename)['ID'], 
                'Latitude': getSiteInfo(sitename)['centerLatLon'][0], 'Longitude': getSiteInfo(sitename)['centerLatLon'][1],
                'date': getSiteInfo(sitename)['date'].strftime('%d %b %y'),
                'forest': getSiteInfo(sitename)['forest'], 
                'GT': lbl_count, 'TPs':tp_count, 'FPs':fp_count, 'AP':average_precision,  'Persons': len(lbl_stats), 'Found': len(lbl_found), 'Incorrect': ip_count }, lbl_stats, lbl_found
    #print( metricsPerClass )
    #cv2.rectangle( img, (10.5,10.4),(300.123,300), (255,0,0), thickness=3 )

    #cv2.waitKey(0)
    #cv2.destroyAllWindows()



def evaluate_open_site( sitename, fp_threshold = .05, ap_threshold = 0.0001, iou_threshold=0.25, show_results=False, write_results=True, flip_images=False, 
        label_color=(0,0,0), border_color=(255,255,255), fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=1.5, fontThickness=2, add_scale_bar=False, show_confidence=True ):
    """Evaluates an open site scene based on 2D labels in the 'Labels2D' folder

    """

    lbl_stats = {}
    lbl_found = {}
    try:
        lbl_map = getSiteInfo(sitename)['lbl_map'] # maps from our labels I,K,A, ... to anyonymous labels A,B,C,D...
    except:
        lbl_map = {} # we cannot use a predefined label map, so we use our own!
        anonymous_lbl = ord('A')


    lbl_count = 0
    tp_count = 0
    fp_count = 0
    ip_count = 0 #incorrect person
    cp_count = 0 #correct person (differs from tp, because we consider a detection in any gt BB to be correct; so multiple detections of the same GT are allowed!)

    #sitename = 'Test20201020F1'
    anaos_path = os.environ.get('ANAOS_DATA')
    SaveImagePath = os.path.join( anaos_path, 'SITES', sitename, 'Labels2D' )
    ResultsFolder = os.path.join( anaos_path, 'SITES', sitename, 'LabelResults' )
    if write_results and not os.path.isdir(ResultsFolder):
        os.mkdir( ResultsFolder )

    
    count_images = 0

    new_K = projection_matrix(flip_images)
    closeup_size = (56,56)
    closeup_scale = 3
    closeup_border = 3 # pixels

    img = None
    image_count = 0

    bbs_to_evaluate = BoundingBoxes()

    for filename in glob.glob( os.path.join( SaveImagePath, '*.png' ) ): #assuming gif

        image_name = 'Site{}_{}'.format( sitename,os.path.basename(filename) )

        results = { 'detections':[], 'gt_labels':[] }


        #label_file = os.path.join( SaveImagePath, "{}.json".format(os.path.splitext(filename)[0]) )

      


        #print(center_cam)

        img = cv2.imread( os.path.join( SaveImagePath, filename ), cv2.IMREAD_COLOR )

        # read raw file:
        #img_raw_file = os.path.join( SaveImagePath, "{}.raw.npy".format(PathsIdentifier) )
        #img_raw = np.load( img_raw_file )
        #img = img_raw

          # add labels
        try:
            load_gt_to_BBs(bbs_to_evaluate, image_name, os.path.join( SaveImagePath, filename ), img.shape[0:2] )
        except:
            print( 'no GT labels for {}'.format(image_name) )

        # run inference with yolo!
        dimg, detections = image_detection( img, network, class_names, class_colors, ap_threshold, nms_thresh=iou_threshold )
        #cv2.imshow( 'Line {}'.format(PathsIdentifier), dimg ) 

        if flip_images:
            img = cv2.flip(img, 1) # flip image left right!
            digm = cv2.flip(dimg,1)

        oimg = img.copy()

        
        add_detections_to_BBs(bbs_to_evaluate, image_name, detections, flip_images)

        # check if a label is in the detections
        det_bbs = bbs_to_evaluate.getBoundingBoxesByImageName(image_name)

        # filter to only contain detections above a threshold:
        det_bbs = [ bb for bb in det_bbs if bb.getBBType() == BBType.Detected and bb.getConfidence() >= fp_threshold ]
        fp_count += len(det_bbs) # assume that every detection is a false positive!
        ip_count += len(det_bbs)

        # detections:
        for bb in det_bbs:
            x,y,x2,y2= bb.getAbsoluteBoundingBox(format=BBFormat.XYX2Y2)
            cv2.rectangle( img, (x,y), (x2,y2), fp_color, thickness=3 )
            if show_confidence:
                cv2.putText(img, "{:5.2f}".format(bb.getConfidence()*100), (x,y2), cv2.FONT_HERSHEY_PLAIN, 2, color=text_color, thickness=2 )



        # get gt bbs for one image
        gt_bbs = [ bb for bb in bbs_to_evaluate.getBoundingBoxesByImageName(image_name) if bb.getBBType() == BBType.GroundTruth ]
        lbl_count += len(gt_bbs)
        
        # gt lables
        for gt_bb in gt_bbs:
            
            gt_bb_found = False
            x,y,x2,y2= gt_bb.getAbsoluteBoundingBox(format=BBFormat.XYX2Y2)
            results["gt_labels"].append( {'XYX2Y2': (int(x),int(y),int(x2),int(y2)) } )

            #extract closeup
            cx = np.amax([int((x+x2)/2 - closeup_size[0]/2),0])
            cy = np.amax([int((y+y2)/2 - closeup_size[1]/2),0])
            cx = cx if cx+closeup_size[1] < oimg.shape[1] else oimg.shape[1]-closeup_size[1]
            cy = cy if cy+closeup_size[0] < oimg.shape[0] else oimg.shape[0]-closeup_size[0]

            closeup = oimg[cy:cy+closeup_size[1],cx:cx+closeup_size[0],:]
            #closeup = cv2.normalize(closeup, None, norm_type=cv2.NORM_MINMAX )
            closeup = cv2.resize(closeup, tuple([z * closeup_scale for z in closeup_size]) )
            #print(cx,cy)
            #cv2.putText(closeup, "{}".format(lbl_map[lbl["Label"].upper()]), (10,40),  fontFace, fontScale, color=text_color, thickness=int(fontThickness) )
            #if closeup_border > 0:
            #    closeup = cv2.copyMakeBorder( closeup, closeup_border, closeup_border, closeup_border, closeup_border, cv2.BORDER_CONSTANT, value=border_color )

            #cv2.imwrite( os.path.join(CloseupsFolder,"{}_{}.png".format(PathsIdentifier,lbl_map[lbl["Label"].upper()])),closeup)

            cv2.rectangle( img, (x,y), (x2,y2), boundingbox_color, thickness=3 )

            ious = Evaluator._getAllIOUs(gt_bb, det_bbs)
            ious = sorted(ious, key=lambda i: i[2].getConfidence(), reverse=True)  # sort by confidence (from highest to lowest)
            assert( len(det_bbs) == len(ious) )

            for iou in ious:
                x,y,x2,y2= iou[2].getAbsoluteBoundingBox(format=BBFormat.XYX2Y2)
                # iou has the format iou, gt, det
                if iou[2].getConfidence() >= fp_threshold:
                    if iou[0] >= iou_threshold and not gt_bb_found:

                        tp_count += 1
                        fp_count -= 1
                        cp_count += 1
                        ip_count -= 1
                        gt_bb_found = True # only count once as true positive!
                        x,y,x2,y2= iou[2].getAbsoluteBoundingBox(format=BBFormat.XYX2Y2)
                        cv2.rectangle( img, (x,y), (x2,y2), tp_color, thickness=3 )

                        results["detections"].append( {'XYX2Y2': (int(x),int(y),int(x2),int(y2)), 'conf': iou[2].getConfidence(), 'isTP':True  } )
                    elif iou[0] >= iou_threshold :
                        results["detections"].append( {'XYX2Y2': (int(x),int(y),int(x2),int(y2)), 'conf': iou[2].getConfidence(), 'isTP':False  } )
                        cv2.rectangle( img, (x,y), (x2,y2), tp_color, thickness=3 )
                        cp_count += 1
                        ip_count -= 1
                    else:
                        results["detections"].append( {'XYX2Y2': (int(x),int(y),int(x2),int(y2)), 'conf': iou[2].getConfidence(), 'isTP':False, 'closeToLabel':""  } )
                        #cv2.rectangle( img, (x,y), (x2,y2), fp_color, thickness=3 )
                        #pass
                else:
                    raise "this should never happen!"

            # put label text last so it is on top!
            #putBBText( img, min_coord, max_coord, "{}".format(lbl_map[lbl["Label"].upper()]), fontFace, fontScale, color=text_color, thickness=fontThickness )
            #cv2.putText(img, "{}".format(lbl_map[lbl["Label"].upper()]), (x,y-10),  fontFace, fontScale, color=text_color, thickness=fontThickness )

        # place a label with the image number in the corner
        cv2.putText(img, "{}".format(image_count), (10,40), fontFace, fontScale, color=border_color,  thickness=fontThickness )
        
        if show_results:
            cv2.imshow( image_name, img ) 

        if write_results:
            cv2.imwrite( os.path.join(ResultsFolder, "Detections{}".format(os.path.basename(filename))), img ) 
            #with open( os.path.join(ResultsFolder,"Detections{}.json".format(os.path.basename(filename))), 'w' ) as det_file:
            #    json.dump( results, det_file )

        image_count += 1
   


    print( "Persons: {} (total {})".format(lbl_stats,len(lbl_stats)) )
    print( "How often Found: {} (missed {})".format(lbl_found,len(lbl_stats)-len(lbl_found)) )
    print( "#Persons (labels): ", len(lbl_stats.keys()) )
    print( "Total Labels: ", lbl_count )
    print( "TPs: ", tp_count )
    print( "FPs: ", fp_count )
    #print(lbl_map)


    evaluator = Evaluator()
    metricsPerClass = evaluator.GetPascalVOCMetrics(
        bbs_to_evaluate, IOUThreshold=iou_threshold,
        method=MethodAveragePrecision.EveryPointInterpolation )
    #print("Average precision (EveryPointInterpolation):")
    # Loop through classes to obtain their metrics
    for mc in metricsPerClass:
        # Get metric values per each class
        c = mc['class']
        assert( c == 'person')
        precision = mc['precision']
        recall = mc['recall']
        average_precision = mc['AP']
        ipre = mc['interpolated precision']
        irec = mc['interpolated recall']
        # FP/TP 'total positives': 13, 'total TP': 8.0, 'total FP': 53.0
        # Print AP per class
        print('AP %s: %f' % (c, average_precision))
        #print('FP: %f' % (mc['total FP']))
        global mAP_interPts
        mAP_interPts = average_precision # assing global variable

    #assert len(lbl_found) == cp_count
    return  bbs_to_evaluate, {'site': sitename, 'ID': getSiteInfo(sitename)['ID'], 
                'Latitude': getSiteInfo(sitename)['centerLatLon'][0], 'Longitude': getSiteInfo(sitename)['centerLatLon'][1],
                'date': getSiteInfo(sitename)['date'].strftime('%d %b %y'),
                'forest': getSiteInfo(sitename)['forest'], 
                'GT': lbl_count, 'TPs':tp_count, 'FPs':fp_count, 'AP':average_precision,  'Persons': len(lbl_stats), 'Found': len(lbl_found), 'Incorrect': ip_count }, lbl_stats, lbl_found
    #print( metricsPerClass )
    #cv2.rectangle( img, (10.5,10.4),(300.123,300), (255,0,0), thickness=3 )

    #cv2.waitKey(0)
    #cv2.destroyAllWindows()


new_K = projection_matrix()

ap_threshold = 0.005 # threshold used for computing the average precision! should be pretty low
fp_threshold = 0.10 # threshold for computing detections ... this needs to be adjusted!! # we use 10% in the paper (vL.2noTest)
iou_threshold = .01 # usually this is 25%!!!
aug = "noAHE"
yoloversion = "yolov4-tiny"
weightsfile, cfgfile, datafile = prepareDarknetFiles( aug, yoloversion, 'vM.0' )
wd = os.getcwd()
os.chdir(yolo_path) # change to yolo working dir for startup!
network, class_names, class_colors = darknet.load_network(
    cfgfile,
    datafile,
    weightsfile,
    batch_size=1
)
os.chdir(wd) # change to old workign dir



text_color = (0,0,0) # black
boundingbox_color = text_color 
tp_color = (0,255,0) # green
fp_color = (0,0,255) # red


sites = [ "Test20201120_OpenField",
    "TestFG_20210209_OpenField_T4R2_LargerGrid3_IP2",
    "20210219_OpenField_T4R2",
    "20210309_OpenField_T4R2_T2",
    "20210323_OpenFieldLarge_T6",
    "20210323_OpenFieldLarge_T10",
    "20210323_OpenField_T10NA",
    "20210323_OpenField_T6NA",
    "20210323_OpenField_T4NA",
    "20210323_OpenField_T4",
    "Test20200326_Conifer_Fs6Re3_static",
    "Test20200326_Conifer_Fs4Re2_static",
    "Test20210420_ConiferLarge_f1_4ms",
    "Test20210420_ConiferLarge_f2_6ms",
    "Test20210420_ConiferLarge_f3_10ms",
    # motion (note there are also static persons) scenes
    "Test20210415_Conifer_f1", 
    "Test20210415_Conifer_f2",
    "Test20210415_Conifer_f6",
    
    #"Test20201013_Conifer", "Test20201013_Broadleaf1",   
    #"Test20201015F1", 
    #"Test20201020F1", 
    #"Test20201022F1", 
    #"Test20201022F2",
    #"Test20201028F1", "Test20201028F2" 
    ]

table = []
all_bbs = BoundingBoxes()
for sitename in sites:
    bbs, results, lbl_stats, lbl_found = evaluate_open_site(sitename,  
        fp_threshold=fp_threshold, ap_threshold=ap_threshold, iou_threshold=iou_threshold)

    table.append(results)
    [all_bbs.addBoundingBox(bb) for bb in bbs.getBoundingBoxes()]

evaluator = Evaluator()
metricsPerClass = evaluator.GetPascalVOCMetrics(
    all_bbs, IOUThreshold=iou_threshold,
    method=MethodAveragePrecision.EveryPointInterpolation )
#print('overall AP %s: %f' % ('person', metricsPerClass[0]['AP']))

# plot precision/recall curves
#evaluator.PlotPrecisionRecallCurve(  all_bbs,
#                                 IOUThreshold=iou_threshold,
#                                 method=MethodAveragePrecision.EveryPointInterpolation,
#                                 showAP=False,
#                                 showInterpolatedPrecision=False,
#                                 savePath=None,
#                                 showGraphic=True)

# sum
sumr = {'GT': 0, 'TPs':0, 'FPs':0, 'Persons': 0, 'Found': 0, 'Incorrect': 0 } # dict with sums
for k in sumr.keys():
    if isinstance( table[0][k], Number ):
        for r in table:
            sumr[k] += r[k]

sumr.update({'site': 'ALL', 'ID': 'ALL', 'AP':metricsPerClass[0]['AP'] })
#print(sumr)
table.append(sumr)
#print(table)

df = pd.DataFrame(data=table)
print(df)

df.to_excel('results_new.xlsx', sheet_name='eval_iou{}_conf{}'.format(iou_threshold,fp_threshold), index=False)




darknet.free_network_ptr(network)
cv2.waitKey(0)