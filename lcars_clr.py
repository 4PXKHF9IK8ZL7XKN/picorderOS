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
{"ID":71, "NAME": "c72", "value": '#f7f7f7'}
]

lcars_theme = [
{"ID": 0 ,"NAME": "LOWER DECKS PADD THEME", "colore0": lcars_colores[42]['value'], "colore1": lcars_colores[43]['value'], "colore2": lcars_colores[44]['value'] , "colore3": lcars_colores[45]['value'], "colore4": lcars_colores[46]['value'], "colore5":lcars_colores[47]['value'], "colore6": lcars_colores[48]['value'], "colore7": lcars_colores[49]['value'], "font0": lcars_colores[34]['value'] },
{"ID": 1 ,"NAME": "LOWER DECKS THEME", "colore0": lcars_colores[39]['value'], "colore1": lcars_colores[40]['value'], "colore2": lcars_colores[7]['value'] , "colore3": lcars_colores[29]['value'], "colore4": lcars_colores[41]['value'], "colore5":lcars_colores[41]['value'], "colore6": lcars_colores[41]['value'], "colore7": lcars_colores[49]['value'], "font0": lcars_colores[34]['value'] },
]

lcars_colore = lcars_colores[4]['value']

def lcars_element_elbow(pos_x,pos_y,rotation,colore):
# element needs x,y position
# element needs rotation form 
# element need colore

	global animation_step
    # Load default font.
    
	fill = lcars_colore
	fill2 = "black"
	fill3 = "yellow"
	
	with canvas(device, dither=True) as draw:
	
		draw.rectangle(device.bounding_box, outline="white", fill="grey")
		
		radius = device.height*0.05
	
		# This is wehen the Right is rounded
		if rotation == 0:
			print("0")
			# Main Shape
			Rshape0 = [(pos_x, pos_y ), (pos_x+device.width*0.23, pos_y+device.height*0.05)]
			Rshape1 = [(pos_x+device.width*0.25/2, pos_y+radius/2), (pos_x+device.width*0.26, pos_y+device.height*0.1)]
			shape0 = [(pos_x+device.width*0.2+radius/2,  pos_y), (pos_x+device.width*0.2+radius+radius/2, pos_y+radius)]
		
			# masking
			#shape1 = [(pos_x+device.width*0.075,  pos_y+radius+device.height*0.01), (pos_x+device.width*0.075+radius, pos_y+radius*2+device.height*0.01)]
			#Rshape2 = [(pos_x+device.width*0.075, pos_y+radius+device.height*0.03), (pos_x+device.width*0.075+radius, pos_y+radius*2+device.height*0.01)]
		elif rotation == 1:
			print("1")
 			# Main Shape
			Rshape0 = [(pos_x, pos_y+radius*1.5 ), (pos_x+device.width*0.23, pos_y+device.height*0.05+radius*1.5)]
			Rshape1 = [(pos_x+device.width*0.25/2, pos_y+radius/2), (pos_x+device.width*0.26, pos_y+device.height*0.1)]
			shape0 = [(pos_x+device.width*0.2+radius/2,  pos_y+radius*1.5), (pos_x+device.width*0.2+radius+radius/2, pos_y+radius+radius*1.5)]
		
			# masking
			#shape1 = [(pos_x+device.width*0.09,  pos_y+radius+device.height*0.01), (pos_x+device.width*0.09+radius, pos_y+radius*2+device.height*0.01)]
			#Rshape2 = [(pos_x+device.width*0.09, pos_y+radius+device.height*0.03), (pos_x+device.width*0.09+radius, pos_y+radius*2+device.height*0.01)]
 
 		# This is wehen the left is rounded
		elif rotation == 2:
			print("2")
			Rshape0 = [(pos_x+radius/2, pos_y ), (pos_x+device.width*0.23+radius/2, pos_y+device.height*0.05)]
			Rshape1 = [(pos_x, pos_y+radius/2), (pos_x+device.width*0.25/2, pos_y+device.height*0.1)]
			shape0 = [(pos_x,  pos_y), (pos_x+radius, pos_y+radius)]
		elif rotation == 3:
			print("3")
			Rshape0 = [(pos_x+radius/2, pos_y +radius*1.5), (pos_x+device.width*0.23+radius/2, pos_y+device.height*0.05+radius*1.5)]
			Rshape1 = [(pos_x, pos_y+radius/2), (pos_x+device.width*0.25/2, pos_y+device.height*0.1)]
			shape0 = [(pos_x,  pos_y+radius*1.5), (pos_x+radius, pos_y+radius+radius*1.5)]
 
 
    	# main shape
		draw.rectangle(Rshape0, fill)
		draw.rectangle(Rshape1, fill)
		draw.ellipse(shape0, fill, outline = fill) 
		
		# masking
		#draw.ellipse(shape1, fill2, outline = fill2) 
		#draw.rectangle(Rshape2, fill2)

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
        
