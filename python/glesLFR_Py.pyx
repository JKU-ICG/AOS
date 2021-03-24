from libcpp.vector cimport vector
from libcpp.string cimport string
import numpy as np
cimport numpy as np
import json
import os
import cv2

'''
cdef extern from "glesLFR_Indrajit.cpp":
    void RendererInit()
    void Completerender()
    void TerminateRenderer()
    void LoadDemModel(string ModelFile, string Modelimage)
    void PrintPyLightFieldInstanceInfo(Lightfield *PyLF)

def Py_Initiaterender():
    print('InitiateRender')
    RendererInit()

def Py_Completerender():
    Completerender()

def Py_TerminateRenderer():
    TerminateRenderer()

def Py_LoadDemModel(string OBJModelPath,string OBJModelImagePath):
    LoadDemModel(OBJModelPath.encode(),OBJModelImagePath.encode())

def Py_PrintPyLightFieldInstanceInfo(PyLightfieldClass PyLF):
    PrintPyLightFieldInstanceInfo(PyLF.thisptr)
'''
cdef extern from "glesLFR.cpp": # defines the source C++ file
    cdef cppclass Lightfield:
        vector[string] pynames
        vector[vector[double]] vectorposes
        unsigned char *image_to_bind
        float *image_to_bind_16
        float camerafocallength;
        vector[unsigned int] ogl_textures

        Lightfield(int preallocate) except +
        void allocate(int allocate)
        void GenrateTextureID()
        void DeleteLastTextureID()
        void BindImageWithTextureID(unsigned int index,unsigned int width, unsigned int height, unsigned int nrComponents, unsigned int nrbits)
        void Check16bitImageLoading(unsigned int index,unsigned int width, unsigned int height, unsigned int nrComponents, unsigned int nrbits);
        void RendererInitializationPart1(unsigned int LFRHeigth, unsigned int LFRWidth )
        void RendererInitializationPart2()
        void RenderOnce(float *RenderedImage, float *RenderedImageMin, float *RenderedImageMax)
        void RenderOnceGetDEMInfo(float *RenderedImage)
        void RenderLoop(float *RenderedImage, float *RenderedImageMin, float *RenderedImageMax)
        void ProjectSingleImage(float *RenderedImage, float *RenderedImageMin, float *RenderedImageMax, unsigned int ImageIndex)
        void ProjectCenterImage(float *RenderedImage, float *RenderedImageMin, float *RenderedImageMax, unsigned int ImageIndex)
        void LoadDemModel(string ObjFile, unsigned int width, unsigned int height, unsigned int nrComponents)
        void LFRTerminateRenderer()
        void SetProjectionMatrix()
        unsigned int GetPosesSize()
        void LFUpdateCameraPosition(float posX, float posY, float posZ)
        void LFUpdateWorldUpCoordinate(float upX, float upY, float upZ)
        void LFUpdateCameraYaw(float yaw)
        void LFUpdateCameraPitch(float pitch)
        void LFUpdateCameraZoom(float zoom)

