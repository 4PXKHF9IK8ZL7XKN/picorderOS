#!/usr/bin/python

# PicorderOS Alpha --------------------------------- June 2019
# Created by Chris Barrett ------------------------- directive0
#
# Intended Goals:
# Support three display modes (B/W LCD, Colour LCD, Pygame for tr108)
# Support multiple sensor options across all platforms (BME680, AMG8833, sensehat)

print("PicorderOS - Alpha")
print("Loading Main Script")

from objects import *


# This part loads the appropriate modules depending on which preference flags are set.

# If we are NOT just running on a computer for development or demo purposes.
if not configure.pc:
	# load up the LED indicator module and sensors.
	from leds import *
	from sensehat import *
else:
	# otherwise load up the demonstration and dummy modules that emulate sensors and pass GPIO signals without requiring any real GPIO.
	from getcpu import *
	from gpiodummy import *

# The following are only loaded in TR-108 mode
if configure.tr108:
	# Load the TR-108 display modules
	from tos_display import *



# for the new TR-109 there are two display modes supported.
if configure.tr109:

	# 1.8" TFT colour LCD
	if configure.display == "1":
		from lcars_clr import *

	# Nokia 5110 black and white dot matrix screen.
	if configure.display == "0":
		from lcars_bw import *

# the following function is our main object, it contains all the flow for our program.
def Main():
	status = configure.status


	# From out here in the loop we should instantiate the objects that are common to whatever display configuration we want to use.
	sensors = Sensor()
	timeit = timer()
	ledtime = timer()

	# I think this sets the delay between draws.
	interval = 0


	# Instantiate a screen object to draw data to screen. Right now for testing they all have different names but each display object should use the same named methods for simplicity sake.
	if configure.tr108:
		PyScreen = Screen(buttons)
		if not configure.pc:
			moire = led_display()

	if configure.tr109:
		if configure.display == "0":
			dotscreen = NokiaScreen()
		if configure.display == "1":
			colourscreen = ColourScreen()

	timeit.logtime()
	ledtime.logtime()

	if configure.leds[0]:
		lights = ripple()

	print("Main Loop Starting")
	# The following while loop catches ctrl-c exceptions. I use this structure so that status changes will loop back around and have a chance to activate different functions. It gets a little weird going forward, bear with me.
	while status != "quit":

		# try allows us to capture a keyboard interrupt and assign behaviours.
		try:
			# Runs the startup animation played when you first boot the program.

			# Create a timer object to time things.
			start_time = time.time()
			#print("status is: ", configure.status)

			while status == "startup":
				status = "mode_a"

				if configure.tr108:
					status = PyScreen.startup_screen(start_time)

			if status == "ready":
				status = "mode_a"

			# The rest of these loops all handle a different mode, switched by buttons within the functions.
			while(status == "mode_a"):

				if timeit.timelapsed() > interval:
					data = sensors.get()

					# the following is only run if the tr108 flag is set
					if configure.tr108:

						status = PyScreen.graph_screen(data)

						if not configure.pc:
							leda_on()
							ledb_off()
							ledc_off()
							if configure.moire:
								moire.animate()

					if configure.tr109:
						if configure.display == "0":
							status = dotscreen.push(data)
						if configure.display == "1":
							status = colourscreen.graph_screen(data)
						if configure.leds[0] and not configure.pc:
							lights.cycle()



					timeit.logtime()

			while(status == "mode_b"):

				if timeit.timelapsed() > interval:
					data = sensors.get()

					if configure.tr108:
						status = PyScreen.slider_screen(data)
						leda_off()
						ledb_on()
						ledc_off()


					if configure.tr109:
						if configure.leds[0]:
							lights.cycle()

						if configure.display == "0":
							status = dotscreen.push(data)
						if configure.display == "1":
							status = colourscreen.thermal_screen(data)

					timeit.logtime()

			while (status == "settings"):
				#print(status)
				if configure.tr108:
					status = PyScreen.settings()
					leda_off()
					ledb_off()
					ledc_on()

				if configure.tr109:
					if configure.display == "0":
						status = dotscreen.push(data)
					if configure.display == "1":
						status = colourscreen.settings(data)


		# If CTRL-C is received the program gracefully turns off the LEDs and resets the GPIO.
		except KeyboardInterrupt:
			status = "quit"
	print("Quit Encountered")
	print("Main Loop Shutting Down")

	# The following calls are for cleanup and just turn "off" any GPIO
	resetleds()
	cleangpio()
	#print("Quit reached")


# the following call starts our program and begins the loop.
Main()
