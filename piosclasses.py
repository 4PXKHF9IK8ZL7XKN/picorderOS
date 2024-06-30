#!/usr/bin/python
print("Exspand Classes")
import os
import numpy
import time
import datetime
import json
import random
import math
import psutil
import json
import pika
import ast

from multiprocessing import Process,Queue,Pipe
from objects import *
from random import randint
from array import *
import pandas as pd

#	PLARS (Picorder Library Access and Retrieval System) aims to provide a
#	single surface for storing and retrieving data for display in any of the
#	different Picorder screen modes.



if not configure.pc:
	import os
	
if configure.bme:
	import adafruit_bme680
	import busio as io
	
if configure.sensehat:
	# instantiates and defines paramaters for the sensehat

	from sense_hat import SenseHat

	# instantiate a sensehat object,
	sense = SenseHat()

	# Initially clears the LEDs once loaded
	sense.clear()

	# Sets the IMU Configuration.
	sense.set_imu_config(True,False,False)

	# Prepares an array of 64 pixel triplets for the Sensehat moire display
	moire=[[0 for x in range(3)] for x in range(64)]


if configure.envirophat:
	from envirophat import light, weather, motion, analog

# support for the MLX90614 IR Thermo
if configure.ir_thermo:
	import busio as io
	import adafruit_mlx90614

# These imports are for the Sin and Tan waveform generators
if configure.system_vitals:
	import psutil
	import math

if configure.pocket_geiger:
	from PiPocketGeiger import RadiationWatch

if configure.amg8833:
	import adafruit_amg88xx
	import busio
	i2c = busio.I2C(configure.PIN_SCL, configure.PIN_SDA)
	amg = adafruit_amg88xx.AMG88XX(i2c)

if configure.EM:
	from modulated_em import *

# An object to store each sensor value and context.
class Fragment(object):

	__slots__ = ('value','mini','maxi','dsc','sym','dev','timestamp','position')

	def __init__(self,mini,maxi,dsc,sym,dev):
		self.mini = mini
		self.maxi = maxi
		self.dsc = dsc
		self.dev = dev
		self.sym = sym
		self.value = 47
		self.timestamp = self.value
		self.position = [self.value,self.value]

	# Sets the value and timestamp for the fragment.
	def set(self,value, timestamp, position):
		self.value = value
		self.timestamp = time.time()
		self.position[0],self.position[1] = position

	# Returns all the data for the fragment.
	def get(self):
		return [self.value, self.mini, self.maxi, self.dsc, self.sym, self.dev, self.timestamp, self.position[0], self.position[1]]

	# Returns only the info constants for this fragment
	def get_info(self):
		return [self.mini, self.maxi, self.dsc, self.sym, self.dev]
	
