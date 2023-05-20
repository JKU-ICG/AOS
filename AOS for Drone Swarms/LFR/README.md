
# AOS/LFR: A Light-Field Renderer for Airborne Optical Sectioning

This is a C++ implementation of the Light-Field Renderer for Airborne Optical Sectioning. 
It is based on OpenGL, uses [Dear ImGui](https://github.com/ocornut/imgui) and [WGLF](https://www.glfw.org/) for a basic user interface, and uses [Assimp](https://www.assimp.org/) to load a digital terrain.

![alt text](../img/LFR.gif)

## [Python bindings](/LFR/python/)
We provide Python bindings, which make it easy to use the renderer in Python projects. To compile them follow the steps described in [`/LFR/python/README`](./python/README.md).

## Install
To compile the renderer with the user interface in native C++ follow the steps below:
### Windows building: 
Open the Visual Studio solution at `/LFR/vs/LFR.sln` and compile it. Compilation has been tested with Visual Studio 2019 and the necessary libraries/DLLs (for Assimp and GLFW) are precompiled and included in the repository (`lib` and `bin`). 
Build for the release version and copy the file 'assimp-vc141-mt.dll' to the release folder (/LFR/vs/x64/Release). The 'dll' file is located in '/LFR/python'

### Linux (e.g. a Raspberry Pi) building: 
Install [GLFW](https://www.glfw.org/) and compile [Assimp](https://www.assimp.org/) first. 
To build the module, make [LFR](/LFR) the current directory and run `make `. 
After that, change the dir to LFR/bin and run './main'. Note that you must go to the subdir of the LFR first before you run the 'main' file.


## Detailed usage

Please take a look at [`/LFR/src/main.cpp`](/LFR/src/main.cpp) for how to use the C++ code.

## Dependencies
Our software builds on the following code/libraries/tools from:
- [Dear ImGui](https://github.com/ocornut/imgui) for the user interface
- [GLFW](https://www.glfw.org/) for opengl window creation
- [Assimp](https://www.assimp.org/) for digital terrain loading
- [Glad](https://glad.dav1d.de/) for opengl loading
- [learnopengl.com](https://learnopengl.com/) for handling shaders and meshes
- [GLM](https://github.com/g-truc/glm) for matrix/vector calculations
- [nlohmann/json](https://github.com/nlohmann/json) for reading and writing JSON files
- [stb_image](https://github.com/nothings/stb) for reading images


