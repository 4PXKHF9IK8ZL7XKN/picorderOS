#!/usr/bin/env python
# This module controls the st7735 type screens

import os
import math
import time
import socket
import threading
import psutil

from objects import *
#from sensors import *

from luma.core.render import canvas
from luma.core.util import perf_counter
from luma.core.sprite_system import framerate_regulator

from operator import itemgetter
from display import GenericDisplay

# This the SVG Converter that allows us to save Vectors and later use them as PNG

from lxml import etree
from cairosvg import svg2png

device = GenericDisplay()

print("Loading LCARS Interface ... PID:", threading.get_native_id())

# Load up the image library stuff to help draw bitmaps to push to the screen
import random
import numpy
import PIL.ImageOps
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

# load the module that draws graphs
#from pilgraph import *
#from amg8833_pil import *
from plars import *


# Load default font.
microfont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.055)) 
littlefont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.079)) 
font = ImageFont.truetype("assets/babs.otf",int(device.height * 0.102)) 
titlefont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.13)) 
bigfont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.16)) 
giantfont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.235))


# Standard LCARS colours
lcars_orange = (255,153,0)
lcars_pink = (204,153,204)
lcars_blue = (153,153,208)
lcars_red = (204,102,102)
lcars_peach = (255,204,153)
lcars_bluer = (153,153,255)
lcars_orpeach = (255,153,102)
lcars_pinker = (204,102,153)
lcars_grid = (47,46,84)

theme1 =  [lcars_orange,lcars_blue,lcars_pinker]

fore_col = 0
back_col = 1


class DrawGrid(object):
	def __init__(self,x,y,w,h,colour,segx = 4, segy = 4):
		self.x = x
		self.y = y
		self.h = h
		self.w = w
		self.colour = colour
		self.segx = segx
		self.segy = segy

		#calculate the interval of the vertical segments ( | )
		self.intervalx = self.w / self.segx

		#calculate the interval of the horizontal segments ( - )
		self.intervaly = self.h / self.segy

		self.hcoordlist = []
		self.vcoordlist = []

		self.assign()

	def assign(self):

		# determine verticals
		
		# for each division of the total width
		for i in range(self.segx):

			# if not the first and last positions
			if i != 0 and i != self.segx:

				# define coords for the line segment for this position along the y
				y1 = self.y
				y2 = self.y + self.h 
				
				# x position determined by the current i times the interval
				x = self.x + (self.intervalx * i)

				# append the list of the x/y coords for the line segment into the coord list
				result = [(x,y1),(x,y2)]
				self.vcoordlist.append(result)

		# determine horizontals
		for i in range(self.segy):

			# if not the first and last positions
			if i != 0 and i != self.segy:

				# define coords for the line segment for this position along the y
				x1 = self.x
				x2 = self.x + self.w 
				
				# y position determined by the current i times the interval
				y = self.y + (self.intervaly * i)

				# append the list of the x/y coords for the line segment into the coord list
				result = [(x1,y),(x2,y)]
				self.hcoordlist.append(result)
			

	def push(self, draw):

		# draws the horizontals	
		for i in range(len(self.hcoordlist)):
			draw.line(self.hcoordlist[i],self.colour,1)
		
		#draws the verticals
		for i in range(len(self.vcoordlist)):
			draw.line(self.vcoordlist[i],self.colour,1)


