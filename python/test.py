import cv2
import os

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

