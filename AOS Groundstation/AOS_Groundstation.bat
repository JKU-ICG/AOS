@echo off

REM ── 1) Ensure Mosquitto is fresh ───────────────────────────────
cd "C:\Program Files\mosquitto"
net stop mosquitto
net start mosquitto
.\mosquitto -c mosquitto.conf

REM ── 2) Back to repo root (where this .bat lives) ──────────────
cd /d %~dp0

REM ── 3) Start your Drone‐Swarm server EXE ───────────────────────
start "" "AOS server\DroneSwarmServer.exe"

REM ── 4) Start your Node.js launcher ─────────────────────────────
REM ── Move into the launcher folder ───────────────────
cd /d "%~dp0\AOS waypoint planning"

REM ── Start Node (in its own window) ─────────────────
start "Node Launcher" cmd /k ^
    ""C:\Program Files\nodejs\node.exe" launcher.mjs"

REM ── Give Node time, then open your planner ────────
timeout /t 2 /nobreak >nul
start "" "http://localhost:3000/index.html"

REM ── 7) Open your map‐visualization HTML using the batch’s base folder ──
start "" "%~dp0\AOS map visualization\AOS-Map.html"