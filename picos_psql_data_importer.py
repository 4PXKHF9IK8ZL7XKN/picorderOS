#!/usr/bin/env python
import pika
import sys
import ast
import os
from objects import *
from picosglobals import *

keep_data_lengh = 300 # 5 min
keep_data_lengh_gps = 259200 # keep it 3 days 

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
    exchange='sensor_data', queue='', routing_key='bmp280')
    
channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='sht30')
 
channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='scd4x')
    
channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='lsm6ds3')

channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='lis3mdl')

channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='apds9960')

channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='GPS_DATA')

channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='sensehat')

channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='thermal_frame')
    
channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='system_vitals')
   
channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='generators')


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
		cur.execute('CREATE TABLE "' + table_str + '" (id serial PRIMARY KEY, value real,timestamp numeric,latitude numeric,longitude numeric);')
		ret = table_exists(con, table_str)
		if ret is True:
			print("TABLE: ", table_str ,"CREATED")
		cur.close()
	except psycopg2.Error as e:
		print( e )
	return ret  
    
def table_create_gps(con, table_str):

    ret = False
    try:
        cur = con.cursor()
        cur.execute('CREATE TABLE "' + table_str + '" (id serial PRIMARY KEY, speed real, altitude real, track real, sats real, timestamp numeric,latitude numeric ,longitude numeric);')
        ret = table_exists(con, table_str)
        if ret is True:
        	print("TABLE: ", table_str ,"CREATED")
        cur.close()
    except psycopg2.Error as e:
        print( e )
    return ret  
    
def table_create_termalframe(con, table_str):

    ret = False
    try:
        cur = con.cursor()
        cur.execute('CREATE TABLE "' + table_str + '" (id serial PRIMARY KEY, val0 real, val1 real, val2 real, val3 real, val4 real, val5 real, val6 real, val7 real, val8 real, val9 real, val10 real, val11 real, val12 real, val13 real, val14 real, val15 real, val16 real, val17 real, val18 real, val19 real, val20 real, val21 real, val22 real, val23 real, val24 real, val25 real, val26 real, val27 real, val28 real, val29 real, val30 real, val31 real, val32 real, val33 real, val34 real, val35 real, val36 real, val37 real, val38 real, val39 real, val40 real, val41 real, val42 real, val43 real, val44 real, val45 real, val46 real, val47 real, val48 real, val49 real, val50 real, val51 real, val52 real, val53 real, val54 real, val55 real, val56 real, val57 real, val58 real, val59 real, val60 real, val61 real, val62 real, val63 real, timestamp numeric,latitude numeric ,longitude numeric);')
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
		cur.execute('select * from "' + table_str + '" LIMIT 0')
		lengh = len(cur.fetchall())
		cur.close()
	except psycopg2.Error as e:
		if e == "no results to fetch":
			ret = True
	return ret
	
	
def return_lengh(con, table_str):
	ret = False
	try:
		cur = con.cursor()
		cur.execute('select * from "' + table_str + '" ')
		lengh = len(cur.fetchall())
		ret = lengh
		cur.close()
	except psycopg2.Error as e:
		if e == "no results to fetch":
			print( e )
	return ret


def purge_data_totime(con, table_str, time_lengh_sec):
	# time is the lengh in the past from wehe the purge goes on to start , to keep the newest data
	ret = False
	check_table = empty_tablecheck(con, table_str)
	now_time = time.time()
	time_past = now_time - time_lengh_sec 
	
	try:
		cur = con.cursor()
		if check_table == False:
			cur.execute('delete from "' + table_str + '" where timestamp < ' + str(time_past) + ' RETURNING *')
			removed_items = len(cur.fetchall())
			ret = removed_items
		cur.close()
	except psycopg2.Error as e:
		if e == "no results to fetch":
			print( e )
	return ret


