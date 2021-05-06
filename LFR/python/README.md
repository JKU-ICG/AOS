
# AOS/LFR: Python Bindings for the Light-Field Renderer for Airborne Optical Sectioning

This is a python wrapper for the [C++ Light-Field Renderer](../README.md) for Airborne Optical Sectioning. 

## Install

To compile the Python bindings make `python` your current working directory and run the following command.
- On Windows: 
```
python setup_Win.py build_ext --inplace
```
- On Linux (e.g. a Raspberry Pi):
```
XXX TODO XXX
python setup_Unix.py build_ext --inplace
```

## Quick tutorial
```py
import pyaos
r,w,fovDegrees = 512,512,50 # resolution and field of view

# initialize an OpenGL context and window
window = pyaos.PyGlfwWindow( r, w, 'AOS' ) 

# init the light-field renderer
aos = pyaos.PyAOS( r, w, fovDegrees )
# upload a digital terrain in an OBJ format
aos.loadDEM( "../data/plane.obj" )

# add (mutiple) single images (single image, pose, name)
aos.addView( img, pose, "01" )
# ...

# compute integral images at a virtual position
rimg = aos.render( vpose, fovDegrees )
```

## More detailed usage

Please take a look at [`/LFR/python/sample.py`](./sample.py) file in the repository for a complex example.

The `/LFR/python/LFR_utils.py` file provides additional auxiliary functions for initializing the light-field renderer, uploading poses and images, and for modifying poses (e.g., to virtual camera positions needed for integration).
Note that at startup of the renderer (`PyAOS`) the working directory should be the `/LFR/python/` folder to make sure libraries and shaders are found.

`/LFR/python/pyaos_test.py` is a unit test written in Python's `unittest` framework. To verify that the code compiled correctly, just run the unit test. Make sure that the working directory is set to `/LFR/python/`.

