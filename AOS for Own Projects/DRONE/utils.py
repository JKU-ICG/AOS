import time
import shutil
import os
import glob
import numpy as np
import math
import json
import cv2
import utm
import math
from PIL import Image
import logging
#New Changes to send Email
import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import asyncio
import aiohttp
import aiofiles

#TODo:- Do Dense and Coarse Planning similarily using this function -- independent of compass 
def GenerateGPSGridInfo(CenterUTMCoordinates, DEMCenterUTMInfo,GridSideLength, AreaSideLength, AreaSideWidth, RotationAngle = 0):
    RotationAngle = -RotationAngle
    NoofUnitsinLength = int (AreaSideLength / GridSideLength) 
    NoofUnitsinWidth = int (AreaSideWidth / GridSideLength) 
    print('NoofUnitsinLength',NoofUnitsinLength , NoofUnitsinWidth)
    LengthRangePointList = [*range (-int(math.ceil(NoofUnitsinLength/2)),int(NoofUnitsinLength/2)+1,1)]
    WidthRangePointList = [*range (-int(math.ceil(NoofUnitsinWidth/2)),int(NoofUnitsinWidth/2)+1,1)]
    print('LengthList',LengthRangePointList)
    print('WidthList',WidthRangePointList)
    print('Length',len(LengthRangePointList) , len(WidthRangePointList))
    GPSCenterPoints = np.zeros((len(LengthRangePointList)-1,len(WidthRangePointList)-1,2))
    GPSPoints = np.zeros((len(LengthRangePointList),len(WidthRangePointList),2))

    CenterUTMEast = CenterUTMCoordinates[0] - DEMCenterUTMInfo[0]
    CenterUTMNorth = DEMCenterUTMInfo[1] - CenterUTMCoordinates[1]
    CountH = -1
    CountCH = -1
    for GPH in range (-int(math.ceil(NoofUnitsinLength/2)),int(NoofUnitsinLength/2)+1,1):
        BaseEast = CenterUTMEast + (GPH * GridSideLength * np.cos(np.deg2rad(RotationAngle)))
        BaseNorth = CenterUTMNorth + (GPH * GridSideLength * np.sin(np.deg2rad(RotationAngle)))
        CountH = CountH + 1
        print('GPH',GPH, CountH)
        CountV = -1
        CountCV = -1
        CountCH = CountCH +1
        print(CountCH)
        for GPV in range (-int(math.ceil(NoofUnitsinWidth/2)),int(NoofUnitsinWidth/2)+1,1):
            PointEast = BaseEast + (GPV * GridSideLength * np.sin(np.deg2rad(-RotationAngle)))
            PointNorth = BaseNorth + (GPV * GridSideLength * np.cos(np.deg2rad(-RotationAngle)))
            if GPV <= 0:
                CenterPointEast = PointEast + ((GridSideLength / math.sqrt(2)) * np.sin(np.deg2rad(-RotationAngle + 45)))
                CenterPointNorth= PointNorth + ((GridSideLength / math.sqrt(2)) * np.cos(np.deg2rad(-RotationAngle + 45)))
            else:
                CenterPointEast = PointEast + ((GridSideLength / math.sqrt(2)) * np.cos(np.deg2rad(RotationAngle + 45)))
                CenterPointNorth= PointNorth + ((GridSideLength / math.sqrt(2)) * np.sin(np.deg2rad(RotationAngle + 45)))
            CountV = CountV + 1
            CountCV = CountCV +1
            print(CountCV)
            EastPoint = PointEast + DEMCenterUTMInfo[0]
            NorthPoint = DEMCenterUTMInfo[1] - PointNorth
            CenterEastPoint = CenterPointEast + DEMCenterUTMInfo[0]
            CenterNorthPoint = DEMCenterUTMInfo[1] - CenterPointNorth
            Lat,Lon = utm.to_latlon(EastPoint, NorthPoint,CenterUTMCoordinates[2], CenterUTMCoordinates[3])
            CenterLat,CenterLon = utm.to_latlon(CenterEastPoint, CenterNorthPoint,CenterUTMCoordinates[2], CenterUTMCoordinates[3])
            GPSPoints[CountH,CountV,0] = Lat
            GPSPoints[CountH,CountV,1] = Lon
            if GPH != int(NoofUnitsinLength/2):
                if GPV != int(NoofUnitsinLength/2):
                    GPSCenterPoints[CountCH,CountCV,0] = CenterLat
                    GPSCenterPoints[CountCH,CountCV,1] = CenterLon

    '''
    #Generate Grid of Points
    EastGridPoints = np.array([*range(int(-AreaSideLength/2),int(AreaSideLength/2)+1, GridSideLength)])
    NorthGridPoints = np.array( [*range(int(-AreaSideWidth/2),int(AreaSideWidth/2)+1, GridSideLength)])
    print(EastGridPoints)
    print(NorthGridPoints)
    print(CenterUTMCoordinates[0])
    print(CenterUTMCoordinates[1])
    EastCoordinates = CenterUTMCoordinates[0] + EastGridPoints
    NorthCoordinates = CenterUTMCoordinates[1] + NorthGridPoints
    EastCoordinatesCentered = EastCoordinates - MeanEast
    NorthCoordinatesCentered = MeanNorth - NorthCoordinates
    GridPoints = np.zeros((len(EastCoordinatesCentered),len(NorthCoordinatesCentered),2))
    GPSPoints = np.zeros((len(EastCoordinatesCentered),len(NorthCoordinatesCentered),2))
    for E in range(len(EastCoordinatesCentered)):
        for N in range(len(NorthCoordinatesCentered)):
            print(EastCoordinatesCentered[E],NorthCoordinatesCentered[N])
            print('Finding Distance to')
            LocIndex, Distance = determine_Location_inView(dem_info,EastCoordinatesCentered[E],NorthCoordinatesCentered[N])
            print(len(Distance))
            if len(Distance) == 1 :
                if all(Distance < 1.0):
                        print(LocIndex[:])
                        print('Location of Nearest')
                        GridPoints[E,N,:] = LocIndex[:]
                        EastPoint = dem_info[LocIndex[0],LocIndex[1],0] + MeanEast
                        NorthPoint = MeanNorth - dem_info[LocIndex[0],LocIndex[1],1]
                        Lat,Lon = utm.to_latlon(EastPoint, NorthPoint,CenterUTMCoordinates[2], CenterUTMCoordinates[3])
                        GPSPoints[E,N,0] = Lat
                        GPSPoints[E,N,0] = Lon
            else :
                if all(Distance < 1.0):
                    print(LocIndex)
                    Row = LocIndex[0]
                    Col = LocIndex[1]
                    print('Location of Nearest')
                    GridPoints[E,N,0] = Row[0]
                    GridPoints[E,N,1] = Col[0]
                    EastPoint = dem_info[Row[0],Col[0],0] + MeanEast
                    NorthPoint = MeanNorth - dem_info[Row[0],Col[0],1]
                    Lat,Lon = utm.to_latlon(EastPoint, NorthPoint,CenterUTMCoordinates[2], CenterUTMCoordinates[3])
                    GPSPoints[E,N,0] = Lat
                    GPSPoints[E,N,0] = Lon
    '''
    return GPSPoints,GPSCenterPoints
