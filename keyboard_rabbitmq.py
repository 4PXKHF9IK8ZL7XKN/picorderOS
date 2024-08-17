#!/bin/python
import time
import os
import struct
import sys
import pika

from objects import *

DEBUG = False

infile_path = "/dev/input/event" + (sys.argv[1] if len(sys.argv) > 1 else "3")

"""
FORMAT represents the format used by linux kernel input event struct
See https://github.com/torvalds/linux/blob/v5.5-rc5/include/uapi/linux/input.h#L28
Stands for: long int, long int, unsigned short, unsigned short, unsigned int
"""
FORMAT = 'llHHI'
EVENT_SIZE = struct.calcsize(FORMAT)

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
	#open file in binary mode
	in_file = open(infile_path, "rb")
	event = in_file.read(EVENT_SIZE)
	while event:
		(tv_sec, tv_usec, type, code, value) = struct.unpack(FORMAT, event)
		if type != 0 or code != 0 or value != 0:
			keyboard_message = type,code,value,tv_sec,tv_usec
			publish("keyboard",keyboard_message)
			#print("Event type %u, code %u, value %u at %d.%d" % \
			#(type, code, value, tv_sec, tv_usec))
		#else:
			# Events with code, type and value == 0 are "separator" events
			#print("===========================================")
		event = in_file.read(EVENT_SIZE)

	in_file.close()

if __name__ == "__main__":
	try:
		declare_channel()
		main()
		signal.signal(signal.SIGINT, signal_handler)
	except KeyboardInterrupt or Exception:
		disconnect()
		exit()

