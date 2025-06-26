# AOS waypoint planning

AOS waypoint planning is part of the AOS ground stations. It is used for designing the mission ant its waypoints, checking manually and autonomously collisions between multiple drones. 

## Prerequisites

1. **Node.js**  
   - Download the latest LTS release (v14.x or newer) from [https://nodejs.org](https://nodejs.org) and install it.  
   - Verify installation in a terminal/command prompt:
     ```bash
     node --version
     npm --version
     ```

---

## Folder Structure

Make sure your local copy of the project follows this tree end of this section:

```
/AOS Groundstation
│
├─ /AOS waypoint planning
│   ├─ launcher.js
│   ├─ package.json          ← (we’ll create this below)
│   └─ /public
│       ├─ index.html
|       ├─ script.js
|       ├─ style.css
|       ├─ leaflet.rotatedMarker.min.js
|       ├─ bootstrap.bundle.min.js
│       └─ /images
│           └─ (image files)
│
├─/AOS server
│    ├─ AOS_Broker.exe   
│    └─ ...
│
├─ /AOS_Groundstation.bat
│
└─ ...
```

- **launcher.mjs**  
  Contains your Express server code that serves static files and spawns the EXE.  
- **public/**  
  Contains `index.html` plus other CSS, JS, or image assets for the AOS waypoint planning module.  
- **AOS Server**  
  Contains `AOS_Broker.exe` and other server related files and folders, which will be launched by `launcher.mjs`.

---

## Setup Instructions

### 1. Install Node.js (if needed)

If Node.js is not already installed:

1. Go to [https://nodejs.org](https://nodejs.org) and download the latest LTS installer.  
2. Follow the installer prompts.  
3. Confirm installation:
   ```bash
   node --version   # e.g. v18.16.0
   npm --version    # e.g. 9.5.0
   ```

---

### 2. Initialize

1. Open a terminal (Command Prompt or PowerShell on Windows) and change into the folder containing `launcher.mjs` file, public and API folders:
   ```bash
   cd "<FILE DIRECTORY>\AOS Groundstation\AOS waypoint planning"
   ```
2. Run:
   ```bash
   npm init -y
   ```
   - This creates a `package.json`.  
3. Open `package.json` in a text editor and add make sure `"main": "launcher.mjs"` is there, Example:
   ```jsonc
    {
      "name": "aos-waypoint-planning",
      "version": "1.0.0",
      "description": "",
      "main": "launcher.mjs",
      "keywords": [],
      "author": "",
      "license": "ISC",
      "dependencies": {
        "express": ""
      }
    }

   ```

> **Why?**  
> By setting `"type": "module"`, Node will treat every `.mjs` file in this folder as an ES module. Without it, `import … from 'express'` would fail.

---

### 3. Install Dependencies

Stay in the same directory (`AOS waypoint planning`) in the terminal and run:

```bash
npm install express
```

- This will add `"express": "^x.x.x"` under `"dependencies"` in `package.json`.  
- It will also create `node_modules/` folder and `package-lock.json` file.

---

### 4. Verify Folder Structure & Static Assets

After installing, your folder tree in `AOS waypoint` should look like:

```
/AOS waypoint planning
 ├─ API
 ├─ launcher.mjs
 ├─ package.json
 ├─ package-lock.json
 ├─ /node_modules
 └─ /public
     ├─ index.html
     ├─ script.js
     ├─ style.css
     ├─ leaflet.rotatedMarker.min.js
     ├─ bootstrap.bundle.min.js
     └─ /images
         └─ (image files)
```
#### Note: The rest is done automatically by bat file (**.../AOS Groundstation/AOS_Groundstation.bat**). If you want to try out separately, you can follow the following instructions. 

### 7. Start the Node Server

From the terminal in `AOS waypoint planning`, run:

```bash
npm start
```

This executes the `start` script defined in `package.json` (which is `node launcher.mjs`). You should see:

```
Launcher listening at http://localhost:3000
```

---

### 8. Verify Static Site Serving

1. Open a browser and navigate to:
   ```
   http://localhost:3000/
   ```
2. You should see the waypoint planning module on your browser.

---

# How to Use AOS waypoint planning

## Running the Waypoint Planner  
From the **AOS Groundstation** folder, right-click **AOS_Groundstation.bat** and choose **Run as administrator**. This will automatically launch the waypoint-planning interface in your default web browser—just like the other ground-station components.

![bat_file](https://github.com/user-attachments/assets/b6912dc1-90f9-4798-91d1-811b66a165d6)

## Waypoint Planning Interface  
The waypoint-planning screen is shown in the image below:

![AOS waypoint planning](https://github.com/user-attachments/assets/b2e9b499-b48d-4479-be71-0567fdf9544f)

## Map Controls  
The map pane offers the following controls:

- **Zoom**: Click the “+”/“–” buttons or use your mouse wheel.  
- **Pan**: Left-click and drag to move the map.  
- **Layer Selection**: Choose your preferred map layer from the dropdown.

> **Tip:** Before planning your mission, pan and zoom to the area where you intend to fly.  

![AOS waypoint planning_map](https://github.com/user-attachments/assets/1015fb36-e904-403c-83ec-adebf51bb0fd)

## Main Panel Controls

The right panel of the waypoint-planning interface contains the primary controls of the AOS waypoint planning tool:

- **Start Broker**  
  Start the broker service (`AOS_Broker.exe`).

- **Plan Mission** _(expandable)_  
  Define your mission’s waypoints and parameters.

- **Collisions** _(expandable)_  
  Run a pre-flight collision analysis.

- **Save Images?**  
  Toggle saving images at each waypoint.

- **Send Mission**  
  Transmit the mission.

- **Takeoff**  
  Command the drones to take off.

- **Landing**  
  Command the drones to land.

> **Note:** Click the arrow icon next to **Plan Mission** or **Collision Check** to expand or collapse those sections.

![AOS waypoint planning right side](https://github.com/user-attachments/assets/116ee5d7-eba5-42d9-80a6-f3f6de375cd2)

### 1. Start Broker

Click **Start Broker** to launch the broker service (`AOS_Broker.exe`).  

> **Prerequisite:** Before you click this button, make sure your drone(s) are connected and streaming both telemetry data and video. If they aren’t, close the applications, resolve the connection issue, and then try again.

Once you’ve clicked **Start Broker**, a terminal window will open and display status messages indicating that the broker has started.

![AOS waypoint planning start broker](https://github.com/user-attachments/assets/49239b57-7836-4102-ac20-b9722ab0758d)

### 2. Plan Mission _(expandable)_

1. **Select Drone ID**  
   Choose the drone you want to plan for from the dropdown menu.

2. **Add Waypoints**  
   Click on the map to place your first waypoint. Each subsequent click adds another waypoint.

3. **Configure Waypoint Parameters**  
   For each waypoint you can set:  
   - **Latitude** & **Longitude** (auto-filled from where you clicked)  
   - **Altitude** (defaults to the mission’s default altitude)  
   - **Speed** (defaults to the mission’s default speed)  
   - **Holding Time** (defaults to the mission’s default holding time)

   – If you don’t change these values, the default settings apply to every new waypoint. 

> **Tip:** To streamline planning, adjust your mission’s default altitude, speed, and holding time before placing waypoints.

![waypoint_data](https://github.com/user-attachments/assets/f7492746-9af0-4736-93ed-8febed422117)

> **Note:** To update an existing waypoint, click it on the map. Its parameters will then populate at the top of the **Plan Mission** section, where you can adjust all waypoint parameters.

![AOS waypoint planning right side plan mission](https://github.com/user-attachments/assets/f76b2cff-fcdb-41a6-83bb-d76a444d4ef6)


#### Select Camera

- **Camera Dropdown**  
  Choose the camera you want to use. Available options depend on your drone model (Wide Angle, Tele, Thermal).  
  > **Note:** You must select a camera before proceeding.

  > **Tip:** To streamline planning, chose your preferred camera ,which is depend on your drone, before placing waypoints.

#### Integration & Anomaly

- **Integration** & **Anomaly** buttons  
  These are disabled by default. Activate them only if your mission requires integration or anomaly detection.

#### Gimbal & Heading Settings

- **Gimbal Pitch**, **Gimbal Yaw**, **Heading**  
  - Defaults to **0°**.  
  - When the drone reaches a waypoint, these values are sent to the drone and applied.  
  - You can verify the applied settings via your RC telemetry using AOS Server.

#### Integration Mode Parameters

- **Integration Window** & **Sampling Distance**  
  - Configure these only when **Integration** mode is enabled.  
  - Otherwise, these fields are ignored.
  
![waypoint_camera](https://github.com/user-attachments/assets/90019574-9395-4f35-8ec2-769d45ea553e)

When you want to fly a grid pattern, use the following controls. Note that all waypoints generated will inherit the current parameters but can be updated individually at any time as explained before.

1. **Set Spacings**  
   - **Spacing X** & **Spacing Y** define the grid cell dimensions. Defaults to **3 m × 3 m**.  
   - To fly a straight line, set one spacing to **0 m**.

2. **Draw Grid Manually**  
   Click **Draw Grid Manually**. Your cursor becomes a **+** then click and drag to sketch your grid on the map, creating all waypoints automatically.

3. **Draw Grid Automatically**  
   - Enter **Center Latitude** & **Center Longitude** for the grid’s center.  
   - Enter **Grid Width** & **Grid Height**.   
   - Click **Draw Grid Automatically** to generate the grid.

4. **Rotate Angle** (degrees)
   - Rotate the grid. 

> **Tip:** After drawing, review and adjust individual waypoint settings under **Plan Mission** if needed.   
   
![grid_planning](https://github.com/user-attachments/assets/5a1ebcd5-c9a8-40c7-bec2-7c2d51185576)
   
#### Editing Multiple Grids

When managing more than one grid (e.g., for multiple drones):

- **Select Grid**  
  Click a waypoint from the grid you want to edit. The grid’s controls will appear below, including a **Hide Grid** button.

- **Toggle Visibility**  
  Use **Hide Grid** to show or hide the grid rectangle beneath the waypoints.

- **Resize Grid**  
  With the grid rectangle visible, drag any of its corner handles to adjust the grid’s dimensions.

- **Move Grid**  
  Hold **Alt** + left-click anywhere on the grid rectangle, then drag to reposition it.

> **Tip:** The grid must be visible to resize or move it.    

![example grids](https://github.com/user-attachments/assets/b04e24dc-6ee3-4ffa-b210-47b1cebd204e)

#### Waypoint Threshold
  The waypoint thresholds defines how precise drones reach the waypoint. It sets initially at 2 meters but you can change it.  GPS drift, wind, and other environmental factors can prevent exact waypoint hits. Raising the threshold helps ensure the mission continues even if the drone isn’t perfectly on target.

#### Waypoint Removal Controls

- **Remove All Except Last WP**  
  Removes all waypoints except the final one.

- **Remove Selected WP**  
  Removes only the currently selected waypoint.

- **Remove All Waypoints of Selected Drone**  
  Clears all waypoints for the drone you’ve selected.

- **Remove All WPs**  
  Deletes every waypoint from the map.

> **Tip:** When planning a mission, an arrow icon shows your drone’s current position. If it overlaps a waypoint, you won’t be able to click that waypoint. Use the **Time Line** slider in the **Collisions** section to advance the drone’s position which moves the arrow and lets you select the waypoint. (The Time Line slider is explained later.)

For a step-by-step demonstration, watch the video below:

https://github.com/user-attachments/assets/c7fd8e98-1420-40a5-a2e8-19a1dec2539b

### 3. Collision Check _(expandable)_

Use this section to detect potential collisions between multiple waypoint missions. You can run a check manually or automatically:

#### Manual Check
- Slide the **Time Line** slider to advance each drone’s position along its mission.  
- As you move the slider, the drone arrows animate on the map, letting you visually inspect any overlaps or near-misses.

#### Autonomous Check
1. Set the **Collision Threshold**.  
2. Click **Detect Collisions**.  
3. The tool will compute any collision points based on each waypoint’s location, speed, and holding time, and highlight them on the map. 

Note that this is not live collision checker, it checks if there ara any collisions based on the parameters. GPS drift, wind, acceleration and other environmental factors may cause the collisions even if it is not detected using our check.

![collisions](https://github.com/user-attachments/assets/ccaeec35-8ab2-4b3d-999f-5cd10233471b)

#### Hide Segments

Click **Hide Segments** to hide the lines connecting the waypoints on the map.

### 4. Save Images?

Select **Yes** to save an image at each waypoint, or **No** to disable image capture.

### 5. Send Mission

Click **Send Mission** to transmit your planned waypoint mission to the broker. Every time you send the mission, it will saved in a JSON file. If you want to bring it back you need to press send mission without defining one. You make updates on the the mission waypoints as described above. Note that if you have designed a grid mission, it will lose grid properties (resizing, moving, etc) after sending it. This is working progress.  

> **Note:**  
> - The first time you send a waypoint mission, you must click **Takeoff** to launch the drones. Do not forget to apply the **How to use it** section of the main [README](https://github.com/JKU-ICG/AOS/blob/stable_release/AOS%20Groundstation/README.md).   
> - After the initial takeoff, any subsequent mission uploads will be applied automatically when it is clicked **Send Mission** button without additional manual steps.  

### 6. Takeoff

Click **Takeoff** to launch the drone. It will ascend vertically to the altitude of the first waypoint.

> **Note:** 
> - Ensure the motors are started and took off a couple of meters manually. Unfortunately, it is not allowed to take off on the ground by safety reasons.
> - After manual takeoff you need to enable **Virtual Stick**. It will be printed **Drone <ID> switched to auto flight mode.**

### 7. Landing

Click **Landing** to return the drone autonomously to 2 m above the original takeoff point.

> **Note:** For the final descent, 
> - Disable the **Virtual Stick**. 
> - Then, manually guide the drone down to the ground. 
> - Be careful when drones start landing. GPS drift, wind, acceleration and other environmental factors may change the calculation of the 2 meters above the ground. In the worst case scenario, disable the virtual stick, which will set the drone to manual mode, to take the controls. 
