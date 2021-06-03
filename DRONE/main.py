#import RPi.GPIO as GPIO
import time
import ctypes as ct
import shutil
import os
import glob
import numpy as np
import math
import logging
import json
import cv2
import utm
import matplotlib.pyplot as plt
from PIL import Image
import datetime
import multiprocessing

from pathlib import Path
import sys
detection = False

# to find the local modules we need to add the folders to sys.path
cur_file_path = Path(__file__).resolve().parent
sys.path.insert(1, cur_file_path )
sys.path.insert(1, os.path.join(cur_file_path, '..', 'PLAN') )
sys.path.insert(1, os.path.join(cur_file_path, '..', 'DET') )
sys.path.insert(1, os.path.join(cur_file_path, '..', 'LFR', 'python') )
sys.path.insert(1, os.path.join(cur_file_path, '..', 'CAM') )
import pyaos
detection = True
if detection :
    from detector import Detector
from Planner import Planner
from FlyingControl import DroneFlyingControl
#from ..DRONE.DroneCom import DroneCommunication, ReadGPSReceivedLogFiles, ReadNewGPSReceivedLogFiles
from Renderer_Detector import Renderer
from CameraControl import CameraControl

test_server = True
if test_server :
    from ServerUpload import ServerUpload

from DroneCom import DroneCommunication
from LFR_utils import hdr_mean_adjust
from PathVisualizer import Visualizer
from utils import download_file
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


