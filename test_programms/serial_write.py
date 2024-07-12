#!7bin/python3
# -*- coding: UTF-8 -*-

import serial
import time

port = '/dev/serial0'
baud = 9600
#baud = 115200
stream = serial.Serial(port, baud, timeout=.1)
stream.reset_input_buffer()

def push_data():
	data = 'mode=1\n'
	message = data.encode()
	stream.write(message)
	stream.flush()
	return

while True:
	push_data()
	time.sleep(1)