##############################################################################        
def ReadandUpdateWaypointList(NoofPoints,Rwp):
    WayPointIndex = 1
    WayPointlist = []
    WayPointFlyingPathIndexList = []
    for x in range(NoofPoints):
        Data = Rwp.readline()   
        x = Data.split(" ")
        ReadLatitude = int(x[0])
        ReadLongitude = int(x[1])
        ReadAltitude =  int(x[2])
        #CalibrationWayPoint = x[3]
        if x[3] == 'True' :
            CalibrationWayPoint = True
        elif x[3] == 'False' :
            CalibrationWayPoint = False
        y = x[4].split("\n")
        if y[0] == 'True' :
            StopFlag = True
        elif y[0] == 'False' :
            StopFlag = False
        print('Lat , Long ,  Alt, CalibrationWaypoint,StopFlag ',ReadLatitude,ReadLongitude,ReadAltitude, CalibrationWayPoint, StopFlag)
        WayPointlist.append( WayPointInfoCheck(ReadLatitude, ReadLongitude,ReadAltitude, CalibrationWayPoint, StopFlag) )
        WayPointFlyingPathIndexList.append(WayPointIndex)
        WayPointIndex = WayPointIndex + 1
    return WayPointlist, WayPointFlyingPathIndexList
##############################################################################
##############################################################################
# Calculates Rotation Matrix given euler angles.
def eulerAnglesToRotationMatrix(theta) :
    
    R_x = np.array([[1,         0,                  0                   ],
                    [0,         math.cos(theta[0]), -math.sin(theta[0]) ],
                    [0,         math.sin(theta[0]), math.cos(theta[0])  ]
                    ])
        
        
                    
    R_y = np.array([[math.cos(theta[1]),    0,      math.sin(theta[1])  ],
                    [0,                     1,      0                   ],
                    [-math.sin(theta[1]),   0,      math.cos(theta[1])  ]
                    ])
                
    R_z = np.array([[math.cos(theta[2]),    -math.sin(theta[2]),    0],
                    [math.sin(theta[2]),    math.cos(theta[2]),     0],
                    [0,                     0,                      1]
                    ])
                    
                    
    R = np.dot(R_z, np.dot( R_y, R_x ))

    return R

