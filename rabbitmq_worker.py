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

		self.position = GPS_DATA

	# Returns all the data for the fragment.
	def get(self):
		return [self.value, self.mini, self.maxi, self.dsc, self.sym, self.dev, self.timestamp, self.position[0], self.position[1]]

	# Returns only the info constants for this fragment
	def get_info(self):
		return [self.mini, self.maxi, self.dsc, self.sym, self.dev]
	
class Sensor(object):
	def __init__(self):
			self.gps_speed = Fragment(0.0,0.0,"GPS Speed","kn", "gps")
	
			self.totalmem = psutil.virtual_memory()
			self.deg_sym = '\xB0'
			self.cputemp = Fragment(0, 100, "CpuTemp", self.deg_sym + "c", "RaspberryPi")
			self.cpuperc = Fragment(0,100,"CpuPercent","%","Raspberry Pi")
			self.virtmem = Fragment(0,self.totalmem,"VirtualMemory","b","RaspberryPi")
			self.bytsent = Fragment(0,100000,"BytesSent","b","RaspberryPi")
			self.bytrece = Fragment(0, 100000,"BytesReceived","b","RaspberryPi")
			
			self.sinewav = Fragment(-100,100,"SineWave", "","RaspberryPi")
			self.tanwave = Fragment(-500,500,"TangentWave", "","RaspberryPi")
			self.coswave = Fragment(-100,100,"CosWave", "","RaspberryPi")
			self.sinwav2 = Fragment(-100,100,"SineWave2", "","RaspberryPi")
			
			self.sh_temp = Fragment(-40,120,"Thermometer",self.deg_sym + "c", "sensehat")
			self.sh_humi = Fragment(0,100,"Hygrometer", "%", "sensehat")
			self.sh_baro = Fragment(260,1260,"Barometer","hPa", "sensehat")
			self.sh_magx = Fragment(-500,500,"MagnetX","G", "sensehat")
			self.sh_magy = Fragment(-500,500,"MagnetY","G", "sensehat")
			self.sh_magz = Fragment(-500,500,"MagnetZ","G", "sensehat")
			self.sh_accx = Fragment(-500,500,"AccelX","g", "sensehat")
			self.sh_accy = Fragment(-500,500,"AccelY","g", "sensehat")
			self.sh_accz = Fragment(-500,500,"AccelZ","g", "sensehat")

			self.irt_ambi = Fragment(0,80,"IR ambient [mlx]","C",self.deg_sym + "c")
			self.irt_obje = Fragment(0,80,"IR object [mlx]","C",self.deg_sym + "c")

			self.ep_temp = Fragment(0,65,"Thermometer",self.deg_sym + "c","Envirophat")
			self.ep_colo = Fragment(20,80,"Colour", "RGB","Envirophat")
			self.ep_baro = Fragment(260,1260,"Barometer","hPa","Envirophat")
			self.ep_magx = Fragment(-500,500,"Magnetomer X","G","Envirophat")
			self.ep_magy = Fragment(-500,500,"Magnetomer Y","G","Envirophat")
			self.ep_magz = Fragment(-500,500,"Magnetomer Z","G","Envirophat")
			self.ep_accx = Fragment(-500,500,"Accelerometer X (EP)","g","Envirophat")
			self.ep_accy = Fragment(-500,500,"Accelerometer Y (EP)","g","Envirophat")
			self.ep_accz = Fragment(-500,500,"Accelerometer Z (EP)","g","Envirophat")
			
			self.bme_temp = Fragment(-40,85,"Thermometer",self.deg_sym + "c", "BME680")
			self.bme_humi = Fragment(0,100,"Hygrometer", "%", "BME680")
			self.bme_press = Fragment(300,1100,"Barometer","hPa", "BME680")
			self.bme_voc = Fragment(300000,1100000,"VOC","KOhm", "BME680")
			
			self.radiat = Fragment(0.0, 10000.0, "Radiation", "ur/h", "pocketgeiger")
			self.amg_high = Fragment(0.0, 80.0, "IRHigh", self.deg_sym + "c", "amg8833")
			self.amg_low = Fragment(0.0, 80.0, "IRLow", self.deg_sym + "c", "amg8833")
			
			configure.sensor_info = self.get_all_info()
			
			
	def get_all_info(self):
		info = self.get()

		allinfo = []
		for fragment in info:
			thisfrag = [fragment.dsc,fragment.dev,fragment.sym, fragment.mini, fragment.maxi]
			allinfo.append(thisfrag)
		return allinfo
		
	def get(self):
		#sensorlist holds all the data fragments to be handed to plars.
		sensorlist = []

		#timestamp for this sensor get.
		timestamp = time.time()
		position = GPS_DATA
		
		self.gps_speed.set(0,timestamp, position)
		
		self.bme_temp.set(0,timestamp, position)
		self.bme_humi.set(0,timestamp, position)
		self.bme_press.set(0,timestamp, position)
		self.bme_voc.set(0 / 1000,timestamp, position)
		
		sensorlist.extend((self.bme_temp,self.bme_humi,self.bme_press, self.bme_voc))
		
		magdata = {"x":0,"y":0,"z":0}
		acceldata = {"x":0,"y":0,"z":0}
		
		self.sh_temp.set(0,timestamp, position)
		self.sh_humi.set(0,timestamp, position)
		self.sh_baro.set(0,timestamp, position)
		self.sh_magx.set(magdata["x"],timestamp, position)
		self.sh_magy.set(magdata["y"],timestamp, position)
		self.sh_magz.set(magdata["z"],timestamp, position)
		self.sh_accx.set(acceldata['x'],timestamp, position)
		self.sh_accy.set(acceldata['y'],timestamp, position)
		self.sh_accz.set(acceldata['z'],timestamp, position)

		sensorlist.extend((self.sh_temp, self.sh_baro, self.sh_humi, self.sh_magx, self.sh_magy, self.sh_magz, self.sh_accx, self.sh_accy, self.sh_accz))
		
		data = {"uSvh":0}
		rad_data = float(data["uSvh"])
		
		self.radiat.set(rad_data*100, timestamp, position)
		sensorlist.append(self.radiat)
		
		data = numpy.array([0,80])
		
		high = numpy.max(data)
		low = numpy.min(data)
		
		self.amg_high.set(high,timestamp, position)
		self.amg_low.set(low,timestamp, position)

		sensorlist.extend((self.amg_high, self.amg_low))
		
		self.mag_values = {0:0,1:0,2:0}
		self.acc_values = {0:0,1:0,2:0}
		
		self.ep_temp.set(0,timestamp, position)
		self.ep_colo.set(0,timestamp, position)
		self.ep_baro.set(0, timestamp, position)
		self.ep_magx.set(self.mag_values[0],timestamp, position)
		self.ep_magy.set(self.mag_values[1],timestamp, position)
		self.ep_magz.set(self.mag_values[2],timestamp, position)
		self.ep_accx.set(self.acc_values[0],timestamp, position)
		self.ep_accy.set(self.acc_values[1],timestamp, position)
		self.ep_accz.set(self.acc_values[2],timestamp, position)

		sensorlist.extend((self.ep_temp, self.ep_baro, self.ep_colo, self.ep_magx, self.ep_magy, self.ep_magz, self.ep_accx, self.ep_accy, self.ep_accz))
		
		self.cputemp.set(0,timestamp, position)
		self.cpuperc.set(float(psutil.cpu_percent()),timestamp, position)
		self.virtmem.set(float(psutil.virtual_memory().available * 0.0000001),timestamp, position)
		self.bytsent.set(float(psutil.net_io_counters().bytes_recv * 0.00001),timestamp, position)
		self.bytrece.set(float(psutil.net_io_counters().bytes_recv * 0.00001),timestamp, position)
		
		self.sinewav.set(float(1*100),timestamp, position)
		self.tanwave.set(float(1*100),timestamp, position)
		self.coswave.set(float(1*100),timestamp, position)
		self.sinwav2.set(float(1*100),timestamp, position)
		
		sensorlist.extend((self.cputemp, self.cpuperc, self.virtmem, self.bytsent, self.bytrece))
		
		sensorlist.extend((self.sinewav, self.tanwave, self.coswave, self.sinwav2)) 
		
		configure.max_sensors[0] = len(sensorlist)
		
		return sensorlist

def callback_rabbitmq(ch, method, properties, body):
	#print('book=', mapping_book_byname)
	#print('populating=', method.routing_key)
	if method.routing_key == 'GPS_DATA':
		GPS_DATA = body.decode()
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
			
			
def threaded_rabbitmq_worker():
	global mapping_book_byname
	global mapping_book
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
		configure.sensor_ready[0] = True
		channel.basic_consume(queue='',on_message_callback=callback_rabbitmq, auto_ack=True)
		channel.start_consuming()
