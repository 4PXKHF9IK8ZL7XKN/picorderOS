#!/usr/bin/env python
from objects import *
import pika
import sys
import ast
import time
import psutil
import numpy

GPS_DATA = [4747.0000, 4747.0000]
mapping_book = {}
mapping_book_byname = {}

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.exchange_declare(exchange='sensor_data', exchange_type='topic')
channel.queue_declare(queue='sensor_metadata');



def callback_rabbitmq(ch, method, properties, body):
	#print('book=', mapping_book_byname)
	#print('populating=', method.routing_key)
	global connG
	global sensor_data
	conn = connG
	sensors = Sensor()
	if method.routing_key == 'GPS_DATA':
		GPS_DATA = body.decode()
	elif method.routing_key == 'bme680':
		var1,var2,var3,var4,var5 = body.decode().split(",")
		sensors.update_bme680(var1,var2,var3,var4,var5)
	elif method.routing_key == 'system_vitals':
		print("type:",type(body.decode()))
		var1 = body.decode().split(",")
		#print(var1)
		#sensors.update_system_vitals(var1,var2,var3,var4,var5,var6,var7,var8)
	sensor_data = sensors.get()
	#conn.send([sensor_data])
	#conn.send([sensor_data, thermal_frame])
	#print(f" [x] {method.routing_key}:{body}")			
	
def callback_rabbitmq_meta(ch, method, properties, body):
	global mapping_book_byname
	global mapping_book
	if body == None:
		time.sleep(0.2)
	else:
		sensor_index_dict = ast.literal_eval(body.decode())	
		configure.max_sensors[0] = sensor_index_dict['sensor_index']
		ret_index = sensor_index_dict.pop('sensor_index')
		mapping_book_byname = sensor_index_dict
		for i in sensor_index_dict:
			mapping_book.update({sensor_index_dict[i]: i})
		channel.basic_cancel('sensor_metadata')
			
			
def threaded_rabbitmq_worker(conn):
	global connG 
	global mapping_book_byname
	global mapping_book
	connG = conn
	channel.basic_consume(consumer_tag='sensor_metadata',queue='sensor_metadata',on_message_callback=callback_rabbitmq_meta, auto_ack=True)
	# Waiting for the Metadata message ca 10 sec
	channel.start_consuming()
	# this is an constructor here starts the build of all data
	sensors = Sensor()
	try:
		sensor_data = sensors.get()
	except:
		pass		
		#thermal_frame = sensors.get_thermal_frame()

	result = channel.queue_declare('', exclusive=True)
	queue_name = result.method.queue

	channel.queue_bind(
		exchange='sensor_data', queue='', routing_key='#')

	if len(mapping_book_byname) > 0:
		print("Sensors Ready")
		print("Avail:", len(configure.sensor_info))
		configure.sensor_ready[0] = True
		channel.basic_consume(queue='',on_message_callback=callback_rabbitmq, auto_ack=True)
		channel.start_consuming()
