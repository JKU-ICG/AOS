import time
import ctypes as ct
import shutil
import os
import glob
import numpy as np
import math
import logging
import glm
import json
import cv2
import utm
import statistics
import random
from PIL import Image
#import png
from pathlib import Path
import sys

import asyncio
import aiohttp
import aiofiles


# to find the local modules we need to add the folders to sys.path
cur_file_path = Path(__file__).resolve().parent
sys.path.insert(1, cur_file_path )
sys.path.insert(1, os.path.join(cur_file_path, '..', 'PLAN') )
sys.path.insert(1, os.path.join(cur_file_path, '..', 'DET') )
sys.path.insert(1, os.path.join(cur_file_path, '..', 'CAM') )
sys.path.insert(1, os.path.join(cur_file_path, '..', 'LFR', 'python') )

import pyaos
detection = False
if detection :
    from detector import Detector
from matplotlib import pyplot as plt
from utils import createviewmateuler,FindStartingHeight, upload_images, upload_detectionlabels, create_dummylocation_id, upload_images_was, create_dummylocation_id_was,upload_dummylocation_id_was,upload_detectionlabels_was
from LFR_utils import read_poses_and_images, pose_to_virtualcamera, init_aos, init_window
from Undistort import Undistort
import multiprocessing

#Debug -- Test Planner Update Pipeline
test_planner = True
if test_planner:
    from Planner import Planner


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

class ServerUpload :
    _serveradd = None
    _location_id = None

    def __init__(self, serveraddress, locationid):
        self._serveradd = serveraddress
        self._location_id = locationid 
        self._sessiion = None
        self._ImageIDList = []

    async def server_upload(self, UploadQueue, upload_complete_event):
        print('start Upload')
        async with aiohttp.ClientSession() as session:
            print('start uploading')
            await upload_dummylocation_id_was(session, self._serveradd, self._location_id)
            time.sleep(1.0)
            while not upload_complete_event.is_set():
                while not UploadQueue.empty():
                    if not UploadQueue.empty():
                        UploadInfo = UploadQueue.get()
                        ImageList = UploadInfo['Individual_ImageList']
                        ViewMatrixList = UploadInfo['Individual_ViewMat']
                        IntegralImage = UploadInfo['IntegralImage']
                        IntegralViewMatrix = UploadInfo['IntegralImage_ViewMat']
                        Labels = UploadInfo['Labels']
                        Image_IDList = await asyncio.gather(*[upload_images_was(session,self._serveradd, image, mat, self._location_id, poses = None) for image, mat in zip(ImageList, ViewMatrixList)])
                        if len(Image_IDList):
                            self._ImageIDList.extend(Image_IDList)
                            IntegralImageList = self._ImageIDList[min(0,len(self._ImageIDList)-30):len(self._ImageIDList)-1]
                            await upload_images_was(session, self._serveradd, IntegralImage, IntegralViewMatrix, self._location_id, poses = IntegralImageList)
                        if len(Labels):
                            await upload_detectionlabels_was(session, self._serveradd,self._location_id,Labels)
            print('Upload Thread Finished ---Finished Uploading to Server')                

    def dummy_run(self,UploadQueue, upload_complete_event):
        #self.dummy_integralimages_was(renderedimagelist, individualimagelist, detectevent)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.server_upload(UploadQueue, upload_complete_event))
        #asyncio.run(self.dummy_integralimages(renderedimagelist, individualimagelist, detectevent))

if __name__ == '__main__':
    sitename = 'open_field'
       
    #anaos_path = os.environ.get('ANAOS_DATA')
    ##Testing Server
    base_url1 = 'http://140.78.99.183:80'
    base_url = 'http://localhost:8080/'
    locationid = "open_field"
    basedatapath = Path(__file__).resolve().parent
    ImageLocation = os.path.join(basedatapath, '..', 'data',sitename, 'images')
    ObjModelPath = os.path.join(basedatapath, '..', 'data',sitename, 'DEM','dem.obj')
    ObjModelImagePath = os.path.join(basedatapath,'..', 'data', sitename, 'DEM','dem.png')
    DemInfoJSOn = os.path.join(basedatapath, '..', 'data',sitename, 'DEM','dem_info.json')
    GpsLogFile = os.path.join(basedatapath, '..', 'data',sitename, 'log','GPSLog.log')

    uploadQueue = multiprocessing.Queue(maxsize=100)
    upload_complete_event = multiprocessing.Event()

    ###Testing Server
    serverclass = ServerUpload(serveraddress=base_url1,locationid= locationid)
    uploadprocess = multiprocessing.Process(name = 'uploadprocess', target=serverclass.dummy_run, args=(uploadQueue, upload_complete_event))

    uploadprocess.start()

    individualImageLocation = os.path.join(basedatapath, '..', 'data',sitename, 'images')
    integralImageLocation = os.path.join(basedatapath, '..', 'data',sitename, 'testresults')
    individualimagelist = [x for x in glob.glob(os.path.join(individualImageLocation,'*.png'))]
    integralimagelist = [x for x in glob.glob(os.path.join(integralImageLocation,'*.png'))]
    ImageList = []
    ViewMatList = []
    IntegralImageCount= 0
    for i in range(len(individualimagelist)):
        IndividualImage = cv2.imread(individualimagelist[i])
        viewmat = np.zeros((3,4))
        ImageList.append(IndividualImage)
        ViewMatList.append(viewmat)
        if i % 5 == 0:
            integralImage = cv2.imread(integralimagelist[IntegralImageCount])
            integralimagemat = np.zeros((3,4))
            IntegralImageCount = IntegralImageCount + 1
            uploadinfo = {}
            uploadinfo['Individual_ImageList'] = ImageList
            uploadinfo['Individual_ViewMat'] = ViewMatList
            uploadinfo['IntegralImage'] = integralImage
            uploadinfo['IntegralImage_ViewMat'] = integralimagemat
            uploadinfo['Labels'] = []
            uploadQueue.put(uploadinfo)
            time.sleep(0.5)
            ImageList = []
            ViewMatList = []

    upload_complete_event.set()
    print('uploadprocess.is_alive()', uploadprocess.is_alive())
    uploadprocess.join(5)
    print('uploadprocess.is_alive()', uploadprocess.is_alive())
    if uploadprocess.is_alive() :
        uploadprocess.terminate()
        uploadprocess.join()
    print('uploadprocess.is_alive()', uploadprocess.is_alive())
    print('All Process Done')
