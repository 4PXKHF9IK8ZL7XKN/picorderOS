#!/usr/bin/python

# PicorderOS --------------------------------------------- 2023
# Created by Chris Barrett ------------------------- directive0
# For my sister, a real life Beverly Crusher.



import os
import sys
import threading
from threading import Thread

print("PicorderOS")
print("Loading Components ... PID: ", threading.get_native_id())


from objects import *
from sensors import *

# for the TR-109 there are two display modes supported.
if configure.tr109:

	# 1.8" TFT colour LCD
	if configure.display == 1 or configure.display == 2 or configure.display == 3:
		from lcars_clr import *

	# Nokia 5110 black and white dot matrix screen.
	if configure.display == 0:
		from lcars_bw import *

# the following function is our main loop, it contains all the flow for our program.
def Main():

	# Instantiate a screen object to draw data to screen. Right now for testing
	# they all have different names but each display object should use the same
	# named methods for simplicity sake.
	if configure.tr108:
		screen_object = Screen()
		configure.graph_size[0] = screen_object.get_size()

	if configure.tr109:
		if configure.display == 0:
			screen_object = NokiaScreen()
		if configure.display == 1 or configure.display == 2 or configure.display == 3:
			screen_object = ColourScreen()
			screen_object.start_up()

		configure.graph_size[0] = screen_object.get_size()

	if configure.CLI:
		screen_object = CLI_Display()


	start_time = time.time()
	
	#start the sensor loop
	sensor_thread = Thread(target = threaded_sensor, args = ())
	sensor_thread.name = 'sensor_thread'
	sensor_thread.start()
	

	print("Main Loop Starting")

	# Main loop. Break when status is "quit".
	while configure.status[0] != "quit":

		# try allows us to capture a keyboard interrupt and assign behaviours.
		try:

			screen_object.run()

			if configure.status[0] == "shutdown":
				print("Shut Down!")
				configure.status[0] = "quit"

				if configure.leds[0]:
					resetleds()

				if configure.input_gpio:
					cleangpio()

				os.system("sudo shutdown -h now")
			

		# If CTRL-C is received the program gracefully turns off the LEDs and resets the GPIO.
		except KeyboardInterrupt:
			configure.status[0] = "quit"

	print("Quit Encountered")
	print("Main Loop Shutting Down")
	
	sensor_thread.join()

	sys.exit()


# the following call starts our program and begins the loop.
Main()
