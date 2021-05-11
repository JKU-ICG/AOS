import time
import shutil
import os
import glob
import numpy as np
import math
import logging
import json
import cv2
import utm
import datetime
from scipy.stats import circmean

from PathVisualizer import Visualizer
from Planner_Indrajit import Planner
from Flight_utils import FindStartingHeight, haversine, ReadInterpolatedGPSlogFiles

from Drone_Communication_MultiProcess import DroneCommunication, ReadGPSReceivedLogFiles, ReadNewGPSReceivedLogFiles
from Renderer_Detector_MultiProcess import Renderer

import random
import multiprocessing
from multiprocessing import Process,Queue
from statistics import mean 


###################### Multiple Logging Files Setup ##########################
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logging.basicConfig(level=logging.DEBUG)

def setup_logger(name, log_file, level=logging.DEBUG):
    """To setup as many loggers as you want"""
    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger
##############################################################################

class DroneFlyingControl():
    _simulation = False
    _SimulationCount = 0
    # logging
    _log = None
    _gpsframelog = None
    _out_folder = None
    _sentwaypointlog = None
    _startlat = 0
    _startlon = 0
    _CenterEast = 0
    _CenterNorth = 0
    _objectmodelpath = None
    _maxflighttime = 20.0 * 60.0
    _FlirAttached = False
    _GridAlignedPathPlanning = True
    _PlanningAlgo = None
    _Flying_Height = 35
    _DroneFlyingSpeed = 10
    _ReadfromFile = False
    _WayPointHoldingTime = 5
    _PiWayPointRadiusCheck = 5.0
    _GrabVideoFrames = True
    _ImageSamplingDistance = 1.0
    _SimulatedData = []
    _Render = True
    _adddebugInfo = False
    _RenderAfter = 1
    _area_sides = None

    def  __init__(self, sitename, CenterEast, CenterNorth, objectmodelpath, basedatapath, area_sides = None, ReadfromFile = False, maxflighttime = 20.0*60.0, simulate = False, FlirAttached = False, 
                    startlat = 0,startlon = 0,out_folder='FlyingControl_results', GridAlignedPathPlanning = True, PiWayPointRadiusCheck = 5.0,
                    PlanningAlgo = None, Flying_Height = 35, DroneFlyingSpeed =  1, FasterDroneFlyingSpeed = 3, WayPointHoldingTime = 5,
                    GrabVideoFrames = True, ImageSamplingDistance = 1.0, SimulatedData = None, Render = True,
                      RenderAfter = 1, CenterUTMInfo = None, GridSideLength = 30,prob_map = None, adddebugInfo = False
                    ):
        if not os.path.isdir( out_folder ): 
            os.mkdir( out_folder)
        self._out_folder =  out_folder 
        self._adddebugInfo = adddebugInfo       
        self._simulation = simulate
        self._startlat = startlat
        self._startlon = startlon
        self._CenterEast = CenterEast
        self._CenterNorth = CenterNorth
        self._objectmodelpath = objectmodelpath
        self._maxflighttime = maxflighttime
        self._GridAlignedPathPlanning = GridAlignedPathPlanning
        self._PlanningAlgo = None
        self._Flying_Height = Flying_Height
        self._DroneFlyingSpeed = DroneFlyingSpeed
        self._FasterDroneFlyingSpeed = FasterDroneFlyingSpeed
        self._ReadfromFile = ReadfromFile
        self._WayPointHoldingTime = WayPointHoldingTime
        self._PiWayPointRadiusCheck = PiWayPointRadiusCheck
        self._GrabVideoFrames = GrabVideoFrames
        self._basedatapath = basedatapath
        self._sitename = sitename
        self._ImageSamplingDistance = ImageSamplingDistance
        self._SimulatedData = SimulatedData
        self._Render = Render
        self._RenderAfter = RenderAfter
        self._CenterUTMInfo = CenterUTMInfo
        self._area_sides = area_sides
        self._GridAlignedPathPlanning = GridAlignedPathPlanning
        self._GridSideLength = GridSideLength
        self._prob_map = prob_map

    ##############################################################################    
    def FlyingControl(self, CurrentGPSInfoQueue, SendWayPointInfoQueue, CurrentGPSInfoQueueEventQueue, RenderingQueue, FlyingProcessEvent):
        """Blocking Function till maximum drone flying time has been reached or last waypoint has been reached
            once a waypoint has been reached it ask Planner to plan next waypoints by sending current coordinates
            for every gps tagged frame ut receives from DroneCom it determines whether waypoint has been reached or not
            if waypoint is not reached it than selects frames which are 1m away from last selected frame. 
            selected frames are communicated to the Renderer_Detector
        :param CurrentGPSInfoQueueEventQueue: boolean queue to indicate whether to capture frames or not --- Redundant in new implementation with framegrabber
        :type CurrentGPSInfoQueueEventQueue:    `multiprocessing.Queue` or `threading.Queue`
        :param SendWayPointInfoQueue: queue which stores info of waypoints to be traversed.
            based on planned waypoints it sends DroneCom Waypoints info to communicate to drone
            waypoint data is comprised in a dictionary {    'Latitude':  # value =int(gps long x 10000000), 
                                                            'Longitude': # value =int(gps long x 10000000), 
                                                            'Altitude': # value should be desired Altitude in m above starting height,
                                                            'Speed': # value should be desired speed in m/s, 
                                                            'Index':
                                                        }
            and sent to DroneCom by 'SendWayPointInfoQueue.put(dictionary)'
        :type SendWayPointInfoQueue:    `multiprocessing.Queue` or `threading.Queue`
        :param CurrentGPSInfoQueue: queue which stores gps tagged frames.  
            reading with `CurrentGPSInfoQueue.get()` returns a dictionary of the form 
            {   'Latitude' = # gps lat = (value x 0.0000001)
                'Longitude' = # gps lon = (value x 0.0000001)
                'Altitude' = # absolute altitude
                'BaroAltitude' = # relative altitude = (value / 100) 
                'TargetHoldTime' = # Counter set to fixed value and counts down to 0 once it reaches waypoint
                'CompassHeading' = # compass values in step of 2 degrees
                'Image' = #Acquired frame from framegrabber
            }
        :type CurrentGPSInfoQueue: `multiprocessing.Queue` or `threading.Queue`
        :param RenderingQueue: queue which stores selected gpstagged frames approx. 1m apart from each other.
            each read frame from CurrentGPSInfoQueue is checked to see if waypoint has been reached or not.
            if not it checks if it is 1m away from previously selected frame. 
            if it is the frame is put in queue in form of a dictionary
            {   'Latitude' = # 
                'Longitude' = # 
                'Altitude' = # 
                'Image' = # 
                'StartingHeight' = #
            }
            the dictionary is sent to Renderer_Detector by 'RenderingQueue.put(dictionary)'
        :type RenderingQueue: `multiprocessing.Queue` or `threading.Queue`
        :param FlyingProcessEvent: boolean type event enabled by 'FlyingProcessEvent.set()' when last waypoint has been reached 
                                    or flying time is more than maximum allowed drone flying time
        :type FlyingProcessEvent:`multiprocessing.Event` or `threading.Event`
        """
        self._PlanningAlgo = Planner( utm_center=(self._CenterUTMInfo[0], self._CenterUTMInfo[1], self._CenterUTMInfo[2], self._CenterUTMInfo[3]), area_size= self._area_sides, tile_distance = self._GridSideLength,  prob_map=self._prob_map, debug=False,vis=None, results_folder=self._out_folder,gridalignedplanpath=self._GridAlignedPathPlanning)
        self._log = setup_logger( 'Flying_logger', os.path.join( self._out_folder, 'FlyControlInfoLog.log'))
        self._gpsframelog = setup_logger( 'GPSFrame_logger', os.path.join( self._out_folder, 'GPSLog.log'))
        self._log.debug('Start Flight')
        self._gpsframelog.debug('StartTime StartLatitude StartLongitude')
        if not self._ReadfromFile :
            CurrentGPSInfoQueueEventQueue.put(True)
            while CurrentGPSInfoQueue.empty():
                time.sleep(1)
            CurrentGPSInfoQueueEventQueue.put(False)
            while not CurrentGPSInfoQueue.empty():
                CurrentGPSInfo = CurrentGPSInfoQueue.get()
                StartLatitude = CurrentGPSInfo['Latitude']*0.0000001
                StartLongitude = CurrentGPSInfo['Longitude']*0.0000001
        else :
            StartLatitude = self._startlat
            StartLongitude = self._startlon
        startEast,startNorth,Block,UTMZONE = utm.from_latlon(StartLatitude, StartLongitude)
        StartCenteredEastUTM = startEast - self._CenterEast
        StartCenteredNorthUTM = self._CenterNorth - startNorth
        MinimumStartingHeigth,Index = FindStartingHeight(self._objectmodelpath, StartCenteredEastUTM, StartCenteredNorthUTM)
        #CaptureRenderDetectCurrentData.AddStartingHeight(MinimumStartingHeigth)
        ####Todo :- Communicate MinimumStartingHeight to Renderer
        self._log.debug('StartingPoint StartLatitude = %s StartLongitude =%s StartEast = %s StartNorth = %s CenterEast = %s CenterNorth = %s StartCenterEast = %s StartCenterNorth = %s And StartingHeight = %s', str(StartLatitude), str(StartLongitude), str(startEast), str(startNorth), str(self._CenterEast), str(self._CenterNorth), str(StartCenteredEastUTM), str(StartCenteredNorthUTM), str(MinimumStartingHeigth))
        self._gpsframelog.debug('%s %s', str(StartLatitude),str(StartLongitude))
        self._gpsframelog.debug('Time Latitude Longitude Altitude CompassHeading TargetHoldTime(from GPSLog)')
        NoofCheckedWayPoints = 0
        NoofPointsChecked = 0
        NoofPointsinPreviousPath = 0
        prev_pt = (StartLatitude, StartLongitude)
        NoofPlannedPath = 0
        NoofPlannedPoints = 0
        CompleteRendering = False
        DetectedHumanFlag = False
        starttime = datetime.datetime.now()
        CurrentFlightTime = 0.0
        self._log.debug('Current Time %s ', str(CurrentFlightTime))
        CurrentGPSInfoQueueEventQueue.put(True)
        while CurrentFlightTime < self._maxflighttime:
            if DetectedHumanFlag:
                pass # For Testing Pass if Human Detected --- For Actual Flights -- break
            if not self._GridAlignedPathPlanning :    
                next_pts = self._PlanningAlgo.planpoints( prev_pt )
                if len(next_pts) >= 1:
                    FlyingInfoFlag = [True for i in range(len(next_pts))]
            else :
                next_pts, FlyingInfoFlag = self._PlanningAlgo.planpoints( prev_pt )
            self._log.debug('Planned Points With Length   %s ', str(len(next_pts)))
            #If Grid is completely sampled then next_pts will be empty
            if len(next_pts) >= 1 :
                NoofPlannedPath = NoofPlannedPath + 1
                for i in range(len(next_pts)) :
                    next_pos = next_pts[i]
                    FlyingInfo = FlyingInfoFlag[i]
                    self._log.debug('FlyingInfo  %s ', str(FlyingInfo))
                    NoofPlannedPoints = NoofPlannedPoints + 1
                    DestinationLat = int(next_pos[0]*10000000)
                    DestinationLon = int(next_pos[1]*10000000)
                    NextAltitude = self._Flying_Height
                    if FlyingInfo :
                        FlyingSpeed = self._DroneFlyingSpeed
                    else :
                        FlyingSpeed = self._FasterDroneFlyingSpeed
                    self._log.debug('Sending to Position %s %s %s with Flying Speed %s', str(DestinationLat),str(DestinationLon), str(NextAltitude), str(FlyingSpeed))
                    assert NextAltitude > 25 , "Height Below 25 Meters"
                    WayPointInfo = {}
                    WayPointInfo['Latitude'] = DestinationLat
                    WayPointInfo['Longitude'] = DestinationLon
                    WayPointInfo['Altitude'] = NextAltitude
                    WayPointInfo['Speed'] = FlyingSpeed
                    WayPointInfo['Index'] = NoofPlannedPoints
                    SendWayPointInfoQueue.put(WayPointInfo)
                    x = NoofPlannedPoints
                    self._log.debug('Sent WayPoint %s', str(x))
                    CheckPoint = True
                    if CompleteRendering:
                        self._gpsframelog.debug('%s %s %s %s', str(x-1), str(NoofPointsinPreviousPath),str(NoofPointsChecked),str(0))
                        CompleteRendering = False
                        NoofPointsinPreviousPath = 0
                    PrevImagetoPrevSampleDistance = 0.0
                    PrevLat = 0.0
                    PrevLon = 0.0
                    prevAlt = 0.0
                    PrevComp = 0.0
                    PrevImage = None
                    while CheckPoint == True:
                        NoofCheckedWayPoints = NoofCheckedWayPoints+1
                        NoofPointsChecked = NoofPointsChecked + 1
                        ###################Read Current Drone Information
                        if not self._ReadfromFile :
                            #print('Queue Size',CurrentGPSInfoQueue.qsize())
                            ReceivedCurrentDroneData = CurrentGPSInfoQueue.get()
                            #t1_start = time.perf_counter()
                            Latitude = ReceivedCurrentDroneData['Latitude']*0.0000001
                            Longitude = ReceivedCurrentDroneData['Longitude']*0.0000001
                            Altitude = ReceivedCurrentDroneData['BaroAltitude']/100
                            DroneTargetHoldTime = ReceivedCurrentDroneData['TargetHoldTime']
                            CompassHeading = ReceivedCurrentDroneData['CompassHeading']
                        else :
                            SimulatedDataGPSInfo = self._SimulatedData[NoofCheckedWayPoints]
                            Latitude = SimulatedDataGPSInfo['Latitude']
                            Longitude = SimulatedDataGPSInfo['Longitude']
                            Altitude = SimulatedDataGPSInfo['BaroAltitude']
                            DroneTargetHoldTime = SimulatedDataGPSInfo['TargetHoldTime']
                            CompassHeading = SimulatedDataGPSInfo['CompassHeading']
                            AngleNick = 0
                            AngleRoll = 0
                            DistancetoTarget = 0 
                        Distance = haversine(Latitude, Longitude, next_pos[0], next_pos[1])
                        #print('checking Waypoint')
                        if DroneTargetHoldTime < self._WayPointHoldingTime and DroneTargetHoldTime > 0.0:
                            if (Distance) < self._PiWayPointRadiusCheck :
                                ReachedWayPoint = True
                            else :
                                ReachedWayPoint = False
                        else:
                            ReachedWayPoint = False
                        ###################If  Cell is Scanned
                        if FlyingInfo :
                            if self._adddebugInfo :
                                self._log.debug('Curent Position Considered%s %s %s %s', str(Latitude),str(Longitude),str(Altitude),str(CompassHeading))
                            AddCurrentImage = False
                            AddPreviousImage = False
                            ###################Determine Whether Current Image and GPS Position is ImageSamplingDistance = 1.0 meters away from previous added sample otherwise 
                            ##########################store the sample for future consideration
                            if self._GrabVideoFrames :
                                if self._ReadfromFile :
                                    ReadImageName = os.path.join(self._basedatapath,'FlightResults', self._sitename, 'PiFrameGrabber', str(NoofPlannedPath)+'_'+str(NoofPointsinPreviousPath)+'.png')
                                    Frame = cv2.imread(ReadImageName)
                                else :
                                    Frame = ReceivedCurrentDroneData['Image']
                                    #if Frame is not None:
                                    #    filename = os.path.join(self._out_folder,str(NoofPlannedPath)+'_'+str(NoofPointsChecked)+'.png')
                                    #    cv2.imwrite(filename,Frame)
                            if not NoofPointsinPreviousPath:
                                AddCurrentImage = True
                                AddPreviousImage = False
                                PrevLat = Latitude
                                PrevLon = Longitude
                                prevAlt = Altitude
                                PrevComp = CompassHeading
                                PrevImage = Frame
                                PrevSampleLat = Latitude
                                PrevSampleLon = Longitude
                                PrevImagetoPrevSampleDistance = 0.0
                                if self._adddebugInfo :
                                    self._log.debug('%s %s %s %s', str(Latitude),str(Longitude),str(Altitude),str(CompassHeading))
                                    self._log.debug('Current Image is on new path AddPreviousImage is %s and AddCurrentImage is  %s', str(AddPreviousImage),str(AddCurrentImage)) 
                                    
                            else :
                                CurrentImagetoPreviousSampleDistance = haversine(Latitude, Longitude, PrevSampleLat, PrevSampleLon)
                                CurrentImagetoPreviousImageDistance = haversine(Latitude, Longitude, PrevLat, PrevLon)
                                if self._adddebugInfo :
                                    self._log.debug('distance Calculation %s %s %s %s %s %s', str(PrevSampleLat),str(PrevSampleLon) , str(PrevLat),str(PrevLon), str(Latitude),str(Longitude))
                                    self._log.debug('CurrentImagetoPreviousSampleDistance is %s and CurrentImagetoPreviousImageDistance is  %s and PrevImagetoPrevSampleDistance is %s', str(CurrentImagetoPreviousSampleDistance),str(CurrentImagetoPreviousImageDistance), str(PrevImagetoPrevSampleDistance))
                                if CurrentImagetoPreviousSampleDistance >= self._ImageSamplingDistance or ReachedWayPoint == True:
                                    if  abs(PrevImagetoPrevSampleDistance - 0.0) > 0.01 :
                                        if abs(CurrentImagetoPreviousSampleDistance - self._ImageSamplingDistance) <= abs(PrevImagetoPrevSampleDistance - self._ImageSamplingDistance) or ReachedWayPoint == True :
                                            AddCurrentImage = True
                                            AddPreviousImage = False
                                            if self._adddebugInfo :
                                                self._log.debug('PrevSample Position %s %s', str(PrevSampleLat),str(PrevSampleLon))
                                                self._log.debug('Current Position %s %s %s %s %s', str(Latitude),str(Longitude),str(Altitude),str(CompassHeading), str(CurrentImagetoPreviousSampleDistance))
                                                self._log.debug('Previous Position %s %s %s %s %s', str(PrevLat),str(PrevLon),str(prevAlt),str(PrevComp), str(PrevImagetoPrevSampleDistance))
                                                self._log.debug('Current Image is closer to 1m than previous image AddPreviousImage is %s and AddCurrentImage is  %s', str(AddPreviousImage),str(AddCurrentImage)) 
                                        else :
                                            AddCurrentImage = False
                                            AddPreviousImage = True
                                            NoofPointsinPreviousPath = NoofPointsinPreviousPath + 1
                                            gray = cv2.cvtColor(PrevImage, cv2.COLOR_BGR2GRAY)
                                            gray = gray.astype('float32')
                                            gray /= 255.0
                                            SendImage = gray
                                            RenderingInfo = {}
                                            RenderingInfo['Latitude'] = PrevLat
                                            RenderingInfo['Longitude'] = PrevLon
                                            RenderingInfo['Altitude'] = prevAlt
                                            RenderingInfo['CompassHeading'] = PrevComp
                                            RenderingInfo['Image'] = SendImage
                                            RenderingInfo['StartingHeight'] = MinimumStartingHeigth
                                            
                                            if Frame is not None:
                                                filename2 = os.path.join(self._out_folder,str(NoofPlannedPath)+'_'+str(NoofPointsinPreviousPath)+'_'+str(NoofPointsChecked)+'.png')
                                                cv2.imwrite(filename2,PrevImage)
                                            PrevSampleLat = PrevLat
                                            PrevSampleLon = PrevLon
                                            PrevImagetoPrevSampleDistance = CurrentImagetoPreviousImageDistance
                                            if self._GrabVideoFrames :
                                                if self._Render :
                                                    if ReachedWayPoint == True:
                                                        RenderingInfo['Render'] = True
                                                        RenderingInfo['UpdatePlanningAlgo'] = True
                                                        RenderingQueue.put(RenderingInfo)
                                                    else :
                                                        if NoofPlannedPath > 1 : 
                                                            if ((NoofPointsinPreviousPath % self._RenderAfter) == 0):
                                                                RenderingInfo['Render'] = True
                                                            else :
                                                                RenderingInfo['Render'] = False
                                                            RenderingInfo['UpdatePlanningAlgo'] = False
                                                            RenderingQueue.put(RenderingInfo)
                                                        else :
                                                            if NoofPointsinPreviousPath > 29 :
                                                                #RenderingInfo['Render'] = True
                                                                if ((NoofPointsinPreviousPath % self._RenderAfter) == 0):
                                                                    RenderingInfo['Render'] = True
                                                                else :
                                                                    RenderingInfo['Render'] = False
                                                                RenderingInfo['UpdatePlanningAlgo'] = False
                                                                RenderingQueue.put(RenderingInfo)
                                                            else :
                                                                RenderingInfo['Render'] = False
                                                                RenderingInfo['UpdatePlanningAlgo'] = False
                                                                RenderingQueue.put(RenderingInfo)
                                            
                                            if self._adddebugInfo :                
                                                self._gpsframelog.debug('%s %s %s %s', str(PrevLat),str(PrevLon),str(prevAlt),str(PrevComp))
                                                self._log.debug('PrevSample Position %s %s', str(PrevSampleLat),str(PrevSampleLon))
                                                self._log.debug('Current Position %s %s %s %s %s', str(Latitude),str(Longitude),str(Altitude),str(CompassHeading), str(CurrentImagetoPreviousSampleDistance))
                                                self._log.debug('Previous Position %s %s %s %s %s', str(PrevLat),str(PrevLon),str(prevAlt),str(PrevComp), str(PrevImagetoPrevSampleDistance))
                                                self._log.debug('previous image is closer to 1m AddPreviousImage is %s and AddCurrentImage is  %s', str(AddPreviousImage),str(AddCurrentImage))
                                            else :
                                                self._gpsframelog.debug('%s %s %s %s', str(PrevLat),str(PrevLon),str(prevAlt),str(PrevComp))
                                            if (CurrentImagetoPreviousImageDistance >= self._ImageSamplingDistance) or ReachedWayPoint == True :
                                                AddCurrentImage = True
                                                AddPreviousImage= False
                                                if self._adddebugInfo :
                                                    self._log.debug('PrevSample Position %s %s', str(PrevSampleLat),str(PrevSampleLon))
                                                    self._log.debug('Current Position %s %s %s %s %s', str(Latitude),str(Longitude),str(Altitude),str(CompassHeading), str(CurrentImagetoPreviousSampleDistance))
                                                    self._log.debug('Previous Position %s %s %s %s %s', str(PrevLat),str(PrevLon),str(prevAlt),str(PrevComp), str(PrevImagetoPrevSampleDistance))
                                                    self._log.debug('current image is 1m apart from previous imageAddPreviousImage is %s and AddCurrentImage is  %s', str(AddPreviousImage),str(AddCurrentImage)) 
                                            else :
                                                if CurrentImagetoPreviousImageDistance >= 0.01:
                                                    PrevLat = Latitude
                                                    PrevLon = Longitude
                                                    AddCurrentImage = False
                                                    AddPreviousImage = False
                                                    prevAlt = Altitude
                                                    PrevComp = CompassHeading
                                                    PrevImage = Frame
                                                    PrevImagetoPrevSampleDistance = CurrentImagetoPreviousImageDistance
                                    else :
                                        AddCurrentImage = True
                                        AddPreviousImage = False
                                        if self._adddebugInfo :
                                            self._log.debug('PrevSample Position %s %s', str(PrevSampleLat),str(PrevSampleLon))
                                            self._log.debug('Current Position %s %s %s %s %s', str(Latitude),str(Longitude),str(Altitude),str(CompassHeading), str(CurrentImagetoPreviousSampleDistance))
                                            self._log.debug('Previous Position %s %s %s %s %s', str(PrevLat),str(PrevLon),str(prevAlt),str(PrevComp), str(PrevImagetoPrevSampleDistance))
                                            self._log.debug('Current Image is closer to 1m than previous image AddPreviousImage is %s and AddCurrentImage is  %s', str(AddPreviousImage),str(AddCurrentImage)) 
                                else :
                                    if CurrentImagetoPreviousImageDistance >= 0.001:
                                        PrevLat = Latitude
                                        PrevLon = Longitude
                                        AddCurrentImage = False
                                        AddPreviousImage = False
                                        prevAlt = Altitude
                                        PrevComp = CompassHeading
                                        PrevImage = Frame
                                        PrevImagetoPrevSampleDistance = CurrentImagetoPreviousSampleDistance
                            if AddCurrentImage == True:
                                NoofPointsinPreviousPath = NoofPointsinPreviousPath + 1
                                gray = cv2.cvtColor(Frame, cv2.COLOR_BGR2GRAY)
                                gray = gray.astype('float32')
                                gray /= 255.0
                                SendImage = gray
                                PrevSampleLat = Latitude
                                PrevSampleLon = Longitude
                                PrevImagetoPrevSampleDistance = 0.0
                                RenderingInfo = {}
                                RenderingInfo['Latitude'] = Latitude
                                RenderingInfo['Longitude'] = Longitude
                                RenderingInfo['Altitude'] = Altitude
                                RenderingInfo['CompassHeading'] = CompassHeading
                                RenderingInfo['Image'] = SendImage
                                RenderingInfo['StartingHeight'] = MinimumStartingHeigth
                                if Frame is not None:
                                    filename2 = os.path.join(self._out_folder,str(NoofPlannedPath)+'_'+str(NoofPointsinPreviousPath)+'_'+str(NoofPointsChecked)+'.png')
                                    cv2.imwrite(filename2,Frame)
                                if self._GrabVideoFrames :
                                    if self._Render :
                                        if ReachedWayPoint == True:
                                            RenderingInfo['Render'] = True
                                            RenderingInfo['UpdatePlanningAlgo'] = True
                                            RenderingQueue.put(RenderingInfo)
                                        else :
                                            if NoofPlannedPath > 1 :
                                                if ((NoofPointsinPreviousPath % self._RenderAfter) == 0):
                                                    RenderingInfo['Render'] = True
                                                else :
                                                    RenderingInfo['Render'] = False
                                                RenderingInfo['UpdatePlanningAlgo'] = False
                                                RenderingQueue.put(RenderingInfo)
                                            else :
                                                if NoofPointsinPreviousPath > 29 :
                                                    #RenderingInfo['Render'] = True
                                                    if ((NoofPointsinPreviousPath % self._RenderAfter) == 0):
                                                        RenderingInfo['Render'] = True
                                                    else :
                                                        RenderingInfo['Render'] = False
                                                    RenderingInfo['UpdatePlanningAlgo'] = False
                                                    RenderingQueue.put(RenderingInfo)
                                                else :
                                                    RenderingInfo['Render'] = False
                                                    RenderingInfo['UpdatePlanningAlgo'] = False
                                                    RenderingQueue.put(RenderingInfo)
                                if self._adddebugInfo :                
                                    self._gpsframelog.debug('%s %s %s %s', str(Latitude),str(Longitude),str(Altitude),str(CompassHeading))
                                    self._log.debug('AddPreviousImage is %s and AddCurrentImage is  %s', str(AddPreviousImage),str(AddCurrentImage))
                                else :
                                    self._gpsframelog.debug('%s %s %s %s', str(Latitude),str(Longitude),str(Altitude),str(CompassHeading))     
                        if ReachedWayPoint == False:
                            CheckPoint = True
                        else:
                            CheckPoint = False
                            #with CurrentGPSInfoQueue.mutex :
                            #CurrentGPSInfoQueue.queue.clear()
                    if self._adddebugInfo :
                        self._log.debug('Reached WayPoint %s', str(x))
                    prev_pt = next_pts[-1]
                    CompleteRendering = True   
                    currenttime = datetime.datetime.now()
                    diff = currenttime - starttime
                    CurrentFlightTime = diff.total_seconds()
                    if self._adddebugInfo :
                        self._log.debug('Calculated CurrentFlightTime %s', str(CurrentFlightTime))
            else :
                CurrentFlightTime  = self._maxflighttime + 1
        #################Added for Adaptive Path Planning #################################
        ###################################################################################################                    
        self._gpsframelog.debug('%s %s %s %s', str(x), str(NoofPointsinPreviousPath),str(NoofPointsChecked),str(0))
        time.sleep(1.0)
        CurrentGPSInfoQueueEventQueue.put(False)
        FlyingProcessEvent.set()
        #Todo .-  Indicate to other threads to stop.
        print('Flying  Process Done')
        self._log.debug('Flying  Process Done')
