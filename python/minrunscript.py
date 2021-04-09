print('ProgramStarted')
import json
import numpy as np
import os
import cv2
from PIL import Image
import time
import pyaos
import glm
print('pyaos Import')
virtualcamerapose = np.zeros((4,4),dtype=np.float32)
def ReadJsonPosesFiles(PyClassObject,PosesFilePath,ImageLocation):
    with open(PosesFilePath) as PoseFile:
        PoseFileData = json.load(PoseFile)
        NoofPoses = len(PoseFileData['images'])
        PoseFileImagesData = PoseFileData['images']
        HalfValue = int(round(len(PoseFileData['images'])/2))
        print('HalfValue',HalfValue)
        if len(PoseFileData['images']) > 0:
            for i in range (0,len(PoseFileData['images'])):
                ImageName = PoseFileImagesData[i]['imagefile']
                LoadImageName = ImageName
                LoadImageName = ImageName.replace('.tiff','.png')
                #Convert List of List to Np array
                PoseMatrix = PoseFileImagesData[i]['M3x4']
                PoseMatrixNumpyArray = np.array([], dtype=np.float32)
                for k in range(0,len(PoseMatrix)):
                    PoseMatrixNumpyArray = np.append(PoseMatrixNumpyArray, np.asarray(PoseMatrix[k],dtype=np.float32))
                PoseMatrixNumpyArray = np.append(PoseMatrixNumpyArray, np.asarray([0.0,0.0,0.0,1.0],dtype=np.float32))
                PoseMatrixNumpyArray = PoseMatrixNumpyArray.reshape(4,4)
                PoseMatrixNumpyArray = PoseMatrixNumpyArray.transpose()
                #print('InverseViewMatrix',InverseViewMatrix[0][3],InverseViewMatrix[1][3],InverseViewMatrix[2][3])
                #print('ViewMatrixArrayfrompy Shape',ViewMatrixArrayfrompy.shape)
                #print('ViewMatrixArray',PoseMatrixNumpyArray)
                #print('len(PoseFileData[images]',)
                #print('LoadImageName', LoadImageName)
                PILImage = Image.open(os.path.join(ImageLocation,LoadImageName))
                #PILImage = cv2.imread(os.path.join(ImageLocation,LoadImageName))
                CopiedImage = np.array(PILImage)
                OpencvImage = CopiedImage.astype(np.float32) / 255.0
                #print('Image Data Loading')
                if ( i == HalfValue):
                    #print('AddingCameraValue')
                    print('ViewMatrixArray of', i, 'index is ', PoseMatrixNumpyArray)
                    vpose = PoseMatrixNumpyArray.copy()
                    print('virtualcamerapose of', i, 'index is ', vpose)
                    #inversevirtualcamerapose = np.linalg.inv(virtualcamerapose)
                    Posvec = glm.vec3(glm.inverse(vpose)[3])
                    Upvec = glm.vec3(glm.inverse(vpose)[1])
                    FrontVec = glm.vec3(glm.inverse(vpose)[2])
                    virtualcamerapose = np.array(glm.lookAt(Posvec, Posvec + FrontVec, Upvec))
                    print('inverse virtualcamerapose of', i, 'index is ', np.linalg.inv(vpose))
                    #print('virtualcamerapose when copy',virtualcamerapose)
                    #UPPosx.append(0.0)
                    #UPPosy.append(1.0)
                    #UPPosz.append(1.0)
                #print('ViewMatrixArray',str(ViewMatrixArray[0]),str(ViewMatrixArray[1]),str(ViewMatrixArray[2]),str(ViewMatrixArray[3]),str(ViewMatrixArray[4]),str(ViewMatrixArray[5]),str(ViewMatrixArray[6]),str(ViewMatrixArray[7]),str(ViewMatrixArray[8]),str(ViewMatrixArray[9]),str(ViewMatrixArray[10]),str(ViewMatrixArray[11]))
                #print(PoseMatrixNumpyArray.shape)
                #print(PoseMatrixNumpyArray.dtype)
                #print(type(PoseMatrixNumpyArray))
                PyClassObject.addView(OpencvImage, PoseMatrixNumpyArray, ImageName)
    return NoofPoses, virtualcamerapose

