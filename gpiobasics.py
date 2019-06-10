#!/usr/bin/python

# new Changes
# will need to support a reed switch and more inputs.

# External module import
import RPi.GPIO as GPIO
from objects import *


# Pin Definitons:
led1 = 19 # Broadcom pin 19
led2 = 6 # Broadcom pin 13
led3 = 20
led4 = 16




# Pin Setup:
GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
GPIO.setup(led1, GPIO.OUT) # LED pin set as output
GPIO.setup(led2, GPIO.OUT) # LED pin set as output
GPIO.setup(led3, GPIO.OUT) # LED pin set as output
GPIO.setup(led4, GPIO.OUT) # LED pin set as output


# a function to clear the gpio
def cleangpio():
	GPIO.cleanup() # cleanup all GPIO

# a function to clear the LEDs
def resetleds():
	GPIO.output(led1, GPIO.LOW)
	GPIO.output(led2, GPIO.LOW)
	GPIO.output(led3, GPIO.LOW)
	GPIO.output(led4, GPIO.LOW)

# The following set of functions are for activating each LED individually. I figured it was easier than having different functions for different combinations. This way you can just manually set them as you please.
def leda_on():
	GPIO.output(led1, GPIO.HIGH)

def ledb_on():
	GPIO.output(led2, GPIO.HIGH)

def ledc_on():
	GPIO.output(led3, GPIO.HIGH)

def ledd_on():
	GPIO.output(led4, GPIO.HIGH)

def leda_off():
	GPIO.output(led1, GPIO.LOW)

def ledb_off():
	GPIO.output(led2, GPIO.LOW)

def ledc_off():
	GPIO.output(led3, GPIO.LOW)

def ledd_off():
	GPIO.output(led4, GPIO.LOW)

class ripple(object):
	def __init__(self):
		self.beat = 0

		pass

	def cycle(self):
		self.beat += 1

		if self.beat > 3:
			self.beat = 0

		if self.beat == 0:
			leda_on()
			ledb_off()
			ledc_off()
			ledd_off()

		if self.beat == 1:
			leda_off()
			ledb_on()
			ledc_off()
			ledd_off()

		if self.beat == 2:
			leda_off()
			ledb_off()
			ledc_on()
			ledd_off()

		if self.beat == 3:
			leda_off()
			ledb_off()
			ledc_off()
			ledd_on()
