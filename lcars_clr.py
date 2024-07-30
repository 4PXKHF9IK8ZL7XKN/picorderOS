#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2023 Richard Hull and contributors
# See LICENSE.rst for details.
# PYTHON_ARGCOMPLETE_OK

"""
Unicode font rendering & scrolling.
"""
import os
import sys
import math
import random
import time
import colorsys
import threading
import pika
import pandas as pd
import ast
from objects import *
from pathlib import Path
from luma.core.virtual import viewport, snapshot, range_overlap
from luma.core.sprite_system import framerate_regulator
from luma.core import cmdline, error
from luma.core.render import canvas
from PIL import ImageFont
from datetime import timedelta


bme680_temp = [0]


styles = ["type1", "multi_graph", "type3", "type4"]
style = "type1"
i = 0
i2 = 0

# A Timer to as Frameratecontroller
WAIT_TIME_SECONDS = 0.1

animation_step = 0
sensor_animation = 0
lcars_theme_selection = 0

mapping_book_byname = {}
mapping_book = {}

lcars_microfont = None
lcars_littlefont = None
lcars_font = None
lcars_titlefont = None
lcars_bigfont = None
lcars_giantfont = None


GPS_DATA = [4747.0000,4747.0000]
BUFFER_GLOBAL = pd.DataFrame(columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude'])
BUFFER_GLOBAL_EM = pd.DataFrame(columns=['ssid','signal','quality','frequency','encrypted','channel','dev','mode','dsc','timestamp','latitude','longitude'])

BME680 = [[0,-40,85,'Thermometer','\xB0','BME680','timestamp','latitude','longitude'],[0,0,100,'Hygrometer','%','BME680','timestamp','latitude','longitude'],[0,300,1100,'Barometer','hPa','BME680','timestamp','latitude','longitude'],[0,0,500,'VOC','ppm','BME680','timestamp','latitude','longitude'],[0,0,1100,'ALT','m','BME680','timestamp','latitude','longitude']]
SYSTEMVITALES = [[0,0,'inf','Timer','t','RaspberryPi','timestamp','latitude','longitude'],[0,0,4,'INDICATOR','IND','RaspberryPi','timestamp','latitude','longitude'],[0,-25,100,'CpuTemp','\xB0','RaspberryPi','timestamp','latitude','longitude'],[0,0,400,'CpuPercent','%','RaspberryPi','timestamp','latitude','longitude'],[0,0,4800000,'VirtualMemory','b','RaspberryPi','timestamp','latitude','longitude'],[0,0,100,'disk_usage','%','RaspberryPi','timestamp','latitude','longitude'],[0,0,100000,'BytesSent','b','RaspberryPi','timestamp','latitude','longitude'],[0,0,100000,'BytesReceived','b','RaspberryPi','timestamp','latitude','longitude']]
GENERATORS = [[0,-100,100,'SineWave','','GENERATORS','timestamp','latitude','longitude'],[0,-500,500,'TangentWave','','GENERATORS','timestamp','latitude','longitude'],[0,-100,100,'CosWave','','GENERATORS','timestamp','latitude','longitude'],[0,-100,100,'SineWave2','','GENERATORS','timestamp','latitude','longitude']]
SENSEHAT = [[0,-40,120,'Thermometer','\xB0','sensehat','timestamp','latitude','longitude'],[0,0,100,'Hygrometer','%','sensehat','timestamp','latitude','longitude'],[0,260,1260,'Barometer','hPa','sensehat','timestamp','latitude','longitude'],[0,-500,500,'MagnetX','G','sensehat','timestamp','latitude','longitude'],[0,-500,500,'MagnetY','G','sensehat','timestamp','latitude','longitude'],[0,-500,500,'MagnetZ','G','sensehat','timestamp','latitude','longitude'],[0,-500,500,'"AccelX','g','sensehat','timestamp','latitude','longitude'],[0,-500,500,'"AccelY','g','sensehat','timestamp','latitude','longitude'],[0,-500,500,'"AccelZ','g','sensehat','timestamp','latitude','longitude']]

# Standard LCARS colours
# LCARS CLASSIC THEME, 24# NEMESIS BLUE THEME, 39#LOWER DECKS THEME 42#LOWER DECKS PADD THEME
lcars_colores = [
{"ID":0, "NAME": "space-white", "value": '#f5f6fa' },
{"ID":1, "NAME": "violet-creme", "value": '#ddbbff'},
{"ID":2, "NAME": "green", "value": '#33cc99'},
{"ID":3, "NAME": "magenta", "value": '#cc4499'},
{"ID":4, "NAME": "blue", "value": '#4455ff'},
{"ID":5, "NAME": "yellow", "value": '#ffcc33'},
{"ID":6, "NAME": "violet", "value": '#9944ff'},
{"ID":7, "NAME": "orange", "value": '#ff7700'},
{"ID":8, "NAME": "african-violet", "value": '#cc88ff'},
{"ID":9, "NAME": "text", "value": '#cc77ff'},
{"ID":10, "NAME": "red", "value": '#dd4444'},
{"ID":11, "NAME": "almond", "value": '#ffaa90'},
{"ID":12, "NAME": "almond-creme", "value": '#ffbbaa'},
{"ID":13, "NAME": "sunflower", "value": '#ffcc66'},
{"ID":14, "NAME": "bluey", "value": '#7788ff'},
{"ID":15, "NAME": "gray", "value": '#666688'},
{"ID":16, "NAME": "sky", "value": '#aaaaff'},
{"ID":17, "NAME": "ice", "value": '#88ccff'},
{"ID":18, "NAME": "gold", "value": '#ffaa00'},
{"ID":19, "NAME": "mars", "value": '#ff2200'},
{"ID":20, "NAME": "peach", "value": '#ff8866'},
{"ID":21, "NAME": "butterscotch", "value": '#ff9966'},
{"ID":22, "NAME": "tomato", "value": '#ff5555'},
{"ID":23, "NAME": "lilac", "value": '#cc33ff'},
{"ID":24, "NAME": "evening", "value": '#2255ff'},
{"ID":25, "NAME": "midnight", "value": '#1111ee'},
{"ID":26, "NAME": "ghost", "value": '#88bbff'},
{"ID":27, "NAME": "wheat", "value": '#ccaa88'},
{"ID":28, "NAME": "roseblush", "value": '#cc6666'},
{"ID":29, "NAME": "honey", "value": '#ffcc99'},
{"ID":30, "NAME": "cardinal", "value": '#cc2233'},
{"ID":31, "NAME": "pumpkinshade", "value": '#ff7744'},
{"ID":32, "NAME": "tangerine", "value": '#ff8833'},
{"ID":33, "NAME": "martian", "value": '#99dd66'},
{"ID":34, "NAME": "text2", "value": '#2266ff'},
{"ID":35, "NAME": "moonbeam", "value": '#ccdeff'},
{"ID":36, "NAME": "cool", "value": '#5588ff'},
{"ID":37, "NAME": "galaxy", "value": '#444a77'},
{"ID":38, "NAME": "moonshine", "value": '#ddeeff'},
{"ID":39, "NAME": "october-sunset", "value": '#ff4400'},
{"ID":40, "NAME": "harvestgold", "value": '#ffaa44'},
{"ID":41, "NAME": "butter", "value": '#ddeeff'},
{"ID":42, "NAME": "c43", "value": '#5588ee'},
{"ID":43, "NAME": "c44", "value": '#88ffff'},
{"ID":44, "NAME": "c45", "value": '#344470'},
{"ID":45, "NAME": "c46", "value": '#455580'},
{"ID":46, "NAME": "c47", "value": '#7799dd'},
{"ID":47, "NAME": "c48", "value": '#66ccff'},
{"ID":48, "NAME": "c49", "value": '#99ccff'},
{"ID":49, "NAME": "c50", "value": '#ff3500'},
{"ID":50, "NAME": "c51", "value": '#552255'},
{"ID":51, "NAME": "c52", "value": '#663366'},
{"ID":52, "NAME": "c53", "value": '#774477'},
{"ID":53, "NAME": "c54", "value": '#885588'},
{"ID":54, "NAME": "c55", "value": '#996699'},
{"ID":55, "NAME": "c56", "value": '#ff8800'},
{"ID":56, "NAME": "c57", "value": '#d0b0a0'},
{"ID":57, "NAME": "c58", "value": '#bbbbff'},
{"ID":58, "NAME": "c59", "value": '#99aa66'},
{"ID":59, "NAME": "c60", "value": '#00bb00'},
{"ID":60, "NAME": "c61", "value": '#33ff33'},
{"ID":61, "NAME": "c62", "value": '#ddffdd'},
{"ID":62, "NAME": "c63", "value": '#ffebde'},
{"ID":63, "NAME": "c64", "value": '#cc99cc'},
{"ID":64, "NAME": "c65", "value": '#f6eef6'},
{"ID":65, "NAME": "c66", "value": '#aa66aa'},
{"ID":66, "NAME": "c67", "value": '#dd88dd'},
{"ID":67, "NAME": "c68", "value": '#ff0000'},
{"ID":68, "NAME": "c69", "value": '#cc0000'},
{"ID":69, "NAME": "c70", "value": '#ee0000'},
{"ID":70, "NAME": "c71", "value": '#dfdfdf'},
{"ID":71, "NAME": "c72", "value": '#f7f7f7'},
{"ID":72, "NAME": "42", "value": '#ffeecc'}
]

lcars_theme = [
{"ID": 0 ,"NAME": "LOWER DECKS PADD THEME", "colore0": lcars_colores[42]['value'], "colore1": lcars_colores[43]['value'], "colore2": lcars_colores[44]['value'] , "colore3": lcars_colores[45]['value'], "colore4": lcars_colores[46]['value'], "colore5":lcars_colores[47]['value'], "colore6": lcars_colores[48]['value'], "colore7": lcars_colores[49]['value'], "font0": lcars_colores[43]['value'] },
{"ID": 1 ,"NAME": "LOWER DECKS THEME", "colore0": lcars_colores[39]['value'], "colore1": lcars_colores[40]['value'], "colore2": lcars_colores[7]['value'] , "colore3": lcars_colores[29]['value'], "colore4": lcars_colores[72]['value'], "colore5":lcars_colores[41]['value'], "colore6": lcars_colores[41]['value'], "colore7": lcars_colores[49]['value'], "font0":lcars_colores[43]['value'] },
{"ID": 2 ,"NAME": "Red Alert ?", "colore0": lcars_colores[39]['value'], "colore1": lcars_colores[40]['value'], "colore2": lcars_colores[7]['value'] , "colore3": lcars_colores[29]['value'], "colore4": lcars_colores[41]['value'], "colore5":lcars_colores[41]['value'], "colore6": lcars_colores[41]['value'], "colore7": lcars_colores[49]['value'], "font0": lcars_colores[34]['value'] },
]


# Init rabbitmq connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='sensor_data', exchange_type='topic')

result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue

# We request now all Sensor data and Rabbitmq values to make the graph drawing realy valuable 
channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='#')

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


