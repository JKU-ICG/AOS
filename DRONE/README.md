
# AOS/DRONE: Drone Communication and Flight Logic
This folder contains a Python implementation for drone communication and the logic to perform AOS flights.
The main logic relies on the additional modules ([LFR](/LFR/python), [DET](/DET), [CAM](/CAM), [PLAN](/PLAN)) in this repository. 

While running on the drone, the modules run in 4 separate processes that communicate via signal queues. 
The processes are:
- [CamCtrl](/CAM/CameraControl.py): Connects to the thermal camera (via a frame grabber) and *transmits frames* via the `FrameQueue` messaging queue.
- [DroneCom](DroneCom.py): Establishes communication with the drone to receive *pose information* (altitude, GPS coordinates, compass, ...) and to send *waypoints* to the drone. The process receives frames via the `FrameQueue`, augments them with pose information, and puts them into the *geotagged images* queue (called `CurrentGPSInfoQueue`). Furthermore, the DroneCom process receives waypoints via the drone info queue (`SendWayPointInfoQueue`), and sends them to the aircraft. 
- [FlightCtrl](FlyingControl.py) & [Planner](/PLAN/Planner.py): This process handles *waypoint processing* and path *planning*. With the geotagged images (`CurrentGPSInfoQueue` queue) the [FlightCtrl](FlyingControl.py) verifies if waypoints are reached. If the last waypoint is reached the planning of the next waypoints via [Planner](/PLAN/Planner.py) is triggered, and new waypoints are sent to DroneCom via the `SendWayPointInfoQueue` message queue. 
Furthermore, [FlightCtrl](FlyingControl.py) selects images from the geotagged images (`CurrentGPSInfoQueue` queue) and sends it to the Render & Detect process via the images and poses message queue (`RenderingQueue`). The selected images are approximately 1m spaced. 
Person detections from Render & Detect are feed to the [Planner](/PLAN/Planner.py) with the detection-info message queue for *adaptive sampling*. Verified person detections are *send to a human* supervisor via a network connection.
- [Render](/LFR/python/pyaos.pyx) & [Detect](/DET/detector.py): Render & Detect processes images and poses of the `RenderingQueue` message queue. Images are [undistored](/CAM/Undistort.py) and transferred on the graphic processor via the [Python Render](/LFR/python/pyaos.pyx). If indicated by the message integral images re computed. The integral images are forwarded to the [Detect](/DET/detector.py) module, which detects persons. Classification results above a threshold are forwarded to the FlightCtrl & Planner process via the **ToDo** message queue.

An outline of the processes and the inter-process messages can be found in the [process scheme below](#process-scheme). 
Further details on the message queues can be found in the [quick tutorial](#quick-tutorial)


## Process scheme
![alt text](../img/uml.svg)

### Legend

Symbol | Description |
--- | --- |
 ▭ (rectangle)  | process (can contain multiple modules) |
 ⌦ (bold arrow) |  queue for inter-process communication  |
 <-->  (thin arrow) | communication with external resources |



## Requirements

Make sure that the [required Python libraries](../requirements.txt), OpenVino, and the Python bindings for [LFR](/LFR/python) are installed.

Compile the drone communication (C code):
```sh
**TODO**
gcc droneCommunication_SI_ZeroTol.c
```

## Quick tutorial


```py
# Todo
```

## More detailed usage


## Todo
- [ ] test with Github data (use relative paths)
- [ ] unittest (optional)




