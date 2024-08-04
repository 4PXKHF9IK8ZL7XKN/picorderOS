#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import statistics
import vlc

from picoscolores import *
from picosglobals import *
from objects import *
from pathlib import Path
from luma.core.virtual import viewport, snapshot, range_overlap
from luma.core.sprite_system import framerate_regulator
from luma.core import cmdline, error
from luma.core.render import canvas
from PIL import ImageFont
from datetime import timedelta

BUFFER_GLOBAL = pd.DataFrame(columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude'])
BUFFER_GLOBAL_TERMALFRAME = pd.DataFrame(columns=['Value0','Value1','Value2','Value3','Value4','Value5','Value6','Value7','Value8','Value9','Value10','Value11','Value12','Value13','Value14','Value15','Value16','Value17','Value18','Value19','Value20','Value21','Value22','Value23','Value24','Value25','Value26','Value27','Value28','Value29','Value30','Value31','Value32','Value33','Value34','Value35','Value36','Value37','Value38','Value39','Value40','Value41','Value42','Value43','Value44','Value45','Value46','Value47','Value48','Value49','Value50','Value51','Value52','Value53','Value54','Value55','Value56','Value57','Value58','Value59','Value60','Value61','Value62','Value63','timestamp','latitude','longitude'])
BUFFER_GLOBAL_EM = pd.DataFrame(columns=['ssid','signal','quality','frequency','encrypted','channel','dev','mode','dsc','timestamp','latitude','longitude'])

bme680_temp = [0]

styles = ["type1", "multi_graph", "termal_view", "video_playback","type3", "type4"]
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
vlc_instance = None

lcars_microfont = None
lcars_littlefont = None
lcars_font = None
lcars_titlefont = None
lcars_bigfont = None
lcars_giantfont = None

def lcars_element_videoframe(device, draw,pos_ax,pos_ay,pos_bx,pos_by,file,option):
	fill = "yellow"
	fill2 = "red"
	offset = 0
	sensor_legende = ""
	global vlc_instance

	global lcars_microfont
		
	#bounding box
	box_element_graph = [(pos_ax , pos_ay), (pos_bx, pos_by)] 
	draw.rectangle(box_element_graph,fill="black", outline=lcars_theme[lcars_theme_selection]["colore5"])
	
	print("VLC",type(vlc_instance))
	
	if vlc_instance is None:		
		vlc_instance = vlc.Instance('--no-xlib --quiet')
		print("pass")
		player = vlc_instance.media_player_new()
		media = vlc_instance.media_new("./assets/ekmd.m4v")
		player.set_media(media)
		player.play()

def lcars_element_graph(device, draw,pos_ax,pos_ay,pos_bx,pos_by, sensors_dict,mode):
	fill = "yellow"
	fill2 = "red"
	offset = 0
	sensor_legende = ""

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
			#print("index of array", mysensor_array)
				
			# This draws my dots
			for index, data_point in enumerate(recent):
			
				range_of_graph = mysensor_array[2] - mysensor_array[1]
				graph_hight = pos_by - pos_ay				
					
				if mode == 1:
					grap_y_multi = graph_hight / range_of_graph
				else:
					grap_y_multi = graph_hight / range_of_graph
					
					print("graph;", range_of_graph,graph_hight,grap_y_multi, sensor_dsc )
					# this happens for exampe in the Generrators with +-100 min max vaules
					if mysensor_array[1] < -1:
						#print("is negativ", mysensor_array[1], sensor_dsc)
						offset = pos_ay*0.05 + mysensor_array[1] * grap_y_multi
			

				
				#draw.ellipse([pos_bx*0.99-index*graph_resulutio_X_multi,pos_by-grap_y_multi * data_point,pos_bx*0.99+2-index*graph_resulutio_X_multi,pos_by-grap_y_multi * data_point+2],lcars_colores[index_a]['value'], outline = lcars_colores[index_a]['value'])
				
				
				if len(recent) > 1:
					older_data_point = recent[index - 1]
					
					if mode == 1:
						draw.line([pos_bx*0.99-(index - 1)*graph_resulutio_X_multi,pos_by-older_data_point,pos_bx*0.99-(index - 1)*graph_resulutio_X_multi,pos_by-older_data_point,pos_bx*0.99-index*graph_resulutio_X_multi,pos_by-data_point,pos_bx*0.99-index*graph_resulutio_X_multi,pos_by+-data_point],fill=lcars_colores[index_a]['value'])
					else:
						draw.line([pos_bx*0.99-(index - 1)*graph_resulutio_X_multi,offset+pos_by-grap_y_multi * older_data_point,pos_bx*0.99-(index - 1)*graph_resulutio_X_multi,offset+pos_by-grap_y_multi * older_data_point,pos_bx*0.99-index*graph_resulutio_X_multi,offset+pos_by-grap_y_multi * data_point,pos_bx*0.99-index*graph_resulutio_X_multi,offset+pos_by-grap_y_multi * data_point],fill=lcars_colores[index_a]['value'])
					
					
					
				
			# This Displays the Sensor Naming on the Left
			draw.text((pos_ax, pos_ay+index_a*(device.height * 0.055)), text=str(sensor_dsc), font=lcars_microfont, fill=lcars_colores[index_a]['value'])
			
			# This Displays the Sensor Legende on the Right Top
			draw.text((pos_bx*0.95-index_a*(device.height * 0.1), pos_ay), text=str(mysensor_array[2]), font=lcars_microfont, fill=lcars_colores[index_a]['value'])
			
			# This Displays the Sensor Legende on the Right Bottom
			draw.text((pos_bx*0.95-index_a*(device.height * 0.1), pos_by*0.92), text=str(mysensor_array[1]), font=lcars_microfont, fill=lcars_colores[index_a]['value'])
			

			sensor_legende = '{0}{1}'.format(round(mysensor_array[0]),mysensor_array[4])

			# This Displays the Sensor Legende Bottom
			draw.text((pos_ax+index_a*(device.height * 0.25), pos_by), text=str(sensor_legende), font=lcars_microfont, fill=lcars_colores[index_a]['value'])
			
			#print("bufferinframe", len(recent))




def lcars_element_termal_array(device, draw,pos_ax,pos_ay,pos_bx,pos_by):
	fill = "yellow"
	fill2 = "red"
	offset = 0
	sensor_legende = ""

	global lcars_microfont
	global BUFFER_GLOBAL_TERMALFRAME
	
		
	# Cacluate the element lengh we interpolate a frame in between
	array_resulutio_X = ( pos_bx - pos_ax ) / 17
	array_resulutio_Y = ( pos_by - pos_ay ) / 17

	#bounding box
	box_element_graph = [(pos_ax , pos_ay), (pos_bx, pos_by)] 
	draw.rectangle(box_element_graph,fill="black", outline=lcars_theme[lcars_theme_selection]["colore5"])
	
	result = BUFFER_GLOBAL_TERMALFRAME
	#print("RESULT")
	#print(result)
    
	# trim it to length (num).
	trimmed_data = result.tail(1)	
	data_line = trimmed_data.values.tolist()
	pure_dataline = data_line[0][:63]
	avarage_temp = math.ceil(statistics.mean(pure_dataline)*2)
	interpolatet_array = [(0,avarage_temp,avarage_temp*2)]
	
	# building a full blue frame as rendering step 1
	for fullarray in range(0,289,1):
		interpolatet_array.append((0,avarage_temp,avarage_temp*2))
		
	mask_counter_A = 0
	mask_counter_B = 0
	mask_counter_C = 0
	mask_on = False
	data_line_index = 0
	# this is a range for to sensor value 
	stepping = 255 / 80
	# setting now the pixels from the sensor values translatet to colores with red more and blue less 
	# trying to center my pixels here to get it not to mutch washed out 
	for array_index ,pixel_off_pic in enumerate(interpolatet_array):
		# Masking Top and Bottom
		# carefull this values a pixel counter and i calculatet so that i get a centert array of 64 pixels with a space in between
		if array_index >= 0 and array_index < 272:
			# Masking Left and Right and defining my rows again
			if mask_counter_A <= 16 and  mask_counter_A >= 0:	
				#interpolatet_array[array_index] = '#00ff00'								
				if mask_on:				
					if mask_counter_B % 2 != 0:	
						interpolatet_array[array_index] = '#ff0000'			
						#print("my real pixels",math.ceil(data_line[0][data_line_index]))
						colore_builder_part1 = data_line[0][data_line_index] *2 * stepping
						# this is more or less percentage of temp to value
						colore_builder_part1 = math.ceil(colore_builder_part1 )
						colore_builder_part2 = 255 - math.ceil(colore_builder_part1 / 4)
						colore_builder = (200,colore_builder_part1,colore_builder_part2)
						#print("colore_int", colore_builder  )
						# this section sets the colore of the pixels around the main sensor value
						interpolatet_array[array_index+1] = (0,math.ceil(colore_builder_part1*1),math.ceil(colore_builder_part2*1))
						interpolatet_array[array_index-1] = (0,math.ceil(colore_builder_part1*1),math.ceil(colore_builder_part2*1))
						interpolatet_array[array_index+17] = (0,math.ceil(colore_builder_part1*1),math.ceil(colore_builder_part2*1))
						interpolatet_array[array_index-17] = (0,math.ceil(colore_builder_part1*1),math.ceil(colore_builder_part2*1))
						interpolatet_array[array_index+16] = (0,math.ceil(colore_builder_part1*1),math.ceil(colore_builder_part2*1))
						interpolatet_array[array_index-16] = (0,math.ceil(colore_builder_part1*1),math.ceil(colore_builder_part2*1))
						interpolatet_array[array_index+18] = (0,math.ceil(colore_builder_part1*1),math.ceil(colore_builder_part2*1))
						interpolatet_array[array_index-18] = (0,math.ceil(colore_builder_part1*1),math.ceil(colore_builder_part2*1))
						interpolatet_array[array_index] = colore_builder
						#interpolatet_array[array_index] = '#ff0000'
						data_line_index = data_line_index + 1				
				mask_counter_B = mask_counter_B + 1			
			mask_counter_A = mask_counter_A + 1
			if mask_counter_A == 17:
				mask_counter_A = 0
				mask_counter_B = 0
				
				mask_counter_C = mask_counter_C + 1
				if mask_counter_C == 1:
					if mask_on == False:
						mask_on = True
					elif mask_on == True:
						mask_on = False
					mask_counter_C = 0
					
	
	
	# Drawing the Array
	pixel_counter = 0
	for index1_X , columns in enumerate(range(0,17,1)):	
		for index2_Y, rows in enumerate(range(0,17,1)):
			draw.rectangle((pos_ax+index1_X*array_resulutio_X , pos_ay+index2_Y*array_resulutio_Y,pos_ax+index1_X*array_resulutio_X+array_resulutio_X ,pos_ay+index2_Y*array_resulutio_Y+array_resulutio_Y),fill=interpolatet_array[pixel_counter], outline=interpolatet_array[pixel_counter])
			pixel_counter = pixel_counter + 1
			
			
	
	

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
		#sensors_array_with_dict = [{"BME680":"Thermometer"},{"BME680":"Hygrometer"},{"BME680":"Barometer"},{"BME680":"VOC"},{"BME680":"ALT"}]
		sensors_array_with_dict = [{"BME680":"Barometer"},{"GENERATORS":"SineWave"}]
		#sensors_array_with_dict = [{"GENERATORS":"SineWave"},{"GENERATORS":"CosWave"},{"GENERATORS":"SineWave2"}]
		lcars_element_graph(device, draw,device.width*0.15,device.height*0.12,device.width*0.95,device.height*0.85, sensors_array_with_dict, 0)
           
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
		
		draw.rectangle((device.width*0.7 ,device.height*0.01, device.width*0.93, device.height*0.06), fill=lcars_theme[lcars_theme_selection]["colore5"], outline=lcars_theme[lcars_theme_selection]["colore5"])
		
		bottom_line = [(device.width*0.27 , device.height*0.93), (device.width*0.93, device.height*0.93+radius)] 
		
		draw.rectangle(bottom_line,lcars_theme[lcars_theme_selection]["colore5"])
	
		## Looks like i found my overlapping box
		text = "Multi   Graph"
		left, top, right, bottom = draw.textbbox((0, 0), text)
		w, h = right - left, bottom+5 - top
		w3 = device.width*0.7

		left = w3-radius*2.5
		top = -2
		draw.rectangle((left - 1, top, left + w + 1, top + h), fill="black", outline="black")
		draw.text((left + 1, top), text=text, font=lcars_littlefont, fill=lcars_theme[lcars_theme_selection]["font0"])
		
def lcars_termal_view_build():
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
		#sensors_array_with_dict = [{"BME680":"Thermometer"},{"BME680":"Hygrometer"},{"BME680":"Barometer"},{"BME680":"VOC"},{"BME680":"ALT"}]
		#sensors_array_with_dict = [{"BME680":"Barometer"},{"GENERATORS":"SineWave"}]
		#sensors_array_with_dict = [{"GENERATORS":"SineWave"},{"GENERATORS":"CosWave"},{"GENERATORS":"SineWave2"}]
		lcars_element_termal_array(device, draw,device.width*0.15,device.height*0.12,device.width*0.95,device.height*0.85)
           
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
		
		draw.rectangle((device.width*0.7 ,device.height*0.01, device.width*0.94, device.height*0.06), fill=lcars_theme[lcars_theme_selection]["colore5"], outline=lcars_theme[lcars_theme_selection]["colore5"])
		
		bottom_line = [(device.width*0.27 , device.height*0.93), (device.width*0.93, device.height*0.93+radius)] 
		
		draw.rectangle(bottom_line,lcars_theme[lcars_theme_selection]["colore5"])
	
		## Looks like i found my overlapping box
		text = "Termal  View"
		left, top, right, bottom = draw.textbbox((0, 0), text)
		w, h = right - left, bottom+5 - top
		w3 = device.width*0.7

		left = w3-radius*2.5
		top = -2
		draw.rectangle((left - 1, top, left + w + 6, top + h), fill="black", outline="black")
		draw.text((left + 1, top), text=text, font=lcars_littlefont, fill=lcars_theme[lcars_theme_selection]["font0"])		
		
def lcars_videoplayer_build():
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
		#sensors_array_with_dict = [{"BME680":"Thermometer"},{"BME680":"Hygrometer"},{"BME680":"Barometer"},{"BME680":"VOC"},{"BME680":"ALT"}]
		#sensors_array_with_dict = [{"BME680":"Barometer"},{"GENERATORS":"SineWave"}]
		#sensors_array_with_dict = [{"GENERATORS":"SineWave"},{"GENERATORS":"CosWave"},{"GENERATORS":"SineWave2"}]
		file = '/home/christian/video/file.mkv'
		option = 'play'
		lcars_element_videoframe(device, draw,device.width*0.15,device.height*0.12,device.width*0.95,device.height*0.85,file,option)
           
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
		
		draw.rectangle((device.width*0.7 ,device.height*0.01, device.width*0.94, device.height*0.06), fill=lcars_theme[lcars_theme_selection]["colore5"], outline=lcars_theme[lcars_theme_selection]["colore5"])
		
		bottom_line = [(device.width*0.27 , device.height*0.93), (device.width*0.93, device.height*0.93+radius)] 
		
		draw.rectangle(bottom_line,lcars_theme[lcars_theme_selection]["colore5"])
	
		## Looks like i found my overlapping box
		text = "Video Playback"
		left, top, right, bottom = draw.textbbox((0, 0), text)
		w, h = right - left, bottom+5 - top
		w3 = device.width*0.7

		left = w3-radius*2.5
		top = -2
		draw.rectangle((left - 1, top, left + w + 6, top + h), fill="black", outline="black")
		draw.text((left + 1, top), text=text, font=lcars_littlefont, fill=lcars_theme[lcars_theme_selection]["font0"])		


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
		elif self == "termal_view":
			lcars_termal_view_build()   
		elif self == "video_playback":
			lcars_videoplayer_build()     
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
	global BUFFER_GLOBAL_TERMALFRAME
	global GPS_DATA
	global BME680
	global SYSTEMVITALES
	global GENERATORS
	global SENSEHAT
	global TERMALFRAME
	
	#print('book=', mapping_book_byname)
	#print('populating=', method.routing_key)
	
	timestamp = time.time()
	value = random.randint(1, 100) 
	#sensors = Sensor()
	fragdata = []
	fragdata_termal = []
	sensor_values = []
	trimmbuffer_flag = False
	trimmbuffer_flag_termal = False
	
		
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
		sensor_values = body.decode()	
		sensor_frame = ast.literal_eval(sensor_values)
		#print("TERMALFRAME:", sensor_frame)
		index = 0
		
		for sensor_array_line in sensor_frame:
			for datapoint in sensor_array_line:
				TERMALFRAME[index] = float(datapoint)
				index = index + 1
	
		TERMALFRAME[64] = timestamp
		TERMALFRAME[65] = GPS_DATA[0]
		TERMALFRAME[66] = GPS_DATA[1]

		#print("MATRIX", TERMALFRAME)
		fragdata_termal.append(TERMALFRAME)		
		# creates a new dataframe to add new data 	
		newdata = pd.DataFrame(fragdata_termal, columns=['Value0','Value1','Value2','Value3','Value4','Value5','Value6','Value7','Value8','Value9','Value10','Value11','Value12','Value13','Value14','Value15','Value16','Value17','Value18','Value19','Value20','Value21','Value22','Value23','Value24','Value25','Value26','Value27','Value28','Value29','Value30','Value31','Value32','Value33','Value34','Value35','Value36','Value37','Value38','Value39','Value40','Value41','Value42','Value43','Value44','Value45','Value46','Value47','Value48','Value49','Value50','Value51','Value52','Value53','Value54','Value55','Value56','Value57','Value58','Value59','Value60','Value61','Value62','Value63','timestamp','latitude','longitude'])
		BUFFER_GLOBAL_TERMALFRAME = pd.concat([BUFFER_GLOBAL_TERMALFRAME,newdata]).drop_duplicates().reset_index(drop=True)
		# we get len of one sensor					
		currentsize_termalframe = len(BUFFER_GLOBAL_TERMALFRAME)
		if currentsize_termalframe > targetsize:
			trimmbuffer_flag_termal = True		


	# PD Fails to handel over 1650 rows so we trim the buffer when 64 rows on any sensor gets reached
	if trimmbuffer_flag:
			BUFFER_GLOBAL = trimbuffer(targetsize,'global')
			
	if trimmbuffer_flag_termal:
			BUFFER_GLOBAL_TERMALFRAME = trimbuffer(targetsize,'termal')		
			
	return


def trimbuffer(targetsize,buffername):
	# should take the buffer in memory and trim some of it
	if buffername == 'global':
		targetsize_all_sensors = targetsize * configure.max_sensors[0]
	elif buffername == 'termal':
		targetsize_all_sensors = targetsize * 1
		
	#print("Target Size",targetsize )
	
	#print("targetsize_all_sensors ",targetsize_all_sensors )
	
	# get buffer size to determine how many rows to remove from the end
	if buffername == 'global':
		currentsize = len(BUFFER_GLOBAL) 
	elif buffername == 'termal':
		currentsize = len(BUFFER_GLOBAL_TERMALFRAME) 
	#print("currentsize", currentsize)

	# determine difference between buffer and target size
	length = currentsize - targetsize_all_sensors
	
	#print("length", length)


	# make a new dataframe of the most recent data to keep using
	if buffername == 'global':
		newbuffer = BUFFER_GLOBAL.tail(targetsize_all_sensors)
	elif buffername == 'termal':
		newbuffer = BUFFER_GLOBAL_TERMALFRAME.tail(targetsize_all_sensors)

	# slice off the rows outside the buffer and backup to disk
	if buffername == 'global':
		tocore = BUFFER_GLOBAL.head(length)
	elif buffername == 'termal':
		tocore_termal = BUFFER_GLOBAL_TERMALFRAME.head(length)

	if buffername == 'global':
		if configure.datalog[0]:
				append_to_core(tocore)
	elif buffername == 'termal':
		if configure.datalog[0]:
				append_to_core(tocore_termal)

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
