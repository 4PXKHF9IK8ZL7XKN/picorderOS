#!/usr/bin/env python
import pika
import sys
from objects import *
from picosglobals import *

import psycopg2
from picos_psql_config import load_config

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
    exchange='sensor_data', queue='', routing_key='bme680')

channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='scd4x')

channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='GPS_DATA')

channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='sensehat_joystick')

channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='sensehat')

channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='keyboard')

def table_list(con):
	ret = []
	try:
		cur = con.cursor()
		cur.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")
		for table in cur.fetchall():
			table_unclean = str(table).strip("( ),")
			table_unclean = table_unclean[:-1]
			item = table_unclean[1:]
			ret.append(item)
		cur.close()
	except psycopg2.Error as e:
		print( e )
	return ret


def table_exists(con, table_str):
	exists = False
	try:
		array_of_tables = table_list(con)
		if table_str in array_of_tables:
			exists = True
	except psycopg2.Error as e:
		print( e )
	return exists

def table_create(con, table_str):

    ret = False
    try:
        cur = con.cursor()
        cur.execute('CREATE TABLE "' + table_str + '" (id serial PRIMARY KEY, value real,timestamp numeric,latitude bigint,longitude bigint);')
        ret = table_exists(con, table_str)
        if ret is True:
        	print("TABLE: ", table_str ,"CREATED")
        cur.close()
    except psycopg2.Error as e:
        print( e )
    return ret  

def table_drop(con, table_str):

    ret = False
    try:
        cur = con.cursor()
        cur.execute('DROP TABLE "' + table_str + '" ;')
        ret_check = table_exists(con, table_str)
        if ret_check is False:
        	ret = True
        	print("TABLE: ", table_str ,"DROPED")
        cur.close()
    except psycopg2.Error as e:
        print( e )
    return ret  

def get_table_col_names(con, table_str):

    col_names = []
    try:
        cur = con.cursor()
        cur.execute('select * from "' + table_str + '" LIMIT 0')
        for desc in cur.description:
            col_names.append(desc[0])        
        cur.close()
    except psycopg2.Error as e:
        print( e )

    return col_names

def empty_tablecheck(con, table_str):
	ret = False
	try:
		cur = con.cursor()
		lengh = len(cur.fetchall())
		cur.close()
	except psycopg2.Error as e:
		if e == "no results to fetch":
			ret = True
	return ret




def insert_data(con, table_str, value, stamp, lat, lon, tag):
	print("DEBUG:",table_str, value, stamp, lat, lon, tag)
	check_table = empty_tablecheck(con, table_str)
	ret = False
	prep_tag = f'"{tag}"'
	print(prep_tag)
	try:
		cur = con.cursor()
		print("DEBUG:", check_table)
		if check_table == True:
			print("DEBUG: DO WE FETCHE HERE?")
			lengh = len(cur.fetchall())
		cur.execute('INSERT INTO "' + table_str + '" (value, timestamp, latitude, longitude) VALUES ( '+ str(value) + ' , ' +  str(stamp) + ' , ' + str(lat) + ' , ' + str(lon) + ');')     
		# i know its crude, i may should read data with now known index
		#if check_table == True:
		ret = True          	
		#else:
			#lengh2 = len(cur.fetchall())
			#if lengh2 == lengh + 1:
			#ret = True        
		cur.close()
	except psycopg2.Error as e:
		print( e , "error und so")
	return ret
    

   
    
    
def connect_psql(config):
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error) 
        
