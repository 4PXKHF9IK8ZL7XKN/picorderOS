#!/usr/bin/env python
from objects import *
import pika
import sys

def threaded_rabbitmq_worker:
	connection = pika.BlockingConnection(
		pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()

	channel.exchange_declare(exchange='sensor_data', exchange_type='topic')

	result = channel.queue_declare('', exclusive=True)
	queue_name = result.method.queue

	channel.queue_bind(
		exchange='sensor_data', queue='', routing_key='#')

	print(' [*] Waiting for logs. To exit press CTRL+C')


	def callback(ch, method, properties, body):
		print(f" [x] {method.routing_key}:{body}")

	channel.basic_consume(queue='',on_message_callback=callback, auto_ack=True)
	channel.start_consuming()