def lcars_element_graph(device, draw,pos_ax,pos_ay,pos_bx,pos_by, sensors_dict,mode):
	fill = "yellow"
	fill2 = "red"
	offset = 0

	global lcars_microfont

	if configure.samples:
		samples = configure.samples
	else:
		samples = 64
		
	# (calulation the graph lengh absulut) deviding through tha samples to get the steps of drawing 
	graph_resulutio_X_multi = ( pos_bx - pos_ax ) / samples

	#bounding box
	box_element_graph = [(pos_ax , pos_ay), (pos_bx, pos_by)] 
	draw.rectangle(box_element_graph,fill="black", outline=lcars_theme[lcars_theme_selection]["colore5"])
	
	# center line
	#calc_center_of_graph = pos_ay+(pos_by - pos_ay)/2
	#centerline_element_graph = [(pos_ax,calc_center_of_graph),(pos_bx,calc_center_of_graph)] 
	#draw.line(centerline_element_graph,fill=lcars_theme[lcars_theme_selection]["colore5"])
		
	#sensors_legende = str(sensors_dict)
		
	#draw.text((pos_ax, pos_by), text=sensors_legende, font=lcars_microfont, fill=lcars_theme[lcars_theme_selection]["font0"])
	
	# Unpacking the array with dicts
	for index_a, sensors_to_read in enumerate(sensors_dict):
		# dev is the Pi dsc the cpu 
		
		for sensor_dev,sensor_dsc in sensors_to_read.items():
			#print(get_recent(sensor_dsc, sensor_dev, samples, timeing=True))
			recent, timelength = get_recent(sensor_dsc, sensor_dev, samples, timeing=True)		
			
			# This Block checks for the global variable that defines the sensor end selects the array inside so that i can get the min max values 
			my_global_vars = globals()
			#print("!sensor_legende2",my_global_vars[sensor_dev])
			for index_b, array_tosearch in enumerate(my_global_vars[sensor_dev]):
				if array_tosearch[3] == sensor_dsc:
					mysensor_array = my_global_vars[sensor_dev][index_b]
			print("index of array", mysensor_array)
				
			range_of_graph = mysensor_array[2] - mysensor_array[1]
			graph_hight = pos_by - pos_ay
			# this happens for exampe in the Generrators with +-100 min max vaules
			grap_y_multi = graph_hight / range_of_graph
			
			print("graph;", range_of_graph,graph_hight,grap_y_multi )

			if mysensor_array[1] < 0:
				print("is negativ")
				offset = pos_ay*0.4 + mysensor_array[1] 
			
			# This draws my dots
			for index, data_point in enumerate(recent):
				
				#draw.ellipse([pos_bx*0.99-index*graph_resulutio_X_multi,pos_by-grap_y_multi * data_point,pos_bx*0.99+2-index*graph_resulutio_X_multi,pos_by-grap_y_multi * data_point+2],lcars_colores[index_a]['value'], outline = lcars_colores[index_a]['value'])
				
				if len(recent) > 1:
					older_data_point = recent[index - 2]
					
					draw.line([pos_bx*0.99-(index - 2)*graph_resulutio_X_multi,offset+pos_by-grap_y_multi * older_data_point,pos_bx*0.99-(index - 2)*graph_resulutio_X_multi,offset+pos_by-grap_y_multi * older_data_point,pos_bx*0.99-index*graph_resulutio_X_multi,offset+pos_by-grap_y_multi * data_point,pos_bx*0.99-index*graph_resulutio_X_multi,offset+pos_by-grap_y_multi * data_point],fill=lcars_colores[index_a]['value'])
					
					
					
				
			# This Displays the Sensor Naming on the Left
			draw.text((pos_ax, pos_ay+index_a*(device.height * 0.055)), text=str(sensor_dsc), font=lcars_microfont, fill=lcars_colores[index_a]['value'])
			
			# This Displays the Sensor Legende on the Right Top
			draw.text((pos_bx*0.95-index_a*(device.height * 0.1), pos_ay), text=str(mysensor_array[2]), font=lcars_microfont, fill=lcars_colores[index_a]['value'])
			
			# This Displays the Sensor Legende on the Right Bottom
			draw.text((pos_bx*0.95-index_a*(device.height * 0.1), pos_by*0.92), text=str(mysensor_array[1]), font=lcars_microfont, fill=lcars_colores[index_a]['value'])
			

			sensor_legende = round(mysensor_array[0]),mysensor_array[4]
			# This Displays the Sensor Legende Bottom
			draw.text((pos_ax+index_a*(device.height * 0.25), pos_by), text=str(sensor_legende), font=lcars_microfont, fill=lcars_colores[index_a]['value'])
			
			print("bufferinframe", len(recent))