def callback(ch, method, properties, body):

	print(f" [x] {method.routing_key}:{body}")
        
	#global #BUFFER_GLOBAL
	#global #BUFFER_GLOBAL_TERMALFRAME
	global GPS_DATA
	global BME680
	global SYSTEMVITALES
	global GENERATORS
	global SENSEHAT
	global TERMALFRAME
	global selected_sensor_values
	
	timestamp = time.time()
	fragdata = []
	fragdata_termal = []
	sensor_values = []
	trimmbuffer_flag = False
	trimmbuffer_flag_termal = False
	
		
	# configure buffersize
	if configure.buffer_size[0] == 0:
		targetsize = 128
	else:
		targetsize = configure.buffer_size[0]
		
	 
	if method.routing_key == 'GPS_DATA':
		# needs maybe refiment later, this can be mixed local and remote
		GPS_DATA[0],GPS_DATA[1],GPS_DATA[2]  = body.decode().strip("[]").split(",")	
	
	 	
	elif method.routing_key == 'bme680':	
		# decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")
		origin_tag = sensor_values[-1:]
		del sensor_values[-1]	
		index = 0
		for value in sensor_values:
			#print("BME680:", float(value))
			BME680[index][0] = float(value)					
			BME680[index][6] = timestamp
			BME680[index][7] = GPS_DATA[0]
			BME680[index][8] = GPS_DATA[1]
			BME680[index][9] = origin_tag[0].strip("' '")
			#print("MATRIX", BME680[index])
			fragdata.append(BME680[index])		
			# creates a new dataframe to add new data
			table_string = '%s_%s_%s' % (BME680[index][9],BME680[index][5],BME680[index][3])
			ret = table_exists(psql_connection, table_string)
			if ret is False:
				table_create(psql_connection,  table_string)
			array = get_table_col_names(psql_connection,  table_string)
			print(BME680[index][3],array)
			
			#table_drop(psql_connection, table_string)
			
			ret = insert_data(psql_connection,  table_string, BME680[index][0], BME680[index][6], BME680[index][7], BME680[index][8],BME680[index][9])
			print("writing?", ret )
				
			#newdata = pd.DataFrame(fragdata, columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude','rabbitmq_tag'])
			#BUFFER_GLOBAL = pd.concat([#BUFFER_GLOBAL,#newdata]).drop_duplicates().reset_index(drop=True)
			##BUFFER_GLOBAL = pd.concat([#BUFFER_GLOBAL,#newdata]).reset_index(drop=True)	
			# we get len of one sensor
			#currentsize_persensor = len(#BUFFER_GLOBAL[#BUFFER_GLOBAL["dsc"] == BME680[index][3]])
			#if currentsize_persensor > targetsize * 5:
			#	trimmbuffer_flag = True		
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
			elif cleanup_index == 16:
				 origin_tag = value4555.strip("' '")
			cleanup_index = cleanup_index + 1

		index = 0
		for value in sensor_values:
			#print("SYSTEMVITALES:", value)
			SYSTEMVITALES[index][0] = float(value)					
			SYSTEMVITALES[index][6] = timestamp
			SYSTEMVITALES[index][7] = GPS_DATA[0]
			SYSTEMVITALES[index][8] = GPS_DATA[1]
			SYSTEMVITALES[index][9] = origin_tag
			#print("MATRIX", SYSTEMVITALES[index])
			fragdata.append(SYSTEMVITALES[index])		
			# creates a new dataframe to add new data 	
			#newdata = pd.DataFrame(fragdata, columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude','rabbitmq_tag'])
			#BUFFER_GLOBAL = pd.concat([#BUFFER_GLOBAL,#newdata]).drop_duplicates().reset_index(drop=True)
			##BUFFER_GLOBAL = pd.concat([#BUFFER_GLOBAL,#newdata]).reset_index(drop=True)										
			# we get len of one sensor
			#print("dsc", SYSTEMVITALES[index][3])
			#currentsize_persensor = len(#BUFFER_GLOBAL[#BUFFER_GLOBAL["dsc"] == SYSTEMVITALES[index][3]])
			#if currentsize_persensor > targetsize * 12:
			#	trimmbuffer_flag = True		
			#index = index + 1	
	
	 		
	elif method.routing_key == 'generators':
	    # decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")
		origin_tag = sensor_values[-1:]	
		del sensor_values[-1]	
		index = 0
		for value in sensor_values:
			#print("GENERATORS:", float(value))
			GENERATORS[index][0] = float(value)					
			GENERATORS[index][6] = timestamp
			GENERATORS[index][7] = GPS_DATA[0]
			GENERATORS[index][8] = GPS_DATA[1]
			GENERATORS[index][9] = origin_tag[0].strip("' '")
			#print("MATRIX", GENERATORS[index])
			fragdata.append(GENERATORS[index])		
			# creates a new dataframe to add new data 	
			#newdata = pd.DataFrame(fragdata, columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude','rabbitmq_tag'])
			#BUFFER_GLOBAL = pd.concat([#BUFFER_GLOBAL,#newdata]).drop_duplicates().reset_index(drop=True)
			##BUFFER_GLOBAL = pd.concat([#BUFFER_GLOBAL,#newdata]).reset_index(drop=True)	
			# we get len of one sensor
			#currentsize_persensor = len(#BUFFER_GLOBAL[#BUFFER_GLOBAL["dsc"] == GENERATORS[index][3]])
			#if currentsize_persensor > targetsize * 4:
			#	trimmbuffer_flag = True	
			#index = index + 1	
	
	 			
	elif method.routing_key == 'sensehat':
	    # decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")
		origin_tag = sensor_values[-1:]	
		del sensor_values[-1]		
		index = 0
		for value in sensor_values:
			#print("SENSEHAT:", float(value))
			SENSEHAT[index][0] = float(value)					
			SENSEHAT[index][6] = timestamp
			SENSEHAT[index][7] = GPS_DATA[0]
			SENSEHAT[index][8] = GPS_DATA[1]
			SENSEHAT[index][9] = origin_tag[0].strip("' '")
			#print("MATRIX", SENSEHAT[index])
			fragdata.append(SENSEHAT[index])		
			# creates a new dataframe to add new data 	
			#newdata = pd.DataFrame(fragdata, columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude','rabbitmq_tag'])
			#BUFFER_GLOBAL = pd.concat([#BUFFER_GLOBAL,#newdata]).drop_duplicates().reset_index(drop=True)
			##BUFFER_GLOBAL = pd.concat([#BUFFER_GLOBAL,#newdata]).reset_index(drop=True)
			# we get len of one sensor
			#currentsize_persensor = len(#BUFFER_GLOBAL[#BUFFER_GLOBAL["dsc"] == SENSEHAT[index][3]])
			#if currentsize_persensor > targetsize * 9:
			#	trimmbuffer_flag = True		
			#index = index + 1
	
	 		
	elif method.routing_key == 'apds9960':
		# decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip(" () ").split(",")	
		origin_tag = sensor_values[-1:]	
		del sensor_values[-1]			
		index = 0	
		for value in sensor_values:
			#print("APDS9960:", float(value))
			APDS9960[index][0] = int(value)					
			APDS9960[index][6] = timestamp
			APDS9960[index][7] = GPS_DATA[0]
			APDS9960[index][8] = GPS_DATA[1]
			APDS9960[index][9] = origin_tag[0].strip("' '")
			#print("MATRIX", APDS9960[index])
			fragdata.append(APDS9960[index])		
			# creates a new dataframe to add new data 	
			#newdata = pd.DataFrame(fragdata, columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude','rabbitmq_tag'])
			#BUFFER_GLOBAL = pd.concat([#BUFFER_GLOBAL,#newdata]).drop_duplicates().reset_index(drop=True)
			##BUFFER_GLOBAL = pd.concat([#BUFFER_GLOBAL,#newdata]).reset_index(drop=True)
			# we get len of one sensor
			#currentsize_persensor = len(#BUFFER_GLOBAL[#BUFFER_GLOBAL["dsc"] == APDS9960[index][3]])
			#if currentsize_persensor > targetsize * 6:
			#	trimmbuffer_flag = True		
			#index = index + 1
		
	
	 		
	elif method.routing_key == 'lis3mdl':
		# decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")	
		origin_tag = sensor_values[-1:]	
		del sensor_values[-1]		
		index = 0			
		for value in sensor_values:
			#print("LIS3MDL:", float(value))
			LIS3MDL[index][0] = float(value)					
			LIS3MDL[index][6] = timestamp
			LIS3MDL[index][7] = GPS_DATA[0]
			LIS3MDL[index][8] = GPS_DATA[1]
			LIS3MDL[index][9] = origin_tag[0].strip("' '")
			#print("MATRIX", LIS3MDL[index])
			fragdata.append(LIS3MDL[index])		
			# creates a new dataframe to add new data 	
			#newdata = pd.DataFrame(fragdata, columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude','rabbitmq_tag'])
			#BUFFER_GLOBAL = pd.concat([#BUFFER_GLOBAL,#newdata]).drop_duplicates().reset_index(drop=True)
			##BUFFER_GLOBAL = pd.concat([#BUFFER_GLOBAL,#newdata]).reset_index(drop=True)
			# we get len of one sensor
			#currentsize_persensor = len(#BUFFER_GLOBAL[#BUFFER_GLOBAL["dsc"] == LIS3MDL[index][3]])
			#if currentsize_persensor > targetsize * 3:
			#	trimmbuffer_flag = True		
			#index = index + 1			

	 
	elif method.routing_key == 'lsm6ds3':
		# decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")
		origin_tag = sensor_values[-1:]	
		del sensor_values[-1]			
		index = 0	
		for value in sensor_values:
			#print("LSM6DS3:", float(value))
			LSM6DS3[index][0] = float(value)					
			LSM6DS3[index][6] = timestamp
			LSM6DS3[index][7] = GPS_DATA[0]
			LSM6DS3[index][8] = GPS_DATA[1]
			LSM6DS3[index][9] = origin_tag[0].strip("' '")
			#print("MATRIX", LSM6DS3[index])
			fragdata.append(LSM6DS3[index])		
			# creates a new dataframe to add new data 	
			#newdata = pd.DataFrame(fragdata, columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude','rabbitmq_tag'])
			#BUFFER_GLOBAL = pd.concat([#BUFFER_GLOBAL,#newdata]).drop_duplicates().reset_index(drop=True)
			##BUFFER_GLOBAL = pd.concat([#BUFFER_GLOBAL,#newdata]).reset_index(drop=True)
			# we get len of one sensor
			#currentsize_persensor = len(#BUFFER_GLOBAL[#BUFFER_GLOBAL["dsc"] == LSM6DS3[index][3]])
			#if currentsize_persensor > targetsize * 6:
			#	trimmbuffer_flag = True		
			#index = index + 1	
		
	 
	elif method.routing_key == 'scd4x':
		# decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")
		origin_tag = sensor_values[-1:]	
		del sensor_values[-1]	
		index = 0
		for value in sensor_values:
			#print("SCD4X:", float(value))
			SCD4X[index][0] = float(value)					
			SCD4X[index][6] = timestamp
			SCD4X[index][7] = GPS_DATA[0]
			SCD4X[index][8] = GPS_DATA[1]
			SCD4X[index][9] = origin_tag[0].strip("' '")
			#print("MATRIX", SCD4X[index])
			fragdata.append(SCD4X[index])		
			# creates a new dataframe to add new data 	
			#newdata = pd.DataFrame(fragdata, columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude','rabbitmq_tag'])
			#BUFFER_GLOBAL = pd.concat([#BUFFER_GLOBAL,#newdata]).drop_duplicates().reset_index(drop=True)
			##BUFFER_GLOBAL = pd.concat([#BUFFER_GLOBAL,#newdata]).reset_index(drop=True)
			# we get len of one sensor
			#currentsize_persensor = len(#BUFFER_GLOBAL[#BUFFER_GLOBAL["dsc"] == SCD4X[index][3]])
			#if currentsize_persensor > targetsize * 3:
			#	trimmbuffer_flag = True		
			#index = index + 1			
		
	 
	elif method.routing_key == 'sht30':
		# decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")
		origin_tag = sensor_values[-1:]
		del sensor_values[-1]			
		index = 0		
		for value in sensor_values:
			#print("SHT30:", float(value))
			SHT30[index][0] = float(value)					
			SHT30[index][6] = timestamp
			SHT30[index][7] = GPS_DATA[0]
			SHT30[index][8] = GPS_DATA[1]
			SHT30[index][9] = origin_tag[0].strip("' '")
			#print("SHT30", SHT30[index])
			fragdata.append(SHT30[index])		
			# creates a new dataframe to add new data 	
			#newdata = pd.DataFrame(fragdata, columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude','rabbitmq_tag'])
			#BUFFER_GLOBAL = pd.concat([#BUFFER_GLOBAL,#newdata]).drop_duplicates().reset_index(drop=True)
			##BUFFER_GLOBAL = pd.concat([#BUFFER_GLOBAL,#newdata]).reset_index(drop=True)
			# we get len of one sensor
			#currentsize_persensor = len(#BUFFER_GLOBAL[#BUFFER_GLOBAL["dsc"] == SHT30[index][3]])
			#if currentsize_persensor > targetsize * 3:
			#	trimmbuffer_flag = True		
			#index = index + 1
	
	 
	elif method.routing_key == 'bmp280':
		# decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")	
		origin_tag = sensor_values[-1:]
		del sensor_values[-1]		
		index = 0	
		for value in sensor_values:
			#print("BMP280:", float(value))
			BMP280[index][0] = float(value)					
			BMP280[index][6] = timestamp
			BMP280[index][7] = GPS_DATA[0]
			BMP280[index][8] = GPS_DATA[1]
			BMP280[index][9] = origin_tag[0].strip("' '")
			#print("MATRIX", BMP280[index])
			fragdata.append(BMP280[index])		
			# creates a new dataframe to add new data 	
			#newdata = pd.DataFrame(fragdata, columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude','rabbitmq_tag'])
			#BUFFER_GLOBAL = pd.concat([#BUFFER_GLOBAL,#newdata]).drop_duplicates().reset_index(drop=True)
			##BUFFER_GLOBAL = pd.concat([#BUFFER_GLOBAL,#newdata]).reset_index(drop=True)	
			# we get len of one sensor
			#currentsize_persensor = len(#BUFFER_GLOBAL[#BUFFER_GLOBAL["dsc"] == BMP280[index][3]])
			#if currentsize_persensor > targetsize * 3:
			#	trimmbuffer_flag = True		
			#index = index + 1	
	
	 
	elif method.routing_key == 'thermal_frame':
	    # decodes data byte stream and splits the values by comma
		sensor_values = body.decode()
		sensor_frame = ast.literal_eval(sensor_values)	
		origin_tag = sensor_frame[1]
		#print("TERMALFRAME:", sensor_frame)
		#print("TERMALFRAME:", sensor_frame[1])
		index = 0
		
		for sensor_array_line in sensor_frame[0]:
			for datapoint in sensor_array_line:
				TERMALFRAME[index] = float(datapoint)
				index = index + 1
	
		TERMALFRAME[64] = timestamp
		TERMALFRAME[65] = GPS_DATA[0]
		TERMALFRAME[66] = GPS_DATA[1]
		TERMALFRAME[67] = origin_tag

		#print("MATRIX", TERMALFRAME)
		fragdata_termal.append(TERMALFRAME)		
		# creates a new dataframe to add new data 	
		#newdata = pd.DataFrame(fragdata_termal, columns=['Value0','Value1','Value2','Value3','Value4','Value5','Value6','Value7','Value8','Value9','Value10','Value11','Value12','Value13','Value14','Value15','Value16','Value17','Value18','Value19','Value20','Value21','Value22','Value23','Value24','Value25','Value26','Value27','Value28','Value29','Value30','Value31','Value32','Value33','Value34','Value35','Value36','Value37','Value38','Value39','Value40','Value41','Value42','Value43','Value44','Value45','Value46','Value47','Value48','Value49','Value50','Value51','Value52','Value53','Value54','Value55','Value56','Value57','Value58','Value59','Value60','Value61','Value62','Value63','timestamp','latitude','longitude','rabbitmq_tag'])
		#BUFFER_GLOBAL_TERMALFRAME = pd.concat([#BUFFER_GLOBAL_TERMALFRAME,#newdata]).drop_duplicates().reset_index(drop=True)
		# we get len of one sensor					
		#currentsize_termalframe = len(#BUFFER_GLOBAL_TERMALFRAME)
		#if currentsize_termalframe > 10:
		#	trimmbuffer_flag_termal = True		


	# PD Fails to handel over 1650 rows so we trim the buffer when 64 rows on any sensor gets reached
	#if trimmbuffer_flag:
			#BUFFER_GLOBAL = trimbuffer(targetsize,'global')
			
	#if trimmbuffer_flag_termal:
			#BUFFER_GLOBAL_TERMALFRAME = trimbuffer(targetsize,'termal')		
			
	return


