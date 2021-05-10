import multiprocessing
import time
import cv2
import os
from Camera import CameraControl
from Undistort import Undistort

if __name__ == '__main__':  
    #set up a queue and events to communicate with the camera process
    frame_queue, camera_process_event, get_frames_event = multiprocessing.Queue(maxsize=1000), multiprocessing.Event(), multiprocessing.Event()

    # init a camera class
    camera_class = CameraControl(FlirAttached=False,AddsynthethicImage=True)

    # init the undistortion class
    ud = Undistort()

    #start the camera_process as a separate process
    camera_process = multiprocessing.Process(name = 'camera_process',target=camera_class.AcquireFrames, args=(frame_queue, camera_process_event, get_frames_event))
    camera_process.start()

    time.sleep(1) #wait some time 
    
    # Start recording by sending an event signal 
    get_frames_event.set()

    time.sleep(0.02)
    
    # Retrieve recorded frames
    frames_info = frame_queue.get()
    # frames_info is dictionary of the form { 'Frames': [img1, img2, ...] 'FrameTimes': [time1, time2, ...] }
    times = frames_info['FrameTimes']
    
    count = 0 
    for image in frames_info['Frames']:
        count += 1
        im = ud.undistort( image )
        cv2.imshow('undistorted image {} (time: {:.1f})'.format(count, times[count-1]),im)
    
   

    # Stop recording by sending an event
    camera_process_event.set()

    while not frame_queue.empty():
        print( 'This should not happen!?' )
        frames_info_dummy = frame_queue.get()

    # cleanup
    frame_queue.close()
    camera_process.join(5) 
    if camera_process.is_alive() :
        camera_process.terminate()


    # wait for keyboard to show images
    cv2.waitKey(0) 