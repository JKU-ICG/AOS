import time
import ctypes as ct
import shutil
import os
import glob
import numpy as np
import math
import cv2
import utm
import logging
import random
import statistics
import multiprocessing
from datetime import datetime, timezone

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

class CameraControl :
    _cropImage = None
    _FlirVideoSource = None
    _cameraIndex = 0
    _FlirAttached = True
    _addsynthethicimage = False
    _FrameList = []
    _FrameTimeList = []
    _image_res_y = 480
    _image_res_x = 640
    _log = None
    

    def __init__(self, cropImage = None, cropimageflag = False, FlirAttached = True, AddsynthethicImage = False, out_folder='CameraFrame_results', cameraindex = 0, desiredresx = 640, desiredresy = 480):
        self._cropImage = cropImage
        self._cropImageFlag = cropimageflag
        self._cameraIndex = cameraindex
        self._FlirAttached =FlirAttached
        self._addsynthethicimage =AddsynthethicImage
        self._image_res_y = desiredresy
        self._image_res_x = desiredresx
        if not os.path.isdir( out_folder ): 
            os.mkdir( out_folder)
        self._out_folder = out_folder
        if not self._addsynthethicimage:
            self._FlirVideoSource = cv2.VideoCapture(self._cameraIndex)
            OldHeight = self._FlirVideoSource.get(3)
            OldWidth = self._FlirVideoSource.get(4)
            returnedflag = self._FlirVideoSource.set(3,self._image_res_x)
            returnedflag =self._FlirVideoSource.set(4,self._image_res_y)
            NewHeight = self._FlirVideoSource.get(3)
            NewWidth = self._FlirVideoSource.get(4)
            print('Height',NewHeight,'Width',NewWidth)
    
    def AcquireFrames(self, FrameQueue, CameraProcessEvent, GetFramesEvent):
        """Blocking function that records and provides frames based on events. 
            It is intended to run with threading or multiprocessing

        :param FrameQueue: queue which stores recorded frames and corresponding timings.  
            reading with `FrameQueue.get()` returns a dictionary of the form 
            `{ 'Frames': [img1, img2, ...], 'FrameTimes': [time1, time2, ...] }`
            
        :type FrameQueue: `multiprocessing.Queue` or `threading.Queue`
        :param CameraProcessEvent: if you want to stop recording (exit the infinite loop) `CameraProcessEvent.set()`
        :type CameraProcessEvent: `multiprocessing.Event` or `threading.Event`
        :param GetFramesEvent: if you want to get frames captured till now use `GetFramsEvent.set()`
        :type GetFramesEvent: `multiprocessing.Event` or `threading.Event`
        """
        self._log = setup_logger( 'CameraInterpolation_Logger', os.path.join( self._out_folder, 'CameraFrameCapturedLog.log') )
        while not CameraProcessEvent.is_set():
            if self._FlirAttached and not self._addsynthethicimage:
                FrameGrabbingSuccessFlag, Frame = self._FlirVideoSource.read()
                CurrentFrametime = datetime.now(timezone.utc).timestamp()
                if self._cropImageFlag :
                    Framecropped = Frame[self._cropImage[0]:self._cropImage[0]+self._cropImage[2], self._cropImage[1]:self._cropImage[1]+self._cropImage[3] ]
                    self._FrameList.append(Framecropped)
                else :
                    self._FrameList.append(Frame)
                self._FrameTimeList.append(CurrentFrametime)
                self._log.debug('%s', str(CurrentFrametime))
            else :
                time.sleep(0.03)
                Frame = np.random.randint(0,255,size = (self._image_res_y,self._image_res_x,3)).astype(np.uint8)
                CurrentFrametime = datetime.now(timezone.utc).timestamp()
                self._FrameList.append(Frame)
                self._FrameTimeList.append(CurrentFrametime)
                self._log.debug('%s', str(CurrentFrametime))
            if GetFramesEvent.is_set():
                FrameBundle = {}
                FrameBundle['Frames'] = self._FrameList
                FrameBundle['FrameTimes'] = self._FrameTimeList
                self._log.debug('Added %s', str(len(self._FrameTimeList)))
                FrameQueue.put(FrameBundle)
                self._FrameList = []
                self._FrameTimeList = []
                GetFramesEvent.clear()
        if self._FlirAttached and not self._addsynthethicimage:
            self._FlirVideoSource.release()
        print('CameraProcessEvent is set')
        self._FrameList = []
        self._FrameTimeList = []

