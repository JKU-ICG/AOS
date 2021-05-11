#import RPi.GPIO as GPIO
import time
import ctypes as ct
import shutil
import os
import glob
import numpy as np
import math
import logging
import pyaos
import json
import cv2
import utm
import matplotlib.pyplot as plt
from PIL import Image
detection = False
if detection :
    import naos_det
    import importlib
    importlib.reload(naos_det) # this makes sure that changes in naos_det.py have an effect
import datetime
import multiprocessing
from ..PLAN.Planner import Planner
from ..DRONE.FlyingControl import DroneFlyingControl
from ..DRONE.DroneCom import DroneCommunication, ReadGPSReceivedLogFiles, ReadNewGPSReceivedLogFiles
from ..DRONE.Renderer_Detector import Renderer
from ..CAM.CameraControl import CameraControl
from ..LFR.python.LFR_utils import hdr_mean_adjust
from ..PLAN.PathVisualizer import Visualizer
from scipy.stats import circmean
import random
from scipy import interpolate
from statistics import mean 


#New Changes to send Email
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class InitializationClass():
    _sitename = None
    _DroneFlyingSpeed = 1 # in 0.1m/s
    _FasterDroneFlyingSpeed = 3 # in 0.1m/s
    _WayPointHoldingTime = 5
    _PiWayPointRadiusCheck = 5.0
    _TimeDelayForFlirConnection = 7.0
    _ImageSamplingDistance = 1.0
    _LowerThreshold = 0.05
    _UpperThreshold = 0.10
    _Flying_Height = 35
    _MaxFlightTime = 20*60
    _area_sides = None
    _ReadfromFile = False
    _Render = True
    _Detect = True
    _PrePlannedPath = False
    _legacy_normalization = False
    _AlwaysRenderSeparetly = True
    _SimulateonCPU = False
    _GridAlignedPathPlanning = True
    _WritePoses = False
    _DetectWithPiImages = False
    _SendEmail = False
    _ProjectIndividualImages = False
    _GrabVideoFrames = True
    _ContinuousIntegration = True
    _ContinuousIntegrationAfterNoofImages = 10
    _GridSideLength = 30
    _RotationAngle = 0
    _NormalizedDistance = 30
    _pwmPin = 18
    _dc = 10
    _FieldofView = 43.10803984095769#43.50668199945787 #50.815436217896945
    _device = "MYRIAD" # "CPU" or "MYRIAD"(compute stick)
    _threshold = 0.05
    _aug = "noAHE"
    _yoloversion = "yolov4-tiny"
    _source = '/data/camera/*/*.tiff'
    _basedatapath = '../data'
    _DroneAttached = False
    _FlirAttached = False
    _IntelStickAttached = True
    _StartLatitudeGlobal = 0.0
    _StartLongitudeGlobal = 0.0
    _PiImagesFolder = None
    _Download_Dest = None
    _WritePosesPath = None
    _SavProjPath = None
    _ObjModelPath = None
    _ObjModelImagePath = None
    _LFRPath = None
    _DemInfoJSOn = None
    _DemInfoDict = None
    _CenterUTMInfo = None
    _CenterEast = None   
    _CenterNorth = None
    _prob_map = None
    _utm_center = None

    def  __init__(self, sitename, area_sides, ReadfromFile = False, DroneAttached = True, FlirAttached = True, IntelStickAttached = True, DroneFlyingSpeed = 10, Flying_Height = 35, 
                ImageSamplingDistance = 1.0, MaxFlightTime = 20*60, FieldofView = 43.10803984095769,GridSideLength = 30, GrabVideoFrames = True, StartLatitudeGlobal = 0.0, dc = 10,
                StartLongitudeGlobal = 0.0 , FasterDroneFlyingSpeed = 50, WayPointHoldingTime = 5, PiWayPointRadiusCheck = 5.0, TimeDelayForFlirConnection = 7.0, pwmPin = 18,
                LowerThreshold = 0.05, UpperThreshold = 0.10, Render = True, Detect = True, PrePlannedPath = False, legacy_normalization = False, _NormalizedDistance = 30,
                AlwaysRenderSeparetly = True, SimulateonCPU = False, GridAlignedPathPlanning = True, ContinuousIntegration = True, ContinuousIntegrationAfterNoofImages = 10,
                DetectWithPiImages = False, SendEmail = False, ProjectIndividualImages = False, WritePoses = False, aug = "noAHE", yoloversion = "yolov4-tiny",prob_map = None
    ):
        self._sitename = sitename
        self._DroneFlyingSpeed = DroneFlyingSpeed # in 0.1m/s
        self._FasterDroneFlyingSpeed = FasterDroneFlyingSpeed # in 0.1m/s
        self._WayPointHoldingTime = WayPointHoldingTime
        self._PiWayPointRadiusCheck = PiWayPointRadiusCheck
        self._TimeDelayForFlirConnection = TimeDelayForFlirConnection
        self._ImageSamplingDistance = ImageSamplingDistance
        self._LowerThreshold = LowerThreshold
        self._UpperThreshold = UpperThreshold
        self._Flying_Height = Flying_Height
        self._MaxFlightTime = MaxFlightTime
        
        self._ReadfromFile = ReadfromFile
        self._Render = Render
        self._Detect = Detect
        self._PrePlannedPath = PrePlannedPath
        self._legacy_normalization = legacy_normalization
        self._AlwaysRenderSeparetly = AlwaysRenderSeparetly
        self._SimulateonCPU = SimulateonCPU
        
        self._WritePoses = WritePoses
        self._DetectWithPiImages = DetectWithPiImages
        self._SendEmail = SendEmail
        self._ProjectIndividualImages = ProjectIndividualImages
        self._GrabVideoFrames = GrabVideoFrames
        self._ContinuousIntegration = ContinuousIntegration
        self._ContinuousIntegrationAfterNoofImages = ContinuousIntegrationAfterNoofImages

        self._area_sides = area_sides
        self._GridAlignedPathPlanning = GridAlignedPathPlanning
        self._GridSideLength = GridSideLength
        self._prob_map = prob_map
        
        self._RotationAngle = 0
        self._NormalizedDistance = 30
        self._pwmPin = pwmPin
        self._dc = dc
        self._FieldofView = FieldofView #50.815436217896945
        self._DroneAttached = DroneAttached
        self._FlirAttached = FlirAttached
        self._IntelStickAttached = IntelStickAttached
        self._device = "MYRIAD" if IntelStickAttached else "CPU" # "CPU" or "MYRIAD"(compute stick)
        self._threshold = 0.05
        self._aug = aug
        self._yoloversion = yoloversion
        self._source = '/data/camera/*/*.tiff'
        if self._SimulateonCPU :
            self._basedatapath = 'D:\\Resilio\\ANAOS\\SIMULATIONS'
        else :
            self._basedatapath = '../data'#'../data' 
        self._StartLatitudeGlobal = StartLatitudeGlobal
        self._StartLongitudeGlobal = StartLongitudeGlobal
        if self._DetectWithPiImages :
            self._PiImagesFolder = os.path.join(self._basedatapath,'FlightResults', sitename, 'PiRenderedResults')
        self._Download_Dest = os.path.join(self._basedatapath,'FlightResults', sitename, 'Image')
        self._WritePosesPath = os.path.join(self._basedatapath,'FlightResults', sitename, 'FlightPoses')
        self._SavProjPath = os.path.join(self._basedatapath,'FlightResults', sitename, 'Projections')
        self._ObjModelPath = os.path.join(self._basedatapath,'FlightResults', sitename, 'LFR','dem.obj')
        self._ObjModelImagePath = os.path.join(self._basedatapath,'FlightResults', sitename, 'LFR','dem.png')
        self._LFRPath = os.path.join(self._basedatapath,'FlightResults', sitename, 'LFR')
        self._DemInfoJSOn = os.path.join(self._basedatapath,'FlightResults', sitename, 'LFR','dem_info.json')
        with open(self._DemInfoJSOn) as json_file:
            self._DemInfoDict = json.load(json_file)
        self._CenterUTMInfo = self._DemInfoDict['centerUTM']
        self._CenterEast = self._CenterUTMInfo[0]   
        self._CenterNorth = self._CenterUTMInfo[1]
        if not self._PrePlannedPath :
            self._utm_center = (self._CenterUTMInfo[0], self._CenterUTMInfo[1], self._CenterUTMInfo[2], self._CenterUTMInfo[3])
