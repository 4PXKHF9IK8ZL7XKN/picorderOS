#!/bin/python
import time
import os
import struct
import sys
import pika
from sense_hat import SenseHat

from objects import *

DEBUG = False

sense = SenseHat()

if configure.rabbitmq_remote_server:
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

def main():
	while True:
		event = sense.stick.wait_for_event()
		joystick_message = event.action, event.direction, configure.rabbitmq_tag
		publish("sensehat_joystick",joystick_message)
		if DEBUG:
			print("The joystick was {} {}".format(event.action, event.direction))
		sleep(0.1)
		event = sense.stick.wait_for_event()
		joystick_message = event.action, event.direction, configure.rabbitmq_tag
		publish("sensehat_joystick",joystick_message)
		if DEBUG:
			print("The joystick was {} {}".format(event.action, event.direction))

if __name__ == "__main__":
	if configure.sensehat_joystick:
		try:
			declare_channel()
			main()
			signal.signal(signal.SIGINT, signal_handler)
		except KeyboardInterrupt or Exception:
			disconnect()
			exit()

