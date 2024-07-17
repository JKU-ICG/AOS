# AOS for Drone Swarms

This Weave ([FWF](https://www.fwf.ac.at/en/) & [DFG](https://www.dfg.de/en/index.jsp)) funded basic research project is on exploring AOS for moving targets, in paricular using drone swarms. It started in April 2023, and we are collaborating with the [German Aerospace Center (DLR)](https://www.dlr.de/EN/Home/home_node.html).

## Synthetic Aperture Sensing for Occlusion Removal with Drone Swarms (Simulation)

We demonstrate how efficient autonomous drone swarms can be in detecting and tracking occluded targets in dense forest, such as lost people during search and rescue missions. The exploration and optimization of local viewing conditions, like occlusion density and target view obliqueness, results in much faster and much more reliable findings compared to previous blind sampling strategies that are based on pre-defined waypoints. An adapted real-time particle swarm optimization and a new objective function are presented that are able to deal with dynamic and highly random through-foliage conditions. Synthetic aperture sensing is our fundamental sampling principle, while we apply drone swarms to approximate the optical signal of extremely wide and adaptable airborne lenses.
Here we make the simulation code available that was used to compute the results presented in the article Synthetic Aperture Sensing for Occlusion Removal with Drone Swarms.

**Publication:** Rakesh John Amala Arokia Nathan, Indrajit Kurmi and Oliver Bimber, Synthetic Aperture Sensing for Occlusion Removal with Drone Swarms, Nature Communications Engineering, (2023), [Nature Com. Eng. (open access)](https://www.nature.com/articles/s44172-023-00104-0#:~:text=Our%20approach%20using%20autonomously%20exploring,or%20security%20threats%20during%20patrols.) 

![image](https://user-images.githubusercontent.com/83944465/209770734-9445a4e5-fb86-4074-953f-d58a67357e69.png)
See **[Video Abstract](https://youtu.be/nb0K7n03qFU)** for a summary. 


### Install
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

### AOS-Simulator

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

## An Autonomous Drone Swarm for Detecting and Tracking Anomalies in Dense Vegetation (Physical Implementation)

Swarms of drones offer an increased sensing aperture, and having them mimic behaviors of natural swarms enhances sampling by adapting the aperture to local conditions. We demonstrate that such an approach makes detecting and tracking heavily occluded targets practically feasible. While object classification applied to conventional aerial images generalizes poorly the randomness of occlusion and is therefore inefficient even under lightly occluded conditions, anomaly detection applied to synthetic aperture integral images is robust for dense vegetation, such as forests, and is independent of pre-trained classes. Our autonomous swarm searches the environment for occurrences of the unknown or unexpected, tracking them while continuously adapting its sampling pattern to optimize for local viewing conditions. In our real-life field experiments with a swarm of six drones, we achieved an average positional accuracy of 0.39 m with an average precision of 93.2% and an average recall of 95.9%. Here, adapted particle swarm optimization considers detection confidences and predicted target appearance. We show that sensor noise can effectively be included in the synthetic aperture image integration process, removing the need for a computationally costly optimization of high-dimensional parameter spaces. Finally, we present a complete hard- and [software](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20Groundstation) framework that supports low-latency transmission (approx. 80 ms round-trip time) and fast processing (approx. 600 ms per formation step) of extensive (70-120 Mbit/s) video and telemetry data, and swarm control for swarms of up to ten drones.

**Publication:** Rakesh John Amala Arokia Nathan, Sigrid Strand, Daniel, Mehrwald, Dmitriy Shutin, Oliver Bimber, An Autonomous Drone Swarm for Detecting and Tracking Anomalies among Dense Vegetation, under review (2024)
  - [arXiv (pre-print)](https://arxiv.org/abs/2407.10754)
  - [Video Abstract](https://www.youtube.com/playlist?list=PLgGsWgs4hgaMXzo7QhSwNRctz9JTvh1JM)
  - [Data: ](https://doi.org/10.5281/zenodo.12720784)[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.12720784.svg)](https://doi.org/10.5281/zenodo.12720784) 

Our autarkic and mobile ground station (components provided by the German Aerospace Center, DLR) can drive 10 platforms in real-time (downstreaming of video- and telemetry-data, as well as upstreaming of waypoint- and control-data). It consists of a high end PC (5.8GHz Intel i9-13900KF processor (24 cores), 24GB Nvidia Geforce RTX 4090 OC GPU, 64GB RAM), a 16x Gigabit switch for fast internal data transmission between remote controllers, PC, and an external 5G link for networked RTK data transmission. The Bosch power 1500 profi battery ensures power supply in the field for approximatly 10 hours. The AOS module in our [ground station](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20Groundstation) implements the autonomous swarm sampling (currently with our modified particle swarm optimization approach, as explained above [Nature Com. Eng. (open access)](https://www.nature.com/articles/s44172-023-00104-0#:~:text=Our%20approach%20using%20autonomously%20exploring,or%20security%20threats%20during%20patrols.). 

![image](https://github.com/JKU-ICG/AOS/blob/stable_release/img/mobile_setup.jpg)

### Field Experiments

First field experiments with a swarm of 6 DJI Mavic 3T drones have been carried out together with the German Aearospace Center (DLR) All drones operated fully autonomously using our adapted real-time particle swarm optimization in combination with AOS, and the the above-described soft- and hardware system. A summary of all field experiments and an evaluation of the detection and tracking precision can be found **[here](https://www.youtube.com/playlist?list=PLgGsWgs4hgaMXzo7QhSwNRctz9JTvh1JM)**.       

[![Swarm Open Field](https://github.com/JKU-ICG/AOS/blob/stable_release/img/First_Field_Experiments_Poecking.png)](https://www.youtube.com/watch?v=uiMJt6otmSQ "Swarm Open Field")


### Software

Our AOS groundstation (the software architecture explained above) is available **[here](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20Groundstation)**. 