##############################################################################

if __name__ == '__main__':
    out_folder = 'FlyingControl_Results'
    if not os.path.isdir( out_folder ): 
        os.mkdir( out_folder)
    MainLog = setup_logger( 'MainLogger', os.path.join( out_folder, 'MainTest.log') )

    sitename = '20210304_OpenField_T4R2_T1_S1'
    #anaos_path = os.environ.get('ANAOS_DATA')
    
    basedatapath = 'D:\\RESILIO\\ANAOS\\SIMULATIONS'
    print(os.path.join(basedatapath,'FlightResults', sitename, 'Pose_absolute'))
    PosesFilePath = os.path.join(basedatapath,'FlightResults', sitename, 'NewNormalization','SimulationPoses')
    ImageLocation = os.path.join(basedatapath, 'FlightResults',sitename, 'Frames_renamed')
    ObjModelPath = os.path.join(basedatapath,'FlightResults', sitename, 'LFR','dem.obj')
    ObjModelImagePath = os.path.join(basedatapath,'FlightResults', sitename, 'LFR','dem.png')
    SaveImagePath = os.path.join(basedatapath, 'FlightResults',sitename, 'NewNormalization','SimulationPoses_CPURenderedImages')
    SaveProjImagePath = os.path.join(basedatapath,'FlightResults', sitename, 'NewNormalization','ProjectedImages')
    DemInfoJSOn = os.path.join(basedatapath, 'FlightResults',sitename, 'LFR','dem_info.json')
    GpsLogFile = os.path.join(basedatapath, 'FlightResults',sitename, 'GPSLog.log')
    with open(DemInfoJSOn) as json_file:
        DemInfoDict = json.load(json_file)
    print(DemInfoDict)
    CenterUTMInfo = DemInfoDict['centerUTM']
    CenterEast = CenterUTMInfo[0]   
    CenterNorth = CenterUTMInfo[1]
    FieldofView = 43.10803984095769#43.50668199945787
    startLat = 48.3361339 #48.3360345 48.3361339 
    startLon = 14.32645814596519#14.3264914
    startEast,startNorth,Block,UTMZONE = utm.from_latlon(startLat, startLon)
    StartCenteredEastUTM = startEast - CenterEast
    StartCenteredNorthUTM = CenterNorth - startNorth
    MinimumStartingHeigth,Index = FindStartingHeight(ObjModelPath, StartCenteredEastUTM, StartCenteredNorthUTM)

    CurrentGPSInfoQueue = multiprocessing.Queue()
    SendWayPointInfoQueue = multiprocessing.Queue()
    CurrentGPSInfoQueueEventQueue = multiprocessing.Queue()
    RenderingQueue = multiprocessing.Queue()

    FlyingProcessEvent = multiprocessing.Event()

    InterPolatedGPSReceivedLogFileName = 'D:\\RESILIO\\ANAOS\\SIMULATIONS\\FlightResults\\20210304_OpenField_T4R2_T1_S1\\GPSInterpolatedLog.log'
    InterpolatedLat, InterpolatedLon, InterpolatedAlt, InterpolatedCompass, InterpolatedTargetHoldTime = ReadInterpolatedGPSlogFiles(InterPolatedGPSReceivedLogFileName)

    #utm_center = (CenterUTMInfo[0], CenterUTMInfo[1], CenterUTMInfo[2], CenterUTMInfo[3])

    #PlanningAlgoClass = Planner( utm_center=utm_center, area_size= (90,90), tile_distance = 90,  prob_map=None, debug=False,vis=None, results_folder=out_folder)
    
    FlyingControlClass = DroneFlyingControl(sitename = sitename,CenterEast = CenterEast,CenterNorth = CenterNorth,
    objectmodelpath=ObjModelPath,basedatapath=basedatapath,Render=True,
                                            FlirAttached = True,Flying_Height = 30,
                                            DroneFlyingSpeed = 40,RenderAfter = 2, CenterUTMInfo=CenterUTMInfo,
    out_folder=out_folder,adddebugInfo=True)

    FlyingControlProcess = multiprocessing.Process(name = 'FlyingControlProcess',target= FlyingControlClass.FlyingControl, args=(CurrentGPSInfoQueue,SendWayPointInfoQueue,CurrentGPSInfoQueueEventQueue, RenderingQueue,FlyingProcessEvent,))
    #FlyingControlProcess = multiprocessing.Process(name = 'FlyingControlProcess',target= FlyingControlClass.TryClassFunction, args=(CurrentGPSInfoQueue,))
    
    FlyingControlProcess.start()

    print('Length of Lat', len(InterpolatedLat))

    for i in range(len(InterpolatedLat)):
        CurrentDroneInfoDict = {}
        CurrentDroneInfoDict['Latitude'] = float(InterpolatedLat[i])
        CurrentDroneInfoDict['Longitude'] = float(InterpolatedLon[i])
        CurrentDroneInfoDict['Altitude'] = 0.0
        CurrentDroneInfoDict['BaroAltitude'] = float(InterpolatedAlt[i])
        CurrentDroneInfoDict['TargetHoldTime'] = float(InterpolatedCompass[i])
        CurrentDroneInfoDict['CompassHeading'] = float(InterpolatedTargetHoldTime[i])
        CurrentDroneInfoDict['Image'] = np.random.randint(0,255,size = (640,480,3)).astype(np.uint8)
        CurrentGPSInfoQueue.put(CurrentDroneInfoDict)
        print('Sent Waypoints', i)
        if not RenderingQueue.empty():
            RenderingInfo = RenderingQueue.get()
            MainLog.debug('Rendering Info Received %s %s', str(RenderingInfo['Latitude']),str(RenderingInfo['Longitude']))
        time.sleep(0.01)
        if FlyingProcessEvent.is_set():
            time.sleep(2)
            CurrentGPSInfoQueue.close()
            SendWayPointInfoQueue.close()
            CurrentGPSInfoQueueEventQueue.close()
            RenderingQueue.close()
            break
    FlyingControlProcess.join()
    print('FlyingControlProcess.is_alive()', FlyingControlProcess.is_alive())
    print('All Process Done')
        
            
    

