### AOS Map Visualization
A map visualization module (contributed by Patrick Sack) can be connected to the server for real-time mapping of swarms (drones' positions, heading, full telemetry, and live video data). A digital zoom extends the limited zoom capabilities of conventional map services. It runs in your default webbrowser. 

- The map is used in the same way as any other online map (scrolling, zooming, switching to satellite view, etc).
  
  ![main screen](https://github.com/user-attachments/assets/9ad00894-6947-4863-85f3-e7b958b81e1a)
  
- Clicking on the drone icons with **ctrl** button (which visualizes position and heading) turns on/off the live video/telemetry window.
  
  ![icon](https://github.com/user-attachments/assets/07bf3f80-0984-43ea-9b8d-259e9d1011b4)

- Clicking **space** button will centre the map based on drone positions.
  
  ![icon with image](https://github.com/user-attachments/assets/739cf259-43ed-40e4-b1ac-f4657f26891d)

- New groups are added to AOS Map Visualization.

  ![groups](https://github.com/user-attachments/assets/6d306988-8a78-45a6-b756-204c361fdf9f)

> - AOS group; which changes the Integral and/or Anomaly image parameters by changing the sliders (Focal Length, Compass Correction, RX Threshold, Focal Plane Pitch and Focal Plane Roll).  You can slide each slider to the desired parameter settings.

![AOS](https://github.com/user-attachments/assets/c5199c63-08eb-4f41-b14f-52f22f92652b)

> - Drone group; you can change the view of the drone by sliding the sliders (Heading, Gimbal Pitch and Gimbal Yaw) without defining a new waypoint mission. You only need to click (or ctrl + click) the drone you want to change its view and slide the sliders.

![drone](https://github.com/user-attachments/assets/0d4a5ab3-d51c-44ff-82e6-02ac22fef8b0)

> - Image Group, Image Size slider is added. It can be changed for the selected drone. 

![Image](https://github.com/user-attachments/assets/86ad1714-3415-4cef-ae03-f5995c2a4a98)

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
