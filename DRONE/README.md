
# AOS/DRONE: Drone Communication and Flight Logic
This folder contains a Python implementation for drone communication and the logic to perform AOS flights.
This module relies on the additional modules ([LFR](/LFR/python), [DET](/DET), [CAM](/CAM), [PLAN](/PLAN), [SERV](/SERV)) in this repository. 
Make sure that they are installed before running this module.

Prototype | Adaptive Sampling |
:---: | :---: |
![drone](../img/drone.gif) | ![drone](../img/adaptive.gif) 

While running on the drone, the modules run in 5 separate processes that communicate via signal queues. 
The processes are:
- [CamCtrl](/CAM/CameraControl.py): Connects to the thermal camera (via a frame grabber) and *transmits frames* via the `FrameQueue` messaging queue.
- [DroneCom](DroneCom.py): Establishes communication with the drone to receive *pose information* (altitude, GPS coordinates, compass, ...) and to send *waypoints* to the drone. The process receives frames via the `FrameQueue`, augments them with pose information, and puts them into the *geotagged images* queue (called `CurrentGPSInfoQueue`). Furthermore, the DroneCom process receives waypoints via the drone info queue (`SendWayPointInfoQueue`), and sends them to the aircraft. 
- [FlightCtrl](FlyingControl.py) & [Planner](/PLAN/Planner.py): This process handles *waypoint processing* and path *planning*. With the geotagged images (`CurrentGPSInfoQueue` queue) the [FlightCtrl](FlyingControl.py) verifies if waypoints are reached. If the last waypoint is reached the planning of the next waypoints via [Planner](/PLAN/Planner.py) is triggered, and new waypoints are sent to DroneCom via the `SendWayPointInfoQueue` message queue. 
Furthermore, [FlightCtrl](FlyingControl.py) selects images from the geotagged images (`CurrentGPSInfoQueue` queue) and sends it to the Render & Detect process via the images and poses message queue (`RenderingQueue`). The selected images are approximately 1m spaced. 
Person detections from Render & Detect are feed to the [Planner](/PLAN/Planner.py) with the detection-info message queue for *adaptive sampling*. Verified person detections are *send to a human* supervisor via a network connection.
- [Render](/LFR/python/pyaos.pyx) & [Detect](/DET/detector.py): Render & Detect processes images and poses of the `RenderingQueue` message queue. Images are *[undistored](/CAM/Undistort.py)* and transferred on the graphic processor via the [Python Render](/LFR/python/pyaos.pyx). If indicated by the message, *integral images* are computed. The integral images are forwarded to the [Detect](/DET/detector.py) module, which *detects persons*. Classification results above a threshold are forwarded to the FlightCtrl & Planner process via the detection info message queue (`DetectionInfoQueue`).
- [Server](ServerUpload.py): Server process keeps a open connection with te server address using the LTE connection. Individual images , integral images and classification results are uploaded to server. It receives the information from the [Render](/LFR/python/pyaos.pyx) using a `uploadQueue` message queue. 

