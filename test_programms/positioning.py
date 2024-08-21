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

serialPort = serial.Serial(port, baudrate = baud, timeout = 0.5)

def GPS_function():

		gps_update = {"lat" : 47.00, "lon" : 47.00, "speed" : 0.00,"altitude":0.00, "track" : 0.00, "sats":0}

		stream = serial.Serial(port, 9600, timeout=3)
		nmr = NMEAReader(stream)
		(raw_data, parsed_data) = nmr.read()

		
		if hasattr(parsed_data, "lat"):

			if parsed_data.lat != '':
				gps_update["lat"] = float(parsed_data.lat)

			if parsed_data.lon != '':
				gps_update["lon"] = float(parsed_data.lon)


		if hasattr(parsed_data, "alt"):

			if parsed_data.alt != '':
				gps_update["altitude"] = float(parsed_data.alt)


		if hasattr(parsed_data, "spd"):

			if parsed_data.spd != '':
				gps_update["speed"] = float(parsed_data.spd)
				
				
		if hasattr(parsed_data, "numSV"):

			if parsed_data.numSV != '':
				gps_update["sats"] = float(parsed_data.numSV)
				
				
		if hasattr(parsed_data, "cog"):
			if parsed_data.cog != '':
				gps_update["track"] = float(parsed_data.cog)

		return gps_update


print(GPS_function())

