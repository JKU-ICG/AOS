# AOS: Airborne Optical Sectioning for Search and Rescue in Forests

## News


## Publications

This repository contains software for drone-based search and rescue applications as discussed in the following publications:

- David C. Schedl, Indrajit Kurmi, and Oliver Bimber, Autonomous Drones for Search and Rescue in Forests, Science Robotics (under review), (2021)
  - **Todo** [arXiv (pre-print)]  
  - [Data: ](https://doi.org/10.5281/zenodo.4349220) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4349220.svg)](https://doi.org/10.5281/zenodo.4349220)
- David C. Schedl, Indrajit Kurmi, and Oliver Bimber, Search and rescue with airborne optical sectioning, Nature Machine Intelligence 2 (12), 783-790, https://doi.org/10.1038/s42256-020-00261-3 (2020)
  - [Nature (final version)](https://www.nature.com/articles/s42256-020-00261-3) 
  - [arXiv (pre-print)](https://arxiv.org/pdf/2009.08835.pdf)
  - [Data: ](https://doi.org/10.5281/zenodo.3894773) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3894773.svg)](https://doi.org/10.5281/zenodo.3894773)
- Indrajit Kurmi, David C. Schedl, Oliver Bimber, Fast automatic visibility optimization for thermal synthetic aperture visualization, IEEE Geosci. Remote Sens. Lett. available at https://doi.org/10.1109/LGRS.2020.2987471 (2020).
- David C. Schedl, Indrajit Kurmi, and Oliver Bimber, Airborne Optical Sectioning for Nesting Observation. Sci Rep 10, 7254, https://doi.org/10.1038/s41598-020-63317-9 (2020).
  - [Nature (final version)](https://www.nature.com/articles/s41598-020-63317-9) 
- Indrajit Kurmi, David C. Schedl, and Oliver Bimber, Thermal airborne optical sectioning. Remote Sensing. 11, 1668 (2019).
- Indrajit Kurmi, David C. Schedl, and Oliver Bimber, A statistical view on synthetic aperture imaging for occlusion removal. IEEE Sensors J. 19, 9374 – 9383 (2019).
- Oliver Bimber, Indrajit Kurmi, and David C. Schedl, Synthetic aperture imaging with drones. IEEE Computer Graphics and Applications. 39, 8 – 15 (2019).
- Indrajit Kurmi, David C. Schedl, and Oliver Bimber, Airborne optical sectioning. Journal of Imaging. 4, 102 (2018).



## Modules

- [LFR:          C++ and Python code to compute integral images](LFR/README.md)
- [DET:          Python code for person classification](DET/README.md) 
- [CAM:          Python code for triggering, recording, and processing thermal images](CAM/README.md)
- [DRONE:        C++ and Python code for drone communication and control](DRONE/README.md)
- [PLAN:         Python modules for path planning](PLAN/README.md)


## Hardware

XXX picture of our setup XXX

Drone MK Okto XL

Our FLIR camera is connected with a framegrabber, thus OpenCV's builtin video-input functions are used.

## Installation

XXX script compiles everything XXX

A detailed description on how to compile indivdual modules can be found in every modules folder.

## Demo


## License
* Data: Creative Commons Attribution 4.0 International
* Code: You are free to modify and use our software non-commercially; Commercial usage is restricted (see the [LICENSE.txt](LICENSE.txt))


## Todo
* [ ] rework READMEs
* [ ] LFR/Makefile
* [ ] Drone/Makefile
