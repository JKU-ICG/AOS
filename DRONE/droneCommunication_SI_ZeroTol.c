#include <sys/types.h>
#include <stdio.h>
#include <string.h>
#include <termios.h>		
#include <stdlib.h>

#include <curses.h>
//#include <stdio.h>
//#include <string.h>
//#include <termios.h>		
//#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/joystick.h>
#include <sys/mman.h>
//#include <sys/types.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/select.h>


typedef long long                u64;
typedef unsigned long            u32;
typedef unsigned short           u16;
typedef unsigned char            u8;

typedef signed long              s32;
typedef signed short             s16;
typedef signed char              s8;

typedef volatile unsigned long   vu32;
typedef volatile unsigned short  vu16;
typedef volatile unsigned char   vu8;

typedef volatile signed long     vs32;
typedef volatile signed short    vs16;
typedef volatile signed char     vs8;

//Defines for external control
#define EC_VALID           0x01  // only valid if this is 1
#define EC_GAS_ADD         0x02  // if 1 -> use the GAS Value not as MAX
#define EC_IGNORE_RC       0x80  // if 1 -> for Flying without RC-Control 

#define POINT_TYPE_INVALID 255
#define POINT_TYPE_WP		0
#define POINT_TYPE_POI		1
#define POINT_TYPE_FS		2
#define POINT_TYPE_LAND		3
#define POINT_TYPE_FLYZONE	4
#define POINT_TYPE_HOME		5

// status 
#define INVALID         0x00
#define NEWDATA         0x01
#define PROCESSED       0x02

#define FC_address      1  //(b)
#define NC_address      2  //(c)
#define MK3MAG_address  3  //(d)
#define BL_CTRL_address 5  //(f)

//Command IDs
#define SERIAL_CHANNELS		'y'
#define EXTERNAL_CONTROL	'b'


//#define SERIAL "/dev/bus/usb/001/005" /*<- this needs to be updated*/
//#define SERIAL "/dev/ttyAMA0" /*<- default from student!*/
#define SERIAL "/dev/ttyUSB0" /* <- this should be correct in Linux (e.g. Raspberry Pi)! */

typedef struct
{
	u8 address;
	u8 cmdID;
 	u8 data[1024];
 	u8 txrxdata[1024];
	u8 collecting;
 	u8 position_package;
	u16 cmdLength;
	///////////////////////////////////Added By Indrajit //////////////////////////////////////////////
	u8 c;
	int count;
 	u8 collecting_data[1024];
 	u16 position;
	u16 dataLength;
 	u8 position_package_gps;
	u8 readyForTransmit;
	u8 length_payload;
	u8 msg_id;
	///////////////////////////////////Added By Indrajit //////////////////////////////////////////////

}__attribute__((packed)) serial_data_struct;

typedef struct 
{
    int streamInfo;
    int Index;
    int Latitude;
    int Longitude;
    int Altitude;
    int BaroAltitude;
    int CompassHeading;
    int AngleNick;
    int AngleRoll;
    int WaypointIndex;
    int WayPointNumber;
    int DistanceToTarget;
    int TargetHoldTime;

}DroneInfo;

struct __attribute__((__packed__)) GPS_Pos_t
{
        s32 Longitude;                                  // in 1E-7 deg
		s32 Latitude;                                   // in 1E-7 deg
		s32 Altitude;                                   // in dm
		u8 Status;                                      // validity of data
};

struct __attribute__((__packed__)) WayPointStruct
{
        //struct GPS_Pos_t Position;             // the gps position of the waypoint, see ubx.h for details
		s32 Longitude;                                  // in 1E-7 deg
		s32 Latitude;                                   // in 1E-7 deg
		s32 Altitude;                                   // in dm
		u8 Status;                                      // validity of data
        u16 Heading;                    // orientation, 0 no action, 1...360 fix heading, neg. = Index to POI in WP List
        u8  ToleranceRadius;    		// in meters, if the MK is within that range around the target, then the next target is triggered
        u8  HoldTime;                   // in seconds, if the was once in the tolerance area around a WP, this time defines the delay before the next WP is triggered
        u8  Event_Flag;                 // future implementation and simulation
        u8  Index;              		// to indentify different waypoints, workaround for bad communications PC <-> NC
        u8  Type;                       // typeof Waypoint
        u8  WP_EventChannelValue;  		// Will be transferred to the FC and can be used as Poti value there
        u8  AltitudeRate;           	// rate to change the setpoint in steps of 0.1m/s
        u8  Speed;                      // rate to change the Position(0 = max) in steps of 0.1m/s
        s8  CamAngle;                   // Camera servo angle in degree (121 -> POI-Automatic since V2.20)
        u8  Name[4];                	// Name of that point (ASCII)
        u8  AutoPhotoDistance;  		// in [m]
    	u8  reserve[1];                 // reserve
};


struct WayPointStruct WaypointInfo;
    

serial_data_struct data_package_request_osd;	
serial_data_struct data_package_receive_kopter;
serial_data_struct data_package_waypoint;
serial_data_struct data_package_sendTarget;

DroneInfo CurrentDroneInfo;
int uart0_filestream = -1; 
int usb_stream = -1;
int data_length;		//length of transmitting data string
//FILE * fp;

//>> Adding checksum and transmitting  data
//------------------------------------------------------------------------------------------------------
void transmit_data(serial_data_struct* pdata_package){
	if (uart0_filestream != -1)
	{
		int count = write(uart0_filestream, pdata_package->txrxdata, pdata_package->cmdLength);
        /*
		printf( "   SENT (len %d): ", pdata_package->cmdLength);		
		for(int i=0; i<pdata_package->cmdLength;++i)
		{
			printf( "%c", pdata_package->txrxdata[i]);
		}
		printf( " \n");	
		if (count < 0)		
		{
			printf("UART TX error\n");
		}
        */
	}
}


//>> Adding address and command ID, encoding and checksum
//------------------------------------------------------------------------------------------------------
void create_serial_frame(u8 address, u8 cmdID, u16 cmdLength, serial_data_struct* pdata_package){
	pdata_package->txrxdata[0] = '#';
	pdata_package->txrxdata[1] = address + 'a';
	pdata_package->txrxdata[2] = cmdID;

	//encode data
	u8 a,b,c;
	int counter = 0;
	int u = 3;
	while(cmdLength){
		if(cmdLength)
			{
				cmdLength--; 
				a = pdata_package->data[counter++];
			}else{a = 0; counter++;};
		if(cmdLength)
			{
				cmdLength--; 
				b = pdata_package->data[counter++];
			}else{b = 0; counter++;};
		if(cmdLength)
			{
				cmdLength--; 
				c = pdata_package->data[counter++];
			}else{c = 0; counter++;};
		pdata_package->txrxdata[u++] = '=' + (a >> 2);
		pdata_package->txrxdata[u++] = '=' + (((a & 0x03) << 4) | ((b & 0xf0) >> 4));
		pdata_package->txrxdata[u++] = '=' + (((b & 0x0f) << 2) | ((c & 0xc0) >> 6));
		pdata_package->txrxdata[u++] = '=' + (c & 0x3f);
	}	

	//add Checksum
	u16 crc = 0;
	u8 	crc1, crc2;
	for (int i = 0; i < u; i++)
	{
		crc += pdata_package->txrxdata[i];
	}
	crc %= 4096;
	crc1 = '=' + crc / 64;
	crc2 = '=' + crc % 64;
	pdata_package->txrxdata[u++] = crc1;
	pdata_package->txrxdata[u++] = crc2;
	pdata_package->txrxdata[u++] = '\r';

	pdata_package->cmdLength = u;
}

/////////////////////////////////////////////////////////////////////////////////////////////////////////
u8 get_char(serial_data_struct* pdata_package){
	if(pdata_package->count--)
	{
		pdata_package->c = pdata_package->txrxdata[pdata_package->position++];
		return(1);
	}else{return(0);}
}

