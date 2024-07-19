# reqired libraries
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import json
import numpy as np
import cv2
import time
import matplotlib as plt
import math
import matplotlib.pyplot as plt
import logging
import base64
import math
import subprocess
import json
import ds_wrapper as w
import keyboard
from paho.mqtt import client as mqtt_client
import logging
import json
import base64
import math
import threading
import os

###################################### Parameters to be set ###############################################

decode = w.isHWDecoderEnabled()

if decode == 1:
    decoding = 'hardware'
elif decode == 0:
    decoding = 'software'
else:
    print('Invalid decoding method')

drone_1_incrementor  = 1
drone_2_incrementor  = 1
drone_3_incrementor  = 1
drone_4_incrementor  = 1
drone_5_incrementor  = 1
drone_6_incrementor  = 1
drone_7_incrementor  = 1
drone_8_incrementor  = 1
drone_9_incrementor  = 1
drone_10_incrementor = 1


drone1_waypoint_no  = 0
drone2_waypoint_no  = 0
drone3_waypoint_no  = 0
drone4_waypoint_no  = 0
drone5_waypoint_no  = 0
drone6_waypoint_no  = 0
drone7_waypoint_no  = 0
drone8_waypoint_no  = 0
drone9_waypoint_no  = 0
drone10_waypoint_no = 0


lock = threading.Lock()

debug = False
crop_size = 1080  # original size of image is 1920x1080

# new = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) # Get the current time as string
# os.mkdir(r"Result" + new) # Add a separator between the download location and the new folder name
#  # Create a folder to store the results
# Download_Location = r"Result" + new # Location to store the results
# os.mkdir(Download_Location + '/images') # Create a folder to store the images
# Images_Path = os.path.join(Download_Location,'images')

Way_threshold  = 2 # treshold for the waypoints


key_pressed = {'t': False, 'l': False, 'w': False, 'i': False, 'q': False} # Dictionary to keep track of key press status (# t for takeoff, l to land, w to start waypoint mission, i to emergency, q to quit)
key_pressed_emergency = {'i': False} # Variable to keep track of emergency key press status

drone_speed = 2 # The speed of the drone in m/s, this will be used while taking of and landing

global action_in_progress,  waypoint_confirmation
action_in_progress = False
task = ''
waypoint_confirmation = False
num_drones_for_map_visualization = 10
drones = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] 
connected_drones = [] # List to store the connected drones

####################### MQTT configurations ############################

broker = "localhost"
port = 9001
topic = "drone"
username = 'user'
password = 'user'

# dronedata
droneContent = """
    <div class="mp-0">
    <div class="mp-0">
        {telemetrydata}
    </div>
    <img class="droneImage-tooltip" src="data:image/gif;base64,{img_base64}">
    </div>
"""

stop_mqtt = False # Flag to stop the mqtt client

client_list_mqtt = [] # list to store the mqtt clients

# Function to connect to MQTT broker
def connect_mqtt(broker, port, topic, client_id, username, password):
    def on_connect(client, userdata, flags, rc):
        # not equal to 0 means connection failed	
        if rc != 0:
            print(f"Failed to connect, return code {rc}\n")

    client = mqtt_client.Client(client_id, transport="websockets")
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

# Constants for reconnecting
FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

# Function to handle disconnection and reconnection
def on_disconnect(client, userdata, rc):
    logging.info("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        logging.info("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)
        try:
            client.reconnect()
            logging.info("Reconnected successfully!")
            return
        except Exception as err:
            logging.error("%s. Reconnect failed. Retrying...", err)
        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1
    logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)

# Function to publish the data to MQTT broker for each drone
def publisher_thread(broker, port, topic, username, password):
    
    global stop_mqtt
    time_lists = []
    if num_drones_for_map_visualization >= 1:
        client_id1 = f'python-mqtt-{1}'
        client1 = connect_mqtt(broker, port, topic, client_id1, username, password)
        client1.on_disconnect = on_disconnect
        client_list_mqtt.append(client1)
        client1.loop_start()
        time_list_1 = []
        time_lists.append(time_list_1)
        
    if num_drones_for_map_visualization >= 2:
        client_id2 = f'python-mqtt-{2}'
        client2 = connect_mqtt(broker, port, topic, client_id2, username, password)
        client2.on_disconnect = on_disconnect
        client_list_mqtt.append(client2)
        client2.loop_start()
        time_list_2 = []
        time_lists.append(time_list_2)
    
    if num_drones_for_map_visualization >= 3:
        client_id3 = f'python-mqtt-{3}'
        client3 = connect_mqtt(broker, port, topic, client_id3, username, password)
        client3.on_disconnect = on_disconnect
        client_list_mqtt.append(client3)
        client3.loop_start()
        time_list_3 = []
        time_lists.append(time_list_3)
        
    if num_drones_for_map_visualization >= 4:
        client_id4 = f'python-mqtt-{4}'
        client4 = connect_mqtt(broker, port, topic, client_id4, username, password)
        client4.on_disconnect = on_disconnect
        client_list_mqtt.append(client4)
        client4.loop_start()
        time_list_4 = []
        time_lists.append(time_list_4)
        
    if num_drones_for_map_visualization >= 5:
        client_id5 = f'python-mqtt-{5}'
        client5 = connect_mqtt(broker, port, topic, client_id5, username, password)
        client5.on_disconnect = on_disconnect
        client_list_mqtt.append(client5)
        client5.loop_start()
        time_list_5 = []
        time_lists.append(time_list_5)
        
    if num_drones_for_map_visualization >= 6:
        client_id6 = f'python-mqtt-{6}'
        client6 = connect_mqtt(broker, port, topic, client_id6, username, password)
        client6.on_disconnect = on_disconnect
        client_list_mqtt.append(client6)
        client6.loop_start()
        time_list_6 = []
        time_lists.append(time_list_6)
        
    if num_drones_for_map_visualization >= 7:
        client_id7 = f'python-mqtt-{7}'
        client7 = connect_mqtt(broker, port, topic, client_id7, username, password)
        client7.on_disconnect = on_disconnect
        client_list_mqtt.append(client7)
        client7.loop_start()
        time_list_7 = []
        time_lists.append(time_list_7)
        
    if num_drones_for_map_visualization >= 8:
        client_id8 = f'python-mqtt-{8}'
        client8 = connect_mqtt(broker, port, topic, client_id8, username, password)
        client8.on_disconnect = on_disconnect
        client_list_mqtt.append(client8)
        client8.loop_start()
        time_list_8 = []
        time_lists.append(time_list_8)
        
    if num_drones_for_map_visualization >= 9:
        client_id9 = f'python-mqtt-{9}'
        client9 = connect_mqtt(broker, port, topic, client_id9, username, password)
        client9.on_disconnect = on_disconnect
        client_list_mqtt.append(client9)
        client9.loop_start()
        time_list_9 = []
        time_lists.append(time_list_9)
        
    if num_drones_for_map_visualization >= 10:
        client_id10 = f'python-mqtt-{10}'
        client10 = connect_mqtt(broker, port, topic, client_id10, username, password)
        client10.on_disconnect = on_disconnect
        client_list_mqtt.append(client10)
        client10.loop_start()
        time_list_10 = []
        time_lists.append(time_list_10)
    
    global drone1_waypoint_no, drone2_waypoint_no, drone3_waypoint_no, drone4_waypoint_no, drone5_waypoint_no, drone6_waypoint_no, drone7_waypoint_no, drone8_waypoint_no, drone9_waypoint_no, drone10_waypoint_no, connected_drones, drones
    while True:
        time.sleep(0.1) 
        for i in range(1, num_drones_for_map_visualization+1):
            try:
                droneId = i
                # Get the telemetry and image data from the drones
                Image_Telemetry_data = w.getImageAndTelemetryData(i)
                Telemetry_data = (bytearray(Image_Telemetry_data[3110408:]).decode())
                telemetry_elements = Telemetry_data.split(":")   # Extract all elements from the string
                
                if Telemetry_data != '':  
                    with lock:
                        for id in drones:
                            if id == droneId:
                                connected_drones.append(droneId)
                                drones.remove(droneId)
                                print('connected_drones', connected_drones)
                                print('drones', drones)
                            
                # print(telemetry_elements)
                latitude = telemetry_elements[0] 
                longitude = telemetry_elements[1]
                altitude = telemetry_elements[2]
                heading = telemetry_elements[3] 
                gimbal_pitch = telemetry_elements[4]
                gimbal_pan = telemetry_elements[5]
                gimbal_yaw = telemetry_elements[6]
                velocity_x = float(telemetry_elements[11])
                velocity_y = float(telemetry_elements[12])
                velocity_z = float(telemetry_elements[13])
                speed = math.sqrt(velocity_x**2 + velocity_y**2 + velocity_z**2)
                # map the pitch angle from (-180, 180) to (0, 360)
                if float(gimbal_yaw) < 0:
                    gimbal_yaw = float(gimbal_yaw) + 360
                else:
                    gimbal_yaw = float(gimbal_yaw)
                
                # map the heding angle from (-180, 180) to (0, 360)
                if float(heading) < 0:
                    heading = float(heading) + 360
                else:
                    heading = float(heading)
                
                # Calculate the difference
                angle_diff = gimbal_yaw - heading
                
                # Normalize the difference to the range [-180, 180]
                angle_diff = (angle_diff + 180) % 360 - 180
                
                gimbal_yaw = angle_diff
                # print(f"Drone {droneId} - Latitude: {latitude}, Longitude: {longitude}, Altitude: {altitude}, Heading: {heading}, Speed: {speed}")
                # Get the image data from the drones
                if decoding == 'software':
                    Image = cv2.cvtColor(Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV420p2RGB)   # for software decoding
                elif decoding == 'hardware':
                    Image = cv2.cvtColor(Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV2BGR_NV12) # for hardware decoding
                    
                
                with lock:
                    if i == 1:
                        drone_waypoint_no = drone1_waypoint_no
                    elif i == 2:
                        drone_waypoint_no = drone2_waypoint_no
                    elif i == 3:
                        drone_waypoint_no = drone3_waypoint_no
                    elif i == 4:
                        drone_waypoint_no = drone4_waypoint_no
                    elif i == 5:
                        drone_waypoint_no = drone5_waypoint_no
                    elif i == 6:
                        drone_waypoint_no = drone6_waypoint_no
                    elif i == 7:
                        drone_waypoint_no = drone7_waypoint_no
                    elif i == 8:
                        drone_waypoint_no = drone8_waypoint_no
                    elif i == 9:
                        drone_waypoint_no = drone9_waypoint_no
                    elif i == 10:
                        drone_waypoint_no = drone10_waypoint_no
                    else:
                        drone_waypoint_no = 0
                           
                # Convert the image to base64
                retval, buffer = cv2.imencode('.jpg', Image)
                imgBase64 = base64.b64encode(buffer).decode('utf-8')
                # telemdata = """ID: {:.0f}, ALT: {:.2f}m""".format(int(droneId), float(altitude)) 
                
                telemdata = """ID:{:.0f},Alt:{:.1f}m,Spd:{:.1f}m/s,  Com:{:.1f},Pit:{:.1f},Yaw:{:.1f},Wpt:{:.0f} """.format(int(droneId), float(altitude), speed, float(heading), float(gimbal_pitch), float(gimbal_yaw), int(drone_waypoint_no))
                
                content = droneContent.format(telemetrydata = telemdata, img_base64=imgBase64)
                msg = json.dumps({"id": droneId, "lat": latitude, "lon": longitude, "deg": heading, "content": content, "offset_x": -100, "offset_y": 0, 'colour': '#eb3434'})

                # Publish the data to the MQTT broker

                time_stamp = telemetry_elements[-1]
                time_lists[i-1].append(time_stamp)
                if len(time_lists[i-1]) > 1:
                     
                    if time_lists[i-1][-1] != time_lists[i-1][-2]:    
                        result = client_list_mqtt[i-1].publish(topic, msg)
                        status = result[0]
                        if status != 0:
                            print(f"Failed to send message to topic {topic}")
                    else:
                        continue  
                else:
                    continue 
                
            except IndexError:
                pass
                
        with lock:                 
            if stop_mqtt == True:
                if num_drones_for_map_visualization >= 1:
                    client1.loop_stop()
                    print('client1 stopped')
                if num_drones_for_map_visualization >= 2:
                    client2.loop_stop()
                    print('client2 stopped')
                if num_drones_for_map_visualization >= 3:
                    client3.loop_stop()
                    print('client3 stopped')
                if num_drones_for_map_visualization >= 4:
                    client4.loop_stop()
                    print('client4 stopped')
                if num_drones_for_map_visualization >= 5:
                    client5.loop_stop()
                    print('client5 stopped')
                if num_drones_for_map_visualization >= 6:
                    client6.loop_stop()
                    print('client6 stopped')
                if num_drones_for_map_visualization >= 7:
                    client7.loop_stop()
                    print('client7 stopped')
                if num_drones_for_map_visualization >= 8:
                    client8.loop_stop()
                    print('client8 stopped')
                if num_drones_for_map_visualization >= 9:
                    client9.loop_stop()
                    print('client9 stopped')
                if num_drones_for_map_visualization >= 10:
                    client10.loop_stop()
                    print('client10 stopped')
                break

######################## Drone 1 Thread ############################
d1Image = []
d1Poses= []

def waypoint_tread_drone1(drone1_Latitude_List, drone1_Longitude_list, drone1_Altitude_list,drone1_Heading_list,drone1_Speed_list, Way1_threshold, camera_list, lengthOfStay_list, gimbalPitch_list, gimbalYaw_list):
    # print('Waypoint latitude list for drone1:', drone1_Latitude_List)
    
    number_of_waypoints_for_drone1 = len(drone1_Latitude_List)
    print(f"Number of waypoints for drone1: {number_of_waypoints_for_drone1}")
    
    global drone_1_incrementor, task, drone1_waypoint_no
    
    incrementor = drone_1_incrementor
    
    previous_speed_list_drone1 = [drone1_Speed_list[0], *drone1_Speed_list]
    previous_heading_list_drone1 = [drone1_Heading_list[0], *drone1_Heading_list]
    previous_camera_list_drone1 = [camera_list[0], *camera_list]
    previous_lengthOfStay_list_drone1 = [lengthOfStay_list[0], *lengthOfStay_list]
    previous_gimbalPitch_list_drone1 = [gimbalPitch_list[0], *gimbalPitch_list]
    previous_gimbalYaw_list_drone1 = [gimbalYaw_list[0], *gimbalYaw_list]
    
    iteration = 0
    
    while True:
        
        ### Emergency Case ###
          
        if keyboard.is_pressed('i'):
            if not key_pressed_emergency['i']:
                print("Emergency Case")
                key_pressed_emergency['i'] = True
                with lock:
                    drone_1_incrementor = incrementor
                break
        
        with lock:
            if task == 'waypoint':
                drone1_waypoint_no = drone1_waypoint_no + 1
                print(f"Mission Waypoint {iteration+1} in progress for drone1 ...") 

                drone1_Latitude_go = drone1_Latitude_List[iteration]
                drone1_Longitude_go = drone1_Longitude_list[iteration]
                drone1_Altitude_go = drone1_Altitude_list[iteration]
                drone1_Heading_go = previous_heading_list_drone1[iteration]
                drone1_Speed_go = previous_speed_list_drone1[iteration]
                drone1_Camera_go = previous_camera_list_drone1[iteration]
                drone1_LengthOfStay_go = previous_lengthOfStay_list_drone1[iteration]
                drone1_GimbalPitch_go = previous_gimbalPitch_list_drone1[iteration]
                drone1_GimbalYaw_go = previous_gimbalYaw_list_drone1[iteration]
                
                drone1_Latitude_update = drone1_Latitude_List[iteration]
                drone1_Longitude_update = drone1_Longitude_list[iteration]
                drone1_Altitude_update = drone1_Altitude_list[iteration]
                drone1_Heading_update = drone1_Heading_list[iteration]
                drone1_Speed_update = drone1_Speed_list[iteration]
                drone1_Camera_update = camera_list[iteration]
                drone1_LengthOfStay_update = lengthOfStay_list[iteration]
                drone1_GimbalPitch_update = gimbalPitch_list[iteration]
                drone1_GimbalYaw_update = gimbalYaw_list[iteration]
                
                iteration += 1
                
            else:
                
                drone1_Latitude_go = drone1_Latitude_List[iteration]
                drone1_Longitude_go = drone1_Longitude_list[iteration]
                drone1_Altitude_go = drone1_Altitude_list[iteration]
                drone1_Heading_go = drone1_Heading_list[iteration]
                drone1_Speed_go = drone1_Speed_list[iteration]
                drone1_Camera_go = camera_list[iteration]
                drone1_LengthOfStay_go = lengthOfStay_list[iteration]
                drone1_GimbalPitch_go = gimbalPitch_list[iteration]
                drone1_GimbalYaw_go = gimbalYaw_list[iteration]
                
                drone1_Latitude_update = drone1_Latitude_List[iteration + 1]
                drone1_Longitude_update = drone1_Longitude_list[iteration + 1]
                drone1_Altitude_update = drone1_Altitude_list[iteration + 1]
                drone1_Heading_update = drone1_Heading_list[iteration + 1]
                drone1_Speed_update = drone1_Speed_list[iteration + 1]
                drone1_Camera_update = camera_list[iteration + 1]
                drone1_LengthOfStay_update = lengthOfStay_list[iteration + 1]
                drone1_GimbalPitch_update = gimbalPitch_list[iteration + 1]
                drone1_GimbalYaw_update = gimbalYaw_list[iteration + 1]
                
                iteration += 2
                
        waypointvalue1 = incrementor

        ################ for reaching the waypoint ################
        
        print("waypointvalue1_drone1(go):",waypointvalue1)
        drone1_waypoint_data_reached = f"{drone1_Latitude_go}:{drone1_Longitude_go}:{drone1_Altitude_go}:{drone1_Heading_go}:{drone1_Speed_go}:{waypointvalue1}:{Way1_threshold}:{drone1_GimbalPitch_go}:{drone1_GimbalYaw_go}:{drone1_Camera_go}"
        
        drone1_send_data = w.sendWayPointData(drone1_waypoint_data_reached, 1)     # 1 refers to the drone number
        
        drone1_waypoint_data_sent = f"Lat: {drone1_Latitude_go}, Long: {drone1_Longitude_go}, Alt: {drone1_Altitude_go}, Heading: {drone1_Heading_go}, Speed: {drone1_Speed_go}, Waypoint: {waypointvalue1}, Threshold: {Way1_threshold}, Gimbal Pitch: {drone1_GimbalPitch_go}, Gimbal Yaw: {drone1_GimbalYaw_go}, Camera: {drone1_Camera_go}"
        if debug:
            print("Data being Sent for drone1 (go):",drone1_waypoint_data_sent)
        
        ## Check if the drone has reached the waypoint, element (14) of the getImageAndTelemetryData string is set to 1. Extract the image and telemetry data when the condition is met. ## Every time the drone receive the next waypoints this element is set to zero again ion the drone app.
        ## Element 15 is to confirm that the next waypoint data has been successfully received on the app side.
        
        while True:
        
            drone1_send_data = w.sendWayPointData(drone1_waypoint_data_reached, 1) 
            drone1_Image_Telemetry_data = w.getImageAndTelemetryData(1) # 1 refers to the drone number
            drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[3110408:]).decode())
            
            drone1_elements = drone1_Telemetry_data.split(":")                 # Extract all elements from the string
            drone1_Waypoint_sent = drone1_elements[15].split('.')[0]
            # print("drone1_Waypoint_sent_for_go:",drone1_Waypoint_sent)
            if (drone1_Waypoint_sent) == str(incrementor):
                if debug: 
                    print("drone1 Waypoint data sent for go")
                    print ("go thread for drone1:", drone1_Waypoint_sent, incrementor)
                break # Exit the loop
            
        while True:
            drone1_Image_Telemetry_data = w.getImageAndTelemetryData(1)
            drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[3110408:]).decode())
            
            drone1_elements = drone1_Telemetry_data.split(":")                 # Extract all elements from the string
            drone1_Waypoint_reached = drone1_elements[14]
            
            
            if drone1_Waypoint_reached == str(incrementor):
                if debug:
                    print("drone1 Waypoint has been reached")
                    print ("go thread waypoint reached for drone1:", drone1_Waypoint_reached, incrementor)
                break # Exit the loop
        
        # Call the telemetry data again
        drone1_Image_Telemetry_data = w.getImageAndTelemetryData(1)
        drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[3110408:]).decode())
        
        drone_1_telemetry_elements = drone1_Telemetry_data.split(":")

        latitude = drone_1_telemetry_elements[0] 
        longitude = drone_1_telemetry_elements[1]
        altitude = drone_1_telemetry_elements[2]
        heading = drone_1_telemetry_elements[3]
        gimbal_pitch = drone_1_telemetry_elements[4]
        gimbal_yaw = drone_1_telemetry_elements[6]

        if debug: 
            reached_data = f"Lat_Reached: {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for drone1 (go) --->", reached_data, "\n")
            
            print("drone1_Waypointdata (go):", drone1_Telemetry_data, "\n")  
            
        if drone1_LengthOfStay_go > 0:
            time.sleep(drone1_LengthOfStay_go)   
        
        incrementor += 1
        
        ################ updating the waypoint parameters ################
        
        waypointvalue1_update = incrementor 
        print("waypointvalue1_drone1(update):",waypointvalue1_update)
        drone1_waypoint_data = f"{drone1_Latitude_update}:{drone1_Longitude_update}:{drone1_Altitude_update}:{drone1_Heading_update}:{drone1_Speed_update}:{waypointvalue1_update}:{Way1_threshold}:{drone1_GimbalPitch_update}:{drone1_GimbalYaw_update}:{drone1_Camera_update}"
        drone1_send_data = w.sendWayPointData(drone1_waypoint_data, 1)     # 1 refers to the drone number
        
        drone1_waypoint_data_sent = f"Lat: {drone1_Latitude_update}, Long: {drone1_Longitude_update}, Alt: {drone1_Altitude_update}, Heading: {drone1_Heading_update}, Speed: {drone1_Speed_update}, Waypoint: {waypointvalue1_update}, Threshold: {Way1_threshold}, Gimbal Pitch: {drone1_GimbalPitch_update}, Gimbal Yaw: {drone1_GimbalYaw_update}, Camera: {drone1_Camera_update}"
        if debug:
            print("Data Being Sent for drone1 (update) :",drone1_waypoint_data_sent, "\n")
        
        ## Check if the drone has reached the waypoint, element (14) of the getImageAndTelemetryData string is set to 1. Extract the image and telemetry data when the condition is met. ## Every time the drone receive the next waypoints this element is set to zero again ion the drone app.
        ## Element 15 is to confirm that the next waypoint data has been successfully received on the app side.
        
        while True:
        
            drone1_send_data = w.sendWayPointData(drone1_waypoint_data, 1) 
            drone1_Image_Telemetry_data = w.getImageAndTelemetryData(1) # 1 refers to the drone number
            drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[3110408:]).decode())
            
            drone1_elements = drone1_Telemetry_data.split(":")                 # Extract all elements from the string
            drone1_Waypoint_sent = drone1_elements[15].split('.')[0]

            # print("drone1_Waypoint_sent:",drone1_Waypoint_sent)
            if (drone1_Waypoint_sent) == str(incrementor):
                if debug: 
                    print("drone1 Waypoint data sent")
                    print ("run thread for drone1:", drone1_Waypoint_sent, incrementor)
                    
                break # Exit the loop
            

        while True:
            drone1_Image_Telemetry_data = w.getImageAndTelemetryData(1)
            drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[3110408:]).decode())
            
            drone1_elements = drone1_Telemetry_data.split(":")                 # Extract all elements from the string
            drone1_Waypoint_reached = drone1_elements[14]
            
            
            if drone1_Waypoint_reached == str(incrementor):
                if debug:
                    print("drone1 Waypoint has been reached")
                    print ("run thread waypoint reached:", drone1_Waypoint_reached, incrementor)
                break # Exit the loop
            
        # Hold the drone at the waypoint for a specified length of time
        if drone1_LengthOfStay_update > 0:
            print("drone1_Waypointdata_before_holding:", drone1_Telemetry_data)
        
            print(f'drone1 is waiting  for {drone1_LengthOfStay_update} sn before taking the image and saving the telemetry data')   
            time.sleep(drone1_LengthOfStay_update)  
        
        # Call the telemetry data again
        drone1_Image_Telemetry_data = w.getImageAndTelemetryData(1)
        drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[3110408:]).decode())
        
        drone_1_telemetry_elements = drone1_Telemetry_data.split(":")

        latitude = drone_1_telemetry_elements[0] 
        longitude = drone_1_telemetry_elements[1]
        altitude = drone_1_telemetry_elements[2]
        heading = drone_1_telemetry_elements[3]
        gimbal_pitch = drone_1_telemetry_elements[4]
        gimbal_yaw = drone_1_telemetry_elements[6]
        
        if debug:
            reached_data = f"Lat_Reached {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for Updating Parameter for drone1 --->",reached_data, "\n")
            
            print("drone1_Waypointdata (update):", drone1_Telemetry_data)
            
            # Save the telemetry data to a text file inside the results folder
            file_path = os.path.join(Download_Location, 'telemetry1.txt')
            with open(file_path, 'a') as file:
                file.write(drone1_Telemetry_data + '\n')
                
        ## Covert YUV raw data to rgb image and save   ##

        if decoding == 'software':
            drone1_Image = cv2.cvtColor(drone1_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV420p2RGB)
        elif decoding == 'hardware':
            drone1_Image = cv2.cvtColor(drone1_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV2BGR_NV12)
        else:
            print('Please enter a valid decoding method')
        
        
        # Calculate the center of the image
        center_x, center_y = drone1_Image.shape[1] // 2, drone1_Image.shape[0] // 2

        # Calculate the crop region
        crop_start_x = center_x - crop_size // 2
        crop_start_y = center_y - crop_size // 2

        # Crop the image
        cropped_image1 = drone1_Image[crop_start_y:crop_start_y + crop_size, crop_start_x:crop_start_x + crop_size]
        resized_image1 = cv2.resize(cropped_image1, (512, 512))

        drone1_cropped_Image = resized_image1
        
        if debug:
            waypoint_folder = f'drone1_waypoint_{incrementor}_('+ task + ')'
            waypoint_path = os.path.join(Images_Path, waypoint_folder)
            if not os.path.exists(waypoint_path):
                os.mkdir(waypoint_path)
                
            else:
                print("Folder already exists for drone1 (update)")
                
            cv2.imwrite(os.path.join( waypoint_path, 'drone1Image' + str(incrementor)+'.png'), drone1_cropped_Image)
            print("Image is taken and saved for drone1")
        
        if (len(d1Image)) >= 1:
            
            d1Image[0] = (drone1_cropped_Image)
            d1Poses[0] = (drone1_Telemetry_data)
        else:
            
            d1Image.append(drone1_cropped_Image)
            d1Poses.append(drone1_Telemetry_data)
        
        incrementor += 1
        if iteration >= number_of_waypoints_for_drone1:
            with lock:
                drone_1_incrementor = incrementor
                
            with lock:    
                if task == 'waypoint':
                    print("Mission Waypoint for drone1 completed")
                elif task == 'takeoff':
                    print("Takeoff completed for drone1")
                elif task == 'land':
                    print("Land completed for drone1")
                elif task == 'emergency':
                    print("Emergency Case")
                else:
                    print("Invalid task")
                
            break
        