def insert_data(con, table_str, value, stamp, lat, lon, tag):
	#print("DEBUG:",table_str, value, stamp, lat, lon, tag)
	check_table = empty_tablecheck(con, table_str)
	ret = False
	try:
		cur = con.cursor()
		cur.execute('INSERT INTO "' + table_str + '" (value, timestamp, latitude, longitude) VALUES ( '+ str(value) + ' , ' +  str(stamp) + ' , ' + str(lat) + ' , ' + str(lon) + ') RETURNING id;')
		getback = cur.fetchall()
		if len(getback) != 0:
			# did unpacking the Tuple 
			ret_id = int(str(getback[0]).strip('(, )'))
			ret = True
		cur.close()
	except psycopg2.Error as e:
		print( e )
	return ret, ret_id
    
def insert_data_gps(con, table_str, speed, altitude, track, sats, stamp, lat, lon, tag):
	#print("DEBUG:",table_str, speed, altitude, track, sats, stamp, lat, lon, tag)
	check_table = empty_tablecheck(con, table_str)
	ret = False
	try:
		cur = con.cursor()
		cur.execute('INSERT INTO "' + table_str + '" (speed, altitude, track, sats, timestamp, latitude, longitude) VALUES ( '+ str(speed) + ' , ' + str(altitude) + ' , ' + str(track) + ' , ' + str(sats) + ' , ' +  str(stamp) + ' , ' + str(lat) + ' , ' + str(lon) + ') RETURNING id;')
		getback = cur.fetchall()
		if len(getback) != 0:
			# did unpacking the Tuple 
			ret_id = int(str(getback[0]).strip('(, )'))
			ret = True	 
		cur.close()
	except psycopg2.Error as e:
		print( e )
	return ret, ret_id 
 