class Dialogue(object):

	def __init__(self):

		self.selection = 0


		self.auto = configure.auto[0]
		self.interval = timer()
		self.interval.logtime()

		self.titlex = 25
		self.titley = 6
		self.labely = 102

		self.divider = 47

		self.labely = 102

		self.result = "multi"
		self.title = LabelObj("CAUTION",bigfont, colour = lcars_red)
		self.itemlabel = LabelObj("Item Label",titlefont,colour = lcars_orange)
		self.A_Label = LabelObj("Yes",font,colour = lcars_blue)
		self.B_Label = LabelObj("Enter",font, colour = lcars_blue)
		self.C_Label = LabelObj("No",font, colour = lcars_blue)

		self.item = LabelObj("No Data",bigfont,colour = lcars_orpeach)
		# device needs to show multiple settings
		# first the sensor palette configuration

		self.events = Events([self.result,0,"last",0,0,0,0,0], "poweroff")

	def push(self, draw):

		status,payload = self.events.check()

		#draw the frame heading

		self.title.center(self.titley,self.titlex,135,draw)
		self.A_Label.push(23,self.labely,draw)
		self.C_Label.r_align(156,self.labely,draw)
		self.item.string = "Power Down?"
		self.item.center(self.titley+40, self.titlex, 135,draw)


		return status

	def assign(self,heading,body,result):
		self.title.string = heading
		self.itemlabel.string = body
		self.result = result
		pass

# Controls text objects drawn to the LCD
class LabelObj(object):
	def __init__(self,string, font, colour = lcars_blue):
		self.font = font
		#self.draw = draw
		self.string = string
		self.colour = colour


	# to center the text you need to give it the y position, the starting x pos
	# and the width. Also the draw object.
	def center(self,y,x,w,draw):
		size = self.font.getsize(self.string)
		xmid = x + w/2

		textposx = xmid - (size[0]/2)

		self.push(textposx,y,draw)

	def r_align(self,x,y,draw):
		size = self.font.getbbox(self.string)
		self.push(x-size[0],y,draw)

	# Draws the label onto the provided draw buffer.
	def push(self,locx,locy,draw, string = "None"):
		if string == "None":
			drawstring = self.string
		else:
			drawstring = str(string)
		self.draw = draw
		self.draw.text((locx, locy), drawstring, font = self.font, fill= self.colour)

	def getsize(self):
		size = self.font.getsize(self.string)
		return size

# a class to create a simple text list.
# initialize with x/y coordinates
# on update provide list of items to display, and draw object to draw to.
class Label_List(object):

	def __init__(self, x, y, colour = lcars_orpeach, ofont = font):

		#initial coordinates
		self.x = x
		self.y = y

		# used in the loop to offset y location of items.
		self.jump = 0

		#adjusts the increase in seperation
		self.spacer = 1

		# holds the items to display
		self.labels = []

		self.font = ofont

		self.colour = colour


	# draws the list of items as a text list.
	def update(self, items, draw):
		# clears label buffer.
		self.labels = []

		# for each item in the list of items to draw
		for index, item in enumerate(items):

			string = str(item)
			# create a text item with the string.
			thislabel = LabelObj(string, self.font, colour = self.colour)
			thislabel.push(self.x, self.y + self.jump,draw)

			# increase the y position by the height of the last item, plus spacer
			self.jump += (thislabel.getsize()[1] + self.spacer)

		# when loop is over reset jump counter.
		self.jump = 0