######################## Drone 2 Thread ############################
d2Image = []
d2Poses= []

def waypoint_tread_drone2(drone2_Latitude_List, drone2_Longitude_list, drone2_Altitude_list, drone2_Heading_list, drone2_Speed_list, Way2_threshold, camera_list, lengthOfStay_list, gimbalPitch_list, gimbalYaw_list):
    
    number_of_waypoints_for_drone2 = len(drone2_Latitude_List)
    global drone_2_incrementor, task, drone2_waypoint_no
    
    incrementor = drone_2_incrementor
    
    previous_speed_list_drone2 = [drone2_Speed_list[0], *drone2_Speed_list]
    previous_heading_list_drone2 = [drone2_Heading_list[0], *drone2_Heading_list]
    previous_camera_list_drone2 = [camera_list[0], *camera_list]
    previous_lengthOfStay_list_drone2 = [lengthOfStay_list[0], *lengthOfStay_list]
    previous_gimbalPitch_list_drone2 = [gimbalPitch_list[0], *gimbalPitch_list]
    previous_gimbalYaw_list_drone2 = [gimbalYaw_list[0], *gimbalYaw_list]
    
    iteration = 0
    
    while True:
        
        ### Emergency Case ### 
        if keyboard.is_pressed('i'):
            if not key_pressed_emergency['i']:
                print("Emergency Case")
                key_pressed_emergency['i'] = True
                with lock:
                    drone_2_incrementor = incrementor
                break
        
        with lock:
            if task == 'waypoint':
                drone2_waypoint_no = drone2_waypoint_no + 1
                print(f"Mission Waypoint {iteration+1} in progress for drone2 ...") 

                drone2_Latitude_go = drone2_Latitude_List[iteration]
                drone2_Longitude_go = drone2_Longitude_list[iteration]
                drone2_Altitude_go = drone2_Altitude_list[iteration]
                drone2_Heading_go = previous_heading_list_drone2[iteration]
                drone2_Speed_go = previous_speed_list_drone2[iteration]
                drone2_Camera_go = previous_camera_list_drone2[iteration]
                drone2_LengthOfStay_go = previous_lengthOfStay_list_drone2[iteration]
                drone2_GimbalPitch_go = previous_gimbalPitch_list_drone2[iteration]
                drone2_GimbalYaw_go = previous_gimbalYaw_list_drone2[iteration]
                
                drone2_Latitude_update = drone2_Latitude_List[iteration]
                drone2_Longitude_update = drone2_Longitude_list[iteration]
                drone2_Altitude_update = drone2_Altitude_list[iteration]
                drone2_Heading_update = drone2_Heading_list[iteration]
                drone2_Speed_update = drone2_Speed_list[iteration]
                drone2_Camera_update = camera_list[iteration]
                drone2_LengthOfStay_update = lengthOfStay_list[iteration]
                drone2_GimbalPitch_update = gimbalPitch_list[iteration]
                drone2_GimbalYaw_update = gimbalYaw_list[iteration]
                
                iteration += 1
                
            else:
                
                drone2_Latitude_go = drone2_Latitude_List[iteration]
                drone2_Longitude_go = drone2_Longitude_list[iteration]
                drone2_Altitude_go = drone2_Altitude_list[iteration]
                drone2_Heading_go = drone2_Heading_list[iteration]
                drone2_Speed_go = drone2_Speed_list[iteration]
                drone2_Camera_go = camera_list[iteration]
                drone2_LengthOfStay_go = lengthOfStay_list[iteration]
                drone2_GimbalPitch_go = gimbalPitch_list[iteration]
                drone2_GimbalYaw_go = gimbalYaw_list[iteration]
                
                drone2_Latitude_update = drone2_Latitude_List[iteration + 1]
                drone2_Longitude_update = drone2_Longitude_list[iteration + 1]
                drone2_Altitude_update = drone2_Altitude_list[iteration + 1]
                drone2_Heading_update = drone2_Heading_list[iteration + 1]
                drone2_Speed_update = drone2_Speed_list[iteration + 1]
                drone2_Camera_update = camera_list[iteration + 1]
                drone2_LengthOfStay_update = lengthOfStay_list[iteration + 1]
                drone2_GimbalPitch_update = gimbalPitch_list[iteration + 1]
                drone2_GimbalYaw_update = gimbalYaw_list[iteration + 1]
                
                iteration += 2  
            
            
        waypointvalue2 = incrementor
        
        ################ for reaching the waypoint ################
        
        print("waypointvalue2_drone2(go):",waypointvalue2)
        drone2_waypoint_data_reached = f"{drone2_Latitude_go}:{drone2_Longitude_go}:{drone2_Altitude_go}:{drone2_Heading_go}:{drone2_Speed_go}:{waypointvalue2}:{Way2_threshold}:{drone2_GimbalPitch_go}:{drone2_GimbalYaw_go}:{drone2_Camera_go}"
        
        drone2_send_data = w.sendWayPointData(drone2_waypoint_data_reached, 2)     # 2 refers to the drone number
        
        drone2_waypoint_data_sent = f"Lat: {drone2_Latitude_go}, Long: {drone2_Longitude_go}, Alt: {drone2_Altitude_go}, Heading: {drone2_Heading_go}, Speed: {drone2_Speed_go}, Waypoint: {waypointvalue2}, Threshold: {Way2_threshold}, Gimbal Pitch: {drone2_GimbalPitch_go}, Gimbal Yaw: {drone2_GimbalYaw_go}, Camera: {drone2_Camera_go}"
        if debug:
            print("Data being Sent for drone2 (go):",drone2_waypoint_data_sent)
            
        ## Check if the drone has reached the waypoint, element (14) of the getImageAndTelemetryData string is set to 1. Extract the image and telemetry data when the condition is met. ## Every time the drone receive the next waypoints this element is set to zero again ion the drone app.
        
        while True:
        
            drone2_send_data = w.sendWayPointData(drone2_waypoint_data_reached, 2) 
            drone2_Image_Telemetry_data = w.getImageAndTelemetryData(2)
            drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[3110408:]).decode())
            
            drone2_elements = drone2_Telemetry_data.split(":")                 # Extract all elements from the string
            drone2_Waypoint_sent = drone2_elements[15].split('.')[0]
            # print("drone2_Waypoint_sent_for_go:",drone2_Waypoint_sent)
            if (drone2_Waypoint_sent) == str(incrementor):
                if debug: 
                    print("drone2 Waypoint data sent for go")
                    print ("go thread for drone2:", drone2_Waypoint_sent, incrementor)
                break
            
        while True:
            drone2_Image_Telemetry_data = w.getImageAndTelemetryData(2)
            drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[3110408:]).decode())
            
            drone2_elements = drone2_Telemetry_data.split(":")                 # Extract all elements from the string
            drone2_Waypoint_reached = drone2_elements[14]
            
            
            if drone2_Waypoint_reached == str(incrementor):
                if debug:
                    print("drone2 Waypoint has been reached")
                    print ("go thread waypoint reached for drone2:", drone2_Waypoint_reached, incrementor)
                break
            
        # Call the telemetry data again
        drone2_Image_Telemetry_data = w.getImageAndTelemetryData(2)
        drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[3110408:]).decode())
        
        drone_2_telemetry_elements = drone2_Telemetry_data.split(":")
        
        latitude = drone_2_telemetry_elements[0]
        longitude = drone_2_telemetry_elements[1]
        altitude = drone_2_telemetry_elements[2]
        heading = drone_2_telemetry_elements[3]
        gimbal_pitch = drone_2_telemetry_elements[4]
        gimbal_yaw = drone_2_telemetry_elements[6]
        
        if debug: 
            reached_data = f"Lat_Reached: {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for drone2 (go) --->", reached_data)
            
            print("drone2_Waypointdata (go):", drone2_Telemetry_data)
            
        if drone2_LengthOfStay_go > 0:
            time.sleep(drone2_LengthOfStay_go)
            
        incrementor += 1
        
        ################ updating the waypoint ################
        
        waypointvalue2_update = incrementor
        print("waypointvalue2_drone2(update):",waypointvalue2_update)
        drone2_waypoint_data = f"{drone2_Latitude_update}:{drone2_Longitude_update}:{drone2_Altitude_update}:{drone2_Heading_update}:{drone2_Speed_update}:{waypointvalue2_update}:{Way2_threshold}:{drone2_GimbalPitch_update}:{drone2_GimbalYaw_update}:{drone2_Camera_update}"
        drone2_send_data = w.sendWayPointData(drone2_waypoint_data, 2)     # 2 refers to the drone number
        
        drone2_waypoint_data_sent = f"Lat: {drone2_Latitude_update}, Long: {drone2_Longitude_update}, Alt: {drone2_Altitude_update}, Heading: {drone2_Heading_update}, Speed: {drone2_Speed_update}, Waypoint: {waypointvalue2_update}, Threshold: {Way2_threshold}, Gimbal Pitch: {drone2_GimbalPitch_update}, Gimbal Yaw: {drone2_GimbalYaw_update}, Camera: {drone2_Camera_update}"
        if debug:
            print("Data Being Sent for drone2 (update) :",drone2_waypoint_data_sent)
            
        ## Check if the drone has reached the waypoint, element (14) of the getImageAndTelemetryData string is set to 1. Extract the image and telemetry data when the condition is met. ## Every time the drone receive the next waypoints this element is set to zero again ion the drone app.
        
        while True:
        
            drone2_send_data = w.sendWayPointData(drone2_waypoint_data, 2) 
            drone2_Image_Telemetry_data = w.getImageAndTelemetryData(2)
            drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[3110408:]).decode())
            
            drone2_elements = drone2_Telemetry_data.split(":")                 # Extract all elements from the string
            drone2_Waypoint_sent = drone2_elements[15].split('.')[0]
            # print("drone2_Waypoint_sent:",drone2_Waypoint_sent)
            if (drone2_Waypoint_sent) == str(incrementor):
                if debug: 
                    print("drone2 Waypoint data sent")
                    print ("run thread for drone2:", drone2_Waypoint_sent, incrementor)
                break
            
        while True:
            drone2_Image_Telemetry_data = w.getImageAndTelemetryData(2)
            drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[3110408:]).decode())
            
            drone2_elements = drone2_Telemetry_data.split(":")                 # Extract all elements from the string
            drone2_Waypoint_reached = drone2_elements[14]
            
            if drone2_Waypoint_reached == str(incrementor):
                if debug:
                    print("drone2 Waypoint has been reached")
                    print ("run thread waypoint reached:", drone2_Waypoint_reached, incrementor)
                break
            
        # Hold the drone at the waypoint for a specified length of time
        if drone2_LengthOfStay_update > 0:
            print("drone2_Waypointdata_before_holding:", drone2_Telemetry_data)
        
            print(f'drone2 is waiting  for {drone2_LengthOfStay_update} sn before taking the image and saving the telemetry data')   
            time.sleep(drone2_LengthOfStay_update)
            
        # Call the telemetry data again
        drone2_Image_Telemetry_data = w.getImageAndTelemetryData(2)
        drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[3110408:]).decode())
        
        drone_2_telemetry_elements = drone2_Telemetry_data.split(":")
        
        latitude = drone_2_telemetry_elements[0]
        longitude = drone_2_telemetry_elements[1]
        altitude = drone_2_telemetry_elements[2]
        heading = drone_2_telemetry_elements[3]
        gimbal_pitch = drone_2_telemetry_elements[4]
        gimbal_yaw = drone_2_telemetry_elements[6]
        
        if debug:
            reached_data = f"Lat_Reached {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for Updating Parameter for drone2 --->",reached_data)
            
            print("drone2_Waypointdata (update):", drone2_Telemetry_data)
            
            # Save the telemetry data to a text file inside the results folder
            file_path = os.path.join(Download_Location, 'telemetry2.txt')
            with open(file_path, 'a') as file:
                file.write(drone2_Telemetry_data + '\n')
                
        ## Covert YUV raw data to rgb image and save   ##
        
        if decoding == 'software':
            drone2_Image = cv2.cvtColor(drone2_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV420p2RGB)
        elif decoding == 'hardware':
            drone2_Image = cv2.cvtColor(drone2_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV2BGR_NV12)
        else:
            print('Please enter a valid decoding method')
            
        # Calculate the center of the image
        center_x, center_y = drone2_Image.shape[1] // 2, drone2_Image.shape[0] // 2
        
        # Calculate the crop region
        crop_start_x = center_x - crop_size // 2
        crop_start_y = center_y - crop_size // 2
        
        # Crop the image
        cropped_image2 = drone2_Image[crop_start_y:crop_start_y + crop_size, crop_start_x:crop_start_x + crop_size]
        resized_image2 = cv2.resize(cropped_image2, (512, 512))
        
        drone2_cropped_Image = resized_image2
        
        if debug:
            waypoint_folder = f'drone2_waypoint_{incrementor}_('+ task + ')'
            waypoint_path = os.path.join(Images_Path, waypoint_folder)
            if not os.path.exists(waypoint_path):
                os.mkdir(waypoint_path)
            else:
                print("Folder already exists for drone2 (update)")
                
            cv2.imwrite(os.path.join( waypoint_path, 'drone2Image' + str(incrementor)+'.png'), drone2_cropped_Image)
            print("Image is taken and saved for drone2")
            
        if (len(d2Image)) >= 1:
                
            d2Image[0] = (drone2_cropped_Image)
            d2Poses[0] = (drone2_Telemetry_data)
                
        else:
                    
            d2Image.append(drone2_cropped_Image)
            d2Poses.append(drone2_Telemetry_data)
        
        incrementor += 1  
        if iteration >= number_of_waypoints_for_drone2 :
            with lock:
                drone_2_incrementor = incrementor
            
            with lock:
                if task == 'waypoint':
                    print("Mission Waypoint for drone2 completed")
                elif task == 'takeoff':
                    print("Takeoff completed for drone2")
                elif task == 'land':
                    print("Land completed for drone2")
                elif task == 'emergency':
                    print("Emergency Case")
                else:
                    print("Invalid task") 
            
            break
        
######################## Drone 3 Thread ############################
d3Image = []

d3Poses= []

