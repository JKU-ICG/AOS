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
    ctypedef struct mat:
        pass
    ctypedef struct mat4:
        pass
    ctypedef struct vec3:
        pass
cdef extern from "../include/glm/gtc/type_ptr.hpp":
    mat4 make_mat4(const float  *ptr)
    

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

cdef extern from "../src/image.cpp":
    # ToDo -> this here definitlely is wrong right now.
    Image make_image(int w, int h, int c)
    void copy_image_from_bytes(Image im, char *pdata)
    void copy_image_from_float(Image im, char *pdata)
    void free_image(Image m)

cdef class PyAOS: # defines a python wrapper to the C++ class
    cdef AOS* thisptr # thisptr is a pointer that will hold to the instance of the C++ class
    cdef float *pyfloatarray
    #cdef np.ndarray[float, ndim=2, mode="c"] cinputimage
    def __cinit__(self, unsigned int width, unsigned int height, float fovDegree, int preallocate_images): # defines the python wrapper class' init function
        self.thisptr = new AOS(width, height, fovDegree, preallocate_images) # creates an instance of the C++ class and puts allocates the pointer to this
    def __dealloc__(self): # defines the python wrapper class' deallocation function (python destructor)
        del self.thisptr # destroys the reference to the C++ instance (which calls the C++ class destructor
    def pyloadDEM(self, objmodelpath):
        self.thisptr.loadDEM(objmodelpath.encode())
    def pyaddView(self, readimage, camerapose, pyImagename):
        cdef Image pyImage
        cdef mat4 pyPose
        cdef np.ndarray[float, ndim=1, mode='c'] TempPoseArray
        #TempRenderedImage = np.zeros((self.LFRResolutionHeight,self.LFRResolutionWidth,4), dtype=np.float32)
        height = readimage.shape[0]
        width = readimage.shape[1]
        if len(readimage.shape) == 2 :
            channels = 1
        else :
            channels = readimage.shape[2]
        #TODO Create an Image struct in C
        pyImage  = make_image(width, height,channels)
        #TODO First deliniete numpy array to Contiguous C array and than copy --- Define Input Vector
        copy_image_from_float(pyImage , readimage.tobytes()) ### TODO maybe use memcopy here
        free_image(pyImage)
        
        #cdef float *data
        FlattenPoseArray = camerapose.flatten()
        TempPoseArray = np.asarray(FlattenPoseArray, dtype = np.float32, order="C")
        pyPose =  make_mat4(&TempPoseArray[0])
        #memcpy(data, &Temp1Pose[0], sizeof(float) * 16) ## Not Sure how this would work
        #self.addView(self.pyImage, self.pyPose, pyImagename.encode())
        




cdef class PyGlfwWindow:
    cdef GLFWwindow* windowPointer
    def __cinit__(self, const int width, const int height, appname):
        self.windowPointer = InitGlfwWindow(width, height, appname.encode())
    def __dealloc__(self): # defines the python wrapper class' deallocation function (python destructor)
        DestroyGlfwWindow(self.windowPointer)
#        del self.windowPointer # destroys the reference to the C++ instance (which calls the C++ class destructor