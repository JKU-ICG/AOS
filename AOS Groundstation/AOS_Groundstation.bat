@echo off

REM ── 1) Ensure Mosquitto is fresh ────────────────────────────────────
cd "C:\Program Files\mosquitto"
net stop mosquitto
net start mosquitto

REM    Run Mosquitto in this same window (backgrounded)
start /B "" mosquitto -c mosquitto.conf

REM ── 2) Back to repo root ────────────────────────────────────────────
cd /d %~dp0

REM ── 3) Start your Drone-Swarm server in same window ─────────────────
start /B "" "AOS server\DroneSwarmServer.exe"

REM ── 4) Start your Node.js launcher in same window ───────────────────
cd /d "%~dp0\AOS waypoint planning"
start /B "" "C:\Program Files\nodejs\node.exe" launcher.mjs

REM ── 5) Give Node time, then pop open your planner ───────────────────
timeout /t 2 /nobreak >nul
start "" "http://localhost:3000/index.html"

REM ── 6) Open your map‐visualization HTML in browser ──────────────────
start "" "%~dp0\AOS map visualization\AOS-Map.html"

REM ── 7) Exit the batch.  Because Mosquitto, DroneSwarmServer.exe and
REM     Node have all been backgrounded into this same console,
REM     the window will stay open until you manually close it.
exit /B
