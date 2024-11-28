# reqired libraries
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import json
import numpy as np
import cv2
import time
import math
import base64
import math
import json
import ds_wrapper as w
import keyboard
from paho.mqtt import client as mqtt_client
import json
import base64
import math
import threading
import os
import encodings.idna
import logging
###################################### Parameters to be set ###############################################
simulation_mode = False

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

if debug == True:
    new = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) # Get the current time as string
    os.mkdir(r"Result" + new) # Add a separator between the download location and the new folder name
    # Create a folder to store the results
    Download_Location = r"Result" + new # Location to store the results
    os.mkdir(Download_Location + '/images') # Create a folder to store the images
    Images_Path = os.path.join(Download_Location,'images')
    

Way_threshold  = 3 # treshold for the waypoints

key_pressed_emergency = {'u' : False} # Variable to keep track of emergency key press status

global action_in_progress, stop_waypoint_mission, land_command, listen_16th_element, time_lists, decoding, last_latitudes, last_longitudes, focal_length, compass_correction, RX_threshold, focal_plane_pitch, focal_plane_roll, camera,landing_completed, camera_drone_id, old_parameters, key_p, stop_u_listener, u_action, run_apart, takeoff_completed, heading_vis, gimbal_pitch_vis, gimbal_yaw_vis, old_vis_parameters, drone_id_looking, heading_looking, gimbal_pitch_looking, gimbal_yaw_looking, update_looking, arrange_looking_direction_thread_stop, move_drones, must_check, first_data_confirmed, send_data_to_drone, break_while, drone_1_break_while, drone_2_break_while, drone_3_break_while, drone_4_break_while, drone_5_break_while, drone_6_break_while, drone_7_break_while, drone_8_break_while, drone_9_break_while, drone_10_break_while, drone_1_thread_stop, drone_2_thread_stop, drone_3_thread_stop, drone_4_thread_stop, drone_5_thread_stop, drone_6_thread_stop, drone_7_thread_stop, drone_8_thread_stop, drone_9_thread_stop, drone_10_thread_stop, update_looking_drone_1, update_looking_drone_2, update_looking_drone_3, update_looking_drone_4, update_looking_drone_5, update_looking_drone_6, update_looking_drone_7, update_looking_drone_8, update_looking_drone_9, update_looking_drone_10

break_while = False

drone_1_break_while = False
drone_2_break_while = False
drone_3_break_while = False
drone_4_break_while = False
drone_5_break_while = False
drone_6_break_while = False
drone_7_break_while = False
drone_8_break_while = False
drone_9_break_while = False
drone_10_break_while = False

drone_1_thread_stop = False
drone_2_thread_stop = False
drone_3_thread_stop = False
drone_4_thread_stop = False
drone_5_thread_stop = False
drone_6_thread_stop = False
drone_7_thread_stop = False
drone_8_thread_stop = False
drone_9_thread_stop = False
drone_10_thread_stop = False

update_looking_drone_1 = False
update_looking_drone_2 = False
update_looking_drone_3 = False
update_looking_drone_4 = False
update_looking_drone_5 = False
update_looking_drone_6 = False
update_looking_drone_7 = False
update_looking_drone_8 = False
update_looking_drone_9 = False
update_looking_drone_10 = False


send_data_to_drone = False
first_data_confirmed = False
move_drones = []
update_looking = False
arrange_looking_direction_thread_stop = False

drone_id_looking = 0
heading_looking = 0
gimbal_pitch_looking = 0
gimbal_yaw_looking = 0

takeoff_completed = False
run_apart = True
u_action = False
stop_u_listener = False
key_p = False
old_parameters = [[0.9, 0, 0, 0, 0], [0.9, 0, 0, 0, 0], [0.9, 0, 0, 0, 0], [0.9, 0, 0, 0, 0], [0.9, 0, 0, 0, 0], [0.9, 0, 0, 0, 0], [0.9, 0, 0, 0, 0], [0.9, 0, 0, 0, 0], [0.9, 0, 0, 0, 0], [0.9, 0, 0, 0, 0]]	
camera_drone_id = 1
landing_completed = False
u_key = False
decoding = 'hardware'
focal_length = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
compass_correction = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
RX_threshold = [0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9]
focal_plane_pitch = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
focal_plane_roll = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

heading_vis = [0.0] * 10
gimbal_pitch_vis = [0.0] * 10
gimbal_yaw_vis = [0.0] * 10

old_vis_parameters = [[0.0, 0.0, 0.0] for i in range(10)]

action_in_progress = False
num_drones_for_map_visualization = 10
drones = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] 
saved_data = ['', '', '', '', '', '', '', '', '', '']
connected_drones = [] # List to store the connected drones
stop_waypoint_mission = False	
land_command = False
listen_16th_element = False
last_latitudes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
last_longitudes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

camera = [91, 91, 91, 91, 91, 91, 91, 91, 91, 91] 

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
active_clients = {}

# Function to connect to MQTT broker
def connect_mqtt(broker, port, topic, client_id, username, password):
    def on_connect(client, userdata, flags, rc):
        if rc != 0:
            print(f"Failed to connect, return code {rc}")
        else:
            # print("Connected to MQTT broker")
            client.subscribe("drone/#")  # Subscribe to all drone topics

    client = mqtt_client.Client(client_id, transport="websockets")
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def connect_mqtt_to_read(broker, port, topic, client_id, username, password):
    def on_connect(client, userdata, flags, rc):
        if rc != 0:
            print(f"Failed to connect, return code {rc}")
        else:
            print("Connected to MQTT broker")
            client.subscribe("drone/#")  # Subscribe to all drone topics

    client = mqtt_client.Client(client_id, transport="websockets")
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_message = on_message  # Set the message callback
    client.connect(broker, port)
    return client

def on_message(client, userdata, msg):
    global camera_drone_id
    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode("utf-8"))
        if topic.startswith("drone/") and topic.endswith("/settings"):
            drone_id = int(topic.split('/')[1])
            camera_drone_id = drone_id
            print('camera_drone_id:', camera_drone_id)
            handle_drone_settings(drone_id, payload)
            
        elif topic.startswith("drone/") and topic.endswith("/controls"):
            drone_id = int(topic.split('/')[1])
            camera_drone_id = drone_id
            print('camera_drone_id:', camera_drone_id)
            handle_drone_controls(drone_id, payload)
            
    except Exception as e:
        print(f"Error processing message: {e}")
        
def publish_feedback(client, data, drone_id):
    print(client)
    feedback_topic =  f"drone/{drone_id}/feedback"
    print(f"Publishing feedback to {feedback_topic}: {data}") 
    client.publish(feedback_topic, json.dumps(data))   
         
def handle_drone_settings(drone_id, settings):
    print(f"Received settings for drone {drone_id}: {settings}")
    # Received settings for drone 1: {'focalPlane': '-4.86', 'compass_correction': '-10.42', 'RXThreshold': '0', 'focalPlanePitch': '-6.11', 'focalPlaneRoll': '0'}
    focal_length[drone_id - 1] = float(settings.get('focalPlane'))
    compass_correction[drone_id - 1] = float(settings.get('compass_correction'))
    RX_threshold[drone_id - 1] = float(settings.get('RXThreshold'))
    focal_plane_pitch[drone_id - 1] = float(settings.get('focalPlanePitch'))
    focal_plane_roll[drone_id - 1] = float(settings.get('focalPlaneRoll'))
    
def handle_drone_controls(drone_id, controls):
    global update_looking, heading_vis, gimbal_pitch_vis, gimbal_yaw_vis, drone_1_break_while, drone_2_break_while, drone_3_break_while, drone_4_break_while, drone_5_break_while, drone_6_break_while, drone_7_break_while, drone_8_break_while, drone_9_break_while, drone_10_break_while
 
    with lock:
        globals()[f'drone_{drone_id}_break_while'] = True
        
    if controls.get('heading') == 'N/A':
        current_heading = 'N/A'
    else:
        current_heading = float(controls.get('heading', 0) or 0)
        if current_heading > 180:
            current_heading -= 360 
    
    if controls.get('gimbalPitch') == 'N/A':
        current_gimbal_pitch = 'N/A'
    else:
        current_gimbal_pitch = float(controls.get('gimbalPitch', 0) or 0)
        
    if controls.get('gimbalYaw') == 'N/A':
        current_gimbal_yaw = 'N/A'
    else:
        current_gimbal_yaw = float(controls.get('gimbalYaw', 0) or 0)


    # # Set the values to 'N/A' if they are the same as previous
    heading_vis[drone_id - 1] = current_heading
    gimbal_pitch_vis[drone_id - 1] = current_gimbal_pitch
    gimbal_yaw_vis[drone_id - 1] = current_gimbal_yaw

    print(f"Looking values: Drone {drone_id}, Heading {current_heading}, Gimbal Pitch {current_gimbal_pitch}, Gimbal Yaw {current_gimbal_yaw}")

    with lock:
        update_looking = True
    
    print('update_looking02:', update_looking)
    
# Constants for reconnecting
FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 1
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

def start_or_update_mqtt_for_drones(connected_drones):
    global active_clients
    # add a dummy drone at the end of connected_drone list to communicate with the server
    mqtt_connected_drones= connected_drones + [20] + [20 + i for i in connected_drones]
    
    for drone_id in mqtt_connected_drones:
        if drone_id not in active_clients:
            client_id = f'python-mqtt-{drone_id}'
            if drone_id == 20:
                client = connect_mqtt_to_read(broker, port, topic, client_id, username, password)
            else:
                client = connect_mqtt(broker, port, topic, client_id, username, password)
            client.on_disconnect = on_disconnect
            client.loop_start()
            active_clients[drone_id] = client
            if drone_id != 20:
                print(f'Started MQTT client for drone {drone_id}') 
            else:
                print(f'Started MQTT client for dummy drone {drone_id}') 
        else:
            pass

    for drone_id in list(active_clients.keys()):
        if drone_id not in mqtt_connected_drones:
            active_clients[drone_id].loop_stop()
            del active_clients[drone_id]
            print(f'Stopped MQTT client for drone {drone_id}')   
        
def stop_all_mqtt_clients():
    global active_clients
    for client in active_clients.values():
        client.loop_stop()
    active_clients.clear()
    print('All MQTT clients stopped')