def waypoint_tread_drone3(drone3_Latitude_List, drone3_Longitude_list, drone3_Altitude_list, drone3_Heading_list, drone3_Speed_list, Way3_threshold, camera_list, lengthOfStay_list, gimbalPitch_list, gimbalYaw_list):
    
    number_of_waypoints_for_drone3 = len(drone3_Latitude_List)
    
    global drone_3_incrementor, task, drone3_waypoint_no
    
    incrementor = drone_3_incrementor
    
    previous_speed_list_drone3 = [drone3_Speed_list[0], *drone3_Speed_list]
    previous_heading_list_drone3 = [drone3_Heading_list[0], *drone3_Heading_list]
    previous_camera_list_drone3 = [camera_list[0], *camera_list]
    previous_lengthOfStay_list_drone3 = [lengthOfStay_list[0], *lengthOfStay_list]
    previous_gimbalPitch_list_drone3 = [gimbalPitch_list[0], *gimbalPitch_list]
    previous_gimbalYaw_list_drone3 = [gimbalYaw_list[0], *gimbalYaw_list]
    
    iteration = 0
    while True:
        
        ### Emergency Case ###
        if keyboard.is_pressed('i'):
            if not key_pressed_emergency['i']:
                print("Emergency Case")
                key_pressed_emergency['i'] = True
                with lock:
                    drone_3_incrementor = incrementor
                break
        
        with lock:
            if task == 'waypoint':
                drone3_waypoint_no = drone3_waypoint_no + 1       
                print(f"Mission Waypoint {iteration+1} in progress for drone3 ...") 

                drone3_Latitude_go = drone3_Latitude_List[iteration]
                drone3_Longitude_go = drone3_Longitude_list[iteration]
                drone3_Altitude_go = drone3_Altitude_list[iteration]
                drone3_Heading_go = previous_heading_list_drone3[iteration]
                drone3_Speed_go = previous_speed_list_drone3[iteration]
                drone3_Camera_go = previous_camera_list_drone3[iteration]
                drone3_LengthOfStay_go = previous_lengthOfStay_list_drone3[iteration]
                drone3_GimbalPitch_go = previous_gimbalPitch_list_drone3[iteration]
                drone3_GimbalYaw_go = previous_gimbalYaw_list_drone3[iteration]
                
                drone3_Latitude_update = drone3_Latitude_List[iteration]
                drone3_Longitude_update = drone3_Longitude_list[iteration]
                drone3_Altitude_update = drone3_Altitude_list[iteration]
                drone3_Heading_update = drone3_Heading_list[iteration]
                drone3_Speed_update = drone3_Speed_list[iteration]
                drone3_Camera_update = camera_list[iteration]
                drone3_LengthOfStay_update = lengthOfStay_list[iteration]
                drone3_GimbalPitch_update = gimbalPitch_list[iteration]
                drone3_GimbalYaw_update = gimbalYaw_list[iteration]
                
                iteration += 1
                    
            else:
                
                drone3_Latitude_go = drone3_Latitude_List[iteration]
                drone3_Longitude_go = drone3_Longitude_list[iteration]
                drone3_Altitude_go = drone3_Altitude_list[iteration]
                drone3_Heading_go = drone3_Heading_list[iteration]
                drone3_Speed_go = drone3_Speed_list[iteration]
                drone3_Camera_go = camera_list[iteration]
                drone3_LengthOfStay_go = lengthOfStay_list[iteration]
                drone3_GimbalPitch_go = gimbalPitch_list[iteration]
                drone3_GimbalYaw_go = gimbalYaw_list[iteration]
                
                drone3_Latitude_update = drone3_Latitude_List[iteration + 1]
                drone3_Longitude_update = drone3_Longitude_list[iteration + 1]
                drone3_Altitude_update = drone3_Altitude_list[iteration + 1]
                drone3_Heading_update = drone3_Heading_list[iteration + 1]
                drone3_Speed_update = drone3_Speed_list[iteration + 1]
                drone3_Camera_update = camera_list[iteration + 1]
                drone3_LengthOfStay_update = lengthOfStay_list[iteration + 1]
                drone3_GimbalPitch_update = gimbalPitch_list[iteration + 1]
                drone3_GimbalYaw_update = gimbalYaw_list[iteration + 1]
                
                iteration += 2
                
        
        waypointvalue3 = incrementor

        ################ for reaching the waypoint ################
        
        print("waypointvalue3_drone3(go):",waypointvalue3)
        drone3_waypoint_data_reached = f"{drone3_Latitude_go}:{drone3_Longitude_go}:{drone3_Altitude_go}:{drone3_Heading_go}:{drone3_Speed_go}:{waypointvalue3}:{Way3_threshold}:{drone3_GimbalPitch_go}:{drone3_GimbalYaw_go}:{drone3_Camera_go}"
        
        drone3_send_data = w.sendWayPointData(drone3_waypoint_data_reached, 3)     # 3 refers to the drone number
        
        drone3_waypoint_data_sent = f"Lat: {drone3_Latitude_go}, Long: {drone3_Longitude_go}, Alt: {drone3_Altitude_go}, Heading: {drone3_Heading_go}, Speed: {drone3_Speed_go}, Waypoint: {waypointvalue3}, Threshold: {Way3_threshold}, Gimbal Pitch: {drone3_GimbalPitch_go}, Gimbal Yaw: {drone3_GimbalYaw_go}, Camera: {drone3_Camera_go}"
        
        if debug:
            print("Data being Sent for drone3 (go):",drone3_waypoint_data_sent)
            
        ## Check if the drone has reached the waypoint, element (14) of the getImageAndTelemetryData string is set to 1. Extract the image and telemetry data when the condition is met. ## Every time the drone receive the next waypoints this element is set to zero again ion the drone app.
        
        while True:
        
            drone3_send_data = w.sendWayPointData(drone3_waypoint_data_reached, 3) 
            drone3_Image_Telemetry_data = w.getImageAndTelemetryData(3)
            drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[3110408:]).decode())
            
            drone3_elements = drone3_Telemetry_data.split(":")                 # Extract all elements from the string
            drone3_Waypoint_sent = drone3_elements[15].split('.')[0]
            # print("drone3_Waypoint_sent_for_go:",drone3_Waypoint_sent)
            if (drone3_Waypoint_sent) == str(incrementor):
                if debug: 
                    print("drone3 Waypoint data sent for go")
                    print ("go thread for drone3:", drone3_Waypoint_sent, incrementor)
                break
            
        while True:
            drone3_Image_Telemetry_data = w.getImageAndTelemetryData(3)
            drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[3110408:]).decode())
            
            drone3_elements = drone3_Telemetry_data.split(":")                 # Extract all elements from the string
            drone3_Waypoint_reached = drone3_elements[14]
            
            # print("drone3_Waypoint_reached:",drone3_Waypoint_reached)
            # print("incrementor:", incrementor)
            
            if drone3_Waypoint_reached == str(incrementor):
                if debug:
                    print("drone3 Waypoint has been reached")
                    print ("go thread waypoint reached for drone3:", drone3_Waypoint_reached, incrementor)
                break
            
        # Call the telemetry data again
        drone3_Image_Telemetry_data = w.getImageAndTelemetryData(3)
        drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[3110408:]).decode())
        
        drone_3_telemetry_elements = drone3_Telemetry_data.split(":")
        
        latitude = drone_3_telemetry_elements[0]
        longitude = drone_3_telemetry_elements[1]
        altitude = drone_3_telemetry_elements[2]
        heading = drone_3_telemetry_elements[3]
        gimbal_pitch = drone_3_telemetry_elements[4]
        gimbal_yaw = drone_3_telemetry_elements[6]
        
        if debug: 
            reached_data = f"Lat_Reached: {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for drone3 (go) --->", reached_data)
            
            print("drone3_Waypointdata (go):", drone3_Telemetry_data)
            
        if drone3_LengthOfStay_go > 0:
            time.sleep(drone3_LengthOfStay_go)
            
        incrementor += 1
        
        ################ updating the waypoint ################
        
        waypointvalue3_update = incrementor
        print("waypointvalue3_drone3(update):",waypointvalue3_update)
        drone3_waypoint_data = f"{drone3_Latitude_update}:{drone3_Longitude_update}:{drone3_Altitude_update}:{drone3_Heading_update}:{drone3_Speed_update}:{waypointvalue3_update}:{Way3_threshold}:{drone3_GimbalPitch_update}:{drone3_GimbalYaw_update}:{drone3_Camera_update}"
        drone3_send_data = w.sendWayPointData(drone3_waypoint_data, 3)     # 3 refers to the drone number
        
        drone3_waypoint_data_sent = f"Lat: {drone3_Latitude_update}, Long: {drone3_Longitude_update}, Alt: {drone3_Altitude_update}, Heading: {drone3_Heading_update}, Speed: {drone3_Speed_update}, Waypoint: {waypointvalue3_update}, Threshold: {Way3_threshold}, Gimbal Pitch: {drone3_GimbalPitch_update}, Gimbal Yaw: {drone3_GimbalYaw_update}, Camera: {drone3_Camera_update}"
        if debug:
            print("Data Being Sent for drone3 (update) :",drone3_waypoint_data_sent)
            
        ## Check if the drone has reached the waypoint, element (14) of the getImageAndTelemetryData string is set to 1. Extract the image and telemetry data when the condition is met. ## Every time the drone receive the next waypoints this element is set to zero again ion the drone app.
        
        while True:
        
            drone3_send_data = w.sendWayPointData(drone3_waypoint_data, 3) 
            drone3_Image_Telemetry_data = w.getImageAndTelemetryData(3)
            drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[3110408:]).decode())
            
            drone3_elements = drone3_Telemetry_data.split(":")                 # Extract all elements from the string
            drone3_Waypoint_sent = drone3_elements[15].split('.')[0]
            # print("drone3_Waypoint_sent:",drone3_Waypoint_sent)
            if (drone3_Waypoint_sent) == str(incrementor):
                if debug: 
                    print("drone3 Waypoint data sent")
                    print ("run thread for drone3:", drone3_Waypoint_sent, incrementor)
                break
            
        while True:
            drone3_Image_Telemetry_data = w.getImageAndTelemetryData(3)
            drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[3110408:]).decode())
            
            drone3_elements = drone3_Telemetry_data.split(":")                 # Extract all elements from the string
            drone3_Waypoint_reached = drone3_elements[14]
            
            # print("drone3_Waypoint_reached:",drone3_Waypoint_reached)
            # print("incrementor:", incrementor)
            
            if drone3_Waypoint_reached == str(incrementor):
                if debug:
                    print("drone3 Waypoint has been reached")
                    print ("run thread waypoint reached:", drone3_Waypoint_reached, incrementor)
                break
            
        # Hold the drone at the waypoint for a specified length of time
        if drone3_LengthOfStay_update > 0:
            print("drone3_Waypointdata_before_holding:", drone3_Telemetry_data)
        
            print(f'drone3 is waiting  for {drone3_LengthOfStay_update} sn before taking the image and saving the telemetry data')   
            time.sleep(drone3_LengthOfStay_update)
            
        # Call the telemetry data again
        drone3_Image_Telemetry_data = w.getImageAndTelemetryData(3)
        drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[3110408:]).decode())
        
        drone_3_telemetry_elements = drone3_Telemetry_data.split(":")
        
        latitude = drone_3_telemetry_elements[0]
        longitude = drone_3_telemetry_elements[1]
        altitude = drone_3_telemetry_elements[2]
        heading = drone_3_telemetry_elements[3]
        gimbal_pitch = drone_3_telemetry_elements[4]
        gimbal_yaw = drone_3_telemetry_elements[6]
        
        if debug:
            reached_data = f"Lat_Reached {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for Updating Parameter for drone3 --->",reached_data)
            
            print("drone3_Waypointdata (update):", drone3_Telemetry_data)
            
            # Save the telemetry data to a text file inside the results folder
            file_path = os.path.join(Download_Location, 'telemetry3.txt')
            with open(file_path, 'a') as file:
                file.write(drone3_Telemetry_data + '\n')
                
        ## Covert YUV raw data to rgb image and save   ##
        
        if decoding == 'software':
            drone3_Image = cv2.cvtColor(drone3_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV420p2RGB)
        elif decoding == 'hardware':
            drone3_Image = cv2.cvtColor(drone3_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV2BGR_NV12)
        else:
            print('Please enter a valid decoding method')
            
        # Calculate the center of the image
        center_x, center_y = drone3_Image.shape[1] // 2, drone3_Image.shape[0] // 2
        
        # Calculate the crop region
        crop_start_x = center_x - crop_size // 2
        crop_start_y = center_y - crop_size // 2
        
        # Crop the image
        cropped_image3 = drone3_Image[crop_start_y:crop_start_y + crop_size, crop_start_x:crop_start_x + crop_size]
        resized_image3 = cv2.resize(cropped_image3, (512, 512))
        
        drone3_cropped_Image = resized_image3
        
        if debug:
            waypoint_folder = f'drone3_waypoint_{incrementor}_('+ task + ')'
            waypoint_path = os.path.join(Images_Path, waypoint_folder)
            if not os.path.exists(waypoint_path):
                os.mkdir(waypoint_path)
            else:
                print("Folder already exists for drone3 (update)")
                
            cv2.imwrite(os.path.join( waypoint_path, 'drone3Image' + str(incrementor)+'.png'), drone3_cropped_Image)
            print("Image is taken and saved for drone3")
            
        if (len(d3Image)) >= 1:
            
            d3Image[0] = (drone3_cropped_Image)
            d3Poses[0] = (drone3_Telemetry_data)
            
        else:
                
            d3Image.append(drone3_cropped_Image)
            d3Poses.append(drone3_Telemetry_data)
        
        incrementor += 1
        
        if iteration >= number_of_waypoints_for_drone3:
            with lock:
                drone_3_incrementor = incrementor
            
            with lock:
                if task == 'waypoint':
                    print("Mission Waypoint for drone3 completed")
                elif task == 'takeoff':
                    print("Takeoff completed for drone3")
                elif task == 'land':
                    print("Land completed for drone3")
                elif task == 'emergency':
                    print("Emergency Case")
                else:
                    print("Invalid task")
                
            break
    
######################## Drone 4 Thread ############################
d4Image = []
d4Poses= []

def waypoint_tread_drone4(drone4_Latitude_List, drone4_Longitude_list, drone4_Altitude_list,drone4_Heading_list,drone4_Speed_list, Way4_threshold, camera_list, lengthOfStay_list, gimbalPitch_list, gimbalYaw_list):
    # print('Waypoint latitude list for drone4:', drone4_Latitude_List)
    
    number_of_waypoints_for_drone4 = len(drone4_Latitude_List)
    print(f"Number of waypoints for drone4: {number_of_waypoints_for_drone4}")
    
    global drone_4_incrementor, task, drone4_waypoint_no
    
    incrementor = drone_4_incrementor
    
    previous_speed_list_drone4 = [drone4_Speed_list[0], *drone4_Speed_list]
    previous_heading_list_drone4 = [drone4_Heading_list[0], *drone4_Heading_list]
    previous_camera_list_drone4 = [camera_list[0], *camera_list]
    previous_lengthOfStay_list_drone4 = [lengthOfStay_list[0], *lengthOfStay_list]
    previous_gimbalPitch_list_drone4 = [gimbalPitch_list[0], *gimbalPitch_list]
    previous_gimbalYaw_list_drone4 = [gimbalYaw_list[0], *gimbalYaw_list]
    
    iteration = 0
    
    while True:
        
        ### Emergency Case ###  
        if keyboard.is_pressed('i'):
            if not key_pressed_emergency['i']:
                print("Emergency Case")
                key_pressed_emergency['i'] = True
                with lock:
                    drone_4_incrementor = incrementor
                break
        
        with lock:
            if task == 'waypoint':
                drone4_waypoint_no = drone4_waypoint_no + 1
                print(f"Mission Waypoint {iteration+1} in progress for drone4 ...") 

                drone4_Latitude_go = drone4_Latitude_List[iteration]
                drone4_Longitude_go = drone4_Longitude_list[iteration]
                drone4_Altitude_go = drone4_Altitude_list[iteration]
                drone4_Heading_go = previous_heading_list_drone4[iteration]
                drone4_Speed_go = previous_speed_list_drone4[iteration]
                drone4_Camera_go = previous_camera_list_drone4[iteration]
                drone4_LengthOfStay_go = previous_lengthOfStay_list_drone4[iteration]
                drone4_GimbalPitch_go = previous_gimbalPitch_list_drone4[iteration]
                drone4_GimbalYaw_go = previous_gimbalYaw_list_drone4[iteration]
                
                drone4_Latitude_update = drone4_Latitude_List[iteration]
                drone4_Longitude_update = drone4_Longitude_list[iteration]
                drone4_Altitude_update = drone4_Altitude_list[iteration]
                drone4_Heading_update = drone4_Heading_list[iteration]
                drone4_Speed_update = drone4_Speed_list[iteration]
                drone4_Camera_update = camera_list[iteration]
                drone4_LengthOfStay_update = lengthOfStay_list[iteration]
                drone4_GimbalPitch_update = gimbalPitch_list[iteration]
                drone4_GimbalYaw_update = gimbalYaw_list[iteration]
                
                iteration += 1
                
            else:
                
                drone4_Latitude_go = drone4_Latitude_List[iteration]
                drone4_Longitude_go = drone4_Longitude_list[iteration]
                drone4_Altitude_go = drone4_Altitude_list[iteration]
                drone4_Heading_go = drone4_Heading_list[iteration]
                drone4_Speed_go = drone4_Speed_list[iteration]
                drone4_Camera_go = camera_list[iteration]
                drone4_LengthOfStay_go = lengthOfStay_list[iteration]
                drone4_GimbalPitch_go = gimbalPitch_list[iteration]
                drone4_GimbalYaw_go = gimbalYaw_list[iteration]
                
                drone4_Latitude_update = drone4_Latitude_List[iteration + 1]
                drone4_Longitude_update = drone4_Longitude_list[iteration + 1]
                drone4_Altitude_update = drone4_Altitude_list[iteration + 1]
                drone4_Heading_update = drone4_Heading_list[iteration + 1]
                drone4_Speed_update = drone4_Speed_list[iteration + 1]
                drone4_Camera_update = camera_list[iteration + 1]
                drone4_LengthOfStay_update = lengthOfStay_list[iteration + 1]
                drone4_GimbalPitch_update = gimbalPitch_list[iteration + 1]
                drone4_GimbalYaw_update = gimbalYaw_list[iteration + 1]
                
                iteration += 2
                
        waypointvalue4 = incrementor

        ################ for reaching the waypoint ################
        
        print("waypointvalue4_drone4(go):",waypointvalue4)
        drone4_waypoint_data_reached = f"{drone4_Latitude_go}:{drone4_Longitude_go}:{drone4_Altitude_go}:{drone4_Heading_go}:{drone4_Speed_go}:{waypointvalue4}:{Way4_threshold}:{drone4_GimbalPitch_go}:{drone4_GimbalYaw_go}:{drone4_Camera_go}"
        
        drone4_send_data = w.sendWayPointData(drone4_waypoint_data_reached, 4)     # 4 refers to the drone number
        
        drone4_waypoint_data_sent = f"Lat: {drone4_Latitude_go}, Long: {drone4_Longitude_go}, Alt: {drone4_Altitude_go}, Heading: {drone4_Heading_go}, Speed: {drone4_Speed_go}, Waypoint: {waypointvalue4}, Threshold: {Way4_threshold}, Gimbal Pitch: {drone4_GimbalPitch_go}, Gimbal Yaw: {drone4_GimbalYaw_go}, Camera: {drone4_Camera_go}"
        if debug:
            print("Data being Sent for drone4 (go):",drone4_waypoint_data_sent)
        
        ## Check if the drone has reached the waypoint, element (14) of the getImageAndTelemetryData string is set to 1. Extract the image and telemetry data when the condition is met. ## Every time the drone receive the next waypoints this element is set to zero again ion the drone app.
        ## Element 15 is to confirm that the next waypoint data has been successfully received on the app side.
        
        while True:
        
            drone4_send_data = w.sendWayPointData(drone4_waypoint_data_reached, 4) 
            drone4_Image_Telemetry_data = w.getImageAndTelemetryData(4) # 4 refers to the drone number
            drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[3110408:]).decode())
            
            drone4_elements = drone4_Telemetry_data.split(":")                 # Extract all elements from the string
            drone4_Waypoint_sent = drone4_elements[15].split('.')[0]
            if (drone4_Waypoint_sent) == str(incrementor):
                if debug: 
                    print("drone4 Waypoint data sent for go")
                    print ("go thread for drone4:", drone4_Waypoint_sent, incrementor)
                break # Exit the loop
            
        while True:
            drone4_Image_Telemetry_data = w.getImageAndTelemetryData(4)
            drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[3110408:]).decode())
            
            drone4_elements = drone4_Telemetry_data.split(":")                 # Extract all elements from the string
            drone4_Waypoint_reached = drone4_elements[14]
            
            if drone4_Waypoint_reached == str(incrementor):
                if debug:
                    print("drone4 Waypoint has been reached")
                    print ("go thread waypoint reached for drone4:", drone4_Waypoint_reached, incrementor)
                break # Exit the loop
        
        # Call the telemetry data again
        drone4_Image_Telemetry_data = w.getImageAndTelemetryData(4)
        drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[3110408:]).decode())
        
        drone_4_telemetry_elements = drone4_Telemetry_data.split(":")

        latitude = drone_4_telemetry_elements[0] 
        longitude = drone_4_telemetry_elements[1]
        altitude = drone_4_telemetry_elements[2]
        heading = drone_4_telemetry_elements[3]
        gimbal_pitch = drone_4_telemetry_elements[4]
        gimbal_yaw = drone_4_telemetry_elements[6]

        if debug: 
            reached_data = f"Lat_Reached: {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for drone4 (go) --->", reached_data, "\n")
            
            print("drone4_Waypointdata (go):", drone4_Telemetry_data, "\n")  
            
        if drone4_LengthOfStay_go > 0:
            time.sleep(drone4_LengthOfStay_go)   
        
        incrementor += 1
        ################ updating the waypoint ################
        
        waypointvalue4_update = incrementor 
        print("waypointvalue4_drone4(update):",waypointvalue4_update)
        drone4_waypoint_data = f"{drone4_Latitude_update}:{drone4_Longitude_update}:{drone4_Altitude_update}:{drone4_Heading_update}:{drone4_Speed_update}:{waypointvalue4_update}:{Way4_threshold}:{drone4_GimbalPitch_update}:{drone4_GimbalYaw_update}:{drone4_Camera_update}"
        drone4_send_data = w.sendWayPointData(drone4_waypoint_data, 4)     # 4 refers to the drone number
        
        drone4_waypoint_data_sent = f"Lat: {drone4_Latitude_update}, Long: {drone4_Longitude_update}, Alt: {drone4_Altitude_update}, Heading: {drone4_Heading_update}, Speed: {drone4_Speed_update}, Waypoint: {waypointvalue4_update}, Threshold: {Way4_threshold}, Gimbal Pitch: {drone4_GimbalPitch_update}, Gimbal Yaw: {drone4_GimbalYaw_update}, Camera: {drone4_Camera_update}"
        if debug:
            print("Data Being Sent for drone4 (update) :",drone4_waypoint_data_sent, "\n")
        
        ## Check if the drone has reached the waypoint, element (14) of the getImageAndTelemetryData string is set to 1. Extract the image and telemetry data when the condition is met. ## Every time the drone receive the next waypoints this element is set to zero again ion the drone app.
        ## Element 15 is to confirm that the next waypoint data has been successfully received on the app side.
        
        while True:
        
            drone4_send_data = w.sendWayPointData(drone4_waypoint_data, 4) 
            drone4_Image_Telemetry_data = w.getImageAndTelemetryData(4) # 4 refers to the drone number
            drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[3110408:]).decode())
            
            drone4_elements = drone4_Telemetry_data.split(":")                 # Extract all elements from the string
            drone4_Waypoint_sent = drone4_elements[15].split('.')[0]

            if (drone4_Waypoint_sent) == str(incrementor):
                if debug: 
                    print("drone4 Waypoint data sent")
                    print ("run thread for drone4:", drone4_Waypoint_sent, incrementor)
                    
                break # Exit the loop
            

        while True:
            drone4_Image_Telemetry_data = w.getImageAndTelemetryData(4)
            drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[3110408:]).decode())
            
            drone4_elements = drone4_Telemetry_data.split(":")                 # Extract all elements from the string
            drone4_Waypoint_reached = drone4_elements[14]
            
            if drone4_Waypoint_reached == str(incrementor):
                if debug:
                    print("drone4 Waypoint has been reached")
                    print ("run thread waypoint reached:", drone4_Waypoint_reached, incrementor)
                break # Exit the loop
            
        # Hold the drone at the waypoint for a specified length of time
        if drone4_LengthOfStay_update > 0:
            print("drone4_Waypointdata_before_holding:", drone4_Telemetry_data)
        
            print(f'drone4 is waiting  for {drone4_LengthOfStay_update} sn before taking the image and saving the telemetry data')   
            time.sleep(drone4_LengthOfStay_update)  
        
        # Call the telemetry data again
        drone4_Image_Telemetry_data = w.getImageAndTelemetryData(4)
        drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[3110408:]).decode())
        
        drone_4_telemetry_elements = drone4_Telemetry_data.split(":")

        latitude = drone_4_telemetry_elements[0] 
        longitude = drone_4_telemetry_elements[1]
        altitude = drone_4_telemetry_elements[2]
        heading = drone_4_telemetry_elements[3]
        gimbal_pitch = drone_4_telemetry_elements[4]
        gimbal_yaw = drone_4_telemetry_elements[6]
        
        if debug:
            reached_data = f"Lat_Reached {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for Updating Parameter for drone4 --->",reached_data, "\n")
            
            print("drone4_Waypointdata (update):", drone4_Telemetry_data)
            
            # Save the telemetry data to a text file inside the results folder
            file_path = os.path.join(Download_Location, 'telemetry4.txt')
            with open(file_path, 'a') as file:
                file.write(drone4_Telemetry_data + '\n')
                
        ## Convert YUV raw data to rgb image and save   ##

        if decoding == 'software':
            drone4_Image = cv2.cvtColor(drone4_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV420p2RGB)
        elif decoding == 'hardware':
            drone4_Image = cv2.cvtColor(drone4_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV2BGR_NV12)
        else:
            print('Please enter a valid decoding method')
        
        
        # Calculate the center of the image
        center_x, center_y = drone4_Image.shape[1] // 2, drone4_Image.shape[0] // 2

        # Calculate the crop region
        crop_start_x = center_x - crop_size // 2
        crop_start_y = center_y - crop_size // 2

        # Crop the image
        cropped_image4 = drone4_Image[crop_start_y:crop_start_y + crop_size, crop_start_x:crop_start_x + crop_size]
        resized_image4 = cv2.resize(cropped_image4, (512, 512))

        drone4_cropped_Image = resized_image4
        
        if debug:
            waypoint_folder = f'drone4_waypoint_{incrementor}_('+ task + ')'
            waypoint_path = os.path.join(Images_Path, waypoint_folder)
            if not os.path.exists(waypoint_path):
                os.mkdir(waypoint_path)
                
            else:
                print("Folder already exists for drone4 (update)")
                
            cv2.imwrite(os.path.join( waypoint_path, 'drone4Image' + str(incrementor)+'.png'), drone4_cropped_Image)
            print("Image is taken and saved for drone4")
        
        if (len(d4Image)) >= 1:
            
            d4Image[0] = (drone4_cropped_Image)
            d4Poses[0] = (drone4_Telemetry_data)
        else:
            
            d4Image.append(drone4_cropped_Image)
            d4Poses.append(drone4_Telemetry_data)
        
        incrementor += 1
        if iteration >= number_of_waypoints_for_drone4:
            with lock:
                drone_4_incrementor = incrementor
                
            with lock:    
                if task == 'waypoint':
                    print("Mission Waypoint for drone4 completed")
                elif task == 'takeoff':
                    print("Takeoff completed for drone4")
                elif task == 'land':
                    print("Land completed for drone4")
                elif task == 'emergency':
                    print("Emergency Case")
                else:
                    print("Invalid task")
                
            break
                