def eul2rotm(theta) :
    s_1 = math.sin(theta[0])
    c_1 = math.cos(theta[0]) 
    s_2 = math.sin(theta[1]) 
    c_2 = math.cos(theta[1]) 
    s_3 = math.sin(theta[2]) 
    c_3 = math.cos(theta[2])
    rotm = np.identity(3)
    rotm[0,0] =  c_1*c_2
    rotm[0,1] =  c_1*s_2*s_3 - s_1*c_3
    rotm[0,2] =  c_1*s_2*c_3 + s_1*s_3

    rotm[1,0] =  s_1*c_2
    rotm[1,1] =  s_1*s_2*s_3 + c_1*c_3
    rotm[1,2] =  s_1*s_2*c_3 - c_1*s_3

    rotm[2,0] = -s_2
    rotm[2,1] =  c_2*s_3
    rotm[2,2] =  c_2*c_3        

    return rotm

# Checks if a matrix is a valid rotation matrix.
def isRotationMatrix(R) :
    Rt = np.transpose(R)
    shouldBeIdentity = np.dot(Rt, R)
    I = np.identity(3, dtype = R.dtype)
    n = np.linalg.norm(I - shouldBeIdentity)
    return n < 1e-6


# Calculates rotation matrix to euler angles
# The result is the same as MATLAB except the order
# of the euler angles ( x and z are swapped ).
def rotationMatrixToEulerAngles(R) :

    assert(isRotationMatrix(R))
    
    sy = math.sqrt(R[0,0] * R[0,0] +  R[1,0] * R[1,0])
    
    singular = sy < 1e-6

    if  not singular :
        x = math.atan2(R[2,1] , R[2,2])
        y = math.atan2(-R[2,0], sy)
        z = math.atan2(R[1,0], R[0,0])
    else :
        x = math.atan2(-R[1,2], R[1,1])
        y = math.atan2(-R[2,0], sy)
        z = 0

    return np.array([x, y, z])
##############################################################################
##############################################################################
def createviewmateuler(eulerang, camLocation):
    #rotationmat = eulerAnglesToRotationMatrix(eulerang)
    rotationmat = eul2rotm(eulerang)
    #print(rotationmat)
    translVec =  np.reshape((-camLocation @ rotationmat),(3,1))
    #print(translVec)
    conjoinedmat = (np.append(np.transpose(rotationmat), translVec, axis=1))
    #viewMatrix = (np.vstack( (conjoinedmat, np.array([0,0,0,1]))))
    #print(conjoinedmat)
    return conjoinedmat
    
    #viewMatrix[4,4] = 1.0