cdef class PyLightfieldClass: # defines a python wrapper to the C++ class
    cdef Lightfield* thisptr # thisptr is a pointer that will hold to the instance of the C++ class
    cdef unsigned char *PyCheckArray
    cdef float *PyCheckArray_short
    cdef unsigned int LFRResolutionHeight
    cdef unsigned int LFRResolutionWidth
    def __cinit__(self, int preallocatedvalue): # defines the python wrapper class' init function
        self.thisptr = new Lightfield(preallocatedvalue) # creates an instance of the C++ class and puts allocates the pointer to this
    def __dealloc__(self): # defines the python wrapper class' deallocation function (python destructor)
        del self.thisptr # destroys the reference to the C++ instance (which calls the C++ class destructor
    def PySetLFRResolution(self,Height,Width): #Set Resolution
        self.LFRResolutionHeight = Height  # destroys the reference to the C++ instance (which calls the C++ class destructor
        self.LFRResolutionWidth = Width
    def Py_allocate(self, int Py_NameSize):
        self.thisptr.allocate(Py_NameSize)
    def Py_GetPosesSize(self):
        return self.thisptr.vectorposes.size()
    def Py_DeleteLastTextureID(self):
        self.thisptr.DeleteLastTextureID()
    def Py_setCameraFocalLength(self, float camerafocallength):
        self.thisptr.camerafocallength = camerafocallength
    def Py_setProjectionMatrix(self):
        self.thisptr.SetProjectionMatrix()
    def namespushback(self, namestring):
        self.thisptr.pynames.push_back(namestring.encode())
    def posespushback(self, np.ndarray[double, ndim=1, mode="c"] InputVector not None):
        cdef vector[double] InputVectorC = InputVector
        self.thisptr.vectorposes.push_back(InputVectorC)
    def namesIndex(self, index, namestring):
        self.thisptr.pynames[index] = namestring.encode()
    def posesIndex(self, index, np.ndarray[double, ndim=1, mode="c"] InputVector not None):
        cdef vector[double] InputVectorC = InputVector
        self.thisptr.vectorposes[index] = InputVectorC
    def LoadImageToC_8bit_1ch(self,np.ndarray[unsigned char, ndim=2, mode="c"] InputVector not None):
        cdef unsigned char[:,::1] InputVectorC = InputVector
        self.PyCheckArray = &InputVectorC[0,0]
        self.thisptr.image_to_bind = self.PyCheckArray
    def LoadImageToC_8bit_3ch(self,np.ndarray[unsigned char, ndim=3, mode="c"] InputVector not None):
        cdef unsigned char[:,:,::1] InputVectorC = InputVector
        self.PyCheckArray = &InputVectorC[0,0,0]
        self.thisptr.image_to_bind = self.PyCheckArray
    def LoadImageToC_16bit_1ch(self,np.ndarray[float, ndim=2, mode="c"] InputVector not None):
        cdef float[:,::1] InputVectorC = InputVector
        self.PyCheckArray_short = &InputVectorC[0,0]
        self.thisptr.image_to_bind_16 = self.PyCheckArray_short
    def LoadImageToC_16bit_3ch(self,np.ndarray[unsigned char, ndim=3, mode="c"] InputVector not None):
        cdef unsigned char[:,:,::1] InputVectorC = InputVector
        self.PyCheckArray = &InputVectorC[0,0,0]
        self.thisptr.image_to_bind = self.PyCheckArray
    def RenderInitializeP1(self):
        self.thisptr.RendererInitializationPart1(self.LFRResolutionHeight,self.LFRResolutionWidth)
    def Py_GenrateTextureID(self):
        self.thisptr.GenrateTextureID()
    def Py_BindImageWithTextureID(self,index, width, height, nrComponents,nrbits):
        self.thisptr.BindImageWithTextureID(index, width, height, nrComponents,nrbits)
    def Py_Check16BitImage(self,index, width, height, nrComponents,nrbits):
        self.thisptr.Check16bitImageLoading(index, width, height, nrComponents,nrbits)
    def RenderInitializeP2(self):
        self.thisptr.RendererInitializationPart2()
    def Py_LoadDemModel(self,ObjModelPath, OBJModelImageName):
        DemImage = cv2.imread(OBJModelImageName,-1)
        DemImage = cv2.flip(DemImage,0)
        
        # height, width, number of channels in image
        height = DemImage.shape[0]
        width = DemImage.shape[1]
        print(len(DemImage.shape))
        if len(DemImage.shape) == 2 :
            nrComponents = 1
            self.LoadImageToC_8bit_1ch(DemImage)
        else :
            nrComponents = DemImage.shape[2]
            self.LoadImageToC_8bit_3ch(DemImage)          
        self.thisptr.LoadDemModel(ObjModelPath.encode(),width, height, nrComponents)
    def GetnamesIndex(self, index):
        namestring = self.thisptr.pynames[index].decode()
        return namestring
    def RenderImageOnce(self, ImageName):
        print('Rendering Scene')
        cdef np.ndarray[float, ndim=3, mode='c'] TempRenderedImage
        TempRenderedImage = np.zeros((self.LFRResolutionHeight,self.LFRResolutionWidth,4), dtype=np.float32)
        cdef np.ndarray[float, ndim=1, mode='c'] TempRenderedImageMin
        TempRenderedImageMin = np.zeros((4,), dtype=np.float32)
        cdef np.ndarray[float, ndim=1, mode='c'] TempRenderedImageMax
        TempRenderedImageMax = np.zeros((4,), dtype=np.float32)
        self.thisptr.RenderOnce(&TempRenderedImage[0,0,0], &TempRenderedImageMin[0] , &TempRenderedImageMax[0])
        print('Rendering Finished')
        print('Center Returend PixelValue',TempRenderedImage[256,256,:])
        RedChannelAfterToneMapped = TempRenderedImage[:,:,0:3]
        ImageConverted = cv2.normalize(RedChannelAfterToneMapped, None, 0,255, cv2.NORM_MINMAX, cv2.CV_8UC3)
        cv2.imwrite(ImageName, ImageConverted)
        print('Image Written')
        return ImageConverted
    def RenderImageOnce_ToneMapped(self, ImageName):
        print('Rendering Integral Scene')
        cdef np.ndarray[float, ndim=3, mode='c'] TempRenderedImage
        TempRenderedImage = np.zeros((self.LFRResolutionHeight,self.LFRResolutionWidth,4), dtype=np.float32)
        cdef np.ndarray[float, ndim=1, mode='c'] TempRenderedImageMin
        TempRenderedImageMin = np.zeros((4,), dtype=np.float32)
        cdef np.ndarray[float, ndim=1, mode='c'] TempRenderedImageMax
        TempRenderedImageMax = np.zeros((4,), dtype=np.float32)
        self.thisptr.RenderOnce(&TempRenderedImage[0,0,0], &TempRenderedImageMin[0] , &TempRenderedImageMax[0])
        print('Rendering Integral Scene Finished')
        TempRenderedImage -= [TempRenderedImageMin[0], TempRenderedImageMin[0], TempRenderedImageMin[0],0] #Currently Red Channel only Change accordingly
        TempRenderedImage[TempRenderedImage < 0.0] = 0.0
        TempRenderedImage /= [(TempRenderedImageMax[0] - TempRenderedImageMin[0]), (TempRenderedImageMax[0] - TempRenderedImageMin[0]),(TempRenderedImageMax[0] - TempRenderedImageMin[0]),1]
        #cv2.imwrite("imgOut.bmp",  a)
        RedChannelAfterToneMapped = TempRenderedImage[:,:,0:3]
        ImageConverted = cv2.normalize(RedChannelAfterToneMapped, None, 0,255, cv2.NORM_MINMAX, cv2.CV_8UC3)
        cv2.imwrite(ImageName, ImageConverted)
        print('Image Written')
        return ImageConverted
    def RenderGetDemInfo(self):
        print('Rendering DEM')
        cdef np.ndarray[float, ndim=3, mode='c'] TempRenderedImage
        TempRenderedImage = np.zeros((self.LFRResolutionHeight,self.LFRResolutionWidth,4), dtype=np.float32)
        self.thisptr.RenderOnceGetDEMInfo(&TempRenderedImage[0,0,0])
        print('Rendering DEM Finished')
        #print(TempRenderedImage[1,150,:])
        #RedChannelAfterToneMapped = TempRenderedImage[:,:,0:3]
        #ImageConverted = cv2.normalize(RedChannelAfterToneMapped, None, 0,255, cv2.NORM_MINMAX, cv2.CV_8UC3)
        #cv2.imwrite(ImageName, ImageConverted)
        #print('Image Written')
        return TempRenderedImage
    def PyProjectSingleImage(self, ImageIndex):
        print('Projecting Single Image')
        cdef np.ndarray[float, ndim=3, mode='c'] TempRenderedImage
        TempRenderedImage = np.zeros((self.LFRResolutionHeight,self.LFRResolutionWidth,4), dtype=np.float32)
        cdef np.ndarray[float, ndim=1, mode='c'] TempRenderedImageMin
        TempRenderedImageMin = np.zeros((4,), dtype=np.float32)
        cdef np.ndarray[float, ndim=1, mode='c'] TempRenderedImageMax
        TempRenderedImageMax = np.zeros((4,), dtype=np.float32)
        self.thisptr.ProjectSingleImage(&TempRenderedImage[0,0,0], &TempRenderedImageMin[0] , &TempRenderedImageMax[0], ImageIndex )
        print('Projecting Single Image Finished')
        RedChannelAfterToneMapped = TempRenderedImage[:,:,0:3]
        ImageConverted = cv2.normalize(RedChannelAfterToneMapped, None, 0,255, cv2.NORM_MINMAX, cv2.CV_8UC3)
        #cv2.imwrite(ImageName, ImageConverted)
        #print('Image Written')
        return ImageConverted
    def PyProjectCenterImage(self, ImageIndex):
        print('Projecting Center Image')
        cdef np.ndarray[float, ndim=3, mode='c'] TempRenderedImage
        TempRenderedImage = np.zeros((self.LFRResolutionHeight,self.LFRResolutionWidth,4), dtype=np.float32)
        cdef np.ndarray[float, ndim=1, mode='c'] TempRenderedImageMin
        TempRenderedImageMin = np.zeros((4,), dtype=np.float32)
        cdef np.ndarray[float, ndim=1, mode='c'] TempRenderedImageMax
        TempRenderedImageMax = np.zeros((4,), dtype=np.float32)
        self.thisptr.ProjectCenterImage(&TempRenderedImage[0,0,0], &TempRenderedImageMin[0] , &TempRenderedImageMax[0], ImageIndex )
        print('Projecting Center Image Finished')
        RedChannelAfterToneMapped = TempRenderedImage[:,:,0:3]
        ImageConverted = cv2.normalize(RedChannelAfterToneMapped, None, 0,255, cv2.NORM_MINMAX, cv2.CV_8UC3)
        #cv2.imwrite(ImageName, ImageConverted)
        #print('Image Written')
        return ImageConverted
    def PyRenderLoop(self, ImageIndex):
        print('Rendering in Loop')
        cdef np.ndarray[float, ndim=3, mode='c'] TempRenderedImage
        TempRenderedImage = np.zeros((self.LFRResolutionHeight,self.LFRResolutionWidth,4), dtype=np.float32)
        cdef np.ndarray[float, ndim=1, mode='c'] TempRenderedImageMin
        TempRenderedImageMin = np.zeros((4,), dtype=np.float32)
        cdef np.ndarray[float, ndim=1, mode='c'] TempRenderedImageMax
        TempRenderedImageMax = np.zeros((4,), dtype=np.float32)
        self.thisptr.RenderLoop(&TempRenderedImage[0,0,0], &TempRenderedImageMin[0] , &TempRenderedImageMax[0] )
        print('Rendering in Loop')
        RedChannelAfterToneMapped = TempRenderedImage[:,:,0:3]
        ImageConverted = cv2.normalize(RedChannelAfterToneMapped, None, 0,255, cv2.NORM_MINMAX, cv2.CV_8UC3)
        #cv2.imwrite(ImageName, ImageConverted)
        #print('Image Written')
        return ImageConverted    
    def TerminateRendererOnceFinished(self):
        self.thisptr.LFRTerminateRenderer()

    def Py_LFUpdateCameraPosition(self,posX,posY,posZ):
        self.thisptr.LFUpdateCameraPosition(posX,posY,posZ)

    def Py_LFUpdateWorldUpCoordinate(self,upX,upY,upZ):
        self.thisptr.LFUpdateWorldUpCoordinate(upX,upY,upZ)
    
    def Py_LFUpdateCameraYaw(self,yaw):
        self.thisptr.LFUpdateCameraYaw(yaw)
    
    def Py_LFUpdateCameraPitch(self,pitch):
        self.thisptr.LFUpdateCameraPitch(pitch)

    def Py_LFUpdateCameraZoom(self,zoom):
        self.thisptr.LFUpdateCameraZoom(zoom)




    
        