class SelectableLabel(LabelObj):


	def __init__(self,font,draw,oper,colour = lcars_blue, special = 0):
		self.font = font
		self.draw = draw
		self.colour = colour

		# special determines the behaviour of the label for each type of oper
		# the class is supplied. There may be multiple types of int or boolean based
		# configuration parameters so this variable helps make new options
		self.special = special

		# coordinates
		self.x = 0
		self.y = 0

		# basic graphical parameters
		self.fontSize = 33

		# self.myfont = pygame.font.Font(titleFont, self.fontSize)
		# text = "Basic Item"
		# self.size = self.myfont.size(text)

		self.scaler = 3
		self.selected = False
		self.indicator = Image()
		self.content = "default"

		# this variable is a reference to a list stored in "objects.py"
		# containing either a boolean or an integer
		self.oper = oper

	def update(self, content, fontSize, nx, ny, fontType, color):
		self.x = nx
		self.y = ny
		self.content = content
		self.fontSize = fontSize
		self.myfont = pygame.font.Font(fontType, self.fontSize)
		self.color = color
		self.indicator.update(sliderb, nx - 23, ny+1)

	def toggle(self):

		# if the parameter supplied is a boolean just flip it.
		if isinstance(self.oper[0], bool):
			#toggle its state
			self.oper[0] = not self.oper[0]

		# if the parameter supplied is an integer its to change
		# one of the graphed sensors.

		elif isinstance(self.oper[0], int):

			# increment the integer.
			self.oper[0] += 1

			# if the integer is larger than the pool reset it
			if self.special == 1 and self.oper[0] > configure.max_sensors[0]-1:
				self.oper[0] = 0


			if self.special == 2 and self.oper[0] > (len(themes) - 1):
				self.oper[0] = 0


		return self.oper[0]

	def draw(self, surface):
		if self.selected:
			self.indicator.draw(surface)

		label = self.myfont.render(self.content, 1, self.color)


		status_text = "dummy"
		if self.special == 0:
			status_text = str(self.oper[0])
		elif self.special == 1:
			status_text = configure.sensor_info[self.oper[0]][3]
		elif self.special == 2:
			status_text = themenames[self.oper[0]]

		pos = resolution[0] - (self.get_size(status_text) + 37)
		state = self.myfont.render(status_text, 1, self.color)


		surface.blit(label, (self.x, self.y))
		surface.blit(state, (pos, self.y))

# serves as a screen to show the current status of the picorder
class MasterSystemsDisplay(object):

	def __init__(self):
		self.title = None
		self.status_list = None
		#self.draw = draw

		# the set labels for the screen
		self.title = LabelObj("Master Systems Display",titlefont,colour = lcars_orange)

		# three input cue labels
		self.C_Label = LabelObj("Exit",font, colour = lcars_orpeach)

		# A list of all the cool data.
		self.status_list = Label_List(frameconstruct.labelx,frameconstruct.labely, colour = lcars_blue, ofont = littlefont)

		# grabs the RPI model info
		if not configure.pc:
			text = os.popen("cat /proc/device-tree/model").readline()
			self.model = str(text.rstrip("\x00")).replace("Raspberry Pi","Raspi")
		else:
			self.model = "Unknown"

		self.events = Events([1,2,"last",0,0,0,0,0],"msd")


	def load_list(self):
	
		# seconds passed since epoch
		seconds = time.time()
	
		# convert the time in seconds since the epoch to a readable format
		local_time = time.ctime(seconds)

		# pulls data from the modulated_em.py
		wifi = "SSID: " + os.popen("iwgetid").readline()

		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		try:
			s.connect(("8.8.8.8", 80))
			IPAddr = s.getsockname()[0]
		except:
			IPAddr = "No IP Found"
		
		ip_str = "IP:  " + IPAddr
		host_str = "Name:  " + socket.gethostname()
		sense_ready = "Sensors Avl:  " + str(len(configure.sensor_info))
		model_name = "CPU:  " + self.model
		PLARS_size, PLARS_em_size = plars.get_plars_size()
		db_size = "PLARS Size:  " + str(PLARS_size)
		em_size = "PLARS EM Size:  " + str(PLARS_em_size)
		loctime = "Time:" + str(local_time)
		lumaperf = "Luma:" + str(perf_counter())

		status_list = [model_name, ip_str, host_str, sense_ready, db_size, em_size, loctime, lumaperf]
		return status_list


	def push(self,draw):

		status, payload = self.events.check()

		#draw the frame heading
		self.title.center(frameconstruct.titley,frameconstruct.titlex,int(device.width*0.25)*-1,draw)	
		self.status_list.update(self.load_list(),draw)
		return status