def lcars_type1_build(lcars_colore):
# ACCESS Screen 
	global animation_step

	# Load default font.
	lcars_microfont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.055)) 
	lcars_littlefont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.079)) 
	lcars_font = ImageFont.truetype("assets/babs.otf",int(device.height * 0.102)) 
	lcars_titlefont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.13)) 
	lcars_bigfont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.16)) 
	lcars_giantfont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.235))


		
	if animation_step <= 3:
		fill_g1 = '#344470'
		fill_g2 = '#344470'
		fill_g3 = '#344470'
		fill_g4 = '#344470'
		fill_g5 = '#344470'
		fill_g6 = '#344470'
		fill_g7 = '#344470'
		fill_g8 = '#344470'
	elif animation_step == 4:
		fill_g1 = '#88ffff'
		fill_g2 = '#344470'
		fill_g3 = '#344470'
		fill_g4 = '#344470'
		fill_g5 = '#344470'
		fill_g6 = '#344470'
		fill_g7 = '#344470'
		fill_g8 = '#344470'
	elif animation_step == 5:
		fill_g1 = '#344470'
		fill_g2 = '#88ffff'
		fill_g3 = '#344470'
		fill_g4 = '#344470'
		fill_g5 = '#344470'
		fill_g6 = '#344470'
		fill_g7 = '#344470'
		fill_g8 = '#344470'
	elif animation_step == 6:
		fill_g1 = '#344470'
		fill_g2 = '#344470'
		fill_g3 = '#88ffff'
		fill_g4 = '#344470'
		fill_g5 = '#344470'
		fill_g6 = '#344470'
		fill_g7 = '#344470'
		fill_g8 = '#344470'
	elif animation_step == 7:
		fill_g1 = '#344470'
		fill_g2 = '#344470'
		fill_g3 = '#344470'
		fill_g4 = '#88ffff'
		fill_g5 = '#344470'
		fill_g6 = '#344470'
		fill_g7 = '#344470'
		fill_g8 = '#344470'
	elif animation_step == 8:
		fill_g1 = '#344470'
		fill_g2 = '#344470'
		fill_g3 = '#344470'
		fill_g4 = '#344470'
		fill_g5 = '#88ffff'
		fill_g6 = '#344470'
		fill_g7 = '#344470'
		fill_g8 = '#344470'
	elif animation_step == 9:
		fill_g1 = '#344470'
		fill_g2 = '#344470'
		fill_g3 = '#344470'
		fill_g4 = '#344470'
		fill_g5 = '#344470'
		fill_g6 = '#88ffff'
		fill_g7 = '#344470'
		fill_g8 = '#344470'
	elif animation_step == 10:
		fill_g1 = '#344470'
		fill_g2 = '#344470'
		fill_g3 = '#344470'
		fill_g4 = '#344470'
		fill_g5 = '#344470'
		fill_g6 = '#344470'
		fill_g7 = '#88ffff'
		fill_g8 = '#344470'
	elif animation_step == 11:
		fill_g1 = '#344470'
		fill_g2 = '#344470'
		fill_g3 = '#344470'
		fill_g4 = '#344470'
		fill_g5 = '#344470'
		fill_g6 = '#344470'
		fill_g7 = '#344470'
		fill_g8 = '#88ffff'
	elif animation_step >= 12:
		fill_g1 = '#88ffff'
		fill_g2 = '#88ffff'
		fill_g3 = '#88ffff'
		fill_g4 = '#88ffff'
		fill_g5 = '#88ffff'
		fill_g6 = '#88ffff'
		fill_g7 = '#88ffff'
		fill_g8 = '#88ffff'
        
	with canvas(device, dither=True) as draw:
		# top line
		fill = lcars_colore
		fill2 = "black"
		fill3 = "yellow"
  
  
        
		radius = device.height*0.05
		w0, h0 = device.width*0.05, device.height*0.01
		w1, h1 = device.width*0.05, device.height*0.9
		w2, h2 = device.width*0.9, device.height*0.01
		w3, h3 = device.width*0.9, device.height*0.9
        
		shape0 = [(w0,  h0), (w0+radius, h0+radius)]
		shape1 = [(w1 , h1), (w1+radius, h1+radius)] 
		shape2 = [(w2 , h2), (w2+radius, h2+radius)] 
		shape3 = [(w3 , h3), (w3+radius, h3+radius)]
        
		Rshape0 = [(w0+radius/2,  h0+radius), (w2+radius/2, h0)]
		Rshape1 = [(w1+radius/2 , h1+radius), (w3+radius/2, h3)] 
        
		# Ending Lines
		Rshape4 = [(device.width*0.09 , device.height), (device.width*0.09+radius/2, 0)]
		Rshape5 = [(w3 , device.height), (w3-radius/2, 0)]   
		
		# Bottom Line 10 Times 
		Rshape6 = [(device.height*0.15 , device.height*0.7), (device.height*0.25, device.height*0.7+radius)] 
		Rshape7 = [(device.height*0.28 , device.height*0.7), (device.height*0.38, device.height*0.7+radius)] 
		Rshape8 = [(device.height*0.41 , device.height*0.7), (device.height*0.51, device.height*0.7+radius)]   
		Rshape9 = [(device.height*0.54, device.height*0.7), (device.height*0.64, device.height*0.7+radius)] 
		Rshape10 = [(device.height*0.67 , device.height*0.7), (device.height*0.77, device.height*0.7+radius)] 
		Rshape11 = [(device.height*0.80 , device.height*0.7), (device.height*0.90, device.height*0.7+radius)] 
		Rshape12 = [(device.height*0.93 , device.height*0.7), (device.height*1.03, device.height*0.7+radius)] 
		Rshape13 = [(device.height*1.06 , device.height*0.7), (device.height*1.16, device.height*0.7+radius)]   
	
        
		draw.ellipse(shape0, fill, outline = fill) 
		draw.ellipse(shape1, fill, outline = fill) 
		draw.ellipse(shape2, fill, outline = fill) 
		draw.ellipse(shape3, fill, outline = fill) 
        
		draw.rectangle(Rshape0, fill)
		draw.rectangle(Rshape1, fill)
        
		# Ending Lines
		draw.rectangle(Rshape4, fill2)
		draw.rectangle(Rshape5, fill2)
			
		
		
		# Bottom Line 10 Times 
		draw.rectangle(Rshape6, fill_g1)
		draw.rectangle(Rshape7, fill_g2)
		draw.rectangle(Rshape8, fill_g3)
		draw.rectangle(Rshape9, fill_g4)
		draw.rectangle(Rshape10, fill_g5)
		draw.rectangle(Rshape11, fill_g6)
		draw.rectangle(Rshape12, fill_g7)
		draw.rectangle(Rshape13, fill_g8)

		
        
		if animation_step > 14:
			if animation_step % 2 == 0:
				draw.text((device.width*0.2, device.height*0.25), "Accessing",font=lcars_giantfont ,fill=lcars_colores[20]['value'])
			else:
				draw.text((device.width*0.2, device.height*0.25), "Accessing",font=lcars_giantfont ,fill=lcars_colores[43]['value'])