#createviewmateuler(np.array([math.radians(266.646+6), 0,0]), np.array([-2.5781693845638074,-4.117117996327579,-28.15]))
'''
def CreateJsonPoseFile(EastCenteredList, NorthCenteredList, AltitudeList, CompassHeadingList, ImageList, basefolder, FileName):
    thermal_imagesdict={}
    thermal_imagesList =[]
    for i in range (0,len(EastCenteredList)):
        thermal_imagesdict['imagefile'] = ImageList[i]
        #print(ImageList[i])
        #M = createviewmateuler(np.array([0,0,math.radians(CompassHeadingList[i])]),np.array( [EastCenteredList[i],NorthCenteredList[i],AltitudeList[i]]) )
        M = createviewmateuler(np.array([math.radians(CompassHeadingList[i]), 0,0]),np.array( [EastCenteredList[i],NorthCenteredList[i],AltitudeList[i]]) )
        #print(M)
        thermal_imagesdict['M3x4'] = M.tolist()
        thermal_imagesList.append(thermal_imagesdict)
        thermal_imagesdict={}
    thermal = {}
    thermal['images'] = thermal_imagesList
    with open(os.path.join(basefolder,FileName), 'w') as json_file:
        json.dump(thermal, json_file)
    
#BaseFolder = 'D:\\RESILIO\\NAOS_DATA\\SITES\\TS20200207F2\\LFR'
#FileName = 'Test.json'
#CreateJsonPoseFile([-2.5781693845638074], [-4.117117996327579], [-28.15], [266.64+6#], ['20200207_124519.tiff'], BaseFolder, FileName)
'''
def CreateJsonPoseFile(EastCenteredList, NorthCenteredList, AltitudeList, CompassHeadingList, ImageList, basefolder, FileName, startHeight):
    thermal_imagesdict={}
    thermal_imagesList =[]
    CompassArray = np.array(CompassHeadingList)
    MeanCompass = CompassArray[CompassArray!=0].mean()
    CompassRad = math.radians((MeanCompass*2))
    AltitudeArray = np.array(AltitudeList)
    MeanAltitude = AltitudeArray[AltitudeArray!=0].mean()
    for i in range (0,len(EastCenteredList)):
        thermal_imagesdict['imagefile'] = ImageList[i]
        #print(ImageList[i])
        #M = createviewmateuler(np.array([0,0,math.radians(CompassHeadingList[i])]),np.array( [EastCenteredList[i],NorthCenteredList[i],AltitudeList[i]]) )
        #M = createviewmateuler(np.array([math.radians(CompassHeadingList[i]), 0,0]),np.array( [EastCenteredList[i],NorthCenteredList[i],AltitudeList[i]]) )
        if AltitudeList[i] == 0.0:
            Altitude = -((MeanAltitude+startHeight))
        else:
            Altitude = -((AltitudeList[i]+startHeight))
        M = createviewmateuler(np.array([math.radians(CompassRad), 0,0]),np.array( [EastCenteredList[i],NorthCenteredList[i],Altitude]) )
        #M = createviewmateuler(np.array([math.radians(8.0), 0,0]),np.array( [EastCenteredList[i],NorthCenteredList[i],AltitudeList[i]]) )
        #print(math.radians(CompassHeadingList[i]),EastCenteredList[i],NorthCenteredList[i],AltitudeList[i] )
        #print(M)
        thermal_imagesdict['M3x4'] = M.tolist()
        thermal_imagesList.append(thermal_imagesdict)
        thermal_imagesdict={}
    thermal = {}
    thermal['images'] = thermal_imagesList
    with open(os.path.join(basefolder,FileName), 'w') as json_file:
        json.dump(thermal, json_file)
    
