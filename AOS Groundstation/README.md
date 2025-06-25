# AOS Groundstation

For our [swarm implementation](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20for%20Drone%20Swarms), we present a complete hard- and software framework that supports low-latency transmission (approx. 80 ms round-trip-time) of extensive (70-120 Mbits/s) video and telemetry data, and swarm control for swarms of up to ten drones. Our AOS groundstation (software architecture) allows to operate single or multiple DJI drones from a PC. The drones must be DJI SDK5 compatible. We tested DJI Mavic 3T and DJI Mavic 30T. Our software architecture consists of the following modules:

- **[AOS for DJI App](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20for%20DJI)**: Our DJI app to be installed on the Android remote controller.
- **[AOS server](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20Groundstation/AOS%20server)**: Server for video, telemetry, and waypoint streaming to be installed on a Windows PC.
- **[AOS map visualization](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20Groundstation/AOS%20map%20visualization)**: Visualization module for real-time drone mapping in a webbrowser.
- **[AOS waypoint planning](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20Groundstation/AOS%20waypoint%20planning)**: Module for waypoint mission planning in a webbrowser.

![image](https://github.com/JKU-ICG/AOS/blob/stable_release/img/ClientServer2.jpg)

## Download

- Download the AOS Groundstation repository using git or as a ZIP file and extract its contents.
- Download **[Mosquitto](https://mosquitto.org/files/binary/win64/mosquitto-2.0.18-install-windows-x64.exe)**
- Download the **[AOS for DJI app](https://drive.google.com/file/d/1IXteVwdWi8-W926vCZI2gXri00goVNCK/view?usp=sharing)** to your drone.
- Download the  **[AOS_Broker.exe](https://github.com/JKU-ICG/AOS/releases/tag/v1.0)** file. Then, copy that file in to the AOS server folder.
- Download **[Node.js](https://nodejs.org)**. 

## Installation

### Mosquitto
Mosquito is necessary for AOS map visualization.  In order to complete the installation you need to follow the steps in [AOS map visualization](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20Groundstation/AOS%20map%20visualization).

### AOS Server
- Build and install the DroneSwarmServer application according to the instructions provided in **[AOS Server](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20Groundstation/AOS%20server)**

###  Install Node.js
  
1. Go to [Node.js](https://nodejs.org) and download the latest LTS installer.  
2. Follow the installer prompts.  
3. Confirm installation:
   ```bash
   node --version   # e.g. v18.16.0
   npm --version    # e.g. 9.5.0
   ```
---
Node.js is necessary for AOS waypoint planning. In order to complete the installation you need to follow the steps in [AOS Waypoint Mission Planning](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20Groundstation/AOS%20waypoint%20planning).


**Note:** Restart the pc after the all installations.


## How to use it

After installing all modules on the PC and the DJI app on the remote controller(s), and after making sure that all devices are in the same network, you need to run AOS_Groundstation.bat file inside the AOS Groundstation folder as an administrator. It will automatically launch all modules on the PC: server, map visualization, and waypoint mission planning. Then you need to connect your drones to the server. After all drones are connected, you can go AOS waypoint planning. Start your broker by pressing the **Start Broker** button. That will start the broker and open a new terminal for the broker so that you can observe the print statements. After running the broker, you need to plan your waypoint mission and transmit it to the server (see AOS Waypoint Mission Planning). You will see the mission parameters on the terminal where it appears in the new terminal. Then, you need to activate virtual sticks for all drones which will change the mode of drones to auto. Then you need to press **Takeoff** for the drones to take off and execute the first mission on the AOS waypoint planning. After pressing **Takeoff** they will increase their altitude vertically from the position you took off. The altitude is the altitude of the mission’s first waypoint. If you want to continue with a new mission after all drones completed previous one, you need to set a new mission and send it to the server by pressing **Send Mission** button. After sending the new mission, all drones will execute it right away. Later when you decide to land, you need to press **Landing** button for the drones to return to their altitudes and positions above the initial take-off position and land them. Note, that for take-off and landing, the first and last meters have to be flown manually for safety reasons. So the drones will not directly take off from or land to the ground.

### AOS for DJI app
Basics on how to use and install our DJI compatible app on the remote controller of your drone can be found [here](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20for%20DJI). The latest version (v3.7) supports the communication with the AOS Server. The direct (manual) usage of AOS in the app is restricted to prevent dual use. To enable this feature in the app, an RC-individual keycode has to be requested (by email). This will only be given out to civil (blue-light) organizations. The transmission of videodata, telemetry, and waypoints as well as waypoint flights through the sverver, however, are unrestricted.

- Upon starting the app, press **No Warranty** to acknowledge using the app at your own risk.
- Press the **C3** (front, right) button on the remote controller to navigate to the settings menu. Toggle the **Enable DroneSwarm RTSP Server** button to view the IP address of the remote controller in the settings menu.
- Press **C2** (back, right) to activate virtual stick mode for waypoint flights. 
- Upon completion of the waypoint flight, press the **shutter button** (top-side, right) to disable virtual stick mode and regain manual control of the drone using the remote controller.
  
**Manual usage of the app**

**Note:** Manual usage of the app is restricted by default. Follow these steps to enable this feature.
  - In the settings menu, select the **AOS Scan** toggle button (default state is OFF) to display the serial number of the remote controller.
  - Send an email containing the serial number of your remote controller to request an RC-individual keycode.
  - Enter the received keycode in the **Enter AOS key** field. Select **CONFIGURE AOS KEY** to apply the keycode.
  - Toggle the **AOS Scan** button to ON state which enables the manual usage feature.
  - When the **AOS Scan** button is ON, manual usage feature of the app is enabled. When OFF, the app is configured for performing waypoint flights with the AOS Server.


<div align="center">
	 <video src="https://user-images.githubusercontent.com/83944465/217470172-74a2b272-2cd4-431c-9e21-b91938a340f2.mp4" width="400" />
</div>
		 
### AOS Server
Our client-server infrastructure (contributed by Daniel Mehrwald) supports real-time downstreaming of video- and telemetry-data, as well as upstreaming of waypoint- and control-data was tested for up to 10 platforms. It runs on a Windows PC with sufficient GPU power (we use an Nvidia RTX 4090). 

- Ensure that the Windows PC and all drones are connected to the same network. The DJI app should be installed and the RTSP server should be enabled (see AOS for DJI app) before proceeding with the next steps.
- Navigate to the **Scan Network for Connected Drones** section.
- Click on the **Scan** button. This will display a list of active IP addresses on the network.
- Select the IP address of the active remote controllers from the list and click on the **SendTo** button.
- Go to the **Drone Connection/Live Video Stream** section and select **Connect**.
- Press the **record** (top-side, left) button on the remote controller a few times to initialize the connection. This enables the real time steaming of video and telemetry data.
- For connecting to additional drones, use the **Drone Nr arrow** button to switch to the next drone.
- Repeat the connecting, and initialization steps for each drone.
- By default, hardware decoding (**hevc_cuvid**) is enabled. If your PC does not have a Nvidia GPU (AMD GPU's are not supported), change to software decoding (**hevc**) in the **select decoder** menu before selecting **Connect.**

<div align="center">
  <video src="https://github.com/user-attachments/assets/9416c325-0cec-423e-b1b0-bcf0eb463706" width="400" />
</div>

### AOS Map Visualization
A map visualization module (contributed by Patrick Sack) can be connected to the server for real-time mapping of swarms (drones' positions, heading, full telemetry, and live video data). A digital zoom extends the limited zoom capabilities of conventional map services. It runs in your default webbrowser.  

Note: Before using this module refer to [README](https://github.com/JKU-ICG/AOS/blob/stable_release/AOS%20Groundstation/AOS%20map%20visualization/README.md).

### AOS Waypoint Mission Planning
A waypoint mission planning module (contributed by Patrick Sack) has also been developed. In contrast to the autonomous AOS module, it allows interactive waypoint planning, grid waypoint planning(manual or automatic) on a map and supports planning for single drones as well as swarms - including collision inspection; over flight time or over mission data (waypoint data(speed of drones and holding time) and collision threshold). It runs in your default webbrowser. 

Note: Before start using this module refer to [README](https://github.com/JKU-ICG/AOS/blob/stable_release/AOS%20Groundstation/AOS%20waypoint%20planning/README.md). 

<div align="center">
	<video src="https://github.com/user-attachments/assets/1ea8e7f5-da1a-4faf-a66e-808cd7f62f79" width="400" />
</div>
		
## License
* Data: Creative Commons Attribution 4.0 International
* Software Modules: You are free to modify and use our software non-commercially; Commercial usage is restricted (see the [LICENSE.txt](LICENSE.txt))