void print_navicntrl_data(serial_data_struct* pdata_package_flight_data, DroneInfo* CurrentDroneInfo){
	//printf("Index Received \n%d\n", pdata_package_flight_data->data[0]);
	int32_t  GPS_Lon_1 = pdata_package_flight_data->data[1];
	int32_t  GPS_Lon_2 = pdata_package_flight_data->data[2];
	int32_t  GPS_Lon_3 = pdata_package_flight_data->data[3];
	int32_t  GPS_Lon_4 = pdata_package_flight_data->data[4];
	int32_t  GPS_Lon_OP = (GPS_Lon_1) | (GPS_Lon_2 << 8) | (GPS_Lon_3 << 16) | (GPS_Lon_4 << 24); // Correct Format 4321 --> Int
    CurrentDroneInfo->Longitude = GPS_Lon_OP;
	//int32_t  GPS_Lon = (GPS_Lon_4) | (GPS_Lon_3 << 8) | (GPS_Lon_2 << 16) | (GPS_Lon_1 << 24);

	int32_t  GPS_Lat_1 = pdata_package_flight_data->data[5];
	int32_t  GPS_Lat_2 = pdata_package_flight_data->data[6];
	int32_t  GPS_Lat_3 = pdata_package_flight_data->data[7];
	int32_t  GPS_Lat_4 = pdata_package_flight_data->data[8];
	int32_t  GPS_Lat_OP = (GPS_Lat_1) | (GPS_Lat_2 << 8) | (GPS_Lat_3 << 16) | (GPS_Lat_4 << 24);
    CurrentDroneInfo->Latitude = GPS_Lat_OP;

	int16_t  GPS_Alt_1; int16_t  GPS_Alt_2; int16_t  GPS_Alt; int16_t GPS_Alt_m; int GPS_Alt_cm;
	int GroundSpeed; int OSDStatusFlags; char CamCtrlChar;

	int32_t  Target_GPS_Lon_1;int32_t  Target_GPS_Lon_2;int32_t  Target_GPS_Lon_3;int32_t  Target_GPS_Lon_4;int32_t  Target_GPS_Lon_OP; 
	int32_t  Target_GPS_Lat_1;int32_t  Target_GPS_Lat_2;int32_t  Target_GPS_Lat_3;int32_t  Target_GPS_Lat_4;int32_t  Target_GPS_Lat_OP;
	int16_t  Target_GPS_Alt_1; int16_t  Target_GPS_Alt_2; int16_t  Target_GPS_Alt; int16_t Target_GPS_Alt_m;

	int32_t  Home_GPS_Lon_1;int32_t  Home_GPS_Lon_2;int32_t  Home_GPS_Lon_3;int32_t  Home_GPS_Lon_4;int32_t  Home_GPS_Lon_OP; 
	int32_t  Home_GPS_Lat_1;int32_t  Home_GPS_Lat_2;int32_t  Home_GPS_Lat_3;int32_t  Home_GPS_Lat_4;int32_t  Home_GPS_Lat_OP;
	int16_t  Home_GPS_Alt_1; int16_t  Home_GPS_Alt_2; int16_t  Home_GPS_Alt; int16_t Home_GPS_Alt_m;

	int AngleNick; int AngleRoll;
	int WaypointIndex; int WaypointNumber; int TargetHoldTime;
	int Heading; int CompassHeading; int16_t ShutterCounter_1; int16_t ShutterCounter_2; int16_t ShutterCounter;

    int16_t  Distancetarget_1; int16_t  Distancetarget_2; int16_t  Distancetarget;

	int16_t  Old_Compass_Heading_1;int16_t  Old_Compass_Heading_2;int16_t  Old_Compass_Heading;
	int32_t  Old_GPS_Alt_1;int32_t  Old_GPS_Alt_2;int32_t  Old_GPS_Alt_3;int32_t  Old_GPS_Alt_4;int32_t  Old_GPS_Alt;

	switch(pdata_package_flight_data->data[0])
			{
				case 10:	//Get Sensor lables
					GPS_Alt_1 = pdata_package_flight_data->data[9];
					GPS_Alt_2 = pdata_package_flight_data->data[10];
					GPS_Alt = (GPS_Alt_1) | (GPS_Alt_2 << 8);
					GPS_Alt_m = (int16_t)GPS_Alt / (int16_t)20;
                    GPS_Alt_cm = GPS_Alt*5;

					GroundSpeed = pdata_package_flight_data->data[11];
					OSDStatusFlags = pdata_package_flight_data->data[12];
					CamCtrlChar = pdata_package_flight_data->data[13];
                    CurrentDroneInfo->Index = 10;
					break;
				case 11:	//Get External Control
					GPS_Alt_1 = pdata_package_flight_data->data[9];
					GPS_Alt_2 = pdata_package_flight_data->data[10];
					GPS_Alt = (GPS_Alt_1) | (GPS_Alt_2 << 8);
					GPS_Alt_m = (int16_t)GPS_Alt / (int16_t)20;
                    GPS_Alt_cm = GPS_Alt*5;

					GroundSpeed = pdata_package_flight_data->data[11];
					OSDStatusFlags = pdata_package_flight_data->data[12];
                    CurrentDroneInfo->Index = 11;
					break;
				case 12:	//Get External Control
					GPS_Alt_1 = pdata_package_flight_data->data[9];
					GPS_Alt_2 = pdata_package_flight_data->data[10];
					GPS_Alt = (GPS_Alt_1) | (GPS_Alt_2 << 8);
					GPS_Alt_m = (int16_t)GPS_Alt / (int16_t)20;
                    GPS_Alt_cm = GPS_Alt*5;

					GroundSpeed = pdata_package_flight_data->data[11];
					OSDStatusFlags = pdata_package_flight_data->data[12];

					Target_GPS_Lon_1 = pdata_package_flight_data->data[13];
					Target_GPS_Lon_2 = pdata_package_flight_data->data[14];
					Target_GPS_Lon_3 = pdata_package_flight_data->data[15];
					Target_GPS_Lon_4 = pdata_package_flight_data->data[16];
					Target_GPS_Lon_OP = (Target_GPS_Lon_1) | (Target_GPS_Lon_2 << 8) | (Target_GPS_Lon_3 << 16) | (Target_GPS_Lon_4 << 24); // Correct Format 4321 --> Int
					//int32_t  GPS_Lon = (GPS_Lon_4) | (GPS_Lon_3 << 8) | (GPS_Lon_2 << 16) | (GPS_Lon_1 << 24);

					Target_GPS_Lat_1 = pdata_package_flight_data->data[17];
					Target_GPS_Lat_2 = pdata_package_flight_data->data[18];
					Target_GPS_Lat_3 = pdata_package_flight_data->data[19];
					Target_GPS_Lat_4 = pdata_package_flight_data->data[20];
					Target_GPS_Lat_OP = (Target_GPS_Lat_1) | (Target_GPS_Lat_2 << 8) | (Target_GPS_Lat_3 << 16) | (Target_GPS_Lat_4 << 24);

					Target_GPS_Alt_1 = pdata_package_flight_data->data[21];
					Target_GPS_Alt_2 = pdata_package_flight_data->data[22];
					Target_GPS_Alt = (Target_GPS_Alt_1) | (Target_GPS_Alt_2 << 8);
					Target_GPS_Alt_m = (int16_t)Target_GPS_Alt / (int16_t)20;
                    CurrentDroneInfo->Index = 12;
					break;
				case 13:	//Get External Control
					GPS_Alt_1 = pdata_package_flight_data->data[9];
					GPS_Alt_2 = pdata_package_flight_data->data[10];
					GPS_Alt = (GPS_Alt_1) | (GPS_Alt_2 << 8);
					GPS_Alt_m = (int16_t)GPS_Alt / (int16_t)20;
                    GPS_Alt_cm = GPS_Alt*5;

					GroundSpeed = pdata_package_flight_data->data[11];
					OSDStatusFlags = pdata_package_flight_data->data[12];

					Home_GPS_Lon_1 = pdata_package_flight_data->data[13];
					Home_GPS_Lon_2 = pdata_package_flight_data->data[14];
					Home_GPS_Lon_3 = pdata_package_flight_data->data[15];
					Home_GPS_Lon_4 = pdata_package_flight_data->data[16];
					Home_GPS_Lon_OP = (Home_GPS_Lon_1) | (Home_GPS_Lon_2 << 8) | (Home_GPS_Lon_3 << 16) | (Home_GPS_Lon_4 << 24); // Correct Format 4321 --> Int
					//int32_t  GPS_Lon = (GPS_Lon_4) | (GPS_Lon_3 << 8) | (GPS_Lon_2 << 16) | (GPS_Lon_1 << 24);

					Home_GPS_Lat_1 = pdata_package_flight_data->data[17];
					Home_GPS_Lat_2 = pdata_package_flight_data->data[18];
					Home_GPS_Lat_3 = pdata_package_flight_data->data[19];
					Home_GPS_Lat_4 = pdata_package_flight_data->data[20];
					Home_GPS_Lat_OP = (Home_GPS_Lat_1) | (Home_GPS_Lat_2 << 8) | (Home_GPS_Lat_3 << 16) | (Home_GPS_Lat_4 << 24);

					Home_GPS_Alt_1 = pdata_package_flight_data->data[21];
					Home_GPS_Alt_2 = pdata_package_flight_data->data[22];
					Home_GPS_Alt = (Home_GPS_Alt_1) | (Home_GPS_Alt_2 << 8);
					Home_GPS_Alt_m = (int16_t)Home_GPS_Alt / (int16_t)20;
                    CurrentDroneInfo->Index = 13;
					break;
				case 14:	//Get External Control
					GPS_Alt_1 = pdata_package_flight_data->data[9];
					GPS_Alt_2 = pdata_package_flight_data->data[10];
					GPS_Alt = (GPS_Alt_1) | (GPS_Alt_2 << 8);
					GPS_Alt_m = (int16_t)GPS_Alt / (int16_t)20;
                    GPS_Alt_cm = GPS_Alt*5;

					GroundSpeed = pdata_package_flight_data->data[11];
					OSDStatusFlags = pdata_package_flight_data->data[12];
					/*
					u16 FlyingTime;                 // in seconds ---13, 14
					u16 DistanceToHome;             // [10cm] (100 = 10m) ---15, 16
					u8  HeadingToHome;              // in 2° (100 = 200°) -- 17
					u16 DistanceToTarget;   // [10cm] (100 = 10m)    --18,19
					u8  HeadingToTarget;    // in 2° (100 = 200°) --20
					*/
                    Distancetarget_1 = pdata_package_flight_data->data[18];
					Distancetarget_2 = pdata_package_flight_data->data[19];
					Distancetarget = (Distancetarget_1) | (Distancetarget_2 << 8);
					AngleNick = pdata_package_flight_data->data[21];
					AngleRoll = pdata_package_flight_data->data[22];
                    CurrentDroneInfo->Index = 14;
                    CurrentDroneInfo->AngleNick = AngleNick;
                    CurrentDroneInfo->AngleRoll = AngleRoll;
                    CurrentDroneInfo->DistanceToTarget = Distancetarget;
					break;
				case 15:	//Get External Control
					GPS_Alt_1 = pdata_package_flight_data->data[9];
					GPS_Alt_2 = pdata_package_flight_data->data[10];
					GPS_Alt = (GPS_Alt_1) | (GPS_Alt_2 << 8);
					GPS_Alt_m = (int16_t)GPS_Alt / (int16_t)20;
                    GPS_Alt_cm = GPS_Alt*5;

					GroundSpeed = pdata_package_flight_data->data[11];
					OSDStatusFlags = pdata_package_flight_data->data[12];

					WaypointIndex = pdata_package_flight_data->data[13];
					WaypointNumber = pdata_package_flight_data->data[14];
					TargetHoldTime = pdata_package_flight_data->data[15];
                    CurrentDroneInfo->Index = 15;
                    CurrentDroneInfo->WaypointIndex = WaypointIndex;
                    CurrentDroneInfo->WayPointNumber = WaypointNumber;
                    CurrentDroneInfo->TargetHoldTime = TargetHoldTime;
					break;
				case 16:	//Get External Control
					GPS_Alt_1 = pdata_package_flight_data->data[9];
					GPS_Alt_2 = pdata_package_flight_data->data[10];
					GPS_Alt = (GPS_Alt_1) | (GPS_Alt_2 << 8);
					GPS_Alt_m = (int16_t)GPS_Alt / (int16_t)20;
                    GPS_Alt_cm = GPS_Alt*5;

					GroundSpeed = pdata_package_flight_data->data[11];
					OSDStatusFlags = pdata_package_flight_data->data[12];
					/*
					u16 UBat;                               // Battery Voltage in 0.1 Volts -- 13,14
					u16 Current;                    // actual current in 0.1A steps ---15,16
					u16 UsedCapacity;               // used capacity in mAh ---17,18
					s8  Variometer;                 // climb(+) and sink(-) rate --19
					*/
					Heading = pdata_package_flight_data->data[20];
					CompassHeading = pdata_package_flight_data->data[21];
					/*
					u8  Gas;                                // current gas (thrust) -- 22
					*/
					ShutterCounter_1 = pdata_package_flight_data->data[23];
					ShutterCounter_2 = pdata_package_flight_data->data[24];
					ShutterCounter = (ShutterCounter_1) | (ShutterCounter_2 << 8);
                    CurrentDroneInfo->Index = 16;
                    CurrentDroneInfo->CompassHeading = CompassHeading;
					//printf("CompassHeading %d\n", CompassHeading);
					//fprintf (fp, "CompassHeading %d\n", CompassHeading);
					break;
				case 17:	//Get External Control
					GPS_Alt_1 = pdata_package_flight_data->data[9];
					GPS_Alt_2 = pdata_package_flight_data->data[10];
					GPS_Alt = (GPS_Alt_1) | (GPS_Alt_2 << 8);
					GPS_Alt_m = (int16_t)GPS_Alt / (int16_t)20;
                    GPS_Alt_cm = GPS_Alt*5;

					GroundSpeed = pdata_package_flight_data->data[11];
					OSDStatusFlags = pdata_package_flight_data->data[12];
                    CurrentDroneInfo->Index = 17;
					break;
				case 18:	//Get External Control
					GPS_Alt_1 = 0;
					GPS_Alt_2 = 0;
					GPS_Alt = (GPS_Alt_1) | (GPS_Alt_2 << 8);
					GPS_Alt_m = (int16_t)GPS_Alt / (int16_t)20;
                    GPS_Alt_cm = GPS_Alt*5;

					GroundSpeed = 0;
					OSDStatusFlags = 0;
                    CurrentDroneInfo->Index = 18;
					break;
				case 19:	//Get External Control
					GPS_Alt_1 = pdata_package_flight_data->data[9];
					GPS_Alt_2 = pdata_package_flight_data->data[10];
					GPS_Alt = (GPS_Alt_1) | (GPS_Alt_2 << 8);
					GPS_Alt_m = (int16_t)GPS_Alt / (int16_t)20;
                    GPS_Alt_cm = GPS_Alt*5;

					GroundSpeed = pdata_package_flight_data->data[11];
					OSDStatusFlags = pdata_package_flight_data->data[12];
                    CurrentDroneInfo->Index = 19;
					break;
				case 20:	//Get External Control
					GPS_Alt_1 = pdata_package_flight_data->data[9];
					GPS_Alt_2 = pdata_package_flight_data->data[10];
					GPS_Alt = (GPS_Alt_1) | (GPS_Alt_2 << 8);
					GPS_Alt_m = (int16_t)GPS_Alt / (int16_t)20;
                    GPS_Alt_cm = GPS_Alt*5;

					GroundSpeed = pdata_package_flight_data->data[11];
					OSDStatusFlags = pdata_package_flight_data->data[12];
                    CurrentDroneInfo->Index = 20;
					break;
				default :
					{	
					Old_GPS_Alt_1 = pdata_package_flight_data->data[10];
					Old_GPS_Alt_2 = pdata_package_flight_data->data[11];
					Old_GPS_Alt_3 = pdata_package_flight_data->data[12];
					Old_GPS_Alt_4 = pdata_package_flight_data->data[13];
					Old_GPS_Alt = (Old_GPS_Alt_1) | (Old_GPS_Alt_2 << 8) | (Old_GPS_Alt_3 << 16) | (Old_GPS_Alt_4 << 24);
					//GPS_Alt_m = (int16_t)Old_GPS_Alt / (int16_t)20;
					//GPS_Alt = (int16_t)Old_GPS_Alt;
                    //GPS_Alt_cm = GPS_Alt/10;
                    /*
                    GPS_Pos_t TargetPosition; --- 14-26
                    GPS_PosDev_t TargetPositionDeviation; --- 27-30
                    GPS_Pos_t HomePosition; --- 31-43
                    GPS_PosDev_t HomePositionDeviation; --- 44-47
                    u8  WaypointIndex;                              // index of current waypoints running from 0 to WaypointNumber-1 --48
                    u8  WaypointNumber;                             // number of stored waypoints --49
                    u8  SatsInUse;                                  // number of satellites used for position solution --50
                    s16 Altimeter;                                  // hight according to air pressure --51,52
                    s16 Variometer;                                 // climb(+) and sink(-) rate --53,54
                    u16 FlyingTime;                                 // in seconds --55,56
                    u8  UBat;                                       // Battery Voltage in 0.1 Volts --57
                    u16 GroundSpeed;                                // speed over ground in cm/s (2D) --58,59
                    s16 Heading;                                    // current flight direction in ° as angle to north --60,61
                    s16 CompassHeading;                             // current compass value in ° -- 62,63
                    s8  AngleNick;                                  // current Nick angle in 1° -- 64
                    s8  AngleRoll;                                  // current Rick angle in 1° -- 65
                    u8  RC_Quality;                                 // RC_Quality -- 66
                    u8  FCStatusFlags;                              // Flags from FC -- 67
                    u8  NCFlags;                                    // Flags from NC -- 68
                    u8  Errorcode;                                  // 0 --> okay
                    u8  OperatingRadius;                            // current operation radius around the Home Position in m
                    s16 TopSpeed;                                   // velocity in vertical direction in cm/s
                    u8  TargetHoldTime;                             // time in s to stay at the given target, counts down to 0 if target has been reached
                    u8  FCStatusFlags2;                             // StatusFlags2 (since version 5 added)
                    s16 SetpointAltitude;                           // setpoint for altitude
                    u8  Gas;                                        // for future use
                    u16 Current;                                    // actual current in 0.1A steps
                    u16 UsedCapacity;                               // used capacity in mAh
                    */
                    GPS_Alt_1 = pdata_package_flight_data->data[51];
					GPS_Alt_2 = pdata_package_flight_data->data[52];
					GPS_Alt = (GPS_Alt_1) | (GPS_Alt_2 << 8);
					GPS_Alt_m = (int16_t)GPS_Alt / (int16_t)20;
                    GPS_Alt_cm = GPS_Alt*5;

					Old_Compass_Heading_1 = pdata_package_flight_data->data[62];
					Old_Compass_Heading_2 = pdata_package_flight_data->data[63];
					Old_Compass_Heading = (Old_Compass_Heading_1) | (Old_Compass_Heading_2 << 8);
					AngleNick = pdata_package_flight_data->data[64];
					AngleRoll = pdata_package_flight_data->data[65];
					//printf("Old_CompassHeading %d\n", Old_Compass_Heading);
					//fprintf (fp, "CompassHeading %d\n", CompassHeading);
                    CurrentDroneInfo->Index = 5;
					}

			}	
    CurrentDroneInfo->BaroAltitude = GPS_Alt_cm;
	//int32_t  GPS_Lat = (GPS_Lat_4) | (GPS_Lat_3 << 8) | (GPS_Lat_2 << 16) | (GPS_Lat_1 << 24);
    /*
	printf("\nIndex  = %d\n", pdata_package_flight_data->data[0]);
	fprintf (fp, "\nIndex  = %d\n", pdata_package_flight_data->data[0]);
	
	printf("LatitudeOP = %d\n", GPS_Lat_OP);
	fprintf (fp, "LatitudeOP = %d\n", GPS_Lat_OP);
	printf("LongitudeOP = %d\n", GPS_Lon_OP);
	fprintf (fp, "LongitudeOP = %d\n", GPS_Lon_OP);
	printf("GPSALT %d in m = %d \n", GPS_Alt, GPS_Alt_m);
	fprintf (fp, "GPSALT %d in m = %d \n", GPS_Alt, GPS_Alt_m);
	printf("GroundSpeed %d\n", GroundSpeed);
	fprintf (fp, "GroundSpeed %d\n", GroundSpeed);
    */
	//decToHexa(OSDFlags) ;
	//printf("OSDFlags %d\n", GroundSpeed);
}

