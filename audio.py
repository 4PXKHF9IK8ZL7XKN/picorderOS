from objects import *

import pika
import os
import sys
import time
import threading
import ast

import simpleaudio as sa

print("Loading Audio Thread")

# the audio object will serve as the primary mechanism by which all sounds
# are loaded and deployed.

    
#109 Sounds
scansound = sa.WaveObject.from_wave_file("assets/scanning.wav")
clicksound = sa.WaveObject.from_wave_file("assets/clicking.wav")
beepsound = sa.WaveObject.from_wave_file("assets/beep.wav")
alarmsound = sa.WaveObject.from_wave_file("assets/alarm.wav")

#alarm = alarmsound.play()

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
    

    
    

  
  
def audio_function():
		       
		dr_open = True
		warble_state = False
		alarm_state = False
		audio_state = True
		status = "run"
		beep_ready = False
		alarm_ready = True
		start = True
		was_open = False
				
		while True:
			print("Loop" , self.message_var)
			

			
			print(warble_state)
			print(alarm_state)
			print(dir(self.warble))
			
			if warble_state == False:
				print("STOP")
				try:
					self.warble.stop()
				except:
					print("STOP STOP STOP")
					pass
				


			
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
					if not hasattr(self.warble,'is_playing') and warble_state:
						self.warble.play()
				else:
					if hasattr(self.warble,'is_playing'):
						self.warble.stop()
				
				if warble_state == False:
					if hasattr(self.warble,'is_playing'):
						self.warble.stop()

				if alarm_state:
					if not hasattr(alarm,'is_playing'):
						alarm.play()
					alarm_ready = False
			else:
				if hasattr(self.warble,'is_playing'):
					self.warble.stop()
			time.sleep(2)
     	

          
class warble_job(threading.Thread):		
	def __init__(self, kwargs=None):
		threading.Thread.__init__(self, args=(), kwargs=None)
		self.daemon = True
		
	def run(self):
		print(threading.current_thread().name)
		warble = scansound.play()
		warble.wait_done()
		print("Termination")
  
            
print_lock = threading.Lock()
# Stolen Here: https://stackoverflow.com/questions/25904537/how-do-i-send-data-to-a-running-python-thread
class job(threading.Thread):
	def __init__(self, args=(), kwargs=None):
		threading.Thread.__init__(self, args=(), kwargs=None)
		self.daemon = True
		self.receive_messages = args[0]
		self.message_var = [{"dr_opening": False },{"dr_closing": False},{"warble": False},{"alert": False}]
		
	def run(self):
		print(threading.current_thread().name, self.receive_messages)
		loop_warble = warble_job()
		loop_warble.start()
		while True:
			print(threading.current_thread().name, self.receive_messages)
			dr_closing = self.message_var[1]["dr_closing"]
			dr_opening = self.message_var[0]["dr_opening"]
			alarm_state = self.message_var[3]["alert"]
			warble_state = self.message_var[2]["warble"]
			print(dr_closing,dr_opening,alarm_state,warble_state)		
			warble = loop_warble.is_alive()
			print(warble)
			time.sleep(1)

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
		print("RUN RUN RUN")
		#print(dir(warble))
		#print(dir(warble.__getattribute__))
		audio_job = job(args=("1"))
		audio_job.start()
		time.sleep(0.1)
		channel.basic_consume(queue='audio',on_message_callback=callback, auto_ack=True)
		channel.start_consuming()

	except KeyboardInterrupt or Exception or OSError as e:
		print("Termination", e)
		sys.exit(1)
