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

from pynmeagps import NMEAReader
import RPi.GPIO as GPIO
import busio as io
from datetime import timedelta

from multiprocessing import Process,Queue,Pipe
# the following is a sensor module for use with the PicorderOS
print("Loading Unified Sensor Module")

generators = True
DEBUG = False

softbreak_flag = False
term_signal = False

meta_massage = ""

local_gps = [37.7820885,-122.3045112,configure.rabbitmq_tag]

DISPLAY_BL_PWM = 13

# Delcares the IRQ Pins for Cap Touch 
BUTTON_GPIOA = 17
BUTTON_GPIOB = 27

BUTTON_GPIOA_RST = 22

# set the BUS Freq
I2C_FRQ = 100000

# A Timer to reset the interrupt, when the data was not pulled correctly , otherwise the trigger stucks
WAIT_TIME_SECONDS = 0.5

# config the i2c device
i2c = io.I2C(configure.PIN_SCL, configure.PIN_SDA, frequency=I2C_FRQ)

		
if configure.input_cap1188:
	from adafruit_cap1188.i2c import CAP1188_I2C
	import board
	import busio
	import signal
	

	try:

                GPIO.setup(BUTTON_GPIOA_RST, GPIO.OUT, initial=GPIO.LOW)
                time.sleep(0.1)
                GPIO.output(BUTTON_GPIOA_RST,GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(BUTTON_GPIOA_RST,GPIO.LOW)
                time.sleep(0.1)
                cap1188A = CAP1188_I2C(i2c, address=0x28)
                #cap1188B = CAP1188_I2C(i2c, address=0x29)
                cap1188A.sensitivity = 4
                #cap1188B.sensitivity = 32
                #GPIO.setup(BUTTON_GPIOA_RST, GPIO.OUT, initial=GPIO.HIGH)
                #time.sleep(0.01)
                #GPIO.output(BUTTON_GPIOA_RST,GPIO.LOW)
                #time.sleep(0.01)
                #GPIO.output(BUTTON_GPIOA_RST,GPIO.HIGH)

	except OSError as e:
		print("Error in Sensors Rabbitmq by request I2C", e)
		sys.exit(1)		
		



if configure.rabbitmq_remote:
	credentials = pika.PlainCredentials(configure.rabbitmq_user,configure.rabbitmq_password)
	connection = pika.BlockingConnection(pika.ConnectionParameters(configure.rabbitmq_address,configure.rabbitmq_port,configure.rabbitmq_vhost,credentials))
	channel = connection.channel()
else:
	connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
	channel = connection.channel()
    
def declare_channel():
	# Setup Channels for Sensorscap1188A
	channel.exchange_declare(exchange='sensor_data', exchange_type='topic')
    
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
		print("An error occurred in Sensors Rabbitmq:",e)
		try:
			raise Exception('Terminating')
			signal.raise_signal(signal.SIGTERM)
		finally:
			disconnect()
			sys.exit(1)



	if DEBUG:
		print(f" {time_unix} [x] Sent {stack} {routing_key}:{message}")


def disconnect():
    connection.close()

def button_callbackA(channel):
	global softbreak_flag
	global term_signal
	
	#print("Catch")
	
	touchA_dict = {"DICT":"A",0:False,1:False,2:False,3:False,4:False,5:False,6:False,7:False,8:False,9:False,10:False,11:False}
	softbreak_flag = True

	if configure.input_cap_mpr121:	
		for i in range(12):
			touchA_dict[i] = mpr121A[i].value
			
	if configure.input_cap1188:
		for i in range(0,7,1):
			#touchA_dict[i] = cap1188A[i+1].value
			print("valueA", cap1188A[i+1].value)
	
	publish("touch",touchA_dict)
	softbreak_flag = False


def button_callbackB(channel):
	global softbreak_flag
	global term_signal
	print("Catch B")
    	
	touchB_dict = {"DICT":"B",0:False,1:False,2:False,3:False,4:False,5:False,6:False,7:False,8:False,9:False,10:False,11:False}
	softbreak_flag = True
	
	if configure.input_cap_mpr121:	
		for i in range(12):
			touchB_dict[i] = mpr121B[i].value
			
	if configure.input_cap1188:
		for i in range(0,7,1):
			touchB_dict[i] = cap1188B[i+1].value
			#print("valueB", cap1188B[i].value)
	
	
	publish("touch",touchB_dict)
	softbreak_flag = False


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


def signal_handler_function(signum, frame):
	print("Signal from Worker Thread - Terminate on error")
	disconnect()
	GPIO.cleanup()  
	sys.exit(1)





def soft_break():
	global softbreak_flag
	if softbreak_flag:
		time.sleep(0.5)
		softbreak_flag  = False
	return



if __name__ == "__main__":
	open_channel = declare_channel()

	timed = timer()
	wifitimer = timer()
	
	counter = 0
		
	# setup GPIO IRQ
	GPIO.setmode(GPIO.BCM)

	if configure.input_cap1188:
		GPIO.setup(BUTTON_GPIOA, GPIO.IN)
		GPIO.setup(BUTTON_GPIOB, GPIO.IN)

		#GPIO.setup(BUTTON_GPIOA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		#GPIO.setup(BUTTON_GPIOB, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		#GPIO.setup(BUTTON_GPIOA_RST, GPIO.OUT, initial=GPIO.HIGH)
		#time.sleep(0.01)
		#GPIO.output(BUTTON_GPIOA_RST,GPIO.LOW)
		GPIO.add_event_detect(BUTTON_GPIOA, GPIO.BOTH, callback=button_callbackA, bouncetime=10)
		GPIO.add_event_detect(BUTTON_GPIOB, GPIO.BOTH, callback=button_callbackB, bouncetime=10) 
		
		button_callbackA(open_channel)
	
    
	while True:
		try:

			signal.signal(signal.SIGTERM, signal_handler_function)
			  
			print(GPIO.input(BUTTON_GPIOA),GPIO.input(BUTTON_GPIOB))
			#button_callbackA(open_channel)
			
			reset()
			
			soft_break()
			    
			if counter == 0:
				if configure.gps:
					gps_parsed = sensors.get_gps()
					if gps_parsed[0] is not None and gps_parsed[1] is not None:
						soft_break()
						publish("GPS_DATA",gps_parsed)
					    
			soft_break()
			    
			counter = counter + 1 
			if counter == 180:
				counter = 0
			else:
				time.sleep(0.01)
					
					
		except KeyboardInterrupt or Exception or OSError as e:
			print("Termination", e)
			break
			#job.join()
			disconnect()
			GPIO.cleanup()  
			sys.exit(1)