//>> Decoding Data and retrieving address and cmdID
//------------------------------------------------------------------------------------------------------
void collect_serial_frame(serial_data_struct* pdata_package_collect){
	pdata_package_collect->position_package++; 																							//first character: #
	pdata_package_collect->address = pdata_package_collect->collecting_data[pdata_package_collect->position_package++] - 'a'; 	//address
	pdata_package_collect->cmdID = pdata_package_collect->collecting_data[pdata_package_collect->position_package++]; 			//cmdID
	u8 a, b, c, d;
	u16 datacpy = 0;
	while(pdata_package_collect->position_package < pdata_package_collect->dataLength-3){
		a = pdata_package_collect->collecting_data[pdata_package_collect->position_package++] - '=';
		b = pdata_package_collect->collecting_data[pdata_package_collect->position_package++] - '=';
		c = pdata_package_collect->collecting_data[pdata_package_collect->position_package++] - '=';
		d = pdata_package_collect->collecting_data[pdata_package_collect->position_package++] - '=';

		pdata_package_collect->data[datacpy++] = (a << 2) | (b >> 4);
		pdata_package_collect->data[datacpy++] = ((b & 0x0f) << 4) | (c >> 2);
		pdata_package_collect->data[datacpy++] = ((c & 0x03) << 6) | d;
	}
	pdata_package_collect->dataLength = datacpy;
	pdata_package_collect->position_package = 0;
	

	//printf("Decoded data \n%s\n", pdata_package_collect->collecting_data);
	//fprintf (fp,"Decoded data \n%s\n", pdata_package_collect->collecting_data);
	/*
	for (int i = 0; i < datacpy; ++i)
	{
		//printf("|%d|: %d ", i, pdata_package_collect->data[i]);
		fprintf (fp,"|%d|: %d ", i, pdata_package_collect->data[i]);
	}

	//printf("\nData as String \n%s\n", pdata_package_collect->data);
	/**/
	
}