def lcars_element_elbow(device, draw,pos_x,pos_y,rotation,colore):
# element needs x,y position
# element needs rotation form 
# element need colore

	global animation_step
    # Load default font.
    
	fill = colore
	fill2 = "black"
	fill3 = "yellow"
	
	#with canvas(device, dither=True) as draw:
	
	#draw.rectangle(device.bounding_box, outline="white", fill="grey")
	
	radius = device.height*0.05

	# This is wehen the Right is rounded
	if rotation == 0:
		# Main Shape
		Rshape0 = [(pos_x, pos_y ), (pos_x+device.width*0.23, pos_y+device.height*0.05)]
		Rshape1 = [(pos_x+device.width*0.25/2, pos_y+radius/2), (pos_x+device.width*0.26, pos_y+device.height*0.1)]
		shape0 = [(pos_x+device.width*0.2+radius/2,  pos_y), (pos_x+device.width*0.2+radius+radius/2, pos_y+radius)]
	
		# masking
		shape1 = [(pos_x+device.width*0.25/2-radius/2,  pos_y+radius+device.height*0.01), (pos_x+device.width*0.25/2+radius, pos_y+radius*2+device.height*0.01)]
		Rshape2 = [(pos_x+device.width*0.25/2-radius/2,  pos_y+radius+device.height*0.03), (pos_x+device.width*0.25/2+radius, pos_y+radius*2)]
	elif rotation == 1:
		# Main Shape
		Rshape0 = [(pos_x, pos_y+radius*1.5 ), (pos_x+device.width*0.23, pos_y+device.height*0.05+radius*1.5)]
		Rshape1 = [(pos_x+device.width*0.25/2, pos_y+radius/2), (pos_x+device.width*0.26, pos_y+device.height*0.1)]
		shape0 = [(pos_x+device.width*0.2+radius/2,  pos_y+radius*1.5), (pos_x+device.width*0.2+radius+radius/2, pos_y+radius+radius*1.5)]
		
	# this is when the shape0 got down	
		# masking
		shape1 = [(pos_x+device.width*0.25/2-radius/2,  pos_y+radius/2), (pos_x+device.width*0.25/2+radius, pos_y+radius+radius/3)]
		Rshape2 = [(pos_x+device.width*0.25/2-radius/2,  pos_y+radius/2), (pos_x+device.width*0.25/2+radius, pos_y+radius)]

	# This is wehen the left is rounded
	elif rotation == 2:
		Rshape0 = [(pos_x+radius/2, pos_y ), (pos_x+device.width*0.23+radius/2, pos_y+device.height*0.05)]
		Rshape1 = [(pos_x, pos_y+radius/2), (pos_x+device.width*0.25/2, pos_y+device.height*0.1)]
		shape0 = [(pos_x,  pos_y), (pos_x+radius, pos_y+radius)]
		
		# masking
		shape1 = [(pos_x+device.width*0.25/2-radius/2,  pos_y+radius+device.height*0.01), (pos_x+device.width*0.25/2+radius, pos_y+radius*2+device.height*0.01)]
		Rshape2 = [(pos_x+device.width*0.25/2-radius/2,  pos_y+radius+device.height*0.03), (pos_x+device.width*0.25/2+radius, pos_y+radius*2)]
	elif rotation == 3:
		Rshape0 = [(pos_x+radius/2, pos_y +radius*1.5), (pos_x+device.width*0.23+radius/2, pos_y+device.height*0.05+radius*1.5)]
		Rshape1 = [(pos_x, pos_y+radius/2), (pos_x+device.width*0.25/2, pos_y+device.height*0.1)]
		shape0 = [(pos_x,  pos_y+radius*1.5), (pos_x+radius, pos_y+radius+radius*1.5)]
	# this is when the shape0 got down	
		# masking
		shape1 = [(pos_x+device.width*0.25/2-radius/2,  pos_y+radius/2), (pos_x+device.width*0.25/2+radius, pos_y+radius+radius/3)]
		Rshape2 = [(pos_x+device.width*0.25/2-radius/2,  pos_y+radius/2), (pos_x+device.width*0.25/2+radius, pos_y+radius)]


	# main shape
	draw.rectangle(Rshape0, fill)
	draw.rectangle(Rshape1, fill)
	draw.ellipse(shape0, fill, outline = fill) 
	
	# masking
	draw.ellipse(shape1, fill2, outline = fill2) 
	draw.rectangle(Rshape2, fill2)

