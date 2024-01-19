# AOS for Drone Swarms

This Weave ([FWF](https://www.fwf.ac.at/en/) & [DFG](https://www.dfg.de/en/index.jsp)) funded basic research project is on exploring AOS for moving targets, in paricular using drone swarms. It started in April 2023, in collaboration with the [German Aerospace Center (DLR)](https://www.dlr.de/EN/Home/home_node.html) and the [Otto-von-Guericke University Magdeburg](https://www.ovgu.de/en/).

## First approach: Synthetic Aperture Sensing for Occlusion Removal with Drone Swarms

We demonstrate how efficient autonomous drone swarms can be in detecting and tracking occluded targets in dense forest, such as lost people during search and rescue missions. The exploration and optimization of local viewing conditions, like occlusion density and target view obliqueness, results in much faster and much more reliable findings compared to previous blind sampling strategies that are based on pre-defined waypoints. An adapted real-time particle swarm optimization and a new objective function are presented that are able to deal with dynamic and highly random through-foliage conditions. Synthetic aperture sensing is our fundamental sampling principle, while we apply drone swarms to approximate the optical signal of extremely wide and adaptable airborne lenses.
Here we make the simulation code available that was used to compute the results presented in the article Synthetic Aperture Sensing for Occlusion Removal with Drone Swarms.

**Publication:** Rakesh John Amala Arokia Nathan, Indrajit Kurmi and Oliver Bimber, Synthetic Aperture Sensing for Occlusion Removal with Drone Swarms, Nature Communications Engineering, (2023), [Nature Com. Eng. (open access)](https://www.nature.com/articles/s44172-023-00104-0#:~:text=Our%20approach%20using%20autonomously%20exploring,or%20security%20threats%20during%20patrols.) 

![image](https://user-images.githubusercontent.com/83944465/209770734-9445a4e5-fb86-4074-953f-d58a67357e69.png)
See **[Video Abstract](https://youtu.be/nb0K7n03qFU)** for a summary. 


## Install
- [Visual studio code with Live Server extension](https://code.visualstudio.com/download)
- [Visual studio - Desktop Development with C++](https://visualstudio.microsoft.com/downloads/)
- [Python 3.7.9](https://www.python.org/downloads/release/python-379/)
- Follow the instructions in [`/LFR/python/README`](./LFR/python/README.md) for the installation of Light-Field Renderer.

### Quick tutorial (droneswarms.ipynb)

Note that droneswarms.ipynb should be within /LFR/python folder so that the libraries and shaders are found at the startup of the renderer (PyAOS).

```py
import pyaos.lfr as LFR
Download_Location = r'Enter the path to your downloads directory' 

#set_parameters
altitude_list = [43,41,39,37,35,36,38,40,42,44]
drone_speed = 10 # m/s
numberofdrones = 10
fov = 50
rxthreshold = 0.9998
dem_height = 33 
scanning_direction = 0
person = [0,10]  
personorientation = 100
person_speed = 4 # m/s

# Hyperparameters
local_fac = 1.0   #c1
global_fac = 2.0   #c2 
scanning_direction_waypoint_distance = 2.0 #c3
minimum_distance_btwn_drone = 4.2 #c4 
changing_to_linear_speed = 0.3 #c5
 
#blob_threshold
emptyblobthreshold = 0.0   # T
```
Run the sections in droneswarms.ipynb after starting the simulator with set parameters.

## AOS-Simulator

The simulation is based on three.js and runs on all major platforms and web browsers.
Start the simulator (/AOS-simulator/aos-simulation-master) using visual studio code. Select Go Live from the status bar to turn the server on/off.

```py
#set_parameters (/AOS-Simulator/aos-simulation-master/config/demo.json)

{
    "drone": {
        "noofdrones": 10,   # (1..10)
         },
    "forest": {
        "size": 300,        # (300/400/500)
	},

}
```

## Client-Server Infrastructure for DJI Swarm Communication and Control

We have developed our own client-server infrastructure for controlling our swarm (currently based on DIJ Mavic 3T). Real-time downstreaming of video- and telemetry-data, as well as upstreaming of waypoint- and control-data was tested for up to 10 platforms.     

![image](https://github.com/JKU-ICG/AOS/blob/stable_release/img/ClientServer2.jpg)

A map visulaization module can be connected to the server for real-time mapping of swarms (drones' positions, heading, full telemetry, and live video data). A digital zoom extends the limited zoom capabilities of conventional map services. Here is a simple live recording of only three drones (note that the screen recording is downsampled to low spatial and temporal resolution): 

<div align="center">
  <video src="https://github.com/JKU-ICG/AOS/assets/83944465/ddc7e786-a140-49e5-959f-63f22a11d2be" width="400" />
</div>

The AOS module implements swarm sampling (currently with our modified particle swarm optimization approach, as explained above [Nature Com. Eng. (open access)](https://www.nature.com/articles/s44172-023-00104-0#:~:text=Our%20approach%20using%20autonomously%20exploring,or%20security%20threats%20during%20patrols.)). A waypoint mission planning module is in preperation. In contrast to the AOS module, it will allow interactive waypoint planning on a map for AOS sampling.  




