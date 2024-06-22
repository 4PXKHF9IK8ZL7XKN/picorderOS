from multiprocessing import Process,Queue,Pipe
from objects import *
from classes import Sensor
from classes import Fragment
from random import randint


import json
import random
import time
import math

#	PLARS (Picorder Library Access and Retrieval System) aims to provide a
#	single surface for storing and retrieving data for display in any of the
#	different Picorder screen modes.

import os
import numpy
import datetime
from array import *
import pandas as pd
import json
import pika
import ast

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.exchange_declare(exchange='sensor_data', exchange_type='topic')
channel.queue_declare(queue='sensor_metadata');

GPS_DATA = [4747.0000,4747.0000]
mapping_book = {}
mapping_book_byname = {}

print("Loading Picorder Library Access and Retrieval System Module")

# Broken out functions for use with processing:

class PLARS(object):

	BUFFER_GLOBAL = pd.DataFrame(columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude'])
	
	def __init__(self):

		# add a lock to avoid race conditions
		self.lock = threading.Lock()

		# PLARS opens a data frame at initialization.
		# If the csv file exists it opens it, otherwise creates it.
		# self.core is used to refer to the archive on disk for sensor data
		# self.em_core is used to refer to the archive on disk for EM data
		# self.buffer is created as a truncated dataframe for drawing to screen.
		# self.buffer_em is created as a truncated dataframe for drawing  to screen.
			
		# create buffer
		self.file_path = "data/datacore.csv"
		self.em_file_path = "data/em_datacore.csv"
		


		if configure.datalog[0]:

			# make sure the data folder exist
			if not os.path.exists("data"):
					os.mkdir("data")

			# check if a datacore csv file exists
			if os.path.exists(self.file_path):
				self.core = pd.read_csv(self.file_path)
			else:
				self.core = pd.DataFrame(columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude'])
				self.core.to_csv(self.file_path)

			# check if an EM datacore csv file exists
			if os.path.exists(self.em_file_path):
				self.em_core = pd.read_csv(self.em_file_path)
			else:
				self.em_core = pd.DataFrame(columns=['ssid','signal','quality','frequency','encrypted','channel','dev','mode','dsc','timestamp','latitude','longitude'])
				self.em_core.to_csv(self.em_file_path)



		# Set floating point display to raw, instead of exponent
		pd.set_option('display.float_format', '{:.7f}'.format)

		#create a buffer object to hold screen data
		self.buffer = pd.DataFrame(columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude'])
		
		#create a buffer for wifi/bt data
		self.buffer_em = pd.DataFrame(columns=['ssid','signal','quality','frequency','encrypted','channel','dev','mode','dsc','timestamp','latitude','longitude'])


		# variables for EM stats call
		# all unique MACs received during session
		self.em_idents = []
		
		# how many APs this scan
		self.current_em_no = 0

		# Max number APs detected in one scan this session
		self.max_em_no = 0


		# holds the thermal camera frame for display in other programs
		self.thermal_frame = []

		self.timer = timer()

	def get_plars_size(self):

		# set the thread lock so other threads are unable to add data
		self.lock.acquire()

		main_size = len(self.buffer)
		em_size = len(self.buffer_em)
		
		# release the thread lock.
		self.lock.release()
		return main_size, em_size

	def get_em_stats(self):

		return self.em_idents, self.current_em_no, self.max_em_no

	def shutdown(self):
		if configure.datalog[0]:
			self.append_to_core(self.buffer)
			self.append_to_em_core(self.buffer_em)

	# gets the latest CSV file
	def get_core(self):
		datacore = pd.read_csv(self.file_path)
		return datacore

	#appends a new set of data to the CSV file.
	def append_to_core(self, data):
		data.to_csv(self.file_path, mode='a', header=False)

	#appends a new set of data to the EM CSV file.
	def append_to_em_core(self, data):
		data.to_csv(self.em_file_path, mode='a', header=False)

	def get_recent_bt_list(self):
		# set the thread lock so other threads are unable to add data
		self.lock.acquire()

		# get the most recent ssids discovered
		recent_em = self.get_bt_recent()

		# release the thread lock.
		self.lock.release()

		return recent_em.values.tolist()


	# returns a list of every EM transciever that was discovered last scan.
	def get_recent_em_list(self):

		# set the thread lock so other threads are unable to add data
		self.lock.acquire()

		# get the most recent ssids discovered
		recent_em = self.get_em_recent()

		# sort it by signal strength
		recent_em.sort_values(by=['signal'], ascending = False)

		# release the thread lock.
		self.lock.release()

		return recent_em.values.tolist()

	def get_top_em_info(self):

		#find the most recent timestamp to limit focus
		focus = self.get_em_recent()

		# find most powerful signal of the most recent transciever data
		db_column = focus["signal"]
		
		strongest = db_column.astype(int).max()

		# Identify the SSID of the strongest signal.
		self.identity = focus.loc[focus['signal'] == strongest]

		# Return the SSID of the strongest signal as a list.
		return self.identity.values.tolist()

	def get_em_recent(self):
		wifi_buffer = self.buffer_em.loc[self.buffer_em['dsc'] == "wifi"]

		# find the most recent timestamp
		time_column = wifi_buffer["timestamp"]
		most_recent = time_column.max()

		#limit focus to data from that timestamp
		return wifi_buffer.loc[wifi_buffer['timestamp'] == most_recent]
	
	# checks if a mac address has been seen already and if not adds it to list.
	def em_been_seen(self, seen):
		pass

	def get_bt_recent(self):
		bt_buffer = self.buffer_em.loc[self.buffer_em['dsc'] == "bluetooth"]
		# find the most recent timestamp
		time_column = bt_buffer["timestamp"]
		most_recent = time_column.max()

		#limit focus to data from that timestamp
		return bt_buffer.loc[bt_buffer['timestamp'] == most_recent]

	def get_top_em_history(self, no = 5):
		# returns a list of Db values for whatever SSID is currently the strongest.
		# suitable to be fed into pilgraph for graphing.

		# set the thread lock so other threads are unable to add data
		self.lock.acquire()

		#limit focus to data from that timestamp
		focus = self.get_em_recent()

		# find most powerful signal
		db_column = focus["signal"]
		strongest = db_column.astype(int).max()

		# Identify the SSID of the strongest signal.
		self.identity = focus.loc[focus['signal'] == strongest]


		# prepare markers to pull data
		# Wifi APs can have the same name and different paramaters
		# I use MAC and frequency to individualize a signal
		dev = self.identity["dev"].iloc[0]
		frq = self.identity["frequency"].iloc[0]


		# release the thread lock.
		self.lock.release()

		return self.get_recent_em(dev,frq, num = no)


	def update_em(self,data):
		#print("Updating EM Dataframe:")

		# sets/requests the thread lock to prevent other threads reading data.
		self.lock.acquire()


		# logs some data for statistics.nan
		self.current_em_no = len(data)
		if self.current_em_no > self.max_em_no:
			self.max_em_no = self.current_em_no


		for sample in data:
			if sample[6] not in self.buffer_em["dev"].values and sample[6] not in self.em_idents:
				self.em_idents.append(sample[6])

		q = Queue()

		get_process = Process(target=update_em_proc, args=(q, self.buffer_em, data,['ssid','signal','quality','frequency','encrypted','channel','dev','mode','dsc','timestamp','latitude','longitude'],))
		get_process.start()

		# return a list of the values
		result = q.get()
		get_process.join()

		# appends the new data to the buffer
		self.buffer_em = result


		# get buffer size to determine how many rows to remove from the end
		currentsize = len(self.buffer_em)

		if configure.trim_buffer[0]:
			# if buffer is larger than double the buffer size
			if currentsize >= configure.buffer_size[0] * 2:
				self.buffer_em = self.trim_em_buffer(configure.buffer_size[0])

		self.lock.release()


	# updates the thermal frame for display
	def update_thermal(self, frame):
		self.thermal_frame = frame

	# updates the dataframe in memory with the most recent sensor values from each
	# initialized sensor.
	# Sensor data is taken in as Fragment() instance objects. Each one contains
	# the sensor value and context for it (scale, symbol, unit, etc).
	def update(self,ch, method, properties, body):
		#print('book=', mapping_book_byname)
		#print('populating=', method.routing_key)
		
		timestamp = time.time()
		value = random.randint(1, 100) 
		sensors = Sensor()
		fragdata = []
		sensor_values = []
		timestamp = time.time()
		
		BME680 = [[0,-40,8,'Thermometer','\xB0','BME680','timestamp'],[0,0,100,'Hygrometer','%','BME680','timestamp'],[0,300,1100,'Barometer','hPa','BME680','timestamp'],[0,0,500,'VOC','ppm','BME680','timestamp'],[0,0,1100,'ALT','m','BME680','timestamp']]
			
		if method.routing_key == 'GPS_DATA':
			GPS_DATA = body.decode()
		elif method.routing_key == 'bme680':	
			# decodes data byte stream and splits the values by comma
			sensor_values = body.decode().strip("()").split(",")		
			index = 0
			for value in sensor_values:
				#print("BME680:", float(value))
				BME680[index][0] = float(value)					
				BME680[index][6] = timestamp
				#print("MATRIX", BME680[index])
				fragdata.append(BME680[index])		
				# creates a new dataframe to add new data 	
				newdata = pd.DataFrame(fragdata, columns=['value','min','max','dsc','sym','dev','timestamp'])
				PLARS.BUFFER_GLOBAL = pd.concat([PLARS.BUFFER_GLOBAL,newdata]).drop_duplicates().reset_index(drop=True)
				#PLARS.BUFFER_GLOBAL = pd.concat([PLARS.BUFFER_GLOBAL,newdata]).reset_index(drop=True)
				index = index + 1			
		
		elif method.routing_key == 'system_vitals':
			#print("type:",type(body.decode()))
			var1 = body.decode().split(",")	


		currentsize = len(PLARS.BUFFER_GLOBAL)

		if configure.buffer_size[0] == 0:
			targetsize = 64 * configure.max_sensors[0]
		else:
			targetsize = configure.buffer_size[0]


		# determine difference between buffer and target size
		length = currentsize - targetsize
		if currentsize > targetsize:
			# when 200 is reached the first index is dropped, we cant see him.
			PLARS.BUFFER_GLOBAL.drop(range(0, length), inplace=True)




	# return a list of n most recent data from specific sensor defined by keys
	# gets Called from pilgraph
	def get_recent(self, dsc, dev, num, timeing):	
		# Filters the pd Dataframe to a Device like dsc="Thermometer" 
		

		
		result = PLARS.BUFFER_GLOBAL[PLARS.BUFFER_GLOBAL["dsc"] == dsc]
		##print("result")
		##print(result)
		
		untrimmed_data = result.loc[result['dev'] == dev]

		# trim it to length (num).
		trimmed_data = untrimmed_data.tail(num)


		# return a list of the values
		data_line = trimmed_data['value'].tolist()		
		times = trimmed_data['timestamp'].tolist()


		timelength = num

		return data_line, timelength


	def get_em(self,dev,frequency):
		result = self.buffer_em.loc[self.buffer_em['dev'] == dev]
		result2 = result.loc[result["frequency"] == frequency]

		return result2

	# returns all sensor data in the buffer for the specific sensor (dsc,dev)
	def get_sensor(self,dsc,dev):

		result = self.buffer[self.buffer["dsc"] == dsc]

		result2 = result.loc[result['dev'] == dev]

		return result2


	def index_by_time(self,df, ascending = False):
		df.sort_values(by=['timestamp'], ascending = ascending)
		return df


	# return a list of n most recent data from specific ssid defined by keys
	def get_recent_em(self, dev, frequency, num = 5):

		# get a dataframe of just the requested sensor
		untrimmed_data = self.get_em(dev,frequency)

		# trim it to length (num).
		trimmed_data = untrimmed_data.tail(num)

		# return a list of the values
		return trimmed_data['signal'].tolist()

	def trim_em_buffer(self, targetsize):
		# should take the buffer in memory and trim some of it

		# get buffer size to determine how many rows to remove from the end
		currentsize = len(self.buffer_em)

		# determine difference between buffer and target size
		length = currentsize - targetsize

		# make a new dataframe of the most recent data to keep using
		newbuffer = self.buffer_em.tail(targetsize)

		# slice off the rows outside the buffer and backup to disk
		tocore = self.buffer_em.head(length)

		if configure.datalog[0]:
				self.append_to_em_core(tocore)

		# replace existing buffer with new trimmed buffer
		return newbuffer

	def trimbuffer(self, targetsize):
		# should take the buffer in memory and trim some of it

		# get buffer size to determine how many rows to remove from the end
		currentsize = len(self.buffer)

		# determine difference between buffer and target size
		length = currentsize - targetsize

		# make a new dataframe of the most recent data to keep using
		newbuffer = self.buffer.tail(targetsize)

		# slice off the rows outside the buffer and backup to disk
		tocore = self.buffer.head(length)

		if configure.datalog[0]:
				self.append_to_core(tocore)


		# replace existing buffer with new trimmed buffer
		return newbuffer


	def emrg(self):
		self.get_core()
		return self.df

	def convert_epoch(self, time):
		return datetime.datetime.fromtimestamp(time)
		
	def response_check(self):
		return True
		
# updates the dataframe in memory with the most recent sensor values from each
# initialized sensor.
# Sensor data is taken in as Fragment() instance objects. Each one contains
# the sensor value and context for it (scale, symbol, unit, etc).
def callback_rabbitmq(ch, method, properties, body):
	plars = PLARS()
	plars.update(ch, method, properties, body)
	
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

# create a process that can run seperately and handle requests
def threaded_plars():
	channel.basic_consume(consumer_tag='sensor_metadata',queue='sensor_metadata',on_message_callback=callback_rabbitmq_meta, auto_ack=True)
	# Waiting for the Metadata message ca 10 sec
	channel.start_consuming()

	
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
		print("Avail:", len(configure.sensor_info))
		configure.sensor_ready[0] = True
		channel.basic_consume(queue='',on_message_callback=callback_rabbitmq, auto_ack=True)
		while True:
			try:
				channel.start_consuming()
			except:
				pass


# Creates a plars database object as soon as it is loaded.
plars = PLARS()