def lcars_element_end(device, draw, pos_x,pos_y,rotation,colore):
# element needs x,y position
# element needs rotation form 
# element need colore

	global animation_step
    # Load default font.

	fill2 = "black"
	fill3 = "yellow"
	
	radius = device.height*0.05

	# This is wehen the Left is rounded
	if rotation == 0 or rotation == 1:
		# Main Shape
		Rshape0_end = [(pos_x+radius/2, pos_y ), (pos_x+radius+radius/2, pos_y+radius)]
		shape0_end = [(pos_x,  pos_y), (pos_x+radius+radius/2, pos_y+radius)]
		
		#mask
		Rshape1_end = [(pos_x+radius , pos_y), (pos_x+radius+radius/2, pos_y+radius)]


	# This is wehen the left is rounded
	elif rotation == 2 or rotation == 3:
		Rshape0_end = [(pos_x, pos_y ), (pos_x+radius, pos_y+radius)]
		shape0_end = [(pos_x+radius/2,  pos_y), (pos_x+radius+radius/2, pos_y+radius)]
		
		#mask
		Rshape1_end = [(pos_x , pos_y), (pos_x+radius/2, pos_y+radius)]

		
	# main shape

	# main shape
	draw.ellipse(shape0_end, fill = colore, outline = colore) 
	draw.rectangle(Rshape0_end, colore)
	
	# mask
	draw.rectangle(Rshape1_end, fill2)
		
def lcars_element_side_bar(device, draw, pos_x,pos_y,rotation,colore):
# element needs x,y position
# element needs rotation form 
# element need colore

	global animation_step
    # Load default font.
    
	fill = colore
	fill2 = "black"
	fill3 = "red"
	
	radius = device.height*0.05

	Rshape_sidebar = [(pos_x, pos_y ), (pos_x+device.width*0.20/2, pos_y+radius)]
	
	# main shape

	draw.rectangle(Rshape_sidebar, colore)
	
	
def lcars_element_doublebar(device, draw, pos_x,pos_y, posb_x, posb_y,rotation,colore,colore2):
# element needs x,y position
# element needs rotation form 
# element need colore

	global animation_step
    # Load default font.

	Rshape_doublebar0 = [(pos_x, pos_y ), (posb_x, posb_y*0.5)]
	Rshape_doublebar1 = [(pos_x, pos_y*4 ), (posb_x, posb_y)]
	
	# main shape

	draw.rectangle(Rshape_doublebar0 , colore)
	draw.rectangle(Rshape_doublebar1 , colore2)
	
def lcars_element_gibli(device, draw, pos_x,pos_y,rotation,colore):
# element needs x,y position
# element needs rotation form 
# element need colore

	global animation_step
    # Load default font.
	radius = device.height*0.05

	Rshape_gibli = [(pos_x, pos_y ), (pos_x+device.width*0.07, pos_y+radius)]
	
	# main shape
	draw.rectangle(Rshape_gibli , colore)




def lcars_type0_build():
# DEmo grey
    with canvas(device, dither=True) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="grey")
        draw.text((10, 40), "Hello World", fill="white")
        # draw.point((100,40), fill="white") a pixel nothing more
        #draw.textbbox((80, 80), "Header?!")
        
        ## Looks like i found my overlapping box
        text = "Header?!"
        left, top, right, bottom = draw.textbbox((0, 0), text)
        w, h = right - left, bottom - top

        left = (device.width - w) // 2
        top = (device.height - h) // 2
        draw.rectangle((left - 1, top, left + w + 1, top + h), fill="black", outline="black")
        draw.text((left + 1, top), text=text, fill="white")
        
