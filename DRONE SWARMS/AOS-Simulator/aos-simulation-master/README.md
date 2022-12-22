# AOS-Simulation

[Airborne Optical Sectioning Simulation](https://aos.tensorware.app) based on:

- David C. Schedl, Indrajit Kurmi, and Oliver Bimber, Search and rescue with airborne optical sectioning, Nature Machine Intelligence 2, 783-790, https://doi.org/10.1038/s42256-020-00261-3 (2020)
  - [Nature (final version)](https://www.nature.com/articles/s42256-020-00261-3) | [(view only version)](https://rdcu.be/cbcf2)
  - [arXiv (pre-print)](https://arxiv.org/pdf/2009.08835.pdf)
  - [Data: ](https://doi.org/10.5281/zenodo.3894773) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3894773.svg)](https://doi.org/10.5281/zenodo.3894773)
  - [Video on YouTube](https://www.youtube.com/watch?v=kyKVQYG-j7U)

> We show that automated person detection under occlusion conditions can be significantly improved by combining multi-perspective images before classification. Here, we employed image integration by Airborne Optical Sectioning (AOS) - a synthetic aperture imaging technique that uses camera drones to capture unstructured thermal light fields - to achieve this with a precision/recall of 96/93%. Finding lost or injured people in dense forests is not generally feasible with thermal recordings, but becomes practical with use of AOS integral images. Our findings lay the foundation for effective future search and rescue technologies that can be applied in combination with autonomous or manned aircraft. They can also be beneficial for other fields that currently suffer from inaccurate classification of partially occluded people, animals, or objects.

### Publications [![github](https://img.shields.io/badge/github-gray?logo=github&logoColor=white)](#Publications)

Additional publications and software modules for AOS based search and rescue can be found on the author's [main repository](https://github.com/JKU-ICG/AOS).

## Simulation [![html](https://img.shields.io/badge/html-gray?logo=html5&logoColor=white)](#Simulation)

The simulation is based on [three.js](https://threejs.org) and runs on all major platforms and web browsers.

Navigation (zoom, pan, rotate) is available via mouse and touch events.
User controls allow the adjustment of several parameters for:

- `drone`
  - `camera`
  - `cpu`
- `forest`
  - `trees`
    - `branching`
    - `trunk`
  - `persons`
    - `activities`
- `material`
  - `color`

The simulation data may be exported as a zip file for further processing and analysis.

### Online [![browser](https://img.shields.io/badge/browser-gray?logo=googlechrome&logoColor=white)](#Online) [![status](https://img.shields.io/badge/status-up-brightgreen)](#Online)

An online version of this repository code can be found [here](https://aos.tensorware.app).

### Application [![electron](https://img.shields.io/badge/electron-gray?logo=electron&logoColor=white)](#Application) [![platform](https://img.shields.io/badge/platform-windows%20|%20linux%20|%20macos-lightgrey)](#Application)

Additional a standalone application is available for automated and parallelized data export.

[![app](/img/app.gif)](https://aos.tensorware.app)

More details can be found in [INSTALL.md](/INSTALL.md).

## Source [![download](https://img.shields.io/badge/download-free-lightgrey)](#Source)

Drone from [clara.io](https://clara.io):

- [drone.stl](https://clara.io/view/1c6e9fef-d10d-42d0-8493-d619c2b95f55)

Persons from [mixamo.com](https://www.mixamo.com):

- [male.glb](https://www.mixamo.com/#/?page=1&query=Y-Bot&type=Character)
- [female.glb](https://www.mixamo.com/#/?page=1&query=X-Bot&type=Character)

Textures from [texture.ninja](https://texture.ninja):

- [broad-leaf.png](https://texture.ninja/textures/Leaves/4)
- [needle-leaf.png](https://texture.ninja/textures/Leaves/4)

Fonts from [fonts.google.com](https://fonts.google.com):

- [opensans.json](https://fonts.google.com/specimen/Open+Sans)

## License [![license](https://img.shields.io/badge/license-MIT-green)](#License)

[MIT](/LICENSE)
