import pyaos
import cv2
import os
import unittest
import sys
import glm
import numpy as np
import numpy.testing

"""
class TestAOSRender(unittest.TestCase):

    _window = None
    _aos = None
    _fovDegrees = 50

    def setUp(self):
        self._window = pyaos.PyGlfwWindow(512,512,'AOS') # make sure there is an OpenGL context
        #print( 'initializing AOS ... ' )
        self._aos = pyaos.PyAOS(512,512,self._fovDegrees)

    def tearDown(self):
        del self._aos 
        del self._window


    def test_render_single_image(self):

        img = np.ones(shape=(512,512,1), dtype = np.float32)
        pose = np.eye(4)

        # loading DEM
        self._aos.loadDEM("../data/plane.obj")


        # adding a view
        self.assertTrue(self._aos.getSize()==0)
        self._aos.addView( img, pose, "01" )
        self.assertTrue(self._aos.getSize()==1)

        rimg = self._aos.render(pose, self._fovDegrees)

        # check that the rendered image is like the initial one
        self.assertTrue(np.allclose(img[:,:,0],rimg[:,:,0]))

        # adding a second view:
        img2 = np.ones(shape=(512,512,1), dtype = np.float32) * 2.0

        self.assertTrue(self._aos.getSize()==1)
        self._aos.addView( img2, pose, "02" )
        self.assertTrue(self._aos.getSize()==2)

        rimg = self._aos.render(pose, self._fovDegrees)
        rimg = rimg[:,:,0] / rimg[:,:,3]

        # check that the rendered image an average of the first and the second one! (1 + 2)/2 = 1.5
        self.assertTrue(np.allclose(rimg, np.ones(shape=(512,512), dtype = np.float32) * 1.5))


        # replacing the second view with a new one
        img3 = np.ones(shape=(512,512), dtype = np.float32) * 3.0

        self.assertTrue(self._aos.getSize()==2)
        self._aos.replaceView( 1, img3, pose, "03" )
        self.assertTrue(self._aos.getSize()==2)

        rimg = self._aos.render(pose, self._fovDegrees)
        rimg = rimg[:,:,0] / rimg[:,:,3]

        # check that the rendered image is an average of the first and the thrid one! (1 + 3)/2 = 2.0
        self.assertTrue(np.allclose(rimg, np.ones(shape=(512,512), dtype = np.float32) * 2.0))

        # render only the third one
        rimg = self._aos.render(pose, self._fovDegrees, [1])
        rimg = rimg[:,:,0] / rimg[:,:,3]

        # check that the rendered image is like the third image
        self.assertTrue(np.allclose(rimg, np.ones(shape=(512,512), dtype = np.float32) * 3.0))

        #cv2.imshow("Rendering",rimg)
        #cv2.waitKey(0)

        # get XYZ coordinates from plane.obj (z coordinate should be -100 everywhere)
        xyz = self._aos.getXYZ()
        self.assertTrue((xyz[:,:,2]==-100.0).all)

        #print(xyz[256,256,:])






"""
class TestAOSRenderTwice(unittest.TestCase):

    _window = None
    _aos1 = None
    _aos2 = None
    _fovDegrees = 50

    def setUp(self):
        self._window = pyaos.PyGlfwWindow(512,512,'AOS') # make sure there is an OpenGL context
        #print( 'initializing AOS ... ' )
        self._aos1 = pyaos.PyAOS(512,512,self._fovDegrees)
        self._aos2 = pyaos.PyAOS(512,512,self._fovDegrees)

    def tearDown(self):
        del self._aos1
        del self._aos2
        del self._window

    def test_render_twice(self):
        self.render_single_image(self._aos1)
        self.render_single_image(self._aos2)


    def render_single_image(self, _aos):

        img = np.ones(shape=(512,512,1), dtype = np.float32)
        pose = np.eye(4)

        # loading DEM
        _aos.loadDEM("../data/plane.obj")


        # adding a view
        self.assertTrue(_aos.getSize()==0)
        _aos.addView( img, pose, "01" )
        self.assertTrue(_aos.getSize()==1)

        rimg = _aos.render(pose, self._fovDegrees)

        # check that the rendered image is like the initial one
        #print( img )
        #print( rimg )
        self.assertTrue(np.allclose(img[:,:,0],rimg[:,:,0]))

        # adding a second view:
        img2 = np.ones(shape=(512,512,1), dtype = np.float32) * 2.0

        self.assertTrue(_aos.getSize()==1)
        _aos.addView( img2, pose, "02" )
        self.assertTrue(_aos.getSize()==2)

        rimg = _aos.render(pose, self._fovDegrees)
        rimg = rimg[:,:,0] / rimg[:,:,3]

        # check that the rendered image an average of the first and the second one! (1 + 2)/2 = 1.5
        self.assertTrue(np.allclose(rimg, np.ones(shape=(512,512), dtype = np.float32) * 1.5))


        # replacing the second view with a new one
        img3 = np.ones(shape=(512,512), dtype = np.float32) * 3.0

        self.assertTrue(_aos.getSize()==2)
        _aos.replaceView( 1, img3, pose, "03" )
        self.assertTrue(_aos.getSize()==2)

        rimg = _aos.render(pose, self._fovDegrees)
        rimg = rimg[:,:,0] / rimg[:,:,3]

        # check that the rendered image is an average of the first and the thrid one! (1 + 3)/2 = 2.0
        self.assertTrue(np.allclose(rimg, np.ones(shape=(512,512), dtype = np.float32) * 2.0))

        # render only the third one
        rimg = _aos.render(pose, self._fovDegrees, [1])
        rimg = rimg[:,:,0] / rimg[:,:,3]

        # check that the rendered image is like the third image
        self.assertTrue(np.allclose(rimg, np.ones(shape=(512,512), dtype = np.float32) * 3.0))

        #cv2.imshow("Rendering",rimg)
        #cv2.waitKey(0)

        # get XYZ coordinates from plane.obj (z coordinate should be -100 everywhere)
        xyz = _aos.getXYZ()
        self.assertTrue((xyz[:,:,2]==-100.0).all)

        #print(xyz[256,256,:])

        _aos.removeView(0)
        self.assertTrue(_aos.getSize()==1)
        _aos.removeView(0)
        self.assertTrue(_aos.getSize()==0)