u8 collect_data(serial_data_struct* pdata_package){
	if(pdata_package->c == '#')
	{
		pdata_package->collecting = 1;
	}
	if(pdata_package->collecting)
	{
		pdata_package->collecting_data[pdata_package->position_package++] = pdata_package->c;
		if(pdata_package->c == '\r'){
			return(0);
		}
	}
	return(1);
}

void analyze_data_package(serial_data_struct* pdata_package_analyze, DroneInfo* CurrentDroneInfo){
	//printf("Analyzing Data Package\n");
	//fprintf (fp, "Analyzing Data Package\n");
	switch(pdata_package_analyze->collecting_data[1] - 'a')
	{
		
		case 2:	//NaviCtrl
			switch(pdata_package_analyze->collecting_data[2])
			{
				case 'A':	//Get Sensor lables
                    CurrentDroneInfo->Index = -1;
					collect_serial_frame(pdata_package_analyze);
					break;
				case 'B':	//Get External Control
					//printf("Analyzing ExternalCntrl Data Package\n");
					//fprintf (fp, "Analyzing ExternalCntrl Data Package\n");
                    CurrentDroneInfo->Index = -1;
					collect_serial_frame(pdata_package_analyze);
					break;
				case 'D':	//Get Analog Values
                    CurrentDroneInfo->Index = -1;
					collect_serial_frame(pdata_package_analyze);
					break;
				case 'C':	//Get 3D Data
					collect_serial_frame(pdata_package_analyze);
                    CurrentDroneInfo->Index = -1;
					break;
				case 'O':	//Get NaviCntrl Data
					//printf("Analyzing NaviCntrl Data Package\n");
					//fprintf (fp, "Analyzing NaviCntrl Data Package\n");
					collect_serial_frame(pdata_package_analyze);
					print_navicntrl_data(pdata_package_analyze, CurrentDroneInfo);
					break;
				case 'V':	//Get NaviCntrl Data
					//printf("Analyzing Version Data Package\n");
					//fprintf (fp, "Analyzing Version Data Package\n");
					collect_serial_frame(pdata_package_analyze);
                    CurrentDroneInfo->Index = -1;
					//print_Version_data(pdata_package_analyze);
					break;
				case 'W':	//Get NaviCntrl Data
					//printf("Analyzing Number of Waypoint Data Package\n");
					//fprintf (fp, "Analyzing Number of Waypoint Data Package\n");
					collect_serial_frame(pdata_package_analyze);
                    CurrentDroneInfo->Index = -1;
					//printf("\nNumber Of WayPoints  = %d\n", pdata_package_analyze->data[0]);
					//fprintf (fp, "\nNumber Of WayPoints  = %d\n", pdata_package_analyze->data[0]);
					break;
				case 'X':	//Get NaviCntrl Data
					//printf("Analyzing Waypoint Data Package\n");
					//fprintf (fp, "Analyzing Waypoint Data Package\n");
					collect_serial_frame(pdata_package_analyze);
                    CurrentDroneInfo->Index = -1;
					//print_WayPoint_data(pdata_package_analyze);
					break;
			}	
			break;
		case 1:	//FlightCtrl
			switch(pdata_package_analyze->collecting_data[2])
			{
				case 'A':	//Get Sensor lables
				
					collect_serial_frame(pdata_package_analyze);
                    CurrentDroneInfo->Index = -1;
					break;
				case 'B':	//Get Sensor lables
					collect_serial_frame(pdata_package_analyze);
                    CurrentDroneInfo->Index = -1;
					break;
				case 'D':	//Get Analog Values
					collect_serial_frame(pdata_package_analyze);
                    CurrentDroneInfo->Index = -1;
					//create_serial_frame(1, 'D', 66, pdata_package_analyze);
					break;
				case 'Q':	//Get Configuration
					collect_serial_frame(pdata_package_analyze);
                    CurrentDroneInfo->Index = -1;
					break;
				case 'P':	//Get FlightCtrl Values
					collect_serial_frame(pdata_package_analyze);
                    CurrentDroneInfo->Index = -1;
					break;
				case 'C':	//Get 3D Data
					collect_serial_frame(pdata_package_analyze);
                    CurrentDroneInfo->Index = -1;
					break;
				case 'V':	//Get NaviCntrl Data
					//printf("Analyzing Version Data Package\n");
					collect_serial_frame(pdata_package_analyze);
                    CurrentDroneInfo->Index = -1;
					//print_Version_data(pdata_package_analyze);
					break;
			}
			
		case 0:
			switch(pdata_package_analyze->collecting_data[2])
			{
				case 'a':
					collect_serial_frame(pdata_package_analyze);
                    CurrentDroneInfo->Index = -1;
					break;
				case 'h':
					collect_serial_frame(pdata_package_analyze);
                    CurrentDroneInfo->Index = -1;
					break;
			}

	}
	memset(pdata_package_analyze->collecting_data, 0, 1023);
	memset(pdata_package_analyze->data, 0, 1023);
}
///////////////////////////////////Added By Indrajit //////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////
//>> Initializing serial interface
//------------------------------------------------------------------------------------------------------
int uart_init(int Valueunused){
	uart0_filestream = open(SERIAL, O_RDWR | O_NOCTTY | O_NDELAY );
	if (uart0_filestream == -1)
	{
		printf("Error - Unable to open UART.  Ensure it is not in use by another application\n");
        return uart0_filestream;
	}
	//UART Options
	struct termios options;
	tcgetattr(uart0_filestream, &options);
	options.c_cflag = B57600 | CS8 | CLOCAL | CREAD;		
	options.c_iflag = IGNPAR;
	options.c_oflag = 0;
	options.c_lflag = 0;
	tcflush(uart0_filestream, TCIFLUSH);
	tcsetattr(uart0_filestream, TCSANOW, &options);
    return uart0_filestream;
	//fp = fopen ("GPS_Data.txt","w+");
	//UART Options
}

