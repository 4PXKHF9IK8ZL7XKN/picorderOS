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
import os
import sys
import time
import threading
import ast
import simpleaudio as sa
from objects import *

scansound = sa.WaveObject.from_wave_file("assets/scanning.wav")
clicksound = sa.WaveObject.from_wave_file("assets/clicking.wav")
beepsound = sa.WaveObject.from_wave_file("assets/beep.wav")
alarmsound = sa.WaveObject.from_wave_file("assets/alarm.wav")



print("Loading Event Module")

threshold = 3
release_threshold = 2

DEBUG = False

SENSOR_MODE = 0
SENSOR_MODE_LAST = 0

ALERT_STATE = 0 # 0 = green, 1 = yellow, 2 = red, 3 = blue, 4 = black, 5 = grey, 6 = doublered

configure.eventlist[0] = [0,0,0,0,0,0,0,0]

if configure.rabbitmq_remote:
	credentials = pika.PlainCredentials(configure.rabbitmq_user,configure.rabbitmq_password)
	connection = pika.BlockingConnection(pika.ConnectionParameters(configure.rabbitmq_address,configure.rabbitmq_port,configure.rabbitmq_vhost,credentials))
	channel = connection.channel()
else:
	connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
	channel = connection.channel()

channel.exchange_declare(exchange='sensor_data', exchange_type='topic')

result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='lcars')

channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='touch')
    
channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='keyboard')    
    
def publish(IN_routing_key,data):
	configure.beep_ready[0] = True
	configure.eventready[0] = True	

	stack = 'sensor_data'
	if IN_routing_key == 'sensor_metadata':
		stack = ''

	routing_key = str(IN_routing_key)
	message = str(data)
	time_unix = time.time()
	try:
		if message is not None:
			channel = connection.channel()
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
		
def callback(ch, method, properties, body):
	global SENSOR_MODE
	global SENSOR_MODE_LAST
	global ALERT_STATE
	EVENT_MAP = { 'geo': False  , 'met': False, 'bio': False, 'lib': False, 'pwr': False, 'f1/f2': False, 'I': False, 'E': False, 'accpt/pool': False, 'intrship/tricrder': False, 'EMRG': False, 'fwd/input': False, 'rvs/erase': False, 'Ib': False, 'Eb': False, 'Id': False, 'Door_open': False, 'Door_close': False, 'LOW-POWER': False, 'next':False, 'ENTER':False, 'cancel/switch': False, 'SERIAL': False, 'SENSOR_MODE': SENSOR_MODE, 'ALERT_STATE': ALERT_STATE }
	# pcf8575 can map 16 inputs
	configure.input_pcf8575
	# mpr121 can map 12 inputs
	
	#print("array:", configure.eventlist[0])
	print("CALLBACK",method.routing_key)
	if method.routing_key == 'touch':
		if configure.input_cap_mpr121:
			sensor_dict_unclean = body.decode()
			sensor_dict = ast.literal_eval(sensor_dict_unclean)
			print(sensor_dict)
			#print(type(sensor_dict))
			for key in sensor_dict:
				if sensor_dict['DICT'] == 'A':
					if not key == 'DICT':
						if key == 0:
							EVENT_MAP['geo'] = sensor_dict[key]
							configure.eventlist[0][0] =  sensor_dict[key]
						elif key == 1:
							EVENT_MAP['met'] = sensor_dict[key]
							configure.eventlist[0][1] =  sensor_dict[key]
						elif key == 2:
							EVENT_MAP['bio'] = sensor_dict[key]
							configure.eventlist[0][2] =  sensor_dict[key]
						elif key == 3:
							EVENT_MAP['lib'] = sensor_dict[key]
							configure.eventlist[0][3] =  sensor_dict[key]
						elif key == 4:
							EVENT_MAP['pwr'] = sensor_dict[key]
							configure.eventlist[0][4] =  sensor_dict[key]
						elif key == 5:
							EVENT_MAP['f1/f2'] = sensor_dict[key]
							configure.eventlist[0][5] =  sensor_dict[key]
						elif key == 6:
							EVENT_MAP['I'] = sensor_dict[key]
							configure.eventlist[0][6] =  sensor_dict[key]
						elif key == 7:
							EVENT_MAP['E'] = sensor_dict[key]
							configure.eventlist[0][7] =  sensor_dict[key]
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
							#configure.eventlist[0][8] =  sensor_dict[key]						
						elif key == 1:
							EVENT_MAP['intrship/tricrder'] = sensor_dict[key]
							#configure.eventlist[0][9] =  sensor_dict[key]
						elif key == 2:
							EVENT_MAP['EMRG'] = sensor_dict[key]
							#configure.eventlist[0][10] =  sensor_dict[key]
							if sensor_dict[key]:
							  if ALERT_STATE != 2:
							    ALERT_STATE = 2
							    SENSOR_MODE = 2
							  else:
							    ALERT_STATE = 0
							    SENSOR_MODE = SENSOR_MODE_LAST
						elif key == 3:
							EVENT_MAP['fwd/input'] = sensor_dict[key]
							if sensor_dict[key]:
							  SENSOR_MODE = SENSOR_MODE + 1
							  SENSOR_MODE_LAST = SENSOR_MODE 
							  if SENSOR_MODE > 8:
							      SENSOR_MODE = 0
							      SENSOR_MODE_LAST = 0
							#configure.eventlist[0][11] =  sensor_dict[key]
						elif key == 4:
							EVENT_MAP['rvs/erase'] = sensor_dict[key]
							#configure.eventlist[0][12] =  sensor_dict[key]
						elif key == 5:
							EVENT_MAP['Ib'] = sensor_dict[key]
							#configure.eventlist[0][13] =  sensor_dict[key]
						elif key == 6:
							EVENT_MAP['Eb'] = sensor_dict[key]
							#configure.eventlist[0][14] =  sensor_dict[key]
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
	print("EVENT:", EVENT_MAP)
	click = beepsound.play()
	#print(f" [x] {method.routing_key}:{body}")

if __name__ == '__main__':
	try:
		channel.basic_consume(queue='',on_message_callback=callback, auto_ack=True)
		channel.start_consuming()
	except KeyboardInterrupt or Exception or OSError as e:
		print("Termination", e)
		sys.exit(1)