######################## Drone 5 Thread ############################
d5Image = []
d5Poses= []

def waypoint_tread_drone5(drone5_Latitude_List, drone5_Longitude_list, drone5_Altitude_list,drone5_Heading_list,drone5_Speed_list, Way5_threshold, camera_list, lengthOfStay_list, gimbalPitch_list, gimbalYaw_list):
    # print('Waypoint latitude list for drone5:', drone5_Latitude_List)
    
    number_of_waypoints_for_drone5 = len(drone5_Latitude_List)
    print(f"Number of waypoints for drone5: {number_of_waypoints_for_drone5}")
    
    global drone_5_incrementor, task, drone5_waypoint_no
    
    incrementor = drone_5_incrementor
    
    previous_speed_list_drone5 = [drone5_Speed_list[0], *drone5_Speed_list]
    previous_heading_list_drone5 = [drone5_Heading_list[0], *drone5_Heading_list]
    previous_camera_list_drone5 = [camera_list[0], *camera_list]
    previous_lengthOfStay_list_drone5 = [lengthOfStay_list[0], *lengthOfStay_list]
    previous_gimbalPitch_list_drone5 = [gimbalPitch_list[0], *gimbalPitch_list]
    previous_gimbalYaw_list_drone5 = [gimbalYaw_list[0], *gimbalYaw_list]
    
    iteration = 0
    
    while True:
        
        ### Emergency Case ###  
        if keyboard.is_pressed('i'):
            if not key_pressed_emergency['i']:
                print("Emergency Case")
                key_pressed_emergency['i'] = True
                with lock:
                    drone_5_incrementor = incrementor
                break
        
        with lock:
            if task == 'waypoint':
                drone5_waypoint_no = drone5_waypoint_no + 1
                print(f"Mission Waypoint {iteration+1} in progress for drone5 ...") 

                drone5_Latitude_go = drone5_Latitude_List[iteration]
                drone5_Longitude_go = drone5_Longitude_list[iteration]
                drone5_Altitude_go = drone5_Altitude_list[iteration]
                drone5_Heading_go = previous_heading_list_drone5[iteration]
                drone5_Speed_go = previous_speed_list_drone5[iteration]
                drone5_Camera_go = previous_camera_list_drone5[iteration]
                drone5_LengthOfStay_go = previous_lengthOfStay_list_drone5[iteration]
                drone5_GimbalPitch_go = previous_gimbalPitch_list_drone5[iteration]
                drone5_GimbalYaw_go = previous_gimbalYaw_list_drone5[iteration]
                
                drone5_Latitude_update = drone5_Latitude_List[iteration]
                drone5_Longitude_update = drone5_Longitude_list[iteration]
                drone5_Altitude_update = drone5_Altitude_list[iteration]
                drone5_Heading_update = drone5_Heading_list[iteration]
                drone5_Speed_update = drone5_Speed_list[iteration]
                drone5_Camera_update = camera_list[iteration]
                drone5_LengthOfStay_update = lengthOfStay_list[iteration]
                drone5_GimbalPitch_update = gimbalPitch_list[iteration]
                drone5_GimbalYaw_update = gimbalYaw_list[iteration]
                
                iteration += 1
                
            else:
                
                drone5_Latitude_go = drone5_Latitude_List[iteration]
                drone5_Longitude_go = drone5_Longitude_list[iteration]
                drone5_Altitude_go = drone5_Altitude_list[iteration]
                drone5_Heading_go = drone5_Heading_list[iteration]
                drone5_Speed_go = drone5_Speed_list[iteration]
                drone5_Camera_go = camera_list[iteration]
                drone5_LengthOfStay_go = lengthOfStay_list[iteration]
                drone5_GimbalPitch_go = gimbalPitch_list[iteration]
                drone5_GimbalYaw_go = gimbalYaw_list[iteration]
                
                drone5_Latitude_update = drone5_Latitude_List[iteration + 1]
                drone5_Longitude_update = drone5_Longitude_list[iteration + 1]
                drone5_Altitude_update = drone5_Altitude_list[iteration + 1]
                drone5_Heading_update = drone5_Heading_list[iteration + 1]
                drone5_Speed_update = drone5_Speed_list[iteration + 1]
                drone5_Camera_update = camera_list[iteration + 1]
                drone5_LengthOfStay_update = lengthOfStay_list[iteration + 1]
                drone5_GimbalPitch_update = gimbalPitch_list[iteration + 1]
                drone5_GimbalYaw_update = gimbalYaw_list[iteration + 1]
                
                iteration += 2
                
        waypointvalue5 = incrementor

        ################ for reaching the waypoint ################
        
        print("waypointvalue5_drone5(go):",waypointvalue5)
        drone5_waypoint_data_reached = f"{drone5_Latitude_go}:{drone5_Longitude_go}:{drone5_Altitude_go}:{drone5_Heading_go}:{drone5_Speed_go}:{waypointvalue5}:{Way5_threshold}:{drone5_GimbalPitch_go}:{drone5_GimbalYaw_go}:{drone5_Camera_go}"
        
        drone5_send_data = w.sendWayPointData(drone5_waypoint_data_reached, 5)     # 5 refers to the drone number
        
        drone5_waypoint_data_sent = f"Lat: {drone5_Latitude_go}, Long: {drone5_Longitude_go}, Alt: {drone5_Altitude_go}, Heading: {drone5_Heading_go}, Speed: {drone5_Speed_go}, Waypoint: {waypointvalue5}, Threshold: {Way5_threshold}, Gimbal Pitch: {drone5_GimbalPitch_go}, Gimbal Yaw: {drone5_GimbalYaw_go}, Camera: {drone5_Camera_go}"
        if debug:
            print("Data being Sent for drone5 (go):",drone5_waypoint_data_sent)
        
        ## Check if the drone has reached the waypoint, element (14) of the getImageAndTelemetryData string is set to 1. Extract the image and telemetry data when the condition is met. ## Every time the drone receive the next waypoints this element is set to zero again ion the drone app.
        ## Element 15 is to confirm that the next waypoint data has been successfully received on the app side.
        
        while True:
        
            drone5_send_data = w.sendWayPointData(drone5_waypoint_data_reached, 5) 
            drone5_Image_Telemetry_data = w.getImageAndTelemetryData(5) # 5 refers to the drone number
            drone5_Telemetry_data = (bytearray(drone5_Image_Telemetry_data[3110408:]).decode())
            
            drone5_elements = drone5_Telemetry_data.split(":")                 # Extract all elements from the string
            drone5_Waypoint_sent = drone5_elements[15].split('.')[0]
            if (drone5_Waypoint_sent) == str(incrementor):
                if debug: 
                    print("drone5 Waypoint data sent for go")
                    print ("go thread for drone5:", drone5_Waypoint_sent, incrementor)
                break # Exit the loop
            
        while True:
            drone5_Image_Telemetry_data = w.getImageAndTelemetryData(5)
            drone5_Telemetry_data = (bytearray(drone5_Image_Telemetry_data[3110408:]).decode())
            
            drone5_elements = drone5_Telemetry_data.split(":")                 # Extract all elements from the string
            drone5_Waypoint_reached = drone5_elements[14]
            
            if drone5_Waypoint_reached == str(incrementor):
                if debug:
                    print("drone5 Waypoint has been reached")
                    print ("go thread waypoint reached for drone5:", drone5_Waypoint_reached, incrementor)
                break # Exit the loop
        
        # Call the telemetry data again
        drone5_Image_Telemetry_data = w.getImageAndTelemetryData(5)
        drone5_Telemetry_data = (bytearray(drone5_Image_Telemetry_data[3110408:]).decode())
        
        drone_5_telemetry_elements = drone5_Telemetry_data.split(":")

        latitude = drone_5_telemetry_elements[0] 
        longitude = drone_5_telemetry_elements[1]
        altitude = drone_5_telemetry_elements[2]
        heading = drone_5_telemetry_elements[3]
        gimbal_pitch = drone_5_telemetry_elements[4]
        gimbal_yaw = drone_5_telemetry_elements[6]

        if debug: 
            reached_data = f"Lat_Reached: {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for drone5 (go) --->", reached_data, "\n")
            
            print("drone5_Waypointdata (go):", drone5_Telemetry_data, "\n")  
            
        if drone5_LengthOfStay_go > 0:
            time.sleep(drone5_LengthOfStay_go)   
        
        incrementor += 1
        ################ updating the waypoint ################
        
        waypointvalue5_update = incrementor 
        print("waypointvalue5_drone5(update):",waypointvalue5_update)
        drone5_waypoint_data = f"{drone5_Latitude_update}:{drone5_Longitude_update}:{drone5_Altitude_update}:{drone5_Heading_update}:{drone5_Speed_update}:{waypointvalue5_update}:{Way5_threshold}:{drone5_GimbalPitch_update}:{drone5_GimbalYaw_update}:{drone5_Camera_update}"
        drone5_send_data = w.sendWayPointData(drone5_waypoint_data, 5)     # 5 refers to the drone number
        
        drone5_waypoint_data_sent = f"Lat: {drone5_Latitude_update}, Long: {drone5_Longitude_update}, Alt: {drone5_Altitude_update}, Heading: {drone5_Heading_update}, Speed: {drone5_Speed_update}, Waypoint: {waypointvalue5_update}, Threshold: {Way5_threshold}, Gimbal Pitch: {drone5_GimbalPitch_update}, Gimbal Yaw: {drone5_GimbalYaw_update}, Camera: {drone5_Camera_update}"
        if debug:
            print("Data Being Sent for drone5 (update) :",drone5_waypoint_data_sent, "\n")
        
        ## Check if the drone has reached the waypoint, element (14) of the getImageAndTelemetryData string is set to 1. Extract the image and telemetry data when the condition is met. ## Every time the drone receive the next waypoints this element is set to zero again ion the drone app.
        ## Element 15 is to confirm that the next waypoint data has been successfully received on the app side.
        
        while True:
        
            drone5_send_data = w.sendWayPointData(drone5_waypoint_data, 5) 
            drone5_Image_Telemetry_data = w.getImageAndTelemetryData(5) # 5 refers to the drone number
            drone5_Telemetry_data = (bytearray(drone5_Image_Telemetry_data[3110408:]).decode())
            
            drone5_elements = drone5_Telemetry_data.split(":")                 # Extract all elements from the string
            drone5_Waypoint_sent = drone5_elements[15].split('.')[0]

            if (drone5_Waypoint_sent) == str(incrementor):
                if debug: 
                    print("drone5 Waypoint data sent")
                    print ("run thread for drone5:", drone5_Waypoint_sent, incrementor)
                    
                break # Exit the loop
            

        while True:
            drone5_Image_Telemetry_data = w.getImageAndTelemetryData(5)
            drone5_Telemetry_data = (bytearray(drone5_Image_Telemetry_data[3110408:]).decode())
            
            drone5_elements = drone5_Telemetry_data.split(":")                 # Extract all elements from the string
            drone5_Waypoint_reached = drone5_elements[14]
            
            if drone5_Waypoint_reached == str(incrementor):
                if debug:
                    print("drone5 Waypoint has been reached")
                    print ("run thread waypoint reached:", drone5_Waypoint_reached, incrementor)
                break # Exit the loop
            
        # Hold the drone at the waypoint for a specified length of time
        if drone5_LengthOfStay_update > 0:
            print("drone5_Waypointdata_before_holding:", drone5_Telemetry_data)
        
            print(f'drone5 is waiting  for {drone5_LengthOfStay_update} sn before taking the image and saving the telemetry data')   
            time.sleep(drone5_LengthOfStay_update)  
        
        # Call the telemetry data again
        drone5_Image_Telemetry_data = w.getImageAndTelemetryData(5)
        drone5_Telemetry_data = (bytearray(drone5_Image_Telemetry_data[3110408:]).decode())
        
        drone_5_telemetry_elements = drone5_Telemetry_data.split(":")

        latitude = drone_5_telemetry_elements[0] 
        longitude = drone_5_telemetry_elements[1]
        altitude = drone_5_telemetry_elements[2]
        heading = drone_5_telemetry_elements[3]
        gimbal_pitch = drone_5_telemetry_elements[4]
        gimbal_yaw = drone_5_telemetry_elements[6]
        
        if debug:
            reached_data = f"Lat_Reached {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for Updating Parameter for drone5 --->",reached_data, "\n")
            
            print("drone5_Waypointdata (update):", drone5_Telemetry_data)
            
            # Save the telemetry data to a text file inside the results folder
            file_path = os.path.join(Download_Location, 'telemetry5.txt')
            with open(file_path, 'a') as file:
                file.write(drone5_Telemetry_data + '\n')
                
        ## Convert YUV raw data to rgb image and save   ##

        if decoding == 'software':
            drone5_Image = cv2.cvtColor(drone5_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV420p2RGB)
        elif decoding == 'hardware':
            drone5_Image = cv2.cvtColor(drone5_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV2BGR_NV12)
        else:
            print('Please enter a valid decoding method')
        
        
        # Calculate the center of the image
        center_x, center_y = drone5_Image.shape[1] // 2, drone5_Image.shape[0] // 2

        # Calculate the crop region
        crop_start_x = center_x - crop_size // 2
        crop_start_y = center_y - crop_size // 2

        # Crop the image
        cropped_image5 = drone5_Image[crop_start_y:crop_start_y + crop_size, crop_start_x:crop_start_x + crop_size]
        resized_image5 = cv2.resize(cropped_image5, (512, 512))

        drone5_cropped_Image = resized_image5
        
        if debug:
            waypoint_folder = f'drone5_waypoint_{incrementor}_('+ task + ')'
            waypoint_path = os.path.join(Images_Path, waypoint_folder)
            if not os.path.exists(waypoint_path):
                os.mkdir(waypoint_path)
                
            else:
                print("Folder already exists for drone5 (update)")
                
            cv2.imwrite(os.path.join( waypoint_path, 'drone5Image' + str(incrementor)+'.png'), drone5_cropped_Image)
            print("Image is taken and saved for drone5")
        
        if (len(d5Image)) >= 1:
            
            d5Image[0] = (drone5_cropped_Image)
            d5Poses[0] = (drone5_Telemetry_data)
        else:
            
            d5Image.append(drone5_cropped_Image)
            d5Poses.append(drone5_Telemetry_data)
        
        incrementor += 1
        if iteration >= number_of_waypoints_for_drone5:
            with lock:
                drone_5_incrementor = incrementor
                
            with lock:    
                if task == 'waypoint':
                    print("Mission Waypoint for drone5 completed")
                elif task == 'takeoff':
                    print("Takeoff completed for drone5")
                elif task == 'land':
                    print("Land completed for drone5")
                elif task == 'emergency':
                    print("Emergency Case")
                else:
                    print("Invalid task")
                
            break
    
######################## Drone 6 Thread ############################
d6Image = []
d6Poses = []

def waypoint_tread_drone6(drone6_Latitude_List, drone6_Longitude_list, drone6_Altitude_list, drone6_Heading_list, drone6_Speed_list, Way6_threshold, camera_list, lengthOfStay_list, gimbalPitch_list, gimbalYaw_list):
    # print('Waypoint latitude list for drone6:', drone6_Latitude_List)
    
    number_of_waypoints_for_drone6 = len(drone6_Latitude_List)
    print(f"Number of waypoints for drone6: {number_of_waypoints_for_drone6}")
    
    global drone_6_incrementor, task, drone6_waypoint_no
    
    incrementor = drone_6_incrementor
    
    previous_speed_list_drone6 = [drone6_Speed_list[0], *drone6_Speed_list]
    previous_heading_list_drone6 = [drone6_Heading_list[0], *drone6_Heading_list]
    previous_camera_list_drone6 = [camera_list[0], *camera_list]
    previous_lengthOfStay_list_drone6 = [lengthOfStay_list[0], *lengthOfStay_list]
    previous_gimbalPitch_list_drone6 = [gimbalPitch_list[0], *gimbalPitch_list]
    previous_gimbalYaw_list_drone6 = [gimbalYaw_list[0], *gimbalYaw_list]
    
    iteration = 0
    
    while True:
        
        ### Emergency Case ###  
        if keyboard.is_pressed('i'):
            if not key_pressed_emergency['i']:
                print("Emergency Case")
                key_pressed_emergency['i'] = True
                with lock:
                    drone_6_incrementor = incrementor
                break
        
        with lock:
            if task == 'waypoint':
                drone6_waypoint_no = drone6_waypoint_no + 1
                print(f"Mission Waypoint {iteration+1} in progress for drone6 ...") 

                drone6_Latitude_go = drone6_Latitude_List[iteration]
                drone6_Longitude_go = drone6_Longitude_list[iteration]
                drone6_Altitude_go = drone6_Altitude_list[iteration]
                drone6_Heading_go = previous_heading_list_drone6[iteration]
                drone6_Speed_go = previous_speed_list_drone6[iteration]
                drone6_Camera_go = previous_camera_list_drone6[iteration]
                drone6_LengthOfStay_go = previous_lengthOfStay_list_drone6[iteration]
                drone6_GimbalPitch_go = previous_gimbalPitch_list_drone6[iteration]
                drone6_GimbalYaw_go = previous_gimbalYaw_list_drone6[iteration]
                
                drone6_Latitude_update = drone6_Latitude_List[iteration]
                drone6_Longitude_update = drone6_Longitude_list[iteration]
                drone6_Altitude_update = drone6_Altitude_list[iteration]
                drone6_Heading_update = drone6_Heading_list[iteration]
                drone6_Speed_update = drone6_Speed_list[iteration]
                drone6_Camera_update = camera_list[iteration]
                drone6_LengthOfStay_update = lengthOfStay_list[iteration]
                drone6_GimbalPitch_update = gimbalPitch_list[iteration]
                drone6_GimbalYaw_update = gimbalYaw_list[iteration]
                
                iteration += 1
                
            else:
                
                drone6_Latitude_go = drone6_Latitude_List[iteration]
                drone6_Longitude_go = drone6_Longitude_list[iteration]
                drone6_Altitude_go = drone6_Altitude_list[iteration]
                drone6_Heading_go = drone6_Heading_list[iteration]
                drone6_Speed_go = drone6_Speed_list[iteration]
                drone6_Camera_go = camera_list[iteration]
                drone6_LengthOfStay_go = lengthOfStay_list[iteration]
                drone6_GimbalPitch_go = gimbalPitch_list[iteration]
                drone6_GimbalYaw_go = gimbalYaw_list[iteration]
                
                drone6_Latitude_update = drone6_Latitude_List[iteration + 1]
                drone6_Longitude_update = drone6_Longitude_list[iteration + 1]
                drone6_Altitude_update = drone6_Altitude_list[iteration + 1]
                drone6_Heading_update = drone6_Heading_list[iteration + 1]
                drone6_Speed_update = drone6_Speed_list[iteration + 1]
                drone6_Camera_update = camera_list[iteration + 1]
                drone6_LengthOfStay_update = lengthOfStay_list[iteration + 1]
                drone6_GimbalPitch_update = gimbalPitch_list[iteration + 1]
                drone6_GimbalYaw_update = gimbalYaw_list[iteration + 1]
                
                iteration += 2
                
        waypointvalue6 = incrementor

        ################ for reaching the waypoint ################
        
        print("waypointvalue6_drone6(go):", waypointvalue6)
        drone6_waypoint_data_reached = f"{drone6_Latitude_go}:{drone6_Longitude_go}:{drone6_Altitude_go}:{drone6_Heading_go}:{drone6_Speed_go}:{waypointvalue6}:{Way6_threshold}:{drone6_GimbalPitch_go}:{drone6_GimbalYaw_go}:{drone6_Camera_go}"
        
        drone6_send_data = w.sendWayPointData(drone6_waypoint_data_reached, 6)     # 6 refers to the drone number
        
        drone6_waypoint_data_sent = f"Lat: {drone6_Latitude_go}, Long: {drone6_Longitude_go}, Alt: {drone6_Altitude_go}, Heading: {drone6_Heading_go}, Speed: {drone6_Speed_go}, Waypoint: {waypointvalue6}, Threshold: {Way6_threshold}, Gimbal Pitch: {drone6_GimbalPitch_go}, Gimbal Yaw: {drone6_GimbalYaw_go}, Camera: {drone6_Camera_go}"
        if debug:
            print("Data being Sent for drone6 (go):", drone6_waypoint_data_sent)
        
        ## Check if the drone has reached the waypoint, element (14) of the getImageAndTelemetryData string is set to 1. Extract the image and telemetry data when the condition is met. ## Every time the drone receive the next waypoints this element is set to zero again ion the drone app.
        ## Element 15 is to confirm that the next waypoint data has been successfully received on the app side.
        
        while True:
        
            drone6_send_data = w.sendWayPointData(drone6_waypoint_data_reached, 6) 
            drone6_Image_Telemetry_data = w.getImageAndTelemetryData(6) # 6 refers to the drone number
            drone6_Telemetry_data = (bytearray(drone6_Image_Telemetry_data[3110408:]).decode())
            
            drone6_elements = drone6_Telemetry_data.split(":")                 # Extract all elements from the string
            drone6_Waypoint_sent = drone6_elements[15].split('.')[0]
            if (drone6_Waypoint_sent) == str(incrementor):
                if debug: 
                    print("drone6 Waypoint data sent for go")
                    print ("go thread for drone6:", drone6_Waypoint_sent, incrementor)
                break # Exit the loop
            
        while True:
            drone6_Image_Telemetry_data = w.getImageAndTelemetryData(6)
            drone6_Telemetry_data = (bytearray(drone6_Image_Telemetry_data[3110408:]).decode())
            
            drone6_elements = drone6_Telemetry_data.split(":")                 # Extract all elements from the string
            drone6_Waypoint_reached = drone6_elements[14]
            
            if drone6_Waypoint_reached == str(incrementor):
                if debug:
                    print("drone6 Waypoint has been reached")
                    print ("go thread waypoint reached for drone6:", drone6_Waypoint_reached, incrementor)
                break # Exit the loop
        
        # Call the telemetry data again
        drone6_Image_Telemetry_data = w.getImageAndTelemetryData(6)
        drone6_Telemetry_data = (bytearray(drone6_Image_Telemetry_data[3110408:]).decode())
        
        drone_6_telemetry_elements = drone6_Telemetry_data.split(":")

        latitude = drone_6_telemetry_elements[0] 
        longitude = drone_6_telemetry_elements[1]
        altitude = drone_6_telemetry_elements[2]
        heading = drone_6_telemetry_elements[3]
        gimbal_pitch = drone_6_telemetry_elements[4]
        gimbal_yaw = drone_6_telemetry_elements[6]

        if debug: 
            reached_data = f"Lat_Reached: {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for drone6 (go) --->", reached_data, "\n")
            
            print("drone6_Waypointdata (go):", drone6_Telemetry_data, "\n")  
            
        if drone6_LengthOfStay_go > 0:
            time.sleep(drone6_LengthOfStay_go)   
        
        incrementor += 1
        ################ updating the waypoint ################
        
        waypointvalue6_update = incrementor 
        print("waypointvalue6_drone6(update):", waypointvalue6_update)
        drone6_waypoint_data = f"{drone6_Latitude_update}:{drone6_Longitude_update}:{drone6_Altitude_update}:{drone6_Heading_update}:{drone6_Speed_update}:{waypointvalue6_update}:{Way6_threshold}:{drone6_GimbalPitch_update}:{drone6_GimbalYaw_update}:{drone6_Camera_update}"
        drone6_send_data = w.sendWayPointData(drone6_waypoint_data, 6)     # 6 refers to the drone number
        
        drone6_waypoint_data_sent = f"Lat: {drone6_Latitude_update}, Long: {drone6_Longitude_update}, Alt: {drone6_Altitude_update}, Heading: {drone6_Heading_update}, Speed: {drone6_Speed_update}, Waypoint: {waypointvalue6_update}, Threshold: {Way6_threshold}, Gimbal Pitch: {drone6_GimbalPitch_update}, Gimbal Yaw: {drone6_GimbalYaw_update}, Camera: {drone6_Camera_update}"
        if debug:
            print("Data Being Sent for drone6 (update) :", drone6_waypoint_data_sent, "\n")
        
        ## Check if the drone has reached the waypoint, element (14) of the getImageAndTelemetryData string is set to 1. Extract the image and telemetry data when the condition is met. ## Every time the drone receive the next waypoints this element is set to zero again ion the drone app.
        ## Element 15 is to confirm that the next waypoint data has been successfully received on the app side.
        
        while True:
        
            drone6_send_data = w.sendWayPointData(drone6_waypoint_data, 6) 
            drone6_Image_Telemetry_data = w.getImageAndTelemetryData(6) # 6 refers to the drone number
            drone6_Telemetry_data = (bytearray(drone6_Image_Telemetry_data[3110408:]).decode())
            
            drone6_elements = drone6_Telemetry_data.split(":")                 # Extract all elements from the string
            drone6_Waypoint_sent = drone6_elements[15].split('.')[0]

            if (drone6_Waypoint_sent) == str(incrementor):
                if debug: 
                    print("drone6 Waypoint data sent")
                    print ("run thread for drone6:", drone6_Waypoint_sent, incrementor)
                    
                break # Exit the loop
            

        while True:
            drone6_Image_Telemetry_data = w.getImageAndTelemetryData(6)
            drone6_Telemetry_data = (bytearray(drone6_Image_Telemetry_data[3110408:]).decode())
            
            drone6_elements = drone6_Telemetry_data.split(":")                 # Extract all elements from the string
            drone6_Waypoint_reached = drone6_elements[14]
            
            if drone6_Waypoint_reached == str(incrementor):
                if debug:
                    print("drone6 Waypoint has been reached")
                    print ("run thread waypoint reached:", drone6_Waypoint_reached, incrementor)
                break # Exit the loop
            
        # Hold the drone at the waypoint for a specified length of time
        if drone6_LengthOfStay_update > 0:
            print("drone6_Waypointdata_before_holding:", drone6_Telemetry_data)
        
            print(f'drone6 is waiting for {drone6_LengthOfStay_update} sn before taking the image and saving the telemetry data')   
            time.sleep(drone6_LengthOfStay_update)  
        
        # Call the telemetry data again
        drone6_Image_Telemetry_data = w.getImageAndTelemetryData(6)
        drone6_Telemetry_data = (bytearray(drone6_Image_Telemetry_data[3110408:]).decode())
        
        drone_6_telemetry_elements = drone6_Telemetry_data.split(":")

        latitude = drone_6_telemetry_elements[0] 
        longitude = drone_6_telemetry_elements[1]
        altitude = drone_6_telemetry_elements[2]
        heading = drone_6_telemetry_elements[3]
        gimbal_pitch = drone_6_telemetry_elements[4]
        gimbal_yaw = drone_6_telemetry_elements[6]
        
        if debug:
            reached_data = f"Lat_Reached {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for Updating Parameter for drone6 --->", reached_data, "\n")
            
            print("drone6_Waypointdata (update):", drone6_Telemetry_data)
            
            # Save the telemetry data to a text file inside the results folder
            file_path = os.path.join(Download_Location, 'telemetry6.txt')
            with open(file_path, 'a') as file:
                file.write(drone6_Telemetry_data + '\n')
                
        ## Convert YUV raw data to rgb image and save   ##

        if decoding == 'software':
            drone6_Image = cv2.cvtColor(drone6_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV420p2RGB)
        elif decoding == 'hardware':
            drone6_Image = cv2.cvtColor(drone6_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV2BGR_NV12)
        else:
            print('Please enter a valid decoding method')
        
        
        # Calculate the center of the image
        center_x, center_y = drone6_Image.shape[1] // 2, drone6_Image.shape[0] // 2

        # Calculate the crop region
        crop_start_x = center_x - crop_size // 2
        crop_start_y = center_y - crop_size // 2

        # Crop the image
        cropped_image6 = drone6_Image[crop_start_y:crop_start_y + crop_size, crop_start_x:crop_start_x + crop_size]
        resized_image6 = cv2.resize(cropped_image6, (512, 512))

        drone6_cropped_Image = resized_image6
        
        if debug:
            waypoint_folder = f'drone6_waypoint_{incrementor}_('+ task + ')'
            waypoint_path = os.path.join(Images_Path, waypoint_folder)
            if not os.path.exists(waypoint_path):
                os.mkdir(waypoint_path)
                
            else:
                print("Folder already exists for drone6 (update)")
                
            cv2.imwrite(os.path.join(waypoint_path, 'drone6Image' + str(incrementor)+'.png'), drone6_cropped_Image)
            print("Image is taken and saved for drone6")
        
        if (len(d6Image)) >= 1:
            
            d6Image[0] = (drone6_cropped_Image)
            d6Poses[0] = (drone6_Telemetry_data)
        else:
            
            d6Image.append(drone6_cropped_Image)
            d6Poses.append(drone6_Telemetry_data)
        
        incrementor += 1
        if iteration >= number_of_waypoints_for_drone6:
            with lock:
                drone_6_incrementor = incrementor
                
            with lock:    
                if task == 'waypoint':
                    print("Mission Waypoint for drone6 completed")
                elif task == 'takeoff':
                    print("Takeoff completed for drone6")
                elif task == 'land':
                    print("Land completed for drone6")
                elif task == 'emergency':
                    print("Emergency Case")
                else:
                    print("Invalid task")
                
            break
        
