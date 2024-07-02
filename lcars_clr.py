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
import pika
import ast
from pathlib import Path
from luma.core.virtual import viewport, snapshot, range_overlap
from luma.core.sprite_system import framerate_regulator
from luma.core import cmdline, error
from luma.core.render import canvas
from PIL import ImageFont


styles = ["type0","type1", "type2", "type3"]
style = "type1"
i = 0
i2 = 0

# Init rabbitmq connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='sensor_data', exchange_type='topic')

result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='EVENT')


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

lcars_colore = lcars_colores[4]

# twisty swirly goodness
def swirl(x, y, step):
    print("swirl")
    return


# roto-zooming checker board
def checker(x, y, step):
    print("checker")
    return


# weeee waaaah
def blues_and_twos(x, y, step):
    print("blues")
    return


# rainbow search spotlights
def rainbow_search(x, y, step):
    print("rainbow")
    return


# zoom tunnel
def tunnel(x, y, step):
    print("tunnel")
    return

def lcars_type0_build():
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
    # Load default font.
    lcars_microfont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.055)) 
    lcars_littlefont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.079)) 
    lcars_font = ImageFont.truetype("assets/babs.otf",int(device.height * 0.102)) 
    lcars_titlefont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.13)) 
    lcars_bigfont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.16)) 
    lcars_giantfont = ImageFont.truetype("assets/babs.otf",int(device.height * 0.235))

    with canvas(device, dither=True) as draw:
        # top line
        fill = lcars_colore
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
        
        draw.ellipse(shape0, fill, outline = fill) 
        draw.ellipse(shape1, fill, outline = fill) 
        draw.ellipse(shape2, fill, outline = fill) 
        draw.ellipse(shape3, fill, outline = fill) 
        
        draw.rectangle(Rshape0, fill)
        draw.rectangle(Rshape1, fill)

        draw.text((device.width*0.2, device.height*0.25), "Accessing",font=lcars_giantfont ,fill=lcars_colores[20]['value'])

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
        
        # the connecting from top to bottom
        draw.rectangle(Rshape2, fill)
        draw.rectangle(Rshape3, fill2)
        
        # masking dots
        draw.ellipse(shape4, fill2, outline = fill2) 
        draw.ellipse(shape5, fill2, outline = fill2) 


class LCARS_Struct(object):
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
            lcars_type2_build(lcars_colore)              
        elif self == "type4":
            with canvas(device, dither=True) as draw:
                draw.rectangle((100, 8, 100 + 1, 33 + 1), fill=(255, 255, 0))
        
        



def init():
	print("RUN")
	lcars_type1_build(lcars_colore['value'])
  

             
def callback(ch, method, properties, body):
	global style
	global i
	global i2
	global lcars_colore
    
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
    	
	LCARS_Struct.draw(style)


if __name__ == "__main__":
	channel.basic_consume(queue='',on_message_callback=callback, auto_ack=True)
	try:
		device = get_device(['--interface', 'spi', '--display', 'st7789', '--spi-port', '0', '--spi-bus-speed', '52000000', '--width', '320', '--height', '240','--mode','RGB' ])
		init()
		channel.start_consuming()
	except KeyboardInterrupt:
		pass
