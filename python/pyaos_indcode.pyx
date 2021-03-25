from libcpp.vector cimport vector
from libcpp.string cimport string
from libc.stdlib cimport malloc , free
from libc.string cimport memcpy 
from libcpp cimport bool
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

cdef extern from "../include/glm/glm.hpp" namespace "glm":
    ctypedef struct mat4:
        pass
    ctypedef struct vec3:
        pass   

cdef extern from "../include/GLFW/glfw3.h":
    ctypedef struct GLFWwindow :
        pass
    

cdef extern from "../src/gl_utils.cpp":
    # ToDo -> this here definitlely is wrong right now.
    GLFWwindow* InitGlfwWindow(const int width, const int height, const char* appname)
    void DestroyGlfwWindow(GLFWwindow* window)

cdef extern from "../include/AOS.h": # defines the source C++ file
    cdef cppclass AOS:
        AOS(unsigned int width, unsigned int height, float fovDegree, int preallocate_images) except +
        void loadDEM(string obj_file)
        void addView(Image img, mat4 pose, string name)
        mat4 getPose(unsigned int idx)
        mat4 setPose(unsigned int idx, const mat4 pose)
        const vec3 getPosition(const unsigned int index)
        const vec3 getUp(const unsigned int index)
        const vec3 getForward(const unsigned int index)
        string getName(unsigned int idx)
        void removeView(unsigned int idx)
        void replaceView(unsigned int idx, Image img, mat4 pose, string name)

        Image render(const mat4 virtual_pose, const float virtual_fovDegree, const vector[unsigned int] ids)
        Image getXYZ()
        void display(bool normalize)

        unsigned int getViews()
        unsigned int getSize()
    
cdef extern from *:
    ctypedef struct Image:
        pass

cdef extern from "../src/glm_utils.cpp":
    mat4 make_mat4_from_float(char *pdata)
    vec3 make_vec3_from_float(char* pdata)

cdef extern from "../src/image.cpp":
    # ToDo -> this here definitlely is wrong right now.
    Image make_image(int w, int h, int c)
    void copy_image_from_bytes(Image im, char *pdata)
    void copy_image_from_float(Image im, char *pdata)
    void copy_image_to_float(Image im, float *pdata)
    void free_image(Image m)

cdef class PyAOS: # defines a python wrapper to the C++ class
    cdef AOS* thisptr # thisptr is a pointer that will hold to the instance of the C++ class
    cdef float *pyfloatarray
    cdef unsigned int LFRResolutionHeight
    cdef unsigned int LFRResolutionWidth
    def __cinit__(self, unsigned int width, unsigned int height, float fovDegree, int preallocate_images): # defines the python wrapper class' init function
        self.LFRResolutionHeight = height  # destroys the reference to the C++ instance (which calls the C++ class destructor
        self.LFRResolutionWidth = width
        self.thisptr = new AOS(width, height, fovDegree, preallocate_images) # creates an instance of the C++ class and puts allocates the pointer to this
    def __dealloc__(self): # defines the python wrapper class' deallocation function (python destructor)
        del self.thisptr # destroys the reference to the C++ instance (which calls the C++ class destructor
    def pyloadDEM(self, objmodelpath):
        self.thisptr.loadDEM(objmodelpath.encode())
    def pyaddView(self, readimage, camerapose, pyImagename):
        cdef Image pyImage
        cdef mat4 pyPose
        height = readimage.shape[0]
        width = readimage.shape[1]
        if len(readimage.shape) == 2 :
            channels = 1
        else :
            channels = readimage.shape[2]
        pyImage  = make_image(width, height,channels)
        copy_image_from_float(pyImage , readimage.tobytes()) 
        pyPose =  make_mat4_from_float(camerapose.tobytes())
        self.thisptr.addView(pyImage, pyPose, pyImagename.encode())
        free_image(pyImage)
    
    def pygetPose(self, poseindex):
        cdef mat4 pyPose
        pyPose = self.thisptr.getPose(poseindex)
        #ToDo Return float array which should be converted to numpyarray
    
    def pysetPose(self, poseindex, camerapose):
        cdef mat4 pyPose
        cdef mat4 returnedpyPose
        pyPose =  make_mat4_from_float(camerapose.tobytes())
        returnedpyPose = self.thisptr.setPose(poseindex, pyPose)
        #ToDo Return float array which should be converted to numpyarray
    
    def pygetPosition(self, cameraindex):
        cdef vec3 pyPosition
        pyPosition = self.thisptr.getPosition(cameraindex)
        #ToDO Return float array from vec3 which should be converted to numpyarray
    
    def pygetUp(self, cameraindex):
        cdef vec3 pyUp
        pyUp = self.thisptr.getUp(cameraindex)
        #ToDO Return float array from vec3 which should be converted to numpyarray
    
    def pygetForward(self, cameraindex):
        cdef vec3 pyForward
        pyForward = self.thisptr.getForward(cameraindex)
        #ToDO Return float array from vec3 which should be converted to numpyarray
    
    def pygetName(self, cameraindex):
        cdef string pyname
        pyname = self.thisptr.getName(cameraindex)
        return pyname.decode()
    
    def pyremoveView(self, cameraindex):
        self.thisptr.removeView(cameraindex)
    
    def pyreplaceView(self, cameraindex, replacingimage, replacingpose,replacename):
        cdef Image pyImage
        cdef mat4 pyPose
        height = replacingimage.shape[0]
        width = replacingimage.shape[1]
        if len(replacingimage.shape) == 2 :
            channels = 1
        else :
            channels = replacingimage.shape[2]
        pyImage  = make_image(width, height,channels)
        copy_image_from_float(pyImage , replacingimage.tobytes()) 
        pyPose =  make_mat4_from_float(replacingpose.tobytes())
        self.thisptr.replaceView(cameraindex, pyImage, pyPose, replacename.encode())
    
    def pyrenderwithpose(self, virtualcamerapose, virtualcamerafieldofview, cameraids):
        cdef Image pyrenderedImage
        cdef mat4 pyvirtualPose
        cdef np.ndarray[double, ndim=1, mode="c"] InputVector
        InputVector = np.asarray(cameraids, dtype = np.uintc, order="C")
        cdef vector[unsigned int] ids = InputVector
        pyvirtualPose =  make_mat4_from_float(virtualcamerapose.tobytes())
        pyrenderedImage = self.thisptr.render(pyvirtualPose, virtualcamerafieldofview, ids)
        cdef np.ndarray[float, ndim=3, mode='c'] TempRenderedImage
        TempRenderedImage = np.zeros((self.LFRResolutionHeight,self.LFRResolutionWidth,4), dtype=np.float32)
        copy_image_to_float(pyrenderedImage, &TempRenderedImage[0,0,0])
        RedChannelAfterToneMapped = TempRenderedImage[:,:,0:3]
        ImageConverted = cv2.normalize(RedChannelAfterToneMapped, None, 0,255, cv2.NORM_MINMAX, cv2.CV_8UC3)
        return ImageConverted
    
    def pygetXYZ(self):
        cdef Image pyrenderedDEMImage
        pyrenderedDEMImage = self.thisptr.getXYZ()
        cdef np.ndarray[float, ndim=3, mode='c'] TempRenderedImage
        TempRenderedImage = np.zeros((self.LFRResolutionHeight,self.LFRResolutionWidth,4), dtype=np.float32)
        copy_image_to_float(pyrenderedDEMImage, &TempRenderedImage[0,0,0])
        RedChannelAfterToneMapped = TempRenderedImage[:,:,0:3]
        ImageConverted = cv2.normalize(RedChannelAfterToneMapped, None, 0,255, cv2.NORM_MINMAX, cv2.CV_8UC3)
        return ImageConverted
    
    def pydisplay(self, normalize):
        cdef bool normalizeoption = <bint> normalize
        self.thisptr.display(normalizeoption)
    
    def pygetViews(self):
        NoofViews = self.thisptr.getViews()
        return NoofViews
    
    def pygetSize(self):
        SizeInfo = self.thisptr.getSize()
        return SizeInfo

cdef class PyGlfwWindow:
    cdef GLFWwindow* windowPointer
    def __cinit__(self, const int width, const int height, appname):
        self.windowPointer = InitGlfwWindow(width, height, appname.encode())
    def __dealloc__(self): # defines the python wrapper class' deallocation function (python destructor)
        DestroyGlfwWindow(self.windowPointer)
#        del self.windowPointer # destroys the reference to the C++ instance (which calls the C++ class destructor