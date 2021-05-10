import multiprocessing
import time
import cv2
import os
from Camera import CameraControl
from Undistort import Undistort

if __name__ == '__main__':  
    #set up a queue to communicate data with the camera process
    frame_queue = multiprocessing.Queue(maxsize=1000)

    #set up an event to let camera process know when to stop acquriring samples for AOS
    camera_process_event = multiprocessing.Event()

    #set up an event to let camera process know to put the acquired frames into the queue
    get_frames_event = multiprocessing.Event()

    #folder to save output results
    #out_folder = os.path.join( Path(__file__).parent.absolute(), '..',  'data', 'open_field', 'images' )

    #set up a camera class
    camera_class = CameraControl(cropImage=None, FlirAttached=False,AddsynthethicImage=True)

    #set up undistortion class
    ud = Undistort()

    #start the camera_process as a separate process
    camera_process = multiprocessing.Process(name = 'camera_process',target=camera_class.AcquireFrames, args=(frame_queue, camera_process_event, get_frames_event))

    #start the camera_process
    camera_process.start()

    #wait for certain time 
    time.sleep(1)
    
    #send an event signal to let camera_process know that acquired samples need to be put in queue
    get_frames_event.set()

    time.sleep(0.02)
    frames_info = frame_queue.get()
     
    for image in frames_info['FrameTimes']:
        im = ud.undistort( image )
        cv2.imshow('undistorted_image',im)
        cv2.waitKey(0)

    camera_process_event.set()
    while not frame_queue.empty():
        frames_info_dummy = frame_queue.get()
    frame_queue.close()
    camera_process.join(5) 
    if camera_process.is_alive() :
        camera_process.terminate()