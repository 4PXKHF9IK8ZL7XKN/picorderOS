#!/usr/bin/env python
import pika
import sys
from pygame import mixer

mixer.init()
alert=mixer.Sound('../assets/beep.wav')

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='sensor_data', exchange_type='topic')

result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='EVENT')

print(' [*] Waiting for logs. To exit press CTRL+C')


def callback(ch, method, properties, body):
    print(f" [x] {method.routing_key}:{body}")
    alert.play()

channel.basic_consume(queue='',on_message_callback=callback, auto_ack=True)

channel.start_consuming()