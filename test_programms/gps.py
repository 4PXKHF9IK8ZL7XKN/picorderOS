#!/usr/bin/python
# -*- coding: utf-8 -*-
# Filename: gps.py

import serial
import time
import datetime

from serial import Serial

#ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=3)
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=3)


def GPS_function(select):

	if select:
		mode = 1 
	else:
		mode = 0

	NEMA_DICT = []
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

	# reading in serial stream
	while True:
		data_array = [0]
		while ser.inWaiting() > 0:
			if mode == 0:
				data = ser.read(ser.inWaiting())
			if mode == 1:
				data = ser.readline(ser.inWaiting())
			# converting bytes to string
			data = data.decode()
			# removing special symbols like linefeed , return 
			data = data.replace('\n','')
			data = data.replace('\t','')
			data = data.replace('\r','')
			# creating a array by coma split
			data_array = data.split(',')
			#print("Array:", data_array )
			# creating a matrix by adding the array in the NEMA array
			NEMA_DICT.append(data_array)
		#stopping the serial read when i detect the last sentence from a NEMA block 
		if mode == 0:
			if data_array[0] == '$GPGLL':
				break
		if mode == 1:
			if data_array[0] == '$GNVTG':
				break
		
	for item in NEMA_DICT:
		#print("item", item )
		if "$GPRMC" == item[0] or "$GNRMC" == item[0]: 
			if item[2] == 'V':
				print("no satellite data available")
				return 1, "no satellite data available"
			#print("---Parsing GPRMC---")
			time0, time1, time2 = int(item[1][0:2]), int(item[1][2:4]), int( item[1][4:6])
			lat0, lat1, lat2 ,lat3 ,lat4 = decode(item[3]) #latitude
			lat_compat = round(float(item[3])*0.01,10) # moving dot super magic
			dirLat = item[4]      #latitude direction N/S
			lon0, lon1, lon2, lon3, lon4 = decode(item[5]) #longitute
			lon_compat = round(float(item[5])*0.01,10) # moving dot super magic
			dirLon = item[6]      #longitude direction E/W
			speed = float(item[7])      #Speed in knots
			
			if item[8] == '':
				trCourse = 0
			else:
				trCourse = float(item[8])   #True course			
			
			date0, date1, date2 = int(item[9][0:2]), int(item[9][2:4]), int(item[9][4:6]) #date
			# thanks to this short display of the date do i have to fix it when i m dead
			epoch = datetime.datetime(date2+2000, date1, date0, time0, time1, time2).timestamp() 
		if '$GPGSV' == item[0]:
			sat_viewA = int(item[1])
		if '$GPGLL' == item[0]:
			pos_val = item[6]
		if '$GPGGA' == item[0]:
			sat_viewB = int(item[7])
			if item[9] != '':
				alt = float(item[9])
			
	if sat_viewB == 0:
		sat_view = sat_viewA
	else:
		sat_view = sat_viewB
				
	return lat_compat, lon_compat, lat0, lat1, lat2 ,lat3 ,lat4 , dirLat ,lon0 , lon1, lon2, lon3, lon4, dirLon, speed, trCourse, alt, pos_val, sat_view, epoch

def decode(coord):
    #Converts DDDMM.MMMMM > DD deg MM.MMMMM min
    x = coord.split(".")
    head = x[0]
    tail = int(x[1])
    deg = int(head[0:-2])
    min = int(head[-2:])
    return deg , "deg" , min , tail , "min"



print(GPS_function(False))

