# AOS Simulation

A first version of our AOS simulator was implemented by Francis Seits in 2022. It was realized with a procedural forest algorithm called ProcTree and was implemented with WebGL. It supports various procedural tree parameters, such as tree height, trunk length, trunk radius, and leaf size, and tree species. A seeded random generator was applied to generate a variety of trees at defined densities and degrees of similarity. Aerial images for different drone poses and camera parameters, such as field of view, could be rendered with it which were used as input for AOS.  

- Francis Seits, Indrajit Kurmi, Rakesh John Amala Arokia Nathan, Rudolf Ortner and Oliver Bimber, On the Role of Field of View for Occlusion Removal with Airborne Optical Sectioning (2022)
  - [arXiv (pre-print)](https://arxiv.org/abs/2204.13371) 
  - [AOS simulator](https://aos.tensorware.app)
  - [code](https://github.com/tensorware/aos-simulation)

In 2022, a team of the Otto-von-Guericke-University Magdeburg re-implented the first simulator version in Gazebo in 2023. It became significantly faster and offered several additional options, such as thermal camera and depth camera simulation. 
- Lukas Bostelmann-Arp, Christoph Steup, and Mostaghim
  - [Gazebo-based AOS simulator](https://github.com/bostelma/gazebo_sim/tree/main)
 
The Gazebo-based AOS simulator was later used for the generation of training data to support machine learing architectures, such as for AOS image restoration. Available simulated training datasets are:
- [Image Restoration](https://drive.google.com/drive/folders/1UC6sGGWkRpJjqyYOnqByaa_mxeucFmqJ): 33.000 simulations with random 100 trees/ha and 200 trees/ha and random person figure poses and positions. 


