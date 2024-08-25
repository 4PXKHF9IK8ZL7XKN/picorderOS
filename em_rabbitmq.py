# PicorderOS Wifi Module Proto
print("Loading Modulated EM Signal Analysis")

#!/bin/python
import time
import sys
import pika
import picosglobals
import piwifi


from objects import *
from bluetooth import *

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

def publish_wifi_stats(IN_routing_key,data):
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
			sys.exit(1)
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
				
		
	def get_wifi_stats(self):
		GPS_DATA = picosglobals.GPS_DATA
		timestamp = time.time()
		
		
		self.sinewav = "static"
	
		return self.sinewav ,timestamp, GPS_DATA[0], GPS_DATA[1], configure.rabbitmq_tag



if __name__ == "__main__":
	if configure.generators:
		try:
			declare_channel()
			timed = timer()
			sensors = sensor_functions()

			while True:	
				wifi_stats = sensors.get_wifi_stats()	
				#publish_wifi_stats('wifi_stats',wifi_stats)
				time.sleep(1)

			signal.signal(signal.SIGINT, signal_handler)
		except KeyboardInterrupt or Exception or OSError as e:
			print("Termination", e)
			disconnect()
			sys.exit(1)
	else:
		print("Service Disabled")
		exit(1)