//>> Receiving Data from the Kopter and collecting serial frame if needed
// from ExPlat project on Mikrokopter SVN
//------------------------------------------------------------------------------------------------------
void receive_data(serial_data_struct* pdata_package_receive_kopter, DroneInfo* CurrentDroneInfo){
	//fp = fopen ("GPS_Data.txt","a+");
	if (uart0_filestream != -1)
	{
		memset(pdata_package_receive_kopter->txrxdata, 0, 1023);
		{	
			int rx_length = read(uart0_filestream, (void*)pdata_package_receive_kopter->txrxdata, 512);		//Filestream, buffer to store in, number of bytes to read (max)
			if (rx_length > 0)
			{
					{
						//printf( "RECEIVED (len %d): ", rx_length);
						for(int i=0; i<rx_length;++i)
						{
							if(!(pdata_package_receive_kopter->txrxdata[i] == '\r'))
								//printf( "%c", pdata_package_receive_kopter->txrxdata[i] );
						}
						//printf( " \n");	
					}
					pdata_package_receive_kopter->cmdLength = rx_length;
					pdata_package_receive_kopter->count = rx_length;
					pdata_package_receive_kopter->position = 0;
					while(get_char(pdata_package_receive_kopter))
					{
						if(!collect_data(pdata_package_receive_kopter))
						{
							pdata_package_receive_kopter->collecting = 0;
							pdata_package_receive_kopter->dataLength = pdata_package_receive_kopter->position_package;
							pdata_package_receive_kopter->position_package = 0;
							u16 crc = 0;
							u8 	crc1, crc2;
							for (int i = 0; i < pdata_package_receive_kopter->dataLength - 3; i++)
							{
								crc += pdata_package_receive_kopter->collecting_data[i];
							}
							crc %= 4096;
							crc1 = '=' + crc / 64;
							crc2 = '=' + crc % 64;
							if(crc1 == pdata_package_receive_kopter->collecting_data[pdata_package_receive_kopter->dataLength - 3] && crc2 == pdata_package_receive_kopter->collecting_data[pdata_package_receive_kopter->dataLength - 2])
							{
                                CurrentDroneInfo->streamInfo = uart0_filestream;
								analyze_data_package(pdata_package_receive_kopter, CurrentDroneInfo);
								//>> CRC OK
								pdata_package_receive_kopter->position_package = 0;
							}else{
								//>> CRC NOT OK
								//printf("RX Checksum Error\n");
                                CurrentDroneInfo->streamInfo = -1;
								pdata_package_receive_kopter->position_package = 0;
								memset(pdata_package_receive_kopter->collecting_data, 0, 1023);
							}
						}
                        else
                        {
                            CurrentDroneInfo->streamInfo = -1;
                        }
                        
					}
                /**/
			}
            else
            {
                CurrentDroneInfo->streamInfo = -1;
            }
            
		}
	}else{
		//printf("KOPTER RX Error\n");
        CurrentDroneInfo->streamInfo = uart0_filestream;
	}
	//fclose (fp);
	//return true;
}
void CurrentDroneInfoInit(DroneInfo* CurrentDroneInfo)
{
        CurrentDroneInfo->streamInfo = -1;
        CurrentDroneInfo->Index = -1;
        CurrentDroneInfo->Latitude = -1;
        CurrentDroneInfo->Longitude = -1;
        CurrentDroneInfo->Altitude = -1;
        CurrentDroneInfo->BaroAltitude = -1;
        CurrentDroneInfo->CompassHeading = -1;
        CurrentDroneInfo->AngleNick = -1;
        CurrentDroneInfo->AngleRoll = -1;
        CurrentDroneInfo->WaypointIndex = -1;
        CurrentDroneInfo->WayPointNumber = -1;
        CurrentDroneInfo->DistanceToTarget = -1;
        CurrentDroneInfo->TargetHoldTime = -1;
}

