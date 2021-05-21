import time
import ctypes as ct
import shutil
import os
import glob
import numpy as np
import math
import logging
import glm
import json
import cv2
import utm
import statistics
import random
from PIL import Image
#import png
from pathlib import Path
import sys

import asyncio
import aiohttp
import aiofiles


# to find the local modules we need to add the folders to sys.path
cur_file_path = Path(__file__).resolve().parent
sys.path.insert(1, cur_file_path )
sys.path.insert(1, os.path.join(cur_file_path, '..', 'PLAN') )
sys.path.insert(1, os.path.join(cur_file_path, '..', 'DET') )
sys.path.insert(1, os.path.join(cur_file_path, '..', 'CAM') )
sys.path.insert(1, os.path.join(cur_file_path, '..', 'LFR', 'python') )

import pyaos
detection = False
if detection :
    from detector import Detector
from matplotlib import pyplot as plt
from utils import createviewmateuler,FindStartingHeight, upload_images, upload_detectionlabels,create_dummylocation_id,upload_images_was
from LFR_utils import read_poses_and_images, pose_to_virtualcamera, init_aos, init_window
from Undistort import Undistort
import multiprocessing

#Debug -- Test Planner Update Pipeline
test_planner = True
if test_planner:
    from Planner import Planner


formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logging.basicConfig(level=logging.DEBUG)

def setup_logger(name, log_file, level=logging.DEBUG):
    """To setup as many loggers as you want"""
    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger
    
def ReadGPSlogFiles(GPSLogfileName, Skipheader = 3):
    Date, Time, DebugIndex, Latitude,Longitude,Altitude,CompassHeading = np.genfromtxt(GPSLogfileName, skip_header=3, unpack=True, delimiter=' ')
    LatitudeCellList = []
    LongitudeCellList = []
    AltitudeCellList = []
    CompassCellList = []
    LatitudeExtendedCellList = []
    LongitudeExtendedCellList = []
    AltitudeExtendedCellList = []
    CompassExtendedCellList = []
    CurrentCellLatList = []
    CurrentCellLonList = []
    CurrentCellAltList = []
    CurrentCellCompassList = []
    CellCount = 0
    for i in range(len(Latitude)) :
        #print(i,CellCount)
        if CellCount+1 == Latitude[i] :
            CellCount = CellCount + 1
            if CurrentCellLatList:
                LatitudeCellList.append(CurrentCellLatList)
                LongitudeCellList.append(CurrentCellLonList)
                AltitudeCellList.append(CurrentCellAltList)
                CompassCellList.append(CurrentCellCompassList)
                LatitudeExtendedCellList.extend(CurrentCellLatList)
                LongitudeExtendedCellList.extend(CurrentCellLonList)
                AltitudeExtendedCellList.extend(CurrentCellAltList)
                CompassExtendedCellList.extend(CurrentCellCompassList)
                CurrentCellLatList = []
                CurrentCellLonList = []
                CurrentCellAltList = []
                CurrentCellCompassList = []     
        else :
            CurrentCellLatList.append(Latitude[i])
            CurrentCellLonList.append(Longitude[i])
            CurrentCellAltList.append(Altitude[i])
            CurrentCellCompassList.append(CompassHeading[i])
    return LatitudeCellList, LongitudeCellList, AltitudeCellList, CompassCellList, LatitudeExtendedCellList, LongitudeExtendedCellList, AltitudeExtendedCellList, CompassExtendedCellList

