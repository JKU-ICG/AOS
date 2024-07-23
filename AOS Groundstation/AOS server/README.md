# Installation Procedure

- Install [Git for Windows x64](https://git-scm.com/download/win)
- Install [Visual studio 2022 Community Edition](https://visualstudio.microsoft.com/de/vs/community/) with
  * -- C++ MFC for latest v143 build tools (x86 & x64)
  * -- C++/CLI support for v143 build tools (latest)
- Install [Python 3.7.9](https://www.python.org/downloads/release/python-379/) and update the Python path in the environment variables list. Install the following libraries : numpy, opencv-python, matplotlib, keyboard, paho-mqtt
- Install [CMake for Windows](https://cmake.org/download/) (Windows x64 Installer).
- Install [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads) for Windows 11 (CUDA Toolkit 12.2.1 and CUDA Toolkit 11.8.0 are tested and working, latest should also work).
- Install [Npcap](https://npcap.com/dist/npcap-1.79.exe) Packet capture library for Windows
- Install [MSYS2](https://www.msys2.org/) needed for FFmpeg compilation

## Getting the source code
- Choose a location for your project from within a Explorer window.
- Right Click and choose _expanded options -> Open Git GUI here
  <img width="640" alt="c710d54e-87f1-4c70-b863-1fca79ff8170" src="https://github.com/user-attachments/assets/115a52d3-9df6-4791-b621-d2e19dd4da40">
- Then type ```git clone https://github.com/JKU-ICG/AOS.git``` and hit enter.

## Building 
- Open x64 Native Tools Command Prompt for VS 2022, go to search and type 'x64' and double click on the search result
  <img width="512" alt="prompt" src="https://github.com/user-attachments/assets/8a361eb0-ba6c-45f9-ba43-5b9a45477570">
  * From there change directory to Droneswarm_Wrapper. e.g ```cd D:\mytestProject\AOS\AOS Groundstation\AOS server\DroneSwarm_Wrapper```
  * ```mkdir build```
  * ```cd build```
  * ```cmake -G "Visual Studio 17 2022" -A x64 ..\.```
  * Now open the genereated **_DroneSwarmWrapper.sln_** file by double click on it and build the Python wrapper library **_(build -> build ds_wrapper)_**
- Depending on your build configuration (Release or Debug) you can find the Python wrapper library with it's import library inside your build folder (e.g build\Release), copy the import library **_(ds_wrapper.lib)_** to your _DroneSwarmServer_ folder ```D:\mytestProject\AOS\AOS Groundstation\AOS server\DroneSwarmServer```
- Download the [Npcap SDK](https://npcap.com/dist/npcap-sdk-1.13.zip)
- Open the zip by double click on it and copy the contains of the **_include_** folder to ```C:\Program Files (x86)\Windows Kits\10\Include\10.0.xxxxx.0\um``` and the contains of the **_Lib\x64_** folder to ```C:\Program Files (x86)\Windows Kits\10\Lib\10.0.xxxxx.0\um\x64``` _(xxxxx should be the higest version number in that directory)_
  <img width="512" alt="16287878-3859-44c5-b662-d2df2fc28bd8" src="https://github.com/user-attachments/assets/257e1107-65ff-4569-bedc-fb87d6dd4397">
  <img width="512" alt="9d07b0fd-85a7-40f1-b88f-4cd8313628d6" src="https://github.com/user-attachments/assets/172240ad-ba5e-4588-8231-7c21d49084ec">
- Clone Paho Eclipse MQTT Client source code with
  * ```cd D:\mytestProject```
  * ```git clone https://github.com/eclipse/paho.mqtt.c.git```
  * ```cd paho.mqtt.c```
  * ```mkdir build```
  * ```cd build```
  * ```cmake -G "Visual Studio 17 2022" -A x64 -D PAHO_BUILD_STATIC=TRUE -D PAHO_BUILD_SHARED=FALSE ..\.```
  * Open **_Eclipse Paho C.sln_** with Visual Studio 2022 by double click on it, choose Release as build type and build the MQTT Client libraries **_(build -> build Solution)_**
  * From the ```build\src\Release``` directory copy **_paho-mqtt3c-static.lib_** and **_paho-mqtt3a-static.lib_** to your ```D:\mytestProject\AOS\AOS Groundstation\AOS server\DroneSwarmServer``` directory
  * From the ```src``` directory copy **_MQTTAsync.h MQTTClient.h MQTTClientPersistence.h MQTTExportDeclarations.h MQTTProperties.h MQTTReasonCodes.h MQTTSubscribeOpts.h_** files to your ```D:\mytestProject\AOS\AOS Groundstation\AOS server\DroneSwarmServer``` directory
- We used **[FFmpeg 6.1](https://github.com/FFmpeg/FFmpeg/tree/release/6.1)** compiled with **_NVIDIA hardware decoder_** support, however due to newer CUDA Tool Kits in this build instruction we use **FFmpeg 7.0.1**
  * Open again x64 Native Tools Command Prompt for VS 2022, go to search and type 'x64' and double click on the search result
  * From there change directory to your MSYS2 installation e.g ```cd D:\mytestProject\msys64```
  * Then type ```msys2_shell -ucrt64 -use-full-path``` -> a MSYS2 shell will be opened
  * From the MSYS2 shell rename the linker command in order to use the Microsoft linker cmd instead with ```mv /usr/bin/link.exe /usr/bin/link.orig```
  * Install some packages needed to build FFmpeg with ```pacman -S make pkg-config diffutils```
  * Change directory to your project location -> e.g ```cd /d/mytestProject``` **(Your directory structure should not contain any spaces!)**
  * Then get the FFmpeg sources with ```git clone https://github.com/FFmpeg/FFmpeg.git```
  * ```cd FFmpeg```
  * ```git reset --hard af25a4b```
  * ```mkdir include```
  * Copy everything from ```C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.x\include``` to the newly created **_include_** directroy (**_D:\mytestProject\FFmpeg\include_**)
  * ```mkdir lib```
  * Copy everything from ```C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.x\lib\x64``` to the newly created **_lib_** directroy (**_D:\mytestProject\FFmpeg\lib_**)
  * ```cd include```
  * ```git clone https://github.com/FFmpeg/nv-codec-headers.git```
  * ```cp -R nv-codec-headers/include/ffnvcodec/ .```
  * ```cd nv-codec-headers```
  * Edit first line in **_Makefile_** from **_PREFIX = /usr/local_** to **_PREFIX = /ucrt64_**
  * ```make install```
  * ```cd ../..```
  * Now configure FFmpeg with ```./configure --disable-vulkan --disable-vdpau --disable-vaapi --enable-cuda --disable-cuda-llvm --enable-cuvid --enable-asm --enable-x86asm --disable-avdevice --disable-doc --disable-ffplay --disable-ffprobe --disable-shared --enable-static --disable-bzlib --disable-libopenjpeg --disable-iconv --disable-zlib --enable-nvdec --enable-nvenc --enable-nonfree --enable-ffnvcodec --enable-nonfree --prefix=/c/FFmpeg-7.0.1 --toolchain=msvc --target-os=win64 --arch=x86_64 --extra-ldflags="/MACHINE:X64 /NODEFAULTLIB:libcmt /LIBPATH:\"D:\\\mytestProject\\\FFmpeg\\\lib\"" --extra-cflags="-MD -I \"D:\\\mytestProject\\\FFmpeg\\\include\" -I \"D:\\\mytestProject\\\FFmpeg\\\include\\\ffnvcodec\""```
  * After configure is done type ```make V=1 -j10``` and hit enter
  * After build is done type ```make install V=1 -j10``` and hit enter, your FFmpeg libraries are now in ```C:\FFmpeg-7.0.1``` folder
  * From the **_C:\FFmpeg-7.0.1\lib_** folder copy **_libavcodec.a libavfilter.a libavformat.a libavutil.a libswresample.a libswscale.a_** over to your ```D:\mytestProject\AOS\AOS Groundstation\AOS server\DroneSwarmServer``` directory
  * From the **_C:\FFmpeg-7.0.1\include_** folder copy this sub directories + contains **_libavcodec libavfilter libavformat libavutil libswresample libswscale_** to your ```D:\mytestProject\AOS\AOS Groundstation\AOS server\DroneSwarmServer``` directory
  * Then execute the file **_gen_win_library.bat_** from your ```D:\mytestProject\AOS\AOS Groundstation\AOS server\DroneSwarmServer``` directory by double click on it.
- Open **_DroneSwarmServer.sln_** with Visual Studio 2022 by double click on it and build the server **_(build -> build DroneSwamServer)_**, this will give you the (DroneSwarmServer.exe) executeable.
- The **_DroneSwarmServer_** executeable and **_ds_wrapper.cp37-win_amd64.pyd_** must be in the same folder.

Start the wrapper before running the app file.

```import ds_wrapper as w```

Now run the app (DroneSwarmServer.exe). 

**Note:** the **_DroneSwarmServer_** is running with **_Administrator_** credentials, therefore if you run your Python scripts with VSCode, VSCode must run also with **_Admin_** credentials