DroneInfo receiveDroneInfo()
{
			// Request OSD ---- Working
		u8 sending_interval = 1; // 1- 10ms interval.  This value [10ms] is used when starting the abbo. 10 => send the data every 100ms
		int16_t MaxBytePerSec = 1024;  //Max Bytes Per Sec -- 10ms interval -- 100 data request -- 20 bytes per packet max -- 2048 bytes per sec. This value [bytes per second] is used when starting the abbo.
		//It is used to keep the used bandwith to a specified (max) level according to the maximum data throughput of the communication interface. A useful value could be 1024 for a good wireless transmission and 200 for a slow transmission like GSM-Modems etc.
		int16_t  MaxBytePerSec_Low = MaxBytePerSec & 0xFF; // Get Lower Byte of MaxBytePerSec
		int16_t  MaxBytePerSec_High = (MaxBytePerSec >> 8) & 0xFF; // Get Higher Byte of MaxBytePerSec
		int16_t MaxBytePerSecTest = (MaxBytePerSec_Low) | (MaxBytePerSec_High << 8) ;
		data_package_request_osd.data[0] = sending_interval;
		data_package_request_osd.data[1] = (u8) MaxBytePerSec_High;
		data_package_request_osd.data[2] = (u8) MaxBytePerSec_Low;
		/*
		printf("MaxBytePerSecTest = %d \n", MaxBytePerSecTest);
		printf("MaxBytePerSec_High = %d \n", MaxBytePerSec_High);
		printf("MaxBytePerSec_Low = %d \n", MaxBytePerSec_Low);
		printf("SendingInterval \n%d\n", data_package_request_osd.data[0]);
		printf("SendingMaxBytePerSec_High \n%d\n", data_package_request_osd.data[1]);
		printf("SendingMaxBytePerSec_Low \n%d\n", data_package_request_osd.data[2]);
		printf("Size \n%d\n", sizeof(sending_interval)*3);*/
		create_serial_frame(2, 'o', sizeof(sending_interval)*3, &data_package_request_osd ); 
		transmit_data( &data_package_request_osd );
        CurrentDroneInfoInit(&CurrentDroneInfo);
		///////////////////////////////////Added By Indrajit //////////////////////////////////////////////
		receive_data(&data_package_receive_kopter, &CurrentDroneInfo);
		usleep(10000); 
        return CurrentDroneInfo;
	
}

