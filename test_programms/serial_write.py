#!7bin/python3
# -*- coding: UTF-8 -*-

import serial
import time
import sys

port = '/dev/serial0'
#baud = 9600
#baud = 115200
baud =  1000000
stream = serial.Serial(port, baud, timeout=.01)
stream.reset_input_buffer()

def push_data():
	data = sys.argv[1]
	message = data.encode()
	stream.write(message)
	stream.flush()
	return

while True:
	push_data()
	time.sleep(1)
