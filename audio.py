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
WAIT_TIME_SECONDS = 31


# ex globals
dr_open = True
warble_state = False
alarm_state = False
audio_state = True

status = "run"

dr_closing = False
dr_opening = False

beep_ready = False
alarm_ready = False
alarm = False


print("Loading Audio Thread")

#109 Sounds
scansound = sa.WaveObject.from_wave_file("assets/scanning.wav")
clicksound = sa.WaveObject.from_wave_file("assets/clicking.wav")
beepsound = sa.WaveObject.from_wave_file("assets/beep.wav")
alarmsound = sa.WaveObject.from_wave_file("assets/alarm.wav")

warble = scansound
alarm = alarmsound


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

result = channel.queue_declare('audio', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='audio')



def threaded_audio():
	timed = timer()
	start = True
	was_open = False
	
	global dr_open
	global warble_state
	global alarm_state
	global audio_state

	global status

	global dr_closing
	global dr_opening

	global beep_ready
	global alarm_ready
	global alarm
	
	global scansound
	global clicksound
	global beepsound
	global alarmsound
	
	global warble
	global alarm
	      
	      
	if audio_state:

		if dr_opening:
			clicksound.play()
			dr_opening = False

		if dr_closing:
			clicksound.play()
			dr_closing = False

		if beep_ready:
			beepsound.play()
			beep_ready = False


        # controls the main tricorder sound loop
		if dr_open:
			if not hasattr(warble,'is_playing') and warble_state:
				scansound.play()
		else:
			if hasattr(warble,'is_playing'):
				scansound.stop()
        
		if not warble_state:
			scansound.stop()

		if alarm_ready and alarm_state:
			if not hasattr(alarm,'is_playing'):
				alarmsound.play()
			alarm_ready = False
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
	try:
		job = Job(interval=timedelta(seconds=WAIT_TIME_SECONDS), execute=threaded_audio) 
		job.start()
		channel.basic_consume(queue='audio',on_message_callback=callback, auto_ack=True)
		channel.start_consuming()

	except KeyboardInterrupt or Exception or OSError as e:
		print("Termination", e)
		sys.exit(1)