class PowerMenu(object):
	
	def __init__(self):

		# pages are a description string and an item to change. 
		# If a boolean it will toggle it. 
		# First 3 items are reserved for graph items.
		self.pages = [["Shutdown", "poweroff"],
						["Reboot", "reboot"],
						["Fault Mode", "fault"],
						["Timed Shutdown", "timer"]]

		# Sets the x and y span of the graph
		self.gspanx = 133
		self.gspany = 71

		self.selection = 0
		self.status_raised = False

		self.auto = configure.auto[0]
		self.interval = timer()
		self.interval.logtime()
		#self.draw = draw
		self.titlex = 2
		self.titley = 11
		self.labely = 114

		self.graphcycle = 0
		self.decimal = 1

		self.divider = 47


		# the set labels for the screen
		self.title = LabelObj("Power Control",bigfont)
		self.itemlabel = LabelObj("Item Label",bigfont,colour = lcars_peach)
		self.item = LabelObj("No Data",titlefont,colour = lcars_pink)

		# three input cue labels
		self.A_Label = LabelObj("Next",font,colour = lcars_orpeach)
		self.B_Label = LabelObj("Enter",font, colour = lcars_orpeach)
		self.C_Label = LabelObj("Exit",font, colour = lcars_orpeach)

		self.events = Events([1,2,"last","last",0,"msd",0,0],"settings")


		# device needs to show multiple settings
		# first the sensor palette configuration

	def toggle(self,oper):

		# if the parameter supplied is a boolean
		if isinstance(oper[0], bool):
			#toggle its state
			oper[0] = not oper[0]

		#if the parameter supplied is an integer
		elif isinstance(oper[0], int):

			# increment the integer.
			oper[0] += 1

			# if the integer is larger than the pool
			if oper[0] > configure.max_sensors[0]-1:
				oper[0] = 0

		elif isinstance(oper, str):
			#configure.last_status[0] = configure.status[0]
			self.status_raised = True
			configure.status[0] = oper


		return oper


	def push(self, draw):

		# returns mode_a to the main loop unless something causes state change
		status,payload  = self.events.check()

		if payload == 1:
			self.selection = self.selection + 1
			if self.selection > (len(self.pages) - 1):
				self.selection = 0
		elif payload == 2:
			state = self.toggle(self.pages[self.selection][1])
			if self.status_raised:
				status = state
				self.status_raised = False




		#draw the frame heading
		self.title.push(self.titlex,self.titley,draw)


		#draw the option item heading
		self.itemlabel.string = str(self.pages[self.selection][0])
		self.itemlabel.push(self.titlex+23,self.titley+25,draw)

		self.A_Label.push(2,self.labely,draw)
		self.B_Label.center(self.labely,23,114,draw)
		self.C_Label.r_align(156,self.labely,draw)


		#draw the 3 graph parameter items
		if self.selection == 0 or self.selection == 1 or self.selection == 2:
			self.item.string = str(configure.sensor_info[self.pages[self.selection][1][0]][0])
			self.item.push(self.titlex+23,self.titley+53,draw)
		else:
			if isinstance(self.pages[self.selection][1][0], bool):
				self.item.string = str(self.pages[self.selection][1][0])
				self.item.push(self.titlex+23,self.titley+53,draw)


		return status

