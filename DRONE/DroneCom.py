import time
import ctypes as ct
import shutil
import os
import glob
import numpy as np
import math
import json
import cv2
import utm
import random
from datetime import datetime, timezone
from CameraControl_MultiProcess import CameraControl
from scipy import interpolate
from scipy.interpolate import InterpolatedUnivariateSpline
import logging
import multiprocessing
from statistics import mean 



class GPSInfo:
    def __init__(self, Latitude, Longitude, Altitude, TargetHoldTime,CompassHeading):
        self.Latitude = Latitude
        self.Longitude = Longitude
        self.BaroAltitude = Altitude
        self.TargetHoldTime = TargetHoldTime
        self.CompassHeading = CompassHeading
        self.Altitude = 0.0
        self.streamInfo = 1
        self.Index = 10
##############################################################################
class CurrentDroneInfo(ct.Structure):
    _fields_ = [("streamInfo", ct.c_int),("Index", ct.c_int), ("Latitude", ct.c_int), ("Longitude", ct.c_int), ("Altitude", ct.c_int), ("BaroAltitude", ct.c_int), ("CompassHeading", ct.c_int), ("AngleNick", ct.c_int), ("AngleRoll", ct.c_int), ("WaypointIndex", ct.c_int), ("WayPointNumber", ct.c_int), ("DistanceToTarget", ct.c_int), ("TargetHoldTime", ct.c_int)]
##############################################################################

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

def ReadGPSReceivedLogFiles(FileName):
    LatitudeList = []
    LongitudeList = []
    AltitudeList = []
    DroneHoldTime = []
    CompassList = []
    DistanceToTarget = []
    AngleRollList = []
    AngleNickList = []
    Date = []
    Time = []
    DebugInfo = []
    CompleteGPSReceivedInfo = []
    Date, Time, DebugInfo, LatitudeList,LongitudeList,AltitudeList,AngleNickList,AngleRollList,CompassList,DistanceToTarget,DroneHoldTime =  np.genfromtxt(FileName, skip_header=0, unpack=True, delimiter=' ')
    print(len(LatitudeList))
    for i in range(len(LatitudeList)):
        Dict = GPSInfo(LatitudeList[i],LongitudeList[i],AltitudeList[i],DroneHoldTime[i],CompassList[i])
        CompleteGPSReceivedInfo.append(Dict)
    return CompleteGPSReceivedInfo

def ReadNewGPSReceivedLogFiles(FileName):
    LatitudeList = []
    LongitudeList = []
    AltitudeList = []
    DroneHoldTime = []
    CompassList = []
    DistanceToTarget = []
    AngleRollList = []
    AngleNickList = []
    Date = []
    Time = []
    DebugInfo = []
    CompleteGPSReceivedInfo = []
    Date, Time, DebugInfo, LatitudeList,LongitudeList,AltitudeList,CompassList,DroneHoldTime =  np.genfromtxt(FileName, skip_header=0, unpack=True, delimiter=' ')
    print(len(LatitudeList))
    for i in range(len(LatitudeList)):
        Dict = GPSInfo(LatitudeList[i],LongitudeList[i],AltitudeList[i],DroneHoldTime[i],CompassList[i])
        CompleteGPSReceivedInfo.append(Dict)
    return CompleteGPSReceivedInfo


