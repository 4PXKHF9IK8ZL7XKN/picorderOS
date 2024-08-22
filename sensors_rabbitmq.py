#!/usr/bin/env python
# -*- coding: utf-8 -*-
from objects import *
import sys
import time
import math
import numpy
import threading
import pika
import signal
import serial
import datetime
import picos_pika_worker as publisher_worker
from pynmeagps import NMEAReader
import RPi.GPIO as GPIO
import busio as io
from datetime import timedelta

from multiprocessing import Process,Queue,Pipe
# the following is a sensor module for use with the PicorderOS
print("Loading Unified Sensor Module")

generators = True
DEBUG = False

meta_massage = ""
local_gps = [37.7820885,-122.3045112,configure.rabbitmq_tag]


# Delcares the IRQ Pins for Cap Touch 
BUTTON_GPIOA = 17
BUTTON_GPIOB = 27

# set the BUS Freq
I2C_FRQ = 100000

# A Timer to reset the interrupt, when the data was not pulled correctly , otherwise the trigger stucks
WAIT_TIME_SECONDS = 0.5

# config the i2c device
i2c = io.I2C(configure.PIN_SCL, configure.PIN_SDA, frequency=I2C_FRQ)

# needs configure flag
if configure.SCD4X:
	import adafruit_scd4x

if configure.gps:
	# configure serial port for GPS
	port = '/dev/ttyACM0'
	baud = 115200
	serialPort = serial.Serial(port, baudrate = baud, timeout = 0.5)

if not configure.pc:
	import os
	
	
if configure.input_cap_mpr121:
	import adafruit_mpr121
	import board
	import busio
	import signal
	
	# Note you can optionally change the address of the device:
	mpr121A = adafruit_mpr121.MPR121(i2c, address=0x5A)
	mpr121B = adafruit_mpr121.MPR121(i2c, address=0x5B)	
	
if configure.bme:
	import adafruit_bme680
	
	
if configure.bmp280:
	import adafruit_bmp280
	
if configure.LSM6DS3TR:
	from adafruit_lsm6ds.lsm6ds3 import LSM6DS3
	
if configure.LIS3MDL:
	import adafruit_lis3mdl
		
if configure.APDS9960:
	import adafruit_apds9960.apds9960
	
if configure.SHT30:
	import adafruit_sht31d
	
	
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

# support for the MLX90614 IR Thermoif SCD4X:
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
	amg = adafruit_amg88xx.AMG88XX(i2c)

if configure.EM:
	from modulated_em import *

if configure.rabbitmq_remote:
	credentials = pika.PlainCredentials(configure.rabbitmq_user,configure.rabbitmq_password)
	connection = pika.BlockingConnection(pika.ConnectionParameters(configure.rabbitmq_address,configure.rabbitmq_port,configure.rabbitmq_vhost,credentials))
	channel = connection.channel()
else:
	connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
	channel = connection.channel()
    
def declare_channel():
	# Setup Channels for Sensors
	channel.exchange_declare(exchange='sensor_data', exchange_type='topic')
	channel.queue_declare(queue='sensor_metadata')
	# cleanup entreys , we could have multible index
	channel.queue_purge(queue='sensor_metadata')

    
def publish(IN_routing_key,data):
	stack = 'sensor_data'
	if IN_routing_key == 'sensor_metadata':
		stack = ''
   
	routing_key = str(IN_routing_key)
	message = str(data)
	time_unix = time.time()
	try:
		if message is not None:
			channel.basic_publish(exchange=stack, routing_key=routing_key, body=message)
		else:
			print("Is that a buffer underflow?")
	except Exception as e:
		print("An error occurred:",e)
		try:
			raise Exception('Terminating')
		finally:
			os._exit(1)
		
		
		
	if DEBUG:
		print(f" {time_unix} [x] Sent {stack} {routing_key}:{message}")

    
def disconnect():
    connection.close()
        
def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)
     
    	
def button_callbackA(channel):
	touchA_dict = {"DICT":"A",0:False,1:False,2:False,3:False,4:False,5:False,6:False,7:False,8:False,9:False,10:False,11:False}
	for i in range(12):
		touchA_dict[i] = mpr121A[i].value
	
	pikaworkerA = threading.Thread(target = publisher_worker.main_pika_worker, args = ("touch",touchA_dict))
	pikaworkerA.start()
	pikaworkerA.join()

