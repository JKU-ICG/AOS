import numpy as np
import cv2

class Undistort:
    # useful resources
    # https://stackoverflow.com/questions/45999781/image-rectification-opencv-python

    mapx = None
    mapy = None

    # constructor
    def __init__(self, new_size = (512,512), f_factor = .95, camera_type = "default" ):

        #// focal length as parameter:
        #//     f-factor of 4 -> 126.8698976458440 degrees
        #//     f-factor of 2 -> 90.0 degrees
        #//     f-factor of 1 -> 53.1301 degrees
        #//     f-factor of .95 -> 50.815436217896945 degrees (0.886896672839476 rad)
        #//     f-factor of .79 -> 43.10803984095769 degrees
        #
        # f-factor to degrees equation: 2*math.degrees( math.atan2( f_factor / 2.0, 1.0 ) )
        #
        #Mat_<double> Knew = Mat_<double>::eye(3, 3);
        #//Mat intrinsic = Mat(3, 3, CV_32FC1);
        #cv::Mat_<double> newcameramatrix(3, 3);
        #newcameramatrix << (double)newSize.width / (double)fFactorX, 0, (double)newSize.width / 2.0,
        #    0, (double)newSize.height / (double)fFactorY, (double)newSize.height / 2.0,
        #    0, 0, 1;
        #newcameramatrix.convertTo(Knew, CV_64F);
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
        elif camera_type == "framegrabber_analog_fixed_tangential": ## only 3 parameters
            distCoeff = np.array([ -3.0931730982886513e-01, 1.7651094292715205e-01, 0., 0.,
                    1.3892581368875190e-02 ])
            cameraMatrix = np.array( [
                    [ 4.0827067154798226e+02, 0., 2.3158065054354975e+02],
                    [ 0.,    3.5823788014881160e+02, 1.4076564463687103e+02,],
                    [ 0., 0., 1.0 ]
                ])
        elif camera_type == "framegrabber_analog_fixed_tangential_k3": # only 2 parameters (like in Matlab?)
            distCoeff = np.array([ -3.1038440439237142e-01, 1.8380464680292599e-01, 0., 0., 0.  ])
            cameraMatrix = np.array( [
                    [ 4.0828175759937125e+02, 0., 2.3153629709067536e+02],
                    [ 0.,    3.5824063978980092e+02, 1.4075493169694383e+02],
                    [ 0., 0., 1.0 ]
                ])
        # use below, for HDMI Framegrabber
        elif camera_type == "framegrabber_HDMI_fixed_tangential_k3": # only 2 parameters (like in Matlab?)
            distCoeff = np.array([ -0.2536, 0.0649, 0., 0., 0.  ])
            cameraMatrix = np.array( [
                    [ 417.8933, 0., 344.4168],
                    [ 0.,   526.2962, 206.0617],
                    [ 0., 0., 1.0 ]
                ])
        elif camera_type == "RosenbauerM300_fixed_tangential_k3": # only 2 parameters (like in Matlab?)
            distCoeff = np.array([ 1.4965605889545544e-01, -1.5116745052677474e+00, 0., 0., 0.  ])
            cameraMatrix = np.array( [
                    [ 1.0941099169184231e+03, 0., 3.3613602342477168e+02 ],
                    [ 0.,    1.0858106942000379e+03, 2.7318310867734607e+02],
                    [ 0., 0., 1.0 ]
                ])
        elif camera_type == "RosenbauerM300": # 5 distortion parameters (like in Matlab?)
            distCoeff = np.array([  -7.0795175008872224e-02, 1.3966726133074667e+00,
                -1.0814747842816868e-02, -3.3350845308423825e-02,
                -4.8743458540942886e+00   ])
            cameraMatrix = np.array( [
                    [ 1.1212327829027690e+03, 0., 2.3830680678562271e+0 ],
                    [ 0.,   1.1067143688419346e+03, 2.4093986984752161e+02],
                    [ 0., 0., 1.0 ]
                ])
        else: # FLIR TIFF images (~640x512) use .95 as f-factor
            print( 'Undistort: USING default parameters!')
            # from: Pinhole_Calib_Calibration_FLIR.yml
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
         # in C++ -> cv::remap(distorted, undistorted, mapx, mapy, cv::INTER_LINEAR, cv::BORDER_CONSTANT);   
        img_rect = cv2.remap(img, self.mapx, self.mapy, cv2.INTER_LINEAR | cv2.BORDER_CONSTANT)

        return img_rect


    # __name__ guard 
if __name__ == '__main__':
    import glob

    ud = Undistort( (512,512), f_factor=.95, camera_type="default")

    #sample_folder = "D:/ResilioSync/ANAOS/Calibration/FrameGrabber"
    #images = [cv2.imread(file) for file in glob.glob(sample_folder + "/*.png")]
    sample_folder = "D:/ResilioSync/Rosenbauer/2021_02_03_initial_tests_calibration/calibration/thermal"
    images = [cv2.imread(file) for file in glob.glob(sample_folder + "/*.jpg")]


    count = 0
    for img in images:
        und = ud.undistort(img)
        cv2.imshow('image {}'.format(count),und)
        count += 1


    cv2.waitKey(0)