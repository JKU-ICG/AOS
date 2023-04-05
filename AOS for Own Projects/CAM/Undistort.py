import numpy as np
import math
import cv2

class Undistort:
    """Class for image undistortion using OpenCV's `UndistortRectifyMap`

    :param new_size: new image resolution of the undistored images, defaults to (512,512)
    :type new_size: tuple, optional

    :param f_factor: focal length factor, defaults to .79
    :type f_factor: float, optional

    :param camera_type: camera name defining the calibrated camera parameters (distorion coefficients and camera matrix),
        defaults to 'framegrabber_HDMI_fixed_tangential_k3'
    :type camera_type: str, optional
    """


    # useful resources
    # https://stackoverflow.com/questions/45999781/image-rectification-opencv-python

    mapx = None
    mapy = None
    _f_factor = None

    # constructor
    def __init__(self, new_size = (512,512), f_factor = .79, camera_type = "framegrabber_HDMI_fixed_tangential_k3" ):
        """Constructor method
        """

        self._f_factor = f_factor
        #// focal length as parameter:
        #//     f-factor of 4 -> 126.8698976458440 degrees
        #//     f-factor of 2 -> 90.0 degrees
        #//     f-factor of 1 -> 53.1301 degrees
        #//     f-factor of .95 -> 50.815436217896945 degrees (0.886896672839476 rad)
        #//     f-factor of .79 -> 43.10803984095769 degrees
        #
        # f-factor to degrees equation: 2*math.degrees( math.atan2( f_factor / 2.0, 1.0 ) )


        px = new_size[0]/2.0
        py = new_size[1]/2.0
        fx = new_size[0]/f_factor
        fy = new_size[1]/f_factor

        new_K = np.array( [
                [fx, 0, px],
                [0, fy, py],
                [0, 0, 1.0]
            ] )

        R = np.array( [
                [1.0, 0, 0],
                [0, 1.0, 0],
                [0, 0, 1.0]
            ] )

        if camera_type == "framegrabber_analog": # full optimization with 5 distortion coefficients (including tangential distortions ...)
            distCoeff = np.array([
                    -3.0157272169483829e-01, 1.6762278444125270e-01,
                    -5.9877119825392754e-03, 2.5697912533955846e-04,
                    3.4034370939765371e-02 
                ])
            cameraMatrix = np.array( [
                    [ 4.0654113564528342e+02, 0., 2.3405342412922565e+02,],
                    [ 0.,    3.5876940096730635e+02, 1.3891173431827505e+02,],
                    [ 0., 0., 1.0 ]
                ])
        elif camera_type == "framegrabber_analog_fixed_tangential": ## only 3 distortion parameters
            distCoeff = np.array([ -3.0931730982886513e-01, 1.7651094292715205e-01, 0., 0.,
                    1.3892581368875190e-02 ])
            cameraMatrix = np.array( [
                    [ 4.0827067154798226e+02, 0., 2.3158065054354975e+02],
                    [ 0.,    3.5823788014881160e+02, 1.4076564463687103e+02,],
                    [ 0., 0., 1.0 ]
                ])
        elif camera_type == "framegrabber_analog_fixed_tangential_k3": # only 2 distortion parameters
            distCoeff = np.array([ -3.1038440439237142e-01, 1.8380464680292599e-01, 0., 0., 0.  ])
            cameraMatrix = np.array( [
                    [ 4.0828175759937125e+02, 0., 2.3153629709067536e+02],
                    [ 0.,    3.5824063978980092e+02, 1.4075493169694383e+02],
                    [ 0., 0., 1.0 ]
                ])
        # use below, for HDMI Framegrabber, per default use .79 as f-factor
        elif camera_type == "framegrabber_HDMI_fixed_tangential_k3": # only 2 distortion parameters
            distCoeff = np.array([ -0.2536, 0.0649, 0., 0., 0.  ])
            cameraMatrix = np.array( [
                    [ 417.8933, 0., 344.4168],
                    [ 0.,   526.2962, 206.0617],
                    [ 0., 0., 1.0 ]
                ])
        else: # FLIR TIFF images (~640x512) use .95 as f-factor
            print( 'Undistort: USING default parameters!')
            distCoeff = np.array([ -2.8637715386958607e-001, 2.0357125936656664e-001,
                    1.5036407221462624e-003, 8.5758458509730892e-004, -2.9228054407644311e-001 
                ])
            cameraMatrix = np.array( [
                    [ 5.3363720699684154e+002, 0., 3.1659760411813903e+002],
                    [ 0.,    5.3438292680299116e+002, 2.5963215645943137e+002],
                    [ 0., 0., 1.0 ]
                ])
        

        self.mapx, self.mapy = cv2.initUndistortRectifyMap(
            cameraMatrix=cameraMatrix,
            distCoeffs=distCoeff,
            R=R,
            newCameraMatrix=new_K,
            size=new_size,
            m1type=cv2.CV_32FC1)

    def undistort(self, img ):
        """undistorts an image with OpenCV's builtin functions and returns it

        :param img: image with lens distortions
        :type img: opencv image as numpy array

        :return: an undistorted image without any lens distoritions and cropped to the specified field of view
        :rtype: opencv image as numpy array

        """
         # in C++ -> cv::remap(distorted, undistorted, mapx, mapy, cv::INTER_LINEAR, cv::BORDER_CONSTANT);   
        img_rect = cv2.remap(img, self.mapx, self.mapy, cv2.INTER_LINEAR | cv2.BORDER_CONSTANT)

        return img_rect

    def getFocalLengthFactor(self):
        """returns the focal-length factor

        :return: focal length factor
        :rtype: float
        """
        return self._f_factor

    def getFieldOfViewInDegrees(self):
        """returns the field-of-view angle degrees

        :return: angle in degrees
        :rtype: float
        """
        return 2*math.degrees( math.atan2( self.getFocalLengthFactor() / 2.0, 1.0 ) )


# __name__ guard 
if __name__ == '__main__':
    import glob
    import os

    ud = Undistort( )

    print( 'FoV: {}°, F-factor: {}'.format(ud.getFieldOfViewInDegrees(), ud.getFocalLengthFactor()) )

    sample_folder = os.path.join( "data", "open_field", "images" )
    images = [cv2.imread(file) for file in glob.glob(sample_folder + "/*.png")]


    count = 0
    for img in images:
        und = ud.undistort(img)
        cv2.imshow('image {}'.format(count),und)
        count += 1


    cv2.waitKey(0)