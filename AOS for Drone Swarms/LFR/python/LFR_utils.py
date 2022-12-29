# %%
import json
import numpy as np
import cv2
from PIL import Image # needed to load hdr images
import math
import os
from pathlib import Path 
import glm # PyGLM
import sys
import pyaos as LFR


def init_window( ):
       
    window = LFR.PyGlfwWindow(512,512,'AOS') # make sure there is an OpenGL context
    return window

def init_aos( w=512, h=512, fov = 50.815436217896945 ) -> LFR:
   
    aos = LFR.PyAOS(w,h,fov)
    return aos

def rotate_vec(vec, radians, rotate_around):
    rm = np.array(glm.rotate(glm.mat4(),radians,glm.vec3(rotate_around)))

    if len(vec)==3:
        vec = np.concatenate((vec,[1]))

    return np.array(rm) @ vec

def translate_pose( pose, t ):
    inv_pose = np.asarray(glm.inverse(pose)).copy()
    inv_pose[3][0:3] += t
    return np.asarray(glm.inverse(inv_pose))

def position_from_pose( pose ):
    return glm.vec3(glm.inverse(pose)[3])

def pose_to_virtualcamera( vpose ):
    vp = glm.mat4(*np.array(vpose).transpose().flatten())
    ivp = glm.inverse(glm.transpose(vp))
    Posvec = glm.vec3(ivp[3])
    Upvec = glm.vec3(ivp[1])
    FrontVec = glm.vec3(ivp[2])
    lookAt = glm.lookAt(Posvec, Posvec + FrontVec, Upvec)
    return np.asarray(glm.transpose(lookAt))



def read_poses_and_images(aos,PosesFilePath,ImageLocation,mask=None, ud=None,replace_ext=None,adjust_mean=False):
    """ read images and poses from the json file and the image directory

    """
    with open(PosesFilePath) as PoseFile:
        PoseFileData = json.load(PoseFile)
        NoofPoses = len(PoseFileData['images'])
        PoseFileImagesData = PoseFileData['images']
        HalfValue = int(round(len(PoseFileData['images'])/2))

        if isinstance(mask,str):
            mask = cv2.imread(mask)[:,:,0]

        if mask is not None: 
            assert isinstance(mask, (np.ndarray, np.generic) )
            assert len(mask.shape)==2 or mask.shape[2] == 1 # single channel image
            if mask.dtype == np.uint8:
                mask = mask.astype(np.float32) / 255.0
            elif mask.dtype == np.uint16:
                mask = mask.astype(np.float32) / 2**16
            #print(f'mask dtype {mask.dtype}, shape: {mask.shape}')
            #assert isinstance( mask, np.floating )

        # read images first and put them in img_list
        img_list = []
        for i in range(0,NoofPoses): 
            LoadImageName = PoseFileImagesData[i]['imagefile']
            if replace_ext is not None:
                LoadImageName = LoadImageName.replace('.tiff',replace_ext)
            #PILImage = Image.open(os.path.join(ImageLocation,LoadImageName))
            CopiedImage = cv2.imread( os.path.join(ImageLocation,LoadImageName), -1 ) # np.array(PILImage)
            FloatImage = CopiedImage.astype(np.float32) #/255.0

            if mask is not None:
                channels = 1 if len(FloatImage.shape)==2 else FloatImage.shape[2]
                rgb = np.zeros((*FloatImage.shape[:2],3))
                rgb[:,:,:channels] = FloatImage
                rgba = np.stack((rgb[:,:,0],rgb[:,:,1],rgb[:,:,2],mask),axis=-1)
                FloatImage = rgba

            img_list.append(FloatImage)


        min_max_median = get_min_max_median( img_list )

        if adjust_mean:
            # adjust the mean
            img_list = hdr_mean_adjust( img_list )

        # read poses matrices and use the adjusted images
        poses = []
        if len(PoseFileData['images']) > 0:
            for i in range (0,NoofPoses):
                
                PoseMatrix = PoseFileImagesData[i]['M3x4']
                PoseMatrixNumpyArray = np.array([], dtype=np.float32)
                for k in range(0,len(PoseMatrix)):
                    PoseMatrixNumpyArray = np.append(PoseMatrixNumpyArray, np.asarray(PoseMatrix[k],dtype=np.float32))
                PoseMatrixNumpyArray = np.append(PoseMatrixNumpyArray, np.asarray([0.0,0.0,0.0,1.0],dtype=np.float32))
                PoseMatrixNumpyArray = PoseMatrixNumpyArray.reshape(4,4)
                PoseMatrixNumpyArray = PoseMatrixNumpyArray.transpose()
                poses.append(PoseMatrixNumpyArray.copy())

                img = ud.undistort( img_list[i] ) if ud else img_list[i]


                aos.addView(img, poses[i], PoseFileImagesData[i]['imagefile'])
    return img_list, poses

