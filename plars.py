from multiprocessing import Process,Queue,Pipe
from objects import *
from piosclasses import Sensor
#from classes import Fragment
from random import randint


import json
import random
import time
import math
import psutil

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

sensors = Sensor()

print("Loading Picorder Library Access and Retrieval System Module")

# Broken out functions for use with processing:

BUFFER_GLOBAL = pd.DataFrame(columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude'])

# PLARS opens a data frame at initialization.
# If the csv file exists it opens it, otherwise creates it.
# core is used to refer to the archive on disk for sensor data
# em_core is used to refer to the archive on disk for EM data
# buffer is created as a truncated dataframe for drawing to screen.
# buffer_em is created as a truncated dataframe for drawing  to screen.
	
# create buffer
file_path = "data/datacore.csv"
em_file_path = "data/em_datacore.csv"



if configure.datalog[0]:

	# make sure the data folder exist
	if not os.path.exists("data"):
			os.mkdir("data")

	# check if a datacore csv file exists
	if os.path.exists(file_path):
		core = pd.read_csv(file_path)
	else:
		core = pd.DataFrame(columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude'])
		core.to_csv(file_path)

	# check if an EM datacore csv file exists
	if os.path.exists(em_file_path):
		em_core = pd.read_csv(em_file_path)
	else:
		em_core = pd.DataFrame(columns=['ssid','signal','quality','frequency','encrypted','channel','dev','mode','dsc','timestamp','latitude','longitude'])
		em_core.to_csv(em_file_path)



	# Set floating point display to raw, instead of exponent
	pd.set_option('display.float_format', '{:.7f}'.format)

	#create a buffer object to hold screen data
	buffer = pd.DataFrame(columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude'])
	
	#create a buffer for wifi/bt data
	buffer_em = pd.DataFrame(columns=['ssid','signal','quality','frequency','encrypted','channel','dev','mode','dsc','timestamp','latitude','longitude'])


	# variables for EM stats call
	# all unique MACs received during session
	em_idents = []
	
	# how many APs this scan
	current_em_no = 0

	# Max number APs detected in one scan this session
	max_em_no = 0


	# holds the thermal camera frame for display in other programs
	thermal_frame = []

	timer = timer()

def get_plars_size():

	# set the thread lock so other threads are unable to add data
	lock.acquire()

	main_size = len(buffer)
	em_size = len(buffer_em)
	
	# release the thread lock.
	lock.release()
	return main_size, em_size

def get_em_stats():

	return em_idents, current_em_no, max_em_no

def shutdown():
	if configure.datalog[0]:
		append_to_core(buffer)
		append_to_em_core(buffer_em)

# gets the latest CSV file
def get_core():
	datacore = pd.read_csv(file_path)
	return datacore

#appends a new set of data to the CSV file.
def append_to_core( data):
	data.to_csv(file_path, mode='a', header=False)

#appends a new set of data to the EM CSV file.
def append_to_em_core( data):
	data.to_csv(em_file_path, mode='a', header=False)

def get_recent_bt_list():
	# set the thread lock so other threads are unable to add data
	lock.acquire()

	# get the most recent ssids discovered
	recent_em = get_bt_recent()

	# release the thread lock.
	lock.release()

	return recent_em.values.tolist()


# returns a list of every EM transciever that was discovered last scan.
def get_recent_em_list():

	# set the thread lock so other threads are unable to add data
	lock.acquire()

	# get the most recent ssids discovered
	recent_em = get_em_recent()

	# sort it by signal strength
	recent_em.sort_values(by=['signal'], ascending = False)

	# release the thread lock.
	lock.release()

	return recent_em.values.tolist()

def get_top_em_info():

	#find the most recent timestamp to limit focus
	focus = get_em_recent()

	# find most powerful signal of the most recent transciever data
	db_column = focus["signal"]
	
	strongest = db_column.astype(int).max()

	# Identify the SSID of the strongest signal.
	identity = focus.loc[focus['signal'] == strongest]

	# Return the SSID of the strongest signal as a list.
	return identity.values.tolist()

def get_em_recent():
	wifi_buffer = buffer_em.loc[buffer_em['dsc'] == "wifi"]

	# find the most recent timestamp
	time_column = wifi_buffer["timestamp"]
	most_recent = time_column.max()

	#limit focus to data from that timestamp
	return wifi_buffer.loc[wifi_buffer['timestamp'] == most_recent]

# checks if a mac address has been seen already and if not adds it to list.
def em_been_seen( seen):
	pass

def get_bt_recent():
	bt_buffer = buffer_em.loc[buffer_em['dsc'] == "bluetooth"]
	# find the most recent timestamp
	time_column = bt_buffer["timestamp"]
	most_recent = time_column.max()

	#limit focus to data from that timestamp
	return bt_buffer.loc[bt_buffer['timestamp'] == most_recent]

def get_top_em_history( no = 5):
	# returns a list of Db values for whatever SSID is currently the strongest.
	# suitable to be fed into pilgraph for graphing.

	# set the thread lock so other threads are unable to add data
	lock.acquire()

	#limit focus to data from that timestamp
	focus = get_em_recent()

	# find most powerful signal
	db_column = focus["signal"]
	strongest = db_column.astype(int).max()

	# Identify the SSID of the strongest signal.
	identity = focus.loc[focus['signal'] == strongest]


	# prepare markers to pull data
	# Wifi APs can have the same name and different paramaters
	# I use MAC and frequency to individualize a signal
	dev = identity["dev"].iloc[0]
	frq = identity["frequency"].iloc[0]


	# release the thread lock.
	lock.release()

	return get_recent_em(dev,frq, num = no)


def update_em(data):
	#print("Updating EM Dataframe:")

	# sets/requests the thread lock to prevent other threads reading data.
	lock.acquire()


	# logs some data for statistics.nan
	current_em_no = len(data)
	if current_em_no > max_em_no:
		max_em_no = current_em_no


	for sample in data:
		if sample[6] not in buffer_em["dev"].values and sample[6] not in em_idents:
			em_idents.append(sample[6])

	q = Queue()

	get_process = Process(target=update_em_proc, args=(q, buffer_em, data,['ssid','signal','quality','frequency','encrypted','channel','dev','mode','dsc','timestamp','latitude','longitude'],))
	get_process.start()

	# return a list of the values
	result = q.get()
	get_process.join()

	# appends the new data to the buffer
	buffer_em = result


	# get buffer size to determine how many rows to remove from the end
	currentsize = len(buffer_em)

	if configure.trim_buffer[0]:
		# if buffer is larger than double the buffer size
		if currentsize >= configure.buffer_size[0] * 2:
			buffer_em = trim_em_buffer(configure.buffer_size[0])

	lock.release()


# updates the thermal frame for display
def update_thermal( frame):
	thermal_frame = frame

# updates the dataframe in memory with the most recent sensor values from each
# initialized sensor.
# Sensor data is taken in as Fragment() instance objects. Each one contains
# the sensor value and context for it (scale, symbol, unit, etc).
def update(ch, method, properties, body):
	global BUFFER_GLOBAL
	#print('book=', mapping_book_byname)
	#print('populating=', method.routing_key)
	
	timestamp = time.time()
	value = random.randint(1, 100) 
	#sensors = Sensor()
	fragdata = []
	sensor_values = []
	trimmbuffer_flag = False
	
	BME680 = [[0,-40,85,'Thermometer','\xB0','BME680','timestamp','latitude','longitude'],[0,0,100,'Hygrometer','%','BME680','timestamp','latitude','longitude'],[0,300,1100,'Barometer','hPa','BME680','timestamp','latitude','longitude'],[0,0,500,'VOC','ppm','BME680','timestamp','latitude','longitude'],[0,0,1100,'ALT','m','BME680','timestamp','latitude','longitude']]
	SYSTEMVITALES = [[0,0,'inf','Timer','t','RaspberryPi','timestamp','latitude','longitude'],[0,0,4,'INDICATOR','IND','RaspberryPi','timestamp','latitude','longitude'],[0,-25,100,'CpuTemp','\xB0','RaspberryPi','timestamp','latitude','longitude'],[0,0,400,'CpuPercent','%','RaspberryPi','timestamp','latitude','longitude'],[0,0,4800000,'VirtualMemory','b','RaspberryPi','timestamp','latitude','longitude'],[0,0,100,'disk_usage','%','RaspberryPi','timestamp','latitude','longitude'],[0,0,100000,'BytesSent','b','RaspberryPi','timestamp','latitude','longitude'],[0,0,100000,'BytesReceived','b','RaspberryPi','timestamp','latitude','longitude']]
	GENERATORS = [[0,-100,100,'SineWave','','RaspberryPi','timestamp','latitude','longitude'],[0,-500,500,'TangentWave','','RaspberryPi','timestamp','latitude','longitude'],[0,-100,100,'CosWave','','RaspberryPi','timestamp','latitude','longitude'],[0,-100,100,'SineWave2','','RaspberryPi','timestamp','latitude','longitude']]
	SENSEHAT = [[0,-40,120,'Thermometer','\xB0','sensehat','timestamp','latitude','longitude'],[0,0,100,'Hygrometer','%','sensehat','timestamp','latitude','longitude'],[0,260,1260,'Barometer','hPa','sensehat','timestamp','latitude','longitude'],[0,-500,500,'MagnetX','G','sensehat','timestamp','latitude','longitude'],[0,-500,500,'MagnetY','G','sensehat','timestamp','latitude','longitude'],[0,-500,500,'MagnetZ','G','sensehat','timestamp','latitude','longitude'],[0,-500,500,'"AccelX','g','sensehat','timestamp','latitude','longitude'],[0,-500,500,'"AccelY','g','sensehat','timestamp','latitude','longitude'],[0,-500,500,'"AccelZ','g','sensehat','timestamp','latitude','longitude']]
		
	# configure buffersize
	if configure.buffer_size[0] == 0:
		targetsize = 64
	else:
		targetsize = configure.buffer_size[0]
		
		
	if method.routing_key == 'GPS_DATA':
		GPS_DATA[0],GPS_DATA[1]  = body.decode().strip("[]").split(",")	
	elif method.routing_key == 'bme680':	
		# decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")		
		index = 0
		for value in sensor_values:
			#print("BME680:", float(value))
			BME680[index][0] = float(value)					
			BME680[index][6] = timestamp
			BME680[index][7] = GPS_DATA[0]
			BME680[index][8] = GPS_DATA[1]
			#print("MATRIX", BME680[index])
			fragdata.append(BME680[index])		
			# creates a new dataframe to add new data 	
			newdata = pd.DataFrame(fragdata, columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude'])
			BUFFER_GLOBAL = pd.concat([BUFFER_GLOBAL,newdata]).drop_duplicates().reset_index(drop=True)
			#BUFFER_GLOBAL = pd.concat([BUFFER_GLOBAL,newdata]).reset_index(drop=True)	
			# we get len of one sensor
			currentsize_persensor = len(BUFFER_GLOBAL[BUFFER_GLOBAL["dsc"] == BME680[index][3]])
			if currentsize_persensor > targetsize:
				trimmbuffer_flag = True		
			index = index + 1			

	elif method.routing_key == 'system_vitals':
		sensor_array_unclean = []
		sensor_values = [0,1,2,3,4,5,6,7]
		#decodes data byte stream and splits the values by comma
		sensor_array_unclean = body.decode().strip("()").split(",")
		cleanup_index = 0
		for value4555 in sensor_array_unclean:
			if cleanup_index == 0:
				# uptime
				sensor_values[0] = value4555.strip("'")
			elif cleanup_index == 1:
				# CPU Load Overall last min
				sensor_values[1] = float(value4555.strip('( '))
			elif cleanup_index == 5:
				# CPU Temperatur
				array2541 = value4555.rsplit('=')
				sensor_values[2] = float(array2541[1])
			elif cleanup_index == 8:
				# CPU Load in Percentage
				sensor_values[3] = float(value4555)
			elif cleanup_index == 9:
				# virtual mem
				sensor_values[4] = float(value4555)
			elif cleanup_index == 13:
				# diskussage in percentage i skipped bytes
				array56461 = value4555.rsplit('=')			
				sensor_values[5] = float(array56461[1].strip(' )'))
			elif cleanup_index == 14:
				# bytes send bytes
				sensor_values[6] = float(value4555)
			elif cleanup_index == 15:
				# bytes rec 
				sensor_values[7] = float(value4555)
			cleanup_index = cleanup_index + 1

		index = 0
		for value in sensor_values:
			#print("SYSTEMVITALES:", value)
			SYSTEMVITALES[index][0] = float(value)					
			SYSTEMVITALES[index][6] = timestamp
			SYSTEMVITALES[index][7] = PLARS.GPS_DATA[0]
			SYSTEMVITALES[index][8] = PLARS.GPS_DATA[1]
			#print("MATRIX", SYSTEMVITALES[index])
			fragdata.append(SYSTEMVITALES[index])		
			# creates a new dataframe to add new data 	
			newdata = pd.DataFrame(fragdata, columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude'])
			BUFFER_GLOBAL = pd.concat([BUFFER_GLOBAL,newdata]).drop_duplicates().reset_index(drop=True)
			#BUFFER_GLOBAL = pd.concat([BUFFER_GLOBAL,newdata]).reset_index(drop=True)										
			# we get len of one sensor
			#print("dsc", SYSTEMVITALES[index][3])
			currentsize_persensor = len(BUFFER_GLOBAL[BUFFER_GLOBAL["dsc"] == SYSTEMVITALES[index][3]])
			if currentsize_persensor > targetsize:
				trimmbuffer_flag = True		
			index = index + 1	
			
	elif method.routing_key == 'generators':
	    # decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")		
		index = 0
		for value in sensor_values:
			#print("GENERATORS:", float(value))
			GENERATORS[index][0] = float(value)					
			GENERATORS[index][6] = timestamp
			GENERATORS[index][7] = PLARS.GPS_DATA[0]
			GENERATORS[index][8] = PLARS.GPS_DATA[1]
			#print("MATRIX", GENERATORS[index])
			fragdata.append(GENERATORS[index])		
			# creates a new dataframe to add new data 	
			newdata = pd.DataFrame(fragdata, columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude'])
			BUFFER_GLOBAL = pd.concat([BUFFER_GLOBAL,newdata]).drop_duplicates().reset_index(drop=True)
			#BUFFER_GLOBAL = pd.concat([BUFFER_GLOBAL,newdata]).reset_index(drop=True)	
			# we get len of one sensor
			currentsize_persensor = len(BUFFER_GLOBAL[BUFFER_GLOBAL["dsc"] == GENERATORS[index][3]])
			if currentsize_persensor > targetsize:
				trimmbuffer_flag = True	
			index = index + 1	
				
	elif method.routing_key == 'sensehat':
	    # decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")		
		index = 0
		for value in sensor_values:
			#print("SENSEHAT:", float(value))
			SENSEHAT[index][0] = float(value)					
			SENSEHAT[index][6] = timestamp
			SENSEHAT[index][7] = PLARS.GPS_DATA[0]
			SENSEHAT[index][8] = PLARS.GPS_DATA[1]
			#print("MATRIX", SENSEHAT[index])
			fragdata.append(SENSEHAT[index])		
			# creates a new dataframe to add new data 	
			newdata = pd.DataFrame(fragdata, columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude'])
			BUFFER_GLOBAL = pd.concat([BUFFER_GLOBAL,newdata]).drop_duplicates().reset_index(drop=True)
			#BUFFER_GLOBAL = pd.concat([BUFFER_GLOBAL,newdata]).reset_index(drop=True)
			# we get len of one sensor
			currentsize_persensor = len(BUFFER_GLOBAL[BUFFER_GLOBAL["dsc"] == GENERATORS[index][3]])
			if currentsize_persensor > targetsize:
				trimmbuffer_flag = True		
			index = index + 1	
			
						
	elif method.routing_key == 'envirophat':
	    # decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")		
		index = 0

	elif method.routing_key == 'pocket_geiger':
	    # decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")		
		index = 0
		
	elif method.routing_key == 'ir_thermo':
	    # decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")		
		index = 0
	
	elif method.routing_key == 'thermal_frame':
	    # decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")		
		index = 0

	# PD Fails to handel over 1650 rows so we trim the buffer when 64 rows on any sensor gets reached
	if trimmbuffer_flag:
			BUFFER_GLOBAL = trimbuffer(targetsize)


# return a list of n most recent data from specific sensor defined by keys
# gets Called from pilgraph
def get_recent(dsc, dev, num, timeing):	
	# Filters the pd Dataframe to a Device like dsc="Thermometer" 
	
	#print("Sensor_count:",configure.max_sensors[0])
	
	currentsize = len(BUFFER_GLOBAL)
	
	#print("currentsize ",currentsize )
	
	result = BUFFER_GLOBAL[BUFFER_GLOBAL["dsc"] == dsc]
	#print("result")
	#print(result)
	
	#print("Buffer")
	#print(BUFFER_GLOBAL[BUFFER_GLOBAL["dsc"] == 'CpuTemp')
	#print(BUFFER_GLOBAL)
	
	untrimmed_data = result.loc[result['dev'] == dev]

	# trim it to length (num).
	trimmed_data = untrimmed_data.tail(num)


	# return a list of the values
	data_line = trimmed_data['value'].tolist()		
	times = trimmed_data['timestamp'].tolist()


	timelength = num

	return data_line, timelength


def get_em(dev,frequency):
	result = buffer_em.loc[buffer_em['dev'] == dev]
	result2 = result.loc[result["frequency"] == frequency]

	return result2

# returns all sensor data in the buffer for the specific sensor (dsc,dev)
def get_sensor(dsc,dev):

	result = BUFFER_GLOBAL[BUFFER_GLOBAL["dsc"] == dsc]

	result2 = result.loc[result['dev'] == dev]

	return result2


def index_by_time(df, ascending = False):
	df.sort_values(by=['timestamp'], ascending = ascending)
	return df


# return a list of n most recent data from specific ssid defined by keys
def get_recent_em( dev, frequency, num = 5):

	# get a dataframe of just the requested sensor
	untrimmed_data = get_em(dev,frequency)

	# trim it to length (num).
	trimmed_data = untrimmed_data.tail(num)

	# return a list of the values
	return trimmed_data['signal'].tolist()

def trim_em_buffer( targetsize):
	# should take the buffer in memory and trim some of it

	# get buffer size to determine how many rows to remove from the end
	currentsize = len(buffer_em)

	# determine difference between buffer and target size
	length = currentsize - targetsize

	# make a new dataframe of the most recent data to keep using
	newbuffer = buffer_em.tail(targetsize)

	# slice off the rows outside the buffer and backup to disk
	tocore = buffer_em.head(length)

	if configure.datalog[0]:
			append_to_em_core(tocore)

	# replace existing buffer with new trimmed buffer
	return newbuffer

def trimbuffer( targetsize):
	# should take the buffer in memory and trim some of it
	targetsize_all_sensors = targetsize * configure.max_sensors[0]

	# get buffer size to determine how many rows to remove from the end
	currentsize = len(BUFFER_GLOBAL) 

	# determine difference between buffer and target size
	length = currentsize - targetsize_all_sensors

	# make a new dataframe of the most recent data to keep using
	newbuffer = BUFFER_GLOBAL.tail(targetsize_all_sensors)

	# slice off the rows outside the buffer and backup to disk
	tocore = BUFFER_GLOBAL.head(length)

	if configure.datalog[0]:
			append_to_core(tocore)


	# replace existing buffer with new trimmed buffer
	return newbuffer


def emrg():
	get_core()
	return df

def convert_epoch( time):
	return datetime.datetime.fromtimestamp(time)
	
def response_check():
	return True
	
# updates the dataframe in memory with the most recent sensor values from each
# initialized sensor.
# Sensor data is taken in as Fragment() instance objects. Each one contains
# the sensor value and context for it (scale, symbol, unit, etc).
def callback_rabbitmq(ch, method, properties, body):
	update(ch, method, properties, body)
	
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