######################## Drone 7 Thread ############################ 
d7Image = []
d7Poses = []

def waypoint_tread_drone7(drone7_Latitude_List, drone7_Longitude_list, drone7_Altitude_list, drone7_Heading_list, drone7_Speed_list, Way7_threshold, camera_list, lengthOfStay_list, gimbalPitch_list, gimbalYaw_list):
    # print('Waypoint latitude list for drone7:', drone7_Latitude_List)
    
    number_of_waypoints_for_drone7 = len(drone7_Latitude_List)
    print(f"Number of waypoints for drone7: {number_of_waypoints_for_drone7}")
    
    global drone_7_incrementor, task, drone7_waypoint_no
    
    incrementor = drone_7_incrementor
    
    previous_speed_list_drone7 = [drone7_Speed_list[0], *drone7_Speed_list]
    previous_heading_list_drone7 = [drone7_Heading_list[0], *drone7_Heading_list]
    previous_camera_list_drone7 = [camera_list[0], *camera_list]
    previous_lengthOfStay_list_drone7 = [lengthOfStay_list[0], *lengthOfStay_list]
    previous_gimbalPitch_list_drone7 = [gimbalPitch_list[0], *gimbalPitch_list]
    previous_gimbalYaw_list_drone7 = [gimbalYaw_list[0], *gimbalYaw_list]
    
    iteration = 0
    
    while True:
        
        ### Emergency Case ###  
        if keyboard.is_pressed('i'):
            if not key_pressed_emergency['i']:
                print("Emergency Case")
                key_pressed_emergency['i'] = True
                with lock:
                    drone_7_incrementor = incrementor
                break
        
        with lock:
            if task == 'waypoint':
                drone7_waypoint_no = drone7_waypoint_no + 1
                print(f"Mission Waypoint {iteration+1} in progress for drone7 ...") 

                drone7_Latitude_go = drone7_Latitude_List[iteration]
                drone7_Longitude_go = drone7_Longitude_list[iteration]
                drone7_Altitude_go = drone7_Altitude_list[iteration]
                drone7_Heading_go = previous_heading_list_drone7[iteration]
                drone7_Speed_go = previous_speed_list_drone7[iteration]
                drone7_Camera_go = previous_camera_list_drone7[iteration]
                drone7_LengthOfStay_go = previous_lengthOfStay_list_drone7[iteration]
                drone7_GimbalPitch_go = previous_gimbalPitch_list_drone7[iteration]
                drone7_GimbalYaw_go = previous_gimbalYaw_list_drone7[iteration]
                
                drone7_Latitude_update = drone7_Latitude_List[iteration]
                drone7_Longitude_update = drone7_Longitude_list[iteration]
                drone7_Altitude_update = drone7_Altitude_list[iteration]
                drone7_Heading_update = drone7_Heading_list[iteration]
                drone7_Speed_update = drone7_Speed_list[iteration]
                drone7_Camera_update = camera_list[iteration]
                drone7_LengthOfStay_update = lengthOfStay_list[iteration]
                drone7_GimbalPitch_update = gimbalPitch_list[iteration]
                drone7_GimbalYaw_update = gimbalYaw_list[iteration]
                
                iteration += 1
                
            else:
                
                drone7_Latitude_go = drone7_Latitude_List[iteration]
                drone7_Longitude_go = drone7_Longitude_list[iteration]
                drone7_Altitude_go = drone7_Altitude_list[iteration]
                drone7_Heading_go = drone7_Heading_list[iteration]
                drone7_Speed_go = drone7_Speed_list[iteration]
                drone7_Camera_go = camera_list[iteration]
                drone7_LengthOfStay_go = lengthOfStay_list[iteration]
                drone7_GimbalPitch_go = gimbalPitch_list[iteration]
                drone7_GimbalYaw_go = gimbalYaw_list[iteration]
                
                drone7_Latitude_update = drone7_Latitude_List[iteration + 1]
                drone7_Longitude_update = drone7_Longitude_list[iteration + 1]
                drone7_Altitude_update = drone7_Altitude_list[iteration + 1]
                drone7_Heading_update = drone7_Heading_list[iteration + 1]
                drone7_Speed_update = drone7_Speed_list[iteration + 1]
                drone7_Camera_update = camera_list[iteration + 1]
                drone7_LengthOfStay_update = lengthOfStay_list[iteration + 1]
                drone7_GimbalPitch_update = gimbalPitch_list[iteration + 1]
                drone7_GimbalYaw_update = gimbalYaw_list[iteration + 1]
                
                iteration += 2
                
        waypointvalue7 = incrementor

        ################ for reaching the waypoint ################
        
        print("waypointvalue7_drone7(go):", waypointvalue7)
        drone7_waypoint_data_reached = f"{drone7_Latitude_go}:{drone7_Longitude_go}:{drone7_Altitude_go}:{drone7_Heading_go}:{drone7_Speed_go}:{waypointvalue7}:{Way7_threshold}:{drone7_GimbalPitch_go}:{drone7_GimbalYaw_go}:{drone7_Camera_go}"
        
        drone7_send_data = w.sendWayPointData(drone7_waypoint_data_reached, 7)     # 7 refers to the drone number
        
        drone7_waypoint_data_sent = f"Lat: {drone7_Latitude_go}, Long: {drone7_Longitude_go}, Alt: {drone7_Altitude_go}, Heading: {drone7_Heading_go}, Speed: {drone7_Speed_go}, Waypoint: {waypointvalue7}, Threshold: {Way7_threshold}, Gimbal Pitch: {drone7_GimbalPitch_go}, Gimbal Yaw: {drone7_GimbalYaw_go}, Camera: {drone7_Camera_go}"
        if debug:
            print("Data being Sent for drone7 (go):", drone7_waypoint_data_sent)
        
        ## Check if the drone has reached the waypoint, element (14) of the getImageAndTelemetryData string is set to 1. Extract the image and telemetry data when the condition is met. ## Every time the drone receive the next waypoints this element is set to zero again ion the drone app.
        ## Element 15 is to confirm that the next waypoint data has been successfully received on the app side.
        
        while True:
        
            drone7_send_data = w.sendWayPointData(drone7_waypoint_data_reached, 7) 
            drone7_Image_Telemetry_data = w.getImageAndTelemetryData(7) # 7 refers to the drone number
            drone7_Telemetry_data = (bytearray(drone7_Image_Telemetry_data[3110408:]).decode())
            
            drone7_elements = drone7_Telemetry_data.split(":")                 # Extract all elements from the string
            drone7_Waypoint_sent = drone7_elements[15].split('.')[0]
            if (drone7_Waypoint_sent) == str(incrementor):
                if debug: 
                    print("drone7 Waypoint data sent for go")
                    print ("go thread for drone7:", drone7_Waypoint_sent, incrementor)
                break # Exit the loop
            
        while True:
            drone7_Image_Telemetry_data = w.getImageAndTelemetryData(7)
            drone7_Telemetry_data = (bytearray(drone7_Image_Telemetry_data[3110408:]).decode())
            
            drone7_elements = drone7_Telemetry_data.split(":")                 # Extract all elements from the string
            drone7_Waypoint_reached = drone7_elements[14]
            
            if drone7_Waypoint_reached == str(incrementor):
                if debug:
                    print("drone7 Waypoint has been reached")
                    print ("go thread waypoint reached for drone7:", drone7_Waypoint_reached, incrementor)
                break # Exit the loop
        
        # Call the telemetry data again
        drone7_Image_Telemetry_data = w.getImageAndTelemetryData(7)
        drone7_Telemetry_data = (bytearray(drone7_Image_Telemetry_data[3110408:]).decode())
        
        drone_7_telemetry_elements = drone7_Telemetry_data.split(":")

        latitude = drone_7_telemetry_elements[0] 
        longitude = drone_7_telemetry_elements[1]
        altitude = drone_7_telemetry_elements[2]
        heading = drone_7_telemetry_elements[3]
        gimbal_pitch = drone_7_telemetry_elements[4]
        gimbal_yaw = drone_7_telemetry_elements[6]

        if debug: 
            reached_data = f"Lat_Reached: {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for drone7 (go) --->", reached_data, "\n")
            
            print("drone7_Waypointdata (go):", drone7_Telemetry_data, "\n")  
            
        if drone7_LengthOfStay_go > 0:
            time.sleep(drone7_LengthOfStay_go)   
        
        incrementor += 1
        ################ updating the waypoint ################
        
        waypointvalue7_update = incrementor 
        print("waypointvalue7_drone7(update):", waypointvalue7_update)
        drone7_waypoint_data = f"{drone7_Latitude_update}:{drone7_Longitude_update}:{drone7_Altitude_update}:{drone7_Heading_update}:{drone7_Speed_update}:{waypointvalue7_update}:{Way7_threshold}:{drone7_GimbalPitch_update}:{drone7_GimbalYaw_update}:{drone7_Camera_update}"
        drone7_send_data = w.sendWayPointData(drone7_waypoint_data, 7)     # 7 refers to the drone number
        
        drone7_waypoint_data_sent = f"Lat: {drone7_Latitude_update}, Long: {drone7_Longitude_update}, Alt: {drone7_Altitude_update}, Heading: {drone7_Heading_update}, Speed: {drone7_Speed_update}, Waypoint: {waypointvalue7_update}, Threshold: {Way7_threshold}, Gimbal Pitch: {drone7_GimbalPitch_update}, Gimbal Yaw: {drone7_GimbalYaw_update}, Camera: {drone7_Camera_update}"
        if debug:
            print("Data Being Sent for drone7 (update) :", drone7_waypoint_data_sent, "\n")
        
        ## Check if the drone has reached the waypoint, element (14) of the getImageAndTelemetryData string is set to 1. Extract the image and telemetry data when the condition is met. ## Every time the drone receive the next waypoints this element is set to zero again ion the drone app.
        ## Element 15 is to confirm that the next waypoint data has been successfully received on the app side.
        
        while True:
        
            drone7_send_data = w.sendWayPointData(drone7_waypoint_data, 7) 
            drone7_Image_Telemetry_data = w.getImageAndTelemetryData(7) # 7 refers to the drone number
            drone7_Telemetry_data = (bytearray(drone7_Image_Telemetry_data[3110408:]).decode())
            
            drone7_elements = drone7_Telemetry_data.split(":")                 # Extract all elements from the string
            drone7_Waypoint_sent = drone7_elements[15].split('.')[0]

            if (drone7_Waypoint_sent) == str(incrementor):
                if debug: 
                    print("drone7 Waypoint data sent")
                    print ("run thread for drone7:", drone7_Waypoint_sent, incrementor)
                    
                break # Exit the loop
            

        while True:
            drone7_Image_Telemetry_data = w.getImageAndTelemetryData(7)
            drone7_Telemetry_data = (bytearray(drone7_Image_Telemetry_data[3110408:]).decode())
            
            drone7_elements = drone7_Telemetry_data.split(":")                 # Extract all elements from the string
            drone7_Waypoint_reached = drone7_elements[14]
            
            if drone7_Waypoint_reached == str(incrementor):
                if debug:
                    print("drone7 Waypoint has been reached")
                    print ("run thread waypoint reached:", drone7_Waypoint_reached, incrementor)
                break # Exit the loop
            
        # Hold the drone at the waypoint for a specified length of time
        if drone7_LengthOfStay_update > 0:
            print("drone7_Waypointdata_before_holding:", drone7_Telemetry_data)
        
            print(f'drone7 is waiting for {drone7_LengthOfStay_update} sn before taking the image and saving the telemetry data')   
            time.sleep(drone7_LengthOfStay_update)  
        
        # Call the telemetry data again
        drone7_Image_Telemetry_data = w.getImageAndTelemetryData(7)
        drone7_Telemetry_data = (bytearray(drone7_Image_Telemetry_data[3110408:]).decode())
        
        drone_7_telemetry_elements = drone7_Telemetry_data.split(":")

        latitude = drone_7_telemetry_elements[0] 
        longitude = drone_7_telemetry_elements[1]
        altitude = drone_7_telemetry_elements[2]
        heading = drone_7_telemetry_elements[3]
        gimbal_pitch = drone_7_telemetry_elements[4]
        gimbal_yaw = drone_7_telemetry_elements[6]
        
        if debug:
            reached_data = f"Lat_Reached {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for Updating Parameter for drone7 --->", reached_data, "\n")
            
            print("drone7_Waypointdata (update):", drone7_Telemetry_data)
            
            # Save the telemetry data to a text file inside the results folder
            file_path = os.path.join(Download_Location, 'telemetry7.txt')
            with open(file_path, 'a') as file:
                file.write(drone7_Telemetry_data + '\n')
                
        ## Convert YUV raw data to rgb image and save   ##

        if decoding == 'software':
            drone7_Image = cv2.cvtColor(drone7_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV420p2RGB)
        elif decoding == 'hardware':
            drone7_Image = cv2.cvtColor(drone7_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV2BGR_NV12)
        else:
            print('Please enter a valid decoding method')
        
        
        # Calculate the center of the image
        center_x, center_y = drone7_Image.shape[1] // 2, drone7_Image.shape[0] // 2

        # Calculate the crop region
        crop_start_x = center_x - crop_size // 2
        crop_start_y = center_y - crop_size // 2

        # Crop the image
        cropped_image7 = drone7_Image[crop_start_y:crop_start_y + crop_size, crop_start_x:crop_start_x + crop_size]
        resized_image7 = cv2.resize(cropped_image7, (512, 512))

        drone7_cropped_Image = resized_image7
        
        if debug:
            waypoint_folder = f'drone7_waypoint_{incrementor}_('+ task + ')'
            waypoint_path = os.path.join(Images_Path, waypoint_folder)
            if not os.path.exists(waypoint_path):
                os.mkdir(waypoint_path)
                
            else:
                print("Folder already exists for drone7 (update)")
                
            cv2.imwrite(os.path.join(waypoint_path, 'drone7Image' + str(incrementor)+'.png'), drone7_cropped_Image)
            print("Image is taken and saved for drone7")
        
        if (len(d7Image)) >= 1:
            
            d7Image[0] = (drone7_cropped_Image)
            d7Poses[0] = (drone7_Telemetry_data)
        else:
            
            d7Image.append(drone7_cropped_Image)
            d7Poses.append(drone7_Telemetry_data)
        
        incrementor += 1
        if iteration >= number_of_waypoints_for_drone7:
            with lock:
                drone_7_incrementor = incrementor
                
            with lock:    
                if task == 'waypoint':
                    print("Mission Waypoint for drone7 completed")
                elif task == 'takeoff':
                    print("Takeoff completed for drone7")
                elif task == 'land':
                    print("Land completed for drone7")
                elif task == 'emergency':
                    print("Emergency Case")
                else:
                    print("Invalid task")
                
            break
        
######################## Drone 8 Thread ############################               
d8Image = []
d8Poses = []