class Renderer :
    "Class to Render based on both posesfile, GpsInformation and allow communication with other modules"
    _FieldofView = 43.10803984095769#43.50668199945787#50.815436217896945
    _yoloversion = "yolov4-tiny"
    _aug = "noAHE"
    _device = "MYRIAD"
    _LFRHeight = 512
    _LFRWidth = 512
    _Render = True
    _Detect = True
    _legacy_normalization = False
    _PrePlannedPath = False
    _LowerThreshold = 0.05
    _UpperThreshold = 0.1
    _GrabVideoFrames = True
    _adddebuginfo = False
    # debugging things:
    _debug = False
    _fig = None
    _ax = None
    _basedatapath = None
    # logging
    _RendererLog = None
    _out_folder = None
    _imagecount = 0
    _previousMergedDetection = None
    _previousMergedDetectionCount = None
    _WriteImages = True
    _UpdatePathPlanning = False
    _CenterUTMInfo = None

    def __init__(self, CenterUTMInfo, ObjModelPath, ObjModelImagePath, basedatapath, sitename, results_folder='Renderer_results', device = "MYRIAD", yoloversion = "yolov4-tiny",aug = "noAHE", FieldofView = 43.10803984095769, LFRHeight = 512,LFRWidth = 512, Render = True, Detect = True, legacy_normalization = False,PrePlannedPath = False, LowerThreshold = 0.1,UpperThreshold = 0.1,GrabVideoFrames = True, uploadserver = False, baseserver = 'http://localhost:8080', locationid = None, adddebuginfo = False):
        if not os.path.isdir( results_folder ): 
            os.mkdir( results_folder)
        self._adddebuginfo = adddebuginfo
        self._CenterUTMInfo = CenterUTMInfo
        self._basedatapath = basedatapath
        self._sitename = sitename
        self._out_folder = results_folder
        self._GrabVideoFrames = GrabVideoFrames
        self._yoloversion = yoloversion
        self._aug = aug
        self._FieldofView = FieldofView
        self._LFRHeight = LFRHeight
        self._LFRWidth = LFRWidth
        self._Render = Render
        self._Detect = Detect
        self.ObjModelPath = ObjModelPath
        self.ObjModelImagePath = ObjModelImagePath
        self._device = device
        self._legacy_normalization = legacy_normalization
        self._PrePlannedPath = PrePlannedPath
        self._LowerThreshold = LowerThreshold
        self._UpperThreshold = UpperThreshold
        self.CenterEast = CenterUTMInfo[0]
        self.CenterNorth = CenterUTMInfo[1]
        self.CenterUTMInfo = CenterUTMInfo
        self._imagecount = 0
        self._WriteImages = True
        self._UpdatePathPlanning = False
        self._uploadserver = uploadserver
        self._serveraddress = baseserver
        self._locationid = locationid
        self._ImageList = []
        self._ImageMatList = []
        self._ImageIDList = []
        self._session = None
        if self._Detect:
            self._previousMergedDetection = np.zeros((self._LFRHeight, self._LFRWidth))
            self._previousMergedDetection = self._previousMergedDetection.astype('float32')
            self._previousMergedDetectionCount = np.zeros((self._LFRHeight, self._LFRWidth))
            self._previousMergedDetectionCount = self._previousMergedDetectionCount.astype('float32')
    
    async def initalize_aiohttpsession(self):
        self._session = aiohttp.ClientSession()
        yield
        await self._session.close()
    
    async def UploadAllImages(self,ImageList,ViewMatrixList, IntegralImage, IntegralViewMatrix):
        if self._session is None:
            self._session = aiohttp.ClientSession()
        Image_IDList = await asyncio.gather(*[upload_images_was(self._session,self._serveraddress, image, mat, self._locationid, poses = None) for image, mat in zip(ImageList, ViewMatrixList)])
        if len(Image_IDList):
            self._ImageIDList.extend(Image_IDList)
            IntegralImageList = self._ImageIDList[len(self._ImageIDList)-30:len(self._ImageIDList)-1]
            await upload_images_was(self._session, self._serveraddress, IntegralImage, IntegralViewMatrix, self._locationid, poses = IntegralImageList)

    
    async def UploadAllImages_ss(self,ImageList,ViewMatrixList, IntegralImage, IntegralViewMatrix):
        async with aiohttp.ClientSession() as session:
            Image_IDList = await asyncio.gather(*[upload_images_was(session,self._serveraddress, image, mat, self._locationid, poses = None) for image, mat in zip(ImageList, ViewMatrixList)])
            if len(Image_IDList):
                self._ImageIDList.extend(Image_IDList)
                IntegralImageList = self._ImageIDList[len(self._ImageIDList)-30:len(self._ImageIDList)-1]
                await upload_images_was(session, self._serveraddress, IntegralImage, IntegralViewMatrix, self._locationid, poses = IntegralImageList)


    def RenderContinuous(self, PyLFClass,DownloadedImage, Latitude, Longitude, Altitude, CompassHeading, NoofPathsRendered,CurrentImageIndex,CompassCorrection,StartHeight,ud,MeanAltitude,MeanCompass,CompassRad, CurrentImageNumber, virtualcamerapose, CenterCameraIndex, PreviousRenderedMean = 0.5, RenderandDetectFlag = True):
        if len(DownloadedImage.shape) == 2 :
            MeanAdjustedImage = DownloadedImage
        else :
            MeanAdjustedImage = DownloadedImage[:,:,0]
        undstortedimage = ud.undistort( MeanAdjustedImage )
        East,North,Block,Utmzone = utm.from_latlon(Latitude, Longitude)
        if abs(MeanAltitude - Altitude) > 2.0  :
            Altitude = -((MeanAltitude + StartHeight))
        else :
            Altitude = -((Altitude + StartHeight)) #GetStartHeight and SetStartHeight
        EastCentered = (East - self.CenterEast) #Get MeanEast and Set MeanEast
        NorthCentered = (self.CenterNorth - North) #Get MeanNorth and Set MeanNorth
        generatedviewmatrix = createviewmateuler(np.array([CompassRad, 0,0]),np.array( [EastCentered,NorthCentered,Altitude]) )
        if self._uploadserver :
            #image_id = await upload_images(self._serveraddress, undstortedimage, generatedviewmatrix, self._locationid, poses = None)
            self._ImageList.append(undstortedimage)
            self._ImageMatList.append(generatedviewmatrix)
            image_id = None
        else :
            image_id = None
        ViewMatrix = np.vstack((generatedviewmatrix, np.array([0.0,0.0,0.0,1.0],dtype=np.float32)))
        camerapose = np.asarray(ViewMatrix.transpose(),dtype=np.float32)
        vpose = camerapose.copy()
        inversecamerapose = glm.inverse(camerapose)
        Posvec =glm.vec3(inversecamerapose[3])
        Upvec = glm.vec3(inversecamerapose[1])
        FrontVec = glm.vec3(inversecamerapose[2])
        cameraviewarr = np.array(glm.lookAt(Posvec, Posvec + FrontVec, Upvec))
        gpsloc = (Latitude, Longitude)
        #ViewMatrixArray = ViewMatrix.flatten()
        if (CurrentImageIndex < 30) :
            PyLFClass.addView(undstortedimage, camerapose, str(CurrentImageNumber))
        else :
            PyLFClass.replaceView(CurrentImageNumber, undstortedimage, camerapose, str(CurrentImageNumber))
        #print('No of Poses', PyLFClass.getViews())
        #print('CurrentImageIndex', CurrentImageIndex)
        #print('CurrentImageNumber', CurrentImageNumber)
        #print('virtualcamerapose', virtualcamerapose)
        if RenderandDetectFlag:
            ids = np.array([],dtype=np.uintc)
            ImageReturned1 = PyLFClass.render(virtualcamerapose, self._FieldofView)
            #ImageReturned1 = cv2.flip(ImageReturned1,1)
            if self._UpdatePathPlanning:
                #self._RendererLog.debug('Rendering Finished')
                RenderDemInfo = PyLFClass.getXYZ()
                #RenderDemInfo = cv2.flip(RenderDemInfo,1)
        else :
            ImageReturned1 = np.zeros((512,512), dtype=float)
        if not self._UpdatePathPlanning:
            RenderDemInfo = np.zeros((512,512,3), dtype=float)
        return ImageReturned1,RenderDemInfo,cameraviewarr,gpsloc, generatedviewmatrix, image_id
    def GenerateDetectionTuples(self, RenderedDEM_Info, DetectedObjects, CenterUTMInfo):
        Detections = []
        labels_data = []        
        for i in range(0,len(DetectedObjects)):
            ObjectInfo = {}
            label = {}
            Object = DetectedObjects[i]
            #print(Object)
            Xmin = float(Object['xmin'])
            Ymin = float(Object['ymin'])
            Xmax = float(Object['xmax'])
            Ymax = float(Object['ymax'])
            ConfidenceScore = float(Object['confidence'])
            XCenter = int((Xmin + Xmax)/2)
            YCenter = int((Ymin + Ymax)/2)
            ObjectCenterEast = RenderedDEM_Info[YCenter,XCenter,0]
            ObjectCenterNorth = RenderedDEM_Info[YCenter,XCenter,1]
            ObjectEast = ObjectCenterEast + CenterUTMInfo[0]
            ObjectNorth = CenterUTMInfo[1] - ObjectCenterNorth
            Lat,Lon = utm.to_latlon(ObjectEast,ObjectNorth,CenterUTMInfo[2],CenterUTMInfo[3])
            ObjectInfo['gps'] = (Lat,Lon) 
            ObjectInfo['conf'] = ConfidenceScore
            label['poly_dem'] = [
                                 [ RenderedDEM_Info[Ymin,Xmax,0], RenderedDEM_Info[Ymin,Xmax,1], RenderedDEM_Info[Ymin,Xmax,2]],
                                 [ RenderedDEM_Info[Ymin,Xmin,0], RenderedDEM_Info[Ymin,Xmin,1], RenderedDEM_Info[Ymin,Xmin,2]],
                                 [ RenderedDEM_Info[Ymax,Xmin,0], RenderedDEM_Info[Ymax,Xmin,1], RenderedDEM_Info[Ymax,Xmin,2]],
                                 [ RenderedDEM_Info[Ymax,Xmax,0], RenderedDEM_Info[Ymax,Xmax,1], RenderedDEM_Info[Ymax,Xmax,2]]
                                ]
            label['texture_poly'] = [[int(Xmax),int(Ymin)],[int(Xmin),int(Ymin)],[int(Xmin),int(Ymax)],[int(Xmax),int(Ymax)]]
            label['label'] = str(Object['confidence'])
            Detections.append(ObjectInfo)
            labels_data.append(label)
        return Detections, labels_data

    def RendererandDetectContinuous(self, RenderingQueue, DetectionInfoQueue, RenderingProcessEvent):
        #print('Renderer and Detection Started in Third Thread')
        self._RendererLog = setup_logger( 'Renderer_logger', os.path.join( self._out_folder, 'RendererLog.log') )
        self._RendererLog.debug('Renderer and Detection Started in Third Thread')
        asyncio.run(create_dummylocation_id(self._serveraddress, self._locationid))
        #asyncio.run(self.initalize_aiohttpsession())
        #weightsXmlFile = os.path.join(".","weights",yoloversion,aug,yoloversion+'.xml')
        #weightsXmlFile = os.path.join(".","weights","vL.2noTest","AP25to30",yoloversion,aug,yoloversion+'.xml')
        #weightsXmlFile = os.path.join(".","weights","vL.2noTest","APall",self._yoloversion,self._aug,self._yoloversion+'.xml')
        #weightsXmlFile = os.path.join(".","weights","vL.56","APall",self._yoloversion,self._aug,self._yoloversion+'.xml')
        try:
            cur_file_path = Path(__file__).resolve().parent
            weightsXmlFile = os.path.join(cur_file_path, '..', 'DET',"weights",self._yoloversion+'.xml')
            if self._Render == True or self._Detect == True :
                if 'window' not in locals() or window == None: 
                    window = init_window() # only init the window once (causes problems if closed and loaded again!)
                fov = self._FieldofView
                # init the light-field renderer
                PLFClass = init_aos(fov=fov)
                PLFClass.loadDEM(self.ObjModelPath)
                self._RendererLog.debug('Renderer Initialized')
                if self._Detect == True:
                    self._RendererLog.debug('starting Detector Initilized')
                    YoloDetector = Detector()
                    YoloDetector.init(weightsXmlFile, device = self._device )
                    self._RendererLog.debug('Detector Initilized')
                ud = Undistort()
                PreviousRenderedMean = 0.5
                CurrentPathIndex = 0
                CurrentImageIndex = 0
                CompassCorrection = 0
                CurrentPathCameraPose = [np.zeros((4,4),dtype=np.float32) for _ in range(30)]
                currentpath_genviewmat = [np.zeros((3,4),dtype=np.float32) for _ in range(30)]
                CurrentPathgpsloc = [(0.0,0.0) for _ in range(30)]
                imageidlist = ['' for _ in range(30)]
                CurrentPathAltitude = [0.0] *30
                CurrentPathCompass = [0.0] *30
                PreviousVirtualCamPos = (0.0,0.0)
                RenderSeparatlyFlag = True
                PreviousCameraNumber = None
                CurrentPathDetections = []
                #LUTRange = apply_custom_colormap()
                if self._GrabVideoFrames:
                    while not RenderingProcessEvent.is_set():
                        while not RenderingQueue.empty():
                            if not RenderingQueue.empty():
                                RenderingInfo = RenderingQueue.get()
                                self._RendererLog.debug('Render or Add an Image')
                                CurrentLatitude =  RenderingInfo['Latitude']
                                CurrentLongitude = RenderingInfo['Longitude']
                                CurrentAltitude = RenderingInfo['Altitude']
                                CurrentCompass = RenderingInfo['CompassHeading']
                                CurrentDownloadedImage = RenderingInfo['Image']
                                StartHeight = RenderingInfo['StartingHeight']
                                RenderandDetectFlag = RenderingInfo['Render']
                                UpdatePathPlanningFlag = RenderingInfo['UpdatePlanningAlgo']
                                    
                                self._UpdatePathPlanning = UpdatePathPlanningFlag
                                CurrentImageNumber = int(CurrentImageIndex % 30)
                                CentralCameraIndex = int((CurrentImageNumber + 15) % 30)
                                    
                                CurrentPathAltitude[CurrentImageNumber] = CurrentAltitude
                                CurrentPathCompass[CurrentImageNumber] = CurrentCompass
                                centercameraviewarr = CurrentPathCameraPose[CentralCameraIndex]
                                CurrentAltitudeArray = np.array(CurrentPathAltitude)
                                CurrentCompassArray  = np.array(CurrentPathCompass)
                                #MeanAltitude = CurrentAltitudeArray[CurrentAltitudeArray!=0].mean()
                                MeanAltitude = statistics.median(CurrentAltitudeArray)
                                #MeanCompass = circmean(CurrentCompassArray,high = 360, low = 0)#CompassArray[CompassArray!=0].mean()
                                MeanCompass = CurrentCompassArray[CurrentCompassArray!=0].mean()
                                CompassRad = math.radians((MeanCompass*2) + CompassCorrection)
                                if self._adddebuginfo :
                                    self._RendererLog.debug('Current Frame Lat = %s, Lon = %s, Alt = %s, Comp = %s',str(CurrentLatitude),str(CurrentLongitude),str(CurrentAltitude),str(CurrentCompass))
                                    self._RendererLog.debug('StartingHeigth = %s, Render = %s, UpdatePlanningAlgo = %s',str(StartHeight),str(RenderandDetectFlag),str(UpdatePathPlanningFlag))
                                    self._RendererLog.debug('CurrentImageNumber = %s, CentralCameraIndex = %s , CurrentImageNumber = %s',str(CurrentImageNumber),str(CentralCameraIndex), str(CurrentImageNumber))
                                    self._RendererLog.debug('MeanAltitude = %s, CompassRad = %s',str(MeanAltitude),str(CompassRad))
                                if not RenderandDetectFlag :
                                    RenderedImage, RenderedDEM_Info, CurrentCamviewarr,gpsloc, genviewmat, image_id = self.RenderContinuous(PLFClass,CurrentDownloadedImage,CurrentLatitude,CurrentLongitude,CurrentAltitude,CurrentCompass,CurrentPathIndex,CurrentImageIndex,CompassCorrection,StartHeight, ud,MeanAltitude,MeanCompass,CompassRad,CurrentImageNumber,centercameraviewarr,CentralCameraIndex,PreviousRenderedMean,RenderandDetectFlag)
                                    currentpath_genviewmat[CurrentImageNumber] = genviewmat
                                    imageidlist[CurrentImageNumber] = image_id
                                    CurrentPathCameraPose[CurrentImageNumber] = CurrentCamviewarr
                                    CurrentPathgpsloc[CurrentImageNumber] = gpsloc
                                    if self._adddebuginfo :
                                        self._RendererLog.debug('Image Added')
                                else :
                                    t2_start = time.perf_counter()
                                    RenderedImage, RenderedDEM_Info, CurrentCamviewarr,gpsloc, genviewmat, image_id  = self.RenderContinuous(PLFClass, CurrentDownloadedImage, CurrentLatitude, CurrentLongitude, CurrentAltitude, CurrentCompass, CurrentPathIndex,CurrentImageIndex,CompassCorrection,StartHeight, ud,MeanAltitude,MeanCompass,CompassRad, CurrentImageNumber,centercameraviewarr, CentralCameraIndex, PreviousRenderedMean, RenderandDetectFlag)
                                    t2_stop = time.perf_counter()
                                    print('Rendering Images Elapsed time',str(t2_stop - t2_start))
                                    if self._adddebuginfo :
                                        self._RendererLog.debug('Rendering Elapsed time: = %s,',str(t2_stop -t2_start))
                                    currentpath_genviewmat[CurrentImageNumber] = genviewmat
                                    imageidlist[CurrentImageNumber] = image_id
                                    CurrentPathCameraPose[CurrentImageNumber] = CurrentCamviewarr
                                    CurrentPathgpsloc[CurrentImageNumber] = gpsloc
                                    PreviousVirtualCamPos = CurrentPathgpsloc[CentralCameraIndex]
                                    Alpha = RenderedImage[:,:,3]
                                    Alpha[Alpha == 0] = 1
                                    RenderedImage[:,:,0] = np.divide(RenderedImage[:,:,0] , Alpha)
                                    RenderedImage[:,:,1] = np.divide(RenderedImage[:,:,1] , Alpha)
                                    RenderedImage[:,:,2] = np.divide(RenderedImage[:,:,2] , Alpha)
                                    RenderedImage = RenderedImage[:,:,0:3] * 255
                                    minval = np.min(RenderedImage[np.nonzero(RenderedImage)])
                                    RenderedImage[RenderedImage == 0] = minval
                                    RenderedImage = cv2.normalize(RenderedImage, None, 0,255, cv2.NORM_MINMAX, cv2.CV_8UC3)
                                    if self._uploadserver :

                                        #image_id = await upload_images(self._serveraddress, RenderedImage, currentpath_genviewmat[CentralCameraIndex], self._locationid, poses = imageidlist)
                                        t3_start = time.perf_counter()
                                        asyncio.run(self.UploadAllImages(self._ImageList,self._ImageMatList,RenderedImage,currentpath_genviewmat[CentralCameraIndex]))
                                        #asyncio.run(self.UploadAllImages_ss(self._ImageList,self._ImageMatList,RenderedImage,currentpath_genviewmat[CentralCameraIndex]))
                                        t3_stop = time.perf_counter()
                                        self._RendererLog.debug('Uploading Images Elapsed time: = %s,',str(t3_stop - t3_start))
                                        print('Uploading Images Elapsed time',str(t3_stop - t3_start))
                                        self._ImageList = []
                                        self._ImageMatList = []
                                    if self._WriteImages :
                                        if self._adddebuginfo :
                                            self._RendererLog.debug('Image Rendered')
                                        RenderedPathName = os.path.join(self._out_folder, str(CurrentPathIndex)+'_'+str(CurrentImageIndex)+'.png')
                                        cv2.imwrite(RenderedPathName,RenderedImage)
                                        if self._adddebuginfo :
                                            self._RendererLog.debug('Renderer for Path = %s, Finished stored at = %s',str(CurrentPathIndex),RenderedPathName)
                                    if self._Detect == True:
                                        if self._adddebuginfo :
                                            self._RendererLog.debug('Detection Started')
                                        t1_start = time.perf_counter()
                                        DetectedImage, DetectedObjects = YoloDetector.detect(RenderedImage, prob_threshold = self._UpperThreshold)
                                        t1_stop = time.perf_counter()
                                        DLDetections = None
                                        if self._adddebuginfo :
                                            self._RendererLog.debug('Detection Elapsed time: = %s,',str(t1_stop -t1_start))
                                        if self._uploadserver :
                                            DLDetections,labels_data = self.GenerateDetectionTuples(RenderedDEM_Info, DetectedObjects,self._CenterUTMInfo)
                                            upload_detectionlabels(self._serveraddress,self._locationid,labels_data)
                                        if self._WriteImages :
                                            DetectedPathName = os.path.join(self._out_folder, str(CurrentPathIndex)+'_'+str(CurrentImageIndex)+'_Detected.png')
                                            cv2.imwrite(DetectedPathName,DetectedImage)
                                        if self._adddebuginfo :
                                            self._RendererLog.debug('Detected')
                                        if not self._PrePlannedPath:
                                            if self._adddebuginfo :
                                                self._RendererLog.debug('UpdatePathPlanningFlag for Path = %s',str(UpdatePathPlanningFlag))
                                            if not UpdatePathPlanningFlag:
                                                CurrentPathDetections.extend(DLDetections)
                                            else :
                                                if DLDetections is not None:
                                                    DLDetections,labels_data = self.GenerateDetectionTuples(RenderedDEM_Info, DetectedObjects,self._CenterUTMInfo)
                                                DetectionInfo = {}
                                                DetectionInfo['PreviousVirtualCamPos'] = PreviousVirtualCamPos
                                                DetectionInfo['DLDetections'] = DLDetections
                                                DetectionInfo['DetectedImageName'] = DetectedPathName
                                                DetectionInfoQueue.put(DetectionInfo)
                                                CurrentPathDetections = []
                                                CurrentPathIndex = CurrentPathIndex + 1
                                                if self._adddebuginfo :
                                                    self._RendererLog.debug('UpdatedPathPlanningFlag for Path = %s with Current Path  = %s and Current Image = %s',str(UpdatePathPlanningFlag), str(CurrentPathIndex), str(CurrentImageIndex))
                                CurrentImageIndex = CurrentImageIndex + 1   
                del(PLFClass)
                if self._Detect == True:
                    YoloDetector.destroy()
                print('Renderer terminated, Detector Closed, Flight Completed and Third Thread Finished')
        except Exception as ex:
            self._RendererLog.exception('Error in Renderer and Detector')
    
    def dummy_run(self,RenderingQueue, DetectionInfoQueue, RenderingProcessEvent):
        self.RendererandDetectContinuous(RenderingQueue, DetectionInfoQueue, RenderingProcessEvent)
        #loop = asyncio.get_event_loop()
        #loop.run_until_complete(self.RendererandDetectContinuous(RenderingQueue, DetectionInfoQueue, RenderingProcessEvent))