class SettingsFrame(object):
	def __init__(self):

		# pages are a description string and an item to change. 
		# If a boolean it will toggle it. 
		# First 3 items are reserved for graph items.
		self.pages = [["Sensor 1", configure.sensor1],
						["Sensor 2", configure.sensor2],
						["Sensor 3", configure.sensor3],
						["Audio", configure.audio],
						["Warble", configure.warble],
						["LEDs", configure.leds_on],
						["Alarm", configure.alarm],
						["Auto Range", configure.auto],
						["Trim Buffer", configure.trim_buffer],
						["Data Logging", configure.datalog]]

		# Sets the x and y span of the graph
		self.gspanx = 133
		self.gspany = 71

		self.selection = 0
		self.status_raised = False

		self.auto = configure.auto[0]
		self.interval = timer()
		self.interval.logtime()
		#self.draw = draw
		self.titlex = 2
		self.titley = 11
		self.labely = 114

		self.graphcycle = 0
		self.decimal = 1

		self.divider = 47


		# the set labels for the screen
		self.title = LabelObj("Settings",bigfont)
		self.itemlabel = LabelObj("Item Label",bigfont,colour = lcars_peach)
		self.item = LabelObj("No Data",titlefont,colour = lcars_pink)

		# three input cue labels
		self.A_Label = LabelObj("Next",font,colour = lcars_orpeach)
		self.B_Label = LabelObj("Enter",font, colour = lcars_orpeach)
		self.C_Label = LabelObj("Exit",font, colour = lcars_orpeach)

		self.events = Events([1,2,"last","last",0,"msd",0,0],"settings")


		# device needs to show multiple settings
		# first the sensor palette configuration

	def toggle(self,oper):

		# if the parameter supplied is a boolean
		if isinstance(oper[0], bool):
			#toggle its state
			oper[0] = not oper[0]

		#if the parameter supplied is an integer
		elif isinstance(oper[0], int):

			# increment the integer.
			oper[0] += 1

			# if the integer is larger than the pool
			if oper[0] > configure.max_sensors[0]-1:
				oper[0] = 0

		elif isinstance(oper, str):
			#configure.last_status[0] = configure.status[0]
			self.status_raised = True
			configure.status[0] = oper


		return oper


	def push(self, draw):

		# returns mode_a to the main loop unless something causes state change
		status,payload  = self.events.check()

		if payload == 1:
			self.selection = self.selection + 1
			if self.selection > (len(self.pages) - 1):
				self.selection = 0
		elif payload == 2:
			state = self.toggle(self.pages[self.selection][1])
			if self.status_raised:
				status = state
				self.status_raised = False




		#draw the frame heading
		self.title.push(self.titlex,self.titley,draw)


		#draw the option item heading
		self.itemlabel.string = str(self.pages[self.selection][0])
		self.itemlabel.push(self.titlex+23,self.titley+25,draw)

		self.A_Label.push(2,self.labely,draw)
		self.B_Label.center(self.labely,23,114,draw)
		self.C_Label.r_align(156,self.labely,draw)


		#draw the 3 graph parameter items
		if self.selection == 0 or self.selection == 1 or self.selection == 2:
			self.item.string = str(configure.sensor_info[self.pages[self.selection][1][0]][0])
			self.item.push(self.titlex+23,self.titley+53,draw)
		else:
			if isinstance(self.pages[self.selection][1][0], bool):
				self.item.string = str(self.pages[self.selection][1][0])
				self.item.push(self.titlex+23,self.titley+53,draw)


		return status

# a simple frame that tells the user that the picorder is loading another screen.
class LoadingFrame(object):

	captions = ["working", "accessing", "initializing", "computing", "calculating"]

	def __init__(self):
		self.annunciator = LabelObj("Stand By",giantfont,colour = lcars_peach)
		self.caption = LabelObj("47",bigfont,colour = lcars_peach)
		self.titley = 20
		self.captiony = 65

	def push(self, draw, status):

		self.caption.string = random.choice(self.captions)
		self.annunciator.center(self.titley,0,160,draw)
		self.caption.center(self.captiony,0,160,draw)

		return status

class StartUp(object):
	def __init__(self):
		self.titlex = 0
		self.titley = 120
		self.labely = 102
		self.jump = 45

		self.graphcycle = 0
		self.decimal = 1

		self.divider = 47
		self.labely = 102


		self.title = LabelObj("PicorderOS " + configure.version,bigfont, colour = lcars_peach)
		self.item = LabelObj(configure.boot_message,font,colour = lcars_peach)

		# creates and interval timer for screen refresh.
		self.interval = timer()
		self.interval.logtime()

	def push(self, draw):


		#draw the frame heading
		self.title.center(self.titley,0,320,draw)

		#draw the title and version
		self.item.center(self.titley+self.jump,0, 320,draw)


		
		status = "msd"

		return status