def lcars_type2_build(lcars_colore):
    # Load default font.
    lcars_microfont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.055)) 
    lcars_littlefont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.079)) 
    lcars_font = ImageFont.truetype("assets/babs.otf",int(device.height * 0.102)) 
    lcars_titlefont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.13)) 
    lcars_bigfont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.16)) 
    lcars_giantfont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.235))

    with canvas(device, dither=True) as draw:
    
        fill = lcars_colore
        fill2 = "black"
        fill3 = "yellow"
        
        #thicknis of stripes 
        radius = device.height*0.05
        
        
        #end dot locations
        w0, h0 = device.width*0.05, device.height*0.01
        w1, h1 = device.width*0.05, device.height*0.9
        w2, h2 = device.width*0.9, device.height*0.01
        w3, h3 = device.width*0.9, device.height*0.9
        
        # masking dots
        w4, h4 = device.width*0.1+radius, device.height*0.1-radius*0.75
        w5, h5 = device.width*0.1+radius, device.height*0.8+radius*0.9
        
        # dot shapes
        shape0 = [(w0,  h0), (w0+radius, h0+radius)]
        shape1 = [(w1 , h1), (w1+radius, h1+radius)] 
        shape2 = [(w2 , h2), (w2+radius, h2+radius)] 
        shape3 = [(w3 , h3), (w3+radius, h3+radius)]
        
        shape4 = [(w4 , h4), (w4+radius, h4+radius)] 
        shape5 = [(w5 , h5), (w5+radius, h5+radius)]
        
        
        Rshape0 = [(w0+radius/2,  h0+radius), (w2+radius/2, h0)]
        Rshape1 = [(w1+radius/2 , h1+radius), (w3+radius/2, h3)] 
        Rshape6 = [(w3 , device.height), (w3-radius/2, 0)]   
		
        
        
        # Blinking Regtangels
        Rshape2 = [(w1+radius/2 , h1+radius), (w3+radius/2, h3)] 
        
        
        
        # the connecting from top to bottom
        Rshape2 = [(w1 , h1+radius/2), (device.width*0.15, h0+radius/2)] 
        # masking line
        Rshape3 = [(device.width*0.15-radius*0.4 , h1-radius*0.5), (device.width*0.15+radius*0.5, h0+radius*1.5)]         
        
        
        
        #drawing the dots 
        draw.ellipse(shape0, fill, outline = fill) 
        draw.ellipse(shape1, fill, outline = fill) 
        draw.ellipse(shape2, fill, outline = fill) 
        draw.ellipse(shape3, fill, outline = fill) 
                
        
        # rectangle overdrawing
        draw.rectangle(Rshape0, fill)
        draw.rectangle(Rshape1, fill)
        
        # endline 
        draw.rectangle(Rshape6, fill2)
        
        # the connecting from top to bottom
        draw.rectangle(Rshape2, fill)
        draw.rectangle(Rshape3, fill2)
        
        # masking dots
        draw.ellipse(shape4, fill2, outline = fill2) 
        draw.ellipse(shape5, fill2, outline = fill2) 