if __name__ == '__main__':
    CameraPosx = []
    CameraPosy = []
    CameraPosz = []
    UPPosx = []
    UPPosy = []
    UPPosz = []

    #PosesFilePath = '../data/Hellmonsoedt_pose_corr_30.json'
    #ImageLocation = '../data/Hellmonsoedt_ldr_r512'
    #ObjModelPath = '../data/dem.obj'
    #ObjModelImagePath = '../data/T20200207F2/dem.png'
    #PosesFilePath = 'D:/RESILIO/ANAOS/SITES/Test20201020F1/NewNormalization/SimulationPoses/4.json'
    #ImageLocation = 'D:/RESILIO/ANAOS/SITES/Test20201020F1/Image/4'
    #ObjModelPath = 'D:/RESILIO/ANAOS/SITES/Test20201020F1/LFR/dem.obj'
    PosesFilePath = '../data/Test20201022F1/SimulationPoses/4.json'
    ImageLocation = '../data/Test20201022F1/UndistortedLDRImages/4/'
    ObjModelPath = '../data/Test20201022F1/LFR/dem.obj'
    #ObjModelImagePath = '../data/FlightResults/Test20201013_Broadleaf1/LFR/dem.png'
    #CheckImageRead = cv2.imread('/home/pi/PyCLFR_AutoDrone/glesLFR/data/T20200207F2/thermal_hdr512/20200207_124519.tiff',0)
    #print('CheckImageRead',type(CheckImageRead))
    FocalLength = 50.815436217896945
    window = pyaos.PyGlfwWindow(512,512,'AOS') # make sure there is an OpenGL context
    PyLFClass = pyaos.PyAOS(512,512,FocalLength,10)
    PyLFClass.loadDEM(ObjModelPath)
    NoofPosesread , virtualcamerapose = ReadJsonPosesFiles(PyLFClass,PosesFilePath,ImageLocation)
    #print('virtualcamerapose returned',virtualcamerapose)
    NoofPoses = PyLFClass.getViews()
    print('NoofPoses',NoofPoses)
    HalfValue = int(round(NoofPoses)/2)
    cameraids = np.array([],dtype=np.uintc)
    print('virtualcamerapose from main',virtualcamerapose)
    ImageReturned1 = PyLFClass.render(virtualcamerapose, FocalLength, cameraids)
    ImageReturned1[:,:,0] = ImageReturned1[:,:,0] / ImageReturned1[:,:,3]
    ImageReturned1[:,:,1] = ImageReturned1[:,:,1] / ImageReturned1[:,:,3]
    ImageReturned1[:,:,2] = ImageReturned1[:,:,2] / ImageReturned1[:,:,3]
    ImageConverted = cv2.normalize(ImageReturned1[:,:,0:3], None, 0,255, cv2.NORM_MINMAX, cv2.CV_8UC3)
    cv2.imwrite('ImageRendered.png', ImageConverted)
    #cv2.imwrite('ImageRendered.png', (ImageReturned1[:,:,0] / ImageReturned1[:,:,3] * 255).astype(np.uint8))
    PyLFClass.display(True)

    vP = PyLFClass.getPose(17)
    print('virtualcamerapose with getPose: ', repr((vP)) )

    vPo = PyLFClass.getPosition(17)
    print('virtual camera Poition with getPosition: ', repr(vPo) )

    vPu = PyLFClass.getUp(17)
    print('virtual camera Poition with getUp: ', repr(vPu) )

    vPF = PyLFClass.getForward(17)
    print('virtual camera Poition with getForward: ', repr(vPF) )

    ImageReturned2 = PyLFClass.getXYZ()
    #ImageConverted = cv2.normalize(ImageReturned2[:,:,0:3], None, 0,1, cv2.NORM_MINMAX, cv2.CV_8UC3)
    #cv2.imwrite('DEMImage.png', ImageConverted)
    '''
    #Process for Generating and Running LFR from Py
    #1) create a Python Light Field Class which in turns generate C++ Light Field Class
        # Input is Light Field Class of certain size where names, poses and textureid are allocated certain space

        # PyLFClass = glesLFR_Indrajit.PyLightfieldClass(0)

        You could also allocate space for them later using allocate function

        # PyLFClass.Py_allocate(LightFieldLength)
    #2) set focal length and camera projection matrix by passing focal length to set camerafocallength and then setting projection matrix

        # PyLFClass.Py_setCameraFocalLength(FocalLength)
        # PyLFClass.Py_setProjectionMatrix()
    #3) Initialize Renderer

        # PyLFClass.posespushback(np.array(PoseMatrixNumpyArray)).RenderInitializeP1()
    #4) set poses in the light field class using pushback for first time and then accesing using index later on

        # PyLFClass.posespushback(np.array(PoseMatrixNumpyArray))
        or 
        # PyLFClass.posesIndex(np.array(PoseMatrixNumpyArray))

    #5) Load Dem Model by passing dem.obj file full path including name and dem.png full path including name

        # ObjModelPath = '../data/T20200207F2/dem.obj'
        # ObjModelImagePath = '../data/T20200207F2/dem.png'
        # PyLFClass.Py_LoadDemModel(ObjModelPath,ObjModelImagePath)

    #6) Now Load Images one by one by passing the numpy array used to read the image and depending on the index you want to place the image in the renderer either 
    #   generate texture id or just bind texture id to the image to existing texture id location by passing index of location from 0 and height width and no of channels of the loaded image

        # PyLFClass.LoadImageToC_8bit_1ch(Image)
        # PyLFClass.Py_GenrateTextureID()
        # PyLFClass.Py_BindImageWithTextureID(i,height,width,nrComponents)

    #7) Repeat Above step 6 and 4 till all images and its corresponding Poses are loaded

    #8) Finally initialize second part of renderer

        # PyLFClass.RenderInitializeP2()

    #9) Step 1,2,3,8 are only needed once whereas part of step 1 and step 5,6 has to be repeated to add or change image and its pose in the renderer. Step 4 is only required again if location is changed

    #10) Get Rendered Image from the renderer by calling 

        # ImageReturned1 = PyLFClass.RenderImageOnce('RenderedImage1.png')

    #11) Finally terminate the renderer using 

        # PyLFClass.TerminateRendererOnceFinished()



    '''
    del(PyLFClass)