def lcars_type1_build():
# ACCESS Screen 
	global animation_step
	
	with canvas(device, dither=True) as draw:	
		lcars_element_gibli(device, draw, device.width*0.15,device.height*0.7 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		lcars_element_gibli(device, draw, device.width*0.24,device.height*0.7 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		lcars_element_gibli(device, draw, device.width*0.33,device.height*0.7 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		lcars_element_gibli(device, draw, device.width*0.42,device.height*0.7 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		lcars_element_gibli(device, draw, device.width*0.51,device.height*0.7 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		lcars_element_gibli(device, draw, device.width*0.60,device.height*0.7 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		lcars_element_gibli(device, draw, device.width*0.69,device.height*0.7 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		lcars_element_gibli(device, draw, device.width*0.78,device.height*0.7 ,3,lcars_theme[lcars_theme_selection]["colore2"])	
	
		if animation_step == 0:
			lcars_element_gibli(device, draw, device.width*0.15,device.height*0.7 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		elif  animation_step == 1:
			lcars_element_gibli(device, draw, device.width*0.24,device.height*0.7 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		elif  animation_step == 2:
			lcars_element_gibli(device, draw, device.width*0.33,device.height*0.7 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		elif  animation_step == 3:
			lcars_element_gibli(device, draw, device.width*0.42,device.height*0.7 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		elif  animation_step == 4:
			lcars_element_gibli(device, draw, device.width*0.51,device.height*0.7 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		elif  animation_step == 5:
			lcars_element_gibli(device, draw, device.width*0.60,device.height*0.7 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		elif  animation_step == 6:
			lcars_element_gibli(device, draw, device.width*0.69,device.height*0.7 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		elif  animation_step == 7:
			lcars_element_gibli(device, draw, device.width*0.78,device.height*0.7 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		
		lcars_element_end(device, draw, device.width*0.93,device.height*0.015,3,lcars_theme[lcars_theme_selection]["colore4"])
		lcars_element_end(device, draw, device.width*0.93,device.height*0.93,3,lcars_theme[lcars_theme_selection]["colore4"])
		
		lcars_element_end(device, draw, device.width*0.015,device.height*0.015,1,lcars_theme[lcars_theme_selection]["colore4"])
		lcars_element_end(device, draw, device.width*0.015,device.height*0.93,1,lcars_theme[lcars_theme_selection]["colore4"])
		
		radius = device.height*0.05
          
        #end locations
		top_line = [(device.width*0.07 , device.height*0.01), (device.width*0.93, device.height*0.01+radius)] 
		bottom_line = [(device.width*0.07 , device.height*0.93), (device.width*0.93, device.height*0.93+radius)] 
        
		# the connecting from top to bottom
		draw.rectangle(top_line, lcars_theme[lcars_theme_selection]["colore4"])
		draw.rectangle(bottom_line, lcars_theme[lcars_theme_selection]["colore4"])
    
		if animation_step > 14:
			if animation_step % 2 == 0:
				draw.text((device.width*0.2, device.height*0.25), "Accessing",font=lcars_giantfont ,fill=lcars_theme[lcars_theme_selection]["colore1"])
			else:
				draw.text((device.width*0.2, device.height*0.25), "Accessing",font=lcars_giantfont ,fill=lcars_theme[lcars_theme_selection]["colore3"])

def lcars_multi_graph_build():
	global animation_step
	global sensor_animation
	global lcars_theme_selection
	
	global lcars_microfont
	global lcars_littlefont 
	global lcars_font
	global lcars_titlefont 
	global lcars_bigfont 
	global lcars_giantfont

	fill2 = "black"
	fill3 = "yellow"
	
	dict_graph = []

	with canvas(device, dither=True) as draw:
					
		lcars_element_elbow(device, draw, device.width*0.01,device.height*0.01,2,lcars_theme[lcars_theme_selection]["colore4"])
		lcars_element_elbow(device, draw, device.width*0.01,device.height*0.86 ,3, lcars_theme[lcars_theme_selection]["colore0"])	
		
		# selecting Values in Pandas DB via dev & dsc
		sensors_array_with_dict = [{"BME680":"Thermometer"},{"BME680":"Hygrometer"},{"BME680":"Barometer"},{"BME680":"VOC"},{"BME680":"ALT"}]
		#sensors_array_with_dict = [{"GENERATORS":"SineWave"},{"GENERATORS":"CosWave"},{"GENERATORS":"SineWave2"}]
		lcars_element_graph(device, draw,device.width*0.15,device.height*0.12,device.width*0.95,device.height*0.85, sensors_array_with_dict, 1)
           
		radius = device.height*0.05
          
        #end locations
		w0, h0 = device.width*0.015, device.height*0.41
		w1, h1 = device.width*0.22/2, device.height*0.865
        
		Rshape0 = [(w0,  h0), (w1, h1)]
        
		# the connecting from top to bottom
		draw.rectangle(Rshape0, lcars_theme[lcars_theme_selection]["colore5"])

		if sensor_animation == 3:
			lcars_element_side_bar(device, draw, device.width*0.015,device.height*0.13 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.015,device.height*0.13 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		if sensor_animation == 2:
			lcars_element_side_bar(device, draw, device.width*0.015,device.height*0.20 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.015,device.height*0.20 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		if sensor_animation == 1:
			lcars_element_side_bar(device, draw, device.width*0.015,device.height*0.274 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.015,device.height*0.274 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		if sensor_animation == 0:
			lcars_element_side_bar(device, draw, device.width*0.015,device.height*0.345 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.015,device.height*0.345 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		lcars_element_end(device, draw, device.width*0.93,device.height*0.015,3,lcars_theme[lcars_theme_selection]["colore0"])
		lcars_element_end(device, draw, device.width*0.93,device.height*0.93,3,lcars_theme[lcars_theme_selection]["colore0"])
		
		lcars_element_doublebar(device, draw, device.width*0.27 ,device.height*0.01, device.width*0.5, device.height*0.055,0,lcars_theme[lcars_theme_selection]["colore0"],lcars_theme[lcars_theme_selection]["colore5"])
		lcars_element_doublebar(device, draw, device.width*0.51 ,device.height*0.01, device.width*0.60, device.height*0.055,0,lcars_theme[lcars_theme_selection]["colore5"],lcars_theme[lcars_theme_selection]["colore0"])
		
		bottom_line = [(device.width*0.27 , device.height*0.93), (device.width*0.93, device.height*0.93+radius)] 
		
		draw.rectangle(bottom_line,lcars_theme[lcars_theme_selection]["colore5"])
	
		## Looks like i found my overlapping box
		text = str(animation_step)
		left, top, right, bottom = draw.textbbox((0, 0), text)
		w, h = right - left, bottom+2 - top
		w3 = device.width*0.9

		left = w3-radius*2.5
		top = device.height*0.93
		draw.rectangle((left - 1, top, left + w + 1, top + h), fill="black", outline="black")
		draw.text((left + 1, top), text=text, fill=lcars_theme[lcars_theme_selection]["font0"])

def lcars_type3_build():
	global animation_step
	global sensor_animation
	global lcars_theme_selection
	
	global lcars_microfont
	global lcars_littlefont 
	global lcars_font
	global lcars_titlefont 
	global lcars_bigfont 
	global lcars_giantfont

	fill2 = "black"
	fill3 = "yellow"

	with canvas(device, dither=True) as draw:
	
		#draw.rectangle(device.bounding_box, outline="white", fill="grey")
		
		print("lcars_theme:", lcars_theme_selection)
		print(lcars_theme[lcars_theme_selection])
		
		lcars_element_gibli(device, draw, device.width*0.15,device.height*0.7 ,3,lcars_theme[lcars_theme_selection]["colore0"])
		lcars_element_gibli(device, draw, device.width*0.24,device.height*0.7 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		lcars_element_gibli(device, draw, device.width*0.33,device.height*0.7 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		lcars_element_gibli(device, draw, device.width*0.42,device.height*0.7 ,3,lcars_theme[lcars_theme_selection]["colore3"])
		lcars_element_gibli(device, draw, device.width*0.51,device.height*0.7 ,3,lcars_theme[lcars_theme_selection]["colore4"])
		lcars_element_gibli(device, draw, device.width*0.60,device.height*0.7 ,3,lcars_theme[lcars_theme_selection]["colore5"])
		lcars_element_gibli(device, draw, device.width*0.69,device.height*0.7 ,3,lcars_theme[lcars_theme_selection]["colore6"])
		lcars_element_gibli(device, draw, device.width*0.78,device.height*0.7 ,3,lcars_theme[lcars_theme_selection]["colore7"])
		lcars_element_gibli(device, draw, device.width*0.87,device.height*0.7 ,3,lcars_theme[lcars_theme_selection]["font0"])
		lcars_element_gibli(device, draw, device.width*0.87,device.height*0.8 ,3,lcars_colores[animation_step]['value'])
		
		lcars_element_elbow(device, draw, device.width*0.01,device.height*0.01,2,lcars_theme[lcars_theme_selection]["colore4"])

		lcars_element_elbow(device, draw, device.width*0.01,device.height*0.86 ,3, lcars_theme[lcars_theme_selection]["colore0"])	
		#print(animation_step, lcars_colores[animation_step]['value'])
           
		radius = device.height*0.05
          
        #end locations
		w0, h0 = device.width*0.015, device.height*0.41
		w1, h1 = device.width*0.22/2, device.height*0.865
        
		Rshape0 = [(w0,  h0), (w1, h1)]
        
		# the connecting from top to bottom
		draw.rectangle(Rshape0, lcars_theme[lcars_theme_selection]["colore5"])

		if sensor_animation == 3:
			lcars_element_side_bar(device, draw, device.width*0.015,device.height*0.13 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.015,device.height*0.13 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		if sensor_animation == 2:
			lcars_element_side_bar(device, draw, device.width*0.015,device.height*0.20 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.015,device.height*0.20 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		if sensor_animation == 1:
			lcars_element_side_bar(device, draw, device.width*0.015,device.height*0.274 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.015,device.height*0.274 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		if sensor_animation == 0:
			lcars_element_side_bar(device, draw, device.width*0.015,device.height*0.345 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.015,device.height*0.345 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		lcars_element_end(device, draw, device.width*0.93,device.height*0.015,3,lcars_theme[lcars_theme_selection]["colore0"])
		lcars_element_end(device, draw, device.width*0.93,device.height*0.93,3,lcars_theme[lcars_theme_selection]["colore0"])
		
		lcars_element_doublebar(device, draw, device.width*0.27 ,device.height*0.01, device.width*0.5, device.height*0.055,0,lcars_theme[lcars_theme_selection]["colore0"],lcars_theme[lcars_theme_selection]["colore5"])
		lcars_element_doublebar(device, draw, device.width*0.51 ,device.height*0.01, device.width*0.60, device.height*0.055,0,lcars_theme[lcars_theme_selection]["colore5"],lcars_theme[lcars_theme_selection]["colore0"])
		
		bottom_line = [(device.width*0.27 , device.height*0.93), (device.width*0.93, device.height*0.93+radius)] 
		
		draw.rectangle(bottom_line,lcars_theme[lcars_theme_selection]["colore5"])
	
		## Looks like i found my overlapping box
		text = str(animation_step)
		left, top, right, bottom = draw.textbbox((0, 0), text)
		w, h = right - left, bottom+2 - top
		w3 = device.width*0.9

		left = w3-radius*2.5
		top = device.height*0.93
		draw.rectangle((left - 1, top, left + w + 1, top + h), fill="black", outline="black")
		draw.text((left + 1, top), text=text, fill=lcars_theme[lcars_theme_selection]["font0"])
			
		text2 = "dev.height * 0.055"
		text3 = "dev.height * 0.079"
		text4 = "dev.height * 0.102"
		text5 = "dev.height * 0.13"
		text6 = "dev.height * 0.16"
		text7 = "dev.height * 0.235"
		top2 = device.height*0.0
		left2 = device.width*0.0
		
		draw.text((left2 + 1, top2), text=text2, font=lcars_microfont, fill=lcars_theme[lcars_theme_selection]["font0"])	
		draw.text((left2 + 1, top2+device.height * 0.079), text=text3, font=lcars_littlefont , fill=lcars_theme[lcars_theme_selection]["font0"])	
		draw.text((left2 + 1, top2+device.height * 0.079+device.height * 0.102), text=text4, font=lcars_font, fill=lcars_theme[lcars_theme_selection]["font0"])	
		draw.text((left2 + 1, top2+device.height * 0.079+device.height * 0.102+device.height * 0.13), text=text5, font= lcars_titlefont , fill=lcars_theme[lcars_theme_selection]["font0"])	
		draw.text((left2 + 1, top2+device.height * 0.079+device.height * 0.102+device.height * 0.13+device.height * 0.16), text=text6, font=lcars_bigfont, fill=lcars_theme[lcars_theme_selection]["font0"])	
		draw.text((left2 + 1, top2+device.height * 0.079+device.height * 0.102+device.height * 0.13+device.height * 0.16+device.height * 0.235), text=text7, font= lcars_giantfont, fill=lcars_theme[lcars_theme_selection]["font0"])	
		
		

class LCARS_Struct(object):
	global lcars_colore
	global sensor_animation
	def __init__(self,  lcarse_type):
		self.lcarse_type = lcarse_type
                
	def draw(self):
		if self == "type0":
			lcars_type0_build()
		elif self == "type1":
			lcars_type1_build()
		elif self == "multi_graph":
			lcars_multi_graph_build()    
		elif self == "type3":
			lcars_type3_build()              
		elif self == "type4":
			lcars_type3_build()
  
  
# return a list of n most recent data from specific sensor defined by keys
# gets Called from pilgraph
def get_recent(dsc, dev, num, timeing):	
	# Filters the pd Dataframe to a Device like dsc="Thermometer" 
	
	#print("Sensor_count:",configure.max_sensors[0])
	
	currentsize = len(BUFFER_GLOBAL)
	
	#print("currentsize ",currentsize )
	
	result = BUFFER_GLOBAL[BUFFER_GLOBAL["dsc"] == dsc]
	#print("result")
	#print(result)
	
	#print("Buffer")
	#print(BUFFER_GLOBAL[BUFFER_GLOBAL["dsc"] == 'CpuTemp')
	#print(BUFFER_GLOBAL)
	
	untrimmed_data = result.loc[result['dev'] == dev]

	# trim it to length (num).
	trimmed_data = untrimmed_data.tail(num)


	# return a list of the values
	data_line = trimmed_data['value'].tolist()		
	times = trimmed_data['timestamp'].tolist()
	
	# Reversing the datapoints to change graph scrolling later reversed
	slices = data_line[::-1]

	timelength = num

	return slices, timelength      

def update(ch, method, properties, body):
	global BUFFER_GLOBAL
	global GPS_DATA
	global BME680
	global SYSTEMVITALES
	global GENERATORS
	global SENSEHAT
	#print('book=', mapping_book_byname)
	#print('populating=', method.routing_key)
	
	timestamp = time.time()
	value = random.randint(1, 100) 
	#sensors = Sensor()
	fragdata = []
	sensor_values = []
	trimmbuffer_flag = False
	

		
	# configure buffersize
	if configure.buffer_size[0] == 0:
		targetsize = 128
	else:
		targetsize = configure.buffer_size[0]
		
	if method.routing_key == 'GPS_DATA':
		GPS_DATA[0],GPS_DATA[1]  = body.decode().strip("[]").split(",")	
	elif method.routing_key == 'bme680':	
		# decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")		
		index = 0
		for value in sensor_values:
			#print("BME680:", float(value))
			BME680[index][0] = float(value)					
			BME680[index][6] = timestamp
			BME680[index][7] = GPS_DATA[0]
			BME680[index][8] = GPS_DATA[1]
			#print("MATRIX", BME680[index])
			fragdata.append(BME680[index])		
			# creates a new dataframe to add new data 	
			newdata = pd.DataFrame(fragdata, columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude'])
			BUFFER_GLOBAL = pd.concat([BUFFER_GLOBAL,newdata]).drop_duplicates().reset_index(drop=True)
			#BUFFER_GLOBAL = pd.concat([BUFFER_GLOBAL,newdata]).reset_index(drop=True)	
			# we get len of one sensor
			currentsize_persensor = len(BUFFER_GLOBAL[BUFFER_GLOBAL["dsc"] == BME680[index][3]])
			if currentsize_persensor > targetsize:
				trimmbuffer_flag = True		
			index = index + 1			

	elif method.routing_key == 'system_vitals':
		sensor_array_unclean = []
		sensor_values = [0,1,2,3,4,5,6,7]
		#decodes data byte stream and splits the values by comma
		sensor_array_unclean = body.decode().strip("()").split(",")
		cleanup_index = 0
		for value4555 in sensor_array_unclean:
			if cleanup_index == 0:
				# uptime
				sensor_values[0] = value4555.strip("'")
			elif cleanup_index == 1:
				# CPU Load Overall last min
				sensor_values[1] = float(value4555.strip('( '))
			elif cleanup_index == 5:
				# CPU Temperatur
				array2541 = value4555.rsplit('=')
				sensor_values[2] = float(array2541[1])
			elif cleanup_index == 8:
				# CPU Load in Percentage
				sensor_values[3] = float(value4555)
			elif cleanup_index == 9:
				# virtual mem
				sensor_values[4] = float(value4555)
			elif cleanup_index == 13:
				# diskussage in percentage i skipped bytes
				array56461 = value4555.rsplit('=')			
				sensor_values[5] = float(array56461[1].strip(' )'))
			elif cleanup_index == 14:
				# bytes send bytes
				sensor_values[6] = float(value4555)
			elif cleanup_index == 15:
				# bytes rec 
				sensor_values[7] = float(value4555)
			cleanup_index = cleanup_index + 1

		index = 0
		for value in sensor_values:
			#print("SYSTEMVITALES:", value)
			SYSTEMVITALES[index][0] = float(value)					
			SYSTEMVITALES[index][6] = timestamp
			SYSTEMVITALES[index][7] = GPS_DATA[0]
			SYSTEMVITALES[index][8] = GPS_DATA[1]
			#print("MATRIX", SYSTEMVITALES[index])
			fragdata.append(SYSTEMVITALES[index])		
			# creates a new dataframe to add new data 	
			newdata = pd.DataFrame(fragdata, columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude'])
			BUFFER_GLOBAL = pd.concat([BUFFER_GLOBAL,newdata]).drop_duplicates().reset_index(drop=True)
			#BUFFER_GLOBAL = pd.concat([BUFFER_GLOBAL,newdata]).reset_index(drop=True)										
			# we get len of one sensor
			#print("dsc", SYSTEMVITALES[index][3])
			currentsize_persensor = len(BUFFER_GLOBAL[BUFFER_GLOBAL["dsc"] == SYSTEMVITALES[index][3]])
			if currentsize_persensor > targetsize:
				trimmbuffer_flag = True		
			index = index + 1	
			
	elif method.routing_key == 'generators':
	    # decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")		
		index = 0
		for value in sensor_values:
			#print("GENERATORS:", float(value))
			GENERATORS[index][0] = float(value)					
			GENERATORS[index][6] = timestamp
			GENERATORS[index][7] = GPS_DATA[0]
			GENERATORS[index][8] = GPS_DATA[1]
			#print("MATRIX", GENERATORS[index])
			fragdata.append(GENERATORS[index])		
			# creates a new dataframe to add new data 	
			newdata = pd.DataFrame(fragdata, columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude'])
			BUFFER_GLOBAL = pd.concat([BUFFER_GLOBAL,newdata]).drop_duplicates().reset_index(drop=True)
			#BUFFER_GLOBAL = pd.concat([BUFFER_GLOBAL,newdata]).reset_index(drop=True)	
			# we get len of one sensor
			currentsize_persensor = len(BUFFER_GLOBAL[BUFFER_GLOBAL["dsc"] == GENERATORS[index][3]])
			if currentsize_persensor > targetsize:
				trimmbuffer_flag = True	
			index = index + 1	
				
	elif method.routing_key == 'sensehat':
	    # decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")		
		index = 0
		for value in sensor_values:
			#print("SENSEHAT:", float(value))
			SENSEHAT[index][0] = float(value)					
			SENSEHAT[index][6] = timestamp
			SENSEHAT[index][7] = GPS_DATA[0]
			SENSEHAT[index][8] = GPS_DATA[1]
			#print("MATRIX", SENSEHAT[index])
			fragdata.append(SENSEHAT[index])		
			# creates a new dataframe to add new data 	
			newdata = pd.DataFrame(fragdata, columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude'])
			BUFFER_GLOBAL = pd.concat([BUFFER_GLOBAL,newdata]).drop_duplicates().reset_index(drop=True)
			#BUFFER_GLOBAL = pd.concat([BUFFER_GLOBAL,newdata]).reset_index(drop=True)
			# we get len of one sensor
			currentsize_persensor = len(BUFFER_GLOBAL[BUFFER_GLOBAL["dsc"] == GENERATORS[index][3]])
			if currentsize_persensor > targetsize:
				trimmbuffer_flag = True		
			index = index + 1	
			
						
	elif method.routing_key == 'envirophat':
	    # decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")		
		index = 0

	elif method.routing_key == 'pocket_geiger':
	    # decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")		
		index = 0
		
	elif method.routing_key == 'ir_thermo':
	    # decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")		
		index = 0
	
	elif method.routing_key == 'thermal_frame':
	    # decodes data byte stream and splits the values by comma
		sensor_values = body.decode().strip("()").split(",")		
		index = 0

	# PD Fails to handel over 1650 rows so we trim the buffer when 64 rows on any sensor gets reached
	if trimmbuffer_flag:
			BUFFER_GLOBAL = trimbuffer(targetsize)
			
	return


def trimbuffer( targetsize):
	# should take the buffer in memory and trim some of it
	targetsize_all_sensors = targetsize * configure.max_sensors[0]
	
	#print("Target Size",targetsize )
	
	#print("targetsize_all_sensors ",targetsize_all_sensors )
	
	# get buffer size to determine how many rows to remove from the end
	currentsize = len(BUFFER_GLOBAL) 

	#print("currentsize", currentsize)

	# determine difference between buffer and target size
	length = currentsize - targetsize_all_sensors
	
	#print("length", length)


	# make a new dataframe of the most recent data to keep using
	newbuffer = BUFFER_GLOBAL.tail(targetsize_all_sensors)

	# slice off the rows outside the buffer and backup to disk
	tocore = BUFFER_GLOBAL.head(length)

	if configure.datalog[0]:
			append_to_core(tocore)


	# replace existing buffer with new trimmed buffer
	return newbuffer

def init(device):
	print("RUN")
	global lcars_colore
	global lcars_microfont
	global lcars_littlefont 
	global lcars_font
	global lcars_titlefont 
	global lcars_bigfont 
	global lcars_giantfont 
    
	lcars_microfont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.055)) 
	lcars_littlefont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.079)) 
	lcars_font = ImageFont.truetype("assets/babs.otf",int(device.height * 0.102)) 
	lcars_titlefont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.13)) 
	lcars_bigfont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.16)) 
	lcars_giantfont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.235))
	
	lcars_type1_build() 

def callback_rabbitmq_meta(ch, method, properties, body):
	global mapping_book_byname
	global mapping_book
	if body == None:
		time.sleep(0.2)
	else:
		sensor_index_dict = ast.literal_eval(body.decode())	
		configure.max_sensors[0] = sensor_index_dict['sensor_index']
		ret_index = sensor_index_dict.pop('sensor_index')
		mapping_book_byname = sensor_index_dict
		for i in sensor_index_dict:
			mapping_book.update({sensor_index_dict[i]: i})
		channel.basic_cancel('sensor_metadata')
             
def callback(ch, method, properties, body):
	global style
	global i
	global i2
	global lcars_colore
	global sensor_animation
	global lcars_theme_selection
	
	update(ch, method, properties, body)
	
	if method.routing_key != 'EVENT':
		sensor_animation = sensor_animation + 0.5
		if sensor_animation == 4:
			sensor_animation = 0
			
	else:
    
		DICT = body.decode()
		DICT_CLEAN = ast.literal_eval(DICT)
		print(DICT_CLEAN)		
		
		if DICT_CLEAN['geo']:
			style = styles.pop()
			styles.insert(0, style)
			
		if DICT_CLEAN['met']:
			lcars_theme_selection = lcars_theme_selection + 1
			if lcars_theme_selection == 3: 
				lcars_theme_selection = 0

def animation_push():
	global animation_step
	LCARS_Struct.draw(style)
	animation_step = animation_step + 1
	if animation_step == 72:
		animation_step = 0

# This Class helps to start a thread that runs a timer non blocking to animate details
class Job(threading.Thread):
    def __init__(self, interval, execute, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.interval = interval
        self.execute = execute
        self.args = args
        self.kwargs = kwargs

    def stop(self):
                self.stopped.set()
                self.join()
    def run(self):
            while not self.stopped.wait(self.interval.total_seconds()):
                self.execute(*self.args, **self.kwargs)


if __name__ == "__main__":
	channel.basic_consume(consumer_tag='sensor_metadata',queue='sensor_metadata',on_message_callback=callback_rabbitmq_meta, auto_ack=True)
	# Waiting for the Metadata message ca 10 sec
	channel.start_consuming()

	channel.basic_consume(queue='',on_message_callback=callback, auto_ack=True)
	# setup the thread with timer and start the IRQ reset function
	job = Job(interval=timedelta(seconds=WAIT_TIME_SECONDS), execute=animation_push)
	
	try:
		device = get_device(['--interface', 'spi', '--display', 'st7789', '--spi-port', '0', '--spi-bus-speed', '52000000', '--width', '320', '--height', '240','--mode','RGB' ])
		init(device)
		job.start()
		channel.start_consuming()
	except KeyboardInterrupt:
		pass
