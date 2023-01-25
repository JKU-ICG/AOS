## Airborne Optical Sectioning (AOS)

**[Airborne Optical Sectioning (AOS)](https://github.com/JKU-ICG/AOS/)** is a wide synthetic-aperture imaging technique that employs manned or unmanned aircraft, to sample images within large (synthetic aperture) areas from above occluded volumes, such as forests. Based on the poses of the aircraft during capturing, these images are computationally combined to integral images by light-field technology. These integral images suppress strong occlusion and reveal targets that remain hidden in single recordings.<br /> 

Single Images         |  Airborne Optical Sectioning
:-------------------------:|:-------------------------:
![single-images](../img/Nature_single-images.gif) | ![AOS](../img/Nature_aos.gif)

> Source: [Video on YouTube](https://www.youtube.com/watch?v=kyKVQYG-j7U) | [FLIR](https://www.flir.com/discover/cores-components/researchers-develop-search-and-rescue-technology-that-sees-through-forest-with-thermal-imaging/)

## AOS for DJI SDKV5

We have upgrated our DJI compatible AOS app ([see below](# AOS for DJI SDKV4)) to [DJI's Mobile SDK v5](https://developer.dji.com/). It supports DJI's enterprise platforms and was tested on the  [Mavic 3T Enterrpise](https://www.dji.com/de/mavic-3-enterprise). Our intention is to supports blue light organisations and others in testing and evaluating airborne optical sectioning for their use cases, and is free for non-commercial usage. For commercial usage of AOS, please refer to our [license conditions](https://github.com/JKU-ICG/AOS/blob/stable_release/LICENSE.txt). <br />

We make the new app and a description available here soon.

## AOS for DJI SDKV4

We have developed a DJI (SDKV4) compatible app that integrates AOS to support blue light organisations and others in testing and evaluating airborne optical sectioning for their use cases. The app is based on [DJI's Mobile SDK](https://developer.dji.com/) and is free for non-commercial usage. For commercial usage of AOS, please refer to our [license conditions](https://github.com/JKU-ICG/AOS/blob/stable_release/LICENSE.txt). <br />

![image7038](https://user-images.githubusercontent.com/48999492/172576924-2fc1bc37-08e1-43d7-ad53-b1cc4d05c3ac.png)

**Left:** Live Drone Images,
**Right:** AOS Integral Images,
**1:** Anomaly Detection Threshold (slider),
**2:** Anomaly Detection (on/off),
**3:** Take-Off / Landing,
**4:** Return to Home,
**5:** O = Settings,
**6:** Compass,
**7:** V = View (toggle: full screen / split screen / drone images / integral images),
**8:** I = Integral (toggle: integral image / spatially alligned single image),
**9:** AOS = AOS scan on/off,
**10:** RGB = Toggle: RGB/Thermal imaging,
**11:** - = Decrement value of the selected slider,
**12:** Focal Plane Pitch (slider),
**13:** Compass Correction (slider),
**14:** + = Increment value of the selected slider,
**15:** Focal Plane Distance (slider),
**16:** Focal Plane Roll (slider),
**17:** Product Connection Status,
**18:** Drone Battery Status ,
**19:** Wifi Signal Strength,
**20:** Video Signal Strength,
**21:** Remote Control Signal Strength,
**22:** Visual Positioning Status,
**23:** GPS Signal Strength,
**24:** Current Flight Mode,
**25:** Remaining Flight Time

The following documentation explains the AOS-specific features of the app. For general usage, flying operations, and initial drone setup and calibration, please refer to [DJI's Fly app](https://www.dji.com/de/dji-fly) and corresponding [tutorial](https://www.youtube.com/watch?v=TF-3CaJG52A).<br /><br />

[**Download v2_0 (Android 10 & 11) or V2_1 (Android < 10)**](https://forms.gle/DrfZiCthjp9g5eF87)<br /><br />

- **Principle Limitations**: AOS applied to RGB images is limited to the amount of sunlight that penetrates through the vegetation. **_If no or little light reaches the target, even occlusion removal will not make it visible. Thermal imaging has to be used instead to overcome this limitation._** The app also supports thermal imaging to use with DJI Enterprise systems. In general, visibility improvement through occlusion removal is limited by density. Best visibility improvements are achieved for 50% occlusion ([see publication](https://arxiv.org/abs/1906.06600)). Due to the sequential sampling, only static targests are supported ([see publication](https://arxiv.org/abs/2111.06959) for moving targets). 
- **Known Issues on our ToDo List**: Anomaly detection is relatively slow (on most phones not really suitable for interactive usage), and does show wrong detections at image borders (propper padding will be implemented to fix this). No digital elevation model is currently supported (ground surface is approximated with a plane). Imaging parameters needs to be manually/visually adjusted (automatic adjustment is not yet integrated). Imaging is limited to 10 frames per second (speed limit of the GPS sensor). The app has not been tested under all conditions and for all phone/drone hardware. It might crash. If this is the case, close and restart it (also possible during flight). <br />

**Copyright:** Institute of Computer Graphics, Johannes Kepler University Linz <br />
**Contact:** Univ.-Prof. Dr. Ing. habil. Oliver Bimber, Email: oliver.bimber@jku.at <br />
**[License](https://github.com/JKU-ICG/AOS/blob/stable_release/LICENSE.txt)**  <br />
**No warranty.**<br />

## Compatability

- **Tested DJI drones:** Mavic Mini, Mini 2, Mavic 2 Enterprise Advanced <br />
- **Compatible DJI drones (in therory, based on Android Mobile SDK 4.16 release notes):** Mavic Mini, Mini 2, Mavic 2 Series, Mavic 2 Enterprise Advanced, Mavic Air, Mavic Pro, Phantom series, Inspire series, Matrice 200 V2 series, Matrice 100, Matrice 600,... <br />
- **Tested mobile phones:** OnePlus 6 (Android 11), Xiaomi Pocophone F1 (Android 10), Samsung Galaxy S9 (Android 10), Samsung Galaxy J7 Max (Android 8.1), Samsung Galaxy S6 (Android 7.0) <br />
- **Tested smart controller:** M2EA -DJI Remote Smart Controller (Android 7.0) <br />
- **Compatible mobile phones:** Android 10 or 11 (**V2_0**) and Android < 10 (**V2_1**), the more RAM the better, the faster the better -<br />

## Installation

Restart the drone and the remote controller after the initial setup. Install the app (see link above) on your mobile device as shown in the video below. After the remote controller is paired with the drone, connect your mobile device to the remote controller and launch the application. 
 <br />
 
 
 






https://user-images.githubusercontent.com/48999492/172589911-ae3d1c03-822c-4b79-8c51-65b91fe92ed5.mp4
















## Pre-Flight Setup

The following parameters can be setup before flight, as shown in the video below:

By default, the **RGB** toggle button is in RGB state and the button **O**  in red providing access to the following settings :

- **Integration Window:** This is the number of single images being integrated for occlusion removal. The higher, the better - but also the slower.<br /><br />
- **Minimal Pose Distance:** This is the minimal distance at which images are integrated. For example, 1m means that images at 1m distance are integrated. With an integration window of, for example, 10 - this would cover a synthetic aperture of 10m (i.e., you need to fly 10m to capture all necessary images). <br /><br />
- **Anomaly Threshold:** This is the threshold for marking anomal pixels. It typically should be between 0.9 and 1.0. The lower, the more sensitive is the anomaly detector. A too low threshold might lead to false detections. A too high threshold might lead to missing the target. The color anomaly detection ([see publication]( https://arxiv.org/abs/2111.06959 )) marks pixles (in blue) that have typical colors as compared to the background. Anomaly detection is computaionally expensive, and might not be efficient on slow phones.  <br />

For thermal imaging, use the **RGB** toggle button to switch to thermal imaging mode (button changes state to **T**) and the button **O** changes to green. While in thermal imaging mode, the button **O** would provide access to the following settings:

- **Color:** This button would provide a list of false color tone-mapping opions (Rain, Red_hot, Green_hot, White_hot, Black_hot, Rainbow, Irainbow_1, Ice_fire, Color_1 and Color_2) for the thermal images.
- **Scene:** This button provides access to different scenes (Linear, Default, Sea_sky, Outdoor, Default, Manual Indoor ad Inspection) for thermal tone-mapping.
- Other settings such as DDE (Digital Data Enhancement Index), ACE (Active Contrast Enhancement), SSO (Smart Scene Optimization), Brightness & Contrast can be adjusted only when the scene mode is set to manual.








https://user-images.githubusercontent.com/48999492/172593660-4cf6623c-1e82-499b-b77c-ab65e95cce13.mp4










## On-Flight Usage

The first video below shows the app elements during flight. After start, press **No Warranty** to use the app at your own risk. This will provide you access to all the app elements and to the live video stream from the aircraft. The button **V** toggels between regular full-screen view of live drone images, full-screen view of AOS integral images, and a split-screen view (left: live aerial images of the drone, right: AOS integral images). Note, that the AOS integral image display is significantly slower than the live drone images, because many live images (as specified with the **Integration Window** parameter) are computationally combined. Flight operation is possible with the sticks in common fashion. _**Note, that the gimbal is always forced to point the camera downwards at 90 degrees (Nadir).**_ <br />
<br />



https://user-images.githubusercontent.com/48999492/172595339-54f47342-168a-44b8-8a77-4d370495d220.mp4




The second video below shows how to carry out an AOS scan. From hovering at the starting position, use the **AOS** button to switch AOS on (button becomes green). Fly to the end position to cover the synthetic aperture (see **Integration Window** and **Minimal Pose Distance** parameters to understand how wide the synthetic aperture is). During scanning, the AOS intergral image is being successively displayed. When reaching the end position, press the **AOS button** again to turn AOS off (button becomes red). For removing occlusion, you now need to set the correct imaging parameters (see Fig.1 in [publication](https://arxiv.org/pdf/2005.04065.pdf)): Use the sliders **FP** to move (up/down) the **focal plane** and **CC** to change (left/right) the **compass correction**. The sliders **Pi** and **Ro** are used to **adjust the focal plane pitch and roll** respectively. The buttons **+** and **-** can also be used to increase or decrease the slider value (select the slider of interest) respectively. For correct occlusion removal, the focal plane has to be aligned with the ground plane as good as possible, and the compass correction (which is necessary as the used compass modules are error prone) must be set correctly. All parameters should be manually tuned until target features can be recognized on the ground. Note again, that if no or little light reaches the target, even occlusion removal will not make it visible. Thermal imaging has to be used instead. The anomaly detector can be turned on / off using the **Rx** button to support visual search. With the **I** button you can toggle between integral image and single image (same perspective of the integral image) for spatial references. If anomaly detection is turned on, the marked anomalies are shown in both cases (blue pixles). All other elements and functions are similar as for the [DJI Fly app](https://www.youtube.com/watch?v=TF-3CaJG52A).
<br /><br />
_Note, that if you see only a static single image while you expect to see an integral image, then you are in single image mode and have to switch back to integral image mode with the **I** button._












https://user-images.githubusercontent.com/48999492/173185430-0e0f5788-e9d9-4ef8-8f86-9c925e35fbb4.mp4




<br /><br />

The third video below shows an example of AOS scan with thermal imaging. Switch to thermal imaging mode using the **RGB** toggle button (button changes state to **T**). The settings can be configured using the button **O** (refer section [pre-flight setup](#pre-flight-setup))

<br /><br />




https://user-images.githubusercontent.com/48999492/172496831-761e0875-2ec2-4e05-a2cb-12cd6388555f.mp4




## Hints from our Experience

- We recommend the following parameters: Set the **Integration Window** as large as the performance of your phone gives a you sufficently smooth display (e.g. 30 or higher). With a supported field of view of 53 degrees, the flying altitude roughly equals the ground coverage (e.g., it is approximately 30m coverage on the ground from 30m above ground level, AGL). Uniform sampling in integral images is achieved if the synthetic aperture size equals the ground coverage. Therefore chose **Minimal Pose Distance** to be fyling altitude (AGL) / **Integration Window** for best occlusion removal results.  <br />  <br />
- Turn on **Anomaly Detection** only after imaging parameters (focal plane and compass correction) are set properly (anomaly detection is in it's current implementation too slow for interative usage) - or use fast phones when computing it contineously.   <br />  <br />
- During scanning, **fly as low as possible** for optimal occlusion removal. Note, that the integral image covers only a 53 degree field of view. At an altitude of 30m AGL, this is roughly 30m on the ground, as explained above. <br />  <br />
- The compass module of low-cost drones is highly error-prone. That is the reason why we support a manual compass correction (see above). However, the compass offset (and consequently its correction) is not constant. It changes a lot, when changing the drones heading. We recommend to **not change the heading during scanning**. In this case, the compass correction is constant, and has to be adjutsed only once. But you will always get better results if you **fine-tune the compass correction (and the focal plane) after every scan**.<br />  <br /> 
- We currently support only focal planes (no digital elevation models). Thus, if your terrain is not flat, after alligning, the focal plane will only approximate the ground surfaces. Therefore, parts of the integral image (where the focal plane is off the ground surface) still appear blurred. You should **set the focal plane and compass parameters** in such a way that you achieve **best visibility for the (expected) target** on the ground. <br />  <br />  
- In thermal imaging mode, we recommend to set the contrast value to maximum with the color mode set to White_hot inorder to obtain the best results.<br />  <br /> 
- The **Anomaly Detection** will not work if the color mode is set to White_hot, Black_hot or Red_hot since the images will be in grayscale .