def lcars_type3_build(lcars_colore):
	global animation_step
	global sensor_animation
    # Load default font.

	lcars_microfont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.055)) 
	lcars_littlefont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.079)) 
	lcars_font = ImageFont.truetype("assets/babs.otf",int(device.height * 0.102)) 
	lcars_titlefont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.13)) 
	lcars_bigfont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.16)) 
	lcars_giantfont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.235))

	with canvas(device, dither=True) as draw:
	
		#draw.rectangle(device.bounding_box, outline="white", fill="grey")
    
		fill = lcars_colore
		fill2 = "black"
		fill3 = "yellow"
        
        #thicknis of stripes 
		radius = device.height*0.05
		offset = device.width*0.35
		offset2 = device.width*0.47
        
        #end dot locations
		w0, h0 = device.width*0.05, device.height*0.01
		w1, h1 = device.width*0.05, device.height*0.9
		w2, h2 = device.width*0.9, device.height*0.01
		w3, h3 = device.width*0.9, device.height*0.9
		
		# inner dots locations
		w6, h6 = device.width*0.52, device.height*0.01
		w7, h7 = device.width*0.52, device.height*0.9
		w8, h8 = device.width*0.46, device.height*0.01
		w9, h9 = device.width*0.46, device.height*0.9
        
		# masking dots
		w4, h4 = device.width*0.1+radius+offset2, device.height*0.1-radius*0.75
		w5, h5 = device.width*0.1+radius+offset2, device.height*0.8+radius*0.9
		
		# masking dots
		w42, h42 = device.width*0.1+radius, device.height*0.1-radius*0.75
		w52, h52 = device.width*0.1+radius, device.height*0.8+radius*0.9
        
		# dot shapes
		shape0 = [(w0,  h0), (w0+radius, h0+radius)]
		shape1 = [(w1 , h1), (w1+radius, h1+radius)] 
		shape2 = [(w2 , h2), (w2+radius, h2+radius)] 
		shape3 = [(w3 , h3), (w3+radius, h3+radius)]
		
		# dot shapes inner dots
		shape6 = [(w6,  h6), (w6+radius, h6+radius)]
		shape7 = [(w7 , h7), (w7+radius, h7+radius)] 
		shape8 = [(w8 , h8), (w8+radius, h8+radius)] 
		shape9 = [(w9 , h9), (w9+radius, h9+radius)]
        
		shape4 = [(w4 , h4), (w4+radius, h4+radius)] 
		shape5 = [(w5 , h5), (w5+radius, h5+radius)]
		
		shape10 = [(offset+radius/2 , h4), (radius*1.5+offset, h4+radius)] 
		shape11 = [(offset+radius/2 , h5), (radius*1.5+offset, h5+radius)]
        
        
		Rshape0 = [(w0+radius/2,  h0+radius), (offset2+radius/2, h0)]
		Rshape1 = [(w1+radius/2 , h1+radius), (offset2+radius/2, h3)] 
		Rshape6 = [(w3 , device.height), (w3-radius/2, 0)]   
		
		Rshape7 = [(offset2+radius*2,  h0+radius), (w2+radius/2, h0)]
		Rshape8 = [(offset2+radius*2 , h1+radius), (w3+radius/2, h3)] 
        
        
		# Blinking Regtangels
		Rshape2 = [(w1+radius/2 , h1+radius), (w3+radius/2, h3)] 
        
        
        
		# the connecting from top to bottom
		#Rshape2 = [(w1 , h1+radius/2), (device.width*0.15, h0+radius/2)] 
		Rshape2 = [(w1+offset , h1+radius/2), (device.width*0.15+offset, h0+radius/2)] 
		Rshape4 = [(w1+offset2 , h1+radius/2), (device.width*0.15+offset2, h0+radius/2)] 
		# masking line
		Rshape3 = [(device.width*0.15-radius*0.4+offset2 , h1-radius*0.5), (device.width*0.15+radius*0.5+offset2, h0+radius*1.5)]         
		Rshape5 = [(device.width*0.09 , device.height), (device.width*0.09+radius/2, 0)]
		Rshape12 = [(offset+radius*0.5 , h1-radius*0.5), (offset+radius*1.5, h0+radius*1.5)]     
        
        #drawing the dots 
		draw.ellipse(shape0, fill, outline = fill) 
		draw.ellipse(shape1, fill, outline = fill) 
		draw.ellipse(shape2, fill, outline = fill) 
		draw.ellipse(shape3, fill, outline = fill) 
                
        #drawing inner the dots 
		draw.ellipse(shape6, fill, outline = fill) 
		draw.ellipse(shape7, fill, outline = fill) 
		draw.ellipse(shape8, fill, outline = fill) 
		draw.ellipse(shape9, fill, outline = fill) 
        
        
        
        
        # rectangle overdrawing
		draw.rectangle(Rshape0, fill)
		draw.rectangle(Rshape1, fill)
		draw.rectangle(Rshape7, fill)
		draw.rectangle(Rshape8, fill)
		
        
        # endline 
		draw.rectangle(Rshape6, fill2)
        
		# the connecting from top to bottom
		draw.rectangle(Rshape2, fill)
		draw.rectangle(Rshape4, fill)
		
		# masking 
		draw.rectangle(Rshape3, fill2)
		draw.rectangle(Rshape12, fill2)
		
		draw.rectangle(Rshape5, fill2)
        
        # masking dots
		draw.ellipse(shape4, fill2, outline = fill2) 
		draw.ellipse(shape5, fill2, outline = fill2) 
		
		draw.ellipse(shape10, fill2, outline = fill2) 
		draw.ellipse(shape11, fill2, outline = fill2) 
                
		#draw.textbbox((w3-radius*2.5, h3), str(animation_step))
		#draw.text((w3-radius*2.5, h3),str(animation_step),font=lcars_microfont ,fill=lcars_colores[43]['value'])
		
		## Looks like i found my overlapping box
		text = str(animation_step)
		left, top, right, bottom = draw.textbbox((0, 0), text)
		w, h = right - left, bottom+2 - top

		left = w3-radius*2.5
		top = h3
		draw.rectangle((left - 1, top, left + w + 1, top + h), fill="black", outline="black")
		draw.text((left + 1, top), text=text, fill=lcars_colores[43]['value'])
		

