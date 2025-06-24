### AOS Map Visualization
A map visualization module (contributed by Patrick Sack) can be connected to the server for real-time mapping of swarms (drones' positions, heading, full telemetry, and live video data). A digital zoom extends the limited zoom capabilities of conventional map services. It runs in your default webbrowser.  

- The map is used in the same way as any other online map (scrolling, zooming, switching to satellite view, etc).
- Clicking on the drone icons with **ctrl** button (which visualizes position and heading) turns on/off the live video/telemetry window.
- New groups are added to AOS Map Visualization. 
> - AOS group; which changes the Integral and/or Anomaly image parameters by changing the sliders (Focal Length, Compass Correction, RX Threshold, Focal Plane Pitch and Focal Plane Roll).  You can slide each slider to the desired parameter settings. 
> - Drone group; you can change the view of the drone by sliding the sliders (Heading, Gimbal Pitch and Gimbal Yaw) without defining a new waypoint mission. You only need to click (or ctrl + click) the drone you want to change its view and slide the sliders.
> - Image Group, Image Size slider is added. It can be changed for the selected drone. 

Before testing the AOS Map Visualization you need to install Mosquitto based on the steps blow.

# Install Mosquitto and Run .exe file
https://mosquitto.org/files/binary/win64/mosquitto-2.0.18-install-windows-x64.exe 

# Run Mosquitto Config   
This is our confic file that consist of our mqtt confiqurations. Which is similar to below.

- listener 9001
- protocol websockets
- listener 1883
- protocol mqtt
- persistence true
- allow_anonymous false
- password_file % location of the file
- persistence_file mosquitto.db
- persistence_location % location mosquitto folder 

**Note:** Do not forget the change the **% location of the file** and **% location mosquitto folder**. Otherwise, AOS_Broker can not transmit data and threw errors related to mqtt.

Run config file: 
> mosquitto -c mosquitto.conf 

Create a password.txt file in the mosquitto directory.
Open a terminal with administrator rights, navigate to the C:\Program Files\mosquitto directory, and execute the following command to create a user with a password:

> .\mosquitto_passwd -b "C:\Program Files\mosquitto\password.txt" user user

# Go to mosquitto installation folder 
Open a terminal with administrator rights, navigate to the C:\Program Files\mosquitto directory.

To start mosquitto: 
> net start mosquitto  

To stop mosquitto: 
> net stop mosquitto  

# Listen  

In order to test your mqtt run below in terminal.
 
> mosquitto_sub -h localhost -t drone -u user –P user 

### Note: After initial test, you do not need to do start and stop every time you want to use AOS map visualization. It will be done automatically by running AOS_Groundstation.bat file. 