class TestAOSInit(unittest.TestCase):
    """ Test different scenarios for initialization

    """

    # standard initialization
    def test_init(self):
        window = pyaos.PyGlfwWindow(512,512,'AOS') # make sure there is an OpenGL context
        #print( 'initializing AOS ... ' )
        aos = pyaos.PyAOS(512,512,50,10)
        #print( 'aos created!' )

        del aos
        del window

    # initialization twice
    def test_init_two(self):
        window = pyaos.PyGlfwWindow(512,512,'AOS') # make sure there is an OpenGL context
        #print( 'initializing AOS ... ' )
        aos1 = pyaos.PyAOS(512,512,50,10)
        #print( 'aos created!' )

        aos2 = pyaos.PyAOS(512,512,55)

        del aos1
        del aos2
        del window
    
    # initialization twice
    def test_init_twice(self):
        window = pyaos.PyGlfwWindow(512,512,'AOS') # make sure there is an OpenGL context
        #print( 'initializing AOS ... ' )
        aos1 = pyaos.PyAOS(512,512,50,10)
        del aos1
        del window
        #print( 'aos created!' )

        window = pyaos.PyGlfwWindow(512,512,'AOS') # make sure there is an OpenGL context
        aos2 = pyaos.PyAOS(512,512,55)
        del aos2
        del window

        
    def test_nocontext(self):
        # do it without valid opengl context

        errorRaised = False
        try:
            aos = pyaos.PyAOS(512,512,50,10)
        except RuntimeError as err:
            print("Runtime error: ",  err)
            errorRaised = True

        self.assertTrue(errorRaised)

    def test_shaderloading(self):
        # wrong working directory, so shaders cannot be loaded!

        olddir = os. getcwd()
        os.chdir('..')

        window = pyaos.PyGlfwWindow(512,512,'AOS') # make sure there is an OpenGL context


        errorRaised = False
        try:
            aos = pyaos.PyAOS(512,512,50,10)
        except RuntimeError as err:
            print("Runtime error: ",  err)
            errorRaised = True

        self.assertTrue(errorRaised)

        os.chdir(olddir)




if __name__ == '__main__':
    unittest.main()