##############################################################################
##############################################################################
if __name__ == "__main__":
    InitializedValuesClass = InitializationClass(sitename="Test20200326_Conifer_Fs6Re3_motion",area_sides = (90,90), ReadfromFile=False, DroneAttached=True,FlirAttached=True,
    DroneFlyingSpeed=6,Flying_Height = 35, GridSideLength = 90, SimulateonCPU=False)
    
    #vis = Visualizer( InitializedValuesClass._LFRPath )
    #PlanningAlgoClass = Planner( InitializedValuesClass._utm_center, InitializedValuesClass._area_sides, tile_distance = InitializedValuesClass._GridSideLength,  prob_map=InitializedValuesClass._prob_map, debug=False,vis=None, results_folder=os.path.join(InitializedValuesClass._basedatapath,'FlightResults', InitializedValuesClass._sitename, 'Log'),gridalignedplanpath = InitializedValuesClass._GridAlignedPathPlanning)
    
    CurrentGPSInfoQueue   = multiprocessing.Queue(maxsize=200)  # 
    SendWayPointInfoQueue = multiprocessing.Queue(maxsize=20)   # waypoint information queue.get() returns a dictionary as:
     #   {   
     #       'Latitude':  # x 10000000
     #       'Longitude': # x 10000000
     #       'Altitude': # x 10
     #       'Speed': # x 10
     #       'Index':
     #   }
    # CurrentGPSInfoQueueEventQueue = multiprocessing.Queue(maxsize=20)
    RenderingQueue = multiprocessing.Queue(maxsize=200) 
    FrameQueue = multiprocessing.Queue(maxsize=200)             # dictionary of the form { 'Frames': [img1, img2, ...] 'FrameTimes': [time1, time2, ...] }
    
    # events are only binary
    DroneProcessEvent = multiprocessing.Event()     # enabling this event (.set) stops the DroneCommunication process terminally (only do once)
    FlyingProcessEvent = multiprocessing.Event()    # if enabled (signaled from the DroneFlyingControl) the last waypoint has been reached
    RenderingProcessEvent = multiprocessing.Event() # enabling this event (.set) stops the Renderer process terminally (only do once)
    CameraProcessEvent = multiprocessing.Event()    # enabling this event (.set) stops the camera process terminally (only do once)
    GetFramesEvent = multiprocessing.Event()        # enable if you want to retrieve recorded frames

    if InitializedValuesClass._ReadfromFile:
        GPSReceivedLogFile = os.path.join(InitializedValuesClass._basedatapath,'FlightResults', InitializedValuesClass._sitename, 'GPSReceivedLog.log')
        #GPSlogFileInfo = ReadGPSReceivedLogFiles(GPSReceivedLogFile)
        GPSlogFileInfo = ReadNewGPSReceivedLogFiles(GPSReceivedLogFile)
    else :
        GPSlogFileInfo = []
    #print(len(GPSReceivedLogFile))

    CameraClass = CameraControl(FlirAttached=InitializedValuesClass._FlirAttached, AddsynthethicImage=False, out_folder = os.path.join(InitializedValuesClass._basedatapath,'FlightResults', InitializedValuesClass._sitename, 'Log'))
    
    # interpolation is done here. 
    DroneCommunicationClass = DroneCommunication(simulate=False,GPSLog=GPSlogFileInfo, interpolation=True,extrapolate=False, AddSynthethicImage=False,FlirAttached = InitializedValuesClass._FlirAttached,
                                                 out_folder=os.path.join(InitializedValuesClass._basedatapath,'FlightResults', InitializedValuesClass._sitename, 'Log'))
    # geotagged images are the output here (interpolation and adding GPS) -> input to FlyingControl
    # many more images than are actually used
    
    # check if waypoint reached, planning the next waypoints, send waypoint to DroneCom
    # selects frames which are one meter apart and send it to Renderer
    # Planner is in here
    FlyingControlClass = DroneFlyingControl(sitename = InitializedValuesClass._sitename,CenterEast = InitializedValuesClass._CenterEast,CenterNorth = InitializedValuesClass._CenterNorth,
                                            objectmodelpath=InitializedValuesClass._ObjModelPath,basedatapath=InitializedValuesClass._basedatapath,Render=True,
                                            FlirAttached = InitializedValuesClass._FlirAttached,Flying_Height = InitializedValuesClass._Flying_Height,
                                            DroneFlyingSpeed = InitializedValuesClass._DroneFlyingSpeed,RenderAfter = 3,CenterUTMInfo=InitializedValuesClass._CenterUTMInfo,
                                            out_folder=os.path.join(InitializedValuesClass._basedatapath,'FlightResults', InitializedValuesClass._sitename, 'SimulatedImages'),
                                            area_sides=InitializedValuesClass._area_sides,GridSideLength=InitializedValuesClass._GridSideLength,GridAlignedPathPlanning=InitializedValuesClass._GridAlignedPathPlanning,
                                            prob_map=InitializedValuesClass._prob_map,
                                            adddebugInfo=True)
    
    # Renderer does undistortion, LFR, DET
    RendererClass = Renderer(CenterUTMInfo=InitializedValuesClass._CenterUTMInfo,ObjModelPath=InitializedValuesClass._ObjModelPath,
                            Detect=True,ObjModelImagePath=InitializedValuesClass._ObjModelImagePath,basedatapath=InitializedValuesClass._basedatapath,
                            sitename=InitializedValuesClass._sitename,results_folder=os.path.join(InitializedValuesClass._basedatapath,'FlightResults',InitializedValuesClass._sitename, 'RenderedResults'),
                            FieldofView=InitializedValuesClass._FieldofView,adddebuginfo=True)

    
    processes = []
    RenderProcess = multiprocessing.Process(name='RenderingProcess', target=RendererClass.RendererandDetectContinuous, args=(RenderingQueue, RenderingProcessEvent))
    processes.append(RenderProcess)
    RenderProcess.start()
    time.sleep(2)

    DroneCommunicationProcess = multiprocessing.Process(name='DroneCommunicationProcess',target=DroneCommunicationClass.DroneInfo, args=(CurrentGPSInfoQueue,SendWayPointInfoQueue,CurrentGPSInfoQueueEventQueue, DroneProcessEvent, FrameQueue, GetFramesEvent))
    processes.append(DroneCommunicationProcess)
    DroneCommunicationProcess.start()

    FlyingControlProcess = multiprocessing.Process(name='FlyingControlProcess',target= FlyingControlClass.FlyingControl, args=(CurrentGPSInfoQueue,SendWayPointInfoQueue,CurrentGPSInfoQueueEventQueue, RenderingQueue,FlyingProcessEvent))
    processes.append(FlyingControlProcess)
    FlyingControlProcess.start()
    
    CameraFrameAcquireProcess = multiprocessing.Process(name='CameraFrameAcquireProcess', target=CameraClass.AcquireFrames, args=(FrameQueue, CameraProcessEvent, GetFramesEvent))
    processes.append(CameraFrameAcquireProcess)
    CameraFrameAcquireProcess.start()
    
    
    while not FlyingProcessEvent.is_set():
        time.sleep(10.0)
    DroneProcessEvent.set()
    CameraProcessEvent.set()
    RenderingProcessEvent.set()
    
    time.sleep(15.0)

    while not FrameQueue.empty():
        FramesInfo = FrameQueue.get()
    while not CurrentGPSInfoQueue.empty():
        FramesInfo = CurrentGPSInfoQueue.get()
    while not SendWayPointInfoQueue.empty():
        FramesInfo = SendWayPointInfoQueue.get()
    while not CurrentGPSInfoQueueEventQueue.empty():
        FramesInfo = CurrentGPSInfoQueueEventQueue.get()
    while not RenderingQueue.empty():
        FramesInfo = RenderingQueue.get()
    CurrentGPSInfoQueue.close()
    SendWayPointInfoQueue.close()
    CurrentGPSInfoQueueEventQueue.close()
    FrameQueue.close()
    RenderingQueue.close()

    print('All Thread Done')
    for process in processes:
        process.join(5)
    print('CameraFrameAcquireProcess.is_alive()', CameraFrameAcquireProcess.is_alive())
    print('DroneCommunicationProcess.is_alive()', DroneCommunicationProcess.is_alive())
    print('FlyingControlProcess.is_alive()', FlyingControlProcess.is_alive())
    print('RenderProcess.is_alive()', RenderProcess.is_alive())
    if CameraFrameAcquireProcess.is_alive() :
        CameraFrameAcquireProcess.terminate()
        CameraFrameAcquireProcess.join()
    print('CameraFrameAcquireProcess.is_alive()', CameraFrameAcquireProcess.is_alive())
    if DroneCommunicationProcess.is_alive() :
        DroneCommunicationProcess.terminate()
        DroneCommunicationProcess.join()
    print('DroneCommunicationProcess.is_alive()', DroneCommunicationProcess.is_alive())
    if FlyingControlProcess.is_alive() :
        FlyingControlProcess.terminate()
        FlyingControlProcess.join()
    print('FlyingControlProcess.is_alive()', FlyingControlProcess.is_alive())
    if RenderProcess.is_alive() :
        RenderProcess.terminate()
        RenderProcess.join()
    print('RenderProcess.is_alive()', RenderProcess.is_alive())
    print('All Process Done')
    #f.close()
    #CurrentDronedata.updateReceiveCommand(False)
    #for thread in enumerate(threads):       
    #    thread.join()
    
##############################################################################
##############################################################################
