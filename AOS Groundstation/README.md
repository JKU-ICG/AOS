# AOS Groundstation

For our swarm implementation, we present [a complete hard- and software framework](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20for%20Drone%20Swarms) that supports low-latency transmission (approx. 80 ms round-trip-time) of extensive (70-120 Mbits/s) video and telemetry data, and swarm control for swarms of up to ten drones. Our AOS groundstation (software architecture) allows to operate singe or multilple DJI drones from a PC. The drones must be DJI SDK5 compatible. We tested DJI Mavic 3T and DJI Mavic 30T. Our software architecture consists of the following modules:

- **[AOS for DJI App](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20for%20DJI)**: Our DJI app to be installed on the remote controller.
- **[AOS Server](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20for%20Drone%20Swarms)**: Server for video, telemetry, and waypoint streaming to be installed on a Windows PC.
- **[AOS Map Visualization](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20for%20Drone%20Swarms)**: Visualization module for real-time drone mapping in a webbrowser.
- **[AOS Waypoint Mission Planning](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20for%20Drone%20Swarms)**: Module for waypoint mission planning in a webbrowser.

![image](https://github.com/JKU-ICG/AOS/blob/stable_release/img/ClientServer2.jpg)

## Download
Coming soon...

## Installation
Coming soon...

## How to use it
After installing all modules on the PC and the DJI app on the remote controller(s), and after making sure that all devices are in the same network, you need to start AOS_Groundstation.bat. It will automatically launch all modules on the PC: server, map visualization, waypoint mission planning. You first need to connect the drones to the server (see AOS server), then plan your wayoint missions and transmit it to the server (see AOS Waypoint Mission PLanning). You need to press XXX for the drones to take off. After they reached the altitudes of the first waypoints above the initial take-off position, you need to press XXX to start the mission. After the mission is completed, the drones return to their initial altitudes of the first waypoint above the initial take-off position. You need to press XXX to land them. Note, that for take.off and landing, the first and last meter have to be flown manually for safety reasons. So the drones will not directly take off from or land to the ground.  


### AOS for DJI app
Basics on how to use and install our DJI compatible app on remote controllers can be found [here](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20for%20DJI). The latest version (v3.7) supports the communication with the AOS server. The direct (manual) usage of AOS in the app is restrictuted to prevent dual use. To enable this feature in the app, a RC-individual keycode has to be requested (by email). This will only given to civil (blue-light) organizations. The transmission of videodata, telemetry, and waypoints as well as waypoint flights through the sverver, however, are unrestricted.

- XX



### AOS Server
Our client-server infrastructure (contributed by Daniel Mehrwald) supports real-time downstreaming of video- and telemetry-data, as well as upstreaming of waypoint- and control-data was tested for up to 10 platforms. It runs on a Windows PC with sufficient GPU power (we use an Nvidia RTX 4090). 

- XXX

<div align="center">
  <video src="https://github.com/user-attachments/assets/9416c325-0cec-423e-b1b0-bcf0eb463706" width="400" />
</div>

### AOS Map Visualization
A map visualization module (contributed by Patrick Sack) can be connected to the server for real-time mapping of swarms (drones' positions, heading, full telemetry, and live video data). A digital zoom extends the limited zoom capabilities of conventional map services. It runs in your default webbrowser.  

- The map is used in the same way as any other online map (scrolling, zooming, switching to satelite view, etc).
- Clicking on the drone icons (which visualize position and heading) turns on/off the live video/telemetry window.
  
<div align="center">
  <video src="https://github.com/JKU-ICG/AOS/assets/83944465/ddc7e786-a140-49e5-959f-63f22a11d2be" width="400" />
</div>

### AOS Waypoint Mission Planning
A waypoint mission planning module (contributed by Patrick Sack) has also been developed. In contrast to the autonomous AOS module, it allows interactive waypoint planning on a map and supports planning for single drones as well as swarms - including collision inspection over flight time. It runs in your default webbrowser.

- Add waypoints to the map by left click in the map.
- To move a waypoint to a new positions, you can drag and drop the marker by a left mouse click.
- Removing waypoints works by selecting a waypoint with a left mouse click on the marker and use the "remove waypoint" button. You can also remove a waypoint by a right clicking on the marker.
- Input parameters are taken over from previous waypoints by default, except the for GPS coordinates.
- Changes for a waypoint must be submitted by clicking on the "update waypoint" button.
- The data can be send to the server by using the "send waypoints to server" button.
- Only latest missions are stored. They can be loaded when no new mission is planned by clicking on "send waypoints to server".

<div align="center">
	<video src="https://github.com/JKU-ICG/AOS/assets/83944465/dd64a1d8-44ad-423e-b650-0843ac04bb39" width="400" />
</div>
		
## License
* Data: Creative Commons Attribution 4.0 International
* Software Modules: You are free to modify and use our software non-commercially; Commercial usage is restricted (see the [LICENSE.txt](LICENSE.txt))