def button_callbackB(channel):
	touchB_dict = {"DICT":"B",0:False,1:False,2:False,3:False,4:False,5:False,6:False,7:False,8:False,9:False,10:False,11:False}
	for i in range(12):
		touchB_dict[i] = mpr121B[i].value

	pikaworkerB = threading.Thread(target = publisher_worker.main_pika_worker, args = ("touch",touchB_dict))
	pikaworkerB.start()
	pikaworkerB.join()
		

def reset():
	if configure.input_cap_mpr121:
		if not GPIO.input(17) or not GPIO.input(27):
			#print("RESETA", touchA_dict)
			#print("RESETB", touchB_dict)
			for i in range(12):
				null = mpr121B[i].value
				null = mpr121A[i].value


# This Class helps to start a thread that runs a timer non blocking to reset the IRQ signal on the mpr121
class Job(threading.Thread):
    def __init__(self, interval, execute, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.interval = interval
        self.execute = execute
        self.args = args
        self.kwargs = kwargs

    def stop(self):
                self.stopped.set()
                self.join()
    def run(self):
            while not self.stopped.wait(self.interval.total_seconds()):
                self.execute(*self.args, **self.kwargs)

def decode(coord):
    #Converts DDDMM.MMMMM > DD deg MM.MMMMM min
    x = coord.split(".")
    head = x[0]
    tail = int(x[1])
    deg = int(head[0:-2])
    min = int(head[-2:])
    return deg , "deg" , min , tail , "min"


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
	lat0 = 0
	lat1 = 0
	lat2 = 0
	lat3 = 0
	lat4 = 0
	lon0 = 0
	lon1 = 0
	lon2 = 0
	lon3 = 0
	lon4 = 0
	
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
				return False
			#print("---Parsing GPRMC---")
			time0, time1, time2 = int(item[1][0:2]), int(item[1][2:4]), int( item[1][4:6])
			
			lat0, lat1, lat2 ,lat3 ,lat4 = decode(item[3]) #latitude
			lat_compat = float(item[3])
			if hasattr(item[13], "lat"):
				if item[13].lat != '':
					lat_compat = float(item[13].lat)
					
			dirLat = item[4]      #latitude direction N/S
			if hasattr(item[13], "NS"):
				if item[13].NS != '':
					dirLat = str(item[13].NS)			
			
			lon0, lon1, lon2, lon3, lon4 = decode(item[5]) #longitute	
			lon_compat = float(item[5])
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
	

class sensor(object):

	# sensors should check the configuration flags to see which sensors are
	# selected and then if active should poll the sensor and append it to the
	# sensor array.

	def __init__(self):

		#set up the necessary info for the sensors that are active.

		# create a simple reference for the degree symbol since we use it a lot
		self.deg_sym = '\xB0'


		# add individual sensor module parameters below.
		#0				1			2		3		4
		#info = (lower range, upper range, unit, symbol)
		#'value','min','max','dsc','sym','dev','timestamp'
		

		# data fragments (objects that contain the most recent sensor value,
		# plus metadata for context) are called Fragment().
		
		# needs config flag
		if configure.SCD4X:
			self.scd4x = adafruit_scd4x.SCD4X(i2c)
			self.scd4x.start_periodic_measurement()
			self.scd4x_CO2 = 0000
			self.scd4x_temp = 0000
			self.scd4x_humi = 0000

	

		if configure.system_vitals:
			totalmem = float(psutil.virtual_memory().total) / 1024

		if configure.sensehat:
			self.ticks = 0
			self.onoff = 1

			# instantiate a sensehat object,
			self.sense = SenseHat()
			# Initially clears the LEDs once loaded
			self.sense.clear()
			# Sets the IMU Configuration.
			self.sense.set_imu_config(True,False,False)
			# activates low light conditions to not blind the user.
			self.sense.low_light = True

		if configure.ir_thermo:
			self.mlx = adafruit_mlx90614.MLX90614(i2c)
			
			

		if configure.envirophat: 
	
			self.ep_temp = 23.5
			self.ep_colo = [0,0,0]
			self.ep_baro = 0
			self.ep_magx = 0
			self.ep_magy = 0
			self.ep_magz = 0
			self.ep_accx = 0
			self.ep_accy = 0
			self.ep_accz = 0

		if configure.bme:
			# Create library object using our Bus I2C port
			self.bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, address=0x76, debug=False)
			self.bme680.sea_level_pressure = 1013.25
		
		if configure.bmp280:
			# Create library object using our Bus I2C port
			self.bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x77)
			self.bmp280.sea_level_pressure = 1013.25

		if configure.pocket_geiger:
			self.radiation = RadiationWatch(configure.PG_SIG,configure.PG_NS)
			self.radiation.setup()

		if configure.amg8833:
			self.thermal_frame = []
			
			
		if configure.LSM6DS3TR:
			self.lsm6ds3 = LSM6DS3(i2c)
	
		if configure.LIS3MDL:
			self.lis3mdl = adafruit_lis3mdl.LIS3MDL(i2c)
		
		if configure.APDS9960:
			self.apds9960 = adafruit_apds9960.apds9960.APDS9960(i2c)
			self.apds9960.enable_proximity = True
			
			# gesture is a blocking function and bad for i2c communication
			self.apds9960.enable_gesture = False
			self.apds9960.enable_color = True
	
		if configure.SHT30:
			self.sht30 = adafruit_sht31d.SHT31D(i2c)



	def get_gps(self):
		global local_gps
		# we get it anytime because its different per sensor read
		timestamp = time.time()
		position = [None, None, 0, 0, 0,0 , None , None, None, None ,None , None, None , None , None , None, None, None , None, timestamp, configure.rabbitmq_tag]
		# braching of local gps information , i want to attach local gps information to the sensor data, so that i can send them with the readings and wenn i combine the 2 devices, can i see wehre the data is from and dont have to puzzle data together later 
		if configure.gps:
			# when gps is on , try to read the data here and fill the variables to send it
			gps_data = GPS_function(False)
			if gps_data is False:
				position = [None, None, 0, 0, 0,0 , None , None, None, None ,None , None, None , None , None , None, None, None , None, timestamp, configure.rabbitmq_tag]
			else:
				position = [
				gps_data["lat"],
				gps_data["lon"],
				gps_data["speed"],
				gps_data["altitude"],
				gps_data["track"],
				gps_data["sats"],
				gps_data["lat0"],
				gps_data["lat1"],
				gps_data["lat2"],
				gps_data["lat3"],
				gps_data["lat4"],
				gps_data["dirLat"],
				gps_data["lon0"],
				gps_data["lon1"],
				gps_data["lon2"],
				gps_data["lon3"],
				gps_data["lon4"],
				gps_data["dirLon"],
				gps_data["pos_val"],
				gps_data["time"],
				configure.rabbitmq_tag
				]
			
		# this part stores gps data in a global to fill sensor data , when we dont have data do we fill a location thats known to be wrong but nice to know 
		if position[0] is not None and position[1] is not None :
			local_gps = position
		else:
			local_gps = [37.7820885,-122.3045112, 0, 0, 0,0 , 37 , 'deg', 78, 20885 , 'min' , 'N', 122 , 'deg' ,30 , 45112, 'min', 'W' , 'N', timestamp, configure.rabbitmq_tag]
		
		# any case retun, if its not none gets send
		return position 

	def get_thermal_frame(self):
		global local_gps
		self.thermal_frame = amg.pixels
		data = numpy.array(self.thermal_frame)
		high = numpy.max(data)
		low = numpy.min(data)
		# we get it anytime because its different per sensor read
		timestamp = time.time()
		
		return self.thermal_frame , timestamp ,local_gps[0], local_gps[1] ,configure.rabbitmq_tag


	def get_bme680(self):
		global local_gps
		self.bme680_temp = self.bme680.temperature
		self.bme680_humi = self.bme680.humidity
		self.bme680_press = self.bme680.pressure
		self.bme680_voc = self.bme680.gas / 1000
		self.bme680_alt = self.bme680.altitude
		# we get it anytime because its different per sensor read
		timestamp = time.time() 
		
		return self.bme680_temp,self.bme680_humi,self.bme680_press, self.bme680_voc, self.bme680_alt , timestamp ,local_gps[0], local_gps[1] ,configure.rabbitmq_tag
		
		
	def get_bmp280(self):
		global local_gps
		self.bmp280_temp = self.bmp280.temperature
		self.bmp280_press = self.bmp280.pressure
		self.bmp280_alt = self.bmp280.altitude
		# we get it anytime because its different per sensor read
		timestamp = time.time() 
		
		return self.bmp280_temp ,self.bmp280_press, self.bmp280_alt	, timestamp ,local_gps[0], local_gps[1] ,configure.rabbitmq_tag	
		
	def get_sht30(self):
		global local_gps
		self.sht30_temp = self.sht30.temperature
		self.sht30_rel_humi = self.sht30.relative_humidity
		# we get it anytime because its different per sensor read
		timestamp = time.time()
				
		return self.sht30_temp , self.sht30_rel_humi , timestamp ,local_gps[0], local_gps[1] ,configure.rabbitmq_tag
		
	def get_lsm6ds3(self):
		global local_gps
		self.lsm6ds3_accel_X, self.lsm6ds3_accel_Y, self.lsm6ds3_accel_Z = self.lsm6ds3.acceleration
		self.lsm6ds3_gyro_X, self.lsm6ds3_gyro_Y, self.lsm6ds3_gyro_Z = self.lsm6ds3.gyro
		# we get it anytime because its different per sensor read
		timestamp = time.time()
		
		return self.lsm6ds3_accel_X ,self.lsm6ds3_accel_Y, self.lsm6ds3_accel_Z, self.lsm6ds3_gyro_X, self.lsm6ds3_gyro_Y, self.lsm6ds3_gyro_Z , timestamp ,local_gps[0], local_gps[1] ,configure.rabbitmq_tag
		

	def get_lis3mdl(self):
		global local_gps
		self.lis3mdl_X, self.lis3mdl_Y, self.lis3mdl_Z = self.lis3mdl.magnetic
		# we get it anytime because its different per sensor read
		timestamp = time.time()
		
		return self.lis3mdl_X, self.lis3mdl_Y, self.lis3mdl_Z , timestamp ,local_gps[0], local_gps[1] ,configure.rabbitmq_tag
		
	def get_apds9960(self):
		global local_gps
		self.apds9960_proximity = self.apds9960.proximity
		self.apds9960_gesture = self.apds9960.gesture()
		self.apds9960_colore_r ,self.apds9960_colore_g ,self.apds9960_colore_b ,self.apds9960_colore_c = self.apds9960.color_data
		# we get it anytime because its different per sensor read
		timestamp = time.time()
		
		return self.apds9960_proximity, self.apds9960_gesture, self.apds9960_colore_r ,self.apds9960_colore_g ,self.apds9960_colore_b ,self.apds9960_colore_c, configure.rabbitmq_tag
		
		
	def get_scd4x(self):
		global local_gps
		try:
			if self.scd4x.data_ready:
				self.scd4x_CO2 = self.scd4x.CO2	
				self.scd4x_temp = self.scd4x.temperature			
				self.scd4x_humi = self.scd4x.relative_humidity
				
		except:
			pass		
		# we get it anytime because its different per sensor read
		timestamp = time.time()
		
		return self.scd4x_CO2, self.scd4x_temp, self.scd4x_humi , timestamp ,local_gps[0], local_gps[1] ,configure.rabbitmq_tag
		

	def get_sensehat(self):
		global local_gps
		magdata = sense.get_compass_raw()
		acceldata = sense.get_accelerometer_raw()

		self.sh_temp = sense.get_temperature()
		self.sh_humi = sense.get_humidity()
		self.sh_baro = sense.get_pressure()
		self.sh_magx = magdata["x"]
		self.sh_magy = magdata["y"]
		self.sh_magz = magdata["z"]
		self.sh_accx = acceldata['x']	
		self.sh_accy = acceldata['y']		
		self.sh_accz = acceldata['z']
		# we get it anytime because its different per sensor read
		timestamp = time.time()
		
			
		return self.sh_temp, self.sh_baro, self.sh_humi, self.sh_magx, self.sh_magy, self.sh_magz, self.sh_accx, self.sh_accy, self.sh_accz , timestamp ,local_gps[0], local_gps[1] ,configure.rabbitmq_tag
		
	def get_pocket_geiger(self):
		global local_gps
		data = self.radiation.status()
		rad_data = float(data["uSvh"])
		# times 100 to convert to urem/h
		self.radiat.set(rad_data*100, timestamp, position)	
		# we get it anytime because its different per sensor read
		timestamp = time.time()
		
		return self.radiat , timestamp ,local_gps[0], local_gps[1] ,configure.rabbitmq_tag
		
	# provides the basic definitions for the system vitals sensor readouts
	def get_system_vitals(self):
		global local_gps
		timestamp = time.time()
		if not configure.pc:
			f = os.popen("cat /sys/class/thermal/thermal_zone0/temp").readline()
			t = float(f[0:2] + "." + f[2:])
		else:
			t = float(47)
		
		time_now = time.time()
		start_time = psutil.boot_time()
		time_delta = time_now - start_time
		
		self.cpuload = psutil.getloadavg()
		self.cpuperc = (float(psutil.cpu_percent()))
		self.cputemp = psutil.sensors_temperatures()
		self.virtmem = (float(psutil.virtual_memory().available * 0.0000001))
		self.diskuse = psutil.disk_usage("/")
		self.uptime  = time_delta
		self.bytsent = (float(psutil.net_io_counters().bytes_sent * 0.00001))
		self.bytrece = (float(psutil.net_io_counters().bytes_recv * 0.00001))
		
		return self.uptime, self.cpuload ,self.cputemp, self.cpuperc, self.virtmem, self.diskuse, self.bytsent, self.bytrece , timestamp ,local_gps[0], local_gps[1] ,configure.rabbitmq_tag

	def get_envirophat(self):
		global local_gps
		self.rgb = light.rgb()
		self.analog_values = analog.read_all()
		self.mag_values = motion.magnetometer()
		self.acc_values = [round(x, 2) for x in motion.accelerometer()]
		self.ep_temp = weather.temperature()
		self.ep_colo = light.light()
		self.ep_baro = weather.pressure(unit='hpa')
		self.ep_magx = self.mag_values[0]
		self.ep_magy = self.mag_values[1]
		self.ep_magz = self.mag_values[2]
		self.ep_accx = self.acc_values[0]	
		self.ep_accy = self.acc_values[1]	
		self.ep_accz = self.acc_values[2]
		# we get it anytime because its different per sensor read
		timestamp = time.time()
			
		return self.ep_temp, self.ep_baro, self.ep_colo, self.ep_magx, self.ep_magy, self.ep_magz, self.ep_accx, self.ep_accy, self.ep_accz, configure.rabbitmq_tag
		
	def get_MLX90614(self):
		global local_gps	
		amb_temp = MLX90614.data_to_temp(MLX90614.get_amb_temp)	
		obj_temp = MLX90614.data_to_temp(MLX90614.get_obj_temp)		
		# we get it anytime because its different per sensor read
		timestamp = time.time()
		
		return amb_temp, obj_temp, configure.rabbitmq_tag


	def end(self):
		if configure.pocket_geiger:
			self.radiation.close()


