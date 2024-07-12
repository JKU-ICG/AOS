# AOS Groundstation

Our AOS groundstation allows to operate singe or multilple (up to 10) DJI drones from a PC. The drones must be DJI SDK5 compatible. We tested DJI Mavic 3T and DJI Mavic 30T. Our software architecture consists of the following components:

- **[AOS for DJI app](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20for%20DJI)**: Our DJI app to be installed on the remote controller.
- **[AOS server](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20for%20Drone%20Swarms)**: Server for video, telemetry, and waypoint streaming to be installed on a Windows PC.
- **[AOS map visualization](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20for%20Drone%20Swarms)**: Visualization module for real-time drone mapping in a webbrowser.
- **[AOS waypoint planning](https://github.com/JKU-ICG/AOS/tree/stable_release/AOS%20for%20Drone%20Swarms)**: Waypoint mission planning module running in a webbrowser. 



This Weave ([FWF](https://www.fwf.ac.at/en/) & [DFG](https://www.dfg.de/en/index.jsp)) funded basic research project is on exploring AOS for moving targets, in paricular using drone swarms. It started in April 2023, in collaboration with the [German Aerospace Center (DLR)](https://www.dlr.de/EN/Home/home_node.html) and the [Otto-von-Guericke University Magdeburg](https://www.ovgu.de/en/).