##############################################################################
class DroneCommunication():
    _simulation = False
    _addsynthethicimage = False
    _so_file = '/home/pi/PyCLFR_AutoDrone/glesLFR/src/droneCommunication_SI_ZeroTol.so'
    _DroneCommunication = None
    _GPSInfoDictList = []
    _SimulationCount = 0
    # logging
    _log = None
    _queueLog = None
    _out_folder = None
    _sentwaypointlog = None
    _synthethic_image_res_x = 480
    _synthethic_image_res_y = 320
    _FlirAttached = False
    _interpolation = True
    _extrapolate = True


    def  __init__(self, simulate = False, GPSLog = [], interpolation = True, extrapolate = True, AddSynthethicImage = False, FlirAttached = False, resx = 480, resy = 320,  out_folder='Communication_results',   so_file = '/home/pi/PyCLFR_AutoDrone/glesLFR/src/droneCommunication_SI_ZeroTol.so'):
        self._simulation = simulate
        self._so_file = so_file
        self._addsynthethicimage = AddSynthethicImage
        self._PreviousLatitude = -1
        self._PreviousLongitude = -1
        self._PreviousAltitude = -1
        self._PreviousBaroAltitude = -1
        self._PreviousDroneTargetHoldTime = -1
        self._PreviousCompassHeading = -1
        self._SimulationCount = 0
        self._CaptureFrameandAddtoQueue = False
        self._FlirAttached = FlirAttached
        if not self._simulation:
            self._DroneCommunication = ct.CDLL(so_file)
            self._DroneCommunication.uart_init.restype = ct.c_int
        else :
            self._GPSInfoDictList = GPSLog
        if not os.path.isdir( out_folder ): 
            os.mkdir( out_folder)
        self._out_folder = out_folder
        self._synthethic_image_res_x = resx
        self._synthethic_image_res_y = resy
        self._interpolation = interpolation
        self._extrapolate = extrapolate
        self._order = 1
        self._CurrentFrameTimeList = []
        self._CurrentFrameList = []
        self._NextFrameTimeList = []
        self._NextFrameList = []
        self._GPSLatList = []
        self._GPSLonList = []
        self._GPSAltList = []
        self._GPSCompList = []
        self._GPSTimeList = []
    

    def DroneInit(self):
        StreamI = self._DroneCommunication.uart_init( ct.c_int(0))
        print(StreamI)
        #fw.write('StreamInfo = ' + repr(StreamI) + '\n');
    
    def DroneInfo(self, CurrentGPSInfoQueue, SendWayPointInfoQueue, CurrentGPSInfoQueueEventQueue, DroneProcessEvent, FrameQueue, GetFramesEvent, GPSLog = None):
        #print('Drone Communication Started in First Thread')
        #if self._simulation:
        #    self._GPSInfoDictList = GPSLog
        print(len(self._GPSInfoDictList))
        self._log = setup_logger( 'GPSReceived_logger', os.path.join( self._out_folder, 'GPSReceivedLog.log') )
        self._queueLog = setup_logger( 'GPSInterpolated_logger', os.path.join( self._out_folder, 'GPSInterpolatedLog.log') )
        self._sentwaypointlog = setup_logger( 'SentWayPoint_logger', os.path.join( self._out_folder, 'SentWaypoint.log') )
        if not self._simulation :
            self.DroneInit()
        else :
            PreviousTime =  datetime.now(timezone.utc).timestamp()
        if not self._interpolation:
            if self._FlirAttached and not self._addsynthethicimage:
                FlirVideoSource = cv2.VideoCapture(0)
        while not DroneProcessEvent.is_set():
            if not CurrentGPSInfoQueueEventQueue.empty():
                self._CaptureFrameandAddtoQueue = CurrentGPSInfoQueueEventQueue.get()
            if not SendWayPointInfoQueue.empty():
                SendingWayPointInfo = SendWayPointInfoQueue.get()
                print('Sending Waypoint')
                Index = SendingWayPointInfo['Index']
                LatToSend = SendingWayPointInfo['Latitude']
                LongtoSend = SendingWayPointInfo['Longitude']
                AlttoSend = SendingWayPointInfo['Altitude']*10
                SpeedtoSend = SendingWayPointInfo['Speed']*10
                #print('Upload and Send Drone to Waypoint', Index)
                self._sentwaypointlog.debug('Upload and Send Drone to Waypoint = %s to Lat = %s, Lon = %s, Alt = %s and Speed = %s', str(Index), str(LatToSend), str(LongtoSend),str(AlttoSend),str(SpeedtoSend) )
                if not self._simulation :
                    self._DroneCommunication.sendWayPoint(ct.c_int(LatToSend),ct.c_int(LongtoSend),ct.c_int(AlttoSend),ct.c_int(Index),ct.c_int(SpeedtoSend))
                #print('SendWayPointInfoQueue Size', SendWayPointInfoQueue.qsize())
            else:
                if not self._simulation :
                    self._DroneCommunication.receiveDroneInfo.restype = CurrentDroneInfo
                    DroneInfoData = self._DroneCommunication.receiveDroneInfo()
                    CurrentGPSReceivedtime = datetime.now(timezone.utc).timestamp()
                else :
                    #print(self._SimulationCount)
                    time.sleep(0.1)
                    DroneInfoData = self._GPSInfoDictList[self._SimulationCount]
                    CurrentGPSReceivedtime = datetime.now(timezone.utc).timestamp()
                    self._SimulationCount = self._SimulationCount + 1
                streamInfo = DroneInfoData.streamInfo
                if streamInfo != -1: 
                    Index = DroneInfoData.Index
                    if Index >= 10:
                        if self._interpolation:
                            if (abs(DroneInfoData.Latitude - self._PreviousLatitude ) > 0.01) or (abs(DroneInfoData.Longitude - self._PreviousLongitude ) > 0.01) :
                                GetFramesEvent.set()
                                if Index == 15:
                                    self._log.debug('%s %s %s %s %s %s New WayPoint', str(DroneInfoData.Latitude),str(DroneInfoData.Longitude),str(DroneInfoData.BaroAltitude),str(self._PreviousCompassHeading),str(DroneInfoData.TargetHoldTime),str(CurrentGPSReceivedtime))           
                                    self._PreviousDroneTargetHoldTime = DroneInfoData.TargetHoldTime
                                elif Index == 16:
                                    self._log.debug('%s %s %s %s %s %s New WayPoint', str(DroneInfoData.Latitude),str(DroneInfoData.Longitude),str(DroneInfoData.BaroAltitude),str(DroneInfoData.CompassHeading),str(self._PreviousDroneTargetHoldTime),str(CurrentGPSReceivedtime))               
                                    self._PreviousCompassHeading = DroneInfoData.CompassHeading
                                else :
                                    self._log.debug('%s %s %s %s %s %s New WayPoint', str(DroneInfoData.Latitude),str(DroneInfoData.Longitude),str(DroneInfoData.BaroAltitude),str(self._PreviousCompassHeading),str(self._PreviousDroneTargetHoldTime),str(CurrentGPSReceivedtime))           
                                self._GPSTimeList.append(CurrentGPSReceivedtime)
                                self._GPSLatList.append(DroneInfoData.Latitude)
                                self._GPSLonList.append(DroneInfoData.Longitude)
                                self._GPSAltList.append(DroneInfoData.BaroAltitude)
                                self._GPSCompList.append(self._PreviousCompassHeading)
                                time.sleep(0.02)    
                            else :
                                if Index == 15:
                                    self._log.debug('%s %s %s %s %s %s Old WayPoint', str(DroneInfoData.Latitude),str(DroneInfoData.Longitude),str(DroneInfoData.BaroAltitude),str(self._PreviousCompassHeading),str(DroneInfoData.TargetHoldTime),str(CurrentGPSReceivedtime))           
                                    self._PreviousDroneTargetHoldTime = DroneInfoData.TargetHoldTime
                                elif Index == 16:
                                    self._log.debug('%s %s %s %s %s %s Old WayPoint', str(DroneInfoData.Latitude),str(DroneInfoData.Longitude),str(DroneInfoData.BaroAltitude),str(DroneInfoData.CompassHeading),str(self._PreviousDroneTargetHoldTime),str(CurrentGPSReceivedtime))               
                                    self._PreviousCompassHeading = DroneInfoData.CompassHeading
                                else :
                                    self._log.debug('%s %s %s %s %s %s Old WayPoint', str(DroneInfoData.Latitude),str(DroneInfoData.Longitude),str(DroneInfoData.BaroAltitude),str(self._PreviousCompassHeading),str(self._PreviousDroneTargetHoldTime),str(CurrentGPSReceivedtime))           
                        self._PreviousLatitude = DroneInfoData.Latitude
                        self._PreviousLongitude = DroneInfoData.Longitude
                        self._PreviousAltitude = DroneInfoData.Altitude
                        self._PreviousBaroAltitude = DroneInfoData.BaroAltitude
                        if self._simulation:
                            self._PreviousDroneTargetHoldTime = DroneInfoData.TargetHoldTime
                            self._PreviousCompassHeading = DroneInfoData.CompassHeading
                    if self._CaptureFrameandAddtoQueue :
                        if not self._interpolation:
                            if self._FlirAttached and not self._addsynthethicimage:
                                FrameGrabbingSuccessFlag, Frame = FlirVideoSource.read()
                            else :
                                Frame = np.random.randint(0,255,size = (self._synthethic_image_res_y,self._synthethic_image_res_x,3)).astype(np.uint8)
                            CurrentDroneInfoDict = {}
                            CurrentDroneInfoDict['Latitude'] = self._PreviousLatitude
                            CurrentDroneInfoDict['Longitude'] = self._PreviousLongitude
                            CurrentDroneInfoDict['Altitude'] = self._PreviousAltitude
                            CurrentDroneInfoDict['BaroAltitude'] = self._PreviousBaroAltitude
                            CurrentDroneInfoDict['TargetHoldTime'] = self._PreviousDroneTargetHoldTime
                            CurrentDroneInfoDict['CompassHeading'] = self._PreviousCompassHeading
                            CurrentDroneInfoDict['Image'] = Frame
                            CurrentGPSInfoQueue.put(CurrentDroneInfoDict)
                        else :
                            if not FrameQueue.empty():
                                FrameBundle = FrameQueue.get()
                                if len(self._GPSTimeList) > 1:
                                    FrameTimeList = FrameBundle['FrameTimes']
                                    FrameList = FrameBundle['Frames']
                                    self._queueLog.debug('No of Frames %s %s %s %s %s', str(len(FrameTimeList)),str(len(self._CurrentFrameTimeList)),str(FrameTimeList[0]),str(FrameTimeList[-1]),str(CurrentGPSReceivedtime))
                                    #t1_start = time.perf_counter()
                                    for i in range(len(FrameTimeList)):
                                        if FrameTimeList[i] > self._GPSTimeList[-1]:
                                            if self._extrapolate:
                                                self._CurrentFrameTimeList.append(FrameTimeList[i])
                                                self._CurrentFrameList.append(FrameList[i])
                                            else:
                                                self._NextFrameTimeList.append(FrameTimeList[i])
                                                self._NextFrameList.append(FrameList[i])
                                        else:
                                            self._CurrentFrameTimeList.append(FrameTimeList[i])
                                            self._CurrentFrameList.append(FrameList[i])
                                    if not self._extrapolate :
                                        FrameInterpolatedLatList = np.interp(self._CurrentFrameTimeList, self._GPSTimeList, self._GPSLatList)
                                        FrameInterpolatedLonList = np.interp(self._CurrentFrameTimeList, self._GPSTimeList, self._GPSLonList)
                                        FrameLatInterpolatedAltList = np.interp(self._CurrentFrameTimeList, self._GPSTimeList, self._GPSAltList)
                                        FrameLatInterpolatedCompList = np.interp(self._CurrentFrameTimeList, self._GPSTimeList, self._GPSCompList) 
                                    else :
                                        InterpolatedLatFunction = InterpolatedUnivariateSpline(self._GPSTimeList, self._GPSLatList, k=self._order)
                                        InterpolatedLonFunction = InterpolatedUnivariateSpline(self._GPSTimeList, self._GPSLonList, k=self._order)
                                        InterpolatedAltFunction = InterpolatedUnivariateSpline(self._GPSTimeList, self._GPSAltList, k=self._order)
                                        InterpolatedCompFunction = InterpolatedUnivariateSpline(self._GPSTimeList, self._GPSCompList, k=self._order)
                                        FrameInterpolatedLatList = InterpolatedLatFunction(self._CurrentFrameTimeList)
                                        FrameInterpolatedLonList = InterpolatedLonFunction(self._CurrentFrameTimeList)
                                        FrameLatInterpolatedAltList = InterpolatedAltFunction(self._CurrentFrameTimeList)
                                        FrameLatInterpolatedCompList = InterpolatedCompFunction(self._CurrentFrameTimeList)
                                    for i in range(len(self._CurrentFrameList)) :
                                        CurrentDroneInfoDict = {}
                                        CurrentDroneInfoDict['Latitude'] = FrameInterpolatedLatList[i]
                                        CurrentDroneInfoDict['Longitude'] = FrameInterpolatedLonList[i]
                                        CurrentDroneInfoDict['Altitude'] = self._PreviousAltitude
                                        CurrentDroneInfoDict['BaroAltitude'] = FrameLatInterpolatedAltList[i]
                                        CurrentDroneInfoDict['TargetHoldTime'] = self._PreviousDroneTargetHoldTime
                                        CurrentDroneInfoDict['CompassHeading'] = FrameLatInterpolatedCompList[i]
                                        CurrentDroneInfoDict['Image'] = self._CurrentFrameList[i]
                                        CurrentGPSInfoQueue.put(CurrentDroneInfoDict)
                                        self._queueLog.debug('%s %s %s %s %s %s', str(CurrentDroneInfoDict['Latitude']),str(CurrentDroneInfoDict['Longitude']),str(CurrentDroneInfoDict['BaroAltitude']),str(CurrentDroneInfoDict['CompassHeading']),str(CurrentDroneInfoDict['TargetHoldTime']),str(self._CurrentFrameTimeList[i]))
                                    FrameInterpolatedLatList = []
                                    FrameInterpolatedLonList = []
                                    FrameLatInterpolatedAltList = []
                                    FrameLatInterpolatedCompList = [] 
                                    self._CurrentFrameTimeList = []
                                    self._CurrentFrameList = []
                                    if not self._extrapolate:
                                        self._CurrentFrameTimeList.extend(self._NextFrameTimeList)
                                        self._CurrentFrameList.extend(self._NextFrameList)
                                    self._NextFrameTimeList = []
                                    self._NextFrameList = []
        if self._FlirAttached and not self._addsynthethicimage:
            FlirVideoSource.release()
        print('Drone Communication Halted and First Process Terminated')