##############################################################################
##############################################################################

# __name__ guard 
if __name__ == '__main__':
    
    sitename = 'open_field'
       
    #anaos_path = os.environ.get('ANAOS_DATA')
    ##Testing Server
    base_url1 = 'http://localhost:8080'
    base_url = 'http://localhost:8080/'
    locationid = "open_field"
     ##Testing Server
    # Todo: change to 
    
    #basedatapath = '../../data'
    #basedatapath = 'D:\\ResilioSync\\ANAOS\\SIMULATIONS'
    #ImageLocation = os.path.join(basedatapath, 'FlightResults',sitename, 'Frames_renamed')
    #ObjModelPath = os.path.join(basedatapath,'FlightResults', sitename, 'LFR','dem.obj')
    #ObjModelImagePath = os.path.join(basedatapath,'FlightResults', sitename, 'LFR','dem.png')
    #DemInfoJSOn = os.path.join(basedatapath, 'FlightResults',sitename, 'LFR','dem_info.json')
    #GpsLogFile = os.path.join(basedatapath, 'FlightResults',sitename, 'GPSLog.log')

    basedatapath = Path(__file__).resolve().parent
    ImageLocation = os.path.join(basedatapath, '..', 'data',sitename, 'images')
    ObjModelPath = os.path.join(basedatapath, '..', 'data',sitename, 'DEM','dem.obj')
    ObjModelImagePath = os.path.join(basedatapath,'..', 'data', sitename, 'DEM','dem.png')
    DemInfoJSOn = os.path.join(basedatapath, '..', 'data',sitename, 'DEM','dem_info.json')
    GpsLogFile = os.path.join(basedatapath, '..', 'data',sitename, 'log','GPSLog.log')

    with open(DemInfoJSOn) as json_file:
        DemInfoDict = json.load(json_file)
    print(DemInfoDict)
    CenterUTMInfo = DemInfoDict['centerUTM']
    CenterEast = CenterUTMInfo[0]   
    CenterNorth = CenterUTMInfo[1]
    FieldofView = 43.10803984095769#43.50668199945787
    startLat = 48.3361723#48.3360345 
    startLon = 14.32628908256837#14.3264914
    startEast,startNorth,Block,UTMZONE = utm.from_latlon(startLat, startLon)
    StartCenteredEastUTM = startEast - CenterEast
    StartCenteredNorthUTM = CenterNorth - startNorth
    MinimumStartingHeigth,Index = FindStartingHeight(ObjModelPath, StartCenteredEastUTM, StartCenteredNorthUTM)
    LatitudeCellList, LongitudeCellList, AltitudeCellList, CompassCellList, LatitudeExtendedCellList, LongitudeExtendedCellList, AltitudeExtendedCellList, CompassExtendedCellList = ReadGPSlogFiles(GpsLogFile)
    print(statistics.median(AltitudeExtendedCellList))
    MedianAltitude =  statistics.median(AltitudeExtendedCellList)
    
    if test_planner:
        PlanningAlgo = Planner( utm_center=(CenterUTMInfo[0], CenterUTMInfo[1], CenterUTMInfo[2], CenterUTMInfo[3]), area_size= (90,90), tile_distance = 30,  prob_map= None, debug=False,vis=None, results_folder=os.path.join(basedatapath, '..', 'data', sitename, 'testresults'),gridalignedplanpath=True)
        TestPlanner = [31,62,95] 
    #TestRenderer = Renderer(CenterUTMInfo,ObjModelPath,ObjModelImagePath,SaveImagePath,sitename,Detect=False,adddebuginfo=True)
    ud = Undistort()

    RenderingQueue = multiprocessing.Queue(maxsize=100)
    DetectionInfoQueue = multiprocessing.Queue(maxsize=100)
    RenderingProcessEvent = multiprocessing.Event()

    #utm_center = (CenterUTMInfo[0], CenterUTMInfo[1], CenterUTMInfo[2], CenterUTMInfo[3])
    #PlanningAlgoClass = Planner( utm_center, (150,150), tile_distance = 150,  prob_map=None, debug=False,vis=None, results_folder=os.path.join(basedatapath,'FlightResults', sitename, 'Log'),gridalignedplanpath = True)
    
    #RendererClass = Renderer(CenterUTMInfo=CenterUTMInfo,ObjModelPath=ObjModelPath, ObjModelImagePath=ObjModelImagePath,basedatapath=basedatapath,
    #sitename=sitename,results_folder=os.path.join(basedatapath, '..', 'data', sitename, 'testresults'), device="MYRIAD", # device should be MYRIAD for Neural Compute Stick
    #FieldofView=float(FieldofView),adddebuginfo=True,Detect=detection)

    ###Testing Server
    RendererClass = Renderer(CenterUTMInfo=CenterUTMInfo,ObjModelPath=ObjModelPath, ObjModelImagePath=ObjModelImagePath,basedatapath=basedatapath,
    sitename=sitename,results_folder=os.path.join(basedatapath, '..', 'data', sitename, 'testresults'), device="MYRIAD", # device should be MYRIAD for Neural Compute Stick
    FieldofView=float(FieldofView),adddebuginfo=True,Detect=detection,uploadserver=True,baseserver=base_url1,locationid=locationid)

    RenderProcess = multiprocessing.Process(name = 'RenderProcess', target=RendererClass.dummy_run, args=(RenderingQueue, DetectionInfoQueue, RenderingProcessEvent,))
    #threads.append(RenderThread)
    RenderProcess.start()
    EastUtmList = []
    NorthUtmList = []
    prev_pt = (startLat, startLon)
    try:
        for i in range(len(LatitudeExtendedCellList)):
            ReadImageName = os.path.join(ImageLocation, str(i+1)+'.png')
            Frame = cv2.imread(ReadImageName)
            #print('MaxFrameValue ', np.amax(Frame))
            cv2.imshow('image', Frame)
            gray = cv2.cvtColor(Frame, cv2.COLOR_BGR2GRAY)
            gray = gray.astype('float32')
            gray /= 255.0
            SendImage = gray
            RenderingInfo = {}
            RenderingInfo['Latitude'] = LatitudeExtendedCellList[i]
            RenderingInfo['Longitude'] = LongitudeExtendedCellList[i]
            #RenderingInfo['Altitude'] = MedianAltitude
            if abs(MedianAltitude - AltitudeExtendedCellList[i]) > 2.0 :
                RenderingInfo['Altitude'] = MedianAltitude#AltitudeExtendedCellList[i]
            else :
                RenderingInfo['Altitude'] = AltitudeExtendedCellList[i]
            RenderingInfo['CompassHeading'] = CompassExtendedCellList[i]
            RenderingInfo['Image'] = SendImage
            RenderingInfo['StartingHeight'] = MinimumStartingHeigth
            East,North,Block,Utmzone = utm.from_latlon(LatitudeExtendedCellList[i], LongitudeExtendedCellList[i])
            EastCentered = (East - CenterEast) #Get MeanEast and Set MeanEast
            NorthCentered = (CenterNorth - North) #Get MeanNorth and Set MeanNorth
            EastUtmList.append(EastCentered)
            NorthUtmList.append(NorthCentered)
            if not DetectionInfoQueue.empty():
                DetectionInfo = DetectionInfoQueue.get()
                PlanningAlgo.update(DetectionInfo['PreviousVirtualCamPos'], DetectionInfo['DLDetections'])
            if i >= 29 :
                if i in TestPlanner:
                    #print('Reached Waypoint')
                    next_pts, FlyingInfoFlag = PlanningAlgo.planpoints( prev_pt )
                    print(next_pts)
                    RenderingInfo['Render'] = True
                    RenderingInfo['UpdatePlanningAlgo'] = True
                    RenderingQueue.put(RenderingInfo)
                    time.sleep(0.5)
                else :
                    if i % 2 == 0:
                        #print('Not Rendering Images')
                        RenderingInfo['Render'] = False
                        RenderingInfo['UpdatePlanningAlgo'] = False
                        RenderingQueue.put(RenderingInfo)
                        time.sleep(0.5)
                    else :
                        #print('Rendering Images')
                        RenderingInfo['Render'] = True
                        RenderingInfo['UpdatePlanningAlgo'] = False
                        RenderingQueue.put(RenderingInfo)
                        time.sleep(0.5)
                
            else :
                RenderingInfo['Render'] = False
                RenderingInfo['UpdatePlanningAlgo'] = False
                RenderingQueue.put(RenderingInfo)
                #time.sleep(0.9)
            time.sleep(0.1)
    except Exception as e:
        print("Oops!", e.__class__, "occurred.")
        print("Next entry.")
        print()
    time.sleep(100)
    RenderingProcessEvent.set()
    time.sleep(10)
    while not RenderingQueue.empty():
        FramesInfo = RenderingQueue.get()
    RenderingQueue.close()
    DetectionInfoQueue.close()
    print('RenderProcess.is_alive()', RenderProcess.is_alive())
    RenderProcess.join(5)
    print('RenderProcess.is_alive()', RenderProcess.is_alive())
    if RenderProcess.is_alive() :
        RenderProcess.terminate()
        RenderProcess.join()
    print('RenderProcess.is_alive()', RenderProcess.is_alive())
    print('All Process Done')
    #ImageList =  [os.path.basename(x) for x in glob.glob(os.path.join(ImageLocation,'*.png'))]
    #print(ImageList)
    #FileName = 'CompletePath.json'
    #CreateJsonPoseFile(EastUtmList, NorthUtmList, AltitudeExtendedCellList, CompassExtendedCellList, ImageList, os.path.join(basedatapath,'FlightResults', sitename, 'Pose_absolute'), FileName,MinimumStartingHeigth)
    #cv2.waitKey()


    #TestRenderer.TerminateRenderer(PyLFClass)

