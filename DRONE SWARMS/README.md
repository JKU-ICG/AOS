# AOS: Airborne Optical Sectioning

Airborne Optical Sectioning (AOS) is a wide synthetic-aperture imaging technique that employs manned or unmanned aircraft, to sample images within large (synthetic aperture) areas from above occluded volumes, such as forests. Based on the poses of the aircraft during capturing, these images are computationally combined to integral images by light-field technology. These integral images suppress strong occlusion and reveal targets that remain hidden in single recordings.

Single Images         |  Airborne Optical Sectioning
:-------------------------:|:-------------------------:
![single-images](../img/Nature_single-images.gif) | ![AOS](../img/Nature_aos.gif)

> Source: [Video on YouTube](https://www.youtube.com/watch?v=kyKVQYG-j7U) | [FLIR](https://www.flir.com/discover/cores-components/researchers-develop-search-and-rescue-technology-that-sees-through-forest-with-thermal-imaging/)
 

## Synthetic Aperture Sensing for Occlusion Removal with Drone Swarms

### Quick tutorial (droneswarms.ipynb)
```py
import pyaos.lfr as LFR
Download_Location = r'Enter your path here' 

#set_parameters
altitude_list = [43,41,39,37,35,36,38,40,42,44]
drone_speed = 10 # m/s
NumberofDrones = 10
fov = 50
rxthreshold = 0.9998
dem_height = 33 
Scanning_direction = 0
person=[0,10]  
personorientation = 100
person_speed = 4 # m/s


# Hyperparameters
local_fac = 1.0   #c1
global_fac = 2.0   #c2 
Scanning_direction_Waypoint_Distance = 2.0 #c3
minimum_distance_btwn_drone = 4.2 #c4 
changing_to_linear_speed = 0.3 #c5
 


#blob_threshold
emptyblobthreshold = 0.0   # T
```