#BaseFolder = 'D:\\RESILIO\\NAOS_DATA\\SITES\\TS20200207F2\\LFR'
#FileName = 'Test.json'
#CreateJsonPoseFile([-2.5781693845638074], [-4.117117996327579], [-28.15], [266.64+6#], ['20200207_124519.tiff'], BaseFolder, FileName)

def FindStartingHeight(DemFileName, StartCenteredEastUTM, StartCenteredNorthUTM):
    MinDistance = 1000000
    MinimumStartingHeigth = 0
    Count = 2
    Index = 0
    with open(DemFileName) as DemFile: 
        print('Opening LogFile')
        Line = DemFile.readline() 
        while True: 
            Line = DemFile.readline() 
            if not Line: 
                break
            CheckVertex = Line.split(' ')
            #print(CheckVertex)
            if 'v' in CheckVertex:
                VertexEast = float(CheckVertex[1])
                VertexNorth = float(CheckVertex[2])
                Height = -(float(CheckVertex[3]))
                UTMDistance = math.sqrt(((StartCenteredEastUTM - VertexEast) * (StartCenteredEastUTM - VertexEast)) + ((StartCenteredNorthUTM - VertexNorth) * (StartCenteredNorthUTM - VertexNorth)))
                if (UTMDistance < MinDistance) :
                    MinDistance = UTMDistance
                    MinimumStartingHeigth = Height
                    Index = Count
            else :
                break
            Count = Count + 1
    return MinimumStartingHeigth,Index
##############################################################################
##############################################################################        
def haversine(lat1, lon1, lat2, lon2):
    R = 6372800  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2) 
    dphi       = math.radians(lat2 - lat1)
    dlambda    = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    
    return 2*R*math.atan2(math.sqrt(a), math.sqrt(1 - a))

##############################################################################
###################### Multiple Logging Files Setup ##########################
def setup_logger(name, log_file, level=logging.DEBUG):
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    logging.basicConfig(level=logging.DEBUG)
    """To setup as many loggers as you want"""
    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger
##############################################################################
##############################################################################

def read_dem(DemFileName):
    Count = 0
    dem_pts = np.zeros(shape=(3,0))
    with open(DemFileName) as DemFile: 
        Line = DemFile.readline() 
        while True: 
            Line = DemFile.readline() 
            if not Line: 
                break
            CheckVertex = Line.split(' ')
            #print(CheckVertex)
            if 'v' in CheckVertex:
                VertexEast = float(CheckVertex[1])
                VertexNorth = float(CheckVertex[2])
                Height = -(float(CheckVertex[3]))
                #UTMDistance = math.sqrt(((StartCenteredEastUTM - VertexEast) * (StartCenteredEastUTM - VertexEast)) + ((StartCenteredNorthUTM - VertexNorth) * (StartCenteredNorthUTM - VertexNorth)))
                #if (UTMDistance < MinDistance) :
                #    MinDistance = UTMDistance
                #    MinimumStartingHeigth = Height
                #    Index = Count
                dem_pts = np.column_stack( (dem_pts,[VertexEast,VertexNorth,Height]) )
            else :
                break
            Count = Count + 1
    return dem_pts

def determine_Location_inView(demArray, XCoord,YCoord):
    X = np.sqrt( np.square( demArray[:,:,0] -  XCoord) +  np.square( demArray[:,:,1] -  YCoord) )
    X[demArray[:,:,2] == 0.0] = X.max()
    idx = np.where( X == X.min() )
    print('Distance to')
    print(X[idx[0],idx[1]])
    print(idx[0],idx[1])
    print(demArray[idx[0],idx[1],:])
    return idx,X[idx[0],idx[1]]

