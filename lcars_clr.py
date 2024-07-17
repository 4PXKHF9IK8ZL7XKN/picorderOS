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
import ast
from pathlib import Path
from luma.core.virtual import viewport, snapshot, range_overlap
from luma.core.sprite_system import framerate_regulator
from luma.core import cmdline, error
from luma.core.render import canvas
from PIL import ImageFont
from datetime import timedelta

styles = ["type1", "type2", "type3", "type4"]
style = "type1"
i = 0
i2 = 0

# A Timer to as Frameratecontroller
WAIT_TIME_SECONDS = 0.1

animation_step = 0
sensor_animation = 0

lcars_theme_selection = 0

lcars_microfont = None
lcars_littlefont = None
lcars_font = None
lcars_titlefont = None
lcars_bigfont = None
lcars_giantfont = None

# Init rabbitmq connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='sensor_data', exchange_type='topic')

result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='EVENT')
    
# A Trigger for Blinking on sensor event
channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='bme680')

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

def lcars_element_graph(device, draw,pos_ax,pos_ay,pos_bx,pos_by, array):

	#bounding box
	box_element_graph = [(pos_ax , pos_ay), (pos_bx, pos_by)] 
	draw.rectangle(box_element_graph,fill="black", outline=lcars_theme[lcars_theme_selection]["colore5"])
	
	# center line
	calc_center_of_graph = pos_ay+(pos_by - pos_ay)/2
	centerline_element_graph = [(pos_ax,calc_center_of_graph),(pos_bx,calc_center_of_graph)] 
	draw.line(centerline_element_graph,fill=lcars_theme[lcars_theme_selection]["colore5"])



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

def lcars_type2_build():
	global animation_step
	global sensor_animation
	global lcars_theme_selection

	fill2 = "black"
	fill3 = "yellow"
	
	dict_graph = []

	with canvas(device, dither=True) as draw:
					
		lcars_element_elbow(device, draw, device.width*0.01,device.height*0.01,2,lcars_theme[lcars_theme_selection]["colore4"])
		lcars_element_elbow(device, draw, device.width*0.01,device.height*0.86 ,3, lcars_theme[lcars_theme_selection]["colore0"])	
		
		lcars_element_graph(device, draw,device.width*0.15,device.height*0.12,device.width*0.95,device.height*0.85, dict_graph)
           
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
		elif self == "type2":
			lcars_type2_build()    
		elif self == "type3":
			lcars_type3_build()              
		elif self == "type4":
			lcars_type3_build()
        
        



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

             
def callback(ch, method, properties, body):
	global style
	global i
	global i2
	global lcars_colore
	global sensor_animation
	global lcars_theme_selection
	
	if method.routing_key == 'bme680':
		sensor_animation = sensor_animation + 1
		if sensor_animation == 4:
			sensor_animation = 0
		return
    
    
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

# This Class helps to start a thread that runs a timer non blocking to reset the IRQ signal on the mpr121
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