def trimbuffer(targetsize,buffername):
	# should take the buffer in memory and trim some of it
	#if buffername == 'global':
		# we need to address that each sensor has sub value too
		#targetsize_all_sensors = targetsize * (configure.max_sensors[0] * 2)
	#elif buffername == 'termal':
		#targetsize_all_sensors = targetsize * 1
		
	#print("buffername:", buffername)
	
	#print("Sensors",configure.max_sensors[0])
	
	#print("Target Size",targetsize )
	
	#print("targetsize_all_sensors ",targetsize_all_sensors )
	
	# get buffer size to determine how many rows to remove from the end
	#if buffername == 'global':
		#currentsize = len(#BUFFER_GLOBAL) 
	#elif buffername == 'termal':
		#currentsize = len(#BUFFER_GLOBAL_TERMALFRAME) 
	#print("currentsize", currentsize)

	# determine difference between buffer and target size
	length = currentsize - targetsize_all_sensors
	
	#print("length", length)


	# make a new dataframe of the most recent data to keep using
	#if buffername == 'global':
		#newbuffer = #BUFFER_GLOBAL.tail(targetsize_all_sensors)
	#elif buffername == 'termal':
		#newbuffer = #BUFFER_GLOBAL_TERMALFRAME.tail(targetsize_all_sensors)
	newbuffer = 0

	# slice off the rows outside the buffer and backup to disk
	#if buffername == 'global':
		#tocore = #BUFFER_GLOBAL.head(length)
	#elif buffername == 'termal':
		#tocore_termal = #BUFFER_GLOBAL_TERMALFRAME.head(length)

	#if buffername == 'global':
		#if configure.datalog[0]:
				#append_to_core(tocore)
	#elif buffername == 'termal':
		#if configure.datalog[0]:
				#append_to_core(tocore_termal)

	# replace existing buffer with new trimmed buffer
	return newbuffer  
  
  
  
  
  
  
  
  
  
    
# Prepare connection to PSQL
config = load_config()
psql_connection = connect_psql(config)
psql_connection.autocommit = True

print(' [*] Waiting for logs. To exit press CTRL+C')


if __name__ == "__main__":
	channel.basic_consume(queue='',on_message_callback=callback, auto_ack=True)
	try:	
		channel.start_consuming()
	except KeyboardInterrupt:
		pass