def ReadInterpolatedGPSlogFiles(GPSLogfileName):
    GPSInterpolatedLogFile = open(GPSLogfileName, 'r')
    Lines = GPSInterpolatedLogFile.readlines()
    count = 0
    InterpolatedLatititude = []
    InterpolatedLongitude = []
    InterpolatedAltitude = []
    InterpolatedCompass = []
    InterpolatedTargetHoldTime = []
    # Strips the newline character
    for line in Lines:
        LineDetails  = line.strip().split(' ')
        if not LineDetails[3] == 'No' :
            InterpolatedLatititude.append(float(LineDetails[3]))
            InterpolatedLongitude.append(float(LineDetails[4]))
            InterpolatedAltitude.append(float(LineDetails[5]))
            InterpolatedCompass.append(float(LineDetails[6]))
            InterpolatedTargetHoldTime.append(float(LineDetails[7]))
            count += 1
    return InterpolatedLatititude, InterpolatedLongitude, InterpolatedAltitude, InterpolatedCompass, InterpolatedTargetHoldTime

##############################################################################
#New Changes to send Email
def CreateText(sender_email, receiver_email, subject, body, ImageName) :
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    filename = ImageName  # In same directory as script

    # Open PDF file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email    
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()
    return text

def smtp_connect(sender_email):
    password = os.getenv('EmailPass')
    print(password)
    context = ssl.create_default_context()
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
    server.login(sender_email, password)
    return server

async def upload_png_file(session, serveraddres,image_ref, file):
    #print("Uploading to " + str(image_ref) + " file " + str(file))
    with open(file, 'rb') as f:
        async with session.request(
                "put", serveraddres + image_ref + ".png",
                data=f,
                headers={"content-type": "image/png"},  # mime type is very relevant
        ) as resp:
            await resp.read()
            assert 201 == resp.status
            return resp.headers["Location"]  # this one is needed for linking with the metadata

async def upload_file(session, resource, file, mime=None):
    #print("Uploading to " + str(resource) + " file " + str(file))
    headers = {}
    if mime:
        headers['content-type'] = str(mime)

    with open(file, 'rb') as f:
        async with session.request(
                "put", resource,
                data=f,
                headers=headers
        ) as resp:
            await resp.read()
            resp.raise_for_status()
            print(resp.headers["Location"])
            return resp.headers["Location"]

#Indrajit Test
async def upload_png_file_data(session, resources, dataup):
    #print("Uploading to " + str(resources) )
    async with session.request(
                "put", resources + ".png",
                data=dataup,
                headers={"content-type": "image/png"},  # mime type is very relevant
        ) as resp:
            await resp.read()
            assert 201 == resp.status
            return resp.headers["Location"]  # this one is needed for linking with the metadata

def upload_png_file_data_was(session, resources, dataup):
    #print("Uploading to " + str(resources) )
    with session.request(
                "put", resources + ".png",
                data=dataup,
                headers={"content-type": "image/png"},  # mime type is very relevant
        ) as resp:
            resp.read()
            assert 201 == resp.status
            return resp.headers["Location"]  # this one is needed for linking with the metadata
'''
async def upload_json(session, resource, data):
    async with session.request(
            "post", resource,
            data=data,
            headers={"content-type": "application/json"}
    ) as resp:
        await resp.read()

        resp.raise_for_status()
        location = resp.headers["Location"]
        print("Metadata created for " + resource + " at " + location)
        return location



async def create_image_meta(session, resources, data) -> str:
    return await upload_json(session, resources, data)
'''
async def upload_json(session, resource, data):
    #print('url',resource)
    async with session.request(
            "post", resource,
            data=data,
            headers={"content-type": "application/json"}
    ) as resp:
        await resp.read()

        resp.raise_for_status()
        location = resp.headers["Location"]
        #print("Metadata created for " + resource + " at " + location)
        return location

def upload_json_was(session, resource, data):
    #print('url',resource)
    with session.request(
            "post", resource,
            data=data,
            headers={"content-type": "application/json"}
    ) as resp:
        resp.read()

        resp.raise_for_status()
        location = resp.headers["Location"]
        #print("Metadata created for " + resource + " at " + location)
        return location


