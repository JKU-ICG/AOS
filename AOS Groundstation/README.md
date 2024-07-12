# AOS Groundstation

For our swarm implementation, we present [a complete hard- and software framework](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20for%20Drone%20Swarms) that supports low-latency transmission (approx. 80 ms round-trip-time) of extensive (70-120 Mbits/s) video and telemetry data, and swarm control for swarms of up to ten drones. Our AOS groundstation (software architecture) allows to operate singe or multilple DJI drones from a PC. The drones must be DJI SDK5 compatible. We tested DJI Mavic 3T and DJI Mavic 30T. Our software architecture consists of the following components:

- **[AOS for DJI app](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20for%20DJI)**: Our DJI app to be installed on the remote controller.
- **[AOS server](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20for%20Drone%20Swarms)**: Server for video, telemetry, and waypoint streaming to be installed on a Windows PC.
- **[AOS map visualization](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20for%20Drone%20Swarms)**: Visualization module for real-time drone mapping in a webbrowser.
- **[AOS waypoint planning](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20for%20Drone%20Swarms)**: Waypoint mission planning module running in a webbrowser. 


