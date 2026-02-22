from objects import *

import pika
import os
import sys
import time
import threading
import ast

import simpleaudio as sa

print("Loading Audio Thread Manager")

# the audio object will serve as the primary mechanism by which all sounds
# are loaded and deployed.

    
#109 Sounds
scansound = sa.WaveObject.from_wave_file("assets/scanning.wav")
clicksound = sa.WaveObject.from_wave_file("assets/clicking.wav")
beepsound = sa.WaveObject.from_wave_file("assets/beep.wav")
alarmsound = sa.WaveObject.from_wave_file("assets/alarm.wav")
sensor_alarmsound = sa.WaveObject.from_wave_file("assets/tric_alarm2.wav")
silencesound = sa.WaveObject.from_wave_file("assets/silence.wav")

sounds = [scansound, clicksound]

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
    

print_lock = threading.Lock()     	
class job_audio_play(threading.Thread):		
	def __init__(self, args=(), kwargs=None):
		threading.Thread.__init__(self, args=(), kwargs=None)
		self.daemon = True
		self.receive_messages = args
		self.message_var = "INIT"
		if self.receive_messages == "warble":
			self.audio_task = scansound.play()
		elif self.receive_messages == "alert":
			self.audio_task = alarmsound.play()
		elif self.receive_messages == "sensor_alert":
			self.audio_task = sensor_alarmsound.play()			
		elif self.receive_messages == "door":
			self.audio_task = clicksound.play()
		elif self.receive_messages == "key_press":
			self.audio_task = beepsound.play()
		else: 
			self.audio_task = silencesound.play()
		
		self.audio_task.stop()
		
	def run(self):
		if self.receive_messages == "warble":
			self.audio_task = scansound.play()
		elif self.receive_messages == "alert":
			self.audio_task = alarmsound.play()
		elif self.receive_messages == "sensor_alert":
			self.audio_task = sensor_alarmsound.play()
		elif self.receive_messages == "door":
			self.audio_task = clicksound.play()
		elif self.receive_messages == "key_press":
			self.audio_task = beepsound.play()
		else: 
			self.audio_task = silencesound.play()
		self.audio_task.wait_done()
		return
		
	def controll(self, message):
		if self.receive_messages:
			with print_lock:
				self.message_var = message
				if self.message_var == "stop":
					self.audio_task.stop()
		return

# Stolen Here: https://stackoverflow.com/questions/25904537/how-do-i-send-data-to-a-running-python-thread
class job(threading.Thread):
	def __init__(self, args=(), kwargs=None):
		threading.Thread.__init__(self, args=(), kwargs=None)
		self.daemon = True
		self.receive_messages = args[0]
		self.message_var = [{"dr_opening": False },{"dr_closing": False},{"warble": False},{"alert": False},{"sensor_alert": False}]
		
	def run(self):
		loop_warble = job_audio_play(args=(""))
		one_shot_alert = job_audio_play(args=(""))
		one_shot_sensor_alert = job_audio_play(args=(""))
		one_shot_closing = job_audio_play(args=(""))
		one_shot_opening = job_audio_play(args=(""))
		while True:
			#print(threading.current_thread().name, self.message_var)
			dr_closing_state = self.message_var[1]["dr_closing"]
			dr_opening_state = self.message_var[0]["dr_opening"]
			alarm_state = self.message_var[3]["alert"]
			warble_state = self.message_var[2]["warble"]
			sensor_alarm_state = self.message_var[4]["sensor_alert"]
			
			if warble_state and loop_warble.is_alive() == False:
				loop_warble = job_audio_play(args=("warble"))
				loop_warble.start()
			
			if warble_state == False and loop_warble.is_alive() == True:
				loop_warble.controll("stop")
				time.sleep(0.1)
				loop_warble.join()		
				
			if alarm_state and one_shot_alert.is_alive() == False:
				one_shot_alert = job_audio_play(args=("alert"))
				one_shot_alert.start()
				self.message_var[3]["alert"] = False
				
			if sensor_alarm_state and one_shot_sensor_alert.is_alive() == False:
				one_shot_sensor_alert = job_audio_play(args=("sensor_alert"))
				one_shot_sensor_alert.start()
				self.message_var[4]["sensor_alert"] = False
				
				
			if dr_opening_state and one_shot_opening.is_alive() == False:
				one_shot_opening = job_audio_play(args=("door"))
				one_shot_opening.start()
				self.message_var[0]["dr_opening"] = False
				
			if dr_closing_state and one_shot_closing.is_alive() == False:
				one_shot_closing = job_audio_play(args=("door"))
				one_shot_closing.start()
				self.message_var[1]["dr_closing"] = False
			
			time.sleep(0.1)

	def do_thing_with_message(self, message):
		if self.receive_messages:
			with print_lock:
				#print(threading.current_thread().name, "Received {}".format(message))
				self.message_var = message
				

def callback(ch, method, properties, body):
	dict_list = body.decode()
	audio_job.do_thing_with_message(ast.literal_eval(dict_list))

            
if __name__ == '__main__':
	try:
		audio_job = job(args=("1"))
		audio_job.start()
		time.sleep(0.1)
		channel.basic_consume(queue='audio',on_message_callback=callback, auto_ack=True)
		channel.start_consuming()

	except KeyboardInterrupt or Exception or OSError as e:
		print("Termination", e)
		sys.exit(1)
