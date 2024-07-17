# AOS Groundstation

For our swarm implementation, we present [a complete hard- and software framework](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20for%20Drone%20Swarms) that supports low-latency transmission (approx. 80 ms round-trip-time) of extensive (70-120 Mbits/s) video and telemetry data, and swarm control for swarms of up to ten drones. Our AOS groundstation (software architecture) allows to operate singe or multilple DJI drones from a PC. The drones must be DJI SDK5 compatible. We tested DJI Mavic 3T and DJI Mavic 30T. Our software architecture consists of the following modules:

- **[AOS for DJI App](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20for%20DJI)**: Our DJI app to be installed on the remote controller.
- **[AOS Server](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20for%20Drone%20Swarms)**: Server for video, telemetry, and waypoint streaming to be installed on a Windows PC.
- **[AOS Map Visualization](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20for%20Drone%20Swarms)**: Visualization module for real-time drone mapping in a webbrowser.
- **[AOS Waypoint Planning](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20for%20Drone%20Swarms)**: Module for waypoint mission planning in a webbrowser.

## Download
Coming soon...

## Installation
Coming soon...

## How to use it
Coming soon...

### AOS for DJI app

### AOS Server

### AOS Map Visualization

### AOS Waypoint Planning
- Add waypoints to the map by left click in the map.
- To move a waypoint to a new positions, you can drag and drop the marker by a left mouse click.
- Removing waypoints works by selecting a waypoint with a left mouse click on the marker and use the "remove waypoint" button. You can also remove a waypoint by a right clicking on the marker.
- Input parameters are taken over from previous waypoints by default, except the for GPS coordinates.
- Changes for a waypoint must be submitted by clicking on the "update waypoint" button.
- The data can be send to the server by using the "send waypoints to server" button.
- Only latest missions are stored. They can be loaded when no new mission is planned by clicking on "send waypoints to server".

## License
* Data: Creative Commons Attribution 4.0 International
* Software Modules: You are free to modify and use our software non-commercially; Commercial usage is restricted (see the [LICENSE.txt](LICENSE.txt))