##############################################################################
if __name__ == '__main__':
    out_folder = 'Communication_results'
    if not os.path.isdir( out_folder ): 
        os.mkdir( out_folder)
    MainLog = setup_logger( 'MainLogger', os.path.join( out_folder, 'MainTest.log') )

    CurrentGPSInfoQueue = multiprocessing.Queue(maxsize=100)
    SendWayPointInfoQueue = multiprocessing.Queue(maxsize=100)
    CurrentGPSInfoQueueEventQueue = multiprocessing.Queue(maxsize=100)
    FrameQueue = multiprocessing.Queue(maxsize=200)

    DroneProcessEvent = multiprocessing.Event()
    CameraProcessEvent = multiprocessing.Event()
    GetFramesEvent = multiprocessing.Event()

    GPSReceivedLogFile = 'D:\\RESILIO\\ANAOS\\SITES\\TestFrameGrab_20210201_Openfield_T3\\GPSReceivedLogFile.log'
    GPSlogFileInfo = ReadGPSReceivedLogFiles(GPSReceivedLogFile)

    CameraClass = CameraControl(FlirAttached=False, AddsynthethicImage=True, out_folder = out_folder)
    
    DroneComm = DroneCommunication(simulate=True, GPSLog=GPSlogFileInfo, interpolation=True,extrapolate=False, AddSynthethicImage=False,FlirAttached = False,
                                                 out_folder = out_folder)
   
    #DroneComm = DroneCommunication(True,GPSlogFileInfo,True)
    CurrentGPSInfoQueueEventQueue.put(True)
    TakeImages = True 
    CurrentGPSInfoQueueEventQueue.put(TakeImages)
    GPSCount = 0
    #Look into Multi Producer -- Multi Consumer Queue Threads
    processes = []
    CameraAcquireFramesProcess =  multiprocessing.Process(name = 'CameraAcquireFramesProcess', target=CameraClass.AcquireFrames, args=(FrameQueue, CameraProcessEvent, GetFramesEvent))
    

    DroneCommunicationProcess = multiprocessing.Process(name = 'DroneCommunicationProcess', target=DroneComm.DroneInfo, args=(CurrentGPSInfoQueue,SendWayPointInfoQueue,CurrentGPSInfoQueueEventQueue, DroneProcessEvent, FrameQueue, GetFramesEvent))

    processes.append(CameraAcquireFramesProcess)
    processes.append(DroneCommunicationProcess)
    CameraAcquireFramesProcess.start()
    DroneCommunicationProcess.start()
     
    while GPSCount <= 1000 or not CurrentGPSInfoQueue.empty() :
        GPSCount = GPSCount + 1
        #if GPSCount % 20 == 0:
            #TakeImages = not(TakeImages)
            #print(TakeImages)
            #CurrentGPSInfoQueueEventQueue.put(TakeImages)
        if not CurrentGPSInfoQueue.empty():
            ReceivedCurrentDroneData = CurrentGPSInfoQueue.get()
            MainLog.debug('%s %s %s %s %s', str(ReceivedCurrentDroneData['Latitude']),str(ReceivedCurrentDroneData['Longitude']),str(ReceivedCurrentDroneData['BaroAltitude']),str(ReceivedCurrentDroneData['CompassHeading']),str(ReceivedCurrentDroneData['TargetHoldTime']))
            #Image = ReceivedCurrentDroneData['Image']
            #if Image is not None:
            #    filename = os.path.join(out_folder,str(GPSCount)+'.png')
            #    cv2.imwrite(filename,Image)
        time.sleep(0.01)
        if(GPSCount > 1000) :
            DroneProcessEvent.set()
    DroneProcessEvent.set()
    CameraProcessEvent.set()
    time.sleep(2)
    while not FrameQueue.empty():
        FramesInfo = FrameQueue.get()
    while not CurrentGPSInfoQueue.empty():
        FramesInfo = CurrentGPSInfoQueue.get()
    while not SendWayPointInfoQueue.empty():
        FramesInfo = SendWayPointInfoQueue.get()
    while not CurrentGPSInfoQueueEventQueue.empty():
        FramesInfo = CurrentGPSInfoQueueEventQueue.get()
    CurrentGPSInfoQueue.close()
    SendWayPointInfoQueue.close()
    CurrentGPSInfoQueueEventQueue.close()
    FrameQueue.close()
    for process in processes:
        process.join(5)
    print('CameraAcquireFramesProcess.is_alive()', CameraAcquireFramesProcess.is_alive())
    print('DroneCommunicationProcess.is_alive()', DroneCommunicationProcess.is_alive())
    if CameraAcquireFramesProcess.is_alive() :
        CameraAcquireFramesProcess.terminate()
        CameraAcquireFramesProcess.join()
    print('CameraAcquireFramesProcess.is_alive()', CameraAcquireFramesProcess.is_alive())
    if DroneCommunicationProcess.is_alive() :
        DroneCommunicationProcess.terminate()
        DroneCommunicationProcess.join()
    print('DroneCommunicationProcess.is_alive()', DroneCommunicationProcess.is_alive())
    print('All Process Done')
        
