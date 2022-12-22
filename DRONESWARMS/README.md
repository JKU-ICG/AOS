Data: Synthetic Aperture Sensing for Occlusion Removal with Drone Swarms
====================================================================
Supplementary Dataset for the article "Synthetic Aperture Sensing for Occlusion Removal with Drone Swarms".

**Abstract:**
We demonstrate how efficient autonomous drone swarms can be in detecting and tracking occluded targets in dense forest, such as lost people during search and rescue missions. The exploration and optimization of local viewing conditions, like occlusion density and target view obliqueness, results in much faster and much more reliable findings compared to previous blind sampling strategies that are based on pre-defined waypoints. An adapted real-time particle swarm optimization and a new objective function are presented that are able to deal with dynamic and highly random through-foliage conditions. Synthetic aperture sensing is our fundamental sampling principle, while we apply drone swarms to approximate the optical signal of extremely wide and adaptable airborne lenses.

**Authors:** Rakesh John Amala Arokia Nathan, Indrajit Kurmi,Oliver Bimber

# Content [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5680949.svg)](https://doi.org/10.5281/zenodo.5680949)

The data is available open access at [Zenodo](https://doi.org/10.5281/zenodo.5680949). Further details can be found in the main article and supplementary material of our article.
The package contains the zip file: `data` .



## Data

The zip package `data` contains the following datasets: 

* Sequentially_sampling_single_camera_drone
* Parallelly_sampling_camera_array
* Swarm_of_three_camera_drones
* Swarm_of_five_camera_drones
* Swarm_of_ten_camera_drones_density_300
* Swarm_of_ten_camera_drones_density_400
* Swarm_of_ten_camera_drones_density_500
* Motion_tracking_linearpath
* Motion_tracking_circularpath

Each set contain the following 12 subfolders:

* debug
* masked_integral 
* masked_integral(with_history)
* objective_metric_plot
* Result
* RGB(single_images)
* RGB_integral
* RGB_integral(with_history)
* stage_images
* Thermal(single_images)
* Thermal_integral
* Thermal_integral(with_history)
 


AOS source code for generating the integral images, datasets, and publications are available at https://github.com/JKU-ICG/AOS/ .

The source code for AOS-simulator and droneswarms are available at https://github.com/JKU-ICG/AOS/ .



# License:
* Data: Creative Commons Attribution 4.0 International
* Code: MIT License (license text below)
    
        Copyright 2020 Johannes Kepler University Linz

        Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

        The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.