def waypoint_tread_drone8(drone8_Latitude_List, drone8_Longitude_list, drone8_Altitude_list, drone8_Heading_list, drone8_Speed_list, Way8_threshold, camera_list, lengthOfStay_list, gimbalPitch_list, gimbalYaw_list):
    # print('Waypoint latitude list for drone8:', drone8_Latitude_List)
    
    number_of_waypoints_for_drone8 = len(drone8_Latitude_List)
    print(f"Number of waypoints for drone8: {number_of_waypoints_for_drone8}")
    
    global drone_8_incrementor, task, drone8_waypoint_no
    
    incrementor = drone_8_incrementor
    
    previous_speed_list_drone8 = [drone8_Speed_list[0], *drone8_Speed_list]
    previous_heading_list_drone8 = [drone8_Heading_list[0], *drone8_Heading_list]
    previous_camera_list_drone8 = [camera_list[0], *camera_list]
    previous_lengthOfStay_list_drone8 = [lengthOfStay_list[0], *lengthOfStay_list]
    previous_gimbalPitch_list_drone8 = [gimbalPitch_list[0], *gimbalPitch_list]
    previous_gimbalYaw_list_drone8 = [gimbalYaw_list[0], *gimbalYaw_list]
    
    iteration = 0
    
    while True:
        
        ### Emergency Case ###  
        if keyboard.is_pressed('i'):
            if not key_pressed_emergency['i']:
                print("Emergency Case")
                key_pressed_emergency['i'] = True
                with lock:
                    drone_8_incrementor = incrementor
                break
        
        with lock:
            if task == 'waypoint':
                drone8_waypoint_no = drone8_waypoint_no + 1
                print(f"Mission Waypoint {iteration+1} in progress for drone8 ...") 

                drone8_Latitude_go = drone8_Latitude_List[iteration]
                drone8_Longitude_go = drone8_Longitude_list[iteration]
                drone8_Altitude_go = drone8_Altitude_list[iteration]
                drone8_Heading_go = previous_heading_list_drone8[iteration]
                drone8_Speed_go = previous_speed_list_drone8[iteration]
                drone8_Camera_go = previous_camera_list_drone8[iteration]
                drone8_LengthOfStay_go = previous_lengthOfStay_list_drone8[iteration]
                drone8_GimbalPitch_go = previous_gimbalPitch_list_drone8[iteration]
                drone8_GimbalYaw_go = previous_gimbalYaw_list_drone8[iteration]
                
                drone8_Latitude_update = drone8_Latitude_List[iteration]
                drone8_Longitude_update = drone8_Longitude_list[iteration]
                drone8_Altitude_update = drone8_Altitude_list[iteration]
                drone8_Heading_update = drone8_Heading_list[iteration]
                drone8_Speed_update = drone8_Speed_list[iteration]
                drone8_Camera_update = camera_list[iteration]
                drone8_LengthOfStay_update = lengthOfStay_list[iteration]
                drone8_GimbalPitch_update = gimbalPitch_list[iteration]
                drone8_GimbalYaw_update = gimbalYaw_list[iteration]
                
                iteration += 1
                
            else:
                
                drone8_Latitude_go = drone8_Latitude_List[iteration]
                drone8_Longitude_go = drone8_Longitude_list[iteration]
                drone8_Altitude_go = drone8_Altitude_list[iteration]
                drone8_Heading_go = drone8_Heading_list[iteration]
                drone8_Speed_go = drone8_Speed_list[iteration]
                drone8_Camera_go = camera_list[iteration]
                drone8_LengthOfStay_go = lengthOfStay_list[iteration]
                drone8_GimbalPitch_go = gimbalPitch_list[iteration]
                drone8_GimbalYaw_go = gimbalYaw_list[iteration]
                
                drone8_Latitude_update = drone8_Latitude_List[iteration + 1]
                drone8_Longitude_update = drone8_Longitude_list[iteration + 1]
                drone8_Altitude_update = drone8_Altitude_list[iteration + 1]
                drone8_Heading_update = drone8_Heading_list[iteration + 1]
                drone8_Speed_update = drone8_Speed_list[iteration + 1]
                drone8_Camera_update = camera_list[iteration + 1]
                drone8_LengthOfStay_update = lengthOfStay_list[iteration + 1]
                drone8_GimbalPitch_update = gimbalPitch_list[iteration + 1]
                drone8_GimbalYaw_update = gimbalYaw_list[iteration + 1]
                
                iteration += 2
                
        waypointvalue8 = incrementor

        ################ for reaching the waypoint ################
        
        print("waypointvalue8_drone8(go):", waypointvalue8)
        drone8_waypoint_data_reached = f"{drone8_Latitude_go}:{drone8_Longitude_go}:{drone8_Altitude_go}:{drone8_Heading_go}:{drone8_Speed_go}:{waypointvalue8}:{Way8_threshold}:{drone8_GimbalPitch_go}:{drone8_GimbalYaw_go}:{drone8_Camera_go}"
        
        drone8_send_data = w.sendWayPointData(drone8_waypoint_data_reached, 8)     # 8 refers to the drone number
        
        drone8_waypoint_data_sent = f"Lat: {drone8_Latitude_go}, Long: {drone8_Longitude_go}, Alt: {drone8_Altitude_go}, Heading: {drone8_Heading_go}, Speed: {drone8_Speed_go}, Waypoint: {waypointvalue8}, Threshold: {Way8_threshold}, Gimbal Pitch: {drone8_GimbalPitch_go}, Gimbal Yaw: {drone8_GimbalYaw_go}, Camera: {drone8_Camera_go}"
        if debug:
            print("Data being Sent for drone8 (go):", drone8_waypoint_data_sent)
        
        ## Check if the drone has reached the waypoint, element (14) of the getImageAndTelemetryData string is set to 1. Extract the image and telemetry data when the condition is met. ## Every time the drone receive the next waypoints this element is set to zero again ion the drone app.
        ## Element 15 is to confirm that the next waypoint data has been successfully received on the app side.
        
        while True:
        
            drone8_send_data = w.sendWayPointData(drone8_waypoint_data_reached, 8) 
            drone8_Image_Telemetry_data = w.getImageAndTelemetryData(8) # 8 refers to the drone number
            drone8_Telemetry_data = (bytearray(drone8_Image_Telemetry_data[3110408:]).decode())
            
            drone8_elements = drone8_Telemetry_data.split(":")                 # Extract all elements from the string
            drone8_Waypoint_sent = drone8_elements[15].split('.')[0]
            if (drone8_Waypoint_sent) == str(incrementor):
                if debug: 
                    print("drone8 Waypoint data sent for go")
                    print ("go thread for drone8:", drone8_Waypoint_sent, incrementor)
                break # Exit the loop
            
        while True:
            drone8_Image_Telemetry_data = w.getImageAndTelemetryData(8)
            drone8_Telemetry_data = (bytearray(drone8_Image_Telemetry_data[3110408:]).decode())
            
            drone8_elements = drone8_Telemetry_data.split(":")                 # Extract all elements from the string
            drone8_Waypoint_reached = drone8_elements[14]
            
            if drone8_Waypoint_reached == str(incrementor):
                if debug:
                    print("drone8 Waypoint has been reached")
                    print ("go thread waypoint reached for drone8:", drone8_Waypoint_reached, incrementor)
                break # Exit the loop
        
        # Call the telemetry data again
        drone8_Image_Telemetry_data = w.getImageAndTelemetryData(8)
        drone8_Telemetry_data = (bytearray(drone8_Image_Telemetry_data[3110408:]).decode())
        
        drone_8_telemetry_elements = drone8_Telemetry_data.split(":")

        latitude = drone_8_telemetry_elements[0] 
        longitude = drone_8_telemetry_elements[1]
        altitude = drone_8_telemetry_elements[2]
        heading = drone_8_telemetry_elements[3]
        gimbal_pitch = drone_8_telemetry_elements[4]
        gimbal_yaw = drone_8_telemetry_elements[6]

        if debug: 
            reached_data = f"Lat_Reached: {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for drone8 (go) --->", reached_data, "\n")
            
            print("drone8_Waypointdata (go):", drone8_Telemetry_data, "\n")  
            
        if drone8_LengthOfStay_go > 0:
            time.sleep(drone8_LengthOfStay_go)   
        
        incrementor += 1
        ################ updating the waypoint ################
        
        waypointvalue8_update = incrementor 
        print("waypointvalue8_drone8(update):", waypointvalue8_update)
        drone8_waypoint_data = f"{drone8_Latitude_update}:{drone8_Longitude_update}:{drone8_Altitude_update}:{drone8_Heading_update}:{drone8_Speed_update}:{waypointvalue8_update}:{Way8_threshold}:{drone8_GimbalPitch_update}:{drone8_GimbalYaw_update}:{drone8_Camera_update}"
        drone8_send_data = w.sendWayPointData(drone8_waypoint_data, 8)     # 8 refers to the drone number
        
        drone8_waypoint_data_sent = f"Lat: {drone8_Latitude_update}, Long: {drone8_Longitude_update}, Alt: {drone8_Altitude_update}, Heading: {drone8_Heading_update}, Speed: {drone8_Speed_update}, Waypoint: {waypointvalue8_update}, Threshold: {Way8_threshold}, Gimbal Pitch: {drone8_GimbalPitch_update}, Gimbal Yaw: {drone8_GimbalYaw_update}, Camera: {drone8_Camera_update}"
        if debug:
            print("Data Being Sent for drone8 (update) :", drone8_waypoint_data_sent, "\n")
        
        ## Check if the drone has reached the waypoint, element (14) of the getImageAndTelemetryData string is set to 1. Extract the image and telemetry data when the condition is met. ## Every time the drone receive the next waypoints this element is set to zero again ion the drone app.
        ## Element 15 is to confirm that the next waypoint data has been successfully received on the app side.
        
        while True:
        
            drone8_send_data = w.sendWayPointData(drone8_waypoint_data, 8) 
            drone8_Image_Telemetry_data = w.getImageAndTelemetryData(8) # 8 refers to the drone number
            drone8_Telemetry_data = (bytearray(drone8_Image_Telemetry_data[3110408:]).decode())
            
            drone8_elements = drone8_Telemetry_data.split(":")                 # Extract all elements from the string
            drone8_Waypoint_sent = drone8_elements[15].split('.')[0]

            if (drone8_Waypoint_sent) == str(incrementor):
                if debug: 
                    print("dron8 Waypoint data sent")
                    print ("run thread for drone8:", drone8_Waypoint_sent, incrementor)
                    
                break # Exit the loop
            
        while True:
            drone8_Image_Telemetry_data = w.getImageAndTelemetryData(8)
            drone8_Telemetry_data = (bytearray(drone8_Image_Telemetry_data[3110408:]).decode())
            
            drone8_elements = drone8_Telemetry_data.split(":")                 # Extract all elements from the string
            drone8_Waypoint_reached = drone8_elements[14]
            
            if drone8_Waypoint_reached == str(incrementor):
                if debug:
                    print("drone8 Waypoint has been reached")
                    print ("run thread waypoint reached:", drone8_Waypoint_reached, incrementor)
                break
            
        # Hold the drone at the waypoint for a specified length of time
        if drone8_LengthOfStay_update > 0:
            print("drone8_Waypointdata_before_holding:", drone8_Telemetry_data)
        
            print(f'drone8 is waiting for {drone8_LengthOfStay_update} sn before taking the image and saving the telemetry data')   
            time.sleep(drone8_LengthOfStay_update)
            
        # Call the telemetry data again
        drone8_Image_Telemetry_data = w.getImageAndTelemetryData(8)
        drone8_Telemetry_data = (bytearray(drone8_Image_Telemetry_data[3110408:]).decode())
        
        drone_8_telemetry_elements = drone8_Telemetry_data.split(":")
        
        latitude = drone_8_telemetry_elements[0]
        longitude = drone_8_telemetry_elements[1]
        altitude = drone_8_telemetry_elements[2]
        heading = drone_8_telemetry_elements[3]
        gimbal_pitch = drone_8_telemetry_elements[4]
        gimbal_yaw = drone_8_telemetry_elements[6]
        
        if debug:
            reached_data = f"Lat_Reached {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for Updating Parameter for drone8 --->", reached_data, "\n")
            
            print("drone8_Waypointdata (update):", drone8_Telemetry_data)
            
            # Save the telemetry data to a text file inside the results folder
            file_path = os.path.join(Download_Location, 'telemetry8.txt')
            with open(file_path, 'a') as file:
                file.write(drone8_Telemetry_data + '\n')
                
        ## Convert YUV raw data to rgb image and save   ##
        if decoding == 'software':
            drone8_Image = cv2.cvtColor(drone8_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV420p2RGB)
        elif decoding == 'hardware':
            drone8_Image = cv2.cvtColor(drone8_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV2BGR_NV12)
        else:
            print('Please enter a valid decoding method')
            
        # Calculate the center of the image
        center_x, center_y = drone8_Image.shape[1] // 2, drone8_Image.shape[0] // 2
        
        # Calculate the crop region
        crop_start_x = center_x - crop_size // 2
        crop_start_y = center_y - crop_size // 2
        
        # Crop the image
        cropped_image8 = drone8_Image[crop_start_y:crop_start_y + crop_size, crop_start_x:crop_start_x + crop_size]
        resized_image8 = cv2.resize(cropped_image8, (512, 512))
        
        drone8_cropped_Image = resized_image8
        
        if debug:
            waypoint_folder = f'drone8_waypoint_{incrementor}_('+ task + ')'
            waypoint_path = os.path.join(Images_Path, waypoint_folder)
            if not os.path.exists(waypoint_path):
                os.mkdir(waypoint_path)
                
            else:
                print("Folder already exists for drone8 (update)")
                
            cv2.imwrite(os.path.join(waypoint_path, 'drone8Image' + str(incrementor)+'.png'), drone8_cropped_Image)
            print("Image is taken and saved for drone8")
            
        if (len(d8Image)) >= 1:
            
            d8Image[0] = (drone8_cropped_Image)
            d8Poses[0] = (drone8_Telemetry_data)
            
        else:
            
            d8Image.append(drone8_cropped_Image)
            d8Poses.append(drone8_Telemetry_data)
            
        incrementor += 1
        if iteration >= number_of_waypoints_for_drone8:
            with lock:
                drone_8_incrementor = incrementor
                
            with lock:    
                if task == 'waypoint':
                    print("Mission Waypoint for drone8 completed")
                elif task == 'takeoff':
                    print("Takeoff completed for drone8")
                elif task == 'land':
                    print("Land completed for drone8")
                elif task == 'emergency':
                    print("Emergency Case")
                else:
                    print("Invalid task")
                
            break
        
######################## Drone 9 Thread ############################
d9Image = []
d9Poses = []

def waypoint_tread_drone9(drone9_Latitude_List, drone9_Longitude_list, drone9_Altitude_list, drone9_Heading_list, drone9_Speed_list, Way9_threshold, camera_list, lengthOfStay_list, gimbalPitch_list, gimbalYaw_list):
    # print('Waypoint latitude list for drone9:', drone9_Latitude_List)
    
    number_of_waypoints_for_drone9 = len(drone9_Latitude_List)
    print(f"Number of waypoints for drone9: {number_of_waypoints_for_drone9}")
    
    global drone_9_incrementor, task, drone9_waypoint_no
    
    incrementor = drone_9_incrementor
    
    previous_speed_list_drone9 = [drone9_Speed_list[0], *drone9_Speed_list]
    previous_heading_list_drone9 = [drone9_Heading_list[0], *drone9_Heading_list]
    previous_camera_list_drone9 = [camera_list[0], *camera_list]
    previous_lengthOfStay_list_drone9 = [lengthOfStay_list[0], *lengthOfStay_list]
    previous_gimbalPitch_list_drone9 = [gimbalPitch_list[0], *gimbalPitch_list]
    previous_gimbalYaw_list_drone9 = [gimbalYaw_list[0], *gimbalYaw_list]
    
    iteration = 0
    
    while True:
        
        ### Emergency Case ###  
        if keyboard.is_pressed('i'):
            if not key_pressed_emergency['i']:
                print("Emergency Case")
                key_pressed_emergency['i'] = True
                with lock:
                    drone_9_incrementor = incrementor
                break
        
        with lock:
            if task == 'waypoint':
                drone9_waypoint_no = drone9_waypoint_no + 1
                print(f"Mission Waypoint {iteration+1} in progress for drone9 ...") 

                drone9_Latitude_go = drone9_Latitude_List[iteration]
                drone9_Longitude_go = drone9_Longitude_list[iteration]
                drone9_Altitude_go = drone9_Altitude_list[iteration]
                drone9_Heading_go = previous_heading_list_drone9[iteration]
                drone9_Speed_go = previous_speed_list_drone9[iteration]
                drone9_Camera_go = previous_camera_list_drone9[iteration]
                drone9_LengthOfStay_go = previous_lengthOfStay_list_drone9[iteration]
                drone9_GimbalPitch_go = previous_gimbalPitch_list_drone9[iteration]
                drone9_GimbalYaw_go = previous_gimbalYaw_list_drone9[iteration]
                
                drone9_Latitude_update = drone9_Latitude_List[iteration]
                drone9_Longitude_update = drone9_Longitude_list[iteration]
                drone9_Altitude_update = drone9_Altitude_list[iteration]
                drone9_Heading_update = drone9_Heading_list[iteration]
                drone9_Speed_update = drone9_Speed_list[iteration]
                drone9_Camera_update = camera_list[iteration]
                drone9_LengthOfStay_update = lengthOfStay_list[iteration]
                drone9_GimbalPitch_update = gimbalPitch_list[iteration]
                drone9_GimbalYaw_update = gimbalYaw_list[iteration]
                
                iteration += 1
                
            else:
                
                drone9_Latitude_go = drone9_Latitude_List[iteration]
                drone9_Longitude_go = drone9_Longitude_list[iteration]
                drone9_Altitude_go = drone9_Altitude_list[iteration]
                drone9_Heading_go = drone9_Heading_list[iteration]
                drone9_Speed_go = drone9_Speed_list[iteration]
                drone9_Camera_go = camera_list[iteration]
                drone9_LengthOfStay_go = lengthOfStay_list[iteration]
                drone9_GimbalPitch_go = gimbalPitch_list[iteration]
                drone9_GimbalYaw_go = gimbalYaw_list[iteration]
                
                drone9_Latitude_update = drone9_Latitude_List[iteration + 1]
                drone9_Longitude_update = drone9_Longitude_list[iteration + 1]
                drone9_Altitude_update = drone9_Altitude_list[iteration + 1]
                drone9_Heading_update = drone9_Heading_list[iteration + 1]
                drone9_Speed_update = drone9_Speed_list[iteration + 1]
                drone9_Camera_update = camera_list[iteration + 1]
                drone9_LengthOfStay_update = lengthOfStay_list[iteration + 1]
                drone9_GimbalPitch_update = gimbalPitch_list[iteration + 1]
                drone9_GimbalYaw_update = gimbalYaw_list[iteration + 1]
                
                iteration += 2
                
        waypointvalue9 = incrementor

        ################ for reaching the waypoint ################
        
        print("waypointvalue9_drone9(go):",waypointvalue9)
        drone9_waypoint_data_reached = f"{drone9_Latitude_go}:{drone9_Longitude_go}:{drone9_Altitude_go}:{drone9_Heading_go}:{drone9_Speed_go}:{waypointvalue9}:{Way9_threshold}:{drone9_GimbalPitch_go}:{drone9_GimbalYaw_go}:{drone9_Camera_go}"
        
        drone9_send_data = w.sendWayPointData(drone9_waypoint_data_reached, 9)     # 9 refers to the drone number
        
        drone9_waypoint_data_sent = f"Lat: {drone9_Latitude_go}, Long: {drone9_Longitude_go}, Alt: {drone9_Altitude_go}, Heading: {drone9_Heading_go}, Speed: {drone9_Speed_go}, Waypoint: {waypointvalue9}, Threshold: {Way9_threshold}, Gimbal Pitch: {drone9_GimbalPitch_go}, Gimbal Yaw: {drone9_GimbalYaw_go}, Camera: {drone9_Camera_go}"
        if debug:
            print("Data being Sent for drone9 (go):",drone9_waypoint_data_sent)
        
        while True:
        
            drone9_send_data = w.sendWayPointData(drone9_waypoint_data_reached, 9) 
            drone9_Image_Telemetry_data = w.getImageAndTelemetryData(9) # 9 refers to the drone number
            drone9_Telemetry_data = (bytearray(drone9_Image_Telemetry_data[3110408:]).decode())
            
            drone9_elements = drone9_Telemetry_data.split(":")                 # Extract all elements from the string
            drone9_Waypoint_sent = drone9_elements[15].split('.')[0]
            if (drone9_Waypoint_sent) == str(incrementor):
                if debug: 
                    print("drone9 Waypoint data sent for go")
                    print ("go thread for drone9:", drone9_Waypoint_sent, incrementor)
                break # Exit the loop
            
        while True:
            drone9_Image_Telemetry_data = w.getImageAndTelemetryData(9)
            drone9_Telemetry_data = (bytearray(drone9_Image_Telemetry_data[3110408:]).decode())
            
            drone9_elements = drone9_Telemetry_data.split(":")                 # Extract all elements from the string
            drone9_Waypoint_reached = drone9_elements[14]
            
            if drone9_Waypoint_reached == str(incrementor):
                if debug:
                    print("drone9 Waypoint has been reached")
                    print ("go thread waypoint reached for drone9:", drone9_Waypoint_reached, incrementor)
                break # Exit the loop
        
        # Call the telemetry data again
        drone9_Image_Telemetry_data = w.getImageAndTelemetryData(9)
        drone9_Telemetry_data = (bytearray(drone9_Image_Telemetry_data[3110408:]).decode())
        
        drone_9_telemetry_elements = drone9_Telemetry_data.split(":")

        latitude = drone_9_telemetry_elements[0] 
        longitude = drone_9_telemetry_elements[1]
        altitude = drone_9_telemetry_elements[2]
        heading = drone_9_telemetry_elements[3]
        gimbal_pitch = drone_9_telemetry_elements[4]
        gimbal_yaw = drone_9_telemetry_elements[6]

        if debug: 
            reached_data = f"Lat_Reached: {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for drone9 (go) --->", reached_data, "\n")
            
            print("drone9_Waypointdata (go):", drone9_Telemetry_data, "\n")  
            
        if drone9_LengthOfStay_go > 0:
            time.sleep(drone9_LengthOfStay_go)   
        
        incrementor += 1
        ################ updating the waypoint ################
        
        waypointvalue9_update = incrementor 
        print("waypointvalue9_drone9(update):",waypointvalue9_update)
        drone9_waypoint_data = f"{drone9_Latitude_update}:{drone9_Longitude_update}:{drone9_Altitude_update}:{drone9_Heading_update}:{drone9_Speed_update}:{waypointvalue9_update}:{Way9_threshold}:{drone9_GimbalPitch_update}:{drone9_GimbalYaw_update}:{drone9_Camera_update}"
        drone9_send_data = w.sendWayPointData(drone9_waypoint_data, 9)     # 9 refers to the drone number
        
        drone9_waypoint_data_sent = f"Lat: {drone9_Latitude_update}, Long: {drone9_Longitude_update}, Alt: {drone9_Altitude_update}, Heading: {drone9_Heading_update}, Speed: {drone9_Speed_update}, Waypoint: {waypointvalue9_update}, Threshold: {Way9_threshold}, Gimbal Pitch: {drone9_GimbalPitch_update}, Gimbal Yaw: {drone9_GimbalYaw_update}, Camera: {drone9_Camera_update}"
        if debug:
            print("Data Being Sent for drone9 (update) :",drone9_waypoint_data_sent, "\n")
        
        while True:
        
            drone9_send_data = w.sendWayPointData(drone9_waypoint_data, 9) 
            drone9_Image_Telemetry_data = w.getImageAndTelemetryData(9) # 9 refers to the drone number
            drone9_Telemetry_data = (bytearray(drone9_Image_Telemetry_data[3110408:]).decode())
            
            drone9_elements = drone9_Telemetry_data.split(":")                 # Extract all elements from the string
            drone9_Waypoint_sent = drone9_elements[15].split('.')[0]

            if (drone9_Waypoint_sent) == str(incrementor):
                if debug: 
                    print("drone9 Waypoint data sent")
                    print ("run thread for drone9:", drone9_Waypoint_sent, incrementor)
                    
                break # Exit the loop
            

        while True:
            drone9_Image_Telemetry_data = w.getImageAndTelemetryData(9)
            drone9_Telemetry_data = (bytearray(drone9_Image_Telemetry_data[3110408:]).decode())
            
            drone9_elements = drone9_Telemetry_data.split(":")                 # Extract all elements from the string
            drone9_Waypoint_reached = drone9_elements[14]
            
            if drone9_Waypoint_reached == str(incrementor):
                if debug:
                    print("drone9 Waypoint has been reached")
                    print ("run thread waypoint reached:", drone9_Waypoint_reached, incrementor)
                break # Exit the loop
            
        # Hold the drone at the waypoint for a specified length of time
        if drone9_LengthOfStay_update > 0:
            print("drone9_Waypointdata_before_holding:", drone9_Telemetry_data)
        
            print(f'drone9 is waiting  for {drone9_LengthOfStay_update} sn before taking the image and saving the telemetry data')   
            time.sleep(drone9_LengthOfStay_update)  
        
        # Call the telemetry data again
        drone9_Image_Telemetry_data = w.getImageAndTelemetryData(9)
        drone9_Telemetry_data = (bytearray(drone9_Image_Telemetry_data[3110408:]).decode())
        
        drone_9_telemetry_elements = drone9_Telemetry_data.split(":")

        latitude = drone_9_telemetry_elements[0] 
        longitude = drone_9_telemetry_elements[1]
        altitude = drone_9_telemetry_elements[2]
        heading = drone_9_telemetry_elements[3]
        gimbal_pitch = drone_9_telemetry_elements[4]
        gimbal_yaw = drone_9_telemetry_elements[6]
        
        if debug:
            reached_data = f"Lat_Reached {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for Updating Parameter for drone9 --->",reached_data, "\n")
            
            print("drone9_Waypointdata (update):", drone9_Telemetry_data)
            
            # Save the telemetry data to a text file inside the results folder
            file_path = os.path.join(Download_Location, 'telemetry9.txt')
            with open(file_path, 'a') as file:
                file.write(drone9_Telemetry_data + '\n')
                
        ## Covert YUV raw data to rgb image and save   ##

        if decoding == 'software':
            drone9_Image = cv2.cvtColor(drone9_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV420p2RGB)
        elif decoding == 'hardware':
            drone9_Image = cv2.cvtColor(drone9_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV2BGR_NV12)
        else:
            print('Please enter a valid decoding method')   
            
        # Calculate the center of the image
        center_x, center_y = drone9_Image.shape[1] // 2, drone9_Image.shape[0] // 2

        # Calculate the crop region
        crop_start_x = center_x - crop_size // 2
        crop_start_y = center_y - crop_size // 2

        # Crop the image
        cropped_image9 = drone9_Image[crop_start_y:crop_start_y + crop_size, crop_start_x:crop_start_x + crop_size]
        resized_image9 = cv2.resize(cropped_image9, (512, 512))

        drone9_cropped_Image = resized_image9
        
        if debug:
            waypoint_folder = f'drone9_waypoint_{incrementor}_('+ task + ')'
            waypoint_path = os.path.join(Images_Path, waypoint_folder)
            if not os.path.exists(waypoint_path):
                os.mkdir(waypoint_path)
                
            else:
                print("Folder already exists for drone9 (update)")
                
            cv2.imwrite(os.path.join( waypoint_path, 'drone9Image' + str(incrementor)+'.png'), drone9_cropped_Image)
            print("Image is taken and saved for drone9")
        
        if (len(d9Image)) >= 1:
            d9Image[0] = (drone9_cropped_Image)
            d9Poses[0] = (drone9_Telemetry_data)
        else:
            d9Image.append(drone9_cropped_Image)
            d9Poses.append(drone9_Telemetry_data)
        
        incrementor += 1
        if iteration >= number_of_waypoints_for_drone9:
            with lock:
                drone_9_incrementor = incrementor
                
            with lock:    
                if task == 'waypoint':
                    print("Mission Waypoint for drone9 completed")
                elif task == 'takeoff':
                    print("Takeoff completed for drone9")
                elif task == 'land':
                    print("Land completed for drone9")
                elif task == 'emergency':
                    print("Emergency Case")
                else:
                    print("Invalid task")
                
            break

