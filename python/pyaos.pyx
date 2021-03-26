from libcpp.vector cimport vector
from libcpp.string cimport string
from libc.stdlib cimport malloc , free
from libc.string cimport memcpy 
from libcpp cimport bool
from cython.view cimport array as cvarray
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
    void get_float_ptr_mat(mat4* m, float* floatarr)
    void get_float_ptr_vec(vec3* m, float* floatarr)

cdef extern from "../src/py_utils.cpp":
    ctypedef struct GLFWwindow :
        pass
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
    def __cinit__(self, unsigned int width, unsigned int height, float fovDegree, int preallocate_images=0): # defines the python wrapper class' init function
        self.LFRResolutionHeight = height  # destroys the reference to the C++ instance (which calls the C++ class destructor
        self.LFRResolutionWidth = width
        self.thisptr = new AOS(width, height, fovDegree, preallocate_images) # creates an instance of the C++ class and puts allocates the pointer to this
    def __dealloc__(self): # defines the python wrapper class' deallocation function (python destructor)
        del self.thisptr # destroys the reference to the C++ instance (which calls the C++ class destructor
    def loadDEM(self, objmodelpath):
        self.thisptr.loadDEM(objmodelpath.encode())
    def addView(self, readimage, camerapose, pyImagename):
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
        pyPose =  make_mat4_from_float(camerapose.astype(np.float32).tobytes())
        self.thisptr.addView(pyImage, pyPose, pyImagename.encode())
        py_free_image(pyImage)
    
    def getPose(self, poseindex):
        cdef mat4 pyPose
        cdef np.ndarray[float, ndim=1, mode='c'] floatarr
        floatarr = np.zeros((16,), dtype=np.float32)
        pyPose = self.thisptr.getPose(poseindex)
        get_float_ptr_mat(&pyPose,&floatarr[0])
        return floatarr[:].reshape(4,4)
        #cdef float[::1] arr = <float [:16]> floatarr # see https://stackoverflow.com/questions/24764048/get-the-value-of-a-cython-pointer
        #return np.asarray( floatarr ).reshape(4,4)
    
    def setPose(self, poseindex, camerapose):
        cdef mat4 pyPose
        cdef mat4 returnedpyPose
        cdef np.ndarray[float, ndim=1, mode='c'] floatarr
        floatarr = np.zeros((16,), dtype=np.float32)
        pyPose =  make_mat4_from_float(camerapose.astype(np.float32).tobytes())
        returnedpyPose = self.thisptr.setPose(poseindex, pyPose)
        get_float_ptr_mat(&pyPose,&floatarr[0])
        return floatarr[:].reshape(4,4)
        #cdef float[::1] arr = <float [:16]> floatarr # see https://stackoverflow.com/questions/24764048/get-the-value-of-a-cython-pointer
        #return np.asarray( arr ).reshape(4,4)
    
    def getPosition(self, cameraindex):
        cdef vec3 pyPosition
        cdef np.ndarray[float, ndim=1, mode='c'] floatarr
        floatarr = np.zeros((3,), dtype=np.float32)
        pyPosition = self.thisptr.getPosition(cameraindex)
        get_float_ptr_vec(&pyPosition, &floatarr[0])
        return floatarr[:]
        #cdef float[::1] arr = <float [:3]>  floatarr# see https://stackoverflow.com/questions/24764048/get-the-value-of-a-cython-pointer
        #return np.asarray( arr ).reshape(3,1)
    
    def getUp(self, cameraindex):
        cdef vec3 pyUp
        cdef np.ndarray[float, ndim=1, mode='c'] floatarr
        floatarr = np.zeros((3,), dtype=np.float32)
        pyUp = self.thisptr.getUp(cameraindex)
        get_float_ptr_vec(&pyUp, &floatarr[0])
        return floatarr[:]
    
    def getForward(self, cameraindex):
        cdef vec3 pyForward
        cdef np.ndarray[float, ndim=1, mode='c'] floatarr
        floatarr = np.zeros((3,), dtype=np.float32)
        pyForward = self.thisptr.getForward(cameraindex)
        get_float_ptr_vec(&pyForward, &floatarr[0])
        return floatarr[:]
    
    def getName(self, cameraindex):
        cdef string pyname
        pyname = self.thisptr.getName(cameraindex)
        return pyname.decode()
    
    def removeView(self, cameraindex):
        self.thisptr.removeView(cameraindex)
    
    def replaceView(self, cameraindex, replacingimage, replacingpose,replacename):
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
        pyPose =  make_mat4_from_float(replacingpose.astype(np.float32).tobytes())
        self.thisptr.replaceView(cameraindex, pyImage, pyPose, replacename.encode())
        py_free_image(pyImage)
    
    def render(self, virtualcamerapose, virtualcamerafieldofview, cameraids=[]):
        cdef vector[unsigned int] ids = np.asarray(cameraids, dtype = np.uintc, order="C")

        cdef mat4 pyvirtualPose =  make_mat4_from_float(virtualcamerapose.astype(np.float32).tobytes())
        img = self.thisptr.render(pyvirtualPose, virtualcamerafieldofview, ids)
        #cdef np.ndarray[float, ndim=3, mode='c'] floatarr
        #floatarr = np.zeros((self.LFRResolutionHeight,self.LFRResolutionWidth,4), dtype=np.float32)
        #py_copy_image_to_float(img, &floatarr[0,0,0])
        #return floatarr
        return np.asarray( <float [:(img.w*img.h*img.c)]>img.data ).reshape(img.w,img.h,img.c)  # see https://stackoverflow.com/questions/59666307/convert-c-vector-to-numpy-array-in-cython-without-copying
    
    def getXYZ(self):
        demimage = self.thisptr.getXYZ()
        return np.asarray( <float [:(demimage.w*demimage.h*demimage.c)]>demimage.data ).reshape(demimage.w,demimage.h,demimage.c)
    
    def display(self, normalize):
        cdef bool normalizeoption = <bint> normalize
        self.thisptr.display(normalizeoption)
    
    def getViews(self):
        NoofViews = self.thisptr.getViews()
        return NoofViews
    
    def getSize(self):
        SizeInfo = self.thisptr.getSize()
        return SizeInfo

cdef class PyGlfwWindow:
    cdef GLFWwindow* windowPointer
    def __cinit__(self, const int width, const int height, appname):
        self.windowPointer = InitGlfwWindow(width, height, appname.encode())
    def __dealloc__(self): # defines the python wrapper class' deallocation function (python destructor)
        DestroyGlfwWindow(self.windowPointer)
#        del self.windowPointer # destroys the reference to the C++ instance (which calls the C++ class destructor