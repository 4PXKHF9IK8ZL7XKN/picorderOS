#!7bin/python3
# -*- coding: UTF-8 -*-

import serial
import time

port = '/dev/serial0'
baud = 9600
#baud = 115200
stream = serial.Serial(port, baud, timeout=.1)
stream.reset_input_buffer()

def get_data():
	data_str = None
	if (stream.in_waiting > 0):
		data_str = stream.readline(stream.inWaiting()).decode('ascii',"ignore").rstrip()
		return data_str

while True:
	ret_data = get_data()
	if ret_data is not None:
		print(ret_data)
	time.sleep(0.1)
