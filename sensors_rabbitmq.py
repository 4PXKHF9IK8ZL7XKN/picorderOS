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
import sys
from pynmeagps import NMEAReader
import RPi.GPIO as GPIO
import busio as io
from datetime import timedelta

from multiprocessing import Process,Queue,Pipe
# the following is a sensor module for use with the PicorderOS
print("Loading Unified Sensor Module")

generators = True
DEBUG = False

# Delcares the IRQ Pins for Cap Touch 
BUTTON_GPIOA = 17
BUTTON_GPIOB = 27

# set the BUS Freq
I2C_FRQ = 100000

# A Timer to reset the interrupt, when the data was not pulled correctly , otherwise the trigger stucks
WAIT_TIME_SECONDS = 0.5

# config the i2c device
i2c = io.I2C(configure.PIN_SCL, configure.PIN_SDA, frequency=I2C_FRQ)


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
	amg = adafruit_amg88xx.AMG88XX(i2c)

if configure.EM:
	from modulated_em import *

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
	channel.basic_publish(
        exchange=stack, routing_key=routing_key, body=message)
	if DEBUG:
		print(f" {time_unix} [x] Sent {stack} {routing_key}:{message}")
    
def disconnect():
    connection.close()
        
def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)
     
    
# Interrupt Callback functions for the Touch Sensors
def button_callbackB(channel):
	touchB_dict = {"DICT":"B",0:False,1:False,2:False,3:False,4:False,5:False,6:False,7:False,8:False,9:False,10:False,11:False}
	for i in range(12):
		touchB_dict[i] = mpr121B[i].value
	publish("touch",touchB_dict)
    

def button_callbackA(channel):
	touchA_dict = {"DICT":"A",0:False,1:False,2:False,3:False,4:False,5:False,6:False,7:False,8:False,9:False,10:False,11:False}
	for i in range(12):
		touchA_dict[i] = mpr121A[i].value
	publish("touch",touchA_dict)


def reset():
    if not GPIO.input(17) or not GPIO.input(27):
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


def GPS_function():

		gps_update = {"lat" : 47.00, "lon" : 47.00, "speed" : 0.00,"altitude":0.00, "track" : 0.00, "sats":0}

		stream = serial.Serial(port, baud, timeout=3)
		nmr = NMEAReader(stream)
		(raw_data, parsed_data) = nmr.read()

		if hasattr(parsed_data, "lat"):

			if parsed_data.lat != '':
				gps_update["lat"] = float(parsed_data.lat)

			if parsed_data.lon != '':
				gps_update["lon"] = float(parsed_data.lon)


		if hasattr(parsed_data, "altitude"):

			if parsed_data.altitude != '':
				gps_update["altitude"] = float(parsed_data.altitude)


		if hasattr(parsed_data, "speed"):

			if parsed_data.speed != '':
				gps_update["speed"] = float(parsed_data.speed)

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

		if generators:
			self.step = 0.0
			self.step2 = 0.0
			self.steptan = 0.0

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

		if configure.pocket_geiger:
			self.radiation = RadiationWatch(configure.PG_SIG,configure.PG_NS)
			self.radiation.setup()

		if configure.amg8833:
			self.thermal_frame = []


	def sin_gen(self):
		wavestep = math.sin(self.step)
		self.step += .1
		return wavestep

	def tan_gen(self):
		wavestep = math.tan(self.steptan)
		self.steptan += .1
		return wavestep

	def sin2_gen(self, offset = 0):
		wavestep = math.sin(self.step2)
		self.step2 += .05
		return wavestep

	def cos_gen(self, offset = 0):
		wavestep = math.cos(self.step)
		self.step += .1
		return wavestep

	def get_thermal_frame(self):
		self.thermal_frame = amg.pixels
		data = numpy.array(self.thermal_frame)
		high = numpy.max(data)
		low = numpy.min(data)
		return self.thermal_frame

	def get_gps(self):
		if configure.gps:
			gps_data = GPS_function()
			position = [gps_data["lat"],gps_data["lon"]]
			
		else:
			position = [37.7820885,-122.3045112]
			# USS Hornet - Sea, Air and Space Museum (Alameda) , Pavel Knows ;)
		return position

	def get_bme680(self):
		self.bme680_temp = self.bme680.temperature
		self.bme680_humi = self.bme680.humidity
		self.bme680_press = self.bme680.pressure
		self.bme680_voc = self.bme680.gas / 1000
		self.bme680_alt = self.bme680.altitude 
		return self.bme680_temp,self.bme680_humi,self.bme680_press, self.bme680_voc, self.bme680_alt

	def get_sensehat(self):
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
			
		return self.sh_temp, self.sh_baro, self.sh_humi, self.sh_magx, self.sh_magy, self.sh_magz, self.sh_accx, self.sh_accy, self.sh_accz
		
	def get_pocket_geiger(self):
		data = self.radiation.status()
		rad_data = float(data["uSvh"])

		# times 100 to convert to urem/h
		self.radiat.set(rad_data*100, timestamp, position)
		
		return self.radiat
		
	# provides the basic definitions for the system vitals sensor readouts
	def get_system_vitals(self):
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
		
		return self.uptime, self.cpuload ,self.cputemp, self.cpuperc, self.virtmem, self.diskuse, self.bytsent, self.bytrece
		
	def get_generators(self):
		timestamp = time.time()
		self.sinewav = float(self.sin_gen()*100)
		self.tanwave = float(self.tan_gen()*100)
		self.coswave = float(self.cos_gen()*100)
		self.sinwav2 = float(self.sin2_gen()*100)		
		return self.sinewav, self.tanwave, self.coswave, self.sinwav2

	def get_envirophat(self):
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
		return self.ep_temp, self.ep_baro, self.ep_colo, self.ep_magx, self.ep_magy, self.ep_magz, self.ep_accx, self.ep_accy, self.ep_accz
		
	def get_MLX90614(self):
		amb_temp = MLX90614.data_to_temp(MLX90614.get_amb_temp)
		obj_temp = MLX90614.data_to_temp(MLX90614.get_obj_temp)
		return amb_temp, obj_temp




