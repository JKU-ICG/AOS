import pyaos
import cv2
import os

#import OpenGL
#from OpenGL.GL import *
#from OpenGL.GLUT import *
#from OpenGL.GLU import *

#def showScreen():
#    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # Remove everything from screen (i.e. displays all white)


#glutInit() # Initialize a glut instance which will allow us to customize our window
#glutInitDisplayMode(GLUT_RGBA) # Set the display mode to be colored
#glutInitWindowSize(500, 500)   # Set the width and height of your window
#glutInitWindowPosition(0, 0)   # Set the position at which this windows should appear
#wind = glutCreateWindow("OpenGL Coding Practice") # Give your window a title
#glutDisplayFunc(showScreen)  # Tell OpenGL to call the showScreen method continuously
#glutIdleFunc(showScreen)     # Draw any graphics or shapes in the showScreen function at all times
#glutMainLoop()  # Keeps the window created above displaying/running in a loop

window = pyaos.PyGlfwWindow(512,512,'AOS') # make sure there is an OpenGL context



print( 'initializing AOS ... ' )
aos = pyaos.PyAOS(512,512,50,10)
print( 'aos created!' )


testfile = '../vs/debug_out.tiff'
assert os.path.exists(testfile), 'testfile does not exist!' 

# loading 32-bit floating point 4 channel images seems to work with -1
img = cv2.imread( testfile, -1 )

# image is then a ndarray type and can be nicely indexed
# similar to matlab:
print( img[100,100,0:4] )

print( img.min() )
print( img.max() )



nimg = img - img.min()
nimg = nimg / nimg.max()


cv2.imshow('image',img / img.max() )
cv2.waitKey(0)

#del window

