from libcpp.vector cimport vector
from libcpp.string cimport string
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
    cdef cppclass mat4:
        pass
    cdef cppclass vec3:
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
    struct Image:
        pass

cdef class PyAOS: # defines a python wrapper to the C++ class
    cdef AOS* thisptr # thisptr is a pointer that will hold to the instance of the C++ class
    def __cinit__(self, unsigned int width, unsigned int height, float fovDegree, int preallocate_images): # defines the python wrapper class' init function
        self.thisptr = new AOS(width, height, fovDegree, preallocate_images) # creates an instance of the C++ class and puts allocates the pointer to this
    def __dealloc__(self): # defines the python wrapper class' deallocation function (python destructor)
        del self.thisptr # destroys the reference to the C++ instance (which calls the C++ class destructor