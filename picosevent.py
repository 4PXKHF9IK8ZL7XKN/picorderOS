#!/usr/bin/env python

# This script retrieves and packages all input events that might be useful to the program
# it sends it back as envent to rabbitmq

# array needs:

# geo, met and bio are going to be standard across all trics.


# array holds the pins for each hard coded button on the tric
# The TR-108 only has 3 buttons

# Max number of buttons for tr109 style (TNG)
#	0	1	 2    3  	4	 5	  6  7		8				9			10		11	  		12  13  14
# geo, met, bio, lib, pwr, f1/f2, I, E, accpt/pool, intrship/tricrder, EMRG, fwd/input, rvs/erase, Ib, Eb, Id
# next, enter, cancel/switch

import pika
import sys
import time
import threading
import ast
from objects import *


print("Loading Event Module")

threshold = 3
release_threshold = 2

DEBUG = False

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='sensor_data', exchange_type='topic')

result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='touch')

def publish(IN_routing_key,data):
	stack = 'sensor_data'
	if IN_routing_key == 'sensor_metadata':
		stack = ''
   
	routing_key = str(IN_routing_key)
	message = str(data)
	time_unix = time.time()
	try:
		channel.basic_publish(exchange=stack, routing_key=routing_key, body=message)
	except:
		raise Exception("Publish Faild, connection lost") 
		disconnect()
		sys.exit(1)		
	if DEBUG:
		print(f" {time_unix} [x] Sent {stack} {routing_key}:{message}")
		

configure.beep_ready[0] = True

def callback(ch, method, properties, body):
	EVENT_MAP = { 'geo': False  , 'met': False, 'bio': False, 'lib': False, 'pwr': False, 'f1/f2': False, 'I': False, 'E': False, 'accpt/pool': False, 'intrship/tricrder': False, 'EMRG': False, 'fwd/input': False, 'rvs/erase': False, 'Ib': False, 'Eb': False, 'Id': False, 'Door_open': False, 'Door_close': False, 'LOW-POWER': False, 'next':False, 'ENTER':False, 'cancel/switch': False, 'SERIAL': False  }
	# pcf8575 can map 16 inputs
	configure.input_pcf8575
	# mpr121 can map 12 inputs
	if configure.input_cap_mpr121:
		sensor_dict_unclean = body.decode()
		sensor_dict = ast.literal_eval(sensor_dict_unclean)
		#print(sensor_dict)
		#print(type(sensor_dict))
		for key in sensor_dict:
			if sensor_dict['DICT'] == 'A':
				if not key == 'DICT':
					if key == 0:
						EVENT_MAP['geo'] = sensor_dict[key]
					elif key == 1:
						EVENT_MAP['met'] = sensor_dict[key]
					elif key == 2:
						EVENT_MAP['bio'] = sensor_dict[key]
					elif key == 3:
						EVENT_MAP['lib'] = sensor_dict[key]
					elif key == 4:
						EVENT_MAP['pwr'] = sensor_dict[key]
					elif key == 5:
						EVENT_MAP['f1/f2'] = sensor_dict[key]
					elif key == 6:
						EVENT_MAP['I'] = sensor_dict[key]
					elif key == 7:
						EVENT_MAP['E'] = sensor_dict[key]
					elif key == 8:
						EVENT_MAP['cancel/switch'] = sensor_dict[key]
					# no mapping here all keys in the top part of the tric are mapped
					elif key == 9:
						pass
					elif key == 10:
						pass
					elif key == 11:
						pass
			elif sensor_dict['DICT'] == 'B':
				if not key == 'DICT':
					if key == 0:
						EVENT_MAP['accpt/pool'] = sensor_dict[key]
					elif key == 1:
						EVENT_MAP['intrship/tricrder'] = sensor_dict[key]
					elif key == 2:
						EVENT_MAP['EMRG'] = sensor_dict[key]
					elif key == 3:
						EVENT_MAP['fwd/input'] = sensor_dict[key]
					elif key == 4:
						EVENT_MAP['rvs/erase'] = sensor_dict[key]
					elif key == 5:
						EVENT_MAP['Ib'] = sensor_dict[key]
					elif key == 6:
						EVENT_MAP['Eb'] = sensor_dict[key]
					elif key == 7:
						EVENT_MAP['Id'] = sensor_dict[key]
					elif key == 8:
						EVENT_MAP['cancel/switch'] = sensor_dict[key]
					elif key == 9:
						pass
					elif key == 10:
						pass
					elif key == 11:
						pass

	# joystick can map 5 inputs
	configure.input_joystick
	# gpio door open close and 3 butten presses for TR-108
	configure.input_gpio
	# 3 inputs for kb
	configure.input_kb
	# cap1208 can handel 8 inputs
	configure.input_cap1208
	publish('EVENT',EVENT_MAP)
	#print(f" [x] {method.routing_key}:{body}")

def threaded_events():
	channel.basic_consume(queue='',on_message_callback=callback, auto_ack=True)
	channel.start_consuming()
	


if __name__ == '__main__':
	channel.basic_consume(queue='',on_message_callback=callback, auto_ack=True)
	channel.start_consuming()











