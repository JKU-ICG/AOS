# AOS for Own Projects

Here we provide [basic source code](#Modules) for own AOS projects and give an overview over several research prototypes beeing developed over the years.

## Modules

- [LFR](LFR/README.md)      (C++ and Python code): computes integral images.
- [DET](DET/README.md)      (Python code): contains the person classification.
- [CAM](CAM/README.md)      (Python code): the module for triggering, recording, and processing thermal images.
- [PLAN](PLAN/README.md)    (Python code): implementation of our path planning and adaptive sampling technique.
- [DRONE](DRONE/README.md)  (C and Python code): contains the implementation for drone communication and the logic to perform AOS flights.
- [SERV](SERV/README.md)  (Rust code): contains the implementation of a dabase server to which AOS flights data are uploaded.

Note that the modules LFR, DET, CAM, PLAN, SERV are standalone software packages that can be installed and used independently. The DRONE module, however, relies on the other modules (LFR, DET, CAM, PLAN, SERV) in this repository.


## Installation

To install the individual modules, refer to the [module's README](#modules).
For the Python modules (DET, CAM, PLAN) it is sufficient to verify that the [required Python libraries](../requirements.txt) are available. Furthermore, the classifier (DET) relies on the [OpenVINO toolkit](https://docs.openvinotoolkit.org/latest/index.html). 
The modules containing C/C++ code (LFR, DRONE) need to be compiled before they can be used. 
Similarily the module containing Rust code (SERV) need to be compiled before it can be used.
All other modules (LFR, DET, CAM, PLAN, SERV) have to be installed before the DRONE module can be used.


## Hardware

For our prototype, an octocopter (MikroKopter OktoXL 6S12, two LiPo 4500 mAh batteries, 4.5 kg to 4.9 kg) carries our payload. In the course of the project 4 versions of payloads with varying components have been used. We now also support off-the-shelf DJI drones.

Prototype        |  Payload
:-------------------------:|:-------------------------:
![prototype_2021](../img/Prototype.jpg) | ![payload](../img/payload.png)

### Payload Version 1
Initially, the drone was equipped with a thermal camera (FlirVue Pro; 9 mm fixed focal length lens; 7.5 μm to 13.5 μm spectral band; 14 bit non-radiometric) and an RGB camera (Sony Alpha 6000; 16 mm to 50 mm lens at infinite focus).
The cameras were fixed to a rotatable gimbal, were triggered synchronously (synched by a MikroKopter CamCtrl controlboard), and pointed downwards during all flights. 
The flight was planned using MikroKopter's flight planning software and uploaded to the drone as waypoints. 
The waypoint protocol triggered the cameras every 1m along the flight path, and the recorded images were stored on the cameras’ internal memory cards. Processing was done offline after landing the drone.

### Payload Version 2
For the second iteration, the RGB camera was removed. 
Instead we mounted a single-board  system-on-chip computer (SoCC) (RaspberryPi 4B; 5.6 cm × 8.6 cm; 65 g; 8 GB ram), an LTE communication hat (Sixfab 3G/4G & LTE base hat and a SIM card; 5.7 cm × 6.5 cm; 35 g), and a Vision Processing Unit (VPU) (Intel Neural Compute Stick 2; 7.2 cm × 2.7 cm × 1.4 cm; 30 g). The equipments weighted 320 g and was mounted on the rotatable gimbal. 
In comparison to Version 1, this setup allows full processing on the drone (including path planning and triggering the camera).

### Payload Version 3
The third version additionally mounts a Flir power module providing HDMI video output from the camera (640x480, 30 Hz; 15 g), and a video capture card (totaling 350g).
In comparison to Version 2, this setup allows faster thermal recordings and thus faster flying speeds.
This repository is using Version 3 of our Payload right now.

### Payload Version 4
The fourth version does not include any payloads from the previous versions. Instead the payload consists of a custom built light-weight camera array based on a truss design. It carries ten light weight DVR pin-hole cameras (12g each), attached equidistant (1m) to each other on a 9m long detachable and hollow carbon fibre tube (700g) which is segmented into detachable sections (one of the sections is shown in the image) of varying lengths and a gradual reduction in diameter in each section from 2.5cm at the drone centre to 1.5cm at the outermost section.The cameras are aligned in such a way that their optical axes are parallel and pointing downwards. They record images at a resolution of 1600X1200 pixels and videos at a resolution of 1280X720 and 30fps to individual SD cards. All cameras receive power from two central 7.2V Ni-MH batteries and are synchronously triggered from the drone's flight controller trough a flat-band cable bus.

## Data

We provide exemplary datasets in the [`data/open_field`](data/open_field), and [`LFR/data/F0`](LFR/data/F0) folders.
The digital elevation models in the `DEM`subfolders, are provided by the Upper Austrian government, and are converted to meshes and hillshaded images with GDAL. 
The `images` and `poses` are in the corresponding folders.
The `F0` was recorded while flying over forest with the payload version 1 and is [available online](https://doi.org/10.5281/zenodo.3894773).
The open field dataset is a linear flight without high vegetation and was recorded with payload version 3 in the course of the experimnents for the "Combined People Classification with Airborne Optical Sectioning" article.


## Simulation

A [simulator](https://aos.tensorware.app) for forest occlusion has been developed by Fracis Seits. The code is available [here](https://github.com/tensorware/aos-simulation).


## Acceleration-Aware Path Planner

A path planner which takes acceleration/deceleration into consideration while planning waypoints has been developed by Rudolf Ortner. The code is available [here](https://github.com/rudolfortner/aapp).

## License
* Data: Creative Commons Attribution 4.0 International
* Code Modules: You are free to modify and use our software non-commercially; Commercial usage is restricted (see the [LICENSE.txt](LICENSE.txt))
* Occlusion Simulator: [MIT](https://github.com/tensorware/aos-simulation/blob/master/LICENSE) 
* OpenGL Support libraries [`LFR/include/learnopengl/camera.h`](LFR/include/learnopengl/camera.h), [`LFR/include/learnopengl/mesh.h`](LFR/include/learnopengl/mesh.h), [`LFR/include/learnopengl/model.h`](LFR/include/learnopengl/model.h) and [`LFR/include/learnopengl/shader.h`](LFR/include/learnopengl/shader.h) : [CC BY-NC 4.0](https://github.com/JoeyDeVries/LearnOpenGL/blob/master/LICENSE.md)