struct WayPointStruct GetWaypointInfo(int WayPointIndex){
									//character for echo
	struct WayPointStruct WaypointInfo_Add;
	switch(WayPointIndex)
			{
				case 1:
					//WaypointInfo_Add.Position.Longitude = 143139817; // the gps position of the waypoint // in 1E-7 deg
					//WaypointInfo_Add.Position.Latitude = 483378862;// the gps position of the waypoint // in 1E-7 deg
					//WaypointInfo_Add.Position.Altitude = 50;// the gps position of the waypoint // in dm
					//WaypointInfo_Add.Position.Status = NEWDATA;// the gps position of the waypoint // validity of data
					WaypointInfo_Add.Longitude = 143264154; // the gps position of the waypoint // in 1E-7 deg
					WaypointInfo_Add.Latitude = 483359296;// the gps position of the waypoint // in 1E-7 deg
					WaypointInfo_Add.Altitude = 100;// the gps position of the waypoint // in dm
					WaypointInfo_Add.Status = 1;// the gps position of the waypoint // validity of data
					WaypointInfo_Add.Heading = 0; // orientation, 0 no action, 1...360 fix heading, neg. = Index to POI in WP List
					WaypointInfo_Add.ToleranceRadius = 2;    		// in meters, if the MK is within that range around the target, then the next target is triggered
					WaypointInfo_Add.HoldTime = 0;                   // in seconds, if the was once in the tolerance area around a WP, this time defines the delay before the next WP is triggered
					WaypointInfo_Add.Event_Flag = 0;                 // future implementation and simulation
					WaypointInfo_Add.Index = 1;              		// to indentify different waypoints, workaround for bad communications PC <-> NC
					WaypointInfo_Add.Type = POINT_TYPE_WP;                       // typeof Waypoint
					WaypointInfo_Add.WP_EventChannelValue = 30;  		// Will be transferred to the FC and can be used as Poti value there
					WaypointInfo_Add.AltitudeRate = 30;           	// rate to change the setpoint in steps of 0.1m/s
					WaypointInfo_Add.Speed = 7;                      // rate to change the Position(0 = max) in steps of 0.1m/s
					WaypointInfo_Add.CamAngle = 108;                   // Camera servo angle in degree (121 -> POI-Automatic since V2.20)
					WaypointInfo_Add.Name[0] = 'S';                	// Name of that point (ASCII)
					WaypointInfo_Add.Name[1] = 'P';                	// Name of that point (ASCII)
					WaypointInfo_Add.Name[2] = 'T';                	// Name of that point (ASCII)
					WaypointInfo_Add.Name[3] = 0;                	// Name of that point (ASCII)
					WaypointInfo_Add.AutoPhotoDistance = 0;  		// in [m]
					WaypointInfo_Add.reserve[0] = 0;
					break;

				case 2:
					//WaypointInfo_Add.Position.Longitude = 143139817; // the gps position of the waypoint // in 1E-7 deg
					//WaypointInfo_Add.Position.Latitude = 483378862;// the gps position of the waypoint // in 1E-7 deg
					//WaypointInfo_Add.Position.Altitude = 50;// the gps position of the waypoint // in dm
					//WaypointInfo_Add.Position.Status = NEWDATA;// the gps position of the waypoint // validity of data
					WaypointInfo_Add.Longitude = 143267975; // the gps position of the waypoint // in 1E-7 deg
					WaypointInfo_Add.Latitude = 483360219;// the gps position of the waypoint // in 1E-7 deg
					WaypointInfo_Add.Altitude = 100;// the gps position of the waypoint // in dm
					WaypointInfo_Add.Status = 1;// the gps position of the waypoint // validity of data
					WaypointInfo_Add.Heading = 0; // orientation, 0 no action, 1...360 fix heading, neg. = Index to POI in WP List
					WaypointInfo_Add.ToleranceRadius = 2;    		// in meters, if the MK is within that range around the target, then the next target is triggered
					WaypointInfo_Add.HoldTime = 0;                   // in seconds, if the was once in the tolerance area around a WP, this time defines the delay before the next WP is triggered
					WaypointInfo_Add.Event_Flag = 0;                 // future implementation and simulation
					WaypointInfo_Add.Index = 1;              		// to indentify different waypoints, workaround for bad communications PC <-> NC
					WaypointInfo_Add.Type = POINT_TYPE_WP;                       // typeof Waypoint
					WaypointInfo_Add.WP_EventChannelValue = 30;  		// Will be transferred to the FC and can be used as Poti value there
					WaypointInfo_Add.AltitudeRate = 30;           	// rate to change the setpoint in steps of 0.1m/s
					WaypointInfo_Add.Speed = 7;                      // rate to change the Position(0 = max) in steps of 0.1m/s
					WaypointInfo_Add.CamAngle = 108;                   // Camera servo angle in degree (121 -> POI-Automatic since V2.20)
					WaypointInfo_Add.Name[0] = 'S';                	// Name of that point (ASCII)
					WaypointInfo_Add.Name[1] = 'P';                	// Name of that point (ASCII)
					WaypointInfo_Add.Name[2] = 'A';                	// Name of that point (ASCII)
					WaypointInfo_Add.Name[3] = 0;                	// Name of that point (ASCII)
					WaypointInfo_Add.AutoPhotoDistance = 0;  		// in [m]
					WaypointInfo_Add.reserve[0] = 0;
					break;
				case 3:
					//WaypointInfo_Add.Position.Longitude = 143139817; // the gps position of the waypoint // in 1E-7 deg
					//WaypointInfo_Add.Position.Latitude = 483378862;// the gps position of the waypoint // in 1E-7 deg
					//WaypointInfo_Add.Position.Altitude = 50;// the gps position of the waypoint // in dm
					//WaypointInfo_Add.Position.Status = NEWDATA;// the gps position of the waypoint // validity of data
					WaypointInfo_Add.Longitude = 143269225; // the gps position of the waypoint // in 1E-7 deg
					WaypointInfo_Add.Latitude = 483357620;// the gps position of the waypoint // in 1E-7 deg
					WaypointInfo_Add.Altitude = 100;// the gps position of the waypoint // in dm
					WaypointInfo_Add.Status = 1;// the gps position of the waypoint // validity of data
					WaypointInfo_Add.Heading = 0; // orientation, 0 no action, 1...360 fix heading, neg. = Index to POI in WP List
					WaypointInfo_Add.ToleranceRadius = 2;    		// in meters, if the MK is within that range around the target, then the next target is triggered
					WaypointInfo_Add.HoldTime = 0;                   // in seconds, if the was once in the tolerance area around a WP, this time defines the delay before the next WP is triggered
					WaypointInfo_Add.Event_Flag = 0;                 // future implementation and simulation
					WaypointInfo_Add.Index = 1;              		// to indentify different waypoints, workaround for bad communications PC <-> NC
					WaypointInfo_Add.Type = POINT_TYPE_WP;                       // typeof Waypoint
					WaypointInfo_Add.WP_EventChannelValue = 30;  		// Will be transferred to the FC and can be used as Poti value there
					WaypointInfo_Add.AltitudeRate = 30;           	// rate to change the setpoint in steps of 0.1m/s
					WaypointInfo_Add.Speed = 7;                      // rate to change the Position(0 = max) in steps of 0.1m/s
					WaypointInfo_Add.CamAngle = 108;                   // Camera servo angle in degree (121 -> POI-Automatic since V2.20)
					WaypointInfo_Add.Name[0] = 'S';                	// Name of that point (ASCII)
					WaypointInfo_Add.Name[1] = 'P';                	// Name of that point (ASCII)
					WaypointInfo_Add.Name[2] = 'B';                	// Name of that point (ASCII)
					WaypointInfo_Add.Name[3] = 0;                	// Name of that point (ASCII)
					WaypointInfo_Add.AutoPhotoDistance = 0;  		// in [m]
					WaypointInfo_Add.reserve[0] = 0;
					break;
				case 4:
					//WaypointInfo_Add.Position.Longitude = 143139817; // the gps position of the waypoint // in 1E-7 deg
					//WaypointInfo_Add.Position.Latitude = 483378862;// the gps position of the waypoint // in 1E-7 deg
					//WaypointInfo_Add.Position.Altitude = 50;// the gps position of the waypoint // in dm
					//WaypointInfo_Add.Position.Status = NEWDATA;// the gps position of the waypoint // validity of data
					WaypointInfo_Add.Longitude = 143265260; // the gps position of the waypoint // in 1E-7 deg
					WaypointInfo_Add.Latitude = 483356729;// the gps position of the waypoint // in 1E-7 deg
					WaypointInfo_Add.Altitude = 100;// the gps position of the waypoint // in dm
					WaypointInfo_Add.Status = 1;// the gps position of the waypoint // validity of data
					WaypointInfo_Add.Heading = 0; // orientation, 0 no action, 1...360 fix heading, neg. = Index to POI in WP List
					WaypointInfo_Add.ToleranceRadius = 2;    		// in meters, if the MK is within that range around the target, then the next target is triggered
					WaypointInfo_Add.HoldTime = 0;                   // in seconds, if the was once in the tolerance area around a WP, this time defines the delay before the next WP is triggered
					WaypointInfo_Add.Event_Flag = 0;                 // future implementation and simulation
					WaypointInfo_Add.Index = 1;              		// to indentify different waypoints, workaround for bad communications PC <-> NC
					WaypointInfo_Add.Type = POINT_TYPE_WP;                       // typeof Waypoint
					WaypointInfo_Add.WP_EventChannelValue = 30;  		// Will be transferred to the FC and can be used as Poti value there
					WaypointInfo_Add.AltitudeRate = 30;           	// rate to change the setpoint in steps of 0.1m/s
					WaypointInfo_Add.Speed = 7;                      // rate to change the Position(0 = max) in steps of 0.1m/s
					WaypointInfo_Add.CamAngle = 108;                   // Camera servo angle in degree (121 -> POI-Automatic since V2.20)
					WaypointInfo_Add.Name[0] = 'S';                	// Name of that point (ASCII)
					WaypointInfo_Add.Name[1] = 'P';                	// Name of that point (ASCII)
					WaypointInfo_Add.Name[2] = 'C';                	// Name of that point (ASCII)
					WaypointInfo_Add.Name[3] = 0;                	// Name of that point (ASCII)
					WaypointInfo_Add.AutoPhotoDistance = 0;  		// in [m]
					WaypointInfo_Add.reserve[0] = 0;
					break;
				case 5:
					//WaypointInfo_Add.Position.Longitude = 143139817; // the gps position of the waypoint // in 1E-7 deg
					//WaypointInfo_Add.Position.Latitude = 483378862;// the gps position of the waypoint // in 1E-7 deg
					//WaypointInfo_Add.Position.Altitude = 50;// the gps position of the waypoint // in dm
					//WaypointInfo_Add.Position.Status = NEWDATA;// the gps position of the waypoint // validity of data
					WaypointInfo_Add.Longitude = 143264154; // the gps position of the waypoint // in 1E-7 deg
					WaypointInfo_Add.Latitude = 483359296;// the gps position of the waypoint // in 1E-7 deg
					WaypointInfo_Add.Altitude = 100;// the gps position of the waypoint // in dm
					WaypointInfo_Add.Status = 1;// the gps position of the waypoint // validity of data
					WaypointInfo_Add.Heading = 0; // orientation, 0 no action, 1...360 fix heading, neg. = Index to POI in WP List
					WaypointInfo_Add.ToleranceRadius = 2;    		// in meters, if the MK is within that range around the target, then the next target is triggered
					WaypointInfo_Add.HoldTime = 0;                   // in seconds, if the was once in the tolerance area around a WP, this time defines the delay before the next WP is triggered
					WaypointInfo_Add.Event_Flag = 0;                 // future implementation and simulation
					WaypointInfo_Add.Index = 1;              		// to indentify different waypoints, workaround for bad communications PC <-> NC
					WaypointInfo_Add.Type = POINT_TYPE_WP;                       // typeof Waypoint
					WaypointInfo_Add.WP_EventChannelValue = 30;  		// Will be transferred to the FC and can be used as Poti value there
					WaypointInfo_Add.AltitudeRate = 30;           	// rate to change the setpoint in steps of 0.1m/s
					WaypointInfo_Add.Speed = 7;                      // rate to change the Position(0 = max) in steps of 0.1m/s
					WaypointInfo_Add.CamAngle = 108;                   // Camera servo angle in degree (121 -> POI-Automatic since V2.20)
					WaypointInfo_Add.Name[0] = 'S';                	// Name of that point (ASCII)
					WaypointInfo_Add.Name[1] = 'P';                	// Name of that point (ASCII)
					WaypointInfo_Add.Name[2] = 'D';                	// Name of that point (ASCII)
					WaypointInfo_Add.Name[3] = 0;                	// Name of that point (ASCII)
					WaypointInfo_Add.AutoPhotoDistance = 0;  		// in [m]
					WaypointInfo_Add.reserve[0] = 0;
					break;
				default :
						{
						//WaypointInfo_Add.Position.Longitude = 143139817; // the gps position of the waypoint // in 1E-7 deg
						//WaypointInfo_Add.Position.Latitude = 483378862;// the gps position of the waypoint // in 1E-7 deg
						//WaypointInfo_Add.Position.Altitude = 50;// the gps position of the waypoint // in dm
						//WaypointInfo_Add.Position.Status = NEWDATA;// the gps position of the waypoint // validity of data
						WaypointInfo_Add.Longitude = 143264154; // the gps position of the waypoint // in 1E-7 deg
						WaypointInfo_Add.Latitude = 483359296;// the gps position of the waypoint // in 1E-7 deg
						WaypointInfo_Add.Altitude = 100;// the gps position of the waypoint // in dm
						WaypointInfo_Add.Status = 1;// the gps position of the waypoint // validity of data
						WaypointInfo_Add.Heading = 0; // orientation, 0 no action, 1...360 fix heading, neg. = Index to POI in WP List
						WaypointInfo_Add.ToleranceRadius = 2;    		// in meters, if the MK is within that range around the target, then the next target is triggered
						WaypointInfo_Add.HoldTime = 2;                   // in seconds, if the was once in the tolerance area around a WP, this time defines the delay before the next WP is triggered
						WaypointInfo_Add.Event_Flag = 0;                 // future implementation and simulation
						WaypointInfo_Add.Index = 1;              		// to indentify different waypoints, workaround for bad communications PC <-> NC
						WaypointInfo_Add.Type = POINT_TYPE_WP;                       // typeof Waypoint
						WaypointInfo_Add.WP_EventChannelValue = 30;  		// Will be transferred to the FC and can be used as Poti value there
						WaypointInfo_Add.AltitudeRate = 30;           	// rate to change the setpoint in steps of 0.1m/s
						WaypointInfo_Add.Speed = 7;                      // rate to change the Position(0 = max) in steps of 0.1m/s
						WaypointInfo_Add.CamAngle = 108;                   // Camera servo angle in degree (121 -> POI-Automatic since V2.20)
						WaypointInfo_Add.Name[0] = 'S';                	// Name of that point (ASCII)
						WaypointInfo_Add.Name[1] = 'P';                	// Name of that point (ASCII)
						WaypointInfo_Add.Name[2] = 'Z';                	// Name of that point (ASCII)
						WaypointInfo_Add.Name[3] = 0;                	// Name of that point (ASCII)
						WaypointInfo_Add.AutoPhotoDistance = 0;  		// in [m]
						WaypointInfo_Add.reserve[0] = 0;
						break;
						}
			}	
	return(WaypointInfo_Add );
}

