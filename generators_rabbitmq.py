#!/bin/python
import time
import os
import struct
import sys
import pika
import math
import picosglobals

from objects import *

DEBUG = False

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

def publish_generators(IN_routing_key,data):
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

class sensor_functions(object): 

	def __init__(self):

		if configure.generators:
			self.step = 0
			self.step2 = 0
			self.steptan = 0
				
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
		
		
	def get_generators(self):
		GPS_DATA = picosglobals.GPS_DATA
		timestamp = time.time()
		self.sinewav = float(self.sin_gen()*100)
		self.tanwave = float(self.tan_gen()*100)
		self.coswave = float(self.cos_gen()*100)
		self.sinwav2 = float(self.sin2_gen()*100)
				
		return self.sinewav, self.tanwave, self.coswave, self.sinwav2 ,timestamp, GPS_DATA[0], GPS_DATA[1], configure.rabbitmq_tag


def main():

	timed = timer()
	sensors = sensor_functions()

	while True:	
		generatorsCurve = sensors.get_generators()	
		publish_generators('generators',generatorsCurve)
		time.sleep(1)

if __name__ == "__main__":
	if configure.generators:
		try:
			declare_channel()
			main()
			signal.signal(signal.SIGINT, signal_handler)
		except KeyboardInterrupt or Exception or OSError as e:
			print("Termination", e)
			disconnect()
			sys.exit(1)
	else:
		print("Service Disabled")
		exit(1)

