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
from utils import createviewmateuler,FindStartingHeight, upload_images, upload_detectionlabels, create_dummylocation_id, upload_images_was, create_dummylocation_id_was
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
        self._sessiion = aiohttp.ClientSession()
    async def dummy_individualimage(self,imagename):
        image = cv2.imread(imagename)
        generatedviewmatrix = np.zeros((3,4))
        image_id = await upload_images(self._serveradd, image, generatedviewmatrix, self._location_id, poses = None)
        print('individual image id', image_id)
        return image_id

    def dummy_individualimage_was(self,imagename):
        image = cv2.imread(imagename)
        generatedviewmatrix = np.zeros((3,4))
        image_id = upload_images_was(self._serveradd, image, generatedviewmatrix, self._location_id, poses = None)
        print('individual image id', image_id)
        return image_id

    async def dummy_integralimages(self,renderedimagelist, individualimagelist, detectevent):
        count = 0
        print('start Function')
        await create_dummylocation_id(self._serveradd, self._location_id)
        while not detectevent.is_set():
            print('start uploading')
            ref_image_id = await self.dummy_individualimage(individualimagelist[count])
            RenderedImage = cv2.imread(renderedimagelist[count])
            viewmat = np.zeros((3,4))
            print('start uploading integral')
            image_id = await upload_images(self._serveradd, RenderedImage, viewmat, self._location_id, poses = [ref_image_id])
            print(image_id)
            time.sleep(0.4)
            count = count + 1

    def dummy_integralimages_was(self,renderedimagelist, individualimagelist, detectevent):
        count = 0
        print('start Function')
        create_dummylocation_id_was(self._serveradd, self._location_id)
        while not detectevent.is_set():
            print('start uploading')
            ref_image_id = self.dummy_individualimage_was(individualimagelist[count])
            RenderedImage = cv2.imread(renderedimagelist[count])
            viewmat = np.zeros((3,4))
            print('start uploading integral')
            image_id = upload_images_was(self._serveradd, RenderedImage, viewmat, self._location_id, poses = [ref_image_id])
            print(image_id)
            time.sleep(0.4)
            count = count + 1

    def dummy_run(self,renderedimagelist, individualimagelist, detectevent):
        self.dummy_integralimages_was(renderedimagelist, individualimagelist, detectevent)
        #loop = asyncio.get_event_loop()
        #loop.run_until_complete(self.dummy_integralimages(renderedimagelist, individualimagelist, detectevent))
        #asyncio.run(self.dummy_integralimages(renderedimagelist, individualimagelist, detectevent))
                                    

if __name__ == '__main__':
    
    sitename = 'open_field'
       
    #anaos_path = os.environ.get('ANAOS_DATA')
    ##Testing Server
    base_url1 = 'http://localhost:8080'
    base_url = 'http://localhost:8080/'
    locationid = "open_field"
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

    time.sleep(50000)

    detectevent.set()
    print('separateprocess.is_alive()', separateprocess.is_alive())
    separateprocess.join(5)
    print('separateprocess.is_alive()', separateprocess.is_alive())
    if separateprocess.is_alive() :
        separateprocess.terminate()
        separateprocess.join()
    print('separateprocess.is_alive()', separateprocess.is_alive())
    print('All Process Done')

    