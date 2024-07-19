# AOS for Drone Swarms (AOS_DJI_SDKv5 - Wrapper/Server)

## Install
- Install [Git for Windows x64](https://git-scm.com/download/win)
- Install [Visual studio 2022 Community Edition](https://visualstudio.microsoft.com/de/vs/community/) with
  * -- C++ MFC for latest v143 build tools (x86 & x64)
  * -- C++/CLI support for v143 build tools (latest)
- Install [Python 3.7.9](https://www.python.org/downloads/release/python-379/) and update the Python path in the environment variables list.
- Install [CMake for Windows](https://cmake.org/download/) (Windows x64 Installer).
- Install [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads) for Windows 11 (CUDA Toolkit 12.2.1 and CUDA Toolkit 11.8.0 are tested and working, lastest should also work).
- Install [Npcap](https://npcap.com/dist/npcap-1.79.exe) Packet capture library for Windows

## Getting the source code
- Choose a location for your project from within a Explorer window.
- Right Click and choose _expanded options -> Open Git GUI here_
  <img width="640" alt="testProject" src="https://github.com/user-attachments/assets/c710d54e-87f1-4c70-b863-1fca79ff8170">
- Then type ```git clone https://github.com/JKU-ICG/AOS_DJI_SDKV5.git``` and hit enter.

## Building 
- Open x64 Native Tools Command Prompt for VS 2022, go to search and type 'x64'
  <img width="512" alt="prompt" src="https://github.com/user-attachments/assets/15e5659e-1df0-4590-9df4-aacceb50047b">
  * From there change directory to Droneswarm_Wrapper. e.g ```cd D:\mytestProject\AOS_DJI_SDKV5\DroneSwarm_Wrapper```
  * ```mkdir build```
  * ```cd build```
  * ```cmake -G "Visual Studio 17 2022" -A x64 ..\.```
  * Now open the genereated **_DroneSwarmWrapper.sln_** file by double click on it and build the Python wrapper library **_(build -> build ds_wrapper)_**
- Depending on your build configuration (Release or Debug) you can find the Python wrapper library with it's import library inside your build folder (e.g build\Release), copy the import library **_(ds_wrapper.lib)_** to your _DroneSwarmServer_ folder ```D:\mytestProject\AOS_DJI_SDKV5\DroneSwarmServer```
- Download the [Npcap SDK](https://npcap.com/dist/npcap-sdk-1.13.zip)
- Open the zip by double click on it and copy the contains of the **_include_** folder to ```C:\Program Files (x86)\Windows Kits\10\Include\10.0.xxxxx.0\um``` and the contains of the **_Lib\x64_** folder to ```C:\Program Files (x86)\Windows Kits\10\Lib\10.0.xxxxx.0\um\x64``` _(xxxxx should be the higest version number in that directory)_
  <img width="512" alt="2024-07-13 (2)" src="https://github.com/user-attachments/assets/16287878-3859-44c5-b662-d2df2fc28bd8">
  <img width="512" alt="2024-07-13 (4)" src="https://github.com/user-attachments/assets/9d07b0fd-85a7-40f1-b88f-4cd8313628d6">
- Clone Paho Eclipse MQTT Client source code with
  * ```cd D:\mytestProject```
  * ```git clone https://github.com/eclipse/paho.mqtt.c.git```
  * ```cd paho.mqtt.c```
  * ```mkdir build```
  * ```cd build```
  * ```cmake -G "Visual Studio 17 2022" -A x64 -D PAHO_BUILD_STATIC=TRUE -D PAHO_BUILD_SHARED=FALSE ..\.```
  * Open **_Eclipse Paho C.sln_** with Visual Studio 2022 by double click on it, choose Release as build type and build the MQTT Client libraries **_(build -> build Solution)_**
  * From the ```build\src\Release``` directory copy **_paho-mqtt3c-static.lib_** and **_paho-mqtt3a-static.lib_** to your ```D:\mytestProject\AOS_DJI_SDKV5\DroneSwarmServer``` directory
  * From the ```src``` directory copy **_MQTTAsync.h MQTTClient.h MQTTClientPersistence.h MQTTExportDeclarations.h MQTTProperties.h MQTTReasonCodes.h MQTTSubscribeOpts.h_** files to your ```D:\mytestProject\AOS_DJI_SDKV5\DroneSwarmServer``` directory
- We used **[FFmpeg 6.1](https://github.com/FFmpeg/FFmpeg/tree/release/6.1)** compiled with **_NVIDIA hardware decoder_** support, using this configure switches ```./configure --disable-vulkan --disable-vdpau --disable-vaapi --enable-cuda --enable-cuvid --enable-asm --enable-x86asm --disable-avdevice --disable-cuda-llvm  --disable-doc --disable-ffplay --disable-ffprobe --disable-shared --enable-static --disable-bzlib --disable-libopenjpeg --disable-iconv --disable-zlib --enable-nvdec --enable-nvenc --enable-ffnvcodec --enable-nonfree --toolchain=msvc --arch=x86_64 --extra-ldflags="/MACHINE:X64 /NODEFAULTLIB:libcmt --nvccflags="-gencode arch=compute_52,code=sm_52 -O2"```, the toolchain we used was Microsoft Visual C++
  * Please follow this external guide to compile it [MSVC Compiliation Guide](https://trac.ffmpeg.org/wiki/CompilationGuide/MSVC)
  * After ```make install V=1``` look where your binaries and header files got copied
  * From the **_lib_** folder copy **_libavcodec.a libavfilter.a libavformat.a libavutil.a libswresample.a libswscale.a_** over to your ```D:\mytestProject\AOS_DJI_SDKV5\DroneSwarmServer``` directory
  * From the **_include_** folder copy this sub directories + contains **_libavcodec libavfilter libavformat libavutil libswresample libswscale_** to your ```D:\mytestProject\AOS_DJI_SDKV5\DroneSwarmServer``` directory
  * Then execute the file **_gen_win_library.bat_** from your ```D:\mytestProject\AOS_DJI_SDKV5\DroneSwarmServer``` directory by double click on it.
- Open **_DroneSwarmServer.sln_** with Visual Studio 2022 by double click on it and build the server **_(build -> build DroneSwamServer)_**, this will give you the (DroneSwarmServer.exe) executeable.
- The **_DroneSwarmServer_** executeable and **_ds_wrapper.cp37-win_amd64.pyd_** must be in the same folder.

Start the wrapper before running the app file.

```import ds_wrapper as w```

Now run the app (DroneSwarmServer.exe). 

**Note:** the **_DroneSwarmServer_** is running with **_Administrator_** credentials, therefore if you run your Python scripts with VSCode, VSCode must run also with **_Admin_** credentials