class PowerDown(object):
	def __init__(self):

		self.selection = 0


		self.auto = configure.auto[0]
		self.interval = timer()
		self.interval.logtime()
		#self.draw = draw
		self.titlex = 25
		self.titley = 6
		self.labely = 102

		self.graphcycle = 0
		self.decimal = 1

		self.divider = 47
		self.labely = 102


		self.title = LabelObj("CAUTION",bigfont, colour = lcars_red)
		self.itemlabel = LabelObj("Item Label",titlefont,colour = lcars_orange)
		self.A_Label = LabelObj("Yes",font,colour = lcars_blue)
		self.B_Label = LabelObj("Enter",font, colour = lcars_blue)
		self.C_Label = LabelObj("No",font, colour = lcars_blue)

		self.item = LabelObj("No Data",bigfont,colour = lcars_orpeach)
		# device needs to show multiple settings
		# first the sensor palette configuration

		self.events = Events(["shutdown",0,"last","0",0,0,0,0], "poweroff")


	def push(self, draw):

		status,payload = self.events.check()

		#draw the frame heading

		self.title.center(self.titley,self.titlex,135,draw)
		self.A_Label.push(23,self.labely,draw)
		self.C_Label.r_align(156,self.labely,draw)
		self.item.string = "Power Down?"
		self.item.center(self.titley+40, self.titlex, 135,draw)


		return status





class frameconstruct:
	titlex = device.width * 0.7 # tested
	titley = -2				# tested
	labelx = device.width * 0.15 # tested
	labely = device.height * 0.15 # tested
	textx = device.width * 0.1
	texty = device.height * 0.1
	triimagex = device.width * 0.7 # tested
	triimagey = device.height * 0.18 # tested
	oslogox = device.width * 0.38 # tested
	oslogoy = device.height * 0.18 # tested

