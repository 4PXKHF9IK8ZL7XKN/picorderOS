#!/usr/bin/env python
from objects import *
import pika
import sys
import ast
import time

mapping_book = {}
mapping_book_byname = {}

# An object to store each sensor value and context.
class Fragment(object):

	__slots__ = ('value','mini','maxi','dsc','sym','dev','timestamp','position')

	def __init__(self,mini,maxi,dsc,sym,dev):
		self.mini = mini
		self.maxi = maxi
		self.dsc = dsc
		self.dev = dev
		self.sym = sym
		self.value = 47
		self.timestamp = self.value
		self.position = [self.value,self.value]

	# Sets the value and timestamp for the fragment.
	def set(self,value, timestamp, position):

		self.value = value

		self.timestamp = time.time()

		self.position = position

	# Returns all the data for the fragment.
	def get(self):
		return [self.value, self.mini, self.maxi, self.dsc, self.sym, self.dev, self.timestamp, self.position[0], self.position[1]]

	# Returns only the info constants for this fragment
	def get_info(self):
		return [self.mini, self.maxi, self.dsc, self.sym, self.dev]
		
def get_all_info(self):
	info = self.get()

	allinfo = []
	for fragment in info:
		thisfrag = [fragment.dsc,fragment.dev,fragment.sym, fragment.mini, fragment.maxi]
		allinfo.append(thisfrag)
	return allinfo

def threaded_rabbitmq_worker():
	connection = pika.BlockingConnection(
		pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()

	channel.exchange_declare(exchange='sensor_data', exchange_type='topic')
	channel.queue_declare(queue='sensor_metadata');
	
	msg_header_array, properties, body = channel.basic_get(queue='sensor_metadata')
	if body is not None:			
		sensor_index_dict = ast.literal_eval(body.decode())	
		configure.max_sensors[0] = sensor_index_dict['sensor_index']
		ret_index = sensor_index_dict.pop('sensor_index')
		mapping_book_byname = sensor_index_dict
		for i in sensor_index_dict:
			mapping_book.update({sensor_index_dict[i]: i})
		configure.sensor_ready[0] = True

	result = channel.queue_declare('', exclusive=True)
	queue_name = result.method.queue

	channel.queue_bind(
		exchange='sensor_data', queue='', routing_key='#')

	def callback(ch, method, properties, body):
		print('book=', mapping_book_byname)
		print('index=', mapping_book_byname[method.routing_key])
		print('populating=', method.routing_key)
		#configure.sensor_info[mapping_book_byname[method.routing_key]] 

		print(f" [x] {method.routing_key}:{body}")

	channel.basic_consume(queue='',on_message_callback=callback, auto_ack=True)
	channel.start_consuming()