class Sensor(object):
	def __init__(self):
			self.sensorlist = []		
			self.gps_speed = Fragment(0.0,0.0,"GPS Speed","kn", "gps")
			
			if configure.system_vitals:
				self.totalmem = psutil.virtual_memory()
				self.deg_sym = '\xB0'
				self.cputemp = Fragment(0, 100, "CpuTemp", self.deg_sym + "c", "RaspberryPi")
				self.cpuperc = Fragment(0,100,"CpuPercent","%","Raspberry Pi")
				self.virtmem = Fragment(0,self.totalmem,"VirtualMemory","b","RaspberryPi")
				self.bytsent = Fragment(0,100000,"BytesSent","b","RaspberryPi")
				self.bytrece = Fragment(0, 100000,"BytesReceived","b","RaspberryPi")
			if generators:	
				self.sinewav = Fragment(-100,100,"SineWave", "","RaspberryPi")
				self.tanwave = Fragment(-500,500,"TangentWave", "","RaspberryPi")
				self.coswave = Fragment(-100,100,"CosWave", "","RaspberryPi")
				self.sinwav2 = Fragment(-100,100,"SineWave2", "","RaspberryPi")
			if configure.sensehat:	
				self.sh_temp = Fragment(-40,120,"Thermometer",self.deg_sym + "c", "sensehat")
				self.sh_humi = Fragment(0,100,"Hygrometer", "%", "sensehat")
				self.sh_baro = Fragment(260,1260,"Barometer","hPa", "sensehat")
				self.sh_magx = Fragment(-500,500,"MagnetX","G", "sensehat")
				self.sh_magy = Fragment(-500,500,"MagnetY","G", "sensehat")
				self.sh_magz = Fragment(-500,500,"MagnetZ","G", "sensehat")
				self.sh_accx = Fragment(-500,500,"AccelX","g", "sensehat")
				self.sh_accy = Fragment(-500,500,"AccelY","g", "sensehat")
				self.sh_accz = Fragment(-500,500,"AccelZ","g", "sensehat")
			if configure.ir_thermo:
				self.irt_ambi = Fragment(0,80,"IR ambient [mlx]","C",self.deg_sym + "c")
				self.irt_obje = Fragment(0,80,"IR object [mlx]","C",self.deg_sym + "c")
			if configure.envirophat:
				self.ep_temp = Fragment(0,65,"Thermometer",self.deg_sym + "c","Envirophat")
				self.ep_colo = Fragment(20,80,"Colour", "RGB","Envirophat")
				self.ep_baro = Fragment(260,1260,"Barometer","hPa","Envirophat")
				self.ep_magx = Fragment(-500,500,"Magnetomer X","G","Envirophat")
				self.ep_magy = Fragment(-500,500,"Magnetomer Y","G","Envirophat")
				self.ep_magz = Fragment(-500,500,"Magnetomer Z","G","Envirophat")
				self.ep_accx = Fragment(-500,500,"Accelerometer X (EP)","g","Envirophat")
				self.ep_accy = Fragment(-500,500,"Accelerometer Y (EP)","g","Envirophat")
				self.ep_accz = Fragment(-500,500,"Accelerometer Z (EP)","g","Envirophat")
			if configure.bme:	
				self.bme_temp = Fragment(-40,85,"Thermometer",self.deg_sym + "c", "BME680")
				self.bme_humi = Fragment(0,100,"Hygrometer", "%", "BME680")
				self.bme_press = Fragment(300,1100,"Barometer","hPa", "BME680")
				self.bme_voc = Fragment(300000,1100000,"VOC","KOhm", "BME680")
			if configure.pocket_geiger:	
				self.radiat = Fragment(0.0, 10000.0, "Radiation", "ur/h", "pocketgeiger")
			if configure.amg8833:
				self.amg_high = Fragment(0.0, 80.0, "IRHigh", self.deg_sym + "c", "amg8833")
				self.amg_low = Fragment(0.0, 80.0, "IRLow", self.deg_sym + "c", "amg8833")
			
			configure.sensor_info = self.get_all_info()
			
			
	def get_all_info(self):
		info = self.get()

		allinfo = []
		for fragment in info:
			thisfrag = [fragment.dsc,fragment.dev,fragment.sym, fragment.mini, fragment.maxi]
			allinfo.append(thisfrag)
		return allinfo
		
	def get(self):
		#sensorlist holds all the data fragments to be handed to plars.
		self.sensorlist = []

		#timestamp for this sensor get.
		timestamp = time.time()
		position = GPS_DATA
		
		self.gps_speed.set(0,timestamp, position)
			
		if configure.bme:
			self.bme_temp.set(0,timestamp, position)
			self.bme_humi.set(0,timestamp, position)
			self.bme_press.set(0,timestamp, position)
			self.bme_voc.set(0 / 1000,timestamp, position)
			
			self.sensorlist.extend((self.bme_temp,self.bme_humi,self.bme_press, self.bme_voc))
			
		if configure.envirophat: 
			magdata = {"x":0,"y":0,"z":0}
			acceldata = {"x":0,"y":0,"z":0}
			
			self.sh_temp.set(0,timestamp, position)
			self.sh_humi.set(0,timestamp, position)
			self.sh_baro.set(0,timestamp, position)
			self.sh_magx.set(magdata["x"],timestamp, position)
			self.sh_magy.set(magdata["y"],timestamp, position)
			self.sh_magz.set(magdata["z"],timestamp, position)
			self.sh_accx.set(acceldata['x'],timestamp, position)
			self.sh_accy.set(acceldata['y'],timestamp, position)
			self.sh_accz.set(acceldata['z'],timestamp, position)

			self.sensorlist.extend((self.sh_temp, self.sh_baro, self.sh_humi, self.sh_magx, self.sh_magy, self.sh_magz, self.sh_accx, self.sh_accy, self.sh_accz))
			
		if configure.pocket_geiger:	
			data = {"uSvh":0}
			rad_data = float(data["uSvh"])
			
			self.radiat.set(rad_data*100, timestamp, position)
			self.sensorlist.append(self.radiat)
			
		if configure.amg8833:
			data = numpy.array([0,80])
			
			high = numpy.max(data)
			low = numpy.min(data)
			
			self.amg_high.set(high,timestamp, position)
			self.amg_low.set(low,timestamp, position)

			self.sensorlist.extend((self.amg_high, self.amg_low))
			
		if configure.sensehat:
			self.mag_values = {0:0,1:0,2:0}
			self.acc_values = {0:0,1:0,2:0}
			
			self.ep_temp.set(0,timestamp, position)
			self.ep_colo.set(0,timestamp, position)
			self.ep_baro.set(0, timestamp, position)
			self.ep_magx.set(self.mag_values[0],timestamp, position)
			self.ep_magy.set(self.mag_values[1],timestamp, position)
			self.ep_magz.set(self.mag_values[2],timestamp, position)
			self.ep_accx.set(self.acc_values[0],timestamp, position)
			self.ep_accy.set(self.acc_values[1],timestamp, position)
			self.ep_accz.set(self.acc_values[2],timestamp, position)

			self.sensorlist.extend((self.ep_temp, self.ep_baro, self.ep_colo, self.ep_magx, self.ep_magy, self.ep_magz, self.ep_accx, self.ep_accy, self.ep_accz))
		
		if configure.system_vitals:	
			self.cputemp.set(0,timestamp, position)
			self.cpuperc.set(float(psutil.cpu_percent()),timestamp, position)
			self.virtmem.set(float(psutil.virtual_memory().available * 0.0000001),timestamp, position)
			self.bytsent.set(float(psutil.net_io_counters().bytes_recv * 0.00001),timestamp, position)
			self.bytrece.set(float(psutil.net_io_counters().bytes_recv * 0.00001),timestamp, position)
			
			self.sinewav.set(float(1*100),timestamp, position)
			self.tanwave.set(float(1*100),timestamp, position)
			self.coswave.set(float(1*100),timestamp, position)
			self.sinwav2.set(float(1*100),timestamp, position)
			
			self.sensorlist.extend((self.cputemp, self.cpuperc, self.virtmem, self.bytsent, self.bytrece))
		if generators:
			self.sensorlist.extend((self.sinewav, self.tanwave, self.coswave, self.sinwav2)) 
		
		configure.max_sensors[0] = len(self.sensorlist)
		
		return self.sensorlist
		
	def update_bme680(self,var1,var2,var3,var4,var5):
		timestamp = time.time()
		position = GPS_DATA
		self.bme_temp.set(var1,timestamp, position)
		self.bme_humi.set(var2,timestamp, position)
		self.bme_press.set(var3,timestamp, position)
		self.bme_voc.set(var4,timestamp, position)			
		self.sensorlist.extend((self.bme_temp,self.bme_humi,self.bme_press, self.bme_voc))	
		return
		
	def update_system_vitals(self,var1,var2,var3,var4,var5,var6,var7,var8):
		timestamp = time.time()
		position = GPS_DATA
		self.cputemp.set(var3,timestamp, position)
		self.cpuperc.set(float(var4),timestamp, position)
		self.virtmem.set(float(var5),timestamp, position)
		self.bytsent.set(float(var7),timestamp, position)
		self.bytrece.set(float(var8),timestamp, position)
		self.sensorlist.extend((self.cputemp, self.cpuperc, self.virtmem, self.bytsent, self.bytrece))
		return