struct WayPointStruct AddWaypointInfo(int Latitude, int Longitude, int Altitude, int WayPointIndex, int FlyingSpeed){
									//character for echo
	struct WayPointStruct WaypointInfo_Add;
	WaypointInfo_Add.Longitude = Longitude; // the gps position of the waypoint // in 1E-7 deg
	WaypointInfo_Add.Latitude = Latitude;// the gps position of the waypoint // in 1E-7 deg
	WaypointInfo_Add.Altitude = Altitude;// the gps position of the waypoint // in dm
	WaypointInfo_Add.Status = 1;// the gps position of the waypoint // validity of data
	WaypointInfo_Add.Heading = 0; // orientation, 0 no action, 1...360 fix heading, neg. = Index to POI in WP List
	WaypointInfo_Add.ToleranceRadius = 3;    		// in meters, if the MK is within that range around the target, then the next target is triggered
	WaypointInfo_Add.HoldTime = 5;                   // in seconds, if the was once in the tolerance area around a WP, this time defines the delay before the next WP is triggered
	WaypointInfo_Add.Event_Flag = 0;                 // future implementation and simulation
	WaypointInfo_Add.Index = 1;              		// to indentify different waypoints, workaround for bad communications PC <-> NC
	WaypointInfo_Add.Type = POINT_TYPE_WP;                       // typeof Waypoint
	WaypointInfo_Add.WP_EventChannelValue = 30;  		// Will be transferred to the FC and can be used as Poti value there
	WaypointInfo_Add.AltitudeRate = 30;           	// rate to change the setpoint in steps of 0.1m/s
	WaypointInfo_Add.Speed = FlyingSpeed;                      // rate to change the Position(0 = max) in steps of 0.1m/s
	WaypointInfo_Add.CamAngle = -1;                   // Camera servo angle in degree (121 -> POI-Automatic since V2.20)
	WaypointInfo_Add.Name[0] = 'S';                	// Name of that point (ASCII)
	WaypointInfo_Add.Name[1] = 'P';                	// Name of that point (ASCII)
	WaypointInfo_Add.Name[2] = 'D';                	// Name of that point (ASCII)
	WaypointInfo_Add.Name[3] = 0;                	// Name of that point (ASCII)
	WaypointInfo_Add.AutoPhotoDistance = 0;  		// in [m]
	WaypointInfo_Add.reserve[0] = 0;
	
	return(WaypointInfo_Add );
}

void create_waypoint(serial_data_struct* pdata_package_waypointGenerate, int Latitude, int Longitude, int Altitude, int WayPointIndex, int FlyingSpeed){
									//character for echo
	//WaypointInfo =  GetWaypointInfo(WayPointIndex);
	WaypointInfo =  AddWaypointInfo(Latitude, Longitude, Altitude, WayPointIndex,FlyingSpeed);
	//printf("WaypointInfo_Add.Position.Longitude%ld ", WaypointInfo.Longitude);
	//printf("WaypointInfo_Add.Position.Latitude%ld ", WaypointInfo.Latitude);
	//printf("WaypointInfo_Add.Headibng%d, %d ", WaypointInfo.Heading,sizeof(WaypointInfo.Heading));
	u8 *tmpData = (unsigned char *) &WaypointInfo;
	for (int i = 0; i < sizeof(struct WayPointStruct); ++i)
	{
		//printf("|%d|: %d ", i, tmpData[i]);
		pdata_package_waypointGenerate->data[i] = tmpData[i];
	}
}

void sendWayPoint(int Latitude, int Longitude, int Altitude, int WayPointIndex, int FlyingSpeed)
{
			create_waypoint(&data_package_waypoint, Latitude, Longitude, Altitude, WayPointIndex,FlyingSpeed);
			create_serial_frame(2, 'w', sizeof(struct WayPointStruct), &data_package_waypoint ); 
			transmit_data( &data_package_waypoint );
			//receive_data(&data_package_receive_kopter);
			usleep(5000);
			create_waypoint(&data_package_sendTarget, Latitude, Longitude, Altitude, WayPointIndex,FlyingSpeed);
			create_serial_frame(2, 's', sizeof(struct WayPointStruct), &data_package_sendTarget ); 
			transmit_data( &data_package_sendTarget );
			//receive_data(&data_package_receive_kopter);
			usleep(5000);
}
