# Install Mosquitto and Run .exe file
https://mosquitto.org/files/binary/win64/mosquitto-2.0.18-install-windows-x64.exe 


# Go to mosquitto installation folder 

To start mosquitto: 
> sudo net start mosquitto  

To stop mosquitto: 
> sudo net stop mosquitto  

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

Run config file: 
> sudo mosquitto -c mosquitto.conf 

# Listen  

In order to test your mqtt run below in terminal.
 
> mosquitto_sub -h localhost -t drone -u user –P user 

 