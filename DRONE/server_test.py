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
from utils import createviewmateuler,FindStartingHeight, upload_images, upload_detectionlabels
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
class Dummy :
    _serveradd = None
    _location_id = None

    def __init__(self, serveraddress, locationid):
        self._serveradd = serveraddress
        self._location_id = locationid 
    async def dummy_individualimage(self,imagename):
        print('new image')
        image = cv2.imread(imagename)
        generatedviewmatrix = np.zeros((3,4))
        image_id = await upload_images(self._serveradd, image, generatedviewmatrix, self._location_id, poses = None)
        print(image_id)

    async def dummy_integralimages(self,renderedimagelist, individualimagelist, detectevent):
        count = 0
        print('start Function')
        while not detectevent.is_set():
            print('start uploading')
            await self.dummy_individualimage(individualimagelist[count])
            RenderedImage = cv2.imread(renderedimagelist[count])
            viewmat = np.zeros((3,4))
            print('start uploading integral')
            image_id = await upload_images(self._serveradd, RenderedImage, viewmat, self._location_id, poses = individualimagelist)
            print(image_id)
            time.sleep(0.4)
            count = count + 1
        
    def dummy_run(self,renderedimagelist, individualimagelist, detectevent):
        asyncio.run(self.dummy_integralimages(renderedimagelist, individualimagelist, detectevent))
                                    



if __name__ == '__main__':
    
    sitename = 'test_open_field_adaptive_simulate'
       
    #anaos_path = os.environ.get('ANAOS_DATA')
    ##Testing Server
    base_url1 = 'http://localhost:8080'
    base_url = 'http://localhost:8080/'
    locationid = "test_open_field_adaptive_simulate"
     ##Testing Server

    basedatapath = Path(__file__).resolve().parent
    individualImageLocation = os.path.join(basedatapath, '..', 'data',sitename, 'images')
    integralImageLocation = os.path.join(basedatapath, '..', 'data',sitename, 'testresults')
    individualimagelist = [x for x in glob.glob(os.path.join(individualImageLocation,'*.png'))]
    integralimagelist = [x for x in glob.glob(os.path.join(integralImageLocation,'*.png'))]
    #print(individualimagelist)
    #print(integralimagelist)
    detectevent = multiprocessing.Event()

    DummyClass = Dummy(serveraddress=base_url1,locationid=locationid)

    separateprocess = multiprocessing.Process(name = 'RenderProcess', target=DummyClass.dummy_run, args=(integralimagelist, individualimagelist, detectevent,))
    separateprocess.start()

    time.sleep(5)

    detectevent.set()
    print('separateprocess.is_alive()', separateprocess.is_alive())
    separateprocess.join(5)
    print('separateprocess.is_alive()', separateprocess.is_alive())
    if separateprocess.is_alive() :
        separateprocess.terminate()
        separateprocess.join()
    print('separateprocess.is_alive()', separateprocess.is_alive())
    print('All Process Done')

    