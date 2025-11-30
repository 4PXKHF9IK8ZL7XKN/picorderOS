# PicorderOS Wifi Module Proto
print("Loading Modulated EM Signal Analysis")

#!/bin/python
import time
import sys
import pika
import picosglobals
import subprocess


from objects import *
from bluetooth import *

DEBUG = False

if configure.rabbitmq_remote:
	credentials = pika.PlainCredentials(configure.rabbitmq_user,configure.rabbitmq_password)
	connection = pika.BlockingConnection(pika.ConnectionParameters(configure.rabbitmq_address,configure.rabbitmq_port,configure.rabbitmq_vhost,credentials))
	channel = connection.channel()
else:
	connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
	channel = connection.channel()

def declare_channel():
	# Setup Channels for Sensors
	channel.exchange_declare(exchange='sensor_data', exchange_type='topic')
	channel.queue_declare(queue='sensor_metadata')
	# cleanup entreys , we could have multible index
	channel.queue_purge(queue='sensor_metadata')

def publish_wifi_stats(IN_routing_key,data):
	stack = 'sensor_data'
	if IN_routing_key == 'sensor_metadata':
		stack = ''

	routing_key = str(IN_routing_key)
	message = str(data)
	time_unix = time.time()
	try:
		if message is not None:
			channel.basic_publish(exchange=stack, routing_key=routing_key, body=message)
		else:
			print("Is that a buffer underflow?")
	except Exception as e:
		print("An error occurred:",e)
		try:
			raise Exception('Terminating')
		finally:
			sys.exit(1)
	if DEBUG:
		print(f" {time_unix} [x] Sent {stack} {routing_key}:{message}")

def disconnect():
    connection.close()

