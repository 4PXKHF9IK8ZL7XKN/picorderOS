#!/usr/bin/python
# -*- coding: utf-8 -*-
# Filename: gps.py

import serial
import time
import datetime
from pynmeagps import NMEAReader

from serial import Serial

#ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=3)
#ser = serial.Serial('/dev/ttyACM0', 115200, timeout=3)

port = '/dev/ttyACM0'
baud = 115200

def GPS_function(select):

	if select:
		mode = 1 
	else:
		mode = 0

	NMEA_DICT = []
	data = ''
	
	time = None
	lat = None
	dirLat = None
	lon = None
	dirLon = None
	speed = None
	trCourse = None
	date = None	
	sat_view = 0
	sat_viewA = 0
	sat_viewB = 0
	pos_val = 'N'
	alt = 0
	lat_compat = 0
	lon_compat = 0
	
	ser = serial.Serial(port, baud, timeout=3)

	# reading in serial stream
	while True:
		data_array = [0]
		while ser.inWaiting() > 0:
			if mode == 0:
				data = ser.read(ser.inWaiting())
			if mode == 1:
				data = ser.readline(ser.inWaiting())
			# converting bytes to string
			data_stream = data.decode()
			data = data_stream
			# removing special symbols like linefeed , return 
			data = data.replace('\n','')
			data = data.replace('\t','')
			data = data.replace('\r','')
			# creating a array by coma split
			data_array = data.split(',')
			if  data_array[0] != '$GPTXT':
				#adding the payload to may data to get the abbility to later query the data too in relation 
				payload = NMEAReader.parse(data_stream,validate=0)
				#print("payload:", payload )
				# creating a matrix by adding the array in the NEMA array
				data_array.append(payload)
				NMEA_DICT.append(data_array)
		#stopping the serial read when i detect the last sentence from a NEMA block 
		if mode == 0:
			if data_array[0] == '$GPGLL':
				break
		if mode == 1:
			if data_array[0] == '$GNVTG':
				break
		
	for item in NMEA_DICT:
		#print("item", item )	
		if "$GPRMC" == item[0] or "$GNRMC" == item[0]: 
			if item[2] == 'V':
				print("no satellite data available")
				return 1, "no satellite data available"
			#print("---Parsing GPRMC---")
			time0, time1, time2 = int(item[1][0:2]), int(item[1][2:4]), int( item[1][4:6])
			
			lat0, lat1, lat2 ,lat3 ,lat4 = decode(item[3]) #latitude			
			if hasattr(item[13], "lat"):
				if item[13].lat != '':
					lat_compat = float(item[13].lat)
					
			dirLat = item[4]      #latitude direction N/S
			if hasattr(item[13], "NS"):
				if item[13].NS != '':
					dirLat = str(item[13].NS)			
			
			lon0, lon1, lon2, lon3, lon4 = decode(item[5]) #longitute		
			if hasattr(item[13], "lon"):
				if item[13].lon != '':
					lon_compat = float(item[13].lon)	
										
			dirLon = item[6]      #longitude direction E/W	
			if hasattr(item[13], "EW"):
				if item[13].EW != '':
					dirLon = str(item[13].EW)			
			
			# setting speed from own parsing and then try pynmeagps
			speed = float(item[7])      #Speed in knots		
			if hasattr(item[13], "spd"):
				if item[13].lon != '':
					speed = float(item[13].spd)		
			
			if item[8] == '':
				trCourse = 0
			else:
				trCourse = float(item[8])   #True course
				if hasattr(item[13], "cog"):
					if item[13].cog != '':
						speed = float(item[13].cog)					
			
			date0, date1, date2 = int(item[9][0:2]), int(item[9][2:4]), int(item[9][4:6]) #date
			# thanks to this short display of the date do i have to fix it when i m dead
			epoch = datetime.datetime(date2+2000, date1, date0, time0, time1, time2).timestamp() 
		if '$GPGSV' == item[0]:
			sat_viewA = int(item[1])
		if '$GPGLL' == item[0]:
			pos_val = item[6]
			if hasattr(item[8], "status"):
				if item[8].status != '':
					pos_val = str(item[8].status)	
			
		if '$GPGGA' == item[0]:
			sat_viewB = int(item[7])
			if hasattr(item[15], "numSV"):
				if item[15].numSV != '':
					sat_viewB = float(item[15].numSV)	
			
			if item[9] != '':
				alt = float(item[9])				
				if hasattr(item[15], "alt"):
					if item[15].alt != '':
						alt = float(item[15].alt)	
				
			
	if sat_viewB == 0:
		sat_view = sat_viewA
	else:
		sat_view = sat_viewB
		
	
		
	gps_update = {"lat" : lat_compat, "lon" : lon_compat, "speed" : speed, "altitude" : alt, "track" : trCourse, "sats" : sat_view , "lat0" : lat0 , "lat1" : lat1, "lat2" : lat2 ,"lat3" : lat3 ,"lat4" : lat4 , "dirLat" : dirLat, "lon0" : lon0 , "lon1" : lon1, "lon2" : lon2, "lon3" : lon3, "lon4" : lon4, "dirLon" : dirLon,"pos_val" : pos_val, "time" : epoch}
				
	return gps_update

def decode(coord):
    #Converts DDDMM.MMMMM > DD deg MM.MMMMM min
    x = coord.split(".")
    head = x[0]
    tail = int(x[1])
    deg = int(head[0:-2])
    min = int(head[-2:])
    return deg , "deg" , min , tail , "min"



print(GPS_function(False))