async def create_image_meta(session, resources, data) -> str:
    return await upload_json(session, resources, data)

def create_image_meta_was(session, resources, data) -> str:
    return upload_json_was(session, resources, data)


async def download_file(serveraddress, resources, local_file,remote_file):
    async with aiohttp.ClientSession() as session:
        #print("Downloading to " + str(local_file) + "from file " + str(remote_file))
        async with session.request("get", os.path.join(serveraddress,resources,remote_file).replace("\\","/"),params=None) as resp:
            assert resp.status == 200
            data = await resp.read()
            async with aiofiles.open(local_file, "wb") as outfile:
                await outfile.write(data)

async def create_dummylocation_id(serveraddress, locationid):
    async with aiohttp.ClientSession() as session:
        # Store metadata of the one drone used in the demo data
        # Provides camera details - may allow to integrate over images provided by drones with different
        # camera settings, no magic numbers in the viewer code.
        async with session.request(
                "put", serveraddress + '/drones/drone1',
                data=json.dumps({
                    "camera": {"fov": {"Deg": 50.815436217896945}, "near": 0.1, "far": 100.0, "aspect": 1.0,
                               "resolution": [512, 512]}}),
                headers={"content-type": "application/json"}
        ) as resp:
            #print(str(resp))
            #print(await resp.text())
            assert 201 == resp.status

        location_id = locationid
        # Store our main location metadata
        async with session.request(
                "put", serveraddress + "/locations/" + location_id,
                data=json.dumps({
                    "start_height": 307.0020751953125,
                    "start_lat_lon": [48.339758, 14.33059],
                    "center_lat_lon": [48.3398054625, 14.3318629125],
                    "start_utm": [450393.91024515807, 5354280.539372292, 33, "U"],
                    "start_gkm31": [73989.71284555788, 356206.4560305681],
                    "center_gkm31": [74084.00932285623, 356212.9582170388],
                    "center_utm": [450488.28387294046, 5354284.992294418, 33, "U"]
                }),
                headers={"content-type": "application/json"}
        ) as resp:
            await resp.read()
            #print(str(resp))
            resp.raise_for_status()
            location_ref = resp.headers["Location"]

def create_dummylocation_id_was(serveraddress, locationid):
    with aiohttp.ClientSession() as session:
        # Store metadata of the one drone used in the demo data
        # Provides camera details - may allow to integrate over images provided by drones with different
        # camera settings, no magic numbers in the viewer code.
        with session.request(
                "put", serveraddress + '/drones/drone1',
                data=json.dumps({
                    "camera": {"fov": {"Deg": 50.815436217896945}, "near": 0.1, "far": 100.0, "aspect": 1.0,
                               "resolution": [512, 512]}}),
                headers={"content-type": "application/json"}
        ) as resp:
            #print(str(resp))
            #print(resp.text())
            assert 201 == resp.status

        location_id = locationid
        # Store our main location metadata
        with session.request(
                "put", serveraddress + "/locations/" + location_id,
                data=json.dumps({
                    "start_height": 307.0020751953125,
                    "start_lat_lon": [48.339758, 14.33059],
                    "center_lat_lon": [48.3398054625, 14.3318629125],
                    "start_utm": [450393.91024515807, 5354280.539372292, 33, "U"],
                    "start_gkm31": [73989.71284555788, 356206.4560305681],
                    "center_gkm31": [74084.00932285623, 356212.9582170388],
                    "center_utm": [450488.28387294046, 5354284.992294418, 33, "U"]
                }),
                headers={"content-type": "application/json"}
        ) as resp:
            resp.read()
            #print(str(resp))
            resp.raise_for_status()
            location_ref = resp.headers["Location"]