def compute_K_matrix(new_size=(512,512),f_factor=.95):
    px = new_size[0]/2.0
    py = new_size[1]/2.0
    fx = new_size[0]/f_factor
    fy = new_size[1]/f_factor

    # projection matrix:
    new_K = np.array( [
            [fx, 0,  px, 0], # x needs to be flipped if images are flipped (np.flip(img,1))
            [0, fy, py, 0],
            [0, 0, 1.0, 0],
            [0, 0,   0, 1]
        ] )

    return new_K

def get_min_max_median( image_list ):
    """
    adjusting the mean and min/max of float32 images
    """
    #print()
    medians = np.zeros(len(image_list),dtype=np.float32)
    for i in range(len(image_list)):
        medians[i] = np.median(image_list[i])

    overall_median = np.median(medians)

    img_minmax = (math.inf,-math.inf)
    adj_minmax = (math.inf,-math.inf)
    for i in range(len(image_list)):
        adj_value = overall_median - medians[i] # correction value to adjust the mean/median of all images
        img_minmax = ( np.min([np.amin(image_list[i]),img_minmax[0]]), np.max([np.amax(image_list[i]),img_minmax[1]]) )
        adj_minmax = ( np.min([np.amin(image_list[i])+adj_value,adj_minmax[0]]), np.max([np.amax(image_list[i])+adj_value,adj_minmax[1]]) )

    return { 'median': overall_median, 'min': img_minmax[0], 'max': img_minmax[1], 'adj_min': adj_minmax[0], 'adj_max': adj_minmax[1] }


def hdr_mean_adjust( image_list ):
    """
    adjusting the mean and min/max of float32 images
    """
    #print()
    medians = np.zeros(len(image_list),dtype=np.float32)
    for i in range(len(image_list)):
        medians[i] = np.median(image_list[i])

    overall_median = np.median(medians)

    img_minmax = (math.inf,-math.inf)
    for i in range(len(image_list)):
        image_list[i] += overall_median - medians[i]
        img_minmax = ( np.min([np.amin(image_list[i]),img_minmax[0]]), np.max([np.amax(image_list[i]),img_minmax[1]]) )

    for i in range(len(image_list)):
        image_list[i] -= img_minmax[0]
        image_list[i] /= (img_minmax[1] - img_minmax[0])
        #img_minmax = ( np.min([np.amin(image_list[i]),img_minmax[0]]), np.max([np.amax(image_list[i]),img_minmax[1]]) )

    return image_list

def minmax_of_images_in_folder( folder ):
    img_minmax = (math.inf,-math.inf)

    for filename in os.listdir(folder):
        PILImage = Image.open(os.path.join(folder,filename))
        cv_image = np.array(PILImage).astype(np.float32)

        img_minmax = ( np.min([np.amin(cv_image),img_minmax[0]]), np.max([np.amax(cv_image),img_minmax[1]]) )
    
    return img_minmax