# Function to publish the data to MQTT broker for each drone
def publisher_thread(broker, port, topic, username, password):
    global drone1_waypoint_no, drone2_waypoint_no, drone3_waypoint_no, drone4_waypoint_no, drone5_waypoint_no, drone6_waypoint_no, drone7_waypoint_no, drone8_waypoint_no, drone9_waypoint_no, drone10_waypoint_no, connected_drones, drones, stop_mqtt, time_lists, active_clients, camera, simulation_mode
    

    for i in range(1, num_drones_for_map_visualization + 1):
        
        Image_Telemetry_data = w.getImageAndTelemetryData(i)
                
        if((len(Image_Telemetry_data)) > 2000000):
            Telemetry_data = (bytearray(Image_Telemetry_data[3110408:]).decode())
        else:
            Telemetry_data = (bytearray(Image_Telemetry_data[1382408:]).decode())
            
        telemetry_elements = Telemetry_data.split(":")  # Extract all elements from the string
        
        if Telemetry_data != '':
            connected_drones.append(i) # If you want to check the other drone threads, arrange the connected drones list accordingly. 
    
    print(f"Connected drones: {connected_drones}")       
    start_or_update_mqtt_for_drones(connected_drones) 
          
    while True:
        time.sleep(0.01)

        for drone_id in connected_drones:
            
            try:
                # Get the telemetry and image data from the drones
                Image_Telemetry_data = w.getImageAndTelemetryData(drone_id)
                
                if((len(Image_Telemetry_data)) > 2000000):
                    Telemetry_data = (bytearray(Image_Telemetry_data[3110408:]).decode())
                else:
                    Telemetry_data = (bytearray(Image_Telemetry_data[1382408:]).decode())
                    
                telemetry_elements = Telemetry_data.split(":")  # Extract all elements from the string
                
                # Process telemetry and image data
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
                
                # Map the pitch angle from (-180, 180) to (0, 360)
                if float(gimbal_yaw) < 0:
                    gimbal_yaw = float(gimbal_yaw) + 360
                else:
                    gimbal_yaw = float(gimbal_yaw)
                
                # Map the heading angle from (-180, 180) to (0, 360)
                if float(heading) < 0:
                    heading = float(heading) + 360
                else:
                    heading = float(heading)
                
                # Calculate the difference
                angle_diff = gimbal_yaw - heading
                
                # Normalize the difference to the range [-180, 180]
                angle_diff = (angle_diff + 180) % 360 - 180
                
                gimbal_yaw = angle_diff
                
                # Test data adjustments
                if simulation_mode:
                    if drone_id == 1:
                        latitude = str(float(latitude) + 0.004)
                        longitude = str(float(longitude) + 0.05)
                        
                    if drone_id == 2:
                        latitude = str(float(latitude) - 0.004)
                        longitude = str(float(longitude) - 0.05)
                
                # Image processing
                decode = w.isHWDecoderEnabled()
                with lock:
                    if decode == 1:
                        decoding = 'hardware'
                    elif decode == 0:
                        decoding = 'software'
                    else:
                        print('Invalid decoding method')
                        
                # cam = camera[drone_id - 1]
                # if cam >= 91 and cam < 94:
                if((len(Image_Telemetry_data)) > 2000000):
                    if decoding == 'software':
                        Image = cv2.cvtColor(Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV420p2RGB)   # for software decoding
                    elif decoding == 'hardware':
                        Image = cv2.cvtColor(Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV2BGR_NV12) # for hardware decoding
                else:
                    if decoding == 'software':
                        Image = cv2.cvtColor(Image_Telemetry_data[0:1382400].reshape(720*3//2, 1280), cv2.COLOR_YUV420p2RGB)   # for software decoding
                    elif decoding == 'hardware':
                        Image = cv2.cvtColor(Image_Telemetry_data[0:1382400].reshape(720*3//2, 1280), cv2.COLOR_YUV2BGR_NV12) # for hardware decoding

                retval, buffer = cv2.imencode('.jpg', Image)
                imgBase64 = base64.b64encode(buffer).decode('utf-8')
                
                # Get waypoint data
                if drone_id == 1:
                    drone_waypoint_no = drone1_waypoint_no
                elif drone_id == 2:
                    drone_waypoint_no = drone2_waypoint_no
                elif drone_id == 3:
                    drone_waypoint_no = drone3_waypoint_no
                elif drone_id == 4:
                    drone_waypoint_no = drone4_waypoint_no
                elif drone_id == 5:
                    drone_waypoint_no = drone5_waypoint_no
                elif drone_id == 6:
                    drone_waypoint_no = drone6_waypoint_no
                elif drone_id == 7:
                    drone_waypoint_no = drone7_waypoint_no
                elif drone_id == 8:
                    drone_waypoint_no = drone8_waypoint_no
                elif drone_id == 9:
                    drone_waypoint_no = drone9_waypoint_no
                elif drone_id == 10:
                    drone_waypoint_no = drone10_waypoint_no
                else:
                    drone_waypoint_no = 0
                
                # drone_waypoint_no = 0            
                telemdata = f"ID:{drone_id},Alt:{float(altitude):.1f}m,Spd:{speed:.1f}m/s,Com:{float(heading):.1f},Pit:{float(gimbal_pitch):.1f},Yaw:{float(gimbal_yaw):.1f},Wpt:{drone_waypoint_no:.0f}"
                
                content = droneContent.format(telemetrydata=telemdata, img_base64=imgBase64)
                
                msg = json.dumps({"id": drone_id, "lat": latitude, "lon": longitude, "deg": heading, "content": content, "offset_x": -100, "offset_y": 0, 'colour': '#eb3434'})

                active_clients[drone_id].publish(topic, msg)

            except IndexError:
                pass
                
        if stop_mqtt:
            stop_all_mqtt_clients()
            break

print("Data Streaming has started")
thread_data_streaming = threading.Thread(target=publisher_thread, args=(broker, port, topic, username, password))
thread_data_streaming.start()
     
######################## Drone 1 Thread ############################
d1Image = []
d1Poses= []

def waypoint_tread_drone1(task, drone1_Latitude_List, drone1_Longitude_list, drone1_Altitude_list,drone1_Heading_list,drone1_Speed_list, Way1_threshold, camera_list, lengthOfStay_list, gimbalPitch_list, gimbalYaw_list, drone1_parameter_mode, drone1_rx_threshold, drone1_compass_correction, drone1_focal_length, drone1_focal_plane_pitch, drone1_focal_plane_roll, drone1_integration_window, drone1_minimum_pose_distance):
    # print('Waypoint latitude list for drone1:', drone1_Latitude_List)
    
    number_of_waypoints_for_drone1 = len(drone1_Latitude_List)
    print(f"Number of waypoints for drone1: {number_of_waypoints_for_drone1}")
    drone1_new_parameter_integral_go = 1 # for triggering integration while reaching (go) to the waypoint 
    drone1_new_parameter_integral_update = 0
    
    global drone_1_incrementor, drone1_waypoint_no, camera, stop_waypoint_mission, break_while, drone_1_break_while, drone_1_thread_stop, update_looking_drone_1, active_clients
    
    with lock: 
        drone_1_thread_stop = False
        update_looking_drone_1 = False
    
    incrementor = drone_1_incrementor
    
    previous_speed_list_drone1 = [drone1_Speed_list[0], *drone1_Speed_list]
    previous_heading_list_drone1 = [drone1_Heading_list[0], *drone1_Heading_list]
    # print('previous_heading_list_drone1:', previous_heading_list_drone1)
    previous_camera_list_drone1 = [camera_list[0], *camera_list]
    previous_lengthOfStay_list_drone1 = [lengthOfStay_list[0], *lengthOfStay_list]
    previous_gimbalPitch_list_drone1 = [gimbalPitch_list[0], *gimbalPitch_list]
    previous_gimbalYaw_list_drone1 = [gimbalYaw_list[0], *gimbalYaw_list]
    previous_drone1_rx_threshold = [drone1_rx_threshold[0], *drone1_rx_threshold]
    previous_drone1_compass_correction = [drone1_compass_correction[0], *drone1_compass_correction]
    previous_drone1_focal_length = [drone1_focal_length[0], *drone1_focal_length]
    previous_drone1_focal_plane_pitch = [drone1_focal_plane_pitch[0], *drone1_focal_plane_pitch]
    previous_drone1_focal_plane_roll = [drone1_focal_plane_roll[0], *drone1_focal_plane_roll]
    previous_drone1_integration_window = [drone1_integration_window[0], *drone1_integration_window]
    previous_drone1_minimum_pose_distance = [drone1_minimum_pose_distance[0], *drone1_minimum_pose_distance]
 
    iteration = 0
    
    while True:
        
        # Check if the drone is in manual mode
        
        drone1_Image_Telemetry_data = w.getImageAndTelemetryData(1) # 1 refers to the drone number
            
        if((len(drone1_Image_Telemetry_data)) > 2000000):
            drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[3110408:]).decode())
        else:
            drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[1382408:]).decode())
            
        drone1_elements = drone1_Telemetry_data.split(":")                 # Extract all elements from the string

        # check 16th element to see if the drone is in manual mode
        if float(drone1_elements[16]) == 0.0:
            with lock:
                drone_1_incrementor = 1
            break
            
        if task == 'takeoff and waypoint' or task == 'update_camera_parameters':
            with lock:
                drone1_waypoint_no = drone1_waypoint_no + 1
            print(f"Mission Waypoint {drone1_waypoint_no} in progress for drone1 ...") 

            drone1_Latitude_go = drone1_Latitude_List[iteration]
            drone1_Longitude_go = drone1_Longitude_list[iteration]
            drone1_Altitude_go = drone1_Altitude_list[iteration]
            drone1_Heading_go = previous_heading_list_drone1[iteration]
            drone1_Speed_go = previous_speed_list_drone1[iteration]
            drone1_Camera_go = previous_camera_list_drone1[iteration]
            drone1_LengthOfStay_go = previous_lengthOfStay_list_drone1[iteration]
            drone1_GimbalPitch_go = previous_gimbalPitch_list_drone1[iteration]
            drone1_GimbalYaw_go = previous_gimbalYaw_list_drone1[iteration]
            drone1_Integration_Window_go = previous_drone1_integration_window[iteration]
            drone1_Minimum_Pose_Distance_go = previous_drone1_minimum_pose_distance[iteration]
            
            drone1_Rx_threshold = previous_drone1_rx_threshold[iteration]
            drone1_Compass_correction = previous_drone1_compass_correction[iteration]
            drone1_Focal_length = previous_drone1_focal_length[iteration]
            drone1_Focal_plane_pitch = previous_drone1_focal_plane_pitch[iteration]
            drone1_Focal_plane_roll = previous_drone1_focal_plane_roll[iteration]
            
            drone1_Latitude_update = drone1_Latitude_List[iteration]
            drone1_Longitude_update = drone1_Longitude_list[iteration]
            drone1_Altitude_update = drone1_Altitude_list[iteration]
            drone1_Heading_update = drone1_Heading_list[iteration]
            drone1_Speed_update = drone1_Speed_list[iteration]
            drone1_Camera_update = camera_list[iteration]
            drone1_LengthOfStay_update = lengthOfStay_list[iteration]
            drone1_GimbalPitch_update = gimbalPitch_list[iteration]
            drone1_GimbalYaw_update = gimbalYaw_list[iteration]
            drone1_Integration_Window_update = drone1_integration_window[iteration]
            drone1_Minimum_Pose_Distance_update = drone1_minimum_pose_distance[iteration]
            
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
            drone1_Integration_Window_go = drone1_integration_window[iteration]
            drone1_Minimum_Pose_Distance_go = drone1_minimum_pose_distance[iteration]
            
            drone1_Rx_threshold = drone1_rx_threshold[iteration]
            drone1_Compass_correction = drone1_compass_correction[iteration]
            drone1_Focal_length = drone1_focal_length[iteration]
            drone1_Focal_plane_pitch = drone1_focal_plane_pitch[iteration]
            drone1_Focal_plane_roll = drone1_focal_plane_roll[iteration]
            
            drone1_Latitude_update = drone1_Latitude_List[iteration + 1]
            drone1_Longitude_update = drone1_Longitude_list[iteration + 1]
            drone1_Altitude_update = drone1_Altitude_list[iteration + 1]
            drone1_Heading_update = drone1_Heading_list[iteration + 1]
            drone1_Speed_update = drone1_Speed_list[iteration + 1]
            drone1_Camera_update = camera_list[iteration + 1]
            drone1_LengthOfStay_update = lengthOfStay_list[iteration + 1]
            drone1_GimbalPitch_update = gimbalPitch_list[iteration + 1]
            drone1_GimbalYaw_update = gimbalYaw_list[iteration + 1]
            drone1_Integration_Window_update = drone1_integration_window[iteration + 1]
            drone1_Minimum_Pose_Distance_update = drone1_minimum_pose_distance[iteration + 1]
            
            iteration += 2
                
        waypointvalue1 = incrementor

        ################ for reaching the waypoint ################
        
        if stop_waypoint_mission:
            with lock:
                drone_1_incrementor = incrementor
            break
            
        if task == 'update_camera_parameters':
            pass
        else: 

            print("waypointvalue1_drone1(go):",waypointvalue1)
            
            drone1_waypoint_data_reached = f"{drone1_Latitude_go}:{drone1_Longitude_go}:{drone1_Altitude_go}:{drone1_Heading_go}:{drone1_Speed_go}:{waypointvalue1}:{Way1_threshold}:{drone1_GimbalPitch_go}:{drone1_GimbalYaw_go}:{drone1_Camera_go}:{drone1_parameter_mode}:{drone1_Rx_threshold}:{drone1_Compass_correction}:{drone1_Focal_length}:{drone1_Focal_plane_pitch}:{drone1_Focal_plane_roll}:{drone1_new_parameter_integral_go}:{drone1_Integration_Window_go}:{drone1_Minimum_Pose_Distance_go}"
            
            drone1_send_data = w.sendWayPointData(drone1_waypoint_data_reached, 1)     # 1 refers to the drone number
            
            drone1_waypoint_data_sent = f"Lat: {drone1_Latitude_go}, Long: {drone1_Longitude_go}, Alt: {drone1_Altitude_go}, Heading: {drone1_Heading_go}, Speed: {drone1_Speed_go}, Waypoint: {waypointvalue1}, Threshold: {Way1_threshold}, Gimbal Pitch: {drone1_GimbalPitch_go}, Gimbal Yaw: {drone1_GimbalYaw_go}, Camera: {drone1_Camera_go}, Mode: {drone1_parameter_mode}, RX Threshold: {drone1_Rx_threshold}, Compass Correction: {drone1_Compass_correction}, Focal Length: {drone1_Focal_length}, Focal Plane Pitch: {drone1_Focal_plane_pitch}, Focal Plane Roll: {drone1_Focal_plane_roll}, Integral: {drone1_new_parameter_integral_go}, Integration Window: {drone1_Integration_Window_go}, Minimum Pose Distance: {drone1_Minimum_Pose_Distance_go}"
            # if debug:
            print("Data being Sent for drone1 (go):",drone1_waypoint_data_sent)
            
            ## Check if the drone has reached the waypoint, element (14) of the getImageAndTelemetryData string is set to 1. Extract the image and telemetry data when the condition is met. ## Every time the drone receive the next waypoints this element is set to zero again ion the drone app.
            ## Element 15 is to confirm that the next waypoint data has been successfully received on the app side.

            while True:
                
                if break_while or drone_1_break_while:
                    break
                
                drone1_send_data = w.sendWayPointData(drone1_waypoint_data_reached, 1) 
                drone1_Image_Telemetry_data = w.getImageAndTelemetryData(1) # 1 refers to the drone number
                
                if((len(drone1_Image_Telemetry_data)) > 2000000):
                    drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[1382408:]).decode())
                    
                #drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[1382408:]).decode())
                
                drone1_elements = drone1_Telemetry_data.split(":")                 # Extract all elements from the string
                drone1_Waypoint_sent = drone1_elements[15].split('.')[0]
                # print("drone1_Waypoint_sent_for_go:",drone1_Waypoint_sent)

                # check 16th element to see if the drone is in manual mode
                if debug:
                    print("drone1_elements[16]_1:",drone1_elements[16])
                    
                if float(drone1_elements[16]) == 0.0:
                    with lock:
                        drone_1_incrementor = 1
                    break
                
                if (drone1_Waypoint_sent) == str(incrementor) or break_while == True or drone_1_break_while == True:
                    if debug: 
                        print("drone1 Waypoint data sent for go")
                        print ("go thread for drone1:", drone1_Waypoint_sent, incrementor)
                    break # Exit the loop
            
            if break_while or drone_1_break_while:
                with lock:
                    drone_1_incrementor = incrementor + 1
                    drone_1_thread_stop = True  
                break    
            
            while True:
                
                if break_while or drone_1_break_while:
                    break

                drone1_Image_Telemetry_data = w.getImageAndTelemetryData(1)
                if((len(drone1_Image_Telemetry_data)) > 2000000):
                    drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[1382408:]).decode())
                
                #drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[1382408:]).decode())
                
                drone1_elements = drone1_Telemetry_data.split(":")                 # Extract all elements from the string
                drone1_Waypoint_reached = drone1_elements[14]

                # check 16th element to see if the drone is in manual mode
                if debug:
                    print("drone1_elements[16]_2:",drone1_elements[16])
                if float(drone1_elements[16]) == 0.0:
                    with lock:
                        drone_1_incrementor = 1
                    break
                
                if drone1_Waypoint_reached == str(incrementor) or break_while == True or drone_1_break_while == True:
                    # print('break_while4:', break_while)
                    if debug:
                        print("drone1 Waypoint has been reached")
                        print ("go thread waypoint reached for drone1:", drone1_Waypoint_reached, incrementor)
                    break # Exit the loop
                
                
            if break_while or drone_1_break_while:
                with lock:
                    drone_1_incrementor = incrementor + 1
                    print('Mission has been stopped2')
                    drone_1_thread_stop = True
                    print('drone_1_thread_stop:', drone_1_thread_stop)
                break 
            
            # Call the telemetry data again
            drone1_Image_Telemetry_data = w.getImageAndTelemetryData(1)
            if((len(drone1_Image_Telemetry_data)) > 2000000):
                drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[3110408:]).decode())
            else:
                drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[1382408:]).decode())
            
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
        
        if stop_waypoint_mission:
            with lock:
                drone_1_incrementor = incrementor
            break
        
        waypointvalue1_update = incrementor 
        print("waypointvalue1_drone1(update):",waypointvalue1_update)
        
        drone1_waypoint_data = f"{drone1_Latitude_update}:{drone1_Longitude_update}:{drone1_Altitude_update}:{drone1_Heading_update}:{drone1_Speed_update}:{waypointvalue1_update}:{Way1_threshold}:{drone1_GimbalPitch_update}:{drone1_GimbalYaw_update}:{drone1_Camera_update}:{drone1_parameter_mode}:{drone1_Rx_threshold}:{drone1_Compass_correction}:{drone1_Focal_length}:{drone1_Focal_plane_pitch}:{drone1_Focal_plane_roll}:{drone1_new_parameter_integral_update}:{drone1_Integration_Window_update}: {drone1_Minimum_Pose_Distance_update}"
        
        drone1_send_data = w.sendWayPointData(drone1_waypoint_data, 1)     # 1 refers to the drone number
        
        # with lock:
        #     camera[0] = drone1_Camera_update # update the camera of the drone 1
        
        drone1_waypoint_data_sent = f"Lat: {drone1_Latitude_update}, Long: {drone1_Longitude_update}, Alt: {drone1_Altitude_update}, Heading: {drone1_Heading_update}, Speed: {drone1_Speed_update}, Waypoint: {waypointvalue1_update}, Threshold: {Way1_threshold}, Gimbal Pitch: {drone1_GimbalPitch_update}, Gimbal Yaw: {drone1_GimbalYaw_update}, Camera: {drone1_Camera_update}, Mode: {drone1_parameter_mode}, RX Threshold: {drone1_Rx_threshold}, Compass Correction: {drone1_Compass_correction}, Focal Length: {drone1_Focal_length}, Focal Plane Pitch: {drone1_Focal_plane_pitch}, Focal Plane Roll: {drone1_Focal_plane_roll}, Integral: {drone1_new_parameter_integral_update}, Integration Window: {drone1_Integration_Window_update}, Minimum Pose Distance: {drone1_Minimum_Pose_Distance_update}"
        
        # if debug:
        print("Data Being Sent for drone1 (update) :",drone1_waypoint_data_sent, "\n")
        
        while True:

            if break_while or drone_1_break_while:
                break
        
            drone1_send_data = w.sendWayPointData(drone1_waypoint_data, 1) 
            drone1_Image_Telemetry_data = w.getImageAndTelemetryData(1) # 1 refers to the drone number
            
            if((len(drone1_Image_Telemetry_data)) > 2000000):
                drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[3110408:]).decode())
            else:
                drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[1382408:]).decode())
                
            #drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[1382408:]).decode())
            
            drone1_elements = drone1_Telemetry_data.split(":")                 # Extract all elements from the string
            drone1_Waypoint_sent = drone1_elements[15].split('.')[0]

            # check 16th element to see if the drone is in manual mode
            if debug:
                print("drone1_elements[16]_3:",drone1_elements[16])
                
            if float(drone1_elements[16]) == 0.0:
                with lock:
                    drone_1_incrementor = 1
                break

            if (drone1_Waypoint_sent) == str(incrementor) or break_while == True or drone_1_break_while == True:
                print('drone1_break_while_111113:', drone_1_break_while)
                print('break_while1113:', break_while)
                if debug: 
                    print("drone1 Waypoint data sent")
                print ("run thread for drone1:", drone1_Waypoint_sent, incrementor)
                    
                break # Exit the loop

        if break_while or drone_1_break_while:
            with lock:
                drone_1_incrementor = incrementor + 1
                drone_1_thread_stop = True
            break 

        while True:
            if break_while or drone_1_break_while:
                break
            
            drone1_Image_Telemetry_data = w.getImageAndTelemetryData(1)
            
            if((len(drone1_Image_Telemetry_data)) > 2000000):
                drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[3110408:]).decode())
            else:
                drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[1382408:]).decode())
                
            #drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[1382408:]).decode())
            
            drone1_elements = drone1_Telemetry_data.split(":")                 # Extract all elements from the string
            
            drone1_Waypoint_reached = drone1_elements[14]
            
            # check 16th element to see if the drone is in manual mode
            if debug:
                print("drone1_elements[16]_4:",drone1_elements[16])
                
            if float(drone1_elements[16]) == 0.0:
                with lock:
                    drone_1_incrementor = 1
                break
            
            if drone1_Waypoint_reached == str(incrementor) or break_while == True or drone_1_break_while == True:
                if debug:
                    print("drone1 Waypoint has been reached")
                    print ("run thread waypoint reached:", drone1_Waypoint_reached, incrementor)
                break # Exit the loop
            
        
        if break_while or drone_1_break_while:
            with lock:
                drone_1_incrementor = incrementor + 1
                drone_1_thread_stop = True
            break   
        
        feedback_data_update_1 = {
            'drone_id': 1,
            'heading': drone1_Heading_update,
            'gimbalPitch': drone1_GimbalPitch_update,
            'gimbalYaw': drone1_GimbalYaw_update
        }
        
        if feedback_data_update_1['heading'] != 'N/A':
            if float(feedback_data_update_1['heading']) < 0.0:
                feedback_data_update_1['heading'] = 360 + float(feedback_data_update_1['heading'])
                feedback_data_update_1['heading'] = str(feedback_data_update_1['heading'])
        
        publish_feedback(active_clients[21], feedback_data_update_1, 1) # publish the feedback data to the client
            
        # Hold the drone at the waypoint for a specified length of time
        if drone1_LengthOfStay_update > 0:
            if debug:
                print("drone1_Waypointdata_before_holding:", drone1_Telemetry_data)
            
                print(f'drone1 is waiting  for {drone1_LengthOfStay_update} sn before taking the image and saving the telemetry data')   
                time.sleep(drone1_LengthOfStay_update)  
        
        # Call the telemetry data again
        drone1_Image_Telemetry_data = w.getImageAndTelemetryData(1)
        
        if((len(drone1_Image_Telemetry_data)) > 2000000):
            drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[3110408:]).decode())
        else:
            drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[1382408:]).decode())
                
        #drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[1382408:]).decode())
        
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
        
        if((len(drone1_Image_Telemetry_data)) > 2000000):
            crop_size = 1080
            if decoding == 'software':
                drone1_Image = cv2.cvtColor(drone1_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV420p2RGB)   # for software decoding

            elif decoding == 'hardware':
                drone1_Image = cv2.cvtColor(drone1_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV2BGR_NV12) # for hardware decoding
        else:
            crop_size = 720
            if decoding == 'software':
                drone1_Image = cv2.cvtColor(drone1_Image_Telemetry_data[0:1382400].reshape(720*3//2, 1280), cv2.COLOR_YUV420p2RGB)   # for software decoding

            elif decoding == 'hardware':
                drone1_Image = cv2.cvtColor(drone1_Image_Telemetry_data[0:1382400].reshape(720*3//2, 1280), cv2.COLOR_YUV2BGR_NV12) # for hardware decoding
        
        
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
            waypoint_folder = f'drone1_waypoint_{(drone1_waypoint_no-2)/2}_('+ task + ')'
            waypoint_path = os.path.join(Images_Path, waypoint_folder)
            if not os.path.exists(waypoint_path):
                os.mkdir(waypoint_path)
                
            else:
                print("Folder already exists for drone1 (update)")
                
            cv2.imwrite(os.path.join( waypoint_path, 'drone1Image' + str(drone1_waypoint_no)+'.png'), drone1_cropped_Image)
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
                # Check if the drone is in manual mode
                
                drone1_Image_Telemetry_data = w.getImageAndTelemetryData(1) # 1 refers to the drone number
                    
                if((len(drone1_Image_Telemetry_data)) > 2000000):
                    drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone1_Telemetry_data = (bytearray(drone1_Image_Telemetry_data[1382408:]).decode())
                    
                drone1_elements = drone1_Telemetry_data.split(":")                 # Extract all elements from the string

                # check 16th element to see if the drone is in manual mode

                if float(drone1_elements[16]) == 0.0:
                    drone_1_incrementor = 1
                else:
                    drone_1_incrementor = incrementor
                
            with lock:    
                if task == 'takeoff and waypoint':
                    print("Takeoff and Mission Waypoint for drone1 completed")
                elif task == 'update_camera_parameters':
                    print("Camera parameters updated for drone1")
                elif task == 'land':
                    print("Land completed for drone1")
                elif task == 'emergency':
                    print("Emergency Case")
                else:
                    print("Invalid task")
            with lock:
                drone_1_thread_stop = True
                update_looking_drone_1 = True
            
            print('incromentor:', incrementor)  
                    
            break
             

######################## Drone 2 Thread ############################
d2Image = []
d2Poses= []

def waypoint_tread_drone2(task,drone2_Latitude_List, drone2_Longitude_list, drone2_Altitude_list, drone2_Heading_list, drone2_Speed_list, Way2_threshold, camera_list, lengthOfStay_list, gimbalPitch_list, gimbalYaw_list, drone2_parameter_mode, drone2_rx_threshold, drone2_compass_correction, drone2_focal_length, drone2_focal_plane_pitch, drone2_focal_plane_roll, drone2_integration_window, drone2_minimum_pose_distance):
    
    number_of_waypoints_for_drone2 = len(drone2_Latitude_List)
    print(f"Number of waypoints for drone2: {number_of_waypoints_for_drone2}")
    
    drone2_new_parameter_integral_go = 1 # for triggering integration while reaching (go) to the waypoint 
    drone2_new_parameter_integral_update = 0
    
    global drone_2_incrementor, drone2_waypoint_no, camera, stop_waypoint_mission, break_while, drone_2_break_while, drone_2_thread_stop, update_looking_drone_2, active_clients
    
    with lock:   
        drone_2_thread_stop = False
        update_looking_drone_2 = False
        
    incrementor = drone_2_incrementor
    
    previous_speed_list_drone2 = [drone2_Speed_list[0], *drone2_Speed_list]
    previous_heading_list_drone2 = [drone2_Heading_list[0], *drone2_Heading_list]
    previous_camera_list_drone2 = [camera_list[0], *camera_list]
    previous_lengthOfStay_list_drone2 = [lengthOfStay_list[0], *lengthOfStay_list]
    previous_gimbalPitch_list_drone2 = [gimbalPitch_list[0], *gimbalPitch_list]
    previous_gimbalYaw_list_drone2 = [gimbalYaw_list[0], *gimbalYaw_list]
    previous_drone2_rx_threshold = [drone2_rx_threshold[0], *drone2_rx_threshold]
    previous_drone2_compass_correction = [drone2_compass_correction[0], *drone2_compass_correction]
    previous_drone2_focal_length = [drone2_focal_length[0], *drone2_focal_length]
    previous_drone2_focal_plane_pitch = [drone2_focal_plane_pitch[0], *drone2_focal_plane_pitch]
    previous_drone2_focal_plane_roll = [drone2_focal_plane_roll[0], *drone2_focal_plane_roll]
    previous_drone2_integration_window = [drone2_integration_window[0], *drone2_integration_window]
    previous_drone2_minimum_pose_distance = [drone2_minimum_pose_distance[0], *drone2_minimum_pose_distance]
    
    iteration = 0
    
    while True:
        
        # Check if the drone is in manual mode
        
        drone2_Image_Telemetry_data = w.getImageAndTelemetryData(2) # 2 refers to the drone number
        
        if((len(drone2_Image_Telemetry_data)) > 2000000):
            drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[3110408:]).decode())
        else:
            drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[1382408:]).decode())
            
        drone2_elements = drone2_Telemetry_data.split(":")                 # Extract all elements from the string
        
        # check 16th element to see if the drone is in manual mode
        if float(drone2_elements[16]) == 0.0:
            with lock:
                drone_2_incrementor = 1
            break

        if task == 'takeoff and waypoint' or task == 'update_camera_parameters':
            with lock:
                drone2_waypoint_no = drone2_waypoint_no + 1
            print(f"Mission Waypoint {drone2_waypoint_no} in progress for drone2 ...") 

            drone2_Latitude_go = drone2_Latitude_List[iteration]
            drone2_Longitude_go = drone2_Longitude_list[iteration]
            drone2_Altitude_go = drone2_Altitude_list[iteration]
            drone2_Heading_go = previous_heading_list_drone2[iteration]
            drone2_Speed_go = previous_speed_list_drone2[iteration]
            drone2_Camera_go = previous_camera_list_drone2[iteration]
            drone2_LengthOfStay_go = previous_lengthOfStay_list_drone2[iteration]
            drone2_GimbalPitch_go = previous_gimbalPitch_list_drone2[iteration]
            drone2_GimbalYaw_go = previous_gimbalYaw_list_drone2[iteration]
            drone2_Integration_window_go = previous_drone2_integration_window[iteration]
            drone2_Minimum_Pose_Distance_go = previous_drone2_minimum_pose_distance[iteration]
            
            drone2_Rx_threshold = previous_drone2_rx_threshold[iteration]
            drone2_Compass_correction = previous_drone2_compass_correction[iteration]
            drone2_Focal_length = previous_drone2_focal_length[iteration]
            drone2_Focal_plane_pitch = previous_drone2_focal_plane_pitch[iteration]
            drone2_Focal_plane_roll = previous_drone2_focal_plane_roll[iteration]
            
            
            drone2_Latitude_update = drone2_Latitude_List[iteration]
            drone2_Longitude_update = drone2_Longitude_list[iteration]
            drone2_Altitude_update = drone2_Altitude_list[iteration]
            drone2_Heading_update = drone2_Heading_list[iteration]
            drone2_Speed_update = drone2_Speed_list[iteration]
            drone2_Camera_update = camera_list[iteration]
            drone2_LengthOfStay_update = lengthOfStay_list[iteration]
            drone2_GimbalPitch_update = gimbalPitch_list[iteration]
            drone2_GimbalYaw_update = gimbalYaw_list[iteration]
            drone2_Integration_window_update = drone2_integration_window[iteration]
            drone2_Minimum_Pose_Distance_update = drone2_minimum_pose_distance[iteration]
            
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
            drone2_Integration_window_go = drone2_integration_window[iteration]
            drone2_Minimum_Pose_Distance_go = drone2_minimum_pose_distance[iteration]
            
            drone2_Rx_threshold = previous_drone2_rx_threshold[iteration]
            drone2_Compass_correction = previous_drone2_compass_correction[iteration]
            drone2_Focal_length = previous_drone2_focal_length[iteration]
            drone2_Focal_plane_pitch = previous_drone2_focal_plane_pitch[iteration]
            drone2_Focal_plane_roll = previous_drone2_focal_plane_roll[iteration]
            
            drone2_Latitude_update = drone2_Latitude_List[iteration + 1]
            drone2_Longitude_update = drone2_Longitude_list[iteration + 1]
            drone2_Altitude_update = drone2_Altitude_list[iteration + 1]
            drone2_Heading_update = drone2_Heading_list[iteration + 1]
            drone2_Speed_update = drone2_Speed_list[iteration + 1]
            drone2_Camera_update = camera_list[iteration + 1]
            drone2_LengthOfStay_update = lengthOfStay_list[iteration + 1]
            drone2_GimbalPitch_update = gimbalPitch_list[iteration + 1]
            drone2_GimbalYaw_update = gimbalYaw_list[iteration + 1]
            drone2_Integration_window_update = drone2_integration_window[iteration + 1]
            drone2_Minimum_Pose_Distance_update = drone2_minimum_pose_distance[iteration + 1]
            
            iteration += 2  
             
        waypointvalue2 = incrementor
        
        ################ for reaching the waypoint ################
        
        if stop_waypoint_mission:
            with lock:
                drone_2_incrementor = incrementor
            break
            
        if task == 'update_camera_parameters':
            pass
        else:
            print("waypointvalue2_drone2(go):", waypointvalue2, "\n")
            
            drone2_waypoint_data_reached = f"{drone2_Latitude_go}:{drone2_Longitude_go}:{drone2_Altitude_go}:{drone2_Heading_go}:{drone2_Speed_go}:{waypointvalue2}:{Way2_threshold}:{drone2_GimbalPitch_go}:{drone2_GimbalYaw_go}:{drone2_Camera_go}:{drone2_parameter_mode}:{drone2_Rx_threshold}:{drone2_Compass_correction}:{drone2_Focal_length}:{drone2_Focal_plane_pitch}:{drone2_Focal_plane_roll}:{drone2_new_parameter_integral_go}:{drone2_Integration_window_go}:{drone2_Minimum_Pose_Distance_go}"
            
            drone2_send_data = w.sendWayPointData(drone2_waypoint_data_reached, 2)     # 2 refers to the drone number
            
            drone2_waypoint_data_sent = f"Lat: {drone2_Latitude_go}, Long: {drone2_Longitude_go}, Alt: {drone2_Altitude_go}, Heading: {drone2_Heading_go}, Speed: {drone2_Speed_go}, Waypoint: {waypointvalue2}, Threshold: {Way2_threshold}, Gimbal Pitch: {drone2_GimbalPitch_go}, Gimbal Yaw: {drone2_GimbalYaw_go}, Camera: {drone2_Camera_go}, Mode: {drone2_parameter_mode}, RX Threshold: {drone2_Rx_threshold}, Compass Correction: {drone2_Compass_correction}, Focal Length: {drone2_Focal_length}, Focal Plane Pitch: {drone2_Focal_plane_pitch}, Focal Plane Roll: {drone2_Focal_plane_roll}, Integral: {drone2_new_parameter_integral_go}, Integration Window: {drone2_Integration_window_go}, Minimum Pose Distance: {drone2_Minimum_Pose_Distance_go}"

            print("Data being Sent for drone2 (go):", drone2_waypoint_data_sent)
            
            while True:
                if break_while or drone_2_break_while:
                    break

                drone2_send_data = w.sendWayPointData(drone2_waypoint_data_reached, 2) 
                
                drone2_Image_Telemetry_data = w.getImageAndTelemetryData(2)
                if((len(drone2_Image_Telemetry_data)) > 2000000):
                    drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[1382408:]).decode())
                #drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[1382408:]).decode())
                
                drone2_elements = drone2_Telemetry_data.split(":")                 # Extract all elements from the string
                drone2_Waypoint_sent = drone2_elements[15].split('.')[0]
                # print("drone2_Waypoint_sent_for_go:",drone2_Waypoint_sent)
                
                # check 16th element to see if the drone is in manual mode
                
                if debug:
                    print("drone2_elements[16]_1:",drone2_elements[16])
                
                if float(drone2_elements[16]) == 0.0:
                    with lock:
                        drone_2_incrementor = 1
                    break
                
                if (drone2_Waypoint_sent) == str(incrementor) or break_while == True or drone_2_break_while == True:
                    if debug: 
                        print("drone2 Waypoint data sent for go")
                        print ("go thread for drone2:", drone2_Waypoint_sent, incrementor)
                    break
            
            if break_while or drone_2_break_while:
                with lock:
                    drone_2_incrementor = incrementor + 1  
                    drone_2_thread_stop = True 
                break
            
                
            while True:
                if break_while or drone_2_break_while:
                    break
                
                drone2_Image_Telemetry_data = w.getImageAndTelemetryData(2)
                if((len(drone2_Image_Telemetry_data)) > 2000000):
                    drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[1382408:]).decode())
                #drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[1382408:]).decode())
                
                drone2_elements = drone2_Telemetry_data.split(":")                 # Extract all elements from the string
                drone2_Waypoint_reached = drone2_elements[14]
                
                if debug:
                    print("drone2_elements[16]_2:", drone2_elements[16])
                
                if float(drone2_elements[16]) == 0.0:
                    with lock:
                        drone_2_incrementor = 1
                    break

                if drone2_Waypoint_reached == str(incrementor) or break_while == True or drone_2_break_while == True:
                    if debug:
                        print("drone2 Waypoint has been reached")
                        print ("go thread waypoint reached for drone2:", drone2_Waypoint_reached, incrementor)
                    break
            
            if break_while or drone_2_break_while:
                with lock:
                    drone_2_incrementor = incrementor + 1
                    drone_2_thread_stop = True
                break
                   
            # Call the telemetry data again
            drone2_Image_Telemetry_data = w.getImageAndTelemetryData(2)
            if((len(drone2_Image_Telemetry_data)) > 2000000):
                drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[3110408:]).decode())
            else:
                drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[1382408:]).decode())
            #drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[1382408:]).decode())
            
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
        drone2_waypoint_data = f"{drone2_Latitude_update}:{drone2_Longitude_update}:{drone2_Altitude_update}:{drone2_Heading_update}:{drone2_Speed_update}:{waypointvalue2_update}:{Way2_threshold}:{drone2_GimbalPitch_update}:{drone2_GimbalYaw_update}:{drone2_Camera_update}:{drone2_parameter_mode}:{drone2_Rx_threshold}:{drone2_Compass_correction}:{drone2_Focal_length}:{drone2_Focal_plane_pitch}:{drone2_Focal_plane_roll}:{drone2_new_parameter_integral_update}:{drone2_Integration_window_update}:{drone2_Minimum_Pose_Distance_update}"
        
        drone2_send_data = w.sendWayPointData(drone2_waypoint_data, 2)     # 2 refers to the drone number
        
        drone2_waypoint_data_sent = f"Lat: {drone2_Latitude_update}, Long: {drone2_Longitude_update}, Alt: {drone2_Altitude_update}, Heading: {drone2_Heading_update}, Speed: {drone2_Speed_update}, Waypoint: {waypointvalue2_update}, Threshold: {Way2_threshold}, Gimbal Pitch: {drone2_GimbalPitch_update}, Gimbal Yaw: {drone2_GimbalYaw_update}, Camera: {drone2_Camera_update}, Mode: {drone2_parameter_mode}, RX Threshold: {drone2_Rx_threshold}, Compass Correction: {drone2_Compass_correction}, Focal Length: {drone2_Focal_length}, Focal Plane Pitch: {drone2_Focal_plane_pitch}, Focal Plane Roll: {drone2_Focal_plane_roll}, Integral: {drone2_new_parameter_integral_update}, Integration Window: {drone2_Integration_window_update}, Minimum Pose Distance: {drone2_Minimum_Pose_Distance_update}"
        
        print("Data Being Sent for drone2 (update) :",drone2_waypoint_data_sent)
        
        while True:
            if break_while or drone_2_break_while:
                break
        
            drone2_send_data = w.sendWayPointData(drone2_waypoint_data, 2) 
            drone2_Image_Telemetry_data = w.getImageAndTelemetryData(2)
            if((len(drone2_Image_Telemetry_data)) > 2000000):
                drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[3110408:]).decode())
            else:
                drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[1382408:]).decode())
            #drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[1382408:]).decode())
            
            drone2_elements = drone2_Telemetry_data.split(":")                 # Extract all elements from the string
            drone2_Waypoint_sent = drone2_elements[15].split('.')[0]
            # print("drone2_Waypoint_sent:",drone2_Waypoint_sent)
            
            if debug:
                print("drone2_elements[16]_3:",drone2_elements[16])
            
            if float(drone2_elements[16]) == 0.0:
                with lock:
                    drone_2_incrementor = 1
                break
            if (drone2_Waypoint_sent) == str(incrementor) or break_while == True or drone_2_break_while == True:
                if debug: 
                    print("drone2 Waypoint data sent")
                    print ("run thread for drone2:", drone2_Waypoint_sent, incrementor)
                break
        
        if break_while or drone_2_break_while:
            
            with lock:
                drone_2_incrementor = incrementor + 1
                drone_2_thread_stop = True
            break   
            
        while True: 
            if break_while or drone_2_break_while:
                break
            
            drone2_Image_Telemetry_data = w.getImageAndTelemetryData(2)
            if((len(drone2_Image_Telemetry_data)) > 2000000):
                drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[3110408:]).decode())
            else:
                drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[1382408:]).decode())
            #drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[1382408:]).decode())
            
            drone2_elements = drone2_Telemetry_data.split(":")                 # Extract all elements from the string
            drone2_Waypoint_reached = drone2_elements[14]
            
            if debug:
                print("drone2_elements[16]_4:",drone2_elements[16])
            
            if float(drone2_elements[16]) == 0.0:
                with lock:
                    drone_2_incrementor = 1
                break

            if drone2_Waypoint_reached == str(incrementor) or break_while == True or drone_2_break_while == True:
                if debug:
                    print("drone2 Waypoint has been reached")
                    print ("run thread waypoint reached:", drone2_Waypoint_reached, incrementor)
                break
        
        if break_while or drone_2_break_while:
            with lock:
                drone_2_incrementor = incrementor + 1
                drone_2_thread_stop = True
            break
        
        feedback_data_update_2 = {
                'drone_id': 2,
                'heading': drone2_Heading_update,
                'gimbalPitch': drone2_GimbalPitch_update,
                'gimbalYaw': drone2_GimbalYaw_update
            }
        
        if feedback_data_update_2['heading'] != 'N/A':
            if float(feedback_data_update_2['heading']) < 0.0:
                feedback_data_update_2['heading'] = 360.0 + float(feedback_data_update_2['heading'])
                feedback_data_update_2['heading'] = str(feedback_data_update_2['heading'])
            
        publish_feedback(active_clients[22], feedback_data_update_2, 2) # publish the feedback data to the client
               
        # Hold the drone at the waypoint for a specified length of time
        if drone2_LengthOfStay_update > 0:
            if debug:
                print("drone2_Waypointdata_before_holding:", drone2_Telemetry_data)
            
                print(f'drone2 is waiting  for {drone2_LengthOfStay_update} sn before taking the image and saving the telemetry data')   
                time.sleep(drone2_LengthOfStay_update)
            
        # Call the telemetry data again
        drone2_Image_Telemetry_data = w.getImageAndTelemetryData(2)
        if((len(drone2_Image_Telemetry_data)) > 2000000):
            drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[3110408:]).decode())
        else:
            drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[1382408:]).decode())
        #drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[1382408:]).decode())
        
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
            
            
        if((len(drone2_Image_Telemetry_data)) > 2000000):
            crop_size = 1080
            if decoding == 'software':
                drone2_Image = cv2.cvtColor(drone2_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV420p2RGB)   # for software decoding

            elif decoding == 'hardware':
                drone2_Image = cv2.cvtColor(drone2_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV2BGR_NV12) # for hardware decoding
        else:
            crop_size = 720
            if decoding == 'software':
                drone2_Image = cv2.cvtColor(drone2_Image_Telemetry_data[0:1382400].reshape(720*3//2, 1280), cv2.COLOR_YUV420p2RGB)   # for software decoding

            elif decoding == 'hardware':
                drone2_Image = cv2.cvtColor(drone2_Image_Telemetry_data[0:1382400].reshape(720*3//2, 1280), cv2.COLOR_YUV2BGR_NV12) # for hardware decoding
            
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
            waypoint_folder = f'drone2_waypoint_{drone2_waypoint_no}_('+ task + ')'
            waypoint_path = os.path.join(Images_Path, waypoint_folder)
            if not os.path.exists(waypoint_path):
                os.mkdir(waypoint_path)
            else:
                print("Folder already exists for drone2 (update)")
                
            cv2.imwrite(os.path.join( waypoint_path, 'drone2Image' + str(drone2_waypoint_no)+'.png'), drone2_cropped_Image)
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
                
                # Check if the drone is in manual mode
                drone2_Image_Telemetry_data = w.getImageAndTelemetryData(2) # 2 refers to the drone number
                
                if((len(drone2_Image_Telemetry_data)) > 2000000):
                    drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone2_Telemetry_data = (bytearray(drone2_Image_Telemetry_data[1382408:]).decode())
                    
                drone2_elements = drone2_Telemetry_data.split(":")                 # Extract all elements from the string
                
                # check 16th element to see if the drone is in manual mode
                if float(drone2_elements[16]) == 0.0:
                    drone_2_incrementor = 1
                else:
                    drone_2_incrementor = incrementor
            
            if task == 'takeoff and waypoint':
                print("Takeoff and Mission Waypoint for drone2 completed")
            elif task == 'update_camera_parameters':
                print("Camera parameters updated for drone2")
            elif task == 'land':
                print("Land completed for drone2")
            elif task == 'emergency':
                print("Emergency Case")
            else:
                print("Invalid task") 
            
            with lock:
                drone_2_thread_stop = True
                update_looking_drone_2 = True
            break
        
######################## Drone 3 Thread ############################
d3Image = []
d3Poses= []

def waypoint_tread_drone3(task, drone3_Latitude_List, drone3_Longitude_list, drone3_Altitude_list, drone3_Heading_list, drone3_Speed_list, Way3_threshold, camera_list, lengthOfStay_list, gimbalPitch_list, gimbalYaw_list, drone3_parameter_mode, drone3_rx_threshold, drone3_compass_correction, drone3_focal_length, drone3_focal_plane_pitch, drone3_focal_plane_roll, drone3_integration_window, drone3_minimum_pose_distance):
    
    number_of_waypoints_for_drone3 = len(drone3_Latitude_List)
    print("Number of waypoints for drone3:", number_of_waypoints_for_drone3)
    
    drone3_new_parameter_integral_go = 1 # for triggering integration while reaching (go) to the waypoint 
    drone3_new_parameter_integral_update = 0
    
    global drone_3_incrementor, drone3_waypoint_no, camera, stop_waypoint_mission, break_while, drone_3_break_while, drone_3_thread_stop, update_looking_drone_3, active_clients
    
    with lock:   
        drone_3_thread_stop = False
        update_looking_drone_3 = False
        
    incrementor = drone_3_incrementor
    
    previous_speed_list_drone3 = [drone3_Speed_list[0], *drone3_Speed_list]
    previous_heading_list_drone3 = [drone3_Heading_list[0], *drone3_Heading_list]
    previous_camera_list_drone3 = [camera_list[0], *camera_list]
    previous_lengthOfStay_list_drone3 = [lengthOfStay_list[0], *lengthOfStay_list]
    previous_gimbalPitch_list_drone3 = [gimbalPitch_list[0], *gimbalPitch_list]
    previous_gimbalYaw_list_drone3 = [gimbalYaw_list[0], *gimbalYaw_list]
    previous_drone3_rx_threshold = [drone3_rx_threshold[0], *drone3_rx_threshold]
    previous_drone3_compass_correction = [drone3_compass_correction[0], *drone3_compass_correction]
    previous_drone3_focal_length = [drone3_focal_length[0], *drone3_focal_length]
    previous_drone3_focal_plane_pitch = [drone3_focal_plane_pitch[0], *drone3_focal_plane_pitch]
    previous_drone3_focal_plane_roll = [drone3_focal_plane_roll[0], *drone3_focal_plane_roll]
    previous_drone3_integration_window = [drone3_integration_window[0], *drone3_integration_window]
    previous_drone3_minimum_pose_distance = [drone3_minimum_pose_distance[0], *drone3_minimum_pose_distance]
    
    iteration = 0
    
    while True:
        
        # Check if the drone is in manual mode
        
        drone3_Image_Telemetry_data = w.getImageAndTelemetryData(3) # 3 refers to the drone number
        
        if((len(drone3_Image_Telemetry_data)) > 2000000):
            drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[3110408:]).decode())
        else:
            drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[1382408:]).decode())
            
        drone3_elements = drone3_Telemetry_data.split(":")                 # Extract all elements from the string
        
        # check 16th element to see if the drone is in manual mode
        if float(drone3_elements[16]) == 0.0:
            with lock:
                drone_3_incrementor = 1
            break

        if task == 'takeoff and waypoint' or task == 'update_camera_parameters':
            with lock:
                drone3_waypoint_no = drone3_waypoint_no + 1       
            print(f"Mission Waypoint {drone3_waypoint_no} in progress for drone3 ...") 

            drone3_Latitude_go = drone3_Latitude_List[iteration]
            drone3_Longitude_go = drone3_Longitude_list[iteration]
            drone3_Altitude_go = drone3_Altitude_list[iteration]
            drone3_Heading_go = previous_heading_list_drone3[iteration]
            drone3_Speed_go = previous_speed_list_drone3[iteration]
            drone3_Camera_go = previous_camera_list_drone3[iteration]
            drone3_LengthOfStay_go = previous_lengthOfStay_list_drone3[iteration]
            drone3_GimbalPitch_go = previous_gimbalPitch_list_drone3[iteration]
            drone3_GimbalYaw_go = previous_gimbalYaw_list_drone3[iteration]
            drone3_Integration_Window_go = previous_drone3_integration_window[iteration]
            drone3_Minimum_Pose_Distance_go = previous_drone3_minimum_pose_distance[iteration]
            
            drone3_Rx_threshold = previous_drone3_rx_threshold[iteration]
            drone3_Compass_correction = previous_drone3_compass_correction[iteration]
            drone3_Focal_length = previous_drone3_focal_length[iteration]
            drone3_Focal_plane_pitch = previous_drone3_focal_plane_pitch[iteration]
            drone3_Focal_plane_roll = previous_drone3_focal_plane_roll[iteration]
            
            drone3_Latitude_update = drone3_Latitude_List[iteration]
            drone3_Longitude_update = drone3_Longitude_list[iteration]
            drone3_Altitude_update = drone3_Altitude_list[iteration]
            drone3_Heading_update = drone3_Heading_list[iteration]
            drone3_Speed_update = drone3_Speed_list[iteration]
            drone3_Camera_update = camera_list[iteration]
            drone3_LengthOfStay_update = lengthOfStay_list[iteration]
            drone3_GimbalPitch_update = gimbalPitch_list[iteration]
            drone3_GimbalYaw_update = gimbalYaw_list[iteration]
            drone3_Integration_Window_update = drone3_integration_window[iteration]
            drone3_Minimum_Pose_Distance_update = drone3_minimum_pose_distance[iteration]

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
            drone3_Integration_Window_go = drone3_integration_window[iteration]
            drone3_Minimum_Pose_Distance_go = drone3_minimum_pose_distance[iteration]
            
            drone3_Rx_threshold = previous_drone3_rx_threshold[iteration]
            drone3_Compass_correction = previous_drone3_compass_correction[iteration]
            drone3_Focal_length = previous_drone3_focal_length[iteration]
            drone3_Focal_plane_pitch = previous_drone3_focal_plane_pitch[iteration]
            drone3_Focal_plane_roll = previous_drone3_focal_plane_roll[iteration]
            
            
            drone3_Latitude_update = drone3_Latitude_List[iteration + 1]
            drone3_Longitude_update = drone3_Longitude_list[iteration + 1]
            drone3_Altitude_update = drone3_Altitude_list[iteration + 1]
            drone3_Heading_update = drone3_Heading_list[iteration + 1]
            drone3_Speed_update = drone3_Speed_list[iteration + 1]
            drone3_Camera_update = camera_list[iteration + 1]
            drone3_LengthOfStay_update = lengthOfStay_list[iteration + 1]
            drone3_GimbalPitch_update = gimbalPitch_list[iteration + 1]
            drone3_GimbalYaw_update = gimbalYaw_list[iteration + 1]
            drone3_Integration_Window_update = drone3_integration_window[iteration + 1]
            drone3_Minimum_Pose_Distance_update = drone3_minimum_pose_distance[iteration + 1]
            
            iteration += 2
                  
        waypointvalue3 = incrementor
        ################ for reaching the waypoint ################
        
        if stop_waypoint_mission:
            with lock:
                drone_3_incrementor = incrementor
            break
            
        if task == 'update_camera_parameters':
            pass
        else:

            print("waypointvalue3_drone3(go):",waypointvalue3, "\n")
            
            drone3_waypoint_data_reached = f"{drone3_Latitude_go}:{drone3_Longitude_go}:{drone3_Altitude_go}:{drone3_Heading_go}:{drone3_Speed_go}:{waypointvalue3}:{Way3_threshold}:{drone3_GimbalPitch_go}:{drone3_GimbalYaw_go}:{drone3_Camera_go}:{drone3_parameter_mode}:{drone3_Rx_threshold}:{drone3_Compass_correction}:{drone3_Focal_length}:{drone3_Focal_plane_pitch}:{drone3_Focal_plane_roll}: {drone3_new_parameter_integral_go}:{drone3_Integration_Window_go}:{drone3_Minimum_Pose_Distance_go}"
            
            drone3_send_data = w.sendWayPointData(drone3_waypoint_data_reached, 3)     # 3 refers to the drone number
            
            drone3_waypoint_data_sent = f"Lat: {drone3_Latitude_go}, Long: {drone3_Longitude_go}, Alt: {drone3_Altitude_go}, Heading: {drone3_Heading_go}, Speed: {drone3_Speed_go}, Waypoint: {waypointvalue3}, Threshold: {Way3_threshold}, Gimbal Pitch: {drone3_GimbalPitch_go}, Gimbal Yaw: {drone3_GimbalYaw_go}, Camera: {drone3_Camera_go}, Mode: {drone3_parameter_mode}, RX Threshold: {drone3_Rx_threshold}, Compass Correction: {drone3_Compass_correction}, Focal Length: {drone3_Focal_length}, Focal Plane Pitch: {drone3_Focal_plane_pitch}, Focal Plane Roll: {drone3_Focal_plane_roll}, Integral: {drone3_new_parameter_integral_go}, Integration Window: {drone3_Integration_Window_go}, Minimum Pose Distance: {drone3_Minimum_Pose_Distance_go}"
            
            # if debug:
            print("Data being Sent for drone3 (go):",drone3_waypoint_data_sent)
            
            ## Check if the drone has reached the waypoint, element (14) of the getImageAndTelemetryData string is set to 1. Extract the image and telemetry data when the condition is met. ## Every time the drone receive the next waypoints this element is set to zero again ion the drone app.
            
            while True:
                
                if break_while == True or drone_3_break_while == True:
                    break
                
                drone3_send_data = w.sendWayPointData(drone3_waypoint_data_reached, 3)
                 
                drone3_Image_Telemetry_data = w.getImageAndTelemetryData(3)
                if((len(drone3_Image_Telemetry_data)) > 2000000):
                    drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[1382408:]).decode())
                #drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[1382408:]).decode())
                
                drone3_elements = drone3_Telemetry_data.split(":")                 # Extract all elements from the string
                drone3_Waypoint_sent = drone3_elements[15].split('.')[0]
                # print("drone3_Waypoint_sent_for_go:",drone3_Waypoint_sent)
                # check 16th element to see if the drone is in manual mode
                
                if debug:
                    print("drone3_elements[16]_1:",drone3_elements[16])
                
                if float(drone3_elements[16]) == 0.0:
                    with lock:
                        drone_3_incrementor = 1
                    break
                
                if (drone3_Waypoint_sent) == str(incrementor) or break_while == True or drone_3_break_while == True:
                    if debug: 
                        print("drone3 Waypoint data sent for go")
                        print ("go thread for drone3:", drone3_Waypoint_sent, incrementor)
                    break
                
            if break_while or drone_3_break_while:
                with lock:
                    drone_3_incrementor = incrementor + 1
                    drone_3_thread_stop = True
                break
                  
            while True:
                
                if break_while == True or drone_3_break_while == True:
                    break
                
                drone3_Image_Telemetry_data = w.getImageAndTelemetryData(3)
                if((len(drone3_Image_Telemetry_data)) > 2000000):
                    drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[1382408:]).decode())
                #drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[1382408:]).decode())
                
                drone3_elements = drone3_Telemetry_data.split(":")                 # Extract all elements from the string
                drone3_Waypoint_reached = drone3_elements[14]
                
                # print("drone3_Waypoint_reached:",drone3_Waypoint_reached)
                # print("incrementor:", incrementor)
                
                if debug:
                    print("drone3_elements[16]_2:",drone3_elements[16])
                
                if float(drone3_elements[16]) == 0.0:
                    with lock:    
                        drone_3_incrementor = 1
                    break
                
                if drone3_Waypoint_reached == str(incrementor) or break_while == True or drone_3_break_while == True:
                    if debug:
                        print("drone3 Waypoint has been reached")
                        print ("go thread waypoint reached for drone3:", drone3_Waypoint_reached, incrementor)
                    break
            
            if break_while or drone_3_break_while:
                with lock:
                    drone_3_incrementor = incrementor + 1
                    drone_3_thread_stop = True
                break 
            
            # Call the telemetry data again
            drone3_Image_Telemetry_data = w.getImageAndTelemetryData(3)
            
            if((len(drone3_Image_Telemetry_data)) > 2000000):
                drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[3110408:]).decode())
            else:
                drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[1382408:]).decode())
            #drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[1382408:]).decode())
            
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
        
        drone3_waypoint_data = f"{drone3_Latitude_update}:{drone3_Longitude_update}:{drone3_Altitude_update}:{drone3_Heading_update}:{drone3_Speed_update}:{waypointvalue3_update}:{Way3_threshold}:{drone3_GimbalPitch_update}:{drone3_GimbalYaw_update}:{drone3_Camera_update}:{drone3_parameter_mode}:{drone3_Rx_threshold}:{drone3_Compass_correction}:{drone3_Focal_length}:{drone3_Focal_plane_pitch}:{drone3_Focal_plane_roll}:{drone3_new_parameter_integral_update}:{drone3_Integration_Window_update}:{drone3_Minimum_Pose_Distance_update}"
        
        drone3_send_data = w.sendWayPointData(drone3_waypoint_data, 3)     # 3 refers to the drone number
        
        drone3_waypoint_data_sent = f"Lat: {drone3_Latitude_update}, Long: {drone3_Longitude_update}, Alt: {drone3_Altitude_update}, Heading: {drone3_Heading_update}, Speed: {drone3_Speed_update}, Waypoint: {waypointvalue3_update}, Threshold: {Way3_threshold}, Gimbal Pitch: {drone3_GimbalPitch_update}, Gimbal Yaw: {drone3_GimbalYaw_update}, Camera: {drone3_Camera_update}, Mode: {drone3_parameter_mode}, RX Threshold: {drone3_Rx_threshold}, Compass Correction: {drone3_Compass_correction}, Focal Length: {drone3_Focal_length}, Focal Plane Pitch: {drone3_Focal_plane_pitch}, Focal Plane Roll: {drone3_Focal_plane_roll}, Integral: {drone3_new_parameter_integral_update}, Integration Window: {drone3_Integration_Window_update}, Minimum Pose Distance: {drone3_Minimum_Pose_Distance_update}"
        
        # if debug:
        print("Data Being Sent for drone3 (update) :",drone3_waypoint_data_sent)
        
        # with lock:
        #     camera[2] = drone3_Camera_update
        
        ## Check if the drone has reached the waypoint, element (14) of the getImageAndTelemetryData string is set to 1. Extract the image and telemetry data when the condition is met. ## Every time the drone receive the next waypoints this element is set to zero again ion the drone app.
        
        while True:
            
            if break_while == True or drone_3_break_while == True:
                break
        
            drone3_send_data = w.sendWayPointData(drone3_waypoint_data, 3) 
            drone3_Image_Telemetry_data = w.getImageAndTelemetryData(3)
            if((len(drone3_Image_Telemetry_data)) > 2000000):
                drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[3110408:]).decode())
            else:
                drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[1382408:]).decode())
            #drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[1382408:]).decode())
            
            drone3_elements = drone3_Telemetry_data.split(":")                 # Extract all elements from the string
            drone3_Waypoint_sent = drone3_elements[15].split('.')[0]
            # print("drone3_Waypoint_sent:",drone3_Waypoint_sent)
            
            if debug:
                print("drone3_elements[16]_3:",drone3_elements[16])
            
            if float(drone3_elements[16]) == 0.0:
                with lock:
                    drone_3_incrementor = 1
                break
            
            if (drone3_Waypoint_sent) == str(incrementor) or break_while == True:
                if debug: 
                    print("drone3 Waypoint data sent")
                    print ("run thread for drone3:", drone3_Waypoint_sent, incrementor)
                break
            
        if break_while or drone_3_break_while:
            with lock:
                drone_3_incrementor = incrementor + 1
                drone_3_thread_stop = True
            break
   
        while True:
            if break_while == True or drone_3_break_while == True:
                break
            
            drone3_Image_Telemetry_data = w.getImageAndTelemetryData(3)
            if((len(drone3_Image_Telemetry_data)) > 2000000):
                drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[3110408:]).decode())
            else:
                drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[1382408:]).decode())
            #drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[1382408:]).decode())
            
            drone3_elements = drone3_Telemetry_data.split(":")                 # Extract all elements from the string
            drone3_Waypoint_reached = drone3_elements[14]
            
            # print("drone3_Waypoint_reached:",drone3_Waypoint_reached)
            # print("incrementor:", incrementor)
            
            if debug:
                print("drone3_elements[16]_4:",drone3_elements[16])
            
            if float(drone3_elements[16]) == 0.0:
                with lock:
                    drone_3_incrementor = 1
                break
            
            if drone3_Waypoint_reached == str(incrementor) or break_while == True or drone_3_break_while == True:
                if debug:
                    print("drone3 Waypoint has been reached")
                    print ("run thread waypoint reached:", drone3_Waypoint_reached, incrementor)
                break
 
        if break_while or drone_3_break_while:
            with lock:
                drone_3_incrementor = incrementor + 1
                drone_3_thread_stop = True
            break
        
        feedback_data_update_3 = {
                'drone_id': 3,
                'heading': drone3_Heading_update,
                'gimbalPitch': drone3_GimbalPitch_update,
                'gimbalYaw': drone3_GimbalYaw_update
            }
        if feedback_data_update_3['heading'] != 'N/A':
            if float(feedback_data_update_3['heading']) < 0.0:
                feedback_data_update_3['heading'] = 360.0 + float(feedback_data_update_3['heading'])
                feedback_data_update_3['heading'] = str(feedback_data_update_3['heading'])
            
        publish_feedback(active_clients[23], feedback_data_update_3, 3) # publish the feedback data to the client  # 23 refers to the client number, 3 refers to the drone number
    
        # Hold the drone at the waypoint for a specified length of time
        if drone3_LengthOfStay_update > 0:
            if debug:
                print("drone3_Waypointdata_before_holding:", drone3_Telemetry_data)
            
                print(f'drone3 is waiting  for {drone3_LengthOfStay_update} sn before taking the image and saving the telemetry data')   
                time.sleep(drone3_LengthOfStay_update)
            
        # Call the telemetry data again
        drone3_Image_Telemetry_data = w.getImageAndTelemetryData(3)
        if((len(drone3_Image_Telemetry_data)) > 2000000):
            drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[3110408:]).decode())
        else:
            drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[1382408:]).decode())
        #drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[1382408:]).decode())
        
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
    
        if((len(drone3_Image_Telemetry_data)) > 2000000):
            crop_size = 1080
            if decoding == 'software':
                drone3_Image = cv2.cvtColor(drone3_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV420p2RGB)   # for software decoding

            elif decoding == 'hardware':
                drone3_Image = cv2.cvtColor(drone3_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV2BGR_NV12) # for hardware decoding
        else:
            crop_size = 720
            if decoding == 'software':
                drone3_Image = cv2.cvtColor(drone3_Image_Telemetry_data[0:1382400].reshape(720*3//2, 1280), cv2.COLOR_YUV420p2RGB)   # for software decoding

            elif decoding == 'hardware':
                drone3_Image = cv2.cvtColor(drone3_Image_Telemetry_data[0:1382400].reshape(720*3//2, 1280), cv2.COLOR_YUV2BGR_NV12) # for hardware decoding
            
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
            waypoint_folder = f'drone3_waypoint_{drone3_waypoint_no}_('+ task + ')'
            waypoint_path = os.path.join(Images_Path, waypoint_folder)
            if not os.path.exists(waypoint_path):
                os.mkdir(waypoint_path)
            else:
                print("Folder already exists for drone3 (update)")
                
            cv2.imwrite(os.path.join( waypoint_path, 'drone3Image' + str(drone3_waypoint_no)+'.png'), drone3_cropped_Image)
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
                # Check if the drone is in manual mode
                drone3_Image_Telemetry_data = w.getImageAndTelemetryData(3) # 2 refers to the drone number
                
                if((len(drone3_Image_Telemetry_data)) > 2000000):
                    drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone3_Telemetry_data = (bytearray(drone3_Image_Telemetry_data[1382408:]).decode())
                    
                drone3_elements = drone3_Telemetry_data.split(":")                 # Extract all elements from the string
                
                # check 16th element to see if the drone is in manual mode
                if float(drone3_elements[16]) == 0.0:
                    drone_3_incrementor = 1
                else:
                    drone_3_incrementor = incrementor
             
            if task == 'takeoff and waypoint':
                print("Takeoff and Mission Waypoint for drone3 completed")
            elif task == 'update_camera_parameters':
                print("Camera parameters updated for drone3")
            elif task == 'land':
                print("Land completed for drone3")
            elif task == 'emergency':
                print("Emergency Case")
            else:
                print("Invalid task")
            
            with lock:
                drone_3_thread_stop = True
                update_looking_drone_3 = True
            break
    
######################## Drone 4 Thread ############################
d4Image = []
d4Poses= []

def waypoint_tread_drone4(task, drone4_Latitude_List, drone4_Longitude_list, drone4_Altitude_list, drone4_Heading_list, drone4_Speed_list, Way4_threshold, camera_list, lengthOfStay_list, gimbalPitch_list, gimbalYaw_list, drone4_parameter_mode, drone4_rx_threshold, drone4_compass_correction, drone4_focal_length, drone4_focal_plane_pitch, drone4_focal_plane_roll, drone4_integration_window, drone4_minimum_pose_distance):
    
    number_of_waypoints_for_drone4 = len(drone4_Latitude_List)
    
    drone4_new_parameter_integral_go = 1 # for triggering integration while reaching (go) to the waypoint
    drone4_new_parameter_integral_update = 0
    
    global drone_4_incrementor, drone4_waypoint_no, camera, stop_waypoint_mission, break_while, drone_4_break_while, drone_4_thread_stop, update_looking_drone_4, active_clients
    
    with lock:
        drone_4_thread_stop = False
        update_looking_drone_4 = False
    
    incrementor = drone_4_incrementor
    
    previous_speed_list_drone4 = [drone4_Speed_list[0], *drone4_Speed_list]
    previous_heading_list_drone4 = [drone4_Heading_list[0], *drone4_Heading_list]
    previous_camera_list_drone4 = [camera_list[0], *camera_list]
    previous_lengthOfStay_list_drone4 = [lengthOfStay_list[0], *lengthOfStay_list]
    previous_gimbalPitch_list_drone4 = [gimbalPitch_list[0], *gimbalPitch_list]
    previous_gimbalYaw_list_drone4 = [gimbalYaw_list[0], *gimbalYaw_list]
    previous_drone4_rx_threshold = [drone4_rx_threshold[0], *drone4_rx_threshold]
    previous_drone4_compass_correction = [drone4_compass_correction[0], *drone4_compass_correction]
    previous_drone4_focal_length = [drone4_focal_length[0], *drone4_focal_length]
    previous_drone4_focal_plane_pitch = [drone4_focal_plane_pitch[0], *drone4_focal_plane_pitch]
    previous_drone4_focal_plane_roll = [drone4_focal_plane_roll[0], *drone4_focal_plane_roll]
    previous_drone4_integration_window = [drone4_integration_window[0], *drone4_integration_window]
    previous_drone4_minimum_pose_distance = [drone4_minimum_pose_distance[0], *drone4_minimum_pose_distance]
    
    iteration = 0
    
    while True:
            
        # Check if the drone is in manual mode
        
        drone4_Image_Telemetry_data = w.getImageAndTelemetryData(4) # 4 refers to the drone number
        
        if((len(drone4_Image_Telemetry_data)) > 2000000):
            drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[3110408:]).decode())
        else:
            drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[1382408:]).decode())
            
        drone4_elements = drone4_Telemetry_data.split(":")                 # Extract all elements from the string
        
        # check 16th element to see if the drone is in manual mode
        if float(drone4_elements[16]) == 0.0:
            with lock:
                drone_4_incrementor = 1
            break
        
        if task == 'takeoff and waypoint' or task == 'update_camera_parameters':
            with lock:
                drone4_waypoint_no = drone4_waypoint_no + 1       
            print(f"Mission Waypoint {drone4_waypoint_no} in progress for drone4 ...") 

            drone4_Latitude_go = drone4_Latitude_List[iteration]
            drone4_Longitude_go = drone4_Longitude_list[iteration]
            drone4_Altitude_go = drone4_Altitude_list[iteration]
            drone4_Heading_go = previous_heading_list_drone4[iteration]
            drone4_Speed_go = previous_speed_list_drone4[iteration]
            drone4_Camera_go = previous_camera_list_drone4[iteration]
            drone4_LengthOfStay_go = previous_lengthOfStay_list_drone4[iteration]
            drone4_GimbalPitch_go = previous_gimbalPitch_list_drone4[iteration]
            drone4_GimbalYaw_go = previous_gimbalYaw_list_drone4[iteration]
            drone4_Integration_Window_go = previous_drone4_integration_window[iteration]
            drone4_Minimum_Pose_Distance_go = previous_drone4_minimum_pose_distance[iteration]
            
            drone4_Rx_threshold = previous_drone4_rx_threshold[iteration]
            drone4_Compass_correction = previous_drone4_compass_correction[iteration]
            drone4_Focal_length = previous_drone4_focal_length[iteration]
            drone4_Focal_plane_pitch = previous_drone4_focal_plane_pitch[iteration]
            drone4_Focal_plane_roll = previous_drone4_focal_plane_roll[iteration]
            
            drone4_Latitude_update = drone4_Latitude_List[iteration]
            drone4_Longitude_update = drone4_Longitude_list[iteration]
            drone4_Altitude_update = drone4_Altitude_list[iteration]
            drone4_Heading_update = drone4_Heading_list[iteration]
            drone4_Speed_update = drone4_Speed_list[iteration]
            drone4_Camera_update = camera_list[iteration]
            drone4_LengthOfStay_update = lengthOfStay_list[iteration]
            drone4_GimbalPitch_update = gimbalPitch_list[iteration]
            drone4_GimbalYaw_update = gimbalYaw_list[iteration]
            drone4_Integration_Window_update = drone4_integration_window[iteration]
            drone4_Minimum_Pose_Distance_update = drone4_minimum_pose_distance[iteration]
            
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
            drone4_Integration_Window_go = drone4_integration_window[iteration]
            drone4_Minimum_Pose_Distance_go = drone4_minimum_pose_distance[iteration]
            
            drone4_Rx_threshold = previous_drone4_rx_threshold[iteration]
            drone4_Compass_correction = previous_drone4_compass_correction[iteration]
            drone4_Focal_length = previous_drone4_focal_length[iteration]
            drone4_Focal_plane_pitch = previous_drone4_focal_plane_pitch[iteration]
            drone4_Focal_plane_roll = previous_drone4_focal_plane_roll[iteration]
            
            drone4_Latitude_update = drone4_Latitude_List[iteration]
            drone4_Longitude_update = drone4_Longitude_list[iteration]
            drone4_Altitude_update = drone4_Altitude_list[iteration]
            drone4_Heading_update = drone4_Heading_list[iteration]
            drone4_Speed_update = drone4_Speed_list[iteration]
            drone4_Camera_update = camera_list[iteration]
            drone4_LengthOfStay_update = lengthOfStay_list[iteration]
            drone4_GimbalPitch_update = gimbalPitch_list[iteration]
            drone4_GimbalYaw_update = gimbalYaw_list[iteration]
            drone4_Integration_Window_update = drone4_integration_window[iteration]
            drone4_Minimum_Pose_Distance_update = drone4_minimum_pose_distance[iteration]
            
            iteration += 2
            
        waypointvalue4 = incrementor
        
        ################ for reaching the waypoint ################
        
        if stop_waypoint_mission:
            with lock:
                drone_4_incrementor = incrementor
            break
        
        if task == 'update_camera_parameters':
            pass
        else:
            
            print("waypointvalue4_drone4(go):",waypointvalue4)
            
            drone4_waypoint_data_reached = f"{drone4_Latitude_go}:{drone4_Longitude_go}:{drone4_Altitude_go}:{drone4_Heading_go}:{drone4_Speed_go}:{waypointvalue4}:{Way4_threshold}:{drone4_GimbalPitch_go}:{drone4_GimbalYaw_go}:{drone4_Camera_go}:{drone4_parameter_mode}:{drone4_Rx_threshold}:{drone4_Compass_correction}:{drone4_Focal_length}:{drone4_Focal_plane_pitch}:{drone4_Focal_plane_roll}: {drone4_new_parameter_integral_go}:{drone4_Integration_Window_go}:{drone4_Minimum_Pose_Distance_go}"
            
            drone4_send_data = w.sendWayPointData(drone4_waypoint_data_reached, 4)     # 4 refers to the drone number
            
            drone4_waypoint_data_sent = f"Lat: {drone4_Latitude_go}, Long: {drone4_Longitude_go}, Alt: {drone4_Altitude_go}, Heading: {drone4_Heading_go}, Speed: {drone4_Speed_go}, Waypoint: {waypointvalue4}, Threshold: {Way4_threshold}, Gimbal Pitch: {drone4_GimbalPitch_go}, Gimbal Yaw: {drone4_GimbalYaw_go}, Camera: {drone4_Camera_go}, Mode: {drone4_parameter_mode}, RX Threshold: {drone4_Rx_threshold}, Compass Correction: {drone4_Compass_correction}, Focal Length: {drone4_Focal_length}, Focal Plane Pitch: {drone4_Focal_plane_pitch}, Focal Plane Roll: {drone4_Focal_plane_roll}, Integral: {drone4_new_parameter_integral_go}, Integration Window: {drone4_Integration_Window_go}, Minimum Pose Distance: {drone4_Minimum_Pose_Distance_go}"
            
            # if debug:
            print("Data being Sent for drone4 (go):",drone4_waypoint_data_sent)
            
            # with lock:
            #     camera[3] = drone4_Camera_go
            
            ## Check if the drone has reached the waypoint, element (14) of the getImageAndTelemetryData string is set to 1. Extract the image and telemetry data when the condition is met. ## Every time the drone receive the next waypoints this element is set to zero again ion the drone app.
            
            while True:
                
                if break_while == True or drone_4_break_while == True:
                    break
                
                drone4_send_data = w.sendWayPointData(drone4_waypoint_data_reached, 4)
                
                drone4_Image_Telemetry_data = w.getImageAndTelemetryData(4)
                if((len(drone4_Image_Telemetry_data)) > 2000000):
                    drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[1382408:]).decode())
                #drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[1382408:]).decode())
                
                drone4_elements = drone4_Telemetry_data.split(":")                 # Extract all elements from the string
                drone4_Waypoint_sent = drone4_elements[15].split('.')[0]
                # print("drone4_Waypoint_sent_for_go:",drone4_Waypoint_sent)
                # check 16th element to see if the drone is in manual mode
                
                if debug:
                    print("drone4_elements[16]_1:",drone4_elements[16])
                
                if float(drone4_elements[16]) == 0.0:
                    with lock:
                        drone_4_incrementor = 1
                    break
                
                if (drone4_Waypoint_sent) == str(incrementor) or break_while == True or drone_4_break_while == True:
                    if debug: 
                        print("drone4 Waypoint data sent for go")
                        print ("go thread for drone4:", drone4_Waypoint_sent, incrementor)
                    break
            
            if break_while or drone_4_break_while:
                with lock:
                    drone_4_incrementor = incrementor + 1
                    drone_4_thread_stop = True
                break    
            
            while True:
                
                if break_while == True or drone_4_break_while == True:
                    break
                
                drone4_Image_Telemetry_data = w.getImageAndTelemetryData(4)
                if((len(drone4_Image_Telemetry_data)) > 2000000):
                    drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[1382408:]).decode())
                #drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[1382408:]).decode())
                
                drone4_elements = drone4_Telemetry_data.split(":")                 # Extract all elements from the string
                drone4_Waypoint_reached = drone4_elements[14]
                
                # print("drone4_Waypoint_reached:",drone4_Waypoint_reached)
                # print("incrementor:", incrementor)
                
                if debug:
                    print("drone4_elements[16]_2:",drone4_elements[16])
                
                if float(drone4_elements[16]) == 0.0:
                    with lock:
                        drone_4_incrementor = 1
                    break
                
                if drone4_Waypoint_reached == str(incrementor) or break_while == True or drone_4_break_while == True:
                    if debug:
                        print("drone4 Waypoint has been reached")
                        print ("go thread waypoint reached for drone4:", drone4_Waypoint_reached, incrementor)
                    break
                
            if break_while or drone_4_break_while:
                with lock:
                    drone_4_incrementor = incrementor + 1
                    drone_4_thread_stop = True
                break 
                
            # Call the telemetry data again
            
            drone4_Image_Telemetry_data = w.getImageAndTelemetryData(4)
            if ((len(drone4_Image_Telemetry_data)) > 2000000):
                drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[3110408:]).decode())
            else:
                drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[1382408:]).decode())
                
            drone_4_telemetry_elements = drone4_Telemetry_data.split(":")
            
            latitude = drone_4_telemetry_elements[0]
            longitude = drone_4_telemetry_elements[1]
            altitude = drone_4_telemetry_elements[2]
            heading = drone_4_telemetry_elements[3]
            gimbal_pitch = drone_4_telemetry_elements[4]
            gimbal_yaw = drone_4_telemetry_elements[6]
            
            if debug:
                reached_data = f"Lat_Reached: {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
                print("Data Being Reached for drone4 (go) --->", reached_data)
                
                print("drone4_Waypointdata (go):", drone4_Telemetry_data)
                
            if drone4_LengthOfStay_go > 0:
                time.sleep(drone4_LengthOfStay_go)
                
            incrementor += 1
            
        ################ updating the waypoint ################
        
        if stop_waypoint_mission:
            with lock:
                drone_4_incrementor = incrementor
            break
        
        waypointvalue4_update = incrementor
        
        print("waypointvalue4_drone4(update):",waypointvalue4_update)
        
        drone4_waypoint_data = f"{drone4_Latitude_update}:{drone4_Longitude_update}:{drone4_Altitude_update}:{drone4_Heading_update}:{drone4_Speed_update}:{waypointvalue4_update}:{Way4_threshold}:{drone4_GimbalPitch_update}:{drone4_GimbalYaw_update}:{drone4_Camera_update}:{drone4_parameter_mode}:{drone4_Rx_threshold}:{drone4_Compass_correction}:{drone4_Focal_length}:{drone4_Focal_plane_pitch}:{drone4_Focal_plane_roll}:{drone4_new_parameter_integral_update}:{drone4_Integration_Window_update}:{drone4_Minimum_Pose_Distance_update}"
        
        drone4_send_data = w.sendWayPointData(drone4_waypoint_data, 4)     # 4 refers to the drone number
        
        drone4_waypoint_data_sent = f"Lat: {drone4_Latitude_update}, Long: {drone4_Longitude_update}, Alt: {drone4_Altitude_update}, Heading: {drone4_Heading_update}, Speed: {drone4_Speed_update}, Waypoint: {waypointvalue4_update}, Threshold: {Way4_threshold}, Gimbal Pitch: {drone4_GimbalPitch_update}, Gimbal Yaw: {drone4_GimbalYaw_update}, Camera: {drone4_Camera_update}, Mode: {drone4_parameter_mode}, RX Threshold: {drone4_Rx_threshold}, Compass Correction: {drone4_Compass_correction}, Focal Length: {drone4_Focal_length}, Focal Plane Pitch: {drone4_Focal_plane_pitch}, Focal Plane Roll: {drone4_Focal_plane_roll}, Integral: {drone4_new_parameter_integral_update}, Integration Window: {drone4_Integration_Window_update}, Minimum Pose Distance: {drone4_Minimum_Pose_Distance_update}"
        
        # if debug:
        print("Data Being Sent for drone4 (update) :",drone4_waypoint_data_sent)
        
        while True:
            
            if break_while == True or drone_4_break_while == True:
                break
            
            drone4_send_data = w.sendWayPointData(drone4_waypoint_data, 4) 
            drone4_Image_Telemetry_data = w.getImageAndTelemetryData(4)
            if((len(drone4_Image_Telemetry_data)) > 2000000):
                drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[3110408:]).decode())
            else:
                drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[1382408:]).decode())
            #drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[1382408:]).decode())
            
            drone4_elements = drone4_Telemetry_data.split(":")                 # Extract all elements from the string
            drone4_Waypoint_sent = drone4_elements[15].split('.')[0]
            # print("drone4_Waypoint_sent:",drone4_Waypoint_sent)
            
            if debug:
                print("drone4_elements[16]_3:",drone4_elements[16])
            
            if float(drone4_elements[16]) == 0.0:
                with lock:
                    drone_4_incrementor = 1
                break
            
            if (drone4_Waypoint_sent) == str(incrementor) or break_while == True or drone_4_break_while == True:
                if debug: 
                    print("drone4 Waypoint data sent")
                    print ("run thread for drone4:", drone4_Waypoint_sent, incrementor)
                break
        
        if break_while or drone_4_break_while:
            with lock:
                drone_4_incrementor = incrementor + 1
                drone_4_thread_stop = True
            break  
        
        while True:
            
            if break_while == True or drone_4_break_while == True:
                break
            
            drone4_Image_Telemetry_data = w.getImageAndTelemetryData(4)
            if((len(drone4_Image_Telemetry_data)) > 2000000):
                drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[3110408:]).decode())
            else:
                drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[1382408:]).decode())
            #drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[1382408:]).decode())
            
            drone4_elements = drone4_Telemetry_data.split(":")                 # Extract all elements from the string
            drone4_Waypoint_reached = drone4_elements[14]
            
            # print("drone4_Waypoint_reached:",drone4_Waypoint_reached)
            # print("incrementor:", incrementor)
            
            if debug:
                print("drone4_elements[16]_4:",drone4_elements[16])
            
            if float(drone4_elements[16]) == 0.0:
                with lock:
                    drone_4_incrementor = 1
                break
            
            if drone4_Waypoint_reached == str(incrementor) or break_while == True or drone_4_break_while == True:
                if debug:
                    print("drone4 Waypoint has been reached")
                    print ("run thread waypoint reached:", drone4_Waypoint_reached, incrementor)
                break
            
        if break_while or drone_4_break_while:
            with lock:
                drone_4_incrementor = incrementor + 1
                drone_4_thread_stop = True    
            break 
        
        feedback_data_update_4 = {
                'drone_id': 4,
                'heading': drone4_Heading_update,
                'gimbalPitch': drone4_GimbalPitch_update,
                'gimbalYaw': drone4_GimbalYaw_update
            }
        if feedback_data_update_4['heading'] != 'N/A':
            if float(feedback_data_update_4['heading']) < 0.0:
                feedback_data_update_4['heading'] = 360.0 + float(feedback_data_update_4['heading'])
                feedback_data_update_4['heading'] = str(feedback_data_update_4['heading'])
                
        publish_feedback(active_clients[24], feedback_data_update_4, 4) # publish the feedback data to the client  # 24 refers to the client number, 4 refers to the drone number
            
        # Hold the drone at the waypoint for a specified length of time
        if drone4_LengthOfStay_update > 0:
            time.sleep(drone4_LengthOfStay_update)
            
            if debug:
                print("drone4_Waypointdata_before_holding:", drone4_Telemetry_data)
            
                print(f'drone4 is waiting  for {drone4_LengthOfStay_update} sn before taking the image and saving the telemetry data')  
                
        # Call the telemetry data again
        drone4_Image_Telemetry_data = w.getImageAndTelemetryData(4)
        if((len(drone4_Image_Telemetry_data)) > 2000000):
            drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[3110408:]).decode())
        else:
            drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[1382408:]).decode())
            
        drone_4_telemetry_elements = drone4_Telemetry_data.split(":")
        
        latitude = drone_4_telemetry_elements[0]
        longitude = drone_4_telemetry_elements[1]
        altitude = drone_4_telemetry_elements[2]
        heading = drone_4_telemetry_elements[3]
        gimbal_pitch = drone_4_telemetry_elements[4]
        gimbal_yaw = drone_4_telemetry_elements[6]
        
        if debug:
            reached_data = f"Lat_Reached {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for Updating Parameter for drone4 --->",reached_data)
            
            print("drone4_Waypointdata (update):", drone4_Telemetry_data)
            
            # Save the telemetry data to a text file inside the results folder
            file_path = os.path.join(Download_Location, 'telemetry4.txt')
            with open(file_path, 'a') as file:
                file.write(drone4_Telemetry_data + '\n')
                
        ## Covert YUV raw data to rgb image and save   ##
        
        if((len(drone4_Image_Telemetry_data)) > 2000000):
            crop_size = 1080
            if decoding == 'software':
                drone4_Image = cv2.cvtColor(drone4_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV420p2RGB)   # for software decoding
                
            elif decoding == 'hardware':
                drone4_Image = cv2.cvtColor(drone4_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV2BGR_NV12)
                
        else:
            
            crop_size = 720
            if decoding == 'software':
                drone4_Image = cv2.cvtColor(drone4_Image_Telemetry_data[0:1382400].reshape(720*3//2, 1280), cv2.COLOR_YUV420p2RGB)
                
            elif decoding == 'hardware':
                drone4_Image = cv2.cvtColor(drone4_Image_Telemetry_data[0:1382400].reshape(720*3//2, 1280), cv2.COLOR_YUV2BGR_NV12)
                
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
            waypoint_folder = f'drone4_waypoint_{drone4_waypoint_no}_('+ task + ')'
            waypoint_path = os.path.join(Images_Path, waypoint_folder)
            if not os.path.exists(waypoint_path):
                os.mkdir(waypoint_path)
            else:
                print("Folder already exists for drone4 (update)")
                
            cv2.imwrite(os.path.join( waypoint_path, 'drone4Image' + str(drone4_waypoint_no)+'.png'), drone4_cropped_Image)
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
                # Check if the drone is in manual mode
                drone4_Image_Telemetry_data = w.getImageAndTelemetryData(4)
                if((len(drone4_Image_Telemetry_data)) > 2000000):
                    drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone4_Telemetry_data = (bytearray(drone4_Image_Telemetry_data[1382408:]).decode())
                    
                drone4_elements = drone4_Telemetry_data.split(":")                 # Extract all elements from the string
                
                # check 16th element to see if the drone is in manual mode
                
                if float(drone4_elements[16]) == 0.0:
                    drone_4_incrementor = 1
                else:
                    drone_4_incrementor = incrementor
                    
            if task == 'takeoff and waypoint':
                print("Takeoff and Mission Waypoint for drone4 completed")
            elif task == 'update_camera_parameters':
                print("Camera parameters updated for drone4")
            elif task == 'land':
                print("Land completed for drone4")
            elif task == 'emergency':
                print("Emergency Case")
            else:
                print("Invalid task")
            
            with lock:
                drone_4_thread_stop = True
                update_looking_drone_4 = True
                
            break
        
######################## Drone 5 Thread ############################
d5Image = []
d5Poses= []

def waypoint_tread_drone5(task, drone5_Latitude_List, drone5_Longitude_list, drone5_Altitude_list, drone5_Heading_list, drone5_Speed_list, Way5_threshold, camera_list, lengthOfStay_list, gimbalPitch_list, gimbalYaw_list, drone5_parameter_mode, drone5_rx_threshold, drone5_compass_correction, drone5_focal_length, drone5_focal_plane_pitch, drone5_focal_plane_roll, drone5_integration_window, drone5_minimum_pose_distance):
    
    number_of_waypoints_for_drone5 = len(drone5_Latitude_List)
    
    drone5_new_parameter_integral_go = 1 # for triggering integration while reaching (go) to the waypoint
    drone5_new_parameter_integral_update = 0
    
    global drone_5_incrementor, drone5_waypoint_no, camera, stop_waypoint_mission, break_while, drone_5_break_while, drone_5_thread_stop, update_looking_drone_5, active_clients
    
    with lock:
        drone_5_thread_stop = False
        update_looking_drone_5 = False
    
    incrementor = drone_5_incrementor
    
    previous_speed_list_drone5 = [drone5_Speed_list[0], *drone5_Speed_list]
    previous_heading_list_drone5 = [drone5_Heading_list[0], *drone5_Heading_list]
    previous_camera_list_drone5 = [camera_list[0], *camera_list]
    previous_lengthOfStay_list_drone5 = [lengthOfStay_list[0], *lengthOfStay_list]
    previous_gimbalPitch_list_drone5 = [gimbalPitch_list[0], *gimbalPitch_list]
    previous_gimbalYaw_list_drone5 = [gimbalYaw_list[0], *gimbalYaw_list]
    previous_drone5_rx_threshold = [drone5_rx_threshold[0], *drone5_rx_threshold]
    previous_drone5_compass_correction = [drone5_compass_correction[0], *drone5_compass_correction]
    previous_drone5_focal_length = [drone5_focal_length[0], *drone5_focal_length]
    previous_drone5_focal_plane_pitch = [drone5_focal_plane_pitch[0], *drone5_focal_plane_pitch]
    previous_drone5_focal_plane_roll = [drone5_focal_plane_roll[0], *drone5_focal_plane_roll]
    previous_drone5_integration_window = [drone5_integration_window[0], *drone5_integration_window]
    previous_drone5_minimum_pose_distance = [drone5_minimum_pose_distance[0], *drone5_minimum_pose_distance]
    
    iteration = 0
    
    while True:
  
        # Check if the drone is in manual mode
        drone5_Image_Telemetry_data = w.getImageAndTelemetryData(5) # 5 refers to the drone number
        
        if((len(drone5_Image_Telemetry_data)) > 2000000):
            drone5_Telemetry_data = (bytearray(drone5_Image_Telemetry_data[3110408:]).decode())
        else:
            drone5_Telemetry_data = (bytearray(drone5_Image_Telemetry_data[1382408:]).decode())
            
        drone5_elements = drone5_Telemetry_data.split(":")  # Extract all elements from the string
        
        # Check 16th element to see if the drone is in manual mode
        if float(drone5_elements[16]) == 0.0:
            with lock:
                drone_5_incrementor = 1
            break
        
        if task == 'takeoff and waypoint' or task == 'update_camera_parameters':
            with lock:
                drone5_waypoint_no = drone5_waypoint_no + 1       
            print(f"Mission Waypoint {drone5_waypoint_no} in progress for drone5 ...") 

            drone5_Latitude_go = drone5_Latitude_List[iteration]
            drone5_Longitude_go = drone5_Longitude_list[iteration]
            drone5_Altitude_go = drone5_Altitude_list[iteration]
            drone5_Heading_go = previous_heading_list_drone5[iteration]
            drone5_Speed_go = previous_speed_list_drone5[iteration]
            drone5_Camera_go = previous_camera_list_drone5[iteration]
            drone5_LengthOfStay_go = previous_lengthOfStay_list_drone5[iteration]
            drone5_GimbalPitch_go = previous_gimbalPitch_list_drone5[iteration]
            drone5_GimbalYaw_go = previous_gimbalYaw_list_drone5[iteration]
            drone5_Integration_Window_go = previous_drone5_integration_window[iteration]
            drone5_Minimum_Pose_Distance_go = previous_drone5_minimum_pose_distance[iteration]
            
            drone5_Rx_threshold = previous_drone5_rx_threshold[iteration]
            drone5_Compass_correction = previous_drone5_compass_correction[iteration]
            drone5_Focal_length = previous_drone5_focal_length[iteration]
            drone5_Focal_plane_pitch = previous_drone5_focal_plane_pitch[iteration]
            drone5_Focal_plane_roll = previous_drone5_focal_plane_roll[iteration]
            
            drone5_Latitude_update = drone5_Latitude_List[iteration]
            drone5_Longitude_update = drone5_Longitude_list[iteration]
            drone5_Altitude_update = drone5_Altitude_list[iteration]
            drone5_Heading_update = drone5_Heading_list[iteration]
            drone5_Speed_update = drone5_Speed_list[iteration]
            drone5_Camera_update = camera_list[iteration]
            drone5_LengthOfStay_update = lengthOfStay_list[iteration]
            drone5_GimbalPitch_update = gimbalPitch_list[iteration]
            drone5_GimbalYaw_update = gimbalYaw_list[iteration]
            drone5_Integration_Window_update = drone5_integration_window[iteration]
            drone5_Minimum_Pose_Distance_update = drone5_minimum_pose_distance[iteration]
            
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
            drone5_Integration_Window_go = drone5_integration_window[iteration]
            drone5_Minimum_Pose_Distance_go = drone5_minimum_pose_distance[iteration]
            
            drone5_Rx_threshold = previous_drone5_rx_threshold[iteration]
            drone5_Compass_correction = previous_drone5_compass_correction[iteration]
            drone5_Focal_length = previous_drone5_focal_length[iteration]
            drone5_Focal_plane_pitch = previous_drone5_focal_plane_pitch[iteration]
            drone5_Focal_plane_roll = previous_drone5_focal_plane_roll[iteration]
            
            drone5_Latitude_update = drone5_Latitude_List[iteration]
            drone5_Longitude_update = drone5_Longitude_list[iteration]
            drone5_Altitude_update = drone5_Altitude_list[iteration]
            drone5_Heading_update = drone5_Heading_list[iteration]
            drone5_Speed_update = drone5_Speed_list[iteration]
            drone5_Camera_update = camera_list[iteration]
            drone5_LengthOfStay_update = lengthOfStay_list[iteration]
            drone5_GimbalPitch_update = gimbalPitch_list[iteration]
            drone5_GimbalYaw_update = gimbalYaw_list[iteration]
            drone5_Integration_Window_update = drone5_integration_window[iteration]
            drone5_Minimum_Pose_Distance_update = drone5_minimum_pose_distance[iteration]
            
            iteration += 2
            
        waypointvalue5 = incrementor
        
        ################ for reaching the waypoint ################
        
        if stop_waypoint_mission:
            with lock:
                drone_5_incrementor = incrementor
            break
        
        if task == 'update_camera_parameters':
            pass
        else:
            
            print("waypointvalue5_drone5(go):",waypointvalue5)
            
            drone5_waypoint_data_reached = f"{drone5_Latitude_go}:{drone5_Longitude_go}:{drone5_Altitude_go}:{drone5_Heading_go}:{drone5_Speed_go}:{waypointvalue5}:{Way5_threshold}:{drone5_GimbalPitch_go}:{drone5_GimbalYaw_go}:{drone5_Camera_go}:{drone5_parameter_mode}:{drone5_Rx_threshold}:{drone5_Compass_correction}:{drone5_Focal_length}:{drone5_Focal_plane_pitch}:{drone5_Focal_plane_roll}: {drone5_new_parameter_integral_go}:{drone5_Integration_Window_go}:{drone5_Minimum_Pose_Distance_go}"
            
            drone5_send_data = w.sendWayPointData(drone5_waypoint_data_reached, 5)     # 5 refers to the drone number
            
            drone5_waypoint_data_sent = f"Lat: {drone5_Latitude_go}, Long: {drone5_Longitude_go}, Alt: {drone5_Altitude_go}, Heading: {drone5_Heading_go}, Speed: {drone5_Speed_go}, Waypoint: {waypointvalue5}, Threshold: {Way5_threshold}, Gimbal Pitch: {drone5_GimbalPitch_go}, Gimbal Yaw: {drone5_GimbalYaw_go}, Camera: {drone5_Camera_go}, Mode: {drone5_parameter_mode}, RX Threshold: {drone5_Rx_threshold}, Compass Correction: {drone5_Compass_correction}, Focal Length: {drone5_Focal_length}, Focal Plane Pitch: {drone5_Focal_plane_pitch}, Focal Plane Roll: {drone5_Focal_plane_roll}, Integral: {drone5_new_parameter_integral_go}, Integration Window: {drone5_Integration_Window_go}, Minimum Pose Distance: {drone5_Minimum_Pose_Distance_go}"
            
            print("Data being Sent for drone5 (go):",drone5_waypoint_data_sent)
            
            while True:
                
                if break_while == True or drone_5_break_while == True:
                    break
                
                drone5_send_data = w.sendWayPointData(drone5_waypoint_data_reached, 5)
                drone5_Image_Telemetry_data = w.getImageAndTelemetryData(5)
                if((len(drone5_Image_Telemetry_data)) > 2000000):
                    drone5_Telemetry_data = (bytearray(drone5_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone5_Telemetry_data = (bytearray(drone5_Image_Telemetry_data[1382408:]).decode())
                
                drone5_elements = drone5_Telemetry_data.split(":")
                drone5_Waypoint_sent = drone5_elements[15].split('.')[0]
                
                if debug:
                    print("drone5_elements[16]_1:",drone5_elements[16])
                
                if float(drone5_elements[16]) == 0.0:
                    with lock:
                        drone_5_incrementor = 1
                    break
                
                if (drone5_Waypoint_sent) == str(incrementor) or break_while == True or drone_5_break_while == True:
                    if debug: 
                        print("drone5 Waypoint data sent for go")
                        print ("go thread for drone5:", drone5_Waypoint_sent, incrementor)
                    break
                    
            if break_while == True or drone_5_break_while == True:
                with lock:
                    drone_5_incrementor = incrementor + 1
                    drone_5_thread_stop = True
                break
            
            while True:
                
                if break_while == True or drone_5_break_while == True:
                    break
                
                drone5_Image_Telemetry_data = w.getImageAndTelemetryData(5)
                if((len(drone5_Image_Telemetry_data)) > 2000000):
                    drone5_Telemetry_data = (bytearray(drone5_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone5_Telemetry_data = (bytearray(drone5_Image_Telemetry_data[1382408:]).decode())
                
                drone5_elements = drone5_Telemetry_data.split(":")
                drone5_Waypoint_reached = drone5_elements[14]
                
                if debug:
                    print("drone5_elements[16]_2:",drone5_elements[16])
                
                if float(drone5_elements[16]) == 0.0:
                    with lock:
                        drone_5_incrementor = 1
                    break
                
                if drone5_Waypoint_reached == str(incrementor) or break_while == True or drone_5_break_while == True:
                    if debug:
                        print("drone5 Waypoint has been reached")
                        print ("go thread waypoint reached for drone5:", drone5_Waypoint_reached, incrementor)
                    break
            
            if break_while == True or drone_5_break_while == True:
                with lock:
                    drone_5_incrementor = incrementor + 1
                    drone_5_thread_stop = True
                break
                
            # Call the telemetry data again
            drone5_Image_Telemetry_data = w.getImageAndTelemetryData(5)
            if ((len(drone5_Image_Telemetry_data)) > 2000000):
                drone5_Telemetry_data = (bytearray(drone5_Image_Telemetry_data[3110408:]).decode())
            else:
                drone5_Telemetry_data = (bytearray(drone5_Image_Telemetry_data[1382408:]).decode())
                
            drone_5_telemetry_elements = drone5_Telemetry_data.split(":")
            
            latitude = drone_5_telemetry_elements[0]
            longitude = drone_5_telemetry_elements[1]
            altitude = drone_5_telemetry_elements[2]
            heading = drone_5_telemetry_elements[3]
            gimbal_pitch = drone_5_telemetry_elements[4]
            gimbal_yaw = drone_5_telemetry_elements[6]
            
            if debug:
                reached_data = f"Lat_Reached: {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
                print("Data Being Reached for drone5 (go) --->", reached_data)
                
                print("drone5_Waypointdata (go):", drone5_Telemetry_data)
                
            if drone5_LengthOfStay_go > 0:
                time.sleep(drone5_LengthOfStay_go)
                
            incrementor += 1
            
        ################ updating the waypoint ################
        
        waypointvalue5_update = incrementor
        
        print("waypointvalue5_drone5(update):",waypointvalue5_update)
        
        drone5_waypoint_data = f"{drone5_Latitude_update}:{drone5_Longitude_update}:{drone5_Altitude_update}:{drone5_Heading_update}:{drone5_Speed_update}:{waypointvalue5_update}:{Way5_threshold}:{drone5_GimbalPitch_update}:{drone5_GimbalYaw_update}:{drone5_Camera_update}:{drone5_parameter_mode}:{drone5_Rx_threshold}:{drone5_Compass_correction}:{drone5_Focal_length}:{drone5_Focal_plane_pitch}:{drone5_Focal_plane_roll}:{drone5_new_parameter_integral_update}:{drone5_Integration_Window_update}:{drone5_Minimum_Pose_Distance_update}"
        
        drone5_send_data = w.sendWayPointData(drone5_waypoint_data, 5)
        
        drone5_waypoint_data_sent = f"Lat: {drone5_Latitude_update}, Long: {drone5_Longitude_update}, Alt: {drone5_Altitude_update}, Heading: {drone5_Heading_update}, Speed: {drone5_Speed_update}, Waypoint: {waypointvalue5_update}, Threshold: {Way5_threshold}, Gimbal Pitch: {drone5_GimbalPitch_update}, Gimbal Yaw: {drone5_GimbalYaw_update}, Camera: {drone5_Camera_update}, Mode: {drone5_parameter_mode}, RX Threshold: {drone5_Rx_threshold}, Compass Correction: {drone5_Compass_correction}, Focal Length: {drone5_Focal_length}, Focal Plane Pitch: {drone5_Focal_plane_pitch}, Focal Plane Roll: {drone5_Focal_plane_roll}, Integral: {drone5_new_parameter_integral_update}, Integration Window: {drone5_Integration_Window_update}, Minimum Pose Distance: {drone5_Minimum_Pose_Distance_update}"
        
        print("Data Being Sent for drone5 (update) :",drone5_waypoint_data_sent)
        
        while True:
            
            if break_while == True or drone_5_break_while == True:
                break
            
            drone5_send_data = w.sendWayPointData(drone5_waypoint_data, 5) 
            drone5_Image_Telemetry_data = w.getImageAndTelemetryData(5)
            if((len(drone5_Image_Telemetry_data)) > 2000000):
                drone5_Telemetry_data = (bytearray(drone5_Image_Telemetry_data[3110408:]).decode())
            else:
                drone5_Telemetry_data = (bytearray(drone5_Image_Telemetry_data[1382408:]).decode())
                
            drone5_elements = drone5_Telemetry_data.split(":")
            drone5_Waypoint_sent = drone5_elements[15].split('.')[0]
            
            if debug:
                print("drone5_elements[16]_3:",drone5_elements[16])
            
            if float(drone5_elements[16]) == 0.0:
                with lock:
                    drone_5_incrementor = 1
                break
            
            if (drone5_Waypoint_sent) == str(incrementor) or break_while == True or drone_5_break_while == True:
                if debug: 
                    print("drone5 Waypoint data sent")
                    print ("run thread for drone5:", drone5_Waypoint_sent, incrementor)
                break
            
        if break_while == True or drone_5_break_while == True:
            with lock:
                drone_5_incrementor = incrementor + 1
                drone_5_thread_stop = True
            break
            
        while True:
            if break_while == True or drone_5_break_while == True:
                break
            
            drone5_Image_Telemetry_data = w.getImageAndTelemetryData(5)
            if((len(drone5_Image_Telemetry_data)) > 2000000):
                drone5_Telemetry_data = (bytearray(drone5_Image_Telemetry_data[3110408:]).decode())
            else:
                drone5_Telemetry_data = (bytearray(drone5_Image_Telemetry_data[1382408:]).decode())
                
            drone5_elements = drone5_Telemetry_data.split(":")
            drone5_Waypoint_reached = drone5_elements[14]
            
            if debug:
                print("drone5_elements[16]_4:",drone5_elements[16])
            
            if float(drone5_elements[16]) == 0.0:
                with lock:
                    drone_5_incrementor = 1
                break
            
            if drone5_Waypoint_reached == str(incrementor) or break_while == True:
                if debug:
                    print("drone5 Waypoint has been reached")
                    print ("run thread waypoint reached:", drone5_Waypoint_reached, incrementor)
                break
        
        if break_while == True or drone_5_break_while == True:
            with lock:
                drone_5_incrementor = incrementor + 1
                drone_5_thread_stop = True
            break
        
        feedback_data_update_5 = {
                'drone_id': 5,
                'heading': drone5_Heading_update,
                'gimbalPitch': drone5_GimbalPitch_update,
                'gimbalYaw': drone5_GimbalYaw_update
            }
        
        if feedback_data_update_5['heading'] != 'N/A':
            if float(feedback_data_update_5['heading']) < 0.0:
                feedback_data_update_5['heading'] = 360.0 + float(feedback_data_update_5['heading'])
                feedback_data_update_5['heading'] = str(feedback_data_update_5['heading'])
                
        publish_feedback(active_clients[25], feedback_data_update_5, 5) # publish the feedback data to the client  # 25 refers to the client number, 5 refers to the drone number
            
        # Hold the drone at the waypoint for a specified length of time
        if drone5_LengthOfStay_update > 0:
            time.sleep(drone5_LengthOfStay_update)
            
            if debug:
                print("drone5_Waypointdata_before_holding:", drone5_Telemetry_data)
                print(f'drone5 is waiting  for {drone5_LengthOfStay_update} sn before taking the image and saving the telemetry data')  
                
        # Call the telemetry data again
        drone5_Image_Telemetry_data = w.getImageAndTelemetryData(5)
        if((len(drone5_Image_Telemetry_data)) > 2000000):
            drone5_Telemetry_data = (bytearray(drone5_Image_Telemetry_data[3110408:]).decode())
        else:
            drone5_Telemetry_data = (bytearray(drone5_Image_Telemetry_data[1382408:]).decode())
            
        drone_5_telemetry_elements = drone5_Telemetry_data.split(":")
        
        latitude = drone_5_telemetry_elements[0]
        longitude = drone_5_telemetry_elements[1]
        altitude = drone_5_telemetry_elements[2]
        heading = drone_5_telemetry_elements[3]
        gimbal_pitch = drone_5_telemetry_elements[4]
        gimbal_yaw = drone_5_telemetry_elements[6]
        
        if debug:
            reached_data = f"Lat_Reached {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for Updating Parameter for drone5 --->",reached_data)
            
            print("drone5_Waypointdata (update):", drone5_Telemetry_data)
            
            # Save the telemetry data to a text file inside the results folder
            file_path = os.path.join(Download_Location, 'telemetry5.txt')
            with open(file_path, 'a') as file:
                file.write(drone5_Telemetry_data + '\n')
                
        ## Covert YUV raw data to rgb image and save   ##
        
        if((len(drone5_Image_Telemetry_data)) > 2000000):
            crop_size = 1080
            if decoding == 'software':
                drone5_Image = cv2.cvtColor(drone5_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV420p2RGB)   # for software decoding
                
            elif decoding == 'hardware':
                drone5_Image = cv2.cvtColor(drone5_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV2BGR_NV12)
                
        else:   
            crop_size = 720
            if decoding == 'software':
                drone5_Image = cv2.cvtColor(drone5_Image_Telemetry_data[0:1382400].reshape(720*3//2, 1280), cv2.COLOR_YUV420p2RGB)
                
            elif decoding == 'hardware':
                drone5_Image = cv2.cvtColor(drone5_Image_Telemetry_data[0:1382400].reshape(720*3//2, 1280), cv2.COLOR_YUV2BGR_NV12)
                
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
            waypoint_folder = f'drone5_waypoint_{drone5_waypoint_no}_('+ task + ')'
            waypoint_path = os.path.join(Images_Path, waypoint_folder)
            if not os.path.exists(waypoint_path):
                os.mkdir(waypoint_path)
            else:
                print("Folder already exists for drone5 (update)")
                
            cv2.imwrite(os.path.join( waypoint_path, 'drone5Image' + str(drone5_waypoint_no)+'.png'), drone5_cropped_Image)
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
                # Check if the drone is in manual mode
                drone5_Image_Telemetry_data = w.getImageAndTelemetryData(5)
                if((len(drone5_Image_Telemetry_data)) > 2000000):
                    drone5_Telemetry_data = (bytearray(drone5_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone5_Telemetry_data = (bytearray(drone5_Image_Telemetry_data[1382408:]).decode())
                    
                drone5_elements = drone5_Telemetry_data.split(":")
                
                # check 16th element to see if the drone is in manual mode
                
                if float(drone5_elements[16]) == 0.0:
                    drone_5_incrementor = 1
                else:
                    drone_5_incrementor = incrementor
                    
            if task == 'takeoff and waypoint':
                print("Takeoff and Mission Waypoint for drone5 completed")
            elif task == 'update_camera_parameters':
                print("Camera parameters updated for drone5")
            elif task == 'land':
                print("Land completed for drone5")
            elif task == 'emergency':
                print("Emergency Case")
            else:
                print("Invalid task")
            
            with lock:
                drone_5_thread_stop = True
                update_looking_drone_5 = True
                
            break

######################## Drone 6 Thread ############################
d6Image = []
d6Poses= []

def waypoint_tread_drone6(task, drone6_Latitude_List, drone6_Longitude_list, drone6_Altitude_list, drone6_Heading_list, drone6_Speed_list, Way6_threshold, camera_list, lengthOfStay_list, gimbalPitch_list, gimbalYaw_list, drone6_parameter_mode, drone6_rx_threshold, drone6_compass_correction, drone6_focal_length, drone6_focal_plane_pitch, drone6_focal_plane_roll, drone6_integration_window, drone6_minimum_pose_distance):
    
    number_of_waypoints_for_drone6 = len(drone6_Latitude_List)
    
    drone6_new_parameter_integral_go = 1 # for triggering integration while reaching (go) to the waypoint
    drone6_new_parameter_integral_update = 0
    
    global drone_6_incrementor, drone6_waypoint_no, camera, stop_waypoint_mission, break_while, drone_6_break_while, drone_6_thread_stop, update_looking_drone_6, active_clients
    
    with lock:
        drone_6_thread_stop = False
        update_looking_drone_6 = False
    
    incrementor = drone_6_incrementor
    
    previous_speed_list_drone6 = [drone6_Speed_list[0], *drone6_Speed_list]
    previous_heading_list_drone6 = [drone6_Heading_list[0], *drone6_Heading_list]
    previous_camera_list_drone6 = [camera_list[0], *camera_list]
    previous_lengthOfStay_list_drone6 = [lengthOfStay_list[0], *lengthOfStay_list]
    previous_gimbalPitch_list_drone6 = [gimbalPitch_list[0], *gimbalPitch_list]
    previous_gimbalYaw_list_drone6 = [gimbalYaw_list[0], *gimbalYaw_list]
    previous_drone6_rx_threshold = [drone6_rx_threshold[0], *drone6_rx_threshold]
    previous_drone6_compass_correction = [drone6_compass_correction[0], *drone6_compass_correction]
    previous_drone6_focal_length = [drone6_focal_length[0], *drone6_focal_length]
    previous_drone6_focal_plane_pitch = [drone6_focal_plane_pitch[0], *drone6_focal_plane_pitch]
    previous_drone6_focal_plane_roll = [drone6_focal_plane_roll[0], *drone6_focal_plane_roll]
    previous_drone6_integration_window = [drone6_integration_window[0], *drone6_integration_window]
    previous_drone6_minimum_pose_distance = [drone6_minimum_pose_distance[0], *drone6_minimum_pose_distance]
    
    iteration = 0
    
    while True:
        
        # Check if the drone is in manual mode
        drone6_Image_Telemetry_data = w.getImageAndTelemetryData(6) # 6 refers to the drone number
        
        if((len(drone6_Image_Telemetry_data)) > 2000000):
            drone6_Telemetry_data = (bytearray(drone6_Image_Telemetry_data[3110408:]).decode())
        else:
            drone6_Telemetry_data = (bytearray(drone6_Image_Telemetry_data[1382408:]).decode())
            
        drone6_elements = drone6_Telemetry_data.split(":")  # Extract all elements from the string
        
        # Check 16th element to see if the drone is in manual mode
        if float(drone6_elements[16]) == 0.0:
            with lock:
                drone_6_incrementor = 1
            break
        
        if task == 'takeoff and waypoint' or task == 'update_camera_parameters':
            with lock:
                drone6_waypoint_no = drone6_waypoint_no + 1       
            print(f"Mission Waypoint {drone6_waypoint_no} in progress for drone6 ...") 

            drone6_Latitude_go = drone6_Latitude_List[iteration]
            drone6_Longitude_go = drone6_Longitude_list[iteration]
            drone6_Altitude_go = drone6_Altitude_list[iteration]
            drone6_Heading_go = previous_heading_list_drone6[iteration]
            drone6_Speed_go = previous_speed_list_drone6[iteration]
            drone6_Camera_go = previous_camera_list_drone6[iteration]
            drone6_LengthOfStay_go = previous_lengthOfStay_list_drone6[iteration]
            drone6_GimbalPitch_go = previous_gimbalPitch_list_drone6[iteration]
            drone6_GimbalYaw_go = previous_gimbalYaw_list_drone6[iteration]
            drone6_Integration_Window_go = previous_drone6_integration_window[iteration]
            drone6_Minimum_Pose_Distance_go = previous_drone6_minimum_pose_distance[iteration]
            
            drone6_Rx_threshold = previous_drone6_rx_threshold[iteration]
            drone6_Compass_correction = previous_drone6_compass_correction[iteration]
            drone6_Focal_length = previous_drone6_focal_length[iteration]
            drone6_Focal_plane_pitch = previous_drone6_focal_plane_pitch[iteration]
            drone6_Focal_plane_roll = previous_drone6_focal_plane_roll[iteration]
            
            drone6_Latitude_update = drone6_Latitude_List[iteration]
            drone6_Longitude_update = drone6_Longitude_list[iteration]
            drone6_Altitude_update = drone6_Altitude_list[iteration]
            drone6_Heading_update = drone6_Heading_list[iteration]
            drone6_Speed_update = drone6_Speed_list[iteration]
            drone6_Camera_update = camera_list[iteration]
            drone6_LengthOfStay_update = lengthOfStay_list[iteration]
            drone6_GimbalPitch_update = gimbalPitch_list[iteration]
            drone6_GimbalYaw_update = gimbalYaw_list[iteration]
            drone6_Integration_Window_update = drone6_integration_window[iteration]
            drone6_Minimum_Pose_Distance_update = drone6_minimum_pose_distance[iteration]
            
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
            drone6_Integration_Window_go = drone6_integration_window[iteration]
            drone6_Minimum_Pose_Distance_go = drone6_minimum_pose_distance[iteration]
            
            drone6_Rx_threshold = previous_drone6_rx_threshold[iteration]
            drone6_Compass_correction = previous_drone6_compass_correction[iteration]
            drone6_Focal_length = previous_drone6_focal_length[iteration]
            drone6_Focal_plane_pitch = previous_drone6_focal_plane_pitch[iteration]
            drone6_Focal_plane_roll = previous_drone6_focal_plane_roll[iteration]
            
            drone6_Latitude_update = drone6_Latitude_List[iteration]
            drone6_Longitude_update = drone6_Longitude_list[iteration]
            drone6_Altitude_update = drone6_Altitude_list[iteration]
            drone6_Heading_update = drone6_Heading_list[iteration]
            drone6_Speed_update = drone6_Speed_list[iteration]
            drone6_Camera_update = camera_list[iteration]
            drone6_LengthOfStay_update = lengthOfStay_list[iteration]
            drone6_GimbalPitch_update = gimbalPitch_list[iteration]
            drone6_GimbalYaw_update = gimbalYaw_list[iteration]
            drone6_Integration_Window_update = drone6_integration_window[iteration]
            drone6_Minimum_Pose_Distance_update = drone6_minimum_pose_distance[iteration]
            
            iteration += 2
            
        waypointvalue6 = incrementor
        
        ################ for reaching the waypoint ################
        
        if stop_waypoint_mission:
            with lock:
                drone_6_incrementor = incrementor
            break
        
        if task == 'update_camera_parameters':
            pass
        else:
            
            print("waypointvalue6_drone6(go):",waypointvalue6)
            
            drone6_waypoint_data_reached = f"{drone6_Latitude_go}:{drone6_Longitude_go}:{drone6_Altitude_go}:{drone6_Heading_go}:{drone6_Speed_go}:{waypointvalue6}:{Way6_threshold}:{drone6_GimbalPitch_go}:{drone6_GimbalYaw_go}:{drone6_Camera_go}:{drone6_parameter_mode}:{drone6_Rx_threshold}:{drone6_Compass_correction}:{drone6_Focal_length}:{drone6_Focal_plane_pitch}:{drone6_Focal_plane_roll}: {drone6_new_parameter_integral_go}:{drone6_Integration_Window_go}:{drone6_Minimum_Pose_Distance_go}"
            
            drone6_send_data = w.sendWayPointData(drone6_waypoint_data_reached, 6)     # 6 refers to the drone number
            
            drone6_waypoint_data_sent = f"Lat: {drone6_Latitude_go}, Long: {drone6_Longitude_go}, Alt: {drone6_Altitude_go}, Heading: {drone6_Heading_go}, Speed: {drone6_Speed_go}, Waypoint: {waypointvalue6}, Threshold: {Way6_threshold}, Gimbal Pitch: {drone6_GimbalPitch_go}, Gimbal Yaw: {drone6_GimbalYaw_go}, Camera: {drone6_Camera_go}, Mode: {drone6_parameter_mode}, RX Threshold: {drone6_Rx_threshold}, Compass Correction: {drone6_Compass_correction}, Focal Length: {drone6_Focal_length}, Focal Plane Pitch: {drone6_Focal_plane_pitch}, Focal Plane Roll: {drone6_Focal_plane_roll}, Integral: {drone6_new_parameter_integral_go}, Integration Window: {drone6_Integration_Window_go}, Minimum Pose Distance: {drone6_Minimum_Pose_Distance_go}"
            
            print("Data being Sent for drone6 (go):",drone6_waypoint_data_sent)
            
            while True:
                
                if break_while == True or drone_6_break_while == True:
                    break
                
                drone6_send_data = w.sendWayPointData(drone6_waypoint_data_reached, 6)
                drone6_Image_Telemetry_data = w.getImageAndTelemetryData(6)
                if((len(drone6_Image_Telemetry_data)) > 2000000):
                    drone6_Telemetry_data = (bytearray(drone6_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone6_Telemetry_data = (bytearray(drone6_Image_Telemetry_data[1382408:]).decode())
                
                drone6_elements = drone6_Telemetry_data.split(":")
                drone6_Waypoint_sent = drone6_elements[15].split('.')[0]
                
                if debug:
                    print("drone6_elements[16]_1:",drone6_elements[16])
                
                if float(drone6_elements[16]) == 0.0:
                    with lock:
                        drone_6_incrementor = 1
                    break
                
                if (drone6_Waypoint_sent) == str(incrementor) or break_while == True or drone_6_break_while == True:
                    if debug: 
                        print("drone6 Waypoint data sent for go")
                        print ("go thread for drone6:", drone6_Waypoint_sent, incrementor)
                    break
                
            if break_while == True or drone_6_break_while == True:
                with lock:
                    drone_6_incrementor = incrementor + 1
                    drone_6_thread_stop = True
                break
            
            while True:
                
                if break_while == True or drone_6_break_while == True:
                    break
                
                drone6_Image_Telemetry_data = w.getImageAndTelemetryData(6)
                if((len(drone6_Image_Telemetry_data)) > 2000000):
                    drone6_Telemetry_data = (bytearray(drone6_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone6_Telemetry_data = (bytearray(drone6_Image_Telemetry_data[1382408:]).decode())
                
                drone6_elements = drone6_Telemetry_data.split(":")
                drone6_Waypoint_reached = drone6_elements[14]
                
                if debug:
                    print("drone6_elements[16]_2:",drone6_elements[16])
                
                if float(drone6_elements[16]) == 0.0:
                    with lock:
                        drone_6_incrementor = 1
                    break
                
                if drone6_Waypoint_reached == str(incrementor) or break_while == True or drone_6_break_while == True:
                    if debug:
                        print("drone6 Waypoint has been reached")
                        print ("go thread waypoint reached for drone6:", drone6_Waypoint_reached, incrementor)
                    break
            
            if break_while == True or drone_6_break_while == True:
                with lock:
                    drone_6_incrementor = incrementor + 1
                    drone_6_thread_stop = True
                break    
            
            # Call the telemetry data again
            drone6_Image_Telemetry_data = w.getImageAndTelemetryData(6)
            if ((len(drone6_Image_Telemetry_data)) > 2000000):
                drone6_Telemetry_data = (bytearray(drone6_Image_Telemetry_data[3110408:]).decode())
            else:
                drone6_Telemetry_data = (bytearray(drone6_Image_Telemetry_data[1382408:]).decode())
                
            drone_6_telemetry_elements = drone6_Telemetry_data.split(":")
            
            latitude = drone_6_telemetry_elements[0]
            longitude = drone_6_telemetry_elements[1]
            altitude = drone_6_telemetry_elements[2]
            heading = drone_6_telemetry_elements[3]
            gimbal_pitch = drone_6_telemetry_elements[4]
            gimbal_yaw = drone_6_telemetry_elements[6]
            
            if debug:
                reached_data = f"Lat_Reached: {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
                print("Data Being Reached for drone6 (go) --->", reached_data)
                
                print("drone6_Waypointdata (go):", drone6_Telemetry_data)
                
            if drone6_LengthOfStay_go > 0:
                time.sleep(drone6_LengthOfStay_go)
                
            incrementor += 1
            
        ################ updating the waypoint ################
        
        waypointvalue6_update = incrementor
        
        print("waypointvalue6_drone6(update):",waypointvalue6_update)
        
        drone6_waypoint_data = f"{drone6_Latitude_update}:{drone6_Longitude_update}:{drone6_Altitude_update}:{drone6_Heading_update}:{drone6_Speed_update}:{waypointvalue6_update}:{Way6_threshold}:{drone6_GimbalPitch_update}:{drone6_GimbalYaw_update}:{drone6_Camera_update}:{drone6_parameter_mode}:{drone6_Rx_threshold}:{drone6_Compass_correction}:{drone6_Focal_length}:{drone6_Focal_plane_pitch}:{drone6_Focal_plane_roll}:{drone6_new_parameter_integral_update}:{drone6_Integration_Window_update}:{drone6_Minimum_Pose_Distance_update}"
        
        drone6_send_data = w.sendWayPointData(drone6_waypoint_data, 6)
        
        drone6_waypoint_data_sent = f"Lat: {drone6_Latitude_update}, Long: {drone6_Longitude_update}, Alt: {drone6_Altitude_update}, Heading: {drone6_Heading_update}, Speed: {drone6_Speed_update}, Waypoint: {waypointvalue6_update}, Threshold: {Way6_threshold}, Gimbal Pitch: {drone6_GimbalPitch_update}, Gimbal Yaw: {drone6_GimbalYaw_update}, Camera: {drone6_Camera_update}, Mode: {drone6_parameter_mode}, RX Threshold: {drone6_Rx_threshold}, Compass Correction: {drone6_Compass_correction}, Focal Length: {drone6_Focal_length}, Focal Plane Pitch: {drone6_Focal_plane_pitch}, Focal Plane Roll: {drone6_Focal_plane_roll}, Integral: {drone6_new_parameter_integral_update}, Integration Window: {drone6_Integration_Window_update}, Minimum Pose Distance: {drone6_Minimum_Pose_Distance_update}"
        
        print("Data Being Sent for drone6 (update) :",drone6_waypoint_data_sent)
        
        while True:
            
            if break_while == True or drone_6_break_while == True:
                break
            
            drone6_send_data = w.sendWayPointData(drone6_waypoint_data, 6) 
            drone6_Image_Telemetry_data = w.getImageAndTelemetryData(6)
            if((len(drone6_Image_Telemetry_data)) > 2000000):
                drone6_Telemetry_data = (bytearray(drone6_Image_Telemetry_data[3110408:]).decode())
            else:
                drone6_Telemetry_data = (bytearray(drone6_Image_Telemetry_data[1382408:]).decode())
                
            drone6_elements = drone6_Telemetry_data.split(":")
            drone6_Waypoint_sent = drone6_elements[15].split('.')[0]
            
            if debug:
                print("drone6_elements[16]_3:",drone6_elements[16])
            
            if float(drone6_elements[16]) == 0.0:
                with lock:
                    drone_6_incrementor = 1
                break
            
            if (drone6_Waypoint_sent) == str(incrementor) or break_while == True or drone_6_break_while == True:
                if debug: 
                    print("drone6 Waypoint data sent")
                    print ("run thread for drone6:", drone6_Waypoint_sent, incrementor)
                break
            
        if break_while == True or drone_6_break_while == True:
            with lock:
                drone_6_incrementor = incrementor + 1
                drone_6_thread_stop = True
            break
    
        while True:
            
            if break_while == True or drone_6_break_while == True:
                break
            
            drone6_Image_Telemetry_data = w.getImageAndTelemetryData(6)
            if((len(drone6_Image_Telemetry_data)) > 2000000):
                drone6_Telemetry_data = (bytearray(drone6_Image_Telemetry_data[3110408:]).decode())
            else:
                drone6_Telemetry_data = (bytearray(drone6_Image_Telemetry_data[1382408:]).decode())
                
            drone6_elements = drone6_Telemetry_data.split(":")
            drone6_Waypoint_reached = drone6_elements[14]
            
            if debug:
                print("drone6_elements[16]_4:",drone6_elements[16])
            
            if float(drone6_elements[16]) == 0.0:
                with lock:
                    drone_6_incrementor = 1
                break
            
            if drone6_Waypoint_reached == str(incrementor) or break_while == True or drone_6_break_while == True:
                if debug:
                    print("drone6 Waypoint has been reached")
                    print ("run thread waypoint reached:", drone6_Waypoint_reached, incrementor)
                break
            
        if break_while == True or drone_6_break_while == True:
            with lock:
                drone_6_incrementor = incrementor + 1
                drone_6_thread_stop = True
            break
        
        feedback_data_update_6 = {
                'drone_id': 6,
                'heading': drone6_Heading_update,
                'gimbalPitch': drone6_GimbalPitch_update,
                'gimbalYaw': drone6_GimbalYaw_update
            }
        
        if feedback_data_update_6['heading'] != 'N/A':
            if float(feedback_data_update_6['heading']) < 0.0:
                feedback_data_update_6['heading'] = 360.0 + float(feedback_data_update_6['heading'])
                feedback_data_update_6['heading'] = str(feedback_data_update_6['heading'])
                
        publish_feedback(active_clients[26], feedback_data_update_6, 6) # publish the feedback data to the client  # 26 refers to the client number, 6 refers to the drone number
    
        # Hold the drone at the waypoint for a specified length of time
        if drone6_LengthOfStay_update > 0:
            time.sleep(drone6_LengthOfStay_update)
            
            if debug:
                print("drone6_Waypointdata_before_holding:", drone6_Telemetry_data)
                print(f'drone6 is waiting  for {drone6_LengthOfStay_update} sn before taking the image and saving the telemetry data')  
                
        # Call the telemetry data again
        drone6_Image_Telemetry_data = w.getImageAndTelemetryData(6)
        if((len(drone6_Image_Telemetry_data)) > 2000000):
            drone6_Telemetry_data = (bytearray(drone6_Image_Telemetry_data[3110408:]).decode())
        else:
            drone6_Telemetry_data = (bytearray(drone6_Image_Telemetry_data[1382408:]).decode())
            
        drone_6_telemetry_elements = drone6_Telemetry_data.split(":")
        
        latitude = drone_6_telemetry_elements[0]
        longitude = drone_6_telemetry_elements[1]
        altitude = drone_6_telemetry_elements[2]
        heading = drone_6_telemetry_elements[3]
        gimbal_pitch = drone_6_telemetry_elements[4]
        gimbal_yaw = drone_6_telemetry_elements[6]
        
        if debug:
            reached_data = f"Lat_Reached {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for Updating Parameter for drone6 --->",reached_data)
            
            print("drone6_Waypointdata (update):", drone6_Telemetry_data)
            
            # Save the telemetry data to a text file inside the results folder
            file_path = os.path.join(Download_Location, 'telemetry6.txt')
            with open(file_path, 'a') as file:
                file.write(drone6_Telemetry_data + '\n')
                
        ## Covert YUV raw data to rgb image and save   ##
        
        if((len(drone6_Image_Telemetry_data)) > 2000000):
            crop_size = 1080
            if decoding == 'software':
                drone6_Image = cv2.cvtColor(drone6_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV420p2RGB)   # for software decoding
                
            elif decoding == 'hardware':
                drone6_Image = cv2.cvtColor(drone6_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV2BGR_NV12)
                
        else:
            
            crop_size = 720
            if decoding == 'software':
                drone6_Image = cv2.cvtColor(drone6_Image_Telemetry_data[0:1382400].reshape(720*3//2, 1280), cv2.COLOR_YUV420p2RGB)
                
            elif decoding == 'hardware':
                drone6_Image = cv2.cvtColor(drone6_Image_Telemetry_data[0:1382400].reshape(720*3//2, 1280), cv2.COLOR_YUV2BGR_NV12)
                
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
            waypoint_folder = f'drone6_waypoint_{drone6_waypoint_no}_('+ task + ')'
            waypoint_path = os.path.join(Images_Path, waypoint_folder)
            if not os.path.exists(waypoint_path):
                os.mkdir(waypoint_path)
            else:
                print("Folder already exists for drone6 (update)")
                
            cv2.imwrite(os.path.join( waypoint_path, 'drone6Image' + str(drone6_waypoint_no)+'.png'), drone6_cropped_Image)
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
                # Check if the drone is in manual mode
                drone6_Image_Telemetry_data = w.getImageAndTelemetryData(6)
                if((len(drone6_Image_Telemetry_data)) > 2000000):
                    drone6_Telemetry_data = (bytearray(drone6_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone6_Telemetry_data = (bytearray(drone6_Image_Telemetry_data[1382408:]).decode())
                    
                drone6_elements = drone6_Telemetry_data.split(":")
                
                # check 16th element to see if the drone is in manual mode
                
                if float(drone6_elements[16]) == 0.0:
                    drone_6_incrementor = 1
                else:
                    drone_6_incrementor = incrementor
                    
            if task == 'takeoff and waypoint':
                print("Takeoff and Mission Waypoint for drone6 completed")
            elif task == 'update_camera_parameters':
                print("Camera parameters updated for drone6")
            elif task == 'land':
                print("Land completed for drone6")
            elif task == 'emergency':
                print("Emergency Case")
            else:
                print("Invalid task")
            
            with lock:
                drone_6_thread_stop = True
                update_looking_drone_6 = True
                
            break

######################## Drone 7 Thread ############################
d7Image = []
d7Poses = []

def waypoint_tread_drone7(task, drone7_Latitude_List, drone7_Longitude_list, drone7_Altitude_list, drone7_Heading_list, drone7_Speed_list, Way7_threshold, camera_list, lengthOfStay_list, gimbalPitch_list, gimbalYaw_list, drone7_parameter_mode, drone7_rx_threshold, drone7_compass_correction, drone7_focal_length, drone7_focal_plane_pitch, drone7_focal_plane_roll, drone7_integration_window, drone7_minimum_pose_distance):
    
    number_of_waypoints_for_drone7 = len(drone7_Latitude_List)
    
    drone7_new_parameter_integral_go = 1 # for triggering integration while reaching (go) to the waypoint
    drone7_new_parameter_integral_update = 0
    
    global drone_7_incrementor, drone7_waypoint_no, camera, stop_waypoint_mission, break_while, drone_7_break_while, drone_7_thread_stop, update_looking_drone_7, active_clients
    
    with lock:
        drone_7_thread_stop = False
        update_looking_drone_7 = False
    
    incrementor = drone_7_incrementor
    
    previous_speed_list_drone7 = [drone7_Speed_list[0], *drone7_Speed_list]
    previous_heading_list_drone7 = [drone7_Heading_list[0], *drone7_Heading_list]
    previous_camera_list_drone7 = [camera_list[0], *camera_list]
    previous_lengthOfStay_list_drone7 = [lengthOfStay_list[0], *lengthOfStay_list]
    previous_gimbalPitch_list_drone7 = [gimbalPitch_list[0], *gimbalPitch_list]
    previous_gimbalYaw_list_drone7 = [gimbalYaw_list[0], *gimbalYaw_list]
    previous_drone7_rx_threshold = [drone7_rx_threshold[0], *drone7_rx_threshold]
    previous_drone7_compass_correction = [drone7_compass_correction[0], *drone7_compass_correction]
    previous_drone7_focal_length = [drone7_focal_length[0], *drone7_focal_length]
    previous_drone7_focal_plane_pitch = [drone7_focal_plane_pitch[0], *drone7_focal_plane_pitch]
    previous_drone7_focal_plane_roll = [drone7_focal_plane_roll[0], *drone7_focal_plane_roll]
    previous_drone7_integration_window = [drone7_integration_window[0], *drone7_integration_window]
    previous_drone7_minimum_pose_distance = [drone7_minimum_pose_distance[0], *drone7_minimum_pose_distance]
    
    iteration = 0
    
    while True:
        
        # Check if the drone is in manual mode
        drone7_Image_Telemetry_data = w.getImageAndTelemetryData(7) # 7 refers to the drone number
        
        if((len(drone7_Image_Telemetry_data)) > 2000000):
            drone7_Telemetry_data = (bytearray(drone7_Image_Telemetry_data[3110408:]).decode())
        else:
            drone7_Telemetry_data = (bytearray(drone7_Image_Telemetry_data[1382408:]).decode())
            
        drone7_elements = drone7_Telemetry_data.split(":")  # Extract all elements from the string
        
        # Check 16th element to see if the drone is in manual mode
        if float(drone7_elements[16]) == 0.0:
            with lock:
                drone_7_incrementor = 1
            break
        
        if task == 'takeoff and waypoint' or task == 'update_camera_parameters':
            with lock:
                drone7_waypoint_no = drone7_waypoint_no + 1       
            print(f"Mission Waypoint {drone7_waypoint_no} in progress for drone7 ...") 

            drone7_Latitude_go = drone7_Latitude_List[iteration]
            drone7_Longitude_go = drone7_Longitude_list[iteration]
            drone7_Altitude_go = drone7_Altitude_list[iteration]
            drone7_Heading_go = previous_heading_list_drone7[iteration]
            drone7_Speed_go = previous_speed_list_drone7[iteration]
            drone7_Camera_go = previous_camera_list_drone7[iteration]
            drone7_LengthOfStay_go = previous_lengthOfStay_list_drone7[iteration]
            drone7_GimbalPitch_go = previous_gimbalPitch_list_drone7[iteration]
            drone7_GimbalYaw_go = previous_gimbalYaw_list_drone7[iteration]
            drone7_Integration_Window_go = previous_drone7_integration_window[iteration]
            drone7_Minimum_Pose_Distance_go = previous_drone7_minimum_pose_distance[iteration]
            
            drone7_Rx_threshold = previous_drone7_rx_threshold[iteration]
            drone7_Compass_correction = previous_drone7_compass_correction[iteration]
            drone7_Focal_length = previous_drone7_focal_length[iteration]
            drone7_Focal_plane_pitch = previous_drone7_focal_plane_pitch[iteration]
            drone7_Focal_plane_roll = previous_drone7_focal_plane_roll[iteration]
            
            drone7_Latitude_update = drone7_Latitude_List[iteration]
            drone7_Longitude_update = drone7_Longitude_list[iteration]
            drone7_Altitude_update = drone7_Altitude_list[iteration]
            drone7_Heading_update = drone7_Heading_list[iteration]
            drone7_Speed_update = drone7_Speed_list[iteration]
            drone7_Camera_update = camera_list[iteration]
            drone7_LengthOfStay_update = lengthOfStay_list[iteration]
            drone7_GimbalPitch_update = gimbalPitch_list[iteration]
            drone7_GimbalYaw_update = gimbalYaw_list[iteration]
            drone7_Integration_Window_update = drone7_integration_window[iteration]
            drone7_Minimum_Pose_Distance_update = drone7_minimum_pose_distance[iteration]
            
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
            drone7_Integration_Window_go = drone7_integration_window[iteration]
            drone7_Minimum_Pose_Distance_go = drone7_minimum_pose_distance[iteration]
            
            drone7_Rx_threshold = previous_drone7_rx_threshold[iteration]
            drone7_Compass_correction = previous_drone7_compass_correction[iteration]
            drone7_Focal_length = previous_drone7_focal_length[iteration]
            drone7_Focal_plane_pitch = previous_drone7_focal_plane_pitch[iteration]
            drone7_Focal_plane_roll = previous_drone7_focal_plane_roll[iteration]
            
            drone7_Latitude_update = drone7_Latitude_List[iteration]
            drone7_Longitude_update = drone7_Longitude_list[iteration]
            drone7_Altitude_update = drone7_Altitude_list[iteration]
            drone7_Heading_update = drone7_Heading_list[iteration]
            drone7_Speed_update = drone7_Speed_list[iteration]
            drone7_Camera_update = camera_list[iteration]
            drone7_LengthOfStay_update = lengthOfStay_list[iteration]
            drone7_GimbalPitch_update = gimbalPitch_list[iteration]
            drone7_GimbalYaw_update = gimbalYaw_list[iteration]
            drone7_Integration_Window_update = drone7_integration_window[iteration]
            drone7_Minimum_Pose_Distance_update = drone7_minimum_pose_distance[iteration]
            
            iteration += 2
            
        waypointvalue7 = incrementor
        
        ################ for reaching the waypoint ################
        
        if stop_waypoint_mission:
            with lock:
                drone_7_incrementor = incrementor
            break
        
        if task == 'update_camera_parameters':
            pass
        else:
            
            print("waypointvalue7_drone7(go):",waypointvalue7)
            
            drone7_waypoint_data_reached = f"{drone7_Latitude_go}:{drone7_Longitude_go}:{drone7_Altitude_go}:{drone7_Heading_go}:{drone7_Speed_go}:{waypointvalue7}:{Way7_threshold}:{drone7_GimbalPitch_go}:{drone7_GimbalYaw_go}:{drone7_Camera_go}:{drone7_parameter_mode}:{drone7_Rx_threshold}:{drone7_Compass_correction}:{drone7_Focal_length}:{drone7_Focal_plane_pitch}:{drone7_Focal_plane_roll}: {drone7_new_parameter_integral_go}:{drone7_Integration_Window_go}:{drone7_Minimum_Pose_Distance_go}"
            
            drone7_send_data = w.sendWayPointData(drone7_waypoint_data_reached, 7)     # 7 refers to the drone number
            
            drone7_waypoint_data_sent = f"Lat: {drone7_Latitude_go}, Long: {drone7_Longitude_go}, Alt: {drone7_Altitude_go}, Heading: {drone7_Heading_go}, Speed: {drone7_Speed_go}, Waypoint: {waypointvalue7}, Threshold: {Way7_threshold}, Gimbal Pitch: {drone7_GimbalPitch_go}, Gimbal Yaw: {drone7_GimbalYaw_go}, Camera: {drone7_Camera_go}, Mode: {drone7_parameter_mode}, RX Threshold: {drone7_Rx_threshold}, Compass Correction: {drone7_Compass_correction}, Focal Length: {drone7_Focal_length}, Focal Plane Pitch: {drone7_Focal_plane_pitch}, Focal Plane Roll: {drone7_Focal_plane_roll}, Integral: {drone7_new_parameter_integral_go}, Integration Window: {drone7_Integration_Window_go}, Minimum Pose Distance: {drone7_Minimum_Pose_Distance_go}"
            
            print("Data being Sent for drone7 (go):",drone7_waypoint_data_sent)
            
            while True:
                
                if break_while == True or drone_7_break_while == True:
                    break
                
                drone7_send_data = w.sendWayPointData(drone7_waypoint_data_reached, 7)
                drone7_Image_Telemetry_data = w.getImageAndTelemetryData(7)
                if((len(drone7_Image_Telemetry_data)) > 2000000):
                    drone7_Telemetry_data = (bytearray(drone7_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone7_Telemetry_data = (bytearray(drone7_Image_Telemetry_data[1382408:]).decode())
                
                drone7_elements = drone7_Telemetry_data.split(":")
                drone7_Waypoint_sent = drone7_elements[15].split('.')[0]
                
                if debug:
                    print("drone7_elements[16]_1:",drone7_elements[16])
                
                if float(drone7_elements[16]) == 0.0:
                    with lock:
                        drone_7_incrementor = 1
                    break
                
                if (drone7_Waypoint_sent) == str(incrementor) or break_while == True or drone_7_break_while == True:
                    if debug: 
                        print("drone7 Waypoint data sent for go")
                        print ("go thread for drone7:", drone7_Waypoint_sent, incrementor)
                    break
            
            if break_while == True or drone_7_break_while == True:
                with lock:
                    drone_7_incrementor = incrementor + 1
                    drone_7_thread_stop = True
                break    
            
            while True:
                
                if break_while == True or drone_7_break_while == True:
                    break
                
                drone7_Image_Telemetry_data = w.getImageAndTelemetryData(7)
                if((len(drone7_Image_Telemetry_data)) > 2000000):
                    drone7_Telemetry_data = (bytearray(drone7_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone7_Telemetry_data = (bytearray(drone7_Image_Telemetry_data[1382408:]).decode())
                
                drone7_elements = drone7_Telemetry_data.split(":")
                drone7_Waypoint_reached = drone7_elements[14]
                
                if debug:
                    print("drone7_elements[16]_2:",drone7_elements[16])
                
                if float(drone7_elements[16]) == 0.0:
                    with lock:
                        drone_7_incrementor = 1
                    break
                
                if drone7_Waypoint_reached == str(incrementor) or break_while == True or drone_7_break_while == True:
                    if debug:
                        print("drone7 Waypoint has been reached")
                        print ("go thread waypoint reached for drone7:", drone7_Waypoint_reached, incrementor)
                    break
            
            if break_while == True or drone_7_break_while == True:
                with lock:
                    drone_7_incrementor = incrementor + 1
                    drone_7_thread_stop = True
                break
                
            # Call the telemetry data again
            drone7_Image_Telemetry_data = w.getImageAndTelemetryData(7)
            if ((len(drone7_Image_Telemetry_data)) > 2000000):
                drone7_Telemetry_data = (bytearray(drone7_Image_Telemetry_data[3110408:]).decode())
            else:
                drone7_Telemetry_data = (bytearray(drone7_Image_Telemetry_data[1382408:]).decode())
                
            drone_7_telemetry_elements = drone7_Telemetry_data.split(":")
            
            latitude = drone_7_telemetry_elements[0]
            longitude = drone_7_telemetry_elements[1]
            altitude = drone_7_telemetry_elements[2]
            heading = drone_7_telemetry_elements[3]
            gimbal_pitch = drone_7_telemetry_elements[4]
            gimbal_yaw = drone_7_telemetry_elements[6]
            
            if debug:
                reached_data = f"Lat_Reached: {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
                print("Data Being Reached for drone7 (go) --->", reached_data)
                
                print("drone7_Waypointdata (go):", drone7_Telemetry_data)
                
            if drone7_LengthOfStay_go > 0:
                time.sleep(drone7_LengthOfStay_go)
                
            incrementor += 1
            
        ################ updating the waypoint ################
        
        waypointvalue7_update = incrementor
        
        print("waypointvalue7_drone7(update):",waypointvalue7_update)
        
        drone7_waypoint_data = f"{drone7_Latitude_update}:{drone7_Longitude_update}:{drone7_Altitude_update}:{drone7_Heading_update}:{drone7_Speed_update}:{waypointvalue7_update}:{Way7_threshold}:{drone7_GimbalPitch_update}:{drone7_GimbalYaw_update}:{drone7_Camera_update}:{drone7_parameter_mode}:{drone7_Rx_threshold}:{drone7_Compass_correction}:{drone7_Focal_length}:{drone7_Focal_plane_pitch}:{drone7_Focal_plane_roll}:{drone7_new_parameter_integral_update}:{drone7_Integration_Window_update}:{drone7_Minimum_Pose_Distance_update}"
        
        drone7_send_data = w.sendWayPointData(drone7_waypoint_data, 7)
        
        drone7_waypoint_data_sent = f"Lat: {drone7_Latitude_update}, Long: {drone7_Longitude_update}, Alt: {drone7_Altitude_update}, Heading: {drone7_Heading_update}, Speed: {drone7_Speed_update}, Waypoint: {waypointvalue7_update}, Threshold: {Way7_threshold}, Gimbal Pitch: {drone7_GimbalPitch_update}, Gimbal Yaw: {drone7_GimbalYaw_update}, Camera: {drone7_Camera_update}, Mode: {drone7_parameter_mode}, RX Threshold: {drone7_Rx_threshold}, Compass Correction: {drone7_Compass_correction}, Focal Length: {drone7_Focal_length}, Focal Plane Pitch: {drone7_Focal_plane_pitch}, Focal Plane Roll: {drone7_Focal_plane_roll}, Integral: {drone7_new_parameter_integral_update}, Integration Window: {drone7_Integration_Window_update}, Minimum Pose Distance: {drone7_Minimum_Pose_Distance_update}"
        
        print("Data Being Sent for drone7 (update) :",drone7_waypoint_data_sent)
        
        while True:
            
            if break_while == True or drone_7_break_while == True:
                break
            
            drone7_send_data = w.sendWayPointData(drone7_waypoint_data, 7) 
            drone7_Image_Telemetry_data = w.getImageAndTelemetryData(7)
            if((len(drone7_Image_Telemetry_data)) > 2000000):
                drone7_Telemetry_data = (bytearray(drone7_Image_Telemetry_data[3110408:]).decode())
            else:
                drone7_Telemetry_data = (bytearray(drone7_Image_Telemetry_data[1382408:]).decode())
                
            drone7_elements = drone7_Telemetry_data.split(":")
            drone7_Waypoint_sent = drone7_elements[15].split('.')[0]
            
            if debug:
                print("drone7_elements[16]_3:",drone7_elements[16])
            
            if float(drone7_elements[16]) == 0.0:
                with lock:
                    drone_7_incrementor = 1
                break
            
            if (drone7_Waypoint_sent) == str(incrementor) or break_while == True or drone_7_break_while == True:
                if debug: 
                    print("drone7 Waypoint data sent")
                    print ("run thread for drone7:", drone7_Waypoint_sent, incrementor)
                break
        
        if break_while == True or drone_7_break_while == True:
            with lock:
                drone_7_incrementor = incrementor + 1
                drone_7_thread_stop = True
            break    
        
        while True:
            
            if break_while == True or drone_7_break_while == True:
                break
            
            drone7_Image_Telemetry_data = w.getImageAndTelemetryData(7)
            if((len(drone7_Image_Telemetry_data)) > 2000000):
                drone7_Telemetry_data = (bytearray(drone7_Image_Telemetry_data[3110408:]).decode())
            else:
                drone7_Telemetry_data = (bytearray(drone7_Image_Telemetry_data[1382408:]).decode())
                
            drone7_elements = drone7_Telemetry_data.split(":")
            drone7_Waypoint_reached = drone7_elements[14]
            
            if debug:
                print("drone7_elements[16]_4:",drone7_elements[16])
            
            if float(drone7_elements[16]) == 0.0:
                with lock:
                    drone_7_incrementor = 1
                break
            
            if drone7_Waypoint_reached == str(incrementor) or break_while == True or drone_7_break_while == True:
                if debug:
                    print("drone7 Waypoint has been reached")
                    print ("run thread waypoint reached:", drone7_Waypoint_reached, incrementor)
                break
        
        if break_while == True or drone_7_break_while == True:
            with lock:
                drone_7_incrementor = incrementor + 1
                drone_7_thread_stop = True
            break
        
        feedback_data_update_7 = {
                'drone_id': 7,
                'heading': drone7_Heading_update,
                'gimbalPitch': drone7_GimbalPitch_update,
                'gimbalYaw': drone7_GimbalYaw_update
            }
        
        if feedback_data_update_7['heading'] != 'N/A':
            if float(feedback_data_update_7['heading']) < 0.0:
                feedback_data_update_7['heading'] = 360.0 + float(feedback_data_update_7['heading'])
                feedback_data_update_7['heading'] = str(feedback_data_update_7['heading'])
                
        publish_feedback(active_clients[27], feedback_data_update_7, 7) # publish the feedback data to the client  # 27 refers to the client number, 7 refers to the drone number
        
        # Hold the drone at the waypoint for a specified length of time
        if drone7_LengthOfStay_update > 0:
            time.sleep(drone7_LengthOfStay_update)
            
            if debug:
                print("drone7_Waypointdata_before_holding:", drone7_Telemetry_data)
                print(f'drone7 is waiting  for {drone7_LengthOfStay_update} sn before taking the image and saving the telemetry data')  
                
        # Call the telemetry data again
        drone7_Image_Telemetry_data = w.getImageAndTelemetryData(7)
        if((len(drone7_Image_Telemetry_data)) > 2000000):
            drone7_Telemetry_data = (bytearray(drone7_Image_Telemetry_data[3110408:]).decode())
        else:
            drone7_Telemetry_data = (bytearray(drone7_Image_Telemetry_data[1382408:]).decode())
            
        drone_7_telemetry_elements = drone7_Telemetry_data.split(":")
        
        latitude = drone_7_telemetry_elements[0]
        longitude = drone_7_telemetry_elements[1]
        altitude = drone_7_telemetry_elements[2]
        heading = drone_7_telemetry_elements[3]
        gimbal_pitch = drone_7_telemetry_elements[4]
        gimbal_yaw = drone_7_telemetry_elements[6]
        
        if debug:
            reached_data = f"Lat_Reached {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for Updating Parameter for drone7 --->",reached_data)
            
            print("drone7_Waypointdata (update):", drone7_Telemetry_data)
            
            # Save the telemetry data to a text file inside the results folder
            file_path = os.path.join(Download_Location, 'telemetry7.txt')
            with open(file_path, 'a') as file:
                file.write(drone7_Telemetry_data + '\n')
                
        ## Covert YUV raw data to rgb image and save   ##
        
        if((len(drone7_Image_Telemetry_data)) > 2000000):
            crop_size = 1080
            if decoding == 'software':
                drone7_Image = cv2.cvtColor(drone7_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV420p2RGB)   # for software decoding
                
            elif decoding == 'hardware':
                drone7_Image = cv2.cvtColor(drone7_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV2BGR_NV12)
                
        else:
            
            crop_size = 720
            if decoding == 'software':
                drone7_Image = cv2.cvtColor(drone7_Image_Telemetry_data[0:1382400].reshape(720*3//2, 1280), cv2.COLOR_YUV420p2RGB)
                
            elif decoding == 'hardware':
                drone7_Image = cv2.cvtColor(drone7_Image_Telemetry_data[0:1382400].reshape(720*3//2, 1280), cv2.COLOR_YUV2BGR_NV12)
                
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
            waypoint_folder = f'drone7_waypoint_{drone7_waypoint_no}_('+ task + ')'
            waypoint_path = os.path.join(Images_Path, waypoint_folder)
            if not os.path.exists(waypoint_path):
                os.mkdir(waypoint_path)
            else:
                print("Folder already exists for drone7 (update)")
                
            cv2.imwrite(os.path.join( waypoint_path, 'drone7Image' + str(drone7_waypoint_no)+'.png'), drone7_cropped_Image)
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
                # Check if the drone is in manual mode
                drone7_Image_Telemetry_data = w.getImageAndTelemetryData(7)
                if((len(drone7_Image_Telemetry_data)) > 2000000):
                    drone7_Telemetry_data = (bytearray(drone7_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone7_Telemetry_data = (bytearray(drone7_Image_Telemetry_data[1382408:]).decode())
                    
                drone7_elements = drone7_Telemetry_data.split(":")
                
                # check 16th element to see if the drone is in manual mode
                
                if float(drone7_elements[16]) == 0.0:
                    drone_7_incrementor = 1
                else:
                    drone_7_incrementor = incrementor
                    
            if task == 'takeoff and waypoint':
                print("Takeoff and Mission Waypoint for drone7 completed")
            elif task == 'update_camera_parameters':
                print("Camera parameters updated for drone7")
            elif task == 'land':
                print("Land completed for drone7")
            elif task == 'emergency':
                print("Emergency Case")
            else:
                print("Invalid task")
            
            with lock:
                drone_7_thread_stop = True
                update_looking_drone_7 = True
            break

######################## Drone 8 Thread ############################
d8Image = []
d8Poses = []

def waypoint_tread_drone8(task, drone8_Latitude_List, drone8_Longitude_list, drone8_Altitude_list, drone8_Heading_list, drone8_Speed_list, Way8_threshold, camera_list, lengthOfStay_list, gimbalPitch_list, gimbalYaw_list, drone8_parameter_mode, drone8_rx_threshold, drone8_compass_correction, drone8_focal_length, drone8_focal_plane_pitch, drone8_focal_plane_roll, drone8_integration_window, drone8_minimum_pose_distance):
    
    number_of_waypoints_for_drone8 = len(drone8_Latitude_List)
    
    drone8_new_parameter_integral_go = 1 # for triggering integration while reaching (go) to the waypoint
    drone8_new_parameter_integral_update = 0
    
    global drone_8_incrementor, drone8_waypoint_no, camera, stop_waypoint_mission, break_while, drone_8_break_while, drone_8_thread_stop, update_looking_drone_8, active_clients
    
    with lock:
        drone_8_thread_stop = False
        update_looking_drone_8 = False
    
    incrementor = drone_8_incrementor
    
    previous_speed_list_drone8 = [drone8_Speed_list[0], *drone8_Speed_list]
    previous_heading_list_drone8 = [drone8_Heading_list[0], *drone8_Heading_list]
    previous_camera_list_drone8 = [camera_list[0], *camera_list]
    previous_lengthOfStay_list_drone8 = [lengthOfStay_list[0], *lengthOfStay_list]
    previous_gimbalPitch_list_drone8 = [gimbalPitch_list[0], *gimbalPitch_list]
    previous_gimbalYaw_list_drone8 = [gimbalYaw_list[0], *gimbalYaw_list]
    previous_drone8_rx_threshold = [drone8_rx_threshold[0], *drone8_rx_threshold]
    previous_drone8_compass_correction = [drone8_compass_correction[0], *drone8_compass_correction]
    previous_drone8_focal_length = [drone8_focal_length[0], *drone8_focal_length]
    previous_drone8_focal_plane_pitch = [drone8_focal_plane_pitch[0], *drone8_focal_plane_pitch]
    previous_drone8_focal_plane_roll = [drone8_focal_plane_roll[0], *drone8_focal_plane_roll]
    previous_drone8_integration_window = [drone8_integration_window[0], *drone8_integration_window]
    previous_drone8_minimum_pose_distance = [drone8_minimum_pose_distance[0], *drone8_minimum_pose_distance]
    
    iteration = 0
    
    while True:
        
        # Check if the drone is in manual mode
        drone8_Image_Telemetry_data = w.getImageAndTelemetryData(8) # 8 refers to the drone number
        
        if((len(drone8_Image_Telemetry_data)) > 2000000):
            drone8_Telemetry_data = (bytearray(drone8_Image_Telemetry_data[3110408:]).decode())
        else:
            drone8_Telemetry_data = (bytearray(drone8_Image_Telemetry_data[1382408:]).decode())
            
        drone8_elements = drone8_Telemetry_data.split(":")  # Extract all elements from the string
        
        # Check 16th element to see if the drone is in manual mode
        if float(drone8_elements[16]) == 0.0:
            with lock:
                drone_8_incrementor = 1
            break
        
        if task == 'takeoff and waypoint' or task == 'update_camera_parameters':
            with lock:
                drone8_waypoint_no = drone8_waypoint_no + 1       
            print(f"Mission Waypoint {drone8_waypoint_no} in progress for drone8 ...") 

            drone8_Latitude_go = drone8_Latitude_List[iteration]
            drone8_Longitude_go = drone8_Longitude_list[iteration]
            drone8_Altitude_go = drone8_Altitude_list[iteration]
            drone8_Heading_go = previous_heading_list_drone8[iteration]
            drone8_Speed_go = previous_speed_list_drone8[iteration]
            drone8_Camera_go = previous_camera_list_drone8[iteration]
            drone8_LengthOfStay_go = previous_lengthOfStay_list_drone8[iteration]
            drone8_GimbalPitch_go = previous_gimbalPitch_list_drone8[iteration]
            drone8_GimbalYaw_go = previous_gimbalYaw_list_drone8[iteration]
            drone8_Integration_Window_go = previous_drone8_integration_window[iteration]
            drone8_Minimum_Pose_Distance_go = previous_drone8_minimum_pose_distance[iteration]
            
            drone8_Rx_threshold = previous_drone8_rx_threshold[iteration]
            drone8_Compass_correction = previous_drone8_compass_correction[iteration]
            drone8_Focal_length = previous_drone8_focal_length[iteration]
            drone8_Focal_plane_pitch = previous_drone8_focal_plane_pitch[iteration]
            drone8_Focal_plane_roll = previous_drone8_focal_plane_roll[iteration]
            
            drone8_Latitude_update = drone8_Latitude_List[iteration]
            drone8_Longitude_update = drone8_Longitude_list[iteration]
            drone8_Altitude_update = drone8_Altitude_list[iteration]
            drone8_Heading_update = drone8_Heading_list[iteration]
            drone8_Speed_update = drone8_Speed_list[iteration]
            drone8_Camera_update = camera_list[iteration]
            drone8_LengthOfStay_update = lengthOfStay_list[iteration]
            drone8_GimbalPitch_update = gimbalPitch_list[iteration]
            drone8_GimbalYaw_update = gimbalYaw_list[iteration]
            drone8_Integration_Window_update = drone8_integration_window[iteration]
            drone8_Minimum_Pose_Distance_update = drone8_minimum_pose_distance[iteration]
            
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
            drone8_Integration_Window_go = drone8_integration_window[iteration]
            drone8_Minimum_Pose_Distance_go = drone8_minimum_pose_distance[iteration]
            
            drone8_Rx_threshold = previous_drone8_rx_threshold[iteration]
            drone8_Compass_correction = previous_drone8_compass_correction[iteration]
            drone8_Focal_length = previous_drone8_focal_length[iteration]
            drone8_Focal_plane_pitch = previous_drone8_focal_plane_pitch[iteration]
            drone8_Focal_plane_roll = previous_drone8_focal_plane_roll[iteration]
            
            drone8_Latitude_update = drone8_Latitude_List[iteration]
            drone8_Longitude_update = drone8_Longitude_list[iteration]
            drone8_Altitude_update = drone8_Altitude_list[iteration]
            drone8_Heading_update = drone8_Heading_list[iteration]
            drone8_Speed_update = drone8_Speed_list[iteration]
            drone8_Camera_update = camera_list[iteration]
            drone8_LengthOfStay_update = lengthOfStay_list[iteration]
            drone8_GimbalPitch_update = gimbalPitch_list[iteration]
            drone8_GimbalYaw_update = gimbalYaw_list[iteration]
            drone8_Integration_Window_update = drone8_integration_window[iteration]
            drone8_Minimum_Pose_Distance_update = drone8_minimum_pose_distance[iteration]
            
            iteration += 2
            
        waypointvalue8 = incrementor
        
        ################ for reaching the waypoint ################
        
        if stop_waypoint_mission:
            with lock:
                drone_8_incrementor = incrementor
            break
        
        if task == 'update_camera_parameters':
            pass
        else:
            
            print("waypointvalue8_drone8(go):",waypointvalue8)
            
            drone8_waypoint_data_reached = f"{drone8_Latitude_go}:{drone8_Longitude_go}:{drone8_Altitude_go}:{drone8_Heading_go}:{drone8_Speed_go}:{waypointvalue8}:{Way8_threshold}:{drone8_GimbalPitch_go}:{drone8_GimbalYaw_go}:{drone8_Camera_go}:{drone8_parameter_mode}:{drone8_Rx_threshold}:{drone8_Compass_correction}:{drone8_Focal_length}:{drone8_Focal_plane_pitch}:{drone8_Focal_plane_roll}: {drone8_new_parameter_integral_go}:{drone8_Integration_Window_go}:{drone8_Minimum_Pose_Distance_go}"
            
            drone8_send_data = w.sendWayPointData(drone8_waypoint_data_reached, 8)     # 8 refers to the drone number
            
            drone8_waypoint_data_sent = f"Lat: {drone8_Latitude_go}, Long: {drone8_Longitude_go}, Alt: {drone8_Altitude_go}, Heading: {drone8_Heading_go}, Speed: {drone8_Speed_go}, Waypoint: {waypointvalue8}, Threshold: {Way8_threshold}, Gimbal Pitch: {drone8_GimbalPitch_go}, Gimbal Yaw: {drone8_GimbalYaw_go}, Camera: {drone8_Camera_go}, Mode: {drone8_parameter_mode}, RX Threshold: {drone8_Rx_threshold}, Compass Correction: {drone8_Compass_correction}, Focal Length: {drone8_Focal_length}, Focal Plane Pitch: {drone8_Focal_plane_pitch}, Focal Plane Roll: {drone8_Focal_plane_roll}, Integral: {drone8_new_parameter_integral_go}, Integration Window: {drone8_Integration_Window_go}, Minimum Pose Distance: {drone8_Minimum_Pose_Distance_go}"
            
            print("Data being Sent for drone8 (go):",drone8_waypoint_data_sent)
            
            while True:
                
                if break_while == True or drone_8_break_while == True:
                    break
                
                drone8_send_data = w.sendWayPointData(drone8_waypoint_data_reached, 8)
                drone8_Image_Telemetry_data = w.getImageAndTelemetryData(8)
                if((len(drone8_Image_Telemetry_data)) > 2000000):
                    drone8_Telemetry_data = (bytearray(drone8_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone8_Telemetry_data = (bytearray(drone8_Image_Telemetry_data[1382408:]).decode())
                
                drone8_elements = drone8_Telemetry_data.split(":")
                drone8_Waypoint_sent = drone8_elements[15].split('.')[0]
                
                if debug:
                    print("drone8_elements[16]_1:",drone8_elements[16])
                
                if float(drone8_elements[16]) == 0.0:
                    with lock:
                        drone_8_incrementor = 1
                    break
                
                if (drone8_Waypoint_sent) == str(incrementor) or break_while == True or drone_8_break_while == True:
                    if debug: 
                        print("drone8 Waypoint data sent for go")
                        print ("go thread for drone8:", drone8_Waypoint_sent, incrementor)
                    break
            
            if break_while == True or drone_8_break_while == True:
                with lock:
                    drone_8_incrementor = incrementor + 1
                    drone_8_thread_stop = True
                break
            
            while True:
                
                if break_while == True or drone_8_break_while == True:
                    break
                
                drone8_Image_Telemetry_data = w.getImageAndTelemetryData(8)
                if((len(drone8_Image_Telemetry_data)) > 2000000):
                    drone8_Telemetry_data = (bytearray(drone8_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone8_Telemetry_data = (bytearray(drone8_Image_Telemetry_data[1382408:]).decode())
                
                drone8_elements = drone8_Telemetry_data.split(":")
                drone8_Waypoint_reached = drone8_elements[14]
                
                if debug:
                    print("drone8_elements[16]_2:",drone8_elements[16])
                
                if float(drone8_elements[16]) == 0.0:
                    with lock:
                        drone_8_incrementor = 1
                    break
                
                if drone8_Waypoint_reached == str(incrementor) or break_while == True or drone_8_break_while == True:
                    if debug:
                        print("drone8 Waypoint has been reached")
                        print ("go thread waypoint reached for drone8:", drone8_Waypoint_reached, incrementor)
                    break
                
            if break_while == True or drone_8_break_while == True:
                with lock:
                    drone_8_incrementor = incrementor + 1
                    drone_8_thread_stop = True
                break
                
            # Call the telemetry data again
            drone8_Image_Telemetry_data = w.getImageAndTelemetryData(8)
            if ((len(drone8_Image_Telemetry_data)) > 2000000):
                drone8_Telemetry_data = (bytearray(drone8_Image_Telemetry_data[3110408:]).decode())
            else:
                drone8_Telemetry_data = (bytearray(drone8_Image_Telemetry_data[1382408:]).decode())
                
            drone_8_telemetry_elements = drone8_Telemetry_data.split(":")
            
            latitude = drone_8_telemetry_elements[0]
            longitude = drone_8_telemetry_elements[1]
            altitude = drone_8_telemetry_elements[2]
            heading = drone_8_telemetry_elements[3]
            gimbal_pitch = drone_8_telemetry_elements[4]
            gimbal_yaw = drone_8_telemetry_elements[6]
            
            if debug:
                reached_data = f"Lat_Reached: {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
                print("Data Being Reached for drone8 (go) --->", reached_data)
                
                print("drone8_Waypointdata (go):", drone8_Telemetry_data)
                
            if drone8_LengthOfStay_go > 0:
                time.sleep(drone8_LengthOfStay_go)
                
            incrementor += 1
            
        ################ updating the waypoint ################
        
        waypointvalue8_update = incrementor
        
        print("waypointvalue8_drone8(update):",waypointvalue8_update)
        
        drone8_waypoint_data = f"{drone8_Latitude_update}:{drone8_Longitude_update}:{drone8_Altitude_update}:{drone8_Heading_update}:{drone8_Speed_update}:{waypointvalue8_update}:{Way8_threshold}:{drone8_GimbalPitch_update}:{drone8_GimbalYaw_update}:{drone8_Camera_update}:{drone8_parameter_mode}:{drone8_Rx_threshold}:{drone8_Compass_correction}:{drone8_Focal_length}:{drone8_Focal_plane_pitch}:{drone8_Focal_plane_roll}:{drone8_new_parameter_integral_update}:{drone8_Integration_Window_update}:{drone8_Minimum_Pose_Distance_update}"
        
        drone8_send_data = w.sendWayPointData(drone8_waypoint_data, 8)
        
        drone8_waypoint_data_sent = f"Lat: {drone8_Latitude_update}, Long: {drone8_Longitude_update}, Alt: {drone8_Altitude_update}, Heading: {drone8_Heading_update}, Speed: {drone8_Speed_update}, Waypoint: {waypointvalue8_update}, Threshold: {Way8_threshold}, Gimbal Pitch: {drone8_GimbalPitch_update}, Gimbal Yaw: {drone8_GimbalYaw_update}, Camera: {drone8_Camera_update}, Mode: {drone8_parameter_mode}, RX Threshold: {drone8_Rx_threshold}, Compass Correction: {drone8_Compass_correction}, Focal Length: {drone8_Focal_length}, Focal Plane Pitch: {drone8_Focal_plane_pitch}, Focal Plane Roll: {drone8_Focal_plane_roll}, Integral: {drone8_new_parameter_integral_update}, Integration Window: {drone8_Integration_Window_update}, Minimum Pose Distance: {drone8_Minimum_Pose_Distance_update}"
        
        print("Data Being Sent for drone8 (update) :",drone8_waypoint_data_sent)
        
        while True:
            
            if break_while == True or drone_8_break_while == True:
                break
            
            drone8_send_data = w.sendWayPointData(drone8_waypoint_data, 8) 
            drone8_Image_Telemetry_data = w.getImageAndTelemetryData(8)
            if((len(drone8_Image_Telemetry_data)) > 2000000):
                drone8_Telemetry_data = (bytearray(drone8_Image_Telemetry_data[3110408:]).decode())
            else:
                drone8_Telemetry_data = (bytearray(drone8_Image_Telemetry_data[1382408:]).decode())
                
            drone8_elements = drone8_Telemetry_data.split(":")
            drone8_Waypoint_sent = drone8_elements[15].split('.')[0]
            
            if debug:
                print("drone8_elements[16]_3:",drone8_elements[16])
            
            if float(drone8_elements[16]) == 0.0:
                with lock:
                    drone_8_incrementor = 1
                break
            
            if (drone8_Waypoint_sent) == str(incrementor) or break_while == True or drone_8_break_while == True:
                if debug: 
                    print("drone8 Waypoint data sent")
                    print ("run thread for drone8:", drone8_Waypoint_sent, incrementor)
                break
        
        if break_while == True or drone_8_break_while == True:
            with lock:
                drone_8_incrementor = incrementor + 1
                drone_8_thread_stop = True
            break    
        
        while True:
            
            if break_while == True or drone_8_break_while == True:
                break
            
            drone8_Image_Telemetry_data = w.getImageAndTelemetryData(8)
            if((len(drone8_Image_Telemetry_data)) > 2000000):
                drone8_Telemetry_data = (bytearray(drone8_Image_Telemetry_data[3110408:]).decode())
            else:
                drone8_Telemetry_data = (bytearray(drone8_Image_Telemetry_data[1382408:]).decode())
                
            drone8_elements = drone8_Telemetry_data.split(":")
            drone8_Waypoint_reached = drone8_elements[14]
            
            if debug:
                print("drone8_elements[16]_4:",drone8_elements[16])
            
            if float(drone8_elements[16]) == 0.0:
                with lock:
                    drone_8_incrementor = 1
                break
            
            if drone8_Waypoint_reached == str(incrementor) or break_while == True or drone_8_break_while == True:
                if debug:
                    print("drone8 Waypoint has been reached")
                    print ("run thread waypoint reached:", drone8_Waypoint_reached, incrementor)
                break
        
        if break_while == True or drone_8_break_while == True:
            with lock:
                drone_8_incrementor = incrementor + 1
                drone_8_thread_stop = True
            break
        
        feedback_data_update_8 = {
                'drone_id': 8,
                'heading': drone8_Heading_update,
                'gimbalPitch': drone8_GimbalPitch_update,
                'gimbalYaw': drone8_GimbalYaw_update
            }
        
        if feedback_data_update_8['heading'] != 'N/A':
            if float(feedback_data_update_8['heading']) < 0.0:
                feedback_data_update_8['heading'] = 360.0 + float(feedback_data_update_8['heading'])
                feedback_data_update_8['heading'] = str(feedback_data_update_8['heading'])
                
        publish_feedback(active_clients[28], feedback_data_update_8, 8) # publish the feedback data to the client  # 28 refers to the client number, 8 refers to the drone number
        
        # Hold the drone at the waypoint for a specified length of time
        if drone8_LengthOfStay_update > 0:
            time.sleep(drone8_LengthOfStay_update)
            
            if debug:
                print("drone8_Waypointdata_before_holding:", drone8_Telemetry_data)
                print(f'drone8 is waiting  for {drone8_LengthOfStay_update} sn before taking the image and saving the telemetry data')  
                
        # Call the telemetry data again
        drone8_Image_Telemetry_data = w.getImageAndTelemetryData(8)
        if((len(drone8_Image_Telemetry_data)) > 2000000):
            drone8_Telemetry_data = (bytearray(drone8_Image_Telemetry_data[3110408:]).decode())
        else:
            drone8_Telemetry_data = (bytearray(drone8_Image_Telemetry_data[1382408:]).decode())
            
        drone_8_telemetry_elements = drone8_Telemetry_data.split(":")
        
        latitude = drone_8_telemetry_elements[0]
        longitude = drone_8_telemetry_elements[1]
        altitude = drone_8_telemetry_elements[2]
        heading = drone_8_telemetry_elements[3]
        gimbal_pitch = drone_8_telemetry_elements[4]
        gimbal_yaw = drone_8_telemetry_elements[6]
        
        if debug:
            reached_data = f"Lat_Reached {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for Updating Parameter for drone8 --->",reached_data)
            
            print("drone8_Waypointdata (update):", drone8_Telemetry_data)
            
            # Save the telemetry data to a text file inside the results folder
            file_path = os.path.join(Download_Location, 'telemetry8.txt')
            with open(file_path, 'a') as file:
                file.write(drone8_Telemetry_data + '\n')
                
        ## Covert YUV raw data to rgb image and save   ##
        
        if((len(drone8_Image_Telemetry_data)) > 2000000):
            crop_size = 1080
            if decoding == 'software':
                drone8_Image = cv2.cvtColor(drone8_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV420p2RGB)   # for software decoding
                
            elif decoding == 'hardware':
                drone8_Image = cv2.cvtColor(drone8_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV2BGR_NV12)
                
        else:
            
            crop_size = 720
            if decoding == 'software':
                drone8_Image = cv2.cvtColor(drone8_Image_Telemetry_data[0:1382400].reshape(720*3//2, 1280), cv2.COLOR_YUV420p2RGB)
                
            elif decoding == 'hardware':
                drone8_Image = cv2.cvtColor(drone8_Image_Telemetry_data[0:1382400].reshape(720*3//2, 1280), cv2.COLOR_YUV2BGR_NV12)
                
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
            waypoint_folder = f'drone8_waypoint_{drone8_waypoint_no}_('+ task + ')'
            waypoint_path = os.path.join(Images_Path, waypoint_folder)
            if not os.path.exists(waypoint_path):
                os.mkdir(waypoint_path)
            else:
                print("Folder already exists for drone8 (update)")
                
            cv2.imwrite(os.path.join( waypoint_path, 'drone8Image' + str(drone8_waypoint_no)+'.png'), drone8_cropped_Image)
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
                # Check if the drone is in manual mode
                drone8_Image_Telemetry_data = w.getImageAndTelemetryData(8)
                if((len(drone8_Image_Telemetry_data)) > 2000000):
                    drone8_Telemetry_data = (bytearray(drone8_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone8_Telemetry_data = (bytearray(drone8_Image_Telemetry_data[1382408:]).decode())
                    
                drone8_elements = drone8_Telemetry_data.split(":")
                
                # check 16th element to see if the drone is in manual mode
                
                if float(drone8_elements[16]) == 0.0:
                    drone_8_incrementor = 1
                else:
                    drone_8_incrementor = incrementor
                    
            if task == 'takeoff and waypoint':
                print("Takeoff and Mission Waypoint for drone8 completed")
            elif task == 'update_camera_parameters':
                print("Camera parameters updated for drone8")
            elif task == 'land':
                print("Land completed for drone8")
            elif task == 'emergency':
                print("Emergency Case")
            else:
                print("Invalid task")
            
            with lock:
                drone_8_thread_stop = True
                update_looking_drone_8 = True
                
            break

######################## Drone 9 Thread ############################
d9Image = []
d9Poses = []

def waypoint_tread_drone9(task, drone9_Latitude_List, drone9_Longitude_list, drone9_Altitude_list, drone9_Heading_list, drone9_Speed_list, Way9_threshold, camera_list, lengthOfStay_list, gimbalPitch_list, gimbalYaw_list, drone9_parameter_mode, drone9_rx_threshold, drone9_compass_correction, drone9_focal_length, drone9_focal_plane_pitch, drone9_focal_plane_roll, drone9_integration_window, drone9_minimum_pose_distance):
    
    number_of_waypoints_for_drone9 = len(drone9_Latitude_List)
    
    drone9_new_parameter_integral_go = 1 # for triggering integration while reaching (go) to the waypoint
    drone9_new_parameter_integral_update = 0
    
    global drone_9_incrementor, drone9_waypoint_no, camera, stop_waypoint_mission, break_while, drone_9_break_while, drone_9_thread_stop, update_looking_drone_9, active_clients
    
    with lock:
        drone_9_thread_stop = False
        update_looking_drone_9 = False
    
    incrementor = drone_9_incrementor
    
    previous_speed_list_drone9 = [drone9_Speed_list[0], *drone9_Speed_list]
    previous_heading_list_drone9 = [drone9_Heading_list[0], *drone9_Heading_list]
    previous_camera_list_drone9 = [camera_list[0], *camera_list]
    previous_lengthOfStay_list_drone9 = [lengthOfStay_list[0], *lengthOfStay_list]
    previous_gimbalPitch_list_drone9 = [gimbalPitch_list[0], *gimbalPitch_list]
    previous_gimbalYaw_list_drone9 = [gimbalYaw_list[0], *gimbalYaw_list]
    previous_drone9_rx_threshold = [drone9_rx_threshold[0], *drone9_rx_threshold]
    previous_drone9_compass_correction = [drone9_compass_correction[0], *drone9_compass_correction]
    previous_drone9_focal_length = [drone9_focal_length[0], *drone9_focal_length]
    previous_drone9_focal_plane_pitch = [drone9_focal_plane_pitch[0], *drone9_focal_plane_pitch]
    previous_drone9_focal_plane_roll = [drone9_focal_plane_roll[0], *drone9_focal_plane_roll]
    previous_drone9_integration_window = [drone9_integration_window[0], *drone9_integration_window]
    previous_drone9_minimum_pose_distance = [drone9_minimum_pose_distance[0], *drone9_minimum_pose_distance]
    
    iteration = 0
    
    while True:
        
        # Check if the drone is in manual mode
        drone9_Image_Telemetry_data = w.getImageAndTelemetryData(9) # 9 refers to the drone number
        
        if((len(drone9_Image_Telemetry_data)) > 2000000):
            drone9_Telemetry_data = (bytearray(drone9_Image_Telemetry_data[3110408:]).decode())
        else:
            drone9_Telemetry_data = (bytearray(drone9_Image_Telemetry_data[1382408:]).decode())
            
        drone9_elements = drone9_Telemetry_data.split(":")  # Extract all elements from the string
        
        # Check 16th element to see if the drone is in manual mode
        if float(drone9_elements[16]) == 0.0:
            with lock:
                drone_9_incrementor = 1
            break
        
        if task == 'takeoff and waypoint' or task == 'update_camera_parameters':
            with lock:
                drone9_waypoint_no = drone9_waypoint_no + 1       
            print(f"Mission Waypoint {drone9_waypoint_no} in progress for drone9 ...") 

            drone9_Latitude_go = drone9_Latitude_List[iteration]
            drone9_Longitude_go = drone9_Longitude_list[iteration]
            drone9_Altitude_go = drone9_Altitude_list[iteration]
            drone9_Heading_go = previous_heading_list_drone9[iteration]
            drone9_Speed_go = previous_speed_list_drone9[iteration]
            drone9_Camera_go = previous_camera_list_drone9[iteration]
            drone9_LengthOfStay_go = previous_lengthOfStay_list_drone9[iteration]
            drone9_GimbalPitch_go = previous_gimbalPitch_list_drone9[iteration]
            drone9_GimbalYaw_go = previous_gimbalYaw_list_drone9[iteration]
            drone9_Integration_Window_go = previous_drone9_integration_window[iteration]
            drone9_Minimum_Pose_Distance_go = previous_drone9_minimum_pose_distance[iteration]
            
            drone9_Rx_threshold = previous_drone9_rx_threshold[iteration]
            drone9_Compass_correction = previous_drone9_compass_correction[iteration]
            drone9_Focal_length = previous_drone9_focal_length[iteration]
            drone9_Focal_plane_pitch = previous_drone9_focal_plane_pitch[iteration]
            drone9_Focal_plane_roll = previous_drone9_focal_plane_roll[iteration]
            
            drone9_Latitude_update = drone9_Latitude_List[iteration]
            drone9_Longitude_update = drone9_Longitude_list[iteration]
            drone9_Altitude_update = drone9_Altitude_list[iteration]
            drone9_Heading_update = drone9_Heading_list[iteration]
            drone9_Speed_update = drone9_Speed_list[iteration]
            drone9_Camera_update = camera_list[iteration]
            drone9_LengthOfStay_update = lengthOfStay_list[iteration]
            drone9_GimbalPitch_update = gimbalPitch_list[iteration]
            drone9_GimbalYaw_update = gimbalYaw_list[iteration]
            drone9_Integration_Window_update = drone9_integration_window[iteration]
            drone9_Minimum_Pose_Distance_update = drone9_minimum_pose_distance[iteration]
            
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
            drone9_Integration_Window_go = drone9_integration_window[iteration]
            drone9_Minimum_Pose_Distance_go = drone9_minimum_pose_distance[iteration]
            
            drone9_Rx_threshold = previous_drone9_rx_threshold[iteration]
            drone9_Compass_correction = previous_drone9_compass_correction[iteration]
            drone9_Focal_length = previous_drone9_focal_length[iteration]
            drone9_Focal_plane_pitch = previous_drone9_focal_plane_pitch[iteration]
            drone9_Focal_plane_roll = previous_drone9_focal_plane_roll[iteration]
            
            drone9_Latitude_update = drone9_Latitude_List[iteration]
            drone9_Longitude_update = drone9_Longitude_list[iteration]
            drone9_Altitude_update = drone9_Altitude_list[iteration]
            drone9_Heading_update = drone9_Heading_list[iteration]
            drone9_Speed_update = drone9_Speed_list[iteration]
            drone9_Camera_update = camera_list[iteration]
            drone9_LengthOfStay_update = lengthOfStay_list[iteration]
            drone9_GimbalPitch_update = gimbalPitch_list[iteration]
            drone9_GimbalYaw_update = gimbalYaw_list[iteration]
            drone9_Integration_Window_update = drone9_integration_window[iteration]
            drone9_Minimum_Pose_Distance_update = drone9_minimum_pose_distance[iteration]
            
            iteration += 2
            
        waypointvalue9 = incrementor
        
        ################ for reaching the waypoint ################
        
        if stop_waypoint_mission:
            with lock:
                drone_9_incrementor = incrementor
            break
        
        if task == 'update_camera_parameters':
            pass
        else:
            
            print("waypointvalue9_drone9(go):",waypointvalue9)
            
            drone9_waypoint_data_reached = f"{drone9_Latitude_go}:{drone9_Longitude_go}:{drone9_Altitude_go}:{drone9_Heading_go}:{drone9_Speed_go}:{waypointvalue9}:{Way9_threshold}:{drone9_GimbalPitch_go}:{drone9_GimbalYaw_go}:{drone9_Camera_go}:{drone9_parameter_mode}:{drone9_Rx_threshold}:{drone9_Compass_correction}:{drone9_Focal_length}:{drone9_Focal_plane_pitch}:{drone9_Focal_plane_roll}: {drone9_new_parameter_integral_go}:{drone9_Integration_Window_go}:{drone9_Minimum_Pose_Distance_go}"
            
            drone9_send_data = w.sendWayPointData(drone9_waypoint_data_reached, 9)     # 9 refers to the drone number
            
            drone9_waypoint_data_sent = f"Lat: {drone9_Latitude_go}, Long: {drone9_Longitude_go}, Alt: {drone9_Altitude_go}, Heading: {drone9_Heading_go}, Speed: {drone9_Speed_go}, Waypoint: {waypointvalue9}, Threshold: {Way9_threshold}, Gimbal Pitch: {drone9_GimbalPitch_go}, Gimbal Yaw: {drone9_GimbalYaw_go}, Camera: {drone9_Camera_go}, Mode: {drone9_parameter_mode}, RX Threshold: {drone9_Rx_threshold}, Compass Correction: {drone9_Compass_correction}, Focal Length: {drone9_Focal_length}, Focal Plane Pitch: {drone9_Focal_plane_pitch}, Focal Plane Roll: {drone9_Focal_plane_roll}, Integral: {drone9_new_parameter_integral_go}, Integration Window: {drone9_Integration_Window_go}, Minimum Pose Distance: {drone9_Minimum_Pose_Distance_go}"
            
            print("Data being Sent for drone9 (go):",drone9_waypoint_data_sent)
            
            while True:
                
                if break_while == True or drone_9_break_while == True:
                    break
                
                drone9_send_data = w.sendWayPointData(drone9_waypoint_data_reached, 9)
                drone9_Image_Telemetry_data = w.getImageAndTelemetryData(9)
                if((len(drone9_Image_Telemetry_data)) > 2000000):
                    drone9_Telemetry_data = (bytearray(drone9_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone9_Telemetry_data = (bytearray(drone9_Image_Telemetry_data[1382408:]).decode())
                
                drone9_elements = drone9_Telemetry_data.split(":")
                drone9_Waypoint_sent = drone9_elements[15].split('.')[0]
                
                if debug:
                    print("drone9_elements[16]_1:",drone9_elements[16])
                
                if float(drone9_elements[16]) == 0.0:
                    with lock:
                        drone_9_incrementor = 1
                    break
                
                if (drone9_Waypoint_sent) == str(incrementor) or break_while == True or drone_9_break_while == True:
                    if debug: 
                        print("drone9 Waypoint data sent for go")
                        print ("go thread for drone9:", drone9_Waypoint_sent, incrementor)
                    break
            
            if break_while == True or drone_9_break_while == True:
                with lock:
                    drone_9_incrementor = incrementor + 1
                    drone_9_thread_stop = True
                break
            
            while True:
                
                if break_while == True or drone_9_break_while == True:
                    break
                
                drone9_Image_Telemetry_data = w.getImageAndTelemetryData(9)
                if((len(drone9_Image_Telemetry_data)) > 2000000):
                    drone9_Telemetry_data = (bytearray(drone9_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone9_Telemetry_data = (bytearray(drone9_Image_Telemetry_data[1382408:]).decode())
                
                drone9_elements = drone9_Telemetry_data.split(":")
                drone9_Waypoint_reached = drone9_elements[14]
                
                if debug:
                    print("drone9_elements[16]_2:",drone9_elements[16])
                
                if float(drone9_elements[16]) == 0.0:
                    with lock:
                        drone_9_incrementor = 1
                    break
                
                if drone9_Waypoint_reached == str(incrementor) or break_while == True or drone_9_break_while == True:
                    if debug:
                        print("drone9 Waypoint has been reached")
                        print ("go thread waypoint reached for drone9:", drone9_Waypoint_reached, incrementor)
                    break
            
            if break_while == True or drone_9_break_while == True:
                with lock:
                    drone_9_incrementor = incrementor + 1
                    drone_9_thread_stop = True
                break
                
            # Call the telemetry data again
            drone9_Image_Telemetry_data = w.getImageAndTelemetryData(9)
            if ((len(drone9_Image_Telemetry_data)) > 2000000):
                drone9_Telemetry_data = (bytearray(drone9_Image_Telemetry_data[3110408:]).decode())
            else:
                drone9_Telemetry_data = (bytearray(drone9_Image_Telemetry_data[1382408:]).decode())
                
            drone_9_telemetry_elements = drone9_Telemetry_data.split(":")
            
            latitude = drone_9_telemetry_elements[0]
            longitude = drone_9_telemetry_elements[1]
            altitude = drone_9_telemetry_elements[2]
            heading = drone_9_telemetry_elements[3]
            gimbal_pitch = drone_9_telemetry_elements[4]
            gimbal_yaw = drone_9_telemetry_elements[6]
            
            if debug:
                reached_data = f"Lat_Reached: {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
                print("Data Being Reached for drone9 (go) --->", reached_data)
                
                print("drone9_Waypointdata (go):", drone9_Telemetry_data)
                
            if drone9_LengthOfStay_go > 0:
                time.sleep(drone9_LengthOfStay_go)
                
            incrementor += 1
            
        ################ updating the waypoint ################
        
        waypointvalue9_update = incrementor
        
        print("waypointvalue9_drone9(update):",waypointvalue9_update)
        
        drone9_waypoint_data = f"{drone9_Latitude_update}:{drone9_Longitude_update}:{drone9_Altitude_update}:{drone9_Heading_update}:{drone9_Speed_update}:{waypointvalue9_update}:{Way9_threshold}:{drone9_GimbalPitch_update}:{drone9_GimbalYaw_update}:{drone9_Camera_update}:{drone9_parameter_mode}:{drone9_Rx_threshold}:{drone9_Compass_correction}:{drone9_Focal_length}:{drone9_Focal_plane_pitch}:{drone9_Focal_plane_roll}:{drone9_new_parameter_integral_update}:{drone9_Integration_Window_update}:{drone9_Minimum_Pose_Distance_update}"
        
        drone9_send_data = w.sendWayPointData(drone9_waypoint_data, 9)
        
        drone9_waypoint_data_sent = f"Lat: {drone9_Latitude_update}, Long: {drone9_Longitude_update}, Alt: {drone9_Altitude_update}, Heading: {drone9_Heading_update}, Speed: {drone9_Speed_update}, Waypoint: {waypointvalue9_update}, Threshold: {Way9_threshold}, Gimbal Pitch: {drone9_GimbalPitch_update}, Gimbal Yaw: {drone9_GimbalYaw_update}, Camera: {drone9_Camera_update}, Mode: {drone9_parameter_mode}, RX Threshold: {drone9_Rx_threshold}, Compass Correction: {drone9_Compass_correction}, Focal Length: {drone9_Focal_length}, Focal Plane Pitch: {drone9_Focal_plane_pitch}, Focal Plane Roll: {drone9_Focal_plane_roll}, Integral: {drone9_new_parameter_integral_update}, Integration Window: {drone9_Integration_Window_update}, Minimum Pose Distance: {drone9_Minimum_Pose_Distance_update}"
        
        print("Data Being Sent for drone9 (update) :",drone9_waypoint_data_sent)
        
        while True:
            
            if break_while == True or drone_9_break_while == True:
                break
            
            drone9_send_data = w.sendWayPointData(drone9_waypoint_data, 9) 
            drone9_Image_Telemetry_data = w.getImageAndTelemetryData(9)
            if((len(drone9_Image_Telemetry_data)) > 2000000):
                drone9_Telemetry_data = (bytearray(drone9_Image_Telemetry_data[3110408:]).decode())
            else:
                drone9_Telemetry_data = (bytearray(drone9_Image_Telemetry_data[1382408:]).decode())
                
            drone9_elements = drone9_Telemetry_data.split(":")
            drone9_Waypoint_sent = drone9_elements[15].split('.')[0]
            
            if debug:
                print("drone9_elements[16]_3:",drone9_elements[16])
            
            if float(drone9_elements[16]) == 0.0:
                with lock:
                    drone_9_incrementor = 1
                break
            
            if (drone9_Waypoint_sent) == str(incrementor) or break_while == True or drone_9_break_while == True:
                if debug: 
                    print("drone9 Waypoint data sent")
                    print ("run thread for drone9:", drone9_Waypoint_sent, incrementor)
                break
            
        if break_while == True or drone_9_break_while == True:
            with lock:
                drone_9_incrementor = incrementor + 1
                drone_9_thread_stop = True
            break
        
        while True:
            
            if break_while == True or drone_9_break_while == True:
                break
            
            drone9_Image_Telemetry_data = w.getImageAndTelemetryData(9)
            if((len(drone9_Image_Telemetry_data)) > 2000000):
                drone9_Telemetry_data = (bytearray(drone9_Image_Telemetry_data[3110408:]).decode())
            else:
                drone9_Telemetry_data = (bytearray(drone9_Image_Telemetry_data[1382408:]).decode())
                
            drone9_elements = drone9_Telemetry_data.split(":")
            drone9_Waypoint_reached = drone9_elements[14]
            
            if debug:
                print("drone9_elements[16]_4:",drone9_elements[16])
            
            if float(drone9_elements[16]) == 0.0:
                with lock:
                    drone_9_incrementor = 1
                break
            
            if drone9_Waypoint_reached == str(incrementor) or break_while == True or drone_9_break_while == True:
                if debug:
                    print("drone9 Waypoint has been reached")
                    print ("run thread waypoint reached:", drone9_Waypoint_reached, incrementor)
                break
            
        if break_while == True or drone_9_break_while == True:
            with lock:
                drone_9_incrementor = incrementor + 1
                drone_9_thread_stop = True
            break
        
        feedback_data_update_9 = {
                'drone_id': 9,
                'heading': drone9_Heading_update,
                'gimbalPitch': drone9_GimbalPitch_update,
                'gimbalYaw': drone9_GimbalYaw_update
            }
        
        if feedback_data_update_9['heading'] != 'N/A':
            if float(feedback_data_update_9['heading']) < 0.0:
                feedback_data_update_9['heading'] = 360.0 + float(feedback_data_update_9['heading'])
                feedback_data_update_9['heading'] = str(feedback_data_update_9['heading'])
                
        publish_feedback(active_clients[29], feedback_data_update_9, 9) # publish the feedback data to the client  # 29 refers to the client number, 9 refers to the drone number
           
        # Hold the drone at the waypoint for a specified length of time
        if drone9_LengthOfStay_update > 0:
            time.sleep(drone9_LengthOfStay_update)
            
            if debug:
                print("drone9_Waypointdata_before_holding:", drone9_Telemetry_data)
                print(f'drone9 is waiting  for {drone9_LengthOfStay_update} sn before taking the image and saving the telemetry data')  
                
        # Call the telemetry data again
        drone9_Image_Telemetry_data = w.getImageAndTelemetryData(9)
        if((len(drone9_Image_Telemetry_data)) > 2000000):
            drone9_Telemetry_data = (bytearray(drone9_Image_Telemetry_data[3110408:]).decode())
        else:
            drone9_Telemetry_data = (bytearray(drone9_Image_Telemetry_data[1382408:]).decode())
            
        drone_9_telemetry_elements = drone9_Telemetry_data.split(":")
        
        latitude = drone_9_telemetry_elements[0]
        longitude = drone_9_telemetry_elements[1]
        altitude = drone_9_telemetry_elements[2]
        heading = drone_9_telemetry_elements[3]
        gimbal_pitch = drone_9_telemetry_elements[4]
        gimbal_yaw = drone_9_telemetry_elements[6]
        
        if debug:
            reached_data = f"Lat_Reached {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for Updating Parameter for drone9 --->",reached_data)
            
            print("drone9_Waypointdata (update):", drone9_Telemetry_data)
            
            # Save the telemetry data to a text file inside the results folder
            file_path = os.path.join(Download_Location, 'telemetry9.txt')
            with open(file_path, 'a') as file:
                file.write(drone9_Telemetry_data + '\n')
                
        ## Covert YUV raw data to rgb image and save   ##
        
        if((len(drone9_Image_Telemetry_data)) > 2000000):
            crop_size = 1080
            if decoding == 'software':
                drone9_Image = cv2.cvtColor(drone9_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV420p2RGB)   # for software decoding
                
            elif decoding == 'hardware':
                drone9_Image = cv2.cvtColor(drone9_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV2BGR_NV12)
                
        else:
            
            crop_size = 720
            if decoding == 'software':
                drone9_Image = cv2.cvtColor(drone9_Image_Telemetry_data[0:1382400].reshape(720*3//2, 1280), cv2.COLOR_YUV420p2RGB)
                
            elif decoding == 'hardware':
                drone9_Image = cv2.cvtColor(drone9_Image_Telemetry_data[0:1382400].reshape(720*3//2, 1280), cv2.COLOR_YUV2BGR_NV12)
                
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
            waypoint_folder = f'drone9_waypoint_{drone9_waypoint_no}_('+ task + ')'
            waypoint_path = os.path.join(Images_Path, waypoint_folder)
            if not os.path.exists(waypoint_path):
                os.mkdir(waypoint_path)
            else:
                print("Folder already exists for drone9 (update)")
                
            cv2.imwrite(os.path.join( waypoint_path, 'drone9Image' + str(drone9_waypoint_no)+'.png'), drone9_cropped_Image)
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
                # Check if the drone is in manual mode
                drone9_Image_Telemetry_data = w.getImageAndTelemetryData(9)
                if((len(drone9_Image_Telemetry_data)) > 2000000):
                    drone9_Telemetry_data = (bytearray(drone9_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone9_Telemetry_data = (bytearray(drone9_Image_Telemetry_data[1382408:]).decode())
                    
                drone9_elements = drone9_Telemetry_data.split(":")
                
                # check 16th element to see if the drone is in manual mode
                
                if float(drone9_elements[16]) == 0.0:
                    drone_9_incrementor = 1
                else:
                    drone_9_incrementor = incrementor
                    
            if task == 'takeoff and waypoint':
                print("Takeoff and Mission Waypoint for drone9 completed")
            elif task == 'update_camera_parameters':
                print("Camera parameters updated for drone9")
            elif task == 'land':
                print("Land completed for drone9")
            elif task == 'emergency':
                print("Emergency Case")
            else:
                print("Invalid task")
            
            with lock:
                drone_9_thread_stop = True
                update_looking_drone_9 = True
                
            break

######################## Drone 10 Thread ############################
d10Image = []
d10Poses = []

def waypoint_tread_drone10(task, drone10_Latitude_List, drone10_Longitude_list, drone10_Altitude_list, drone10_Heading_list, drone10_Speed_list, Way10_threshold, camera_list, lengthOfStay_list, gimbalPitch_list, gimbalYaw_list, drone10_parameter_mode, drone10_rx_threshold, drone10_compass_correction, drone10_focal_length, drone10_focal_plane_pitch, drone10_focal_plane_roll, drone10_integration_window, drone10_minimum_pose_distance):
    
    number_of_waypoints_for_drone10 = len(drone10_Latitude_List)
    
    drone10_new_parameter_integral_go = 1 # for triggering integration while reaching (go) to the waypoint
    drone10_new_parameter_integral_update = 0
    
    global drone_10_incrementor, drone10_waypoint_no, camera, stop_waypoint_mission, break_while, drone_10_break_while, drone_10_thread_stop, update_looking_drone_10, active_clients
    
    with lock:
        drone_10_thread_stop = False
        update_looking_drone_10 = False
    
    incrementor = drone_10_incrementor
    
    previous_speed_list_drone10 = [drone10_Speed_list[0], *drone10_Speed_list]
    previous_heading_list_drone10 = [drone10_Heading_list[0], *drone10_Heading_list]
    previous_camera_list_drone10 = [camera_list[0], *camera_list]
    previous_lengthOfStay_list_drone10 = [lengthOfStay_list[0], *lengthOfStay_list]
    previous_gimbalPitch_list_drone10 = [gimbalPitch_list[0], *gimbalPitch_list]
    previous_gimbalYaw_list_drone10 = [gimbalYaw_list[0], *gimbalYaw_list]
    previous_drone10_rx_threshold = [drone10_rx_threshold[0], *drone10_rx_threshold]
    previous_drone10_compass_correction = [drone10_compass_correction[0], *drone10_compass_correction]
    previous_drone10_focal_length = [drone10_focal_length[0], *drone10_focal_length]
    previous_drone10_focal_plane_pitch = [drone10_focal_plane_pitch[0], *drone10_focal_plane_pitch]
    previous_drone10_focal_plane_roll = [drone10_focal_plane_roll[0], *drone10_focal_plane_roll]
    previous_drone10_integration_window = [drone10_integration_window[0], *drone10_integration_window]
    previous_drone10_minimum_pose_distance = [drone10_minimum_pose_distance[0], *drone10_minimum_pose_distance]
    
    iteration = 0
    
    while True:
        
        # Check if the drone is in manual mode
        drone10_Image_Telemetry_data = w.getImageAndTelemetryData(10) # 10 refers to the drone number
        
        if((len(drone10_Image_Telemetry_data)) > 2000000):
            drone10_Telemetry_data = (bytearray(drone10_Image_Telemetry_data[3110408:]).decode())
        else:
            drone10_Telemetry_data = (bytearray(drone10_Image_Telemetry_data[1382408:]).decode())
            
        drone10_elements = drone10_Telemetry_data.split(":")  # Extract all elements from the string
        
        # Check 16th element to see if the drone is in manual mode
        if float(drone10_elements[16]) == 0.0:
            with lock:
                drone_10_incrementor = 1
            break
        
        if task == 'takeoff and waypoint' or task == 'update_camera_parameters':
            with lock:
                drone10_waypoint_no = drone10_waypoint_no + 1       
            print(f"Mission Waypoint {drone10_waypoint_no} in progress for drone10 ...") 

            drone10_Latitude_go = drone10_Latitude_List[iteration]
            drone10_Longitude_go = drone10_Longitude_list[iteration]
            drone10_Altitude_go = drone10_Altitude_list[iteration]
            drone10_Heading_go = previous_heading_list_drone10[iteration]
            drone10_Speed_go = previous_speed_list_drone10[iteration]
            drone10_Camera_go = previous_camera_list_drone10[iteration]
            drone10_LengthOfStay_go = previous_lengthOfStay_list_drone10[iteration]
            drone10_GimbalPitch_go = previous_gimbalPitch_list_drone10[iteration]
            drone10_GimbalYaw_go = previous_gimbalYaw_list_drone10[iteration]
            drone10_Integration_Window_go = previous_drone10_integration_window[iteration]
            drone10_Minimum_Pose_Distance_go = previous_drone10_minimum_pose_distance[iteration]
            
            drone10_Rx_threshold = previous_drone10_rx_threshold[iteration]
            drone10_Compass_correction = previous_drone10_compass_correction[iteration]
            drone10_Focal_length = previous_drone10_focal_length[iteration]
            drone10_Focal_plane_pitch = previous_drone10_focal_plane_pitch[iteration]
            drone10_Focal_plane_roll = previous_drone10_focal_plane_roll[iteration]
            
            drone10_Latitude_update = drone10_Latitude_List[iteration]
            drone10_Longitude_update = drone10_Longitude_list[iteration]
            drone10_Altitude_update = drone10_Altitude_list[iteration]
            drone10_Heading_update = drone10_Heading_list[iteration]
            drone10_Speed_update = drone10_Speed_list[iteration]
            drone10_Camera_update = camera_list[iteration]
            drone10_LengthOfStay_update = lengthOfStay_list[iteration]
            drone10_GimbalPitch_update = gimbalPitch_list[iteration]
            drone10_GimbalYaw_update = gimbalYaw_list[iteration]
            drone10_Integration_Window_update = drone10_integration_window[iteration]
            drone10_Minimum_Pose_Distance_update = drone10_minimum_pose_distance[iteration]
            
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
            drone10_Integration_Window_go = drone10_integration_window[iteration]
            drone10_Minimum_Pose_Distance_go = drone10_minimum_pose_distance[iteration]
            
            drone10_Rx_threshold = previous_drone10_rx_threshold[iteration]
            drone10_Compass_correction = previous_drone10_compass_correction[iteration]
            drone10_Focal_length = previous_drone10_focal_length[iteration]
            drone10_Focal_plane_pitch = previous_drone10_focal_plane_pitch[iteration]
            drone10_Focal_plane_roll = previous_drone10_focal_plane_roll[iteration]
            
            drone10_Latitude_update = drone10_Latitude_List[iteration]
            drone10_Longitude_update = drone10_Longitude_list[iteration]
            drone10_Altitude_update = drone10_Altitude_list[iteration]
            drone10_Heading_update = drone10_Heading_list[iteration]
            drone10_Speed_update = drone10_Speed_list[iteration]
            drone10_Camera_update = camera_list[iteration]
            drone10_LengthOfStay_update = lengthOfStay_list[iteration]
            drone10_GimbalPitch_update = gimbalPitch_list[iteration]
            drone10_GimbalYaw_update = gimbalYaw_list[iteration]
            drone10_Integration_Window_update = drone10_integration_window[iteration]
            drone10_Minimum_Pose_Distance_update = drone10_minimum_pose_distance[iteration]
            
            iteration += 2
            
        waypointvalue10 = incrementor
        
        ################ for reaching the waypoint ################
        
        if stop_waypoint_mission:
            with lock:
                drone_10_incrementor = incrementor
            break
        
        if task == 'update_camera_parameters':
            pass
        else:
            
            print("waypointvalue10_drone10(go):",waypointvalue10)
            
            drone10_waypoint_data_reached = f"{drone10_Latitude_go}:{drone10_Longitude_go}:{drone10_Altitude_go}:{drone10_Heading_go}:{drone10_Speed_go}:{waypointvalue10}:{Way10_threshold}:{drone10_GimbalPitch_go}:{drone10_GimbalYaw_go}:{drone10_Camera_go}:{drone10_parameter_mode}:{drone10_Rx_threshold}:{drone10_Compass_correction}:{drone10_Focal_length}:{drone10_Focal_plane_pitch}:{drone10_Focal_plane_roll}: {drone10_new_parameter_integral_go}:{drone10_Integration_Window_go}:{drone10_Minimum_Pose_Distance_go}"
            
            drone10_send_data = w.sendWayPointData(drone10_waypoint_data_reached, 10)     # 10 refers to the drone number
            
            drone10_waypoint_data_sent = f"Lat: {drone10_Latitude_go}, Long: {drone10_Longitude_go}, Alt: {drone10_Altitude_go}, Heading: {drone10_Heading_go}, Speed: {drone10_Speed_go}, Waypoint: {waypointvalue10}, Threshold: {Way10_threshold}, Gimbal Pitch: {drone10_GimbalPitch_go}, Gimbal Yaw: {drone10_GimbalYaw_go}, Camera: {drone10_Camera_go}, Mode: {drone10_parameter_mode}, RX Threshold: {drone10_Rx_threshold}, Compass Correction: {drone10_Compass_correction}, Focal Length: {drone10_Focal_length}, Focal Plane Pitch: {drone10_Focal_plane_pitch}, Focal Plane Roll: {drone10_Focal_plane_roll}, Integral: {drone10_new_parameter_integral_go}, Integration Window: {drone10_Integration_Window_go}, Minimum Pose Distance: {drone10_Minimum_Pose_Distance_go}"
            
            print("Data being Sent for drone10 (go):",drone10_waypoint_data_sent)
            
            while True:
                
                if break_while == True or drone_10_break_while == True:
                    break
                
                drone10_send_data = w.sendWayPointData(drone10_waypoint_data_reached, 10)
                drone10_Image_Telemetry_data = w.getImageAndTelemetryData(10)
                if((len(drone10_Image_Telemetry_data)) > 2000000):
                    drone10_Telemetry_data = (bytearray(drone10_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone10_Telemetry_data = (bytearray(drone10_Image_Telemetry_data[1382408:]).decode())
                
                drone10_elements = drone10_Telemetry_data.split(":")
                drone10_Waypoint_sent = drone10_elements[15].split('.')[0]
                
                if debug:
                    print("drone10_elements[16]_1:",drone10_elements[16])
                
                if float(drone10_elements[16]) == 0.0:
                    with lock:
                        drone_10_incrementor = 1
                    break
                
                if (drone10_Waypoint_sent) == str(incrementor) or break_while == True or drone_10_break_while == True:
                    if debug: 
                        print("drone10 Waypoint data sent for go")
                        print ("go thread for drone10:", drone10_Waypoint_sent, incrementor)
                    break
            
            if break_while == True or drone_10_break_while == True:
                with lock:
                    drone_10_incrementor = incrementor + 1
                    drone_10_thread_stop = True
                break
            
            while True:
                
                if break_while == True or drone_10_break_while == True:
                    break
                
                drone10_Image_Telemetry_data = w.getImageAndTelemetryData(10)
                if((len(drone10_Image_Telemetry_data)) > 2000000):
                    drone10_Telemetry_data = (bytearray(drone10_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone10_Telemetry_data = (bytearray(drone10_Image_Telemetry_data[1382408:]).decode())
                
                drone10_elements = drone10_Telemetry_data.split(":")
                drone10_Waypoint_reached = drone10_elements[14]
                
                if debug:
                    print("drone10_elements[16]_2:",drone10_elements[16])
                
                if float(drone10_elements[16]) == 0.0:
                    with lock:
                        drone_10_incrementor = 1
                    break
                
                if drone10_Waypoint_reached == str(incrementor) or break_while == True or drone_10_break_while == True:
                    if debug:
                        print("drone10 Waypoint has been reached")
                        print ("go thread waypoint reached for drone10:", drone10_Waypoint_reached, incrementor)
                    break
            
            if break_while == True or drone_10_break_while == True:
                with lock:
                    drone_10_incrementor = incrementor + 1
                    drone_10_thread_stop = True
                break
                
            # Call the telemetry data again
            drone10_Image_Telemetry_data = w.getImageAndTelemetryData(10)
            if ((len(drone10_Image_Telemetry_data)) > 2000000):
                drone10_Telemetry_data = (bytearray(drone10_Image_Telemetry_data[3110408:]).decode())
            else:
                drone10_Telemetry_data = (bytearray(drone10_Image_Telemetry_data[1382408:]).decode())
                
            drone_10_telemetry_elements = drone10_Telemetry_data.split(":")
            
            latitude = drone_10_telemetry_elements[0]
            longitude = drone_10_telemetry_elements[1]
            altitude = drone_10_telemetry_elements[2]
            heading = drone_10_telemetry_elements[3]
            gimbal_pitch = drone_10_telemetry_elements[4]
            gimbal_yaw = drone_10_telemetry_elements[6]
            
            if debug:
                reached_data = f"Lat_Reached: {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
                print("Data Being Reached for drone10 (go) --->", reached_data)
                
                print("drone10_Waypointdata (go):", drone10_Telemetry_data)
                
            if drone10_LengthOfStay_go > 0:
                time.sleep(drone10_LengthOfStay_go)
                
            incrementor += 1
            
        ################ updating the waypoint ################
        
        waypointvalue10_update = incrementor
        
        print("waypointvalue10_drone10(update):",waypointvalue10_update)
        
        drone10_waypoint_data = f"{drone10_Latitude_update}:{drone10_Longitude_update}:{drone10_Altitude_update}:{drone10_Heading_update}:{drone10_Speed_update}:{waypointvalue10_update}:{Way10_threshold}:{drone10_GimbalPitch_update}:{drone10_GimbalYaw_update}:{drone10_Camera_update}:{drone10_parameter_mode}:{drone10_Rx_threshold}:{drone10_Compass_correction}:{drone10_Focal_length}:{drone10_Focal_plane_pitch}:{drone10_Focal_plane_roll}:{drone10_new_parameter_integral_update}:{drone10_Integration_Window_update}:{drone10_Minimum_Pose_Distance_update}"
        
        drone10_send_data = w.sendWayPointData(drone10_waypoint_data, 10)
        
        drone10_waypoint_data_sent = f"Lat: {drone10_Latitude_update}, Long: {drone10_Longitude_update}, Alt: {drone10_Altitude_update}, Heading: {drone10_Heading_update}, Speed: {drone10_Speed_update}, Waypoint: {waypointvalue10_update}, Threshold: {Way10_threshold}, Gimbal Pitch: {drone10_GimbalPitch_update}, Gimbal Yaw: {drone10_GimbalYaw_update}, Camera: {drone10_Camera_update}, Mode: {drone10_parameter_mode}, RX Threshold: {drone10_Rx_threshold}, Compass Correction: {drone10_Compass_correction}, Focal Length: {drone10_Focal_length}, Focal Plane Pitch: {drone10_Focal_plane_pitch}, Focal Plane Roll: {drone10_Focal_plane_roll}, Integral: {drone10_new_parameter_integral_update}, Integration Window: {drone10_Integration_Window_update}, Minimum Pose Distance: {drone10_Minimum_Pose_Distance_update}"
        
        print("Data Being Sent for drone10 (update) :",drone10_waypoint_data_sent)
        
        while True:
            
            if break_while == True or drone_10_break_while == True:
                break
            
            drone10_send_data = w.sendWayPointData(drone10_waypoint_data, 10) 
            drone10_Image_Telemetry_data = w.getImageAndTelemetryData(10)
            if((len(drone10_Image_Telemetry_data)) > 2000000):
                drone10_Telemetry_data = (bytearray(drone10_Image_Telemetry_data[3110408:]).decode())
            else:
                drone10_Telemetry_data = (bytearray(drone10_Image_Telemetry_data[1382408:]).decode())
                
            drone10_elements = drone10_Telemetry_data.split(":")
            drone10_Waypoint_sent = drone10_elements[15].split('.')[0]
            
            if debug:
                print("drone10_elements[16]_3:",drone10_elements[16])
            
            if float(drone10_elements[16]) == 0.0:
                with lock:
                    drone_10_incrementor = 1
                break
            
            if (drone10_Waypoint_sent) == str(incrementor) or break_while == True or drone_10_break_while == True:
                if debug: 
                    print("drone10 Waypoint data sent")
                    print ("run thread for drone10:", drone10_Waypoint_sent, incrementor)
                break
        
        if break_while == True or drone_10_break_while == True:
            with lock:
                drone_10_incrementor = incrementor + 1
                drone_10_thread_stop = True
            break
        
        while True:
            
            if break_while == True or drone_10_break_while == True:
                break
            
            drone10_Image_Telemetry_data = w.getImageAndTelemetryData(10)
            if((len(drone10_Image_Telemetry_data)) > 2000000):
                drone10_Telemetry_data = (bytearray(drone10_Image_Telemetry_data[3110408:]).decode())
            else:
                drone10_Telemetry_data = (bytearray(drone10_Image_Telemetry_data[1382408:]).decode())
                
            drone10_elements = drone10_Telemetry_data.split(":")
            drone10_Waypoint_reached = drone10_elements[14]
            
            if debug:
                print("drone10_elements[16]_4:",drone10_elements[16])
            
            if float(drone10_elements[16]) == 0.0:
                with lock:
                    drone_10_incrementor = 1
                break
            
            if drone10_Waypoint_reached == str(incrementor) or break_while == True or drone_10_break_while == True:
                if debug:
                    print("drone10 Waypoint has been reached")
                    print ("run thread waypoint reached:", drone10_Waypoint_reached, incrementor)
                break
            
        if break_while == True or drone_10_break_while == True:
            with lock:
                drone_10_incrementor = incrementor + 1
                drone_10_thread_stop = True
            break
        
        feedback_data_update_10 = {
                'drone_id': 10,
                'heading': drone10_Heading_update,
                'gimbalPitch': drone10_GimbalPitch_update,
                'gimbalYaw': drone10_GimbalYaw_update
            }
        
        if feedback_data_update_10['heading'] != 'N/A':
            if float(feedback_data_update_10['heading']) < 0.0:
                feedback_data_update_10['heading'] = 360.0 + float(feedback_data_update_10['heading'])
                feedback_data_update_10['heading'] = str(feedback_data_update_10['heading'])
                
        publish_feedback(active_clients[30], feedback_data_update_10, 10) # publish the feedback data to the client  # 30 refers to the client number, 10 refers to the drone number
        
        # Hold the drone at the waypoint for a specified length of time
        if drone10_LengthOfStay_update > 0:
            time.sleep(drone10_LengthOfStay_update)
            
            if debug:
                print("drone10_Waypointdata_before_holding:", drone10_Telemetry_data)
                print(f'drone10 is waiting  for {drone10_LengthOfStay_update} sn before taking the image and saving the telemetry data')  
                
        # Call the telemetry data again
        drone10_Image_Telemetry_data = w.getImageAndTelemetryData(10)
        if((len(drone10_Image_Telemetry_data)) > 2000000):
            drone10_Telemetry_data = (bytearray(drone10_Image_Telemetry_data[3110408:]).decode())
        else:
            drone10_Telemetry_data = (bytearray(drone10_Image_Telemetry_data[1382408:]).decode())
            
        drone_10_telemetry_elements = drone10_Telemetry_data.split(":")
        
        latitude = drone_10_telemetry_elements[0]
        longitude = drone_10_telemetry_elements[1]
        altitude = drone_10_telemetry_elements[2]
        heading = drone_10_telemetry_elements[3]
        gimbal_pitch = drone_10_telemetry_elements[4]
        gimbal_yaw = drone_10_telemetry_elements[6]
        
        if debug:
            reached_data = f"Lat_Reached {latitude}, Long_Reached: {longitude}, Alt_Reached: {altitude}, Heading_Reached: {heading}, Gimbal Pitch: {gimbal_pitch}, Gimbal Yaw: {gimbal_yaw}"
            print("Data Being Reached for Updating Parameter for drone10 --->",reached_data)
            
            print("drone10_Waypointdata (update):", drone10_Telemetry_data)
            
            # Save the telemetry data to a text file inside the results folder
            file_path = os.path.join(Download_Location, 'telemetry10.txt')
            with open(file_path, 'a') as file:
                file.write(drone10_Telemetry_data + '\n')
                
        ## Covert YUV raw data to rgb image and save   ##
        
        if((len(drone10_Image_Telemetry_data)) > 2000000):
            crop_size = 1080
            if decoding == 'software':
                drone10_Image = cv2.cvtColor(drone10_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV420p2RGB)   # for software decoding
                
            elif decoding == 'hardware':
                drone10_Image = cv2.cvtColor(drone10_Image_Telemetry_data[0:3110400].reshape(1080*3//2, 1920), cv2.COLOR_YUV2BGR_NV12)
                
        else:
            
            crop_size = 720
            if decoding == 'software':
                drone10_Image = cv2.cvtColor(drone10_Image_Telemetry_data[0:1382400].reshape(720*3//2, 1280), cv2.COLOR_YUV420p2RGB)
                
            elif decoding == 'hardware':
                drone10_Image = cv2.cvtColor(drone10_Image_Telemetry_data[0:1382400].reshape(720*3//2, 1280), cv2.COLOR_YUV2BGR_NV12)
                
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
            waypoint_folder = f'drone10_waypoint_{drone10_waypoint_no}_('+ task + ')'
            waypoint_path = os.path.join(Images_Path, waypoint_folder)
            if not os.path.exists(waypoint_path):
                os.mkdir(waypoint_path)
            else:
                print("Folder already exists for drone10 (update)")
                
            cv2.imwrite(os.path.join( waypoint_path, 'drone10Image' + str(drone10_waypoint_no)+'.png'), drone10_cropped_Image)
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
                # Check if the drone is in manual mode
                drone10_Image_Telemetry_data = w.getImageAndTelemetryData(10)
                if((len(drone10_Image_Telemetry_data)) > 2000000):
                    drone10_Telemetry_data = (bytearray(drone10_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone10_Telemetry_data = (bytearray(drone10_Image_Telemetry_data[1382408:]).decode())
                    
                drone10_elements = drone10_Telemetry_data.split(":")
                
                # check 16th element to see if the drone is in manual mode
                
                if float(drone10_elements[16]) == 0.0:
                    drone_10_incrementor = 1
                else:
                    drone_10_incrementor = incrementor
                    
            if task == 'takeoff and waypoint':
                print("Takeoff and Mission Waypoint for drone10 completed")
            elif task == 'update_camera_parameters':
                print("Camera parameters updated for drone10")
            elif task == 'land':
                print("Land completed for drone10")
            elif task == 'emergency':
                print("Emergency Case")
            else:
                print("Invalid task")
                
            with lock:
                drone_10_thread_stop = True
            
            break

######################### Taking Waypoint Data and Sending if there is no waypoint data coming from the server ############################
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

received_drone_data = None
data = None
global stop_server, last_data_id
stop_server = False
NewData = False
last_data_id = None  # Unique identifier to check for new data

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
        
    def is_new_data(self, data):
        """Checks if the data is new based on a unique identifier"""
        global last_data_id
        current_id = data.get("timestamp") if "timestamp" in data else int(time.time() * 1000)  # Use timestamp if available, else use current time
        is_new = current_id != last_data_id
        last_data_id = current_id
        return is_new
        
    def do_POST(self):
        global received_drone_data, NewData
        
        content_length = int(self.headers['Content-Length'])
        
        post_data = self.rfile.read(content_length)

        import encodings.idna
        try:
            received_drone_data = json.loads(post_data.decode('utf-8'))
            print("Received data:", received_drone_data)
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")
            received_drone_data = {}
            
        if self.is_new_data(received_drone_data):  
            NewData = True  

        print("Type of received_drone_data:", type(received_drone_data))   ### it is a string
        #print(received_drone_data)

        if not received_drone_data == str({}):  
            # Save the received data if it is not empty
            self.save_data(received_drone_data)
            # print('saving data')
        else:
            # If received data is empty, load previously saved data
            received_drone_data = self.load_data()
            print("Loaded saved data from file:", received_drone_data)
            
        # Send back the received or loaded data to the client
        response_data = json.dumps(received_drone_data)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        
        import encodings.idna

        self.wfile.write(response_data.encode('utf-8'))
    
def process_data():
    """Function to process data periodically if new data is available."""
    global NewData, received_drone_data, stop_server, send_data_to_drone, break_while, camera
    
    while not stop_server:
        if NewData:
            
            with lock:
                
                send_data_to_drone = True
                # print('send_data_to_drone1', send_data_to_drone)
                break_while = True
                # print('break_while1:', break_while)
                NewData = False
                data = received_drone_data
                
                if type(data) == str:
                    # transform the string data into a dictionary
                    data = json.loads(data)
                    
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
                globals()[f'drone_{drone_id}_waypoint_integration_window'] = []
                globals()[f'drone_{drone_id}_waypoint_minpose_distance'] = []
                globals()[f'drone_{drone_id}_waypoint_integration'] = []
                globals()[f'drone_{drone_id}_waypoint_anomaly'] = []
                
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
                    globals()[f'drone_{drone_id}_waypoint_integration_window'].append(waypoint['integrationWindow'])
                    globals()[f'drone_{drone_id}_waypoint_minpose_distance'].append(float(waypoint['minposeDistance']))
                    globals()[f'drone_{drone_id}_waypoint_integration'].append(waypoint['integration'])
                    globals()[f'drone_{drone_id}_waypoint_anomaly'].append(waypoint['anomaly'])
                    
            # # if the values are outside the range, set them to the maximum or minimum value
            for drone_id in data.keys():
                drone_id = int(drone_id)
                number_of_waypoints = len(globals()[f'drone_{drone_id}_waypoint_lat'])
                for i in range(number_of_waypoints):
                    
                    if globals()[f'drone_{drone_id}_waypoint_camera'][i] == 'tele':
                        globals()[f'drone_{drone_id}_waypoint_camera'][i] = 93
                        
                    elif globals()[f'drone_{drone_id}_waypoint_camera'][i] != 'tele':
                        if globals()[f'drone_{drone_id}_waypoint_integration'][i] == 'on' and globals()[f'drone_{drone_id}_waypoint_anomaly'][i] == 'on':
                            if globals()[f'drone_{drone_id}_waypoint_camera'][i] == 'wide angle': # rgb
                                globals()[f'drone_{drone_id}_waypoint_camera'][i] = 98 
                            elif globals()[f'drone_{drone_id}_waypoint_camera'][i] == 'thermal image': # thermal image
                                globals()[f'drone_{drone_id}_waypoint_camera'][i] = 99
                        elif globals()[f'drone_{drone_id}_waypoint_integration'][i] == 'off' and globals()[f'drone_{drone_id}_waypoint_anomaly'][i] == 'on':
                            if globals()[f'drone_{drone_id}_waypoint_camera'][i] == 'wide angle': # rgb
                                globals()[f'drone_{drone_id}_waypoint_camera'][i] = 96 
                            elif globals()[f'drone_{drone_id}_waypoint_camera'][i] == 'thermal image': # thermal image
                                globals()[f'drone_{drone_id}_waypoint_camera'][i] = 97
                        elif globals()[f'drone_{drone_id}_waypoint_integration'][i] == 'on' and globals()[f'drone_{drone_id}_waypoint_anomaly'][i] == 'off':
                            if globals()[f'drone_{drone_id}_waypoint_camera'][i] == 'wide angle':
                                globals()[f'drone_{drone_id}_waypoint_camera'][i] = 94
                            elif globals()[f'drone_{drone_id}_waypoint_camera'][i] == 'thermal image':
                                globals()[f'drone_{drone_id}_waypoint_camera'][i] = 95
                        else:
                            if globals()[f'drone_{drone_id}_waypoint_camera'][i] == 'wide angle':
                                globals()[f'drone_{drone_id}_waypoint_camera'][i] = 91
                            elif globals()[f'drone_{drone_id}_waypoint_camera'][i] == 'thermal image':
                                globals()[f'drone_{drone_id}_waypoint_camera'][i] = 92
                    else:
                        globals()[f'drone_{drone_id}_waypoint_camera'][i] = 91 # wide angle camera  
                        
                    with lock:
                        camera[drone_id-1] = globals()[f'drone_{drone_id}_waypoint_camera'][i]
                    
                    
            
                    # convert headings from (0, 360) to (-180, 180)
                    if globals()[f'drone_{drone_id}_waypoint_heading'][i] > 180:
                        globals()[f'drone_{drone_id}_waypoint_heading'][i] = globals()[f'drone_{drone_id}_waypoint_heading'][i] - 360
                    elif globals()[f'drone_{drone_id}_waypoint_heading'][i] < -180:
                        globals()[f'drone_{drone_id}_waypoint_heading'][i] = globals()[f'drone_{drone_id}_waypoint_heading'][i] + 360
                        
            print(f'camera: {camera}')
            
            # print the waypoint data for each drone
            for drone_id in data.keys():
                print(f'drone_{drone_id}_waypoint_lat: {globals()[f"drone_{drone_id}_waypoint_lat"]}')
                print(f'drone_{drone_id}_waypoint_lng: {globals()[f"drone_{drone_id}_waypoint_lng"]}')
                print(f'drone_{drone_id}_waypoint_speed: {globals()[f"drone_{drone_id}_waypoint_speed"]}')
                print(f'drone_{drone_id}_waypoint_lengthOfStay: {globals()[f"drone_{drone_id}_waypoint_lengthOfStay"]}')
                print(f'drone_{drone_id}_waypoint_altitude: {globals()[f"drone_{drone_id}_waypoint_altitude"]}')
                print(f'drone_{drone_id}_waypoint_camera: {globals()[f"drone_{drone_id}_waypoint_camera"]}')
                print(f'drone_{drone_id}_waypoint_gimbalPitch: {globals()[f"drone_{drone_id}_waypoint_gimbalPitch"]}')
                print(f'drone_{drone_id}_waypoint_gimbalYaw: {globals()[f"drone_{drone_id}_waypoint_gimbalYaw"]}')
                print(f'drone_{drone_id}_waypoint_heading: {globals()[f"drone_{drone_id}_waypoint_heading"]}')
                print(f'drone_{drone_id}_waypoint_integration_window: {globals()[f"drone_{drone_id}_waypoint_integration_window"]}')
                print(f'drone_{drone_id}_waypoint_minpose_distance: {globals()[f"drone_{drone_id}_waypoint_minpose_distance"]}')
                print(f'drone_{drone_id}_waypoint_integration: {globals()[f"drone_{drone_id}_waypoint_integration"]}')
                print(f'drone_{drone_id}_waypoint_anomaly: {globals()[f"drone_{drone_id}_waypoint_anomaly"]}')
                print("\n")

        time.sleep(0.1)  # Small delay to reduce CPU usage
     
def reset_for_new_mission():
    global received_drone_data, stop_server, stop_waypoint_mission
    received_drone_data = None
    stop_server = False
    stop_waypoint_mission = False

def find_global_heading(connected_drones):
    # Heading Arrangement

    land_altitude = 2 # Altitude for landing for each drone
    heading_list = []
    init_latitude_list = []
    init_longitude_list = []

    for drone_id in connected_drones:
        drone_Image_Telemetry_data = w.getImageAndTelemetryData(drone_id)
        if((len(drone_Image_Telemetry_data)) > 2000000):
            drone_Telemetry_data = (bytearray(drone_Image_Telemetry_data[3110408:]).decode())
        else:
            drone_Telemetry_data = (bytearray(drone_Image_Telemetry_data[1382408:]).decode())
        #drone_Telemetry_data = (bytearray(drone_Image_Telemetry_data[3110408:]).decode())
        drone_elements = drone_Telemetry_data.split(":")  # Extract all elements from the string.
        
        drone_latitude = drone_elements[0]
        drone_longitude = drone_elements[1]
        drone_heading = drone_elements[3]
        
        heading_list.append(drone_heading)
        init_latitude_list.append(drone_latitude)
        init_longitude_list.append(drone_longitude)
        
        # print(f'drone{drone_id}_latitude: {drone_latitude}', f'drone{drone_id}_longitude: {drone_longitude}', f'drone{drone_id}_heading: {drone_heading}')
        
        # waypoints for each drone
        globals()[f'drone{drone_id}_Latitude_list_takeoff_land'] = [drone_latitude]
        globals()[f'drone{drone_id}_Longitude_list_takeoff_land'] = [drone_longitude]
        globals()[f'drone{drone_id}_Altitude_takeoff_land'] = [globals()[f'drone_{drone_id}_waypoint_altitude'][0], land_altitude]

    
    if debug:
        print(f'heading_list: {heading_list}')

    heading_num = int(len(heading_list)//2) # middle drone is taken as the reference drone
    global_heading = heading_list[heading_num] # heading of the drone in the middle of the swarm is taken as the global heading
    print(f'global_heading: {global_heading}')  
    
    return global_heading, init_latitude_list, init_longitude_list  

def execute_landing_procedure():
    global action_in_progress, last_longitudes, last_latitudes, stop_waypoint_mission, simulation_mode, break_while, global_heading, Way_threshold, drone_threads_landing, connected_drones, drone_1_break_while, drone_2_break_while, drone_3_break_while, drone_4_break_while, drone_5_break_while, drone_6_break_while, drone_7_break_while, drone_8_break_while, drone_9_break_while, drone_10_break_while
    
    task = 'land'
    
    with lock:
        break_while = True
        
    action_in_progress = True
    print("Executing Landing Procedure.")

    drone_threads_landing = []
    thresh_waypoint = Way_threshold
    
    for id in connected_drones:
        latitude_list_landing =  [last_latitudes[id-1], last_latitudes[id-1], globals()[f'drone{id}_Latitude_list_takeoff_land'][0], globals()[f'drone{id}_Latitude_list_takeoff_land'][0], globals()[f'drone{id}_Latitude_list_takeoff_land'][0], globals()[f'drone{id}_Latitude_list_takeoff_land'][0]]
        
        longitude_list_landing = [last_longitudes[id-1], last_longitudes[id-1], globals()[f'drone{id}_Longitude_list_takeoff_land'][0], globals()[f'drone{id}_Longitude_list_takeoff_land'][0], globals()[f'drone{id}_Longitude_list_takeoff_land'][0], globals()[f'drone{id}_Longitude_list_takeoff_land'][0]]
        
        drone_altitude_landing = [globals()[f'drone{id}_Altitude_takeoff_land'][0], globals()[f'drone{id}_Altitude_takeoff_land'][0], globals()[f'drone{id}_Altitude_takeoff_land'][0], globals()[f'drone{id}_Altitude_takeoff_land'][0], globals()[f'drone{id}_Altitude_takeoff_land'][1], globals()[f'drone{id}_Altitude_takeoff_land'][1]]

        
        speed_list_landing = [globals()[f'drone_{id}_waypoint_speed'][-1]] * 6
        heading_list_landing = [globals()[f'drone_{id}_waypoint_heading'][-1], globals()[f'drone_{id}_waypoint_heading'][-1], globals()[f'drone_{id}_waypoint_heading'][-1], global_heading, global_heading, global_heading]
        camera_list_landing = [globals()[f'drone_{id}_waypoint_camera'][-1]] * 6
        gimbalPitch_list_landing = [globals()[f'drone_{id}_waypoint_gimbalPitch'][-1]] * 6
        gimbalYaw_list_landing = [globals()[f'drone_{id}_waypoint_gimbalYaw'][-1]] * 6
        lengthOfStay_list_landing = [0] * 6
        
        drone_landing_focal_length = [focal_length[id]]*6
        drone_landing_compass_correction = [compass_correction[id]]*6
        drone_landing_rx_threshold = [RX_threshold[id]]*6
        drone_landing_focal_plane_pitch = [focal_plane_pitch[id]]*6
        drone_landing_focal_plane_roll = [focal_plane_roll[id]]*6
        
        drone_landing_integration_window = [globals()[f'drone_{id}_waypoint_integration_window'][-1]] * 6
        drone_landing_minpose_distance = [globals()[f'drone_{id}_waypoint_minpose_distance'][-1]] * 6
        
        drone_parameter_mode = 0
        
        if simulation_mode == True:
            latitude_list_landing = ['N/A']*6
            longitude_list_landing = ['N/A']*6
            heading_list_landing = ['N/A']*6
                 
        thread_numbers1 = threading.Thread(target=globals()[f'waypoint_tread_drone{id}'], args=(task, latitude_list_landing, longitude_list_landing, drone_altitude_landing, heading_list_landing, speed_list_landing, thresh_waypoint, camera_list_landing, lengthOfStay_list_landing, gimbalPitch_list_landing, gimbalYaw_list_landing, drone_parameter_mode, drone_landing_rx_threshold, drone_landing_compass_correction, drone_landing_focal_length, drone_landing_focal_plane_pitch, drone_landing_focal_plane_roll, drone_landing_integration_window, drone_landing_minpose_distance)) 
                                                                                                
        drone_threads_landing.append(thread_numbers1)

    with lock:
        stop_waypoint_mission = False
        break_while = False
        drone_1_break_while = False
        drone_2_break_while = False
        drone_3_break_while = False
        drone_4_break_while = False
        drone_5_break_while = False
        drone_6_break_while = False
        drone_7_break_while = False
        drone_8_break_while = False
        drone_9_break_while = False
        drone_10_break_while = False
        
    for thread in drone_threads_landing:
        thread.start()

    for thread in drone_threads_landing:
        thread.join()
    
    print('Landing completed')
    action_in_progress = False

def execute_waypoint_mission():
    global action_in_progress, stop_waypoint_mission, received_drone_data, move_drones, global_heading, Way_threshold, waypoint_threads, landing_completed, u_key, takeoff_completed, send_data_to_drone, break_while, simulation_mode
    
    global_heading, init_latitude_list, init_longitude_list = find_global_heading(connected_drones)
    
    takeoff_completed = False
    action_in_progress = True
    
    task = 'takeoff and waypoint'

    print("Executing Takeoff and Waypoint Mission Procedure.")

    # Start the key monitor l key thread
    l_key_monitor_thread = threading.Thread(target=monitor_l_key)
    l_key_monitor_thread.daemon = True
    l_key_monitor_thread.start()
    
    waypoint_status = 0
    
    while not stop_waypoint_mission:
        waypoint_threads = [] 

        if send_data_to_drone == True:
            # print('waypoint_while2')
            with lock:
                send_data_to_drone = False
                # print('send_data_to_drone3', send_data_to_drone)
 
            # print('entered')
            if landing_completed == True:
                landing_completed = False
                
            received_drone_data = None
            with lock:
                break_while = False
                # print('break_while2:', break_while)
               
            drone_focal_length = []
            drone_compass_correction = []
            drone_rx_threshold = []
            drone_focal_plane_pitch = []
            drone_focal_plane_roll = []
            
            for id in connected_drones:

                if stop_waypoint_mission:
                    break
                
                if waypoint_status == 0 and u_key == False:
                    latitude_list_waypoint = globals()[f'drone_{id}_waypoint_lat']
                    latitude_list_waypoint.insert(0, globals()[f'drone{id}_Latitude_list_takeoff_land'][0])

                    longitude_list_waypoint = globals()[f'drone_{id}_waypoint_lng']
                    longitude_list_waypoint.insert(0, globals()[f'drone{id}_Longitude_list_takeoff_land'][0])      
                    
                    altitude_list_waypoint = globals()[f'drone_{id}_waypoint_altitude']
                    altitude_list_waypoint.insert(0, globals()[f'drone{id}_Altitude_takeoff_land'][0])
                    
                    speed_list_waypoint = globals()[f'drone_{id}_waypoint_speed']
                    speed_list_waypoint.insert(0, globals()[f'drone_{id}_waypoint_speed'][0])
                    
                    heading_list_waypoint = globals()[f'drone_{id}_waypoint_heading']
                    heading_list_waypoint.insert(0, global_heading)
                    
                    if simulation_mode == True:
                        latitude_list_waypoint = ['N/A']*len(latitude_list_waypoint)
                        longitude_list_waypoint = ['N/A']*len(longitude_list_waypoint)
                        heading_list_waypoint = ['N/A']*len(heading_list_waypoint)
                    
                    camera_list_waypoint = globals()[f'drone_{id}_waypoint_camera']
                    camera_list_waypoint.insert(0, globals()[f'drone_{id}_waypoint_camera'][0])
                    
                    lengthOfStay_list_waypoint = globals()[f'drone_{id}_waypoint_lengthOfStay']
                    lengthOfStay_list_waypoint.insert(0, 0)
                    
                    gimbalPitch_list_waypoint = globals()[f'drone_{id}_waypoint_gimbalPitch']
                    gimbalPitch_list_waypoint.insert(0, globals()[f'drone_{id}_waypoint_gimbalPitch'][0])
                    
                    gimbalYaw_list_waypoint = globals()[f'drone_{id}_waypoint_gimbalYaw']
                    gimbalYaw_list_waypoint.insert(0, globals()[f'drone_{id}_waypoint_gimbalYaw'][0])
                    
                    drone_integration_window = globals()[f'drone_{id}_waypoint_integration_window']
                    drone_integration_window.insert(0, globals()[f'drone_{id}_waypoint_integration_window'][0])
                    
                    drone_minpose_distance = globals()[f'drone_{id}_waypoint_minpose_distance']
                    drone_minpose_distance.insert(0, globals()[f'drone_{id}_waypoint_minpose_distance'][0])

                else:
                    u_key = False
                    latitude_list_waypoint = globals()[f'drone_{id}_waypoint_lat']
                    longitude_list_waypoint = globals()[f'drone_{id}_waypoint_lng']
                    
                        
                    altitude_list_waypoint = globals()[f'drone_{id}_waypoint_altitude']
                    speed_list_waypoint = globals()[f'drone_{id}_waypoint_speed']
                    heading_list_waypoint = globals()[f'drone_{id}_waypoint_heading']
                    
                    if simulation_mode == True:
                        latitude_list_waypoint = ['N/A']*len(latitude_list_waypoint)
                        longitude_list_waypoint = ['N/A']*len(longitude_list_waypoint)
                        heading_list_waypoint = ['N/A']*len(heading_list_waypoint)
                        
                    camera_list_waypoint = globals()[f'drone_{id}_waypoint_camera']
                    lengthOfStay_list_waypoint = globals()[f'drone_{id}_waypoint_lengthOfStay']
                    gimbalPitch_list_waypoint = globals()[f'drone_{id}_waypoint_gimbalPitch']
                    gimbalYaw_list_waypoint = globals()[f'drone_{id}_waypoint_gimbalYaw']
                    drone_integration_window = globals()[f'drone_{id}_waypoint_integration_window']
                    drone_minpose_distance = globals()[f'drone_{id}_waypoint_minpose_distance']
                    
                drone_focal_length = [0]*len(latitude_list_waypoint)
                drone_compass_correction = [0]*len(latitude_list_waypoint)
                drone_rx_threshold = [0]*len(latitude_list_waypoint)
                drone_focal_plane_pitch = [0]*len(latitude_list_waypoint)
                drone_focal_plane_roll = [0]*len(latitude_list_waypoint)
                    
                drone_parameter_mode = 0    
                thresh_waypoint = Way_threshold

                print('latitude_list_waypoint: ', latitude_list_waypoint, 'longitude_list_waypoint: ', longitude_list_waypoint, 'altitude_list_waypoint: ', altitude_list_waypoint, 'speed_list_waypoint: ', speed_list_waypoint, 'heading_list_waypoint: ', heading_list_waypoint, 'camera_list_waypoint: ', camera_list_waypoint, 'lengthOfStay_list_waypoint: ', lengthOfStay_list_waypoint, 'gimbalPitch_list_waypoint: ', gimbalPitch_list_waypoint, 'gimbalYaw_list_waypoint: ', gimbalYaw_list_waypoint, 'thresh_waypoint: ', thresh_waypoint, 'drone_focal_length: ', drone_focal_length, 'drone_compass_correction: ', drone_compass_correction, 'drone_rx_threshold: ', drone_rx_threshold, 'drone_focal_plane_pitch: ', drone_focal_plane_pitch, 'drone_focal_plane_roll: ', drone_focal_plane_roll, 'drone_integration_window: ', drone_integration_window, 'drone_minpose_distance: ', drone_minpose_distance)
                
                if stop_waypoint_mission:
                    break
                
                thread_numbers_1 = threading.Thread(target=globals()[f'waypoint_tread_drone{id}'], args=(task,
                    latitude_list_waypoint, longitude_list_waypoint, altitude_list_waypoint,
                    heading_list_waypoint, speed_list_waypoint, thresh_waypoint, camera_list_waypoint,
                    lengthOfStay_list_waypoint, gimbalPitch_list_waypoint, gimbalYaw_list_waypoint, drone_parameter_mode, drone_rx_threshold, drone_compass_correction, drone_focal_length, drone_focal_plane_pitch, drone_focal_plane_roll, drone_integration_window, drone_minpose_distance))
                waypoint_threads.append(thread_numbers_1)
                
                if stop_waypoint_mission:
                    break
            
            for thread in waypoint_threads:
                thread.start()
        
            for thread in waypoint_threads:
                thread.join()
            
            if stop_waypoint_mission:
                break

            waypoint_status += 1 
            
        time.sleep(0.5)
            
    if stop_waypoint_mission:
        print('Takeoff and Waypoint mission stopped.')
        
    # Clean up the key monitor thread
    if l_key_monitor_thread.is_alive():
        l_key_monitor_thread.join()
        
    action_in_progress = False

    takeoff_completed = True

def get_state_i(id):
    
    ''' Get the current state of a drone '''
    ''' Outputs are converted to float for calculations '''
    # print("drone_id", id)
    # print(type(id))
    
    telemetry_data = w.getImageAndTelemetryData(id)
    
    if((len(telemetry_data)) > 2000000):
        telemetry_data = (bytearray(telemetry_data[3110408:]).decode())
    else:
        telemetry_data = (bytearray(telemetry_data[1382408:]).decode())
        
    data_elements = telemetry_data.split(":")
    
    drone_latitude = float(data_elements[0])
    drone_longitude = float(data_elements[1])
    drone_altitude = float(data_elements[2])
    drone_heading = float(data_elements[3])
    drone_gimbal_pitch = float(data_elements[4])
    drone_gimbal_yaw = float(data_elements[6])
    
    return drone_latitude, drone_longitude, drone_altitude, drone_heading, drone_gimbal_pitch, drone_gimbal_yaw # await is used to wait for the response from the server
              
def arrange_looking_direction(id, current_camera, old_vis_parameters):  
    
    global heading_vis, gimbal_pitch_vis, gimbal_yaw_vis, break_while, update_looking, drone_1_break_while, drone_2_break_while, drone_3_break_while, drone_4_break_while, drone_5_break_while, drone_6_break_while, drone_7_break_while, drone_8_break_while, drone_9_break_while, drone_10_break_while, drone_1_thread_stop, drone_2_thread_stop, drone_3_thread_stop, drone_4_thread_stop, drone_5_thread_stop, drone_6_thread_stop, drone_7_thread_stop, drone_8_thread_stop, drone_9_thread_stop, drone_10_thread_stop, update_looking_drone_1, update_looking_drone_2, update_looking_drone_3, update_looking_drone_4, update_looking_drone_5, update_looking_drone_6, update_looking_drone_7, update_looking_drone_8, update_looking_drone_9, update_looking_drone_10
    
    # with lock:
    #     break_while = False
        
    print(f'Update looking direction for drone {id}')
   
    task = 'update_camera_parameters'
    
    drone_latitude, drone_longitude, drone_altitude, drone_heading, drone_gimbal_pitch, drone_gimbal_yaw = get_state_i(id)
    
    drone_latitude = 'N/A'
    drone_longitude = 'N/A'
    
    drone_lenghtofstay = 0
    drone_speed = 0 
    drone_camera = current_camera
    thresh_waypoint = Way_threshold
    
    drone_parameter_mode = 0 
    
    drone_focal_length = [focal_length[id - 1]]
    drone_compass_correction = [compass_correction[id - 1]]
    drone_rx_threshold = [RX_threshold[id - 1]]
    drone_focal_plane_pitch = [focal_plane_pitch[id - 1]]
    drone_focal_plane_roll = [focal_plane_roll[id - 1]]
    
    drone_integration_window = [30]
    drone_minpose_distance = [0,5]
    
    new_drone_heading = heading_vis[id-1]
    new_drone_gimbal_pitch = gimbal_pitch_vis[id-1]
    new_drone_gimbal_yaw = gimbal_yaw_vis[id-1]
    
    new_parameters = [new_drone_heading, new_drone_gimbal_pitch, new_drone_gimbal_yaw]
    
    # print('new_parameters:', new_parameters)
    
    previous_parameters = old_vis_parameters[id-1]
    
    # print('previous_parameters:', previous_parameters)
    
    if new_parameters != previous_parameters:
        
        camera_looking_direction_thread = threading.Thread(target=globals()[f'waypoint_tread_drone{id}'], args=(task,
            [drone_latitude], [drone_longitude], [drone_altitude], [new_drone_heading], [drone_speed], thresh_waypoint, [drone_camera], [drone_lenghtofstay], [new_drone_gimbal_pitch], [new_drone_gimbal_yaw], drone_parameter_mode, drone_rx_threshold, drone_compass_correction, drone_focal_length, drone_focal_plane_pitch, drone_focal_plane_roll, drone_integration_window, drone_minpose_distance
        ))
        
        if globals()[f'drone_{id}_thread_stop'] == True or update_looking == True:
            print(f'drone_{id}_break_while, {globals()[f"drone_{id}_break_while"]}')
            with lock:
                globals()[f'drone_{id}_break_while'] = False
                
            print(f'drone_{id}_break_while, {globals()[f"drone_{id}_break_while"]}')
                
            camera_looking_direction_thread.start()
            camera_looking_direction_thread.join()
            
            if globals()[f'update_looking_drone_{id}'] == True:
                with lock:
                    update_looking = False         
                    
    else:
        pass
    
    previous_parameters = [new_drone_heading, new_drone_gimbal_pitch, new_drone_gimbal_yaw]
    
    old_vis_parameters[id-1] = previous_parameters
      
    return old_vis_parameters
         
# Arrange camera parameters
def arrange_camera_parameters(id, current_camera, old_parameters):
    global stop_waypoint_mission
    task = 'update_camera_parameters'
    with lock:
        stop_waypoint_mission = False

    # Get the current state of the drones
    drone_latitude, drone_longitude, drone_altitude, drone_heading, drone_gimbal_pitch, drone_gimbal_yaw = get_state_i(id)
    
    drone_latitude = 'N/A'
    drone_longitude = 'N/A'
    drone_heading = 'N/A'
    drone_gimbal_pitch = 'N/A'
    drone_gimbal_yaw = 'N/A'
    
    drone_lenghtofstay = 0
    drone_speed = 0 
    drone_camera = current_camera
    thresh_waypoint = Way_threshold

    drone_parameter_mode = 1
    
    drone_focal_length = [focal_length[id - 1]]
    drone_compass_correction = [compass_correction[id - 1]]
    drone_rx_threshold = [RX_threshold[id - 1]]
    drone_focal_plane_pitch = [focal_plane_pitch[id - 1]]
    drone_focal_plane_roll = [focal_plane_roll[id - 1]]
    
    drone_integration_window = [int(globals()[f'drone_{id}_waypoint_integration_window'][-1])]
    drone_minpose_distance = [float(globals()[f'drone_{id}_waypoint_minpose_distance'][-1])]

    new_parameters = [drone_rx_threshold[0], drone_compass_correction[0], drone_focal_length[0], drone_focal_plane_pitch[0], drone_focal_plane_roll[0]]

    previous_parameters = old_parameters[id-1]
    
    # print('previous_parameters:', previous_parameters)
    # print('new_parameters:', new_parameters)
    
    # check if all parameters are same as the current camera parameters and if not, update the parameters
    if new_parameters != previous_parameters:
        
        camera_update_thread = threading.Thread(target=globals()[f'waypoint_tread_drone{id}'], args=(task,
            [drone_latitude], [drone_longitude], [drone_altitude], [drone_heading], [drone_speed], thresh_waypoint, [drone_camera], [drone_lenghtofstay], [drone_gimbal_pitch], [drone_gimbal_yaw], drone_parameter_mode, drone_rx_threshold, drone_compass_correction, drone_focal_length, drone_focal_plane_pitch, drone_focal_plane_roll, drone_integration_window, drone_minpose_distance
        ))
                
        camera_update_thread.start()
        camera_update_thread.join()
    
    else:
        pass
    
    previous_parameters = [drone_rx_threshold[0], drone_compass_correction[0], drone_focal_length[0], drone_focal_plane_pitch[0], drone_focal_plane_roll[0]]
    
    old_parameters[id-1] = previous_parameters
    # print('old_parameters:', old_parameters)
    return old_parameters

# Listener for 16th element of the telemetry data
def listener_telemetry_data():
    global listen_16th_element, last_latitudes, last_longitudes
    # Dictionary to store the previous flight mode for each drone
    previous_modes = {1: 3.0, 2: 3.0, 3: 3.0, 4: 3.0, 5: 3.0, 6: 3.0, 7: 3.0, 8: 3.0, 9: 3.0, 10: 3.0}
    error = []
    
    while listen_16th_element != True:
        global drone_1_incrementor, drone_2_incrementor, drone_3_incrementor, drone_4_incrementor, drone_5_incrementor, drone_6_incrementor, drone_7_incrementor, drone_8_incrementor, drone_9_incrementor, drone_10_incrementor, move_drones, stop_waypoint_mission

        for id in connected_drones:
            # print('id', id)
            try:
                drone_Image_Telemetry_data = w.getImageAndTelemetryData(id)
                if((len(drone_Image_Telemetry_data)) > 2000000):
                    drone_Telemetry_data = (bytearray(drone_Image_Telemetry_data[3110408:]).decode())
                else:
                    drone_Telemetry_data = (bytearray(drone_Image_Telemetry_data[1382408:]).decode())
                
                #drone_Telemetry_data = (bytearray(drone_Image_Telemetry_data[3110408:]).decode())
                drone_elements = drone_Telemetry_data.split(":")  # Extract all elements from the string.
                data_16 = drone_elements[16]
                
                latitude = drone_elements[0]
                longitude = drone_elements[1]
                
                # add the current latitude and longitude to the last_latitudes and last_longitudes lists based on the drone id
                with lock:
                    last_latitudes[id-1] = latitude
                    last_longitudes[id-1] = longitude
                current_mode = float(data_16)
                if debug:
                    print(f"Drone {id} current mode: {current_mode}")
                    print(f"Drone {id} incrementor: {globals()[f'drone_{id}_incrementor']}")
                    
                if id not in previous_modes or current_mode != previous_modes[id]:
                    # print(f"Drone {id} mode changed to {current_mode}.")
                    if current_mode == 0.0:  # Manual flight mode
                        print(f"Drone {id} switched to manual flight mode.")
       
                    elif current_mode == 1.0:  # Auto flight mode
                        print(f"Drone {id} switched to auto flight mode.")
                        
                    else:
                        print(f"Drone {id} switched to unknown flight mode.")
                    
                    # Update the previous mode
                    previous_modes[id] = current_mode
                
                else:
                    if debug:
                        print(f"Drone {id} mode unchanged.")
                        
            except Exception as e:
                er = f"Error in listener_telemetry_data: {e}"
                error.append(er)
                if er != error[-1] or len(error) == 0:
                    print(er)
                pass
            
        time.sleep(0.5)
       
class KeyStateTracker:
    def __init__(self):
        self.pressed = False
        self.last_press_time = 0

    def on_press(self, _):
        current_time = time.time()
        if current_time - self.last_press_time > 0.01:  # Debounce time of 0.5 seconds
            self.pressed = True
            self.last_press_time = current_time

    def on_release(self, _):
        self.pressed = False

    def is_pressed(self):
        return self.pressed

    def reset(self):
        self.pressed = False
        self.last_press_time = 0

# Initialize KeyStateTrackers for each key
key_trackers = {
    'q': KeyStateTracker(),
    't': KeyStateTracker(),
    'l': KeyStateTracker(),
    'p': KeyStateTracker()
}

# Set up keyboard listeners
for key, tracker in key_trackers.items():
    keyboard.on_press_key(key, tracker.on_press)
    keyboard.on_release_key(key, tracker.on_release)

# Function to monitor 'L' key during waypoint mission
def monitor_l_key():
    global stop_waypoint_mission, action_in_progress, land_command, break_while
    while not stop_waypoint_mission:
        if key_trackers['l'].is_pressed():
            print("Key 'l' pressed! Stopping Waypoint Mission.")
            with lock:
                stop_waypoint_mission = True
                land_command = True   
                break_while = True
            break
        time.sleep(0.01)

# Function to monitor 'u' key to arrange camera parameters
def monitor_u_key():
    global stop_waypoint_mission, u_key, stop_u_listener, key_p, camera_drone_id, camera, old_parameters, u_action, takeoff_completed, run_apart
    
    while not stop_u_listener:
        if not u_action and key_trackers['u'].is_pressed():
            
            if not key_pressed_emergency['u']:
                key_pressed_emergency['u'] = True
                print("Key 'u' pressed! Arranging camera parameters.")
                with lock:
                    u_key = True
                    u_action = True
                    stop_waypoint_mission = True
                
                p_key_monitor_thread = threading.Thread(target=monitor_p_key)
                p_key_monitor_thread.daemon = True
                p_key_monitor_thread.start()
                
                while True:
                    if takeoff_completed:
                        old_parameters = arrange_camera_parameters(camera_drone_id, camera[camera_drone_id-1], old_parameters)
                    if run_apart:
                        old_parameters = arrange_camera_parameters(camera_drone_id, camera[camera_drone_id-1], old_parameters)
                    if key_p:
                        break
                    time.sleep(0.01)
                
                if p_key_monitor_thread.is_alive():
                    p_key_monitor_thread.join()
                
                with lock:
                    key_p = False
                    u_action = False
                key_trackers['u'].reset()
            else:
                key_pressed_emergency['u'] = False
        
        time.sleep(0.01)  # Small delay to prevent excessive CPU usage

def monitor_p_key():
    global key_p, camera_drone_id
    while not key_p:
        if key_trackers['p'].is_pressed():
            print("Key 'p' pressed! Camera parameters arranged.\n")
            print(f"You can continue to the flight for drone{camera_drone_id}.")
            with lock:
                key_p = True  
            key_trackers['p'].reset()
            break
        time.sleep(0.01)
               
def monitor_update_camera_looking():
    global update_looking, old_vis_parameters, arrange_looking_direction_thread_stop, camera_drone_id, camera
    while not arrange_looking_direction_thread_stop:
        if update_looking == True:
            print('update_looking03:', update_looking)
            old_vis_parameters = arrange_looking_direction(camera_drone_id, camera[camera_drone_id-1], old_vis_parameters)
        else:
            pass
        
        time.sleep(0.1)
        
server_address = ('', 8000)
httpd1 = HTTPServer(server_address, DroneDataHandler)

# Run the HTTP server in its own thread
server_thread = threading.Thread(target=httpd1.serve_forever)
server_thread.daemon = True
server_thread.start()
print('Server started')

# Start data processing in a separate thread
data_thread = threading.Thread(target=process_data)
data_thread.daemon = True
data_thread.start()
 
# Start the listener thread for telemetry data to monitor the 16th element
listener_thread = threading.Thread(target=listener_telemetry_data)
listener_thread.daemon = True
listener_thread.start()   

# Start the key monitor u key thread
u_key_monitor_thread = threading.Thread(target=monitor_u_key)
u_key_monitor_thread.daemon = True
u_key_monitor_thread.start() 

# Start camera looking direction thread
arrange_looking_direction_thread = threading.Thread(target=monitor_update_camera_looking)
arrange_looking_direction_thread.daemon = True # daemon is set to True to stop the thread when the main program ends
arrange_looking_direction_thread.start()

try:
    while True:  # Keep looping to call the threads again
        
        # Section for takeoff and waypoint
        if not action_in_progress and key_trackers['t'].is_pressed():
            action_in_progress = True
            run_apart = False
            reset_for_new_mission()
            execute_waypoint_mission()
            print('Action completed for key t'+'\n')
            action_in_progress = False
            key_trackers['t'].reset()

        # Section for landing
        if not action_in_progress and (key_trackers['l'].is_pressed() or land_command):
            action_in_progress = True
            land_command = False
            with lock:
                stop_waypoint_mission = True
                waypoint_status = 0
            execute_landing_procedure()
            print('Action completed for key l'+'\n')
            action_in_progress = False
            landing_completed = True
            key_trackers['l'].reset()

        time.sleep(0.01)  # Small delay to prevent excessive CPU usage

except KeyboardInterrupt:
    print("Keyboard interrupt detected. Cleaning up...")

finally:
    # Clean up
    stop_u_listener = True
    listen_16th_element = True
    listener_thread.join()
    u_key_monitor_thread.join()
    keyboard.unhook_all()
    stop_server = True
    httpd1.shutdown()  # Stop the HTTP server
    data_thread.join()
    server_thread.join()  # Wait for the server thread to close
    with lock:
        arrange_looking_direction_thread_stop = True
    with lock:
        stop_mqtt = True
        listen_16th_element = True
    thread_data_streaming.join()
    arrange_looking_direction_thread.join()
    print("Program has ended")