######################## Drone 10 Thread ############################

d10Image = []
d10Poses = []

def waypoint_tread_drone10(drone10_Latitude_List, drone10_Longitude_list, drone10_Altitude_list, drone10_Heading_list, drone10_Speed_list, Way10_threshold, camera_list, lengthOfStay_list, gimbalPitch_list, gimbalYaw_list):
    # print('Waypoint latitude list for drone10:', drone10_Latitude_List)
    
    number_of_waypoints_for_drone10 = len(drone10_Latitude_List)
    print(f"Number of waypoints for drone10: {number_of_waypoints_for_drone10}")
    
    global drone_10_incrementor, task, drone10_waypoint_no
    
    incrementor = drone_10_incrementor
    
    previous_speed_list_drone10 = [drone10_Speed_list[0], *drone10_Speed_list]
    previous_heading_list_drone10 = [drone10_Heading_list[0], *drone10_Heading_list]
    previous_camera_list_drone10 = [camera_list[0], *camera_list]
    previous_lengthOfStay_list_drone10 = [lengthOfStay_list[0], *lengthOfStay_list]
    previous_gimbalPitch_list_drone10 = [gimbalPitch_list[0], *gimbalPitch_list]
    previous_gimbalYaw_list_drone10 = [gimbalYaw_list[0], *gimbalYaw_list]
    
    iteration = 0
    
    while True:
        
        ### Emergency Case ###  
        if keyboard.is_pressed('i'):
            if not key_pressed_emergency['i']:
                print("Emergency Case")
                key_pressed_emergency['i'] = True
                with lock:
                    drone_10_incrementor = incrementor
                break
        
        with lock:
            if task == 'waypoint':
                drone10_waypoint_no = drone10_waypoint_no + 1
                print(f"Mission Waypoint {iteration+1} in progress for drone10 ...") 

                drone10_Latitude_go = drone10_Latitude_List[iteration]
                drone10_Longitude_go = drone10_Longitude_list[iteration]
                drone10_Altitude_go = drone10_Altitude_list[iteration]
                drone10_Heading_go = previous_heading_list_drone10[iteration]
                drone10_Speed_go = previous_speed_list_drone10[iteration]
                drone10_Camera_go = previous_camera_list_drone10[iteration]
                drone10_LengthOfStay_go = previous_lengthOfStay_list_drone10[iteration]
                drone10_GimbalPitch_go = previous_gimbalPitch_list_drone10[iteration]
                drone10_GimbalYaw_go = previous_gimbalYaw_list_drone10[iteration]
                
                drone10_Latitude_update = drone10_Latitude_List[iteration]
                drone10_Longitude_update = drone10_Longitude_list[iteration]
                drone10_Altitude_update = drone10_Altitude_list[iteration]
                drone10_Heading_update = drone10_Heading_list[iteration]
                drone10_Speed_update = drone10_Speed_list[iteration]
                drone10_Camera_update = camera_list[iteration]
                drone10_LengthOfStay_update = lengthOfStay_list[iteration]
                drone10_GimbalPitch_update = gimbalPitch_list[iteration]
                drone10_GimbalYaw_update = gimbalYaw_list[iteration]
                
                iteration += 1
                
            else:
                
                drone10_Latitude_go = drone10_Latitude_List[iteration]
                drone10_Longitude_go = drone10_Longitude_list[iteration]
                drone10_Altitude_go = drone10_Altitude_list[iteration]
                drone10_Heading_go = drone10_Heading_list[iteration]
                drone10_Speed_go = drone10_Speed_list[iteration]
                drone10_Camera_go = camera_list[iteration]
                drone10_LengthOfStay_go = lengthOfStay_list[iteration]
                drone10_GimbalPitch_go = gimbalPitch_list[iteration]
                drone10_GimbalYaw_go = gimbalYaw_list[iteration]
                
                drone10_Latitude_update = drone10_Latitude_List[iteration + 1]
                drone10_Longitude_update = drone10_Longitude_list[iteration + 1]
                drone10_Altitude_update = drone10_Altitude_list[iteration + 1]
                drone10_Heading_update = drone10_Heading_list[iteration + 1]
                drone10_Speed_update = drone10_Speed_list[iteration + 1]
                drone10_Camera_update = camera_list[iteration + 1]
                drone10_LengthOfStay_update = lengthOfStay_list[iteration + 1]
                drone10_GimbalPitch_update = gimbalPitch_list[iteration + 1]
                drone10_GimbalYaw_update = gimbalYaw_list[iteration + 1]
                
                iteration += 2
                
        waypointvalue10 = incrementor

        ################ for reaching the waypoint ################
        
        print("waypointvalue10_drone10(go):",waypointvalue10)
        drone10_waypoint_data_reached = f"{drone10_Latitude_go}:{drone10_Longitude_go}:{drone10_Altitude_go}:{drone10_Heading_go}:{drone10_Speed_go}:{waypointvalue10}:{Way10_threshold}:{drone10_GimbalPitch_go}:{drone10_GimbalYaw_go}:{drone10_Camera_go}"
        
        drone10_send_data = w.sendWayPointData(drone10_waypoint_data_reached, 10)     # 10 refers to the drone number
        
        drone10_waypoint_data_sent = f"Lat: {drone10_Latitude_go}, Long: {drone10_Longitude_go}, Alt: {drone10_Altitude_go}, Heading: {drone10_Heading_go}, Speed: {drone10_Speed_go}, Waypoint: {waypointvalue10}, Threshold: {Way10_threshold}, Gimbal Pitch: {drone10_GimbalPitch_go}, Gimbal Yaw: {drone10_GimbalYaw_go}, Camera: {drone10_Camera_go}"
        if debug:
            print("Data being Sent for drone10 (go):",drone10_waypoint_data_sent)
        
        while True:
        
            drone10_send_data = w.sendWayPointData(drone10_waypoint_data_reached, 10) 
            drone10_Image_Telemetry_data = w.getImageAndTelemetryData(10) # 10 refers to the drone number
            drone10_Telemetry_data = (bytearray(drone10_Image_Telemetry_data[3110408:]).decode())
            
            drone10_elements = drone10_Telemetry_data.split(":")                 # Extract all elements from the string
            drone10_Waypoint_sent = drone10_elements[15].split('.')[0]
            if (drone10_Waypoint_sent) == str(incrementor):
                if debug: 
                    print("drone10 Waypoint data sent for go")
                    print ("go thread for drone10:", drone10_Waypoint_sent, incrementor)
                break # Exit the loop
            
        while True:
            drone10_Image_Telemetry_data = w.getImageAndTelemetryData(10)
            drone10_Telemetry_data = (bytearray(drone10_Image_Telemetry_data[3110408:]).decode())
            
            drone10_elements = drone10_Telemetry_data.split(":")                 # Extract all elements from the string
            drone10_Waypoint_reached = drone10_elements[14]
            
            if drone10_Waypoint_reached == str(incrementor):
                if debug:
                    print("drone10 Waypoint has been reached")
                    print ("go thread waypoint reached for drone10:", drone10_Waypoint_reached, incrementor)
                break # Exit the loop
        
        # Call the telemetry data again
        drone10_Image_Telemetry_data = w.getImageAndTelemetryData(10)
        drone10_Telemetry_data = (bytearray(drone10_Image_Telemetry_data[3110408:]).decode())
        
        drone_10_telemetry_elements = drone10_Telemetry_data.split(":")

        latitude = drone_10_telemetry_elements[0] 
        longitude = drone_10_telemetry_elements[1]
        altitude = drone_10_telemetry_elements[2]
        heading = drone_10_telemetry_elements[3]
        gimbal_pitch = drone_10_telemetry_elements[4]
        gimbal_yaw = drone_10_telemetry_elements[6]

        if debug: 
            reached_data = f"Lat_Reached: {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for drone10 (go) --->", reached_data, "\n")
            
            print("drone10_Waypointdata (go):", drone10_Telemetry_data, "\n")  
            
        if drone10_LengthOfStay_go > 0:
            time.sleep(drone10_LengthOfStay_go)   
        
        incrementor += 1
        ################ updating the waypoint ################
        
        waypointvalue10_update = incrementor 
        print("waypointvalue10_drone10(update):",waypointvalue10_update)
        drone10_waypoint_data = f"{drone10_Latitude_update}:{drone10_Longitude_update}:{drone10_Altitude_update}:{drone10_Heading_update}:{drone10_Speed_update}:{waypointvalue10_update}:{Way10_threshold}:{drone10_GimbalPitch_update}:{drone10_GimbalYaw_update}:{drone10_Camera_update}"
        drone10_send_data = w.sendWayPointData(drone10_waypoint_data, 10)     # 10 refers to the drone number
        
        drone10_waypoint_data_sent = f"Lat: {drone10_Latitude_update}, Long: {drone10_Longitude_update}, Alt: {drone10_Altitude_update}, Heading: {drone10_Heading_update}, Speed: {drone10_Speed_update}, Waypoint: {waypointvalue10_update}, Threshold: {Way10_threshold}, Gimbal Pitch: {drone10_GimbalPitch_update}, Gimbal Yaw: {drone10_GimbalYaw_update}, Camera: {drone10_Camera_update}"
        if debug:
            print("Data Being Sent for drone10 (update) :",drone10_waypoint_data_sent, "\n")
        
        while True:
        
            drone10_send_data = w.sendWayPointData(drone10_waypoint_data, 10) 
            drone10_Image_Telemetry_data = w.getImageAndTelemetryData(10) # 10 refers to the drone number
            drone10_Telemetry_data = (bytearray(drone10_Image_Telemetry_data[3110408:]).decode())
            
            drone10_elements = drone10_Telemetry_data.split(":")                 # Extract all elements from the string
            drone10_Waypoint_sent = drone10_elements[15].split('.')[0]

            if (drone10_Waypoint_sent) == str(incrementor):
                if debug: 
                    print("drone10 Waypoint data sent")
                    print ("run thread for drone10:", drone10_Waypoint_sent, incrementor)
                    
                break # Exit the loop
            

        while True:
            drone10_Image_Telemetry_data = w.getImageAndTelemetryData(10)
            drone10_Telemetry_data = (bytearray(drone10_Image_Telemetry_data[3110408:]).decode())
            
            drone10_elements = drone10_Telemetry_data.split(":")                 # Extract all elements from the string
            drone10_Waypoint_reached = drone10_elements[14]
            
            if drone10_Waypoint_reached == str(incrementor):
                if debug:
                    print("drone10 Waypoint has been reached")
                    print ("run thread waypoint reached:", drone10_Waypoint_reached, incrementor)
                break # Exit the loop
            
        # Hold the drone at the waypoint for a specified length of time
        if drone10_LengthOfStay_update > 0:
            print("drone10_Waypointdata_before_holding:", drone10_Telemetry_data)
        
            print(f'drone10 is waiting  for {drone10_LengthOfStay_update} sn before taking the image and saving the telemetry data')   
            time.sleep(drone10_LengthOfStay_update)  
        
        # Call the telemetry data again
        drone10_Image_Telemetry_data = w.getImageAndTelemetryData(10)
        drone10_Telemetry_data = (bytearray(drone10_Image_Telemetry_data[3110408:]).decode())
        
        drone_10_telemetry_elements = drone10_Telemetry_data.split(":")

        latitude = drone_10_telemetry_elements[0] 
        longitude = drone_10_telemetry_elements[1]
        altitude = drone_10_telemetry_elements[2]
        heading = drone_10_telemetry_elements[3]
        gimbal_pitch = drone_10_telemetry_elements[4]
        gimbal_yaw = drone_10_telemetry_elements[6]
        
        if debug:
            reached_data = f"Lat_Reached {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for Updating Parameter for drone10 --->",reached_data, "\n")
            
            print("drone10_Waypointdata (update):", drone10_Telemetry_data)
            
            # Save the telemetry data to a text file inside the results folder
            file_path = os.path.join(Download_Location, 'telemetry10.txt')
            with open(file_path, 'a') as file:
                file.write(drone10_Telemetry_data + '\n')
                
        ## Covert YUV raw data to rgb image and save   ##

        if decoding == 'software':
            drone10_Image = cv2.cvtColor(drone10_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV420p2RGB)
        elif decoding == 'hardware':
            drone10_Image = cv2.cvtColor(drone10_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV2BGR_NV12)
        else:
            print('Please enter a valid decoding method')
        
        
        # Calculate the center of the image
        center_x, center_y = drone10_Image.shape[1] // 2, drone10_Image.shape[0] // 2

        # Calculate the crop region
        crop_start_x = center_x - crop_size // 2
        crop_start_y = center_y - crop_size // 2

        # Crop the image
        cropped_image10 = drone10_Image[crop_start_y:crop_start_y + crop_size, crop_start_x:crop_start_x + crop_size]
        resized_image10 = cv2.resize(cropped_image10, (512, 512))

        drone10_cropped_Image = resized_image10
        
        if debug:
            waypoint_folder = f'drone10_waypoint_{incrementor}_('+ task + ')'
            waypoint_path = os.path.join(Images_Path, waypoint_folder)
            if not os.path.exists(waypoint_path):
                os.mkdir(waypoint_path)
                
            else:
                print("Folder already exists for drone10 (update)")
                
            cv2.imwrite(os.path.join( waypoint_path, 'drone10Image' + str(incrementor)+'.png'), drone10_cropped_Image)
            print("Image is taken and saved for drone10")
        
        if (len(d10Image)) >= 1:
            d10Image[0] = (drone10_cropped_Image)
            d10Poses[0] = (drone10_Telemetry_data)
        else:
            d10Image.append(drone10_cropped_Image)
            d10Poses.append(drone10_Telemetry_data)
        
        incrementor += 1
        if iteration >= number_of_waypoints_for_drone10:
            with lock:
                drone_10_incrementor = incrementor
                
            with lock:    
                if task == 'waypoint':
                    print("Mission Waypoint for drone10 completed")
                elif task == 'takeoff':
                    print("Takeoff completed for drone10")
                elif task == 'land':
                    print("Land completed for drone10")
                elif task == 'emergency':
                    print("Emergency Case")
                else:
                    print("Invalid task")
                
            break
        
######################### Taking Waypoint Data and Sending if there is no waypoint data coming from the server ############################
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

received_drone_data = None

class DroneDataHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        """Sets headers required for CORS"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        """Respond to a CORS preflight request"""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
        
    def save_data(self, data):
        """Saves data to a file"""
        with open('waypoint_mission.json', 'w') as file:
            json.dump(data, file)

    def load_data(self):
        """Loads data from a file"""
        try:
            with open('waypoint_mission.json', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
    def do_POST(self):
        global received_drone_data

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        received_drone_data = json.loads(post_data.decode('utf-8'))
        print("Received data:", received_drone_data)

        if not received_drone_data == str({}):
            # Save the received data if it is not empty
            self.save_data(received_drone_data)
        else:
            # If received data is empty, load previously saved data
            received_drone_data = self.load_data()
            print("Loaded saved data:", received_drone_data)

        # Send back the received or loaded data to the client
        response_data = json.dumps(received_drone_data)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self._send_cors_headers()
        self.end_headers()

        self.wfile.write(response_data.encode('utf-8'))
        
        # Stop the server
        def shutdown_server():
            print("Server stopped")
            self.server.shutdown()

        threading.Thread(target=shutdown_server).start()

def run_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, DroneDataHandler)
    print('Server started')
    httpd.serve_forever()
    
######################### Parsing the received data and sending it to the drones ############################ 
print("Data Streaming has started")
thread_data_streaming = threading.Thread(target=publisher_thread, args=(broker, port, topic, username, password))
thread_data_streaming.start()

# Waypoint data server

server_thread = threading.Thread(target=run_server)
server_thread.start()
server_thread.join()

# Parse the JSON data
data = json.loads(received_drone_data)

# Iterate through each drone's data to dynamically create arrays for each parameter
for drone_id, waypoints in data.items():
    drone_id = int(drone_id)
    globals()[f'drone_{drone_id}_waypoint_lat'] = []
    globals()[f'drone_{drone_id}_waypoint_lng'] = []
    globals()[f'drone_{drone_id}_waypoint_speed'] = []
    globals()[f'drone_{drone_id}_waypoint_lengthOfStay'] = []
    globals()[f'drone_{drone_id}_waypoint_altitude'] = []
    globals()[f'drone_{drone_id}_waypoint_camera'] = []
    globals()[f'drone_{drone_id}_waypoint_gimbalPitch'] = []
    globals()[f'drone_{drone_id}_waypoint_gimbalYaw'] = []
    globals()[f'drone_{drone_id}_waypoint_heading'] = []	
    
    for waypoint in waypoints:
        globals()[f'drone_{drone_id}_waypoint_lat'].append(waypoint['lat'])
        globals()[f'drone_{drone_id}_waypoint_lng'].append(waypoint['lng'])
        globals()[f'drone_{drone_id}_waypoint_speed'].append(float(waypoint['speed']))
        globals()[f'drone_{drone_id}_waypoint_lengthOfStay'].append(float(waypoint['lengthOfStay']))
        globals()[f'drone_{drone_id}_waypoint_altitude'].append(float(waypoint['altitude']))
        globals()[f'drone_{drone_id}_waypoint_camera'].append(waypoint['camera'])
        globals()[f'drone_{drone_id}_waypoint_gimbalPitch'].append(float(waypoint['gimbalPitch']))
        globals()[f'drone_{drone_id}_waypoint_gimbalYaw'].append(float(waypoint['gimbalYaw']))
        globals()[f'drone_{drone_id}_waypoint_heading'].append(float(waypoint['heading']))
        

# # Check the gimbal pitch and yaw values for each drone to ensure they are within the range of -135 to 45 degrees for pitch and -27 to 27 degrees for yaw. 
# # if the values are outside the range, set them to the maximum or minimum value
for drone_id in data.keys():
    drone_id = int(drone_id)
    number_of_waypoints = len(globals()[f'drone_{drone_id}_waypoint_lat'])
    for i in range(number_of_waypoints):
        # if globals()[f'drone_{drone_id}_waypoint_gimbalPitch'][i] > 35:
        #     globals()[f'drone_{drone_id}_waypoint_gimbalPitch'][i] = 35
        # elif globals()[f'drone_{drone_id}_waypoint_gimbalPitch'][i] < -90:
        #     globals()[f'drone_{drone_id}_waypoint_gimbalPitch'][i] = -90

        # if globals()[f'drone_{drone_id}_waypoint_gimbalYaw'][i] > 15:
        #     globals()[f'drone_{drone_id}_waypoint_gimbalYaw'][i] = 15
        # elif globals()[f'drone_{drone_id}_waypoint_gimbalYaw'][i] < -15:
        #     globals()[f'drone_{drone_id}_waypoint_gimbalYaw'][i] = -15

        # Map cameras to their respective indices
        if globals()[f'drone_{drone_id}_waypoint_camera'][i] == 'wide angle': # RGB
            globals()[f'drone_{drone_id}_waypoint_camera'][i] = 90
        elif globals()[f'drone_{drone_id}_waypoint_camera'][i] == 'tele':
            globals()[f'drone_{drone_id}_waypoint_camera'][i] = 92
        elif globals()[f'drone_{drone_id}_waypoint_camera'][i] == 'thermal image':
            globals()[f'drone_{drone_id}_waypoint_camera'][i] = 91
        elif globals()[f'drone_{drone_id}_waypoint_camera'][i] == 'anomaly':
            globals()[f'drone_{drone_id}_waypoint_camera'][i] = 93
        elif globals()[f'drone_{drone_id}_waypoint_camera'][i] == 'integral (RGB)':
            globals()[f'drone_{drone_id}_waypoint_camera'][i] = 94
        elif globals()[f'drone_{drone_id}_waypoint_camera'][i] == 'integral (thermal)':
            globals()[f'drone_{drone_id}_waypoint_camera'][i] = 95
        elif globals()[f'drone_{drone_id}_waypoint_camera'][i] == 'integral (anomaly)':
            globals()[f'drone_{drone_id}_waypoint_camera'][i] = 96
        else:
            globals()[f'drone_{drone_id}_waypoint_camera'][i] = 90 # Default to wide angle
            
        # convert headings from (0, 360) to (-180, 180)
        if globals()[f'drone_{drone_id}_waypoint_heading'][i] > 180:
            globals()[f'drone_{drone_id}_waypoint_heading'][i] = globals()[f'drone_{drone_id}_waypoint_heading'][i] - 360
            
        # gimbal yaw values without drone heading


with lock:
    num_drones = len(connected_drones)
print("Number of drones for waypoint sending:", num_drones)
# End of the waypoint data server

# Heading Arrangement

land_altitude = 2 # Altitude for landing for each drone

heading_list = []
init_latitude_list = []
init_longitude_list = []
if num_drones >= 1:
    drone1_Image_Telemetry_data = w.getImageAndTelemetryData(1)
    drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[3110408:]).decode())
    drone1_elements = drone1_Telemetry_data.split(":")                 # Extract all elements from the string. 
    drone1_latitude = drone1_elements[0]
    drone1_longitude = drone1_elements[1]
    
    # dummy values for latitude and longitude
    
    # drone1_latitude = 48.337049827520666
    # drone1_longitude = 14.320859898638385
    
    drone1_heading = drone1_elements[3]
    heading_list.append(drone1_heading)
    init_latitude_list.append(drone1_latitude)
    init_longitude_list.append(drone1_longitude)
    # print(f'drone1_latitude: {drone1_latitude}', f'drone1_longitude: {drone1_longitude}', f'drone1_heading: {drone1_heading}')
    
    # waypoints for drone1
    drone1_Latitude_list_takeoff_land = [drone1_latitude]                                 
    drone1_Longitude_list_takeoff_land = [drone1_longitude]
    drone1_Altitude_takeoff_land = [globals()[f'drone_1_waypoint_altitude'][0], land_altitude]
    
if num_drones >= 2:
    drone2_Image_Telemetry_data = w.getImageAndTelemetryData(2)
    drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[3110408:]).decode())
    drone2_elements = drone2_Telemetry_data.split(":")                 # Extract all elements from the string.
    drone2_latitude = drone2_elements[0]
    drone2_longitude = drone2_elements[1]
    
    # # dummy values for latitude and longitude
    # drone2_latitude = 48.336994554754455
    # drone2_longitude = 14.320847822201294
    
    drone2_heading = drone2_elements[3]
    heading_list.append(drone2_heading)
    init_latitude_list.append(drone2_latitude)
    init_longitude_list.append(drone2_longitude)
    # print(f'drone2_latitude: {drone2_latitude}', f'drone2_longitude: {drone2_longitude}', f'drone2_heading: {drone2_heading}')
    
    # waypoints for drone2
    drone2_Latitude_list_takeoff_land = [drone2_latitude]
    drone2_Longitude_list_takeoff_land = [drone2_longitude]
    drone2_Altitude_takeoff_land = [globals()[f'drone_2_waypoint_altitude'][0], land_altitude]
    

if num_drones >= 3:
    drone3_Image_Telemetry_data = w.getImageAndTelemetryData(3)
    drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[3110408:]).decode())
    drone3_elements = drone3_Telemetry_data.split(":")                 # Extract all elements from the string.
    drone3_latitude = drone3_elements[0]
    drone3_longitude = drone3_elements[1]
    
    # # dummy values for latitude and longitude
    # drone3_latitude = 48.33693304144421
    # drone3_longitude = 14.320834403937875
    
    drone3_heading = drone3_elements[3]
    heading_list.append(drone3_heading)
    init_latitude_list.append(drone3_latitude)
    init_longitude_list.append(drone3_longitude)
    # print(f'drone3_latitude: {drone3_latitude}', f'drone3_longitude: {drone3_longitude}', f'drone3_heading: {drone3_heading}')
    
    # waypoints for drone3
    drone3_Latitude_list_takeoff_land = [drone3_latitude]
    drone3_Longitude_list_takeoff_land = [drone3_longitude]
    drone3_Altitude_takeoff_land = [globals()[f'drone_3_waypoint_altitude'][0], land_altitude]
    
if num_drones >= 4:
    drone4_Image_Telemetry_data = w.getImageAndTelemetryData(4)
    drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[3110408:]).decode())
    drone4_elements = drone4_Telemetry_data.split(":")                 # Extract all elements from the string.
    drone4_latitude = drone4_elements[0]
    drone4_longitude = drone4_elements[1]
    
    # # dummy values for latitude and longitude
    # drone4_latitude = 48.33687152813396
    # drone4_longitude = 14.320821985674456
    
    drone4_heading = drone4_elements[3]
    heading_list.append(drone4_heading)
    init_latitude_list.append(drone4_latitude)
    init_longitude_list.append(drone4_longitude)
    # print(f'drone4_latitude: {drone4_latitude}', f'drone4_longitude: {drone4_longitude}', f'drone4_heading: {drone4_heading}')
    
    # waypoints for drone4
    drone4_Latitude_list_takeoff_land = [drone4_latitude]
    drone4_Longitude_list_takeoff_land = [drone4_longitude]
    drone4_Altitude_takeoff_land = [globals()[f'drone_4_waypoint_altitude'][0], land_altitude]
    
if num_drones >= 5:
    drone5_Image_Telemetry_data = w.getImageAndTelemetryData(5)
    drone5_Telemetry_data = (bytearray(drone5_Image_Telemetry_data[3110408:]).decode())
    drone5_elements = drone5_Telemetry_data.split(":")                 # Extract all elements from the string.
    drone5_latitude = drone5_elements[0]
    drone5_longitude = drone5_elements[1]
    drone5_heading = drone5_elements[3]
    heading_list.append(drone5_heading)
    init_latitude_list.append(drone5_latitude)
    init_longitude_list.append(drone5_longitude)
    # print(f'drone5_latitude: {drone5_latitude}', f'drone5_longitude: {drone5_longitude}', f'drone5_heading: {drone5_heading}')
    
if num_drones >= 6:
    drone6_Image_Telemetry_data = w.getImageAndTelemetryData(6)
    drone6_Telemetry_data = (bytearray(drone6_Image_Telemetry_data[3110408:]).decode())
    drone6_elements = drone6_Telemetry_data.split(":")                 # Extract all elements from the string.
    drone6_latitude = drone6_elements[0]
    drone6_longitude = drone6_elements[1]
    drone6_heading = drone6_elements[3]
    heading_list.append(drone6_heading)
    init_latitude_list.append(drone6_latitude)
    init_longitude_list.append(drone6_longitude)
    # print(f'drone6_latitude: {drone6_latitude}', f'drone6_longitude: {drone6_longitude}', f'drone6_heading: {drone6_heading}')
    
if num_drones >= 7:
    drone7_Image_Telemetry_data = w.getImageAndTelemetryData(7)
    drone7_Telemetry_data = (bytearray(drone7_Image_Telemetry_data[3110408:]).decode())
    drone7_elements = drone7_Telemetry_data.split(":")                 # Extract all elements from the string.
    drone7_latitude = drone7_elements[0]
    drone7_longitude = drone7_elements[1]
    drone7_heading = drone7_elements[3]
    heading_list.append(drone7_heading)
    init_latitude_list.append(drone7_latitude)
    init_longitude_list.append(drone7_longitude)
    # print(f'drone7_latitude: {drone7_latitude}', f'drone7_longitude: {drone7_longitude}', f'drone7_heading: {drone7_heading}')
    
if num_drones >= 8:
    drone8_Image_Telemetry_data = w.getImageAndTelemetryData(8)
    drone8_Telemetry_data = (bytearray(drone8_Image_Telemetry_data[3110408:]).decode())
    drone8_elements = drone8_Telemetry_data.split(":")                 # Extract all elements from the string.
    drone8_latitude = drone8_elements[0]
    drone8_longitude = drone8_elements[1]
    drone8_heading = drone8_elements[3]
    heading_list.append(drone8_heading)
    init_latitude_list.append(drone8_latitude)
    init_longitude_list.append(drone8_longitude)
    # print(f'drone8_latitude: {drone8_latitude}', f'drone8_longitude: {drone8_longitude}', f'drone8_heading: {drone8_heading}')
    
if num_drones >= 9:
    drone9_Image_Telemetry_data = w.getImageAndTelemetryData(9)
    drone9_Telemetry_data = (bytearray(drone9_Image_Telemetry_data[3110408:]).decode())
    drone9_elements = drone9_Telemetry_data.split(":")                 # Extract all elements from the string.
    drone9_latitude = drone9_elements[0]
    drone9_longitude = drone9_elements[1]
    drone9_heading = drone9_elements[3]
    heading_list.append(drone9_heading)
    init_latitude_list.append(drone9_latitude)
    init_longitude_list.append(drone9_longitude)
    # print(f'drone9_latitude: {drone9_latitude}', f'drone9_longitude: {drone9_longitude}', f'drone9_heading: {drone9_heading}')
    
if num_drones >= 10:
    drone10_Image_Telemetry_data = w.getImageAndTelemetryData(10)
    drone10_Telemetry_data = (bytearray(drone10_Image_Telemetry_data[3110408:]).decode())
    drone10_elements = drone10_Telemetry_data.split(":")                 # Extract all elements from the string.
    drone10_latitude = drone10_elements[0]
    drone10_longitude = drone10_elements[1]
    drone10_heading = drone10_elements[3]
    heading_list.append(drone10_heading)
    init_latitude_list.append(drone10_latitude)
    init_longitude_list.append(drone10_longitude)
    # print(f'drone10_latitude: {drone10_latitude}', f'drone10_longitude: {drone10_longitude}', f'drone10_heading: {drone10_heading}')
    
if debug:
    print(f'heading_list: {heading_list}')

heading_num = int(len(heading_list)//2) # middle drone is taken as the reference drone
global_heading = heading_list[heading_num] # heading of the drone in the middle of the swarm is taken as the global heading
print(f'global_heading: {global_heading}')


while True:  # Keep looping to call the threads again
    
    ###### Section for quitting the program and mqtt ######
    if not action_in_progress:
        if keyboard.is_pressed('q'):
            if not key_pressed['q']:
                print("Key 'q' pressed! Exiting the program.")
                key_pressed['q'] = True
                print("Data Streaming has stopped")
                with lock:
                    stop_mqtt = True
                thread_data_streaming.join()
                break
            else:
                key_pressed['q'] = False
    
    ###### Section for takeoff #############
    if not action_in_progress:
        if keyboard.is_pressed('t'):
            if not key_pressed['t']:
                with lock:
                    task = 'takeoff'
                action_in_progress = True
                key_pressed['t'] = True
                print("Key 't' pressed! Executing Takeoff Procedure.")
                drone_threads_takeoff = []
                for i in range(1,  num_drones + 1):

                    latitude_list_takeoff = [globals()[f'drone{i}_Latitude_list_takeoff_land'][0], globals()[f'drone{i}_Latitude_list_takeoff_land'][0]]
                    longitude_list_takeoff = [globals()[f'drone{i}_Longitude_list_takeoff_land'][0], globals()[f'drone{i}_Longitude_list_takeoff_land'][0]]
                    drone_altitude_takeoff = [globals()[f'drone{i}_Altitude_takeoff_land'][0], globals()[f'drone{i}_Altitude_takeoff_land'][0]]
                    
                    heading_list_for_takeoff = [global_heading, globals()[f'drone_{i}_waypoint_heading'][0]]
                    speed_list_takeoff = [globals()[f'drone_{i}_waypoint_speed'][0], globals()[f'drone_{i}_waypoint_speed'][0]]
                    thresh_waypoint = Way_threshold

                    camera_list_takeoff = [globals()[f'drone_{i}_waypoint_camera'][0], globals()[f'drone_{i}_waypoint_camera'][0]]
                    lengthOfStay_list_takeoff = [0, 0]
                    gimbalPitch_list_takeoff = [globals()[f'drone_{i}_waypoint_gimbalPitch'][0], globals()[f'drone_{i}_waypoint_gimbalPitch'][0]]
                    gimbalYaw_list_takeoff = [globals()[f'drone_{i}_waypoint_gimbalYaw'][0], globals()[f'drone_{i}_waypoint_gimbalYaw'][0]]
                    
                    #### go to takeoff point ####
                    thread_numbers_3 = threading.Thread(target=globals()[f'waypoint_tread_drone{i}'], args=(latitude_list_takeoff, longitude_list_takeoff, drone_altitude_takeoff, heading_list_for_takeoff, speed_list_takeoff, thresh_waypoint, camera_list_takeoff, lengthOfStay_list_takeoff, gimbalPitch_list_takeoff, gimbalYaw_list_takeoff))
                    drone_threads_takeoff.append(thread_numbers_3)
                    
                for thread in drone_threads_takeoff:
                    thread.start()
                for thread in drone_threads_takeoff:
                    thread.join()    

                action_in_progress = False
   
                print('Action completed for key t'+'\n')
                
                key_pressed['t'] = False   

            else:
                key_pressed['t'] = False
    ###### Section for emergency case #############
            
    if not action_in_progress:
        if keyboard.is_pressed('i'):
            if not key_pressed['i']:
                with lock:
                    task = 'emergency'
                action_in_progress = True
                key_pressed['i'] = True
                print("Key 'i' pressed! Executing Emergency Case Procedure.")   
                emergency_case_thread = []
                thresh_waypoint = Way_threshold
                for i in range(1,  num_drones + 1):
                    
                    latitude_list_emergency = [globals()[f'drone{i}_Latitude_list_takeoff_land'][0], globals()[f'drone{i}_Latitude_list_takeoff_land'][0]]
                    longitude_list_emergency = [globals()[f'drone{i}_Longitude_list_takeoff_land'][0], globals()[f'drone{i}_Longitude_list_takeoff_land'][0]]
                    drone_altitude_emergency = [globals()[f'drone{i}_Altitude_takeoff_land'][0], globals()[f'drone{i}_Altitude_takeoff_land'][0]]
                    
                    heading_list_for_emergency = [global_heading, global_heading]
                    speed_list_for_emergency = [drone_speed, drone_speed]

                    camera_list_for_emergency = [90, 90]
                    lengthOfStay_list_for_emergency = [0, 0]
                    gimbalPitch_list_for_emergency = [0, 0]
                    gimbalYaw_list_for_emergency = [0, 0]

                    thread_numbers = threading.Thread(target=globals()[f'waypoint_tread_drone{i}'], args=(latitude_list_emergency, longitude_list_emergency, drone_altitude_emergency, heading_list_for_emergency, speed_list_for_emergency, thresh_waypoint, camera_list_for_emergency, lengthOfStay_list_for_emergency, gimbalPitch_list_for_emergency, gimbalYaw_list_for_emergency))
                    emergency_case_thread.append(thread_numbers)

                for thread in emergency_case_thread:
                    thread.start()
                
                for thread in emergency_case_thread:
                    thread.join()
                    
                print('Action completed for i'+'\n')
                action_in_progress = False
                with lock:
                    key_pressed_emergency['i'] = False 
                        
            else:
                key_pressed['i'] = False  
                
                
    ###### Section for waypoint mission ######
    if not action_in_progress:
        if keyboard.is_pressed('w'):
            if not key_pressed['w']:
                with lock:
                    task = 'waypoint'
                    drone1_waypoint_no = 0
                    drone2_waypoint_no = 0
                    drone3_waypoint_no = 0
                key_pressed['w'] = True
                action_in_progress = True
                print("Key 'w' pressed! Executing Waypoint Mission Procedure.")
                waypoint_treads = []    
                for i in range(1,  num_drones + 1):
                    
                    latitude_list_waypoint = globals()[f'drone_{i}_waypoint_lat'] # [lat_1, lat_2, lat_3, lat_4, lat_5, lat_6]
                    longitude_list_waypoint = globals()[f'drone_{i}_waypoint_lng'] # [long_1, long_2, long_3, long_4, long_5, long_6]
                    altitude_list_waypoint = globals()[f'drone_{i}_waypoint_altitude'] # [alt_1, alt_2, alt_3, alt_4, alt_5, alt_6]
                    
                    speed_list_waypoint = globals()[f'drone_{i}_waypoint_speed'] # [speed_1, speed_2, speed_3, speed_4, speed_5, speed_6]
                    heading_list_waypoint = globals()[f'drone_{i}_waypoint_heading'] # [heading_1, heading_2, heading_3, heading_4, heading_5, heading_6]
                    camera_list_waypoint = globals()[f'drone_{i}_waypoint_camera'] # [camera_1, camera_2, camera_3, camera_4, camera_5, camera_6]
                    lengthOfStay_list_waypoint = globals()[f'drone_{i}_waypoint_lengthOfStay'] # [lengthOfStay_1, lengthOfStay_2, lengthOfStay_3, lengthOfStay_4, lengthOfStay_5,lengthOfStay_6]
                    gimbalPitch_list_waypoint = globals()[f'drone_{i}_waypoint_gimbalPitch'] # [gimbalPitch_1, gimbalPitch_2, gimbalPitch_3, gimbalPitch_4, gimbalPitch_5, gimbalPitch_6]
                    gimbalYaw_list_waypoint = globals()[f'drone_{i}_waypoint_gimbalYaw'] # [gimbalYaw_1, gimbalYaw_2, gimbalYaw_3, gimbalYaw_4, gimbalYaw_5, gimbalYaw_6]
                    thresh_waypoint = Way_threshold

                    thread_numbers_1 = threading.Thread(target=globals()[f'waypoint_tread_drone{i}'], args=(latitude_list_waypoint, longitude_list_waypoint, altitude_list_waypoint,heading_list_waypoint, speed_list_waypoint, thresh_waypoint, camera_list_waypoint, lengthOfStay_list_waypoint, gimbalPitch_list_waypoint, gimbalYaw_list_waypoint))
                    waypoint_treads.append(thread_numbers_1)
                    
                for thread in waypoint_treads:
                    thread.start()
                    
                for thread in waypoint_treads:
                    thread.join()
                   
                print('Action completed for key w'+'\n')
                action_in_progress = False
                key_pressed['w'] = False
                waypoint_confirmation = True
    
            else:
                key_pressed['w'] = False
                
    ###### Section for landing #############
    
    if not action_in_progress:
        if keyboard.is_pressed('l'):
            if not key_pressed['l']:
                with lock:
                    task = 'land'
                key_pressed['l'] = True
                action_in_progress = True
                print("Key 'l' pressed! Executing Landing Procedure.")

                drone_threads_landing = []
 
                thresh_waypoint = Way_threshold
                
                for i in range(1,  num_drones + 1):
                    
                    latitude_list_landing =  [globals()[f'drone{i}_Latitude_list_takeoff_land'][0], globals()[f'drone{i}_Latitude_list_takeoff_land'][0], globals()[f'drone{i}_Latitude_list_takeoff_land'][0], globals()[f'drone{i}_Latitude_list_takeoff_land'][0]]
                    
                    longitude_list_landing = [globals()[f'drone{i}_Longitude_list_takeoff_land'][0], globals()[f'drone{i}_Longitude_list_takeoff_land'][0], globals()[f'drone{i}_Longitude_list_takeoff_land'][0], globals()[f'drone{i}_Longitude_list_takeoff_land'][0]]
                    drone_altitude_landing = [globals()[f'drone{i}_Altitude_takeoff_land'][0], globals()[f'drone{i}_Altitude_takeoff_land'][0], globals()[f'drone{i}_Altitude_takeoff_land'][1], globals()[f'drone{i}_Altitude_takeoff_land'][1]]

                    if waypoint_confirmation:
                        speed_list_landing = [globals()[f'drone_{i}_waypoint_speed'] [-1], globals()[f'drone_{i}_waypoint_speed'] [-1], globals()[f'drone_{i}_waypoint_speed'] [-1], globals()[f'drone_{i}_waypoint_speed'] [-1]]
                        
                        heading_list_landing = [globals()[f'drone_{i}_waypoint_heading'][-1], global_heading, global_heading, global_heading]
                        
                        camera_list_landing = [globals()[f'drone_{i}_waypoint_camera'][-1], globals()[f'drone_{i}_waypoint_camera'][-1], globals()[f'drone_{i}_waypoint_camera'][-1], globals()[f'drone_{i}_waypoint_camera'][-1]]
                        
                        lengthOfStay_list_landing = [0, 0, 0, 0]
                        
                        gimbalPitch_list_landing = [globals()[f'drone_{i}_waypoint_gimbalPitch'][-1], globals()[f'drone_{i}_waypoint_gimbalPitch'][-1], globals()[f'drone_{i}_waypoint_gimbalPitch'][-1], globals()[f'drone_{i}_waypoint_gimbalPitch'][-1]]
                        
                        gimbalYaw_list_landing = [globals()[f'drone_{i}_waypoint_gimbalYaw'][-1], globals()[f'drone_{i}_waypoint_gimbalYaw'][-1], globals()[f'drone_{i}_waypoint_gimbalYaw'][-1], globals()[f'drone_{i}_waypoint_gimbalYaw'][-1]]
                    
                    else:
                        
                        heading_list_landing = [global_heading, global_heading, global_heading, global_heading]
                        speed_list_landing = [drone_speed, drone_speed, drone_speed, drone_speed]
                        camera_list_landing= [90, 90, 90, 90]
                        lengthOfStay_list_landing = [0, 0, 0, 0]
                        gimbalPitch_list_landing = [0, 0, 0, 0]
                        gimbalYaw_list_landing = [0, 0, 0, 0]
                        

                    thread_numbers1 = threading.Thread(target=globals()[f'waypoint_tread_drone{i}'], args=(latitude_list_landing, longitude_list_landing, drone_altitude_landing, heading_list_landing, speed_list_landing, thresh_waypoint, camera_list_landing, lengthOfStay_list_landing, gimbalPitch_list_landing, gimbalYaw_list_landing))
                    
                    drone_threads_landing.append(thread_numbers1)

                
                for thread in drone_threads_landing:
                    thread.start()
                
                for thread in drone_threads_landing:
                    thread.join()
                
                print('Action completed for key l'+'\n')
                action_in_progress = False   
                key_pressed['l'] = False  
                                    
            else:
                key_pressed['l'] = False  
            