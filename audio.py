from objects import *

import pika
import os
import sys
import time
import threading
import ast
from datetime import timedelta

import simpleaudio as sa

# A Timer to as Frameratecontroller
WAIT_TIME_SECONDS = 1

print("Loading Audio Thread")

#109 Sounds
scansound = sa.WaveObject.from_wave_file("assets/scanning.wav")
clicksound = sa.WaveObject.from_wave_file("assets/clicking.wav")
beepsound = sa.WaveObject.from_wave_file("assets/beep.wav")
alarmsound = sa.WaveObject.from_wave_file("assets/alarm.wav")



sounds = [scansound, clicksound]
# the audio object will serve as the primary mechanism by which all sounds
# are loaded and deployed.


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
    exchange='sensor_data', queue='', routing_key='audio')



def threaded_audio():
    timed = timer()
    start = True
    was_open = False
    warble = scansound.play()
    click = clicksound.play()
    alarm = alarmsound.play()

    click.stop()
    warble.stop()
    alarm.stop()

    while not configure.status[0] == "quit":
        if configure.audio[0]:

            if configure.dr_opening[0]:
                click = clicksound.play()
                configure.dr_opening[0] = False

            if configure.dr_closing[0]:
                click = clicksound.play()
                configure.dr_closing[0] = False

            if configure.beep_ready[0]:
                beep = beepsound.play()
                configure.beep_ready[0] = False


            # controls the main tricorder sound loop
            if configure.dr_open[0]:
                if not warble.is_playing() and configure.warble[0]:
                    warble = scansound.play()
            else:
                if warble.is_playing():
                    warble.stop()
            
            if not configure.warble[0]:
                warble.stop()

            if configure.alarm_ready[0] and configure.alarm[0]:
                if not alarm.is_playing():
                    alarm = alarmsound.play()
                configure.alarm_ready[0] = False
        else:
            warble.stop()
            
# This Class helps to start a thread that runs a timer non blocking to animate details
class Job(threading.Thread):
    def __init__(self, interval, execute, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.interval = interval
        self.execute = execute
        self.args = args
        self.kwargs = kwargs

    def stop(self):
                self.stopped.set()
                self.join()
    def run(self):
            while not self.stopped.wait(self.interval.total_seconds()):
                self.execute(*self.args, **self.kwargs)
           
            
            
            

def callback(ch, method, properties, body):
	print("callback")



            
if __name__ == '__main__':
	configure.dr_open[0] == True
	configure.warble[0] == True
	job = Job(interval=timedelta(seconds=WAIT_TIME_SECONDS), execute=threaded_audio)
	try:
		channel.basic_consume(queue='',on_message_callback=callback, auto_ack=True)
		channel.start_consuming()
	except KeyboardInterrupt or Exception or OSError as e:
		print("Termination", e)
		sys.exit(1)
