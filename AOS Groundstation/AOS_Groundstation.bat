@echo off

REM Change directory to Mosquitto folder
cd "C:\Program Files\mosquitto"

REM Stop and start Mosquitto service
net stop mosquitto
net start mosquitto

REM Run Mosquitto with specific config
.\mosquitto -c mosquitto.conf

REM Change back to the original directory (assuming it's on the same drive)
cd /d %~dp0

REM Start the executable file
start "" "AOS server\DroneSwarmServer.exe"

REM Open two HTML files
start "" "AOS waypoint planning\index.html"
start "" "AOS map visualization\AOS-Map.html"