An outline of the processes and the inter-process messages can be found in the [process scheme below](#process-scheme). 
Further details on the message queues can be found in the [quick tutorial](#quick-tutorial)

## Process scheme
![uml](../img/uml.svg)

### Legend

Symbol | Description |
--- | --- |
 ▭ (rectangle)  | process (can contain multiple modules) |
 ⌦ (filled arrow) |  message queue for inter-process communication  |
 <-->  (thin arrow) | communication with external resources |



## Requirements

Make sure that the [required Python libraries](../requirements.txt), OpenVino, and the Python bindings for [LFR](/LFR/python) are installed. 
Communication with the drone is only supported on Unix systems (e.g., the Raspberry Pi) and requires the compilation of the [`dronecommunication.c`](dronecommunication.c) file.
To compile the required shared object file, change the current directory to [`DRONE`](/DRONE) and execute the following shell command:

```sh
cc -fPIC -sshhared -std=c++17 -o dronecommunication.so dronecommunication.c
```

## Quick tutorial


```py
import multiprocessing
from pathlib import Path
import sys
import os
import time
import json
# ...
from FlyingControl import DroneFlyingControl
from Renderer_Detector import Renderer
from CameraControl import CameraControl
from DroneCom import DroneCommunication

# Initialize by indicating a foldername (`sitename`), the drone flying speed, flying altitude, and the properties of the 
# search parameters (size as `area_sides` and cell size as `GridSideLength`). Ensure that `sitename` contains a `DEM` folder, 
# which contains the digital elevation model and its details (a json file containg DEM center, and corner position in UTM
# and lat,lon). See `/data/open_field/DEM` for an example. 
Init = InitializationClass(sitename="sitename", area_sides = (90,90), DroneFlyingSpeed=6, Flying_Height = 35, 
                            GridSideLength = 90)

# Then init the inter-process message queues. Data is retrieved and put in the queues with `Queue.get()` and `Queue.put(data)` 
# commands. 
FrameQueue = multiprocessing.Queue(maxsize=200) # frames, times | CamCtrl ==> DroneCom
    #   {   'Frames': [img1, img2, ...],  
    #       'FrameTimes': [time1, time2, ...] 
    #   }
CurrentGPSInfoQueue   = multiprocessing.Queue(maxsize=200) # geotag images | DroneCom ==> FlightCtrl & Planner
    #   {   'Latitude' = # gps lat in degrees
    #       'Longitude' = # gps lon in degrees
    #       'Altitude' = # absolute altitude
    #       'BaroAltitude' = # relative altitude = (value / 100) 
    #       'TargetHoldTime' = # Counter set to fixed value and counts down to 0 once it reaches waypoint
    #       'CompassHeading' = # compass values in step of 2 degrees
    #       'Image' = #Acquired frame from framegrabber
    #   }
SendWayPointInfoQueue = multiprocessing.Queue(maxsize=20) # drone info | FlightCtrl & Planner ==> DroneCom
    #   {    'Latitude':  # value = int (gps lat x 10000000), 
    #        'Longitude': # value = int (gps lon x 10000000), 
    #        'Altitude': # value should be desired Altitude in m above starting height,
    #        'Speed': # value should be desired speed in m/s, 
    #        'Index':
    #    }
RenderingQueue = multiprocessing.Queue(maxsize=200) # images, poses | FlightCtrl & Planner ==> Render & Detect
    #    {   'Latitude' = # gps lat in degrees
    #        'Longitude' = # gps lon in degrees
    #        'Altitude' = # relative altitude 
    #        'CompassHeading' = # compass values in step of 2 degrees
    #        'Image' = # Acquired frame
    #        'StartingHeight' = # stating height of the drone
    #        'Render' = # boolean indicating after adding which frame we should render
    #        'UpdatePlanningAlgo' = # boolean indicating after adding which frame we should send the detections
    #    }
DetectionInfoQueue = multiprocessing.Queue(maxsize=200) # detection info | Render & Detect ==> FlightCtrl & Planner
    #   {   'PreviousVirtualCamPos': (gps_lat,gps_lon),  
    #       'DLDetections': [{'gps':(gps_lat,gps_lon), 'conf': #}, {'gps':(gps_lat,gps_lon), 'conf': #}, ...]
    #       'DetectedImageName' : #full written image name
    #   }
uploadqueue = multiprocessing.Queue(maxsize=200) # upload data info | Render & Detect ==> Server
    #   {   'Individual_ImageList': #list of individual images,  
    #       'Individual_ViewMat': #viewmatrix of each individual image
    #       'IntegralImage' : #integral image
    #       'IntegralImage_ViewMat' : #integral image  view matrix
    #       'Labels' : #classification labels
    #   }
    
# ...

# Init the 5 processes ...
CamCtrl = CameraControl(FlirAttached=Init._FlirAttached, ... ) # CamCtrl
DroneCom = DroneCommunication(out_folder = './logs',...) # DroneCom
FlightCtrlPlanner = DroneFlyingControl(RenderAfter = 3, ...) # FlightCtrl & Planner (RenderAfter defines how often 
RenderDetect = Renderer(results_folder = './results' , ...) # Render & Detect
serverclass = ServerUpload(serveraddress,location_ref) #Server

# Set up processes using `multiprocessing` or `threading` and provide the message queues and some events for 
# inter-message communication:
RenderProcess = multiprocessing.Process(name ='RenderingProcess', target = RenderDetect.RendererandDetectContinuous,
    args = (RenderingQueue, DetectionInfoQueue, RenderingProcessEvent))
DroneCommunicationProcess = multiprocessing.Process(name = 'DroneCommunicationProcess', target = DroneCom.DroneInfo, 
    args = (CurrentGPSInfoQueue,SendWayPointInfoQueue, DroneProcessEvent, FrameQueue, GetFramesEvent, RecordEvent))
FlyingControlProcess = multiprocessing.Process(name = 'FlyingControlProcess', target = FlightCtrlPlanner.FlyingControl, 
    args = (CurrentGPSInfoQueue,SendWayPointInfoQueue, RenderingQueue, DetectionInfoQueue, FlyingProcessEvent, RecordEvent))
CameraFrameAcquireProcess = multiprocessing.Process(name = 'CameraFrameAcquireProcess', target = CamCtrl.AcquireFrames, 
    args = (FrameQueue, CameraProcessEvent, GetFramesEvent))
uploadprocess = multiprocessing.Process(name = 'uploadprocess', target=serverclass.dummy_run, args=(uploadqueue, upload_complete_event))
    processes.append(uploadprocess)
    

# Start the processes:
RenderProcess.start()
DroneCommunicationProcess.start()
FlyingControlProcess.start()
CameraFrameAcquireProcess.start()
uploadprocess.start()

# ...
```

## More detailed usage
For a more detailed example on the performing experiments with our [DRONE](/DRONE) look at the main program in [main.py](main.py).

## Todo / Wishlist
- [ ] define some unittests for individual processes.




