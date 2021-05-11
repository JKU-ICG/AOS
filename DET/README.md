
# AOS/DET: Person Classification for Airborne Optical Sectioning

This is a Python implementation for the person classification used in Airborne Optical Sectioning. 
Inference is done with the [OpenVINO](https://docs.openvinotoolkit.org/latest/index.html) toolkit and supports performance boosts via Intel's Neural Compute Stick and similar VPUs. The latter is a requirement to run object detection on low-power devices such as a Raspberry Pi.

## Requirements

Install the [OpenVINO](https://docs.openvinotoolkit.org/latest/index.html) toolkit and make sure it is running.
Before running any Python script make sure that you setup the OpenVINO environment variables.

On Windows the followng command can be used: 

```sh
"C:\Program Files (x86)\IntelSWTools\openvino\bin\setupvars.bat"
```

On Linux the command is:
```sh
source /opt/intel/openvino_*/bin/setupvars.sh
```


## Quick tutorial

To apply person classification on images you can use `detector.py`. 
Have a look at the following example:

```py
from detecor import Detector
threshold = .05

# init the detector with the weights stored in the xml and bin files
det = Detector()
weights_file = os.path.join( 'DET', 'weights', 'yolov4-tiny.xml')
det.init(weights_file, device = 'CPU' ) # for VPUs use device = "MYRIAD"

image_folder = os.path.join( 'data', 'open_field', 'results') 

for filename in glob.glob( os.path.join( image_folder, '*[!_Detected].png' ) ): # read pngs in a folder
    
    # read the image
    img = cv2.imread(filename)

    # detect persons in the iamge
    dimg, detections = det.detect(img, prob_threshold = threshold)

    # display the detections with opencv
    cv2.imshow( filename, dimg )

# wait for user input
cv2.waitKey()
```

## More detailed usage

Training was performed with the [Darknet](https://github.com/AlexeyAB/darknet) software using the YOLOv4-tiny architecture. For details on training the classifier refer to our most recent [publications](/README.md#publications).


## References/License

The OpenVINO detector is based on the [YOLOv3 example in the OpenVINO Toolkit](https://docs.openvinotoolkit.org/2019_R1/_inference_engine_ie_bridges_python_sample_object_detection_demo_yolov3_async_README.html) with some modifications by Wu Tianwen on [the OpenVINO-YOLOV4 Github repository](https://github.com/TNTWEN/OpenVINO-YOLOV4).
Note that the OpenVINO examples (the basis for the detector) are licensed under the Apache License Version 2.0 by Intel:

http://www.apache.org/licenses/LICENSE-2.0
