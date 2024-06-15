#!/usr/bin/env python
from objects import *
import pika
import sys
import ast


def threaded_rabbitmq_worker():
	connection = pika.BlockingConnection(
		pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()

	channel.exchange_declare(exchange='sensor_data', exchange_type='topic')
	channel.queue_declare(queue='sensor_metadata');
	
	msg_header_array, properties, body = channel.basic_get(queue='sensor_metadata')
	if body is not None:			
		array_pack = ast.literal_eval(body.decode())	
		key, configure.max_sensors = array_pack
		configure.sensor_ready[0] = True

	result = channel.queue_declare('', exclusive=True)
	queue_name = result.method.queue

	channel.queue_bind(
		exchange='sensor_data', queue='', routing_key='#')

	print(' [*] Waiting for logs. To exit press CTRL+C')


	def callback(ch, method, properties, body):
		print(f" [x] {method.routing_key}:{body}")

	channel.basic_consume(queue='',on_message_callback=callback, auto_ack=True)
	channel.start_consuming()