class MLX90614():

	MLX90614_RAWIR1=0x04
	MLX90614_RAWIR2=0x05
	MLX90614_TA=0x06
	MLX90614_TOBJ1=0x07
	MLX90614_TOBJ2=0x08

	MLX90614_TOMAX=0x20
	MLX90614_TOMIN=0x21
	MLX90614_PWMCTRL=0x22
	MLX90614_TARANGE=0x23
	MLX90614_EMISS=0x24
	MLX90614_CONFIG=0x25
	MLX90614_ADDR=0x0E
	MLX90614_ID1=0x3C
	MLX90614_ID2=0x3D
	MLX90614_ID3=0x3E
	MLX90614_ID4=0x3F

	comm_retries = 5
	comm_sleep_amount = 0.1

	def __init__(self, address=0x5a, bus_num=1):
		self.bus_num = bus_num
		self.address = address
		self.bus = smbus.SMBus(bus=bus_num)

	def read_reg(self, reg_addr):
		err = None
		for i in range(self.comm_retries):
			try:
				return self.bus.read_word_data(self.address, reg_addr)
			except IOError as e:
				err = e
				#"Rate limiting" - sleeping to prevent problems with sensor
				#when requesting data too quickly
				sleep(self.comm_sleep_amount)

		#By this time, we made a couple requests and the sensor didn't respond
		#(judging by the fact we haven't returned from this function yet)
		#So let's just re-raise the last IOError we got
		raise err

	def data_to_temp(self, data):
		temp = (data*0.02) - 273.15
		return temp

	def get_amb_temp(self):
		data = self.read_reg(self.MLX90614_TA)
		return self.data_to_temp(data)

	def get_obj_temp(self):
		data = self.read_reg(self.MLX90614_TOBJ1)
		return self.data_to_temp(data)

# function to use the sensor class as a process.
def main():
	declare_channel()
	
	global meta_massage

	sensors = sensor()
	timed = timer()
	wifitimer = timer()
	
	counter = 0
	
	
	
	# setup GPIO IRQ
	GPIO.setmode(GPIO.BCM)
	if configure.input_cap_mpr121:
		GPIO.setup(BUTTON_GPIOA, GPIO.IN)
		GPIO.setup(BUTTON_GPIOB, GPIO.IN)

		GPIO.add_event_detect(BUTTON_GPIOA, GPIO.RISING, callback=button_callbackA, bouncetime=10)
		GPIO.add_event_detect(BUTTON_GPIOB, GPIO.RISING, callback=button_callbackB, bouncetime=10) 
    
    # setup the thread with timer and start the IRQ reset function
	job = Job(interval=timedelta(seconds=WAIT_TIME_SECONDS), execute=reset)
	job.start() 

	while not configure.status == "quit":

		while True:
			
			if configure.bme:
				bme680 = sensors.get_bme680()
				publish("bme680",bme680)
				
			
				
			if configure.bmp280:
				bmp280 = sensors.get_bmp280()
				publish("bmp280",bmp280)
				
			
				
			if configure.SHT30:
				sht30 = sensors.get_sht30()	
				publish("sht30",sht30)
				
					
				
			if configure.SCD4X:
				scd4x = sensors.get_scd4x()
				publish("scd4x",scd4x)
				
				
			if configure.LSM6DS3TR:
				lsm6ds3 = sensors.get_lsm6ds3()
				publish("lsm6ds3",lsm6ds3)
					
				
			if configure.LIS3MDL:
				lis3mdl = sensors.get_lis3mdl()
				publish("lis3mdl",lis3mdl)
					
				
			if configure.APDS9960:
				apds9960 = sensors.get_apds9960()		
				publish("apds9960",apds9960)
							
			
			if configure.amg8833:
				thermal_frame = sensors.get_thermal_frame()
				publish("thermal_frame",thermal_frame)
						
				
			if configure.system_vitals:
				system_vitals = sensors.get_system_vitals()
				publish("system_vitals",system_vitals)							
			
				
			if configure.sensehat:
				sensehat_data = sensors.get_sensehat()	
				publish("sensehat",sensehat_data)		
			
			if configure.envirophat:
				envirophat_data = sensors.get_envirophat()
				publish("envirophat",envirophat_data)	
							
			if configure.pocket_geiger:			
				pocket_geigert_data = sensors.get_pocket_geiger()			
				publish("pocket_geiger",pocket_geiger_data)	

			if configure.ir_thermo:		
				ir_thermo_data = sensors.get_ir_thermo()	
				publish("ir_thermo",ir_thermo_data)
				
			if counter == 0:
				if configure.gps:
					gps_parsed = sensors.get_gps()
					if gps_parsed[0] is not None and gps_parsed[1] is not None:
						publish("GPS_DATA",gps_parsed)
				
			counter = counter + 1 
			if counter == 180:
				counter = 0
			else:
				time.sleep(0.0001)


if __name__ == "__main__":
	try:
		main()
		signal.signal(signal.SIGINT, signal_handler)
	except KeyboardInterrupt or Exception:
		disconnect()
		exit()
		
# input's from input.py
# configure.input_pcf8575
# configure.sensehat adn configure.input_joystick
# configure.input_gpio
# configure.input_kb
# configure.input_cap1208
