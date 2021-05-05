# AOS: Airborne Optical Sectioning for Search and Rescue in Forests

This repository contains software for drone-based search and rescue applications as discussed in the following publications:

- David C. Schedl, Indrajit Kurmi, and Oliver Bimber, [Search and rescue with airborne optical sectioning](https://arxiv.org/pdf/2009.08835.pdf), Nature Machine Intelligence 2 (12), 783-790, 2020
  - [Data: ](https://doi.org/10.5281/zenodo.3894773) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3894773.svg)](https://doi.org/10.5281/zenodo.3894773)
- David C. Schedl, Indrajit Kurmi, and Oliver Bimber, Autonomous Drones for Search and Rescue in Forests, Science Robotics (under review), 2021
  - [Data: ](https://doi.org/10.5281/zenodo.4349220) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4349220.svg)](https://doi.org/10.5281/zenodo.4349220)
- IEEE Sensors?

## Modules

- LFR:          C++ and Python code to compute integral images
- DET:          Python code for person classification 
- CAM:          Python code for triggering, recording, and processing thermal images
- DRONE:        C++ and Python code for drone communication and control
- PLAN:         Python modules for path planning


## Hardware

XXX picture of our setup XXX

Drone MK Okto XL

Our FLIR camera is connected with a framegrabber, thus OpenCV's builtin video-input functions are used.

## Installation

XXX script compiles everything XXX

A detailed description on how to compile indivdual modules can be found in every modules folder.

## Demo


## License:
* Data: Creative Commons Attribution 4.0 International
* Code: You are free to modify and use our software non-commercially; Commercial usage is restricted (see the [LICENSE.txt](LICENSE.txt))
