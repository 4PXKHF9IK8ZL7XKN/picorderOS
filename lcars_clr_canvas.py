#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2023 Richard Hull and contributors
# See LICENSE.rst for details.
# PYTHON_ARGCOMPLETE_OK

"""
Unicode font rendering & scrolling.
"""
import math
import random
import time
import colorsys
from pathlib import Path
from luma.core.virtual import viewport, snapshot, range_overlap
from luma.core.sprite_system import framerate_regulator
from luma.core import cmdline, error
from luma.core.render import canvas
from PIL import ImageFont

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
lcars_orange = (255,153,0)
lcars_pink = (204,153,204)
lcars_blue = (153,153,208)
lcars_red = (204,102,102)
lcars_peach = (255,204,153)
lcars_bluer = (153,153,255)
lcars_orpeach = (255,153,102)
lcars_pinker = (204,102,153)
lcars_grid = (47,46,84)




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

def lcars_type1_build():
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
        
def lcars_type2_build(lcars_colore):
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

        draw.text((device.width*0.2, device.height*0.25), "Accessing",font=lcars_giantfont ,fill=lcars_peach)

def lcars_type3_build(lcars_colore):
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
            lcars_type3_build("blue")
        elif self == "type1":
            lcars_type3_build("yellow")
        elif self == "type2":
            lcars_type3_build("green")    
        elif self == "type3":
            lcars_type3_build("red")              
        elif self == "type4":
            with canvas(device, dither=True) as draw:
                draw.rectangle((100, 8, 100 + 1, 33 + 1), fill=(255, 255, 0))
        
        



def main():
    effects = ["type0","type1", "type2", "type3"]

    effect = "type1"
    i = 0
    regulator = framerate_regulator(fps=30)
    
    while True:
        with regulator:    
            for i in range(20):
                LCARS_Struct.draw(effect)
                if i >= 19:
                    effect = effects.pop()
                    effects.insert(0, effect)
                    i = 0
            


if __name__ == "__main__":
    try:
        device = get_device(['--interface', 'spi', '--display', 'st7789', '--spi-port', '0', '--spi-bus-speed', '52000000', '--width', '320', '--height', '240','--mode','RGB' ])
        main()
    except KeyboardInterrupt:
        pass