class LCARS_Struct(object):
	global lcars_colore
	global sensor_animation
	def __init__(self,  lcarse_type, lcarse_colore):
		self.lcarse_type = lcarse_type
		self.lcarse_colore = lcarse_colore
                
	def draw(self):
		if self == "type0":
			lcars_type0_build()
		elif self == "type1":
			lcars_type1_build(lcars_colore)
		elif self == "type2":
			lcars_type2_build(lcars_colore)    
		elif self == "type3":
			lcars_type3_build(lcars_colore)              
		elif self == "type4":
			print(sensor_animation )
			lcars_element_elbow(device.width*0.1+animation_step, device.height*0.1+animation_step, sensor_animation , lcars_colore)
        
        



def init():
	print("RUN")
	global lcars_colore
	lcars_type1_build("blue")
  

             
def callback(ch, method, properties, body):
	global style
	global i
	global i2
	global lcars_colore
	global sensor_animation
	
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
		lcars_colore_dict = lcars_colores.pop()
		lcars_colore = lcars_colore_dict['value']
		lcars_colores.insert(0, lcars_colore_dict)

def animation_push():
	global animation_step
	LCARS_Struct.draw(style)
	animation_step = animation_step + 1
	if animation_step == 61:
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
		init()
		job.start()
		channel.start_consuming()
	except KeyboardInterrupt:
		pass