async def upload_dummylocation_id_was(session, serveraddress, locationid):
    async with session.request(
            "put", serveraddress + '/drones/drone1',
            data=json.dumps({
                "camera": {"fov": {"Deg": 50.815436217896945}, "near": 0.1, "far": 100.0, "aspect": 1.0,
                            "resolution": [512, 512]}}),
            headers={"content-type": "application/json"}
    ) as resp:
        #print(str(resp))
        #print(resp.text())
        assert 201 == resp.status

    location_id = locationid
    # Store our main location metadata
    async with session.request(
            "put", serveraddress + "/locations/" + location_id,
            data=json.dumps({
                "start_height": 307.0020751953125,
                "start_lat_lon": [48.335673, 14.32703],
                "center_lat_lon": [48.3356687, 14.3262629],
                "start_utm": [450126.11627760687, 5353828.794316645, 33, "U"],
                "start_gkm31": [73731.66832550615, 355748.8056906797],
                "center_gkm31": [73674.80240903652, 355747.59297018684],
                "center_utm": [450069.2625109379, 5353828.815501057, 33, "U"]
            }),
            headers={"content-type": "application/json"}
    ) as resp:
        await resp.read()
        #print(str(resp))
        resp.raise_for_status()
        location_ref = resp.headers["Location"]

async def upload_images(serveraddress, undstortedimage, generatedviewmatrix, locationid, poses = None):
    async with aiohttp.ClientSession() as session:            
        if poses is not None:
            resources = "/integrals"
            data = {
                    "drone_id": "drone1",
                    "location_id": locationid,
                    "m3x4": generatedviewmatrix.tolist(),
                    "source_images": poses,

                }
        else :
            resources = "/images"
            data = {
                    "location_id": locationid,
                    "drone_id": "drone1",
                    "m3x4": generatedviewmatrix.tolist()
                }
        #print(data)    
        image_ref = await create_image_meta(session,serveraddress + resources,json.dumps(data))
        is_success,img_encoded = cv2.imencode('.png', undstortedimage)
        image_location = await upload_png_file_data(session, serveraddress + image_ref,img_encoded.tobytes())
        return image_ref

async def upload_images_was(session, serveraddress, undstortedimage, generatedviewmatrix, locationid, poses = None):           
    if poses is not None:
        resources = "/integrals"
        data = {
                "drone_id": "drone1",
                "location_id": locationid,
                "m3x4": generatedviewmatrix.tolist(),
                "source_images": poses,

            }
    else :
        resources = "/images"
        data = {
                "location_id": locationid,
                "drone_id": "drone1",
                "m3x4": generatedviewmatrix.tolist()
            }
    #print(data)    
    image_ref = await create_image_meta(session,serveraddress + resources,json.dumps(data))
    is_success,img_encoded = cv2.imencode('.png', undstortedimage)
    image_location = await upload_png_file_data(session, serveraddress + image_ref,img_encoded.tobytes())
    return image_ref
'''
async def upload_images(session,serveraddress, undstortedimage, generatedviewmatrix, locationid, poses = None):
    if poses is not None:
        resources = "/integral_images"
        data = {
                "location_id": locationid,
                "drone_id": "drone1",
                "m3x4": generatedviewmatrix.tolist(),
                "source_images": poses
                }
    else :
        resources = "/images"
        data = {
                "location_id": locationid,
                "drone_id": "drone1",
                "m3x4": [0, 0 ,0]#generatedviewmatrix.tolist()
            }
    image_ref = await create_image_meta(session,serveraddress + resources,json.dumps(data))
    is_success,img_encoded = cv2.imencode('.png', undstortedimage)
    image_location = await upload_png_file_data(session, serveraddress + image_ref,img_encoded.tobytes())
'''       
        
async def upload_detectionlabels(serveraddress, location_id,labels_data):
    async with aiohttp.ClientSession() as session:
        for label in labels_data:
            label["location_id"] = location_id
            await upload_json(session, serveraddress + "/labels", json.dumps(label))

async def upload_detectionlabels_was(session, serveraddress, location_id,labels_data):
    for label in labels_data:
        resources = "/labels"
        #print(json.dumps(label, indent=2))
        await upload_json(session, serveraddress + resources, json.dumps(label))

