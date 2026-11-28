#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

"""
Unicode font rendering & scrolling.
"""
import os
import os.path
import tempfile
import sys
import math
import random
import time

import osmnx as ox

from pathlib import Path

from datetime import timedelta

import psycopg
from picos_psql_config import load_config

from scipy.interpolate import griddata

cwd = os.getcwd()





i = 0
i2 = 0

# A Timer to as Frameratecontroller
WAIT_TIME_SECONDS = 0.1

animation_step = 0
sensor_animation = 0
lcars_theme_selection = 0

tmp_dirpath = tempfile.mkdtemp()
os.chmod(tmp_dirpath , 0o777)

 
  
  
# return a list of n most recent data from specific sensor defined by keys
# gets Called from pilgraph
def get_recent(tag, dsc, dev, time_ing):	
	timelength = 0
	clean_slices = []
	slices = False

	table_string = '%s_%s_%s' % (tag,dsc,dev)
	table_data = return_data_from_sql(psql_connection_lcars, table_string, time_ing)
	slices = table_data
	if type(table_data) != bool:
		timelength = len(table_data)
		for item in table_data:
			item_clean = float(str(item).strip("(, )"))
			clean_slices.append(item_clean)
		slices = clean_slices
	return slices, timelength    
	

def return_data_from_sql(con, table_str, time_lengh_sec):
	ret = False
	now_time = time.time()
	time_past = now_time - time_lengh_sec 
	
	try:
		cur = con.cursor()
		cur.execute('select value from "' + table_str + '"  where timestamp > '+ str(time_past) + ' order by timestamp desc')
		values = cur.fetchall()
		ret = values
		cur.close()
	except psycopg.Error as e:
		if e == "no results to fetch":
			print( e )
	return ret	
		
def return_debug_sql(con):
	ret = False
	try:
		cur = con.cursor()
		cur.execute('SELECT * FROM "local_BME680_Barometer"')
		values = cur.fetchall()
		print(values)
		ret = values
		cur.close()
	except psycopg.Error as e:
		print(f"{type(e).__name__}: {e}")
		return False
	return ret	
		
def connect_psql(config):
	""" Connect to the PostgreSQL database server """
	try:
		# connecting to the PostgreSQL server
		conn = psycopg.connect(**config, autocommit=True)
		print('Connected to the PostgreSQL server.')
		return conn
	except (psycopg.DatabaseError, Exception) as error:
		print(error) 		



# Prepare connection to PSQL
config = load_config()

psql_connection_lcars = connect_psql(config)

def main():
    while True:
        ret = return_debug_sql(psql_connection_lcars)
        print(ret)
        time.sleep(10)



if __name__ == "__main__":
	try:
	    main()


	except KeyboardInterrupt or Exception or OSError as e:
		print("Termination", e)
		sys.exit(1)
