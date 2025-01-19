17#!/bin/python3
# To read the state
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
	state = GPIO.input(17)
	if state:
		print('17 on')
	else:
		print('17 off')

	state2 = GPIO.input(27)
	if state2:
        	print('27 on')
	else:
		print('27 off')

time.sleep(1)

GPIO.cleanup()