class sensor_functions(object):

	def __init__(self):

		if configure.generators:
			self.step = 0
			self.step2 = 0
			self.steptan = 0
				
		
	def get_wifi_stats(self):
		GPS_DATA = picosglobals.GPS_DATA
		timestamp = time.time()
		matrix = {}
		connection_ID = 0

		process = subprocess.Popen(["sudo","iw", "wlan0", "scan"], stdout=subprocess.PIPE)
		
		mac = ""
		interface = ""
		
		
		for line in process.stdout:
			clean_line = line.decode().strip()
			
			if clean_line.startswith("BSS Load:"):
				if 'BSS Load' not in matrix[interface][connection_ID-1][mac]:
					matrix[interface][connection_ID-1][mac]['BSS Load'] = []		

			elif clean_line.startswith("BSS"):
				bss_line = clean_line.split(" ")
				mac, _ = bss_line[1].split("(")
				interface, _ = bss_line[2].split(")")
				if len(bss_line) == 5:
					status = bss_line[4]
				else:
					status = ""

				if interface not in matrix:	
					matrix[interface] = []
				matrix[interface].append({mac: {"status" : status}})
				connection_ID = connection_ID + 1
			
			if clean_line.startswith("freq:"):
				k,v = clean_line.split(" ")
				matrix[interface][connection_ID-1][mac][k] = v
				
			if clean_line.startswith("signal:"):
				k,v,t = clean_line.split(" ")
				matrix[interface][connection_ID-1][mac][k] = v, t
				
			if clean_line.startswith("capability:"):
				k,v = clean_line.split(":")
				list_capability = v.strip().split(" ")
				matrix[interface][connection_ID-1][mac][k.strip()] = list_capability
				
			if clean_line.startswith("Supported rates:"):
				k,v = clean_line.split(":")
				list_rates = v.strip().split(" ")
				matrix[interface][connection_ID-1][mac][k.strip()] = list_rates		
				
			if clean_line.startswith("Country:"):
				k,v,t = clean_line.split(":")
				matrix[interface][connection_ID-1][mac][k.strip()] = v.strip('Environment').strip(), {"Environment": t.strip()}
				
			if clean_line.startswith("TPC report:"):
				k,v,t = clean_line.split(":")
				matrix[interface][connection_ID-1][mac][k.strip()] = {"TX power": t.strip()}			
			
			if clean_line.startswith("SSID:"):
				k,v = clean_line.split(":")
				matrix[interface][connection_ID-1][mac][k] = v
				
			if clean_line.startswith("Power constraint:"):
				k,v = clean_line.split(":")
				matrix[interface][connection_ID-1][mac][k] = v.strip()
				
				
			if clean_line.startswith("DS Parameter set:"):
				k,v = clean_line.split(":")
				matrix[interface][connection_ID-1][mac][k] = v.strip()
			
			if clean_line.startswith("RSN:"):
				print("DEBUG")
				print(clean_line)
				k,v,t = clean_line.split(":")				
				_,v = v.split("*")
				matrix[interface][connection_ID-1][mac][k.strip()] = {v.strip(): t.strip()}
			else:
				matrix[interface][connection_ID-1][mac]['RSN'] = {'RSN': "STATIC"}
				
			if clean_line.startswith("Channels"):
				k,v0,v1,v2,v3,v4,v5 = clean_line.split(" ")
				if k.strip() not in matrix[interface][connection_ID-1][mac]:
					matrix[interface][connection_ID-1][mac][k.strip()] = []
				matrix[interface][connection_ID-1][mac][k.strip()].append([v0.strip('['),v2.strip(']'),v4,v5])			
				
				
			if clean_line.startswith("* Group cipher:"):
				k,v = clean_line.split(":")
				_,k = k.split("*")
				matrix[interface][connection_ID-1][mac]['RSN'][k.strip()] =  v.strip()
				
			if clean_line.startswith("* Pairwise ciphers:"):
				k,v = clean_line.split(":")
				_,k = k.split("*")
				matrix[interface][connection_ID-1][mac]['RSN'][k.strip()] =  v.strip()
				
			if clean_line.startswith("* Authentication suites:"):
				k,v = clean_line.split(":")
				_,k = k.split("*")
				matrix[interface][connection_ID-1][mac]['RSN'][k.strip()] =  v.strip()

			if clean_line.startswith("* Capabilities:"):
				k,v = clean_line.split(":")
				_,k = k.split("*")
				matrix[interface][connection_ID-1][mac]['RSN'][k.strip()] =  v.strip()

			if clean_line.startswith("* station count:"):
				k,v = clean_line.split(":")
				_,k = k.split("*")
				matrix[interface][connection_ID-1][mac]['BSS Load'].append({k.strip() :  v.strip()} )
				
			if clean_line.startswith("* channel utilisation:"):
				k,v = clean_line.split(":")
				_,k = k.split("*")
				matrix[interface][connection_ID-1][mac]['BSS Load'].append({k.strip() :  v.strip()} )
				
			if clean_line.startswith("* available admission capacity:"):
				k,v = clean_line.split(":")
				_,k = k.split("*")
				matrix[interface][connection_ID-1][mac]['BSS Load'].append({k.strip() :  v.strip()} )
				
			if clean_line.startswith("Extended capabilities:"):
				if 'Extended capabilities' not in matrix[interface][connection_ID-1][mac]:
					matrix[interface][connection_ID-1][mac]['Extended capabilities'] = []	
					
			if clean_line.startswith("* Extended Channel Switching"):
				v = clean_line.strip("*")
				matrix[interface][connection_ID-1][mac]['Extended capabilities'].append(v.strip())
				
			if clean_line.startswith("* Event"):
				v = clean_line.strip("*")
				matrix[interface][connection_ID-1][mac]['Extended capabilities'].append(v.strip())
				
			if clean_line.startswith("* BSS Transition"):
				v = clean_line.strip("*")
				matrix[interface][connection_ID-1][mac]['Extended capabilities'].append(v.strip())
				
			if clean_line.startswith("* Interworking"):
				v = clean_line.strip("*")
				matrix[interface][connection_ID-1][mac]['Extended capabilities'].append(v.strip())
				
			if clean_line.startswith("* Operating Mode Notification"):
				v = clean_line.strip("*")
				matrix[interface][connection_ID-1][mac]['Extended capabilities'].append(v.strip())
				
			if clean_line.startswith("* Channel Schedule Management"):
				v = clean_line.strip("*")
				matrix[interface][connection_ID-1][mac]['Extended capabilities'].append(v.strip())
				
			if clean_line.startswith("* 6"):
				v = clean_line.strip("*")
				matrix[interface][connection_ID-1][mac]['Extended capabilities'].append(v.strip())
				
							
			if clean_line.startswith("* Max Number Of MSDUs In A-MSDU is"):
				v = clean_line.strip("*")
				matrix[interface][connection_ID-1][mac]['Extended capabilities'].append(v.strip())
				
			if clean_line.startswith("802."):
				if 'IEEE 802 Options' not in matrix[interface][connection_ID-1][mac]:
					matrix[interface][connection_ID-1][mac]['IEEE 802 Options'] = []	
				matrix[interface][connection_ID-1][mac]['IEEE 802 Options'].append(clean_line.strip(':'))

			if clean_line.startswith("WPS:"):
				k,v,t = clean_line.split(":")				
				_,v = v.split("*")
				matrix[interface][connection_ID-1][mac][k.strip()] = {v.strip(): t.strip()}
				
			if clean_line.startswith("* Wi-Fi Protected Setup State:"):
				k,v = clean_line.split(":")
				_,k = k.split("*")
				matrix[interface][connection_ID-1][mac]['WPS'][k.strip()] =  v.strip()
				
			if clean_line.startswith("* Version2:"):
				k,v = clean_line.split(":")
				_,k = k.split("*")
				matrix[interface][connection_ID-1][mac]['WPS'][k.strip()] =  v.strip()
	
			#print(matrix[interface][connection_ID-1][mac]["Channels"])
			
		#print(matrix)
	
		return matrix ,timestamp, GPS_DATA[0], GPS_DATA[1], configure.rabbitmq_tag



if __name__ == "__main__":
	if configure.generators:
		try:
			declare_channel()
			timed = timer()
			sensors = sensor_functions()

			while True:	
				wifi_stats = sensors.get_wifi_stats()	
				publish_wifi_stats('wifi_stats',wifi_stats)
				time.sleep(30)
			sys.exit(1)

			signal.signal(signal.SIGINT, signal_handler)
		except KeyboardInterrupt or Exception or OSError as e:
			print("Termination", e)
			disconnect()
			sys.exit(1)
	else:
		print("Service Disabled")
		exit(1)