import asyncio
import aiohttp



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
    _UpdatePathPlanning = False

    def  __init__(self, sitename, area_sides, ReadfromFile = False, DroneAttached = True, FlirAttached = True, IntelStickAttached = True, DroneFlyingSpeed = 10, Flying_Height = 35, 
                ImageSamplingDistance = 1.0, MaxFlightTime = 20*60, FieldofView = 43.10803984095769,GridSideLength = 30, GrabVideoFrames = True, StartLatitudeGlobal = 0.0, dc = 10,
                StartLongitudeGlobal = 0.0 , FasterDroneFlyingSpeed = 10, WayPointHoldingTime = 5, PiWayPointRadiusCheck = 5.0, TimeDelayForFlirConnection = 7.0, pwmPin = 18,
                LowerThreshold = 0.05, UpperThreshold = 0.10, Render = True, Detect = True, PrePlannedPath = False, legacy_normalization = False, _NormalizedDistance = 30,
                AlwaysRenderSeparetly = True, SimulateonCPU = False, GridAlignedPathPlanning = True, ContinuousIntegration = True, ContinuousIntegrationAfterNoofImages = 10,
                DetectWithPiImages = False, SendEmail = False, UpdatePathPlanningflag = False, sender_email = None, receiver_email = None, subject = None, body = None,
                ProjectIndividualImages = False, WritePoses = False, aug = "noAHE", yoloversion = "yolov4-tiny",currentpath = '../data',uploadserver = False, baseserver = 'http://localhost:8080',prob_map = None
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
        self._UpdatePathPlanning = UpdatePathPlanningflag
        self._PrePlannedPath = PrePlannedPath
        self._legacy_normalization = legacy_normalization
        self._AlwaysRenderSeparetly = AlwaysRenderSeparetly
        self._SimulateonCPU = SimulateonCPU
        
        self._WritePoses = WritePoses
        self._DetectWithPiImages = DetectWithPiImages
        self._SendEmail = SendEmail
        self._sender_email = sender_email
        self._receiver_email = receiver_email
        self._subject = subject
        self._body = body
        self._uploadserver = uploadserver
        self._serveraddress = baseserver

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
        self._basedatapath = currentpath
        #if self._SimulateonCPU :
        #    self._basedatapath = 'D:\\Resilio\\ANAOS\\SIMULATIONS'
        #else :
        #    self._basedatapath = '../data'#'../data' 
        self._StartLatitudeGlobal = StartLatitudeGlobal
        self._StartLongitudeGlobal = StartLongitudeGlobal
        if self._DetectWithPiImages :
            self._PiImagesFolder = os.path.join(self._basedatapath,'..','data', sitename, 'PiRenderedResults')
        self._Download_Dest = os.path.join(self._basedatapath,'..','data', sitename, 'Image')
        self._WritePosesPath = os.path.join(self._basedatapath,'..','data', sitename, 'FlightPoses')
        self._SavProjPath = os.path.join(self._basedatapath,'..','data', sitename, 'Projections')
        self._ObjModelPath = os.path.join(self._basedatapath,'..','data', sitename, 'DEM','dem.obj')
        self._ObjModelImagePath = os.path.join(self._basedatapath,'..','data', sitename, 'DEM','dem.png')
        self._LFRPath = os.path.join(self._basedatapath,'..','data', sitename, 'DEM')
        self._DemInfoJSOn = os.path.join(self._basedatapath,'..','data', sitename, 'DEM','dem_info.json')
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
    cur_file_path = Path(__file__).resolve().parent
    
    base_url1 = 'http://140.78.99.183:80'
    sitename = "test_flight_server_upload"

    #ToDo --- Download All Files and Place in a Folder Locally
    location_ref = 'test_flight_server_upload' #Find Way to Get locationref from the server
    #download_file(base_url1,"locations",local_file = os.path.join(cur_file_path,'..','data',sitename,'DEM','dem.obj'),remote_file= location_ref + ".obj")
    #download_file(base_url1,"locations",local_file = os.path.join(cur_file_path,'..','data',sitename,'DEM','dem.png'),remote_file= location_ref + ".png")
    #download_file(base_url1,"locations",local_file = os.path.join(cur_file_path,'..','data',sitename,'DEM','dem_info.json'),remote_file= location_ref + ".json")
    InitializedValuesClass = InitializationClass(sitename=sitename,area_sides = (90,90), ReadfromFile=False, DroneAttached=True,FlirAttached=True,
    DroneFlyingSpeed=4,Flying_Height = 30, GridSideLength = 90, UpdatePathPlanningflag = False, SimulateonCPU=False, currentpath = cur_file_path)
    
    #vis = Visualizer( InitializedValuesClass._LFRPath )
    #PlanningAlgoClass = Planner( InitializedValuesClass._utm_center, InitializedValuesClass._area_sides, tile_distance = InitializedValuesClass._GridSideLength,  prob_map=InitializedValuesClass._prob_map, debug=False,vis=None, results_folder=os.path.join(InitializedValuesClass._basedatapath,'FlightResults', InitializedValuesClass._sitename, 'Log'),gridalignedplanpath = InitializedValuesClass._GridAlignedPathPlanning)
    
    CurrentGPSInfoQueue   = multiprocessing.Queue(maxsize=200)  # queue which stores gps tagged frames.  
        #   reading with `CurrentGPSInfoQueue.get()`   returns a dictionary of the form 
        #   {   'Latitude' = # gps lat in degrees
        #       'Longitude' = # gps lon in degrees
        #       'Altitude' = # absolute altitude
        #       'BaroAltitude' = # relative altitude = (value / 100) 
        #       'TargetHoldTime' = # Counter set to fixed value and counts down to 0 once it reaches waypoint
        #       'CompassHeading' = # compass values in step of 2 degrees
        #       'Image' = #Acquired frame from framegrabber
        #   }
    SendWayPointInfoQueue = multiprocessing.Queue(maxsize=20)   # waypoint information queue.get() returns a dictionary as:
        #      {    'Latitude':  # value = int (gps lat x 10000000), 
        #           'Longitude': # value = int (gps lon x 10000000), 
        #           'Altitude': # value should be desired Altitude in m above starting height,
        #           'Speed': # value should be desired speed in m/s, 
        #           'Index':
        #       }
    RenderingQueue = multiprocessing.Queue(maxsize=200) # queue with geotagged frames with ~1m spacing
        #   in the form of a dictionary
        #    {   'Latitude' = # 
        #        'Longitude' = # 
        #        'Altitude' = #
        #        'CompassHeading' = #  
        #        'Image' = # 
        #        'StartingHeight' = #
        #        'Render' = # boolean indicating after adding which frame we should render
        #        'UpdatePlanningAlgo' = # boolean indicating after adding which frame we should send the detections
        #    }
    FrameQueue = multiprocessing.Queue(maxsize=200) # a queue element is a dictionary of the form 
        #   {   'Frames': [img1, img2, ...],  
        #       'FrameTimes': [time1, time2, ...] 
        #   }
    DetectionInfoQueue = multiprocessing.Queue(maxsize=200) # a queue element is a dictionary of the form 
        #   {   'PreviousVirtualCamPos': (gps_lat,gps_lon)),  
        #       'DLDetections': [{'gps':(gps_lat,gps_lon), 'conf': #}, {'gps':(gps_lat,gps_lon), 'conf': #}, ...]
        #       'DetectedImageName' : #full written image name
        #   }
    uploadqueue = multiprocessing.Queue(maxsize=200)
    
    # events are only binary
    DroneProcessEvent = multiprocessing.Event()     # enabling this event (.set) stops the DroneCommunication process terminally (only do once)
    FlyingProcessEvent = multiprocessing.Event()    # if enabled (signaled from the DroneFlyingControl) the last waypoint has been reached
    RenderingProcessEvent = multiprocessing.Event() # enabling this event (.set) stops the Renderer process terminally (only do once)
    CameraProcessEvent = multiprocessing.Event()    # enabling this event (.set) stops the camera process terminally (only do once)
    GetFramesEvent = multiprocessing.Event()        # enable if you want to retrieve recorded frames
    RecordEvent = multiprocessing.Event()           # enable if you want to record information while flying
    upload_complete_event = multiprocessing.Event()

    if InitializedValuesClass._ReadfromFile:
        GPSReceivedLogFile = os.path.join(InitializedValuesClass._basedatapath,'FlightResults', InitializedValuesClass._sitename, 'GPSReceivedLog.log')
        #GPSlogFileInfo = ReadGPSReceivedLogFiles(GPSReceivedLogFile)
        GPSlogFileInfo = ReadNewGPSReceivedLogFiles(GPSReceivedLogFile)
    else :
        GPSlogFileInfo = []
    #print(len(GPSReceivedLogFile))

    CameraClass = CameraControl(FlirAttached=InitializedValuesClass._FlirAttached, AddsynthethicImage=False, out_folder = os.path.join(InitializedValuesClass._basedatapath,'..','data', InitializedValuesClass._sitename, 'log'))
    
    # interpolation is done here. 
    DroneCommunicationClass = DroneCommunication(simulate=False,GPSLog=GPSlogFileInfo, interpolation=True,extrapolate=False, AddSynthethicImage=False,FlirAttached = InitializedValuesClass._FlirAttached,
                                                 out_folder=os.path.join(InitializedValuesClass._basedatapath,'..','data', InitializedValuesClass._sitename, 'log'))
    # geotagged images are the output here (interpolation and adding GPS) -> input to FlyingControl
    # many more images than are actually used
    
    # check if waypoint reached, planning the next waypoints, send waypoint to DroneCom
    # selects frames which are one meter apart and send it to Renderer
    # Planner is in here
    FlyingControlClass = DroneFlyingControl(sitename = InitializedValuesClass._sitename,CenterEast = InitializedValuesClass._CenterEast,CenterNorth = InitializedValuesClass._CenterNorth,
                                            objectmodelpath=InitializedValuesClass._ObjModelPath,basedatapath=InitializedValuesClass._basedatapath,Render=True,
                                            FlirAttached = InitializedValuesClass._FlirAttached,Flying_Height = InitializedValuesClass._Flying_Height,
                                            DroneFlyingSpeed = InitializedValuesClass._DroneFlyingSpeed,RenderAfter = 2,CenterUTMInfo=InitializedValuesClass._CenterUTMInfo,
                                            out_folder=os.path.join(InitializedValuesClass._basedatapath,'..','data', InitializedValuesClass._sitename, 'images'),
                                            area_sides=InitializedValuesClass._area_sides,GridSideLength=InitializedValuesClass._GridSideLength,GridAlignedPathPlanning=InitializedValuesClass._GridAlignedPathPlanning,
                                            prob_map=InitializedValuesClass._prob_map,UpdatePathPlanningflag = InitializedValuesClass._UpdatePathPlanning,
                                            adddebugInfo=True)
    
    # Renderer does undistortion, LFR, DET
    RendererClass = Renderer(CenterUTMInfo=InitializedValuesClass._CenterUTMInfo,ObjModelPath=InitializedValuesClass._ObjModelPath,
                            Detect=True,ObjModelImagePath=InitializedValuesClass._ObjModelImagePath,basedatapath=InitializedValuesClass._basedatapath,
                            sitename=InitializedValuesClass._sitename,results_folder=os.path.join(InitializedValuesClass._basedatapath,'..','data',InitializedValuesClass._sitename, 'results'),
                            FieldofView=InitializedValuesClass._FieldofView,device="MYRIAD",adddebuginfo=True,uploadserver=True,baseserver=base_url1,locationid=location_ref)

    serverclass = ServerUpload(serveraddress=base_url1,locationid= location_ref)
    
    
    processes = []
    uploadprocess = multiprocessing.Process(name = 'uploadprocess', target=serverclass.dummy_run, args=(uploadqueue, upload_complete_event))
    processes.append(uploadprocess)
    uploadprocess.start()
    
    RenderProcess = multiprocessing.Process(name='RenderingProcess', target=RendererClass.RendererandDetectContinuous, args=(RenderingQueue, DetectionInfoQueue, uploadqueue, RenderingProcessEvent))
    processes.append(RenderProcess)
    RenderProcess.start()
    time.sleep(2)

    DroneCommunicationProcess = multiprocessing.Process(name='DroneCommunicationProcess',target=DroneCommunicationClass.DroneInfo, args=(CurrentGPSInfoQueue,SendWayPointInfoQueue, DroneProcessEvent, FrameQueue, GetFramesEvent, RecordEvent))
    processes.append(DroneCommunicationProcess)
    DroneCommunicationProcess.start()

    FlyingControlProcess = multiprocessing.Process(name='FlyingControlProcess',target= FlyingControlClass.FlyingControl, args=(CurrentGPSInfoQueue,SendWayPointInfoQueue, RenderingQueue, DetectionInfoQueue, FlyingProcessEvent, RecordEvent))
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
    upload_complete_event.set()
    time.sleep(25.0)

    while not FrameQueue.empty():
        FramesInfo = FrameQueue.get()
    while not CurrentGPSInfoQueue.empty():
        FramesInfo = CurrentGPSInfoQueue.get()
    while not SendWayPointInfoQueue.empty():
        FramesInfo = SendWayPointInfoQueue.get()
    while not RenderingQueue.empty():
        FramesInfo = RenderingQueue.get()
    while not uploadqueue.empty():
        FramesInfo = uploadqueue.get()
    while not DetectionInfoQueue.empty():
        FramesInfo = DetectionInfoQueue.get()
    CurrentGPSInfoQueue.close()
    SendWayPointInfoQueue.close()
    FrameQueue.close()
    RenderingQueue.close()
    uploadqueue.close()
    DetectionInfoQueue.close()

    print('Wrapping Up all Process')
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
    if uploadprocess.is_alive() :
        uploadprocess.terminate()
        uploadprocess.join()
    print('uploadprocess.is_alive()', uploadprocess.is_alive())
    print('All Process Done')
    #f.close()
    #CurrentDronedata.updateReceiveCommand(False)
    #for thread in enumerate(threads):       
    #    thread.join()
    
##############################################################################
##############################################################################