class ColourScreen(object):


	def __init__(self):
		self.backscreen()
		self.svgtopngconvert()
		#self.simplelogoparser()
		# instantiates an image and uses it in a draw object.
		self.image = None
		self.lcarsframe = Image.open('/tmp/lcarsframe.png')
		self.blankimage = Image.open('/tmp/backscreen.png')
		self.lcarsblankimage = Image.open('/tmp/lcarsframeblank.png')
		#self.tbar = Image.open('assets/lcarssplitframe.png')
		self.burger = Image.open('/tmp/lcarsburgerframe.png')
		self.tr109_schematic = Image.open('/tmp/tr109.png')

		# Load assets
		self.logo = Image.open('/tmp/picorderOS_logo.png')

		self.status = "mode_a"

		self.settings_frame = SettingsFrame()
		self.powerdown_frame = PowerDown()
		self.startup_frame = StartUp()
		self.loading_frame = LoadingFrame()
		self.msd_frame = MasterSystemsDisplay()

		# carousel dict to hold the keys and defs for each state
		self.carousel = {"startup":self.start_up,
				   "voc":self.voc_screen,
				   "settings":self.settings,
				   "msd":self.msd,
				   "poweroff":self.powerdown,
				   "shutdown":self.powerdown}

		
	# Creates an image of the screensize in black as background, so that ImageDraw.Draw has allways the full screen to draw on.
	def backscreen(self):
		self.img = Image.new("RGB", (device.width, device.height),(0, 0, 0)) 
		self.draw = ImageDraw.Draw(self.img) 
		self.img.save('/tmp/backscreen.png')
		
	def svgtopngconvert(self):
		svg2png(url="assets/tr109.svg", write_to="/tmp/tr109.png", scale=device.height/128)
		svg2png(url="assets/lcarsframeblank.svg", write_to="/tmp/lcarsframeblank.png", output_width=device.width, output_height=device.height)
		svg2png(url="assets/lcarsburgerframe.svg", write_to="/tmp/lcarsburgerframe.png", output_width=device.width, output_height=device.height)
		svg2png(url="assets/lcarsframe.svg", write_to="/tmp/lcarsframe.png", output_width=device.width, output_height=device.height)
		svg2png(url="assets/picorderOS_logo.svg", write_to="/tmp/picorderOS_logo.png", output_width=device.width/4, output_height=device.height/4)
		
	def simplelogoparser(self):
		#simple open file to read
		with open('assets/picorderOS_logo.svg','r') as file:
			svgtxt = file.read()
			file.close()

	def start_up(self):
		self.newimage = self.blankimage.copy()
		self.newimage.paste(self.burger,(0,0))
		self.newimage.paste(self.logo,(int(frameconstruct.oslogox),int(frameconstruct.oslogoy)))
		self.draw = ImageDraw.Draw(self.newimage)
		self.status = self.startup_frame.push(self.draw)
		self.pixdrw()
		time.sleep(3)
		return self.status

	# simple frame to let user know new info is loading while waiting.
	def loading(self):
		self.newimage = self.blankimage.copy()
		self.newimage.paste(self.burger,(0,0))
		self.draw = ImageDraw.Draw(self.newimage)
		self.status = self.loading_frame.push(self.draw,self.status)

		self.pixdrw()
		return self.status

	def graph_screen(self):
		self.newimage = self.blankimage.copy()
		self.newimage.paste(self.lcarsframe,(0,0))
		self.draw = ImageDraw.Draw(self.newimage)

		last_status = self.status
		self.status = self.multi_frame.push(self.draw)

		if self.status == last_status:
			self.pixdrw()
		else:
			self.loading()

		return self.status

	def voc_screen(self):
		pass

	def em_screen(self):
		self.newimage = self.tbar.copy()
		self.draw = ImageDraw.Draw(self.newimage)
		last_status = self.status
		self.status = self.em_frame.push(self.draw)

		if self.status == last_status:
			self.pixdrw()
		else:
			self.loading()
		return self.status

	def thermal_screen(self):
		self.newimage = self.image.copy()
		self.draw = ImageDraw.Draw(self.newimage)
		last_status = self.status
		self.status = self.thermal_frame.push(self.draw)

		if self.status == last_status:
			self.pixdrw()
		else:
			self.loading()

		return self.status

	def settings(self):
		self.newimage = self.burger.copy()
		self.draw = ImageDraw.Draw(self.newimage)
		last_status = self.status
		self.status = self.settings_frame.push(self.draw)

		if self.status == last_status:
			self.pixdrw()
		else:
			self.loading()
		return self.status

	def msd(self):
		self.newimage = self.blankimage.copy()
		self.newimage.paste(self.lcarsblankimage,(0,0))
		self.newimage.paste(self.tr109_schematic,(int(frameconstruct.triimagex),int(frameconstruct.triimagey)))
		self.draw = ImageDraw.Draw(self.newimage)
		last_status = self.status
		self.status = self.msd_frame.push(self.draw)

		self.pixdrw()
		return self.status
		
	def powerdown(self):
		self.newimage = self.blankimage.copy()
		self.draw = ImageDraw.Draw(self.newimage)
		self.status = self.powerdown_frame.push(self.draw)
		self.pixdrw()
		return self.status

	def pixdrw(self):
		thisimage = self.newimage.convert(mode = "RGB")
		device.display(thisimage)

	def run(self):	
		configure.status[0] = self.carousel[configure.status[0]]()
		
		
if __name__ == '__main__':
	
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


	if configure.CLI:
		screen_object = CLI_Display()

	start_time = time.time()

	regulator = framerate_regulator(fps=30)

	try:
		while True:
			with regulator:
				screen_object.run()

	except KeyboardInterrupt:
		pass
		
