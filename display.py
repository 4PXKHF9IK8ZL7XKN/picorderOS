print("Unified Display Module loading")

# Serves as a transmission between the various display types and
# the different picorder front ends. Runs the display drawing as a process so
# it can be run concurrently with whatever screen based system the picorder is running.

# (so far only works with tr-109 and LCARS based trics)


import sys
import logging
from objects import *
from multiprocessing import Process,Queue,Pipe
import signal
from luma.core import cmdline, error

def display_settings(device, args):
    """
    Display a short summary of the settings.

    :rtype: str
    """
    iface = ''
    display_types = cmdline.get_display_types()
    if args.display not in display_types['emulator']:
        iface = f'Interface: {args.interface}\n'

    lib_name = cmdline.get_library_for_display_type(args.display)
    if lib_name is not None:
        lib_version = cmdline.get_library_version(lib_name)
    else:
        lib_name = lib_version = 'unknown'

    import luma.core
    version = f'luma.{lib_name} {lib_version} (luma.core {luma.core.__version__})'

    return f'Version: {version}\nDisplay: {args.display}\n{iface}Dimensions: {device.width} x {device.height}\n{"-" * 60}'

def get_device(actual_args=None):
    """
    Create device from command-line arguments and return it.
    """
    if actual_args is None:
        actual_args = sys.argv[1:]
    parser = cmdline.create_parser(description='luma.examples arguments')
    args = parser.parse_args(actual_args)

    if args.config:
        # load config from file
        config = cmdline.load_config(args.config)
        args = parser.parse_args(config + actual_args)

    # create device
    try:
        device = cmdline.create_device(args)
        print(display_settings(device, args))
        return device

    except error.Error as e:
        parser.error(e)
        return None

if configure.display == 3:
        from luma.core.render import canvas
        from luma.emulator.device import pygame

        # Raspberry Pi hardware SPI config:
        DC = 24
        RST = 25
        SPI_PORT = 0
        SPI_DEVICE = 0

        if not configure.pc:
                device = get_device(['--interface', 'spi', '--display', 'st7789', '--spi-port', '0', '--spi-bus-speed', '52000000', '--width', '320', '--height', '240','--mode','RGB' ])
                #device = get_device(['--interface', 'spi', '--display', 'st7789', '--spi-port', '0', '--spi-bus-speed', '52000000', '--width', '160', '--height', '128','--mode','RGB' ])
        else:
                device = pygame(width = 160, height = 128)

if configure.display == 1:
	from luma.core.render import canvas
	from luma.emulator.device import pygame

	# Raspberry Pi hardware SPI config:
	DC = 23
	RST = 24
	SPI_PORT = 0
	SPI_DEVICE = 0

	if not configure.pc:
		serial = spi(port = SPI_PORT, device = SPI_DEVICE, gpio_DC = DC, gpio_RST = RST)
		device = get_device(['--interface', 'spi', '--display', 'st7735', '--spi-port', '0', '--spi-bus-speed', '52000000', '--width', '160', '--height', '128','--mode','RGB'])

	else:
		# if the user has selected the emulated display we
		# load the display as a pygame window.
		device = pygame(width = 160, height = 128)
		# we need something to handle input and send it back to the input handler.


# for TFT24T screens
elif configure.display == 2:
	# Details pulled from https://github.com/BehindTheSciences/ili9341_SPI_TouchScreen_LCD_Raspberry-Pi/blob/master/BTS-ili9341-touch-calibration.py
	from lib_tft24T import TFT24T
	import RPi.GPIO as GPIO
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	import spidev
	DC = 24
	RST = 25
	LED = 15
	PEN = 26
	device = TFT24T(spidev.SpiDev(), GPIO)
	# Initialize display and touch.
	device.initLCD(DC, RST, LED)

# a function intended to be run as a process so as to offload the computation
# of the screen rendering from the GIL.
# takes "q" - a frame of data for the display (PIL imagedraw object)
def DisplayFunction(q):

	# an initiation bit for the process
	go = True

	# lib_tft24 screens require us to create a drawing surface for the screen
	# and add to it.
	if configure.display == 2:
		surface = device.draw()

	while go:

		payload = q.get()

		# add an event to handle shutdown.
		if payload == "quit":
			device.cleanup()
			go = False

		# the following is only for screens that use Luma.LCD
		if configure.display == 1 or configure.display == 3:
			device.display(payload)

		# the following is only for TFT24T screens
		elif configure.display == 2:
			 # Resize the image and rotate it so it's 240x320 pixels.
			frame = payload.rotate(90,0,1).resize((240, 320))
			# Draw the image on the display hardware.
			surface.pasteimage(frame,(0,0))
			device.display()

# a class to control the connected display. It serves as a transmission between
# the main drawing program and the possible connected screen. A range of screens
# and libraries can be used in this way with small modifications to the base
# class.
class GenericDisplay(object):
	width = device.width
	height = device.height

	def __init__(self):
		self.q = Queue()
		self.display_process = Process(target=DisplayFunction, args=(self.q,))
		self.display_process.start()


	# Display takes a PILlow based drawobject and pushes it to screen.
	def display(self,frame):
		self.q.put(frame)
		
	def cleanup(self):
		self.q.put("quit")