def insert_data_termal(con, table_str, val0, val1, val2, val3, val4, val5, val6, val7, val8, val9, val10, val11, val12, val13, val14, val15, val16, val17, val18, val19, val20, val21, val22, val23, val24, val25, val26, val27, val28, val29, val30, val31, val32, val33, val34, val35, val36, val37, val38, val39, val40, val41, val42, val43, val44, val45, val46, val47, val48, val49, val50, val51, val52, val53, val54, val55, val56, val57, val58, val59, val60, val61, val62, val63, stamp, lat, lon, tag):
	#print("DEBUG:",table_str, val0, val1, val2, val3, val4, val5, val6, val7, val8, val9, val10, val11, val12, val13, val14, val15, val16, val17, val18, val19, val20, val21, val22, val23, val24, val25, val26, val27, val28, val29, val30, val31, val32, val33, val34, val35, val36, val37, val38, val39, val40, val41, val42, val43, val44, val45, val46, val47, val48, val49, val50, val51, val52, val53, val54, val55, val56, val57, val58, val59, val60, val61, val62, val63, stamp, lat, lon, tag)
	check_table = empty_tablecheck(con, table_str)
	ret = False
	ret_id = "Test"
	try:
		cur = con.cursor()
		cur.execute('INSERT INTO "' + table_str + '" (val0, val1, val2, val3, val4, val5, val6, val7, val8, val9, val10, val11, val12, val13, val14, val15, val16, val17, val18, val19, val20, val21, val22, val23, val24, val25, val26, val27, val28, val29, val30, val31, val32, val33, val34, val35, val36, val37, val38, val39, val40, val41, val42, val43, val44, val45, val46, val47, val48, val49, val50, val51, val52, val53, val54, val55, val56, val57, val58, val59, val60, val61, val62, val63, timestamp, latitude, longitude) VALUES ( '+ str(val0) + ' , ' + str(val1) + ' , ' + str(val2) + ' , ' + str(val3) + ' , ' + str(val4) + ' , ' + str(val5) + ' , ' + str(val6) + ' , ' + str(val7) + ' , ' + str(val8) + ' , ' + str(val9) + ' , ' + str(val10) + ' , ' + str(val11) + ' , ' + str(val12) + ' , ' + str(val13) + ' , ' + str(val14) + ' , ' + str(val15) + ' , ' + str(val16) + ' , ' + str(val17) + ' , ' + str(val18) + ' , ' + str(val19) + ' , ' + str(val20) + ' , ' + str(val21) + ' , ' + str(val22) + ' , ' + str(val23) + ' , ' + str(val24) + ' , ' + str(val25) + ' , ' + str(val26) + ' , ' + str(val27) + ' , ' + str(val28) + ' , ' + str(val29) + ' , ' + str(val30) + ' , ' + str(val31) + ' , ' + str(val32) + ' , ' + str(val33) + ' , ' + str(val34) + ' , ' + str(val35) + ' , ' + str(val36) + ' , ' + str(val37) + ' , ' + str(val38) + ' , ' + str(val39) + ' , ' + str(val40) + ' , ' + str(val41) + ' , ' + str(val42) + ' , ' + str(val43) + ' , ' + str(val44) + ' , ' + str(val45) + ' , ' + str(val46) + ' , ' + str(val47) + ' , ' + str(val48) + ' , ' + str(val49) + ' , ' + str(val50) + ' , ' + str(val51) + ' , ' + str(val52) + ' , ' + str(val53) + ' , ' + str(val54) + ' , ' + str(val55) + ' , ' + str(val56) + ' , ' + str(val57) + ' , ' + str(val58) + ' , ' + str(val59) + ' , ' + str(val60) + ' , ' + str(val61) + ' , ' + str(val62) + ' , ' + str(val63) + ' , ' + str(stamp) + ' , ' + str(lat) + ' , ' + str(lon) + ') RETURNING id;')
		getback = cur.fetchall()
		if len(getback) != 0:
			# did unpacking the Tuple 
			ret_id = int(str(getback[0]).strip('(, )'))
			ret = True	 
		cur.close()
	except psycopg2.Error as e:
		print( e )
	return ret, ret_id   
    
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

	#print(f" [x] {method.routing_key}:{body}")

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
		GPS_DATA[0], GPS_DATA[1], GPS_DATA[2], GPS_DATA[3], GPS_DATA[4], GPS_DATA[5], GPS_DATA[6], GPS_DATA[7], GPS_DATA[8], GPS_DATA[9], GPS_DATA[10], GPS_DATA[11], GPS_DATA[12], GPS_DATA[13], GPS_DATA[14], GPS_DATA[15], GPS_DATA[16], GPS_DATA[17], GPS_DATA[18], GPS_DATA[19], GPS_DATA[20] = body.decode().strip("[]").split(",")	
		# creates a new dataframe to add new data
		table_string = '%s_%s_%s' % (str(GPS_DATA[20]).strip("' "),'GPS_DATA','POS')
		ret = table_exists(psql_connection, table_string)
		if ret is False:
			table_create_gps(psql_connection,  table_string)
		ret, ent_id = insert_data_gps(psql_connection,  table_string, GPS_DATA[2], GPS_DATA[3], GPS_DATA[4], GPS_DATA[5], GPS_DATA[19], GPS_DATA[0], GPS_DATA[1], GPS_DATA[20])
		if ret is False:
			os.exit("SQL Write Faild")
		purge_data_totime(psql_connection,  table_string, keep_data_lengh_gps)
	 	
	elif method.routing_key == 'bme680':	
		# decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")
		origin_tag = sensor_values[-1:]
		del sensor_values[-1]		
		longitude = sensor_values[-1:]
		del sensor_values[-1]	
		latitude = sensor_values[-1:]
		del sensor_values[-1]
		sensortimestamp = sensor_values[-1:]
		del sensor_values[-1]
		index = 0
		for value in sensor_values:
			#print("BME680:", float(value))
			BME680[index][0] = float(value)					
			BME680[index][6] = sensortimestamp[0]
			BME680[index][7] = latitude[0]
			BME680[index][8] = longitude[0]
			BME680[index][9] = origin_tag[0].strip("' '")
			#print("MATRIX", BME680[index])
			
			# creates a new dataframe to add new data
			table_string = '%s_%s_%s' % (BME680[index][9],BME680[index][5],BME680[index][3])

			ret = table_exists(psql_connection, table_string)
			if ret is False:
				table_create(psql_connection,  table_string)
			
			ret, ent_id = insert_data(psql_connection,  table_string, BME680[index][0], BME680[index][6], BME680[index][7], BME680[index][8],BME680[index][9])
			if ret is False:
				os.exit("SQL Write Faild")
			
			purge_data_totime(psql_connection,  table_string, keep_data_lengh)
			index = index + 1			

	elif method.routing_key == 'system_vitals':
		sensor_array_unclean = []
		sensor_values = [0,1,2,3,4,5,6,7]
		#decodes data byte stream and splits the values by comma
		sensor_array_unclean = body.decode().strip("()").split(",")		
		origin_tag = sensor_array_unclean[-1:]
		del sensor_array_unclean[-1]				
		longitude = sensor_array_unclean[-1:]
		del sensor_array_unclean[-1]					
		latitude = sensor_array_unclean[-1:]
		del sensor_array_unclean[-1]
		sensortimestamp = sensor_array_unclean[-1:]
		del sensor_array_unclean[-1]
	
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
			SYSTEMVITALES[index][6] = sensortimestamp[0]
			SYSTEMVITALES[index][7] = latitude[0]
			SYSTEMVITALES[index][8] = longitude[0]
			SYSTEMVITALES[index][9] = origin_tag[0].strip("' '")
			#print("MATRIX", SYSTEMVITALES[index])
			
			# creates a new dataframe to add new data
			table_string = '%s_%s_%s' % (SYSTEMVITALES[index][9],SYSTEMVITALES[index][5],SYSTEMVITALES[index][3])

			ret = table_exists(psql_connection, table_string)
			if ret is False:
				table_create(psql_connection,  table_string)
			
			ret, ent_id = insert_data(psql_connection,  table_string, SYSTEMVITALES[index][0], SYSTEMVITALES[index][6], SYSTEMVITALES[index][7], SYSTEMVITALES[index][8], SYSTEMVITALES[index][9])
			if ret is False:
				os.exit("SQL Write Faild")
			
			purge_data_totime(psql_connection,  table_string, keep_data_lengh)		
			
			index = index + 1	
	
	 		
	elif method.routing_key == 'generators':
	    # decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")
		origin_tag = sensor_values[-1:]
		del sensor_values[-1]		
		longitude = sensor_values[-1:]
		del sensor_values[-1]	
		latitude = sensor_values[-1:]
		del sensor_values[-1]
		sensortimestamp = sensor_values[-1:]
		del sensor_values[-1]	
		index = 0
		for value in sensor_values:
			#print("GENERATORS:", float(value))
			GENERATORS[index][0] = float(value)					
			GENERATORS[index][6] = sensortimestamp[0]
			GENERATORS[index][7] = latitude[0]
			GENERATORS[index][8] = longitude[0]
			GENERATORS[index][9] = origin_tag[0].strip("' '")
			#print("MATRIX", GENERATORS[index])
		
			# creates a new dataframe to add new data
			table_string = '%s_%s_%s' % (GENERATORS[index][9],GENERATORS[index][5],GENERATORS[index][3])

			ret = table_exists(psql_connection, table_string)
			if ret is False:
				table_create(psql_connection,  table_string)
			
			ret, ent_id = insert_data(psql_connection,  table_string, GENERATORS[index][0], GENERATORS[index][6], GENERATORS[index][7], GENERATORS[index][8],GENERATORS[index][9])
			if ret is False:
				os.exit("SQL Write Faild")
			
			purge_data_totime(psql_connection,  table_string, keep_data_lengh)
						
			index = index + 1	
	
	 			
	elif method.routing_key == 'sensehat':
	    # decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")
		origin_tag = sensor_values[-1:]
		del sensor_values[-1]		
		longitude = sensor_values[-1:]
		del sensor_values[-1]	
		latitude = sensor_values[-1:]
		del sensor_values[-1]
		sensortimestamp = sensor_values[-1:]
		del sensor_values[-1]	
		index = 0
		for value in sensor_values:
			#print("SENSEHAT:", float(value))
			SENSEHAT[index][0] = float(value)					
			SENSEHAT[index][6] = sensortimestamp[0]
			SENSEHAT[index][7] = latitude[0]
			SENSEHAT[index][8] = longitude[0]
			SENSEHAT[index][9] = origin_tag[0].strip("' '")
			#print("MATRIX", SENSEHAT[index])

			# creates a new dataframe to add new data
			table_string = '%s_%s_%s' % (SENSEHAT[index][9],SENSEHAT[index][5],SENSEHAT[index][3])

			ret = table_exists(psql_connection, table_string)
			if ret is False:
				table_create(psql_connection,  table_string)
			
			ret, ent_id = insert_data(psql_connection,  table_string, SENSEHAT[index][0], SENSEHAT[index][6], SENSEHAT[index][7], SENSEHAT[index][8],SENSEHAT[index][9])
			if ret is False:
				os.exit("SQL Write Faild")
			
			purge_data_totime(psql_connection,  table_string, keep_data_lengh)		
				
			index = index + 1
	
	 		
	elif method.routing_key == 'apds9960':
		# decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip(" () ").split(",")	
		origin_tag = sensor_values[-1:]
		del sensor_values[-1]		
		longitude = sensor_values[-1:]
		del sensor_values[-1]	
		latitude = sensor_values[-1:]
		del sensor_values[-1]
		sensortimestamp = sensor_values[-1:]
		del sensor_values[-1]			
		index = 0	
		for value in sensor_values:
			#print("APDS9960:", float(value))
			APDS9960[index][0] = int(value)					
			APDS9960[index][6] = sensortimestamp[0]
			APDS9960[index][7] = latitude[0]
			APDS9960[index][8] = longitude[0]
			APDS9960[index][9] = origin_tag[0].strip("' '")
			#print("MATRIX", APDS9960[index])
				
			# creates a new dataframe to add new data
			table_string = '%s_%s_%s' % (APDS9960[index][9],APDS9960[index][5],APDS9960[index][3])

			ret = table_exists(psql_connection, table_string)
			if ret is False:
				table_create(psql_connection,  table_string)
			
			ret, ent_id = insert_data(psql_connection,  table_string, APDS9960[index][0], APDS9960[index][6], APDS9960[index][7], APDS9960[index][8],APDS9960[index][9])
			if ret is False:
				os.exit("SQL Write Faild")
			
			purge_data_totime(psql_connection,  table_string, keep_data_lengh)			
			
			index = index + 1
		
	
	 		
	elif method.routing_key == 'lis3mdl':
		# decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")	
		origin_tag = sensor_values[-1:]
		del sensor_values[-1]		
		longitude = sensor_values[-1:]
		del sensor_values[-1]	
		latitude = sensor_values[-1:]
		del sensor_values[-1]
		sensortimestamp = sensor_values[-1:]
		del sensor_values[-1]		
		index = 0			
		for value in sensor_values:
			#print("LIS3MDL:", float(value))
			LIS3MDL[index][0] = float(value)					
			LIS3MDL[index][6] = sensortimestamp[0]
			LIS3MDL[index][7] = latitude[0]
			LIS3MDL[index][8] = longitude[0]
			LIS3MDL[index][9] = origin_tag[0].strip("' '")
			#print("MATRIX", LIS3MDL[index])

			# creates a new dataframe to add new data
			table_string = '%s_%s_%s' % (LIS3MDL[index][9],LIS3MDL[index][5],LIS3MDL[index][3])

			ret = table_exists(psql_connection, table_string)
			if ret is False:
				table_create(psql_connection,  table_string)
			
			ret, ent_id = insert_data(psql_connection,  table_string, LIS3MDL[index][0], LIS3MDL[index][6], LIS3MDL[index][7], LIS3MDL[index][8],LIS3MDL[index][9])
			if ret is False:
				os.exit("SQL Write Faild")
			
			purge_data_totime(psql_connection,  table_string, keep_data_lengh)
			
			index = index + 1			

	 
	elif method.routing_key == 'lsm6ds3':
		# decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")
		origin_tag = sensor_values[-1:]
		del sensor_values[-1]		
		longitude = sensor_values[-1:]
		del sensor_values[-1]	
		latitude = sensor_values[-1:]
		del sensor_values[-1]
		sensortimestamp = sensor_values[-1:]
		del sensor_values[-1]			
		index = 0	
		for value in sensor_values:
			#print("LSM6DS3:", float(value))
			LSM6DS3[index][0] = float(value)					
			LSM6DS3[index][6] = sensortimestamp[0]
			LSM6DS3[index][7] = latitude[0]
			LSM6DS3[index][8] = longitude[0]
			LSM6DS3[index][9] = origin_tag[0].strip("' '")
			#print("MATRIX", LSM6DS3[index])

			# creates a new dataframe to add new data
			table_string = '%s_%s_%s' % (LSM6DS3[index][9],LSM6DS3[index][5],LSM6DS3[index][3])

			ret = table_exists(psql_connection, table_string)
			if ret is False:
				table_create(psql_connection,  table_string)
			
			ret, ent_id = insert_data(psql_connection,  table_string, LSM6DS3[index][0], LSM6DS3[index][6], LSM6DS3[index][7], LSM6DS3[index][8],LSM6DS3[index][9])
			if ret is False:
				os.exit("SQL Write Faild")
			
			purge_data_totime(psql_connection,  table_string, keep_data_lengh)
			
			index = index + 1	
		
	 
	elif method.routing_key == 'scd4x':
		# decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")
		origin_tag = sensor_values[-1:]
		del sensor_values[-1]		
		longitude = sensor_values[-1:]
		del sensor_values[-1]	
		latitude = sensor_values[-1:]
		del sensor_values[-1]
		sensortimestamp = sensor_values[-1:]
		del sensor_values[-1]	
		index = 0
		for value in sensor_values:
			#print("SCD4X:", float(value))
			SCD4X[index][0] = float(value)					
			SCD4X[index][6] = sensortimestamp[0]
			SCD4X[index][7] = latitude[0]
			SCD4X[index][8] = longitude[0]
			SCD4X[index][9] = origin_tag[0].strip("' '")
			#print("MATRIX", SCD4X[index])

			# creates a new dataframe to add new data
			table_string = '%s_%s_%s' % (SCD4X[index][9],SCD4X[index][5],SCD4X[index][3])

			ret = table_exists(psql_connection, table_string)
			if ret is False:
				table_create(psql_connection,  table_string)
			
			ret, ent_id = insert_data(psql_connection,  table_string, SCD4X[index][0], SCD4X[index][6], SCD4X[index][7], SCD4X[index][8],SCD4X[index][9])
			if ret is False:
				os.exit("SQL Write Faild")
			
			purge_data_totime(psql_connection,  table_string, keep_data_lengh)
			
			index = index + 1			
		
	 
	elif method.routing_key == 'sht30':
		# decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")
		origin_tag = sensor_values[-1:]
		del sensor_values[-1]		
		longitude = sensor_values[-1:]
		del sensor_values[-1]	
		latitude = sensor_values[-1:]
		del sensor_values[-1]
		sensortimestamp = sensor_values[-1:]
		del sensor_values[-1]		
		index = 0		
		for value in sensor_values:
			#print("SHT30:", float(value))
			SHT30[index][0] = float(value)					
			SHT30[index][6] = sensortimestamp[0]
			SHT30[index][7] = latitude[0]
			SHT30[index][8] = longitude[0]
			SHT30[index][9] = origin_tag[0].strip("' '")
			#print("SHT30", SHT30[index])		

			# creates a new dataframe to add new data
			table_string = '%s_%s_%s' % (SHT30[index][9],SHT30[index][5],SHT30[index][3])

			ret = table_exists(psql_connection, table_string)
			if ret is False:
				table_create(psql_connection,  table_string)
			
			ret, ent_id = insert_data(psql_connection,  table_string, SHT30[index][0], SHT30[index][6], SHT30[index][7], SHT30[index][8],SHT30[index][9])
			if ret is False:
				os.exit("SQL Write Faild")
			
			purge_data_totime(psql_connection,  table_string, keep_data_lengh)
				
			index = index + 1
	
	 
	elif method.routing_key == 'bmp280':
		# decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")	
		origin_tag = sensor_values[-1:]
		del sensor_values[-1]		
		longitude = sensor_values[-1:]
		del sensor_values[-1]	
		latitude = sensor_values[-1:]
		del sensor_values[-1]
		sensortimestamp = sensor_values[-1:]
		del sensor_values[-1]		
		index = 0	
		for value in sensor_values:
			#print("BMP280:", float(value))
			BMP280[index][0] = float(value)					
			BMP280[index][6] = sensortimestamp[0]
			BMP280[index][7] = latitude[0]
			BMP280[index][8] = longitude[0]
			BMP280[index][9] = origin_tag[0].strip("' '")
			#print("MATRIX", BMP280[index])

			# creates a new dataframe to add new data
			table_string = '%s_%s_%s' % (BMP280[index][9],BMP280[index][5],BMP280[index][3])

			ret = table_exists(psql_connection, table_string)
			if ret is False:
				table_create(psql_connection,  table_string)
			
			ret, ent_id = insert_data(psql_connection,  table_string, BMP280[index][0], BMP280[index][6], BMP280[index][7], BMP280[index][8],BMP280[index][9])
			if ret is False:
				os.exit("SQL Write Faild")
			
			purge_data_totime(psql_connection,  table_string, keep_data_lengh)
			
			index = index + 1	
	
	 
	elif method.routing_key == 'thermal_frame':
	    # decodes data byte stream and splits the values by comma
		sensor_values = body.decode()
		sensor_frame = ast.literal_eval(sensor_values)			
		
		origin_tag = sensor_frame[4]
		longitude = sensor_frame[3]
		latitude = sensor_frame[2]
		sensortimestamp = sensor_frame[1]

		index = 0		
		for sensor_array_line in sensor_frame[0]:
			for datapoint in sensor_array_line:
				TERMALFRAME[index] = float(datapoint)
				index = index + 1
	
		TERMALFRAME[64] = sensortimestamp
		TERMALFRAME[65] = longitude
		TERMALFRAME[66] = latitude
		TERMALFRAME[67] = origin_tag

		#print("MATRIX", TERMALFRAME)
		
		# creates a new dataframe to add new data
		table_string = '%s_%s_%s' % (TERMALFRAME[67],'TERMALFRAME','ARRAY')

		ret = table_exists(psql_connection, table_string)
		if ret is False:
			table_create_termalframe(psql_connection,  table_string)
			
		ret, ent_id = insert_data_termal(psql_connection,  table_string, TERMALFRAME[0], TERMALFRAME[1], TERMALFRAME[2], TERMALFRAME[3], TERMALFRAME[4], TERMALFRAME[5], TERMALFRAME[6], TERMALFRAME[7],	TERMALFRAME[8], TERMALFRAME[9], TERMALFRAME[10], TERMALFRAME[11], TERMALFRAME[12], TERMALFRAME[13], TERMALFRAME[14], TERMALFRAME[15], TERMALFRAME[16], TERMALFRAME[17], TERMALFRAME[18], TERMALFRAME[19], TERMALFRAME[20], TERMALFRAME[21], TERMALFRAME[22], TERMALFRAME[23], TERMALFRAME[24], TERMALFRAME[25],
TERMALFRAME[26], TERMALFRAME[27], TERMALFRAME[28], TERMALFRAME[29], TERMALFRAME[30], TERMALFRAME[31], TERMALFRAME[32], TERMALFRAME[33], TERMALFRAME[34], TERMALFRAME[35],
TERMALFRAME[36], TERMALFRAME[37], TERMALFRAME[38], TERMALFRAME[39], TERMALFRAME[40], TERMALFRAME[41], TERMALFRAME[42], TERMALFRAME[43], TERMALFRAME[44], TERMALFRAME[45],
TERMALFRAME[46], TERMALFRAME[47], TERMALFRAME[48], TERMALFRAME[49], TERMALFRAME[50], TERMALFRAME[51], TERMALFRAME[52], TERMALFRAME[53], TERMALFRAME[54], TERMALFRAME[55],
TERMALFRAME[56], TERMALFRAME[57], TERMALFRAME[58], TERMALFRAME[59], TERMALFRAME[60], TERMALFRAME[61], TERMALFRAME[62], TERMALFRAME[63], TERMALFRAME[64], TERMALFRAME[65], TERMALFRAME[66] ,TERMALFRAME[67])
		print("Termal",ret, ent_id)
		if ret is False:
			os.exit("SQL Write Faild")
			
		purge_data_totime(psql_connection,  table_string, keep_data_lengh)

			
	return



  
  
    
# Prepare connection to PSQL
config = load_config()
psql_connection = connect_psql(config)
psql_connection.autocommit = True

print(' [*] Waiting for logs. To exit press CTRL+C')


if __name__ == "__main__":
	channel.basic_consume(queue='',on_message_callback=callback, auto_ack=True)
	try:	
		channel.start_consuming()
	except KeyboardInterrupt or Exception or OSError as e:
		print("Termination", e)
		sys.exit(1)






