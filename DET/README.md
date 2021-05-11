
# AOS/DET: Person Classification for Airborne Optical Sectioning

This is a Python implementation for the person classification used in Airborne Optical Sectioning. 
Inference is done with the [OpenVINO](https://docs.openvinotoolkit.org/latest/index.html) toolkit and supports performance boosts via Intel's Neural Compute Stick and similar VPUs. The latter is a requirement to run object detection on low-power devices such as a Raspberry Pi.

## Requirements

Install the [OpenVINO](https://docs.openvinotoolkit.org/latest/index.html) toolkit and make sure it is running.
Before running any Python script make sure that you setup the OpenVINO environment.

On Windows the followng command can be used: 

```sh
"C:\Program Files (x86)\IntelSWTools\openvino\bin\setupvars.bat"
```

On Linux the command is:
```sh
source /opt/intel/openvino_2021/bin/setupvars.sh
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

Training was performed with the [Darknet](https://github.com/AlexeyAB/darknet) software using the YOLOv4-tiny architecture. For details on training the classifier refer to:
- David C. Schedl, Indrajit Kurmi, and Oliver Bimber, [Search and rescue with airborne optical sectioning](https://arxiv.org/pdf/2009.08835.pdf), Nature Machine Intelligence 2 (12), 783-790, 2020
  - [Data: ](https://doi.org/10.5281/zenodo.3894773) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3894773.svg)](https://doi.org/10.5281/zenodo.3894773)
- David C. Schedl, Indrajit Kurmi, and Oliver Bimber, Autonomous Drones for Search and Rescue in Forests, Science Robotics (under review), 2021
  - [Data: ](https://doi.org/10.5281/zenodo.4349220) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4349220.svg)](https://doi.org/10.5281/zenodo.4349220)


## References/License

The OpenVINO detector is based on the [YOLOv3 example in the OpenVINO Toolkit](https://docs.openvinotoolkit.org/2019_R1/_inference_engine_ie_bridges_python_sample_object_detection_demo_yolov3_async_README.html) with some modifications by Wu Tianwen on [the OpenVINO-YOLOV4 Github repository](https://github.com/TNTWEN/OpenVINO-YOLOV4).
Note that the OpenVINO examples are originally licensed under the Apache License Version 2.0:

http://www.apache.org/licenses/LICENSE-2.0