if __name__ == '__main__':
    """ Exemplary usage of the CameraControl unit. It records frames for 50 seconds in a dictionary every .2 seconds
    """
    out_folder = 'CameraControl_Results'
    if not os.path.isdir( out_folder ): 
        os.mkdir( out_folder)
    MainLog = setup_logger( 'MainLogger', os.path.join( out_folder, 'MainTest.log') )
    
    FrameQueue = multiprocessing.Queue(maxsize=100)
    CameraProcessEvent = multiprocessing.Event()
    GetFramesEvent = multiprocessing.Event()

    CameraClass = CameraControl(cropImage=None, FlirAttached=False,AddsynthethicImage=True,out_folder = out_folder)
    
    CameraAcquireFramesProcess = multiprocessing.Process(name = 'CameraAcquireFramesProcess',target=CameraClass.AcquireFrames, args=(FrameQueue, CameraProcessEvent, GetFramesEvent))
    StartCameraProcessTime = datetime.now(timezone.utc).timestamp()
    print(StartCameraProcessTime)
    print('CameraAcquireFramesProcess will run for 50 seconds ... ')

    CameraAcquireFramesProcess.start()
    ####Checking FPS without interrupting with event at regular intervals
    ####Checking FPS with interrupting with event at regular intervals
    CurrentTime = datetime.now(timezone.utc).timestamp()
    while abs(CurrentTime - StartCameraProcessTime) < 50 :
        MainLog.debug(' Time Difference %s',str(abs(CurrentTime - StartCameraProcessTime)))
        time.sleep(0.2)
        GetFramesEvent.set()
        time.sleep(0.02)
        if not FrameQueue.empty():
            FramesInfo = FrameQueue.get()
            MainLog.debug('Len of Frame List %s',str(len(FramesInfo['FrameTimes'])))
            FrameTimeList = FramesInfo['FrameTimes']
            TimeDifferencebetweenFrames = []
            for i in range(len(FramesInfo['FrameTimes']) - 1):
                #print(i,FrameTimeList[i])
                TimeDifferencebetweenFrames.append(abs(FrameTimeList[i] - FrameTimeList[i+1]))
            if len(TimeDifferencebetweenFrames) > 1:
                MainLog.debug('%s',str(len(FramesInfo['FrameTimes'])))
                MainLog.debug('Minimum Time Difference between frames %s',str( min(TimeDifferencebetweenFrames)))
                MainLog.debug('Maximum Time Difference between frames %s',str(max(TimeDifferencebetweenFrames)))
                MainLog.debug('Mean Time Difference between frames %s',str(np.array(TimeDifferencebetweenFrames).mean()))
                MainLog.debug('Meadian Time Difference between frames %s',str(statistics.median(np.array(TimeDifferencebetweenFrames))))
        CurrentTime = datetime.now(timezone.utc).timestamp()
    print('50 Seconds Done and CameraAcquireFramesProcess is alive', CameraAcquireFramesProcess.is_alive())
    CameraProcessEvent.set()
    time.sleep(2)
    while not FrameQueue.empty():
        FramesInfo = FrameQueue.get()
    FrameQueue.close()
    print('CameraAcquireFramesProcess.is_alive()', CameraAcquireFramesProcess.is_alive())
    CameraAcquireFramesProcess.join(5)
    print('CameraAcquireFramesProcess.is_alive()', CameraAcquireFramesProcess.is_alive())
    if CameraAcquireFramesProcess.is_alive() :
        CameraAcquireFramesProcess.terminate()
    CameraAcquireFramesProcess.join()
    print('CameraAcquireFramesProcess.is_alive()', CameraAcquireFramesProcess.is_alive())
    print('All Process Done')
    