# function to get index number for aval. Sensors
	def get_index(self):

		#index holds a counter about sensors that reacts to the get functions 
		index = {'sensor_index': 0}
		
		# we have a dummy GPS that sends at least static data
		index['sensor_index'] += 1
		index.update({ "GPS_DATA" : index['sensor_index']})

		if configure.bme:
			rety = self.get_bme680()
			if not rety == None: 
				index['sensor_index'] += 1
				index.update({ "bme680" : index['sensor_index']})

		if configure.sensehat:
			rety = self.get_sensehat()
			if not rety == None: 
				index['sensor_index'] += 1
				index.update({ "sensehat" : index['sensor_index']})

		if configure.pocket_geiger:
			rety = self.get_pocket_geiger()
			if not rety == None: 
				index['sensor_index'] += 1
				index.update({ "pocket_geiger" : index['sensor_index']})

		if configure.amg8833:
			rety = self.get_thermal_frame()
			if not rety == None: 
				index['sensor_index'] += 1
				index.update({ "thermal_frame" : index['sensor_index']})
				
		if configure.envirophat:
			rety = self.get_envirophat()
			if not rety == None: 
				index['sensor_index'] += 1
				index.update({ "envirophat" : index['sensor_index']})
		
		if configure.system_vitals:
			rety = self.get_system_vitals()
			if not rety == None: 
				index['sensor_index'] += 1
				index.update({ "system_vitals" : index['sensor_index']})
			
		if generators:
			rety = self.get_generators()
			if not rety == None: 
				index['sensor_index'] += 1
				index.update({ "generators" : index['sensor_index']})
				
		if configure.ir_thermo:
			rety = self. self.get_ir_thermo()
			if not rety == None: 
				index['sensor_index'] += 1
				index.update({ "ir_thermo" : index['sensor_index']})

		configure.max_sensors[0] = index
			
		if index['sensor_index'] < 1:
			print("NO SENSORS LOADED")

		return index

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
def sensor_process():
	sensors = sensor()
	timed = timer()
	wifitimer = timer()
	
	counter = 0
	
	meta_massage = str(sensors.get_index())
	print(meta_massage)
	publish('sensor_metadata',meta_massage)

	while True:
		#if timed.timelapsed() > configure.samplerate[0]:
		#sensor_data = sensors.get()
		if configure.bme:
			bme680 = sensors.get_bme680()
			publish("bme680",bme680)
		
		if configure.amg8833:
			thermal_frame = sensors.get_thermal_frame()
			publish("thermal_frame",thermal_frame)
			
		if configure.system_vitals:
			system_vitals = sensors.get_system_vitals()
			publish("system_vitals",system_vitals)
			
		if generators:
			generatorsCurve = sensors.get_generators()
			publish("generators",generatorsCurve)
			
		if configure.gps:
			gps_parsed = sensors.get_gps()
			publish("GPS_DATA",gps_parsed)
			
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
			
		if counter == 10:
			meta_massage = str(sensors.get_index())
			print(meta_massage)
			publish('sensor_metadata',meta_massage)
			counter = 0

		counter += 1
		timed.logtime()

       
        
def main():
	declare_channel()
	
	# setup GPIO IRQ
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(BUTTON_GPIOA, GPIO.IN)
	GPIO.setup(BUTTON_GPIOB, GPIO.IN)

	GPIO.add_event_detect(BUTTON_GPIOA, GPIO.BOTH, callback=button_callbackA, bouncetime=50)
	GPIO.add_event_detect(BUTTON_GPIOB, GPIO.BOTH, callback=button_callbackB, bouncetime=50) 
    
    # setup the thread with timer and start the IRQ reset function
	job = Job(interval=timedelta(seconds=WAIT_TIME_SECONDS), execute=reset)
	job.start()
    
    
 
	while not configure.status == "quit":
		while True:
		    sensor_process()

if __name__ == "__main__":
	try:
		main()
		disconnect()
		signal.signal(signal.SIGINT, signal_handler)
	except KeyboardInterrupt:
		pass
