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
#import cv2

cdef extern from "../include/glm/glm.hpp" namespace "glm":
    ctypedef struct mat4:
        pass
    ctypedef struct vec3:
        pass   


cdef extern from "../include/AOS.h": # defines the source C++ file
    cdef cppclass AOS:
        AOS(unsigned int width, unsigned int height, float fovDegree, int preallocate_images) except +
        void loadDEM(string obj_file)
        void setDEMTransformation(const vec3 translation, const vec3 eulerAngles)
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
    def setDEMTransform(self, transl, euler=np.array([0,0,0])):
        cdef vec3 translation
        translation = make_vec3_from_float(np.asarray(transl).astype(np.float32).tobytes())
        cdef vec3 eulerAngles
        eulerAngles = make_vec3_from_float(np.asarray(euler).astype(np.float32).tobytes())
        self.thisptr.setDEMTransformation(translation, eulerAngles)
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
        py_copy_image_from_float(pyImage , np.asarray(readimage).astype(np.float32).tobytes())
        pyPose =  make_mat4_from_float(np.asarray(camerapose).astype(np.float32).tobytes())
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

    def clearViews(self):
        while self.getViews()>0:
            self.removeView(0)
        assert self.getViews()==0

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
        py_copy_image_from_float(pyImage , np.asarray(replacingimage).astype(np.float32).tobytes()) 
        pyPose =  make_mat4_from_float(replacingpose.astype(np.float32).tobytes())
        self.thisptr.replaceView(cameraindex, pyImage, pyPose, replacename.encode())
        py_free_image(pyImage)
    
    def render(self, virtualcamerapose, virtualcamerafieldofview, cameraids=[], flipHorizontal=True, copyImage=True):
        """Renders an AOS image with the specified parameters and returns an image.

        :param pose: pose of the virtual camera as 4 by 4 matrix
        :type pose: array
        :param field_of_view: field of view of the virtual camera in degrees
        :type field_of_view: number
        :param cameraids: view/camera ids used for rendering, defaults to [] which renders with all available views
        :type cameraids: array, optional
        :param flipHorizontal: if True, the rendered image is flipped horizontally to be similar to the views (note: the internal format is flipped), defaults to True
        :type flipHorizontal: bool, optional
        :param copyImage: if True, the returned image is copied before returning, defaults to True
        :type copyImage: bool, optional

        :rtype: numpy.array
        :return: Rendered image
        """
        cdef vector[unsigned int] ids = np.asarray(cameraids, dtype = np.uintc, order="C")

        cdef mat4 pyvirtualPose =  make_mat4_from_float(virtualcamerapose.astype(np.float32).tobytes())
        img = self.thisptr.render(pyvirtualPose, virtualcamerafieldofview, ids)
        #cdef np.ndarray[float, ndim=3, mode='c'] floatarr
        #floatarr = np.zeros((self.LFRResolutionHeight,self.LFRResolutionWidth,4), dtype=np.float32)
        #py_copy_image_to_float(img, &floatarr[0,0,0])
        #return floatarr
        tmp = np.asarray( <float [:(img.w*img.h*img.c)]>img.data ).reshape(img.w,img.h,img.c)  # see https://stackoverflow.com/questions/59666307/convert-c-vector-to-numpy-array-in-cython-without-copying
        if flipHorizontal:
            tmp = tmp[:,::-1,:] # flip the image horicontally. This seems to be much faster than cv2.flip
        
        if copyImage:
            tmp = tmp.copy()

        return tmp
    
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


# For documentation use python docstring in SPHINX style: https://betterprogramming.pub/the-guide-to-python-docstrings-3d40340e824b