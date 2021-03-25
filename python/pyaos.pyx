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
        int w #// width
        int h #// heigth
        int c; #// number of channels
        float *data; #// data

cdef extern from "../src/glm_utils.cpp":
    mat4 make_mat4_from_float(char *pdata)
    mat4 make_mat4_from_floatarr(float* pdata)
    vec3 make_vec3_from_float(char* pdata)
    float* get_float_ptr(mat4* m)
    float* get_float_ptr(vec3* m)

cdef extern from "../src/py_utils.cpp":
    # ToDo -> this here definitlely is wrong right now.
    GLFWwindow* InitGlfwWindow(const int width, const int height, const char* appname)
    void DestroyGlfwWindow(GLFWwindow* window)
    Image py_make_image(int w, int h, int c)
    void py_copy_image_from_bytes(Image im, char *pdata)
    void py_copy_image_from_float(Image im, char *pdata)
    void py_copy_image_to_float(Image im, float *pdata)
    void py_free_image(Image m)
    Image py_float_to_image(int w, int h, int c, float *data)
    

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
        print('Add New Image')
        cdef Image pyImage
        cdef mat4 pyPose
        height = readimage.shape[0]
        width = readimage.shape[1]
        if len(readimage.shape) == 2 :
            channels = 1
        else :
            channels = readimage.shape[2]
        pyImage  = py_make_image(width, height,channels)
        py_copy_image_from_float(pyImage , readimage.tobytes())
        #cdef np.ndarray[float, ndim=3, mode='c'] TempImage
        #TempImage = np.asarray(readimage, dtype=np.float32, order='c')
        #pyImage = py_float_to_image(width, height, channels, &TempImage[0,0,0])
        print('camerapose', camerapose)
        #cdef np.ndarray[float, ndim=1, mode='c'] TempPose
        #TempPose = np.asarray(camerapose.flatten(), dtype=np.float32, order='c')
        #pyPose =  make_mat4_from_floatarr(&TempPose[0])
        pyPose =  make_mat4_from_float(camerapose.astype(np.float32).tobytes())
        self.thisptr.addView(pyImage, pyPose, pyImagename.encode())
        py_free_image(pyImage)
    
    def getPose(self, poseindex):
        cdef mat4 pyPose
        pyPose = self.thisptr.getPose(poseindex)
        #ToDo Return float array which should be converted to numpyarray
        cdef float[::1] arr = <float [:16]> get_float_ptr(&pyPose) # see https://stackoverflow.com/questions/24764048/get-the-value-of-a-cython-pointer
        return np.asarray( arr ).reshape(4,4)
    
    def pysetPose(self, poseindex, camerapose):
        cdef mat4 pyPose
        cdef mat4 returnedpyPose
        pyPose =  make_mat4_from_float(camerapose.tobytes())
        returnedpyPose = self.thisptr.setPose(poseindex, pyPose)
        #ToDo Return float array which should be converted to numpyarray
    
    def getPosition(self, cameraindex):
        cdef vec3 pyPosition
        pyPosition = self.thisptr.getPosition(cameraindex)
        #ToDO Return float array from vec3 which should be converted to numpyarray

        cdef float[::1] arr = <float [:3]> get_float_ptr(&pyPosition) # see https://stackoverflow.com/questions/24764048/get-the-value-of-a-cython-pointer
        return np.asarray( arr ).reshape(3,1)
    
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
        pyImage  = py_make_image(width, height,channels)
        py_copy_image_from_float(pyImage , replacingimage.tobytes()) 
        pyPose =  make_mat4_from_float(replacingpose.tobytes())
        self.thisptr.replaceView(cameraindex, pyImage, pyPose, replacename.encode())
        py_free_image(pyImage)
    
    def pyrenderwithpose(self, virtualcamerapose, virtualcamerafieldofview, cameraids):
        cdef vector[unsigned int] ids = np.asarray(cameraids, dtype = np.uintc, order="C")

        cdef mat4 pyvirtualPose =  make_mat4_from_float(virtualcamerapose.astype(np.float32).tobytes())
        img = self.thisptr.render(pyvirtualPose, virtualcamerafieldofview, ids)

        return np.asarray( <float [:(img.w*img.h*img.c)]>img.data ).reshape(img.w,img.h,img.c)  # see https://stackoverflow.com/questions/59666307/convert-c-vector-to-numpy-array-in-cython-without-copying
    
    def pygetXYZ(self):
        cdef Image pyrenderedDEMImage
        pyrenderedDEMImage = self.thisptr.getXYZ()
        cdef np.ndarray[float, ndim=3, mode='c'] TempRenderedImage
        TempRenderedImage = np.zeros((self.LFRResolutionHeight,self.LFRResolutionWidth,4), dtype=np.float32)
        py_copy_image_to_float(pyrenderedDEMImage, &TempRenderedImage[0,0,0])
        RedChannelAfterToneMapped = TempRenderedImage[:,:,0:3]
        ImageConverted = cv2.normalize(RedChannelAfterToneMapped, None, 0,255, cv2.NORM_MINMAX, cv2.CV_8UC3)
        py_free_image(pyrenderedDEMImage)
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