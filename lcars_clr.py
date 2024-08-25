#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

"""
Unicode font rendering & scrolling.
"""
import os
import os.path
import tempfile
import sys
import math
import random
import time
import colorsys
import threading
import pika
import ast
import statistics
import vlc
import numpy as np

from picoscolores import *
from picosglobals import *
from picosvideoplayer import *
from objects import *
from pathlib import Path
from luma.core.virtual import viewport, snapshot, range_overlap
from luma.core.sprite_system import framerate_regulator
from luma.core import cmdline, error
from luma.core.render import canvas
from PIL import ImageFont
from datetime import timedelta
from colour import Color

import psycopg2
from picos_psql_config import load_config

from scipy.interpolate import griddata

bme680_temp = [0]

#styles = [ "multi_graph","termal_view"]
#styles = ["type1", "multi_graph", "termal_view", "video_playback","type3", "type4"]
styles = ["termal_view","multi_graph","wifi_band_view"]
style = "type1"
i = 0
i2 = 0

# A Timer to as Frameratecontroller
WAIT_TIME_SECONDS = 0.1

animation_step = 0
sensor_animation = 0
lcars_theme_selection = 0

tmp_dirpath = tempfile.mkdtemp()
os.chmod(tmp_dirpath , 0o777)

selected_sensor_values = [["local","BME680","Barometer"],["local","GENERATORS","SineWave"],["local","BME680","Thermometer"]]
#selected_sensor_values = [["local","BME680","Barometer"],["local","GENERATORS","SineWave"],["local","BME680","Thermometer"],["local","APDS9960","proximity"]]
#selected_sensor_values = [["local","GENERATORS","SineWave"]]

vlc_instance = None

lcars_microfont = None
lcars_littlefont = None
lcars_font = None
lcars_titlefont = None
lcars_bigfont = None
lcars_giantfont = None

def lcars_element_videoframe(device, draw, pos_ax,pos_ay,pos_bx,pos_by,filename,option):
	# this element needs to be on top so no canvase can be used here

	fill = "yellow"
	fill2 = "red"
	offset = 0
	sensor_legende = ""
	global vlc_instance
	global tmp_dirpath
	global lcars_microfont
	
	filename = "/home/christian/projekt/picorderOS/assets/Firestorm Reveal Trailer.mp4"
	
	#print("VLC",type(vlc_instance))
	
	if vlc_instance is None:		
		#vlc_instance = vlc.Instance('--no-xlib --vout=yuv --yuv-yuv4mpeg2 --yuv-file="{}/stream.yuv"'.format(tmp_dirpath)  )
		vlc_instance = vlc.Instance('--no-xlib --no-video')
		player = vlc_instance.media_player_new()
		#media = vlc_instance.media_new("./assets/ekmd.m4v")
		media = vlc_instance.media_new("./assets/Firestorm Reveal Trailer.mp4")
		player.set_media(media)
		player.play()
		
		frame_x = int(pos_bx - pos_ax)
		frame_y = int(pos_by - pos_ay)	
		
		videoplayer_frame(device, draw, pos_ax,pos_ay,pos_bx,pos_by,filename)
		player.release()

def lcars_element_graph(device, draw,pos_ax,pos_ay,pos_bx,pos_by, sensors_dict,mode):
	# mode is auto scalling depending on min max
	fill = "yellow"
	fill2 = "red"
	offset = 0
	sensor_legende = ""
	mode = 1
	center_line = True
	offset_line = True
	draw_dots = False
	draw_lines = True
	display_current_avr = False
	decimal = 2
	style_dots = False
	radius = 4
	line_thicknes = 1

	global lcars_microfont

	if configure.samples:
		samples = configure.samples
	else:
		samples = 64
		
	time_lengh = 60

	#bounding box
	box_element_graph = [(pos_ax , pos_ay), (pos_bx, pos_by)] 
	draw.rectangle(box_element_graph,fill="black", outline=lcars_theme[lcars_theme_selection]["colore5"])
	
	# center line
	if center_line:
		calc_center_of_graph = pos_ay+(pos_by - pos_ay)/2
		centerline_element_graph = [(pos_ax,calc_center_of_graph),(pos_bx,calc_center_of_graph)] 
		draw.line(centerline_element_graph,fill=lcars_theme[lcars_theme_selection]["colore5"])
	
	# Unpacking the array with with array
	for index_a, sensors_to_read in enumerate(sensors_dict):
		# dev is the Pi dsc the cpu, location_tag is a name of the sending device like local remote or tric2351

		# by setting up all sensor values with a timestamp , can we now select the time section to watch , and ask get recent for example for the last minute
		location_tag,sensor_dev,sensor_dsc = sensors_to_read

		# calling for the data set
		recent, elements_forgieventime = get_recent(location_tag, sensor_dev, sensor_dsc, time_lengh)
		if type(recent) != bool and len(recent) != 0:
		
			sensor_min = min(recent)
			sensor_max = max(recent)
			sensor_avr = statistics.mean(recent)
		
			if elements_forgieventime == 0:
				elements_forgieventime = 60
				
			# (calulation the graph lengh absulut) deviding through tha samples to get the steps of drawing 
			graph_resulutio_X_multi = ( pos_bx - pos_ax ) / elements_forgieventime
			
			
			# This Block checks for the global variable that defines the sensor end selects the array inside so that i can get the min max values 
			my_global_vars = globals()
			for index_b, array_tosearch in enumerate(my_global_vars[sensor_dev]):
				if array_tosearch[3] == sensor_dsc:
					# getting the global defined stats for the sensor
					mysensor_array = my_global_vars[sensor_dev][index_b]

				
				
					# This draws my dots
					for index, data_point in enumerate(recent):		
				
						# Defining my Graph
						range_of_graph = mysensor_array[2] - mysensor_array[1]
						graph_hight = pos_by - pos_ay	
						grap_y_multi = graph_hight / range_of_graph		
																	
							
						if mode == 1:
							# autoscale on
							range_of_graph = sensor_max - sensor_min
							
							# catch devision by 0
							if range_of_graph == 0:
								grap_y_multi = graph_hight
							else:	
							    grap_y_multi = graph_hight / range_of_graph
							
							if sensor_min < -1:
								offset = ( sensor_min * grap_y_multi ) * -1
						else:
							if mysensor_array[1] < -1:
								offset = (mysensor_array[1] * grap_y_multi) * -1
								
								
						# center line
						if offset_line:
							calc_offset_line_of_graph = pos_by*0.99-(offset)							
							offset_line_element_graph = [(pos_ax,calc_offset_line_of_graph),(pos_bx,calc_offset_line_of_graph)] 
							draw.line(offset_line_element_graph,fill=lcars_colores[index_a]['value'])
						
						
						# when we dont have negativ values do we need to use the indexer inbetween to not overscale
						data_unit_index = sensor_max - data_point
						if len(recent) > 1:
							older_data_point = recent[index - 1]						
							older_data_unit_index = sensor_max - older_data_point
						
						if offset == 0:
							point_in_graph = data_unit_index * grap_y_multi
							if len(recent) > 1:
								older_point_in_graph = older_data_unit_index * grap_y_multi
						else:
							point_in_graph = data_point * grap_y_multi
							if len(recent) > 1:
								older_point_in_graph = older_data_point * grap_y_multi
					
	
								
						xmovement = pos_bx*0.99-(index - 1)*graph_resulutio_X_multi
						ymovement = pos_by*0.99-(offset+point_in_graph)
						if len(recent) > 1:
							older_xmovement = pos_bx*0.99-(index - 2)*graph_resulutio_X_multi
							older_ymovement = pos_by*0.99-(offset+older_point_in_graph)
						else:
							print("NO Data")
							older_xmovement = pos_bx*0.99
							older_ymovement = pos_by*0.99
							
						if draw_dots:

							if style_dots: 
								draw.rectangle(
									[xmovement,
									ymovement,
									xmovement+radius,
									ymovement+radius],
								fill = lcars_colores[index_a]['value'], outline = lcars_colores[index_a]['value'])
							else:								
								draw.ellipse(
									[xmovement,
									ymovement,
									xmovement+radius,
									ymovement+radius],
								fill = lcars_colores[index_a]['value'], outline = lcars_colores[index_a]['value'])
							
	
						
						if draw_lines:
							draw.line(
								[older_xmovement,
								older_ymovement,
							
								older_xmovement+line_thicknes,
								older_ymovement+line_thicknes,
							
								xmovement,
								ymovement,
							
								xmovement+line_thicknes,
								ymovement+line_thicknes],
							
							fill=lcars_colores[index_a]['value'])
	
					
					# This Displays the Sensor Naming on the Left
					draw.text((pos_ax, pos_ay+index_a*(device.height * 0.055)), text=str(sensor_dsc), font=lcars_microfont, fill=lcars_colores[index_a]['value'])
					
					# This Displays the Sensor Legende on the Right Top
					if mode == 1:
						draw.text((pos_bx*0.95-index_a*(device.height * 0.1), pos_ay), text=str(round(sensor_max)), font=lcars_microfont, fill=lcars_colores[index_a]['value'])
					else:
						draw.text((pos_bx*0.95-index_a*(device.height * 0.1), pos_ay), text=str(mysensor_array[2]), font=lcars_microfont, fill=lcars_colores[index_a]['value'])
						
						
					# This Displays the Sensor Legende on the Right Bottom
					if mode == 1:
						draw.text((pos_bx*0.95-index_a*(device.height * 0.1), pos_by*0.92), text=str(round(sensor_min)), font=lcars_microfont, fill=lcars_colores[index_a]['value'])
					else:
						draw.text((pos_bx*0.95-index_a*(device.height * 0.1), pos_by*0.92), text=str(mysensor_array[1]), font=lcars_microfont, fill=lcars_colores[index_a]['value'])

					if display_current_avr:
						sensor_legende = '{0}{1}'.format(round(sensor_avr,decimal),mysensor_array[4])
					else:
						vaule_unpacking = recent[-1:]
						sensor_legende = '{0}{1}'.format(round(vaule_unpacking[0],decimal),mysensor_array[4])

					# This Displays the Sensor Legende Bottom
					draw.text((pos_ax+index_a*(device.height * 0.25), pos_by), text=str(sensor_legende), font=lcars_microfont, fill=lcars_colores[index_a]['value'])
						
# some utility functions for termal grid
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))


def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def lcars_element_termal_array(device, draw,pos_ax,pos_ay,pos_bx,pos_by):
	""" 
	# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
	# SPDX-License-Identifier: MIT
    Function is nearly a copy of amg88xx_rpi_thermal_cam.py from https://learn.adafruit.com/ written from tekktrik for Adafruit.
    https://github.com/adafruit/Adafruit_CircuitPython_AMG88xx/blob/main/examples/amg88xx_rpi_thermal_cam.py
    https://github.com/tekktrik
	"""

	global lcars_microfont
	
	location_tag = 'local'
	sensor_dev = 'TERMALFRAME'
	sensor_dsc = 'ARRAY'
	
	termal_matrix = []
	value_list = []
	
	MINTEMP = 26.0
	MAXTEMP = 32.0
	
	COLORDEPTH = 1024
	
	points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
	grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]
	
	points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
	grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]
	
	blue = Color("indigo")
	colors = list(blue.range_to(Color("red"), COLORDEPTH))
	# create the array of colors
	colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in colors]
		
	# Cacluate the element lengh we interpolate a frame in between	
	displayPixelWidth = ( pos_bx - pos_ax ) / 30
	displayPixelHeight = ( pos_by - pos_ay ) / 30

	#bounding box
	box_element_graph = [(pos_ax , pos_ay), (pos_bx, pos_by)] 
	draw.rectangle(box_element_graph,fill="black", outline=lcars_theme[lcars_theme_selection]["colore5"])
	
	result, elements_forgieventime = get_recent_termal(location_tag, sensor_dev, sensor_dsc)
	#print("result",result)
	if type(result) != bool and len(result) != 0:
		for value in result:
			value_list.append(value)
		termal_matrix = list(chunks(value_list, 8))
		
		pixels = []
		for row in termal_matrix:
			pixels = pixels + row
		pixels = [map_value(p, MINTEMP, MAXTEMP, 0, COLORDEPTH - 1) for p in pixels]
		
		# perform interpolation
		bicubic = griddata(points, pixels, (grid_x, grid_y), method="cubic")
    	
		# draw everything
		for index1_X, row in enumerate(bicubic):
			for index2_Y, pixel in enumerate(row):
				#print("drawing row", index1_X,"zeile", index2_Y," row data" , row, "pixel" , pixel )
				draw.rectangle((
				pos_ax+index1_X*displayPixelWidth , 
				pos_ay+index2_Y*displayPixelHeight,
				pos_ax+index1_X*displayPixelWidth+displayPixelWidth ,
				pos_ay+index2_Y*displayPixelHeight+displayPixelHeight),
				colors[constrain(int(pixel), 0, COLORDEPTH - 1)])


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

def lcars_element_elbow_half(device, draw,pos_x,pos_y,rotation,colore):
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
		Rshape0 = [(pos_x, pos_y ), (pos_x+device.width*0.23, pos_y+device.height*0.025)]
		Rshape1 = [(pos_x+device.width*0.25/2, pos_y+radius/2), (pos_x+device.width*0.26, pos_y+device.height*0.1)]
		shape0 = [(pos_x+device.width*0.2+radius/2,  pos_y), (pos_x+device.width*0.2+radius+radius/2, pos_y+radius)]
	
		# masking
		shape1 = [(pos_x+device.width*0.25/2-radius/2,  pos_y+radius-device.height*0.015), (pos_x+device.width*0.25/2+radius, pos_y+radius*2+device.height*0.01)]
		Rshape2 = [(pos_x+device.width*0.25/2-radius/2,  pos_y+radius+device.height*0.03), (pos_x+device.width*0.25/2+radius, pos_y+radius*2)]
	elif rotation == 1:
		# Main Shape
		Rshape0 = [(pos_x, pos_y+radius*2 ), (pos_x+device.width*0.23, pos_y+device.height*0.05+radius*1.5)]
		Rshape1 = [(pos_x+device.width*0.25/2, pos_y+radius/2), (pos_x+device.width*0.26, pos_y+device.height*0.1)]
		shape0 = [(pos_x+device.width*0.2+radius/2,  pos_y+radius*1.5), (pos_x+device.width*0.2+radius+radius/2, pos_y+radius+radius*1.5)]
		
	# this is when the shape0 got down	
		# masking
		shape1 = [(pos_x+device.width*0.25/2-radius/2,  pos_y+radius/2), (pos_x+device.width*0.25/2+radius, pos_y+radius+radius*0.9)]
		Rshape2 = [(pos_x+device.width*0.25/2-radius/2,  pos_y+radius/2), (pos_x+device.width*0.25/2+radius, pos_y+radius)]

	# This is wehen the left is rounded
	elif rotation == 2:
		Rshape0 = [(pos_x+radius/2, pos_y ), (pos_x+device.width*0.23+radius/2, pos_y+device.height*0.025)] # <--- changed pos_y+device.height*0.05
		Rshape1 = [(pos_x, pos_y+radius/2), (pos_x+device.width*0.25/2, pos_y+device.height*0.1)]
		shape0 = [(pos_x,  pos_y), (pos_x+radius, pos_y+radius)]
		
		# masking
		shape1 = [(pos_x+device.width*0.25/2-radius/2,  pos_y+radius-device.height*0.02), (pos_x+device.width*0.25/2+radius, pos_y+radius*2-device.height*0.02)] # <--- changed +device.height*0.01
		Rshape2 = [(pos_x+device.width*0.25/2-radius/2,  pos_y+radius+device.height*0.01), (pos_x+device.width*0.25/2+radius, pos_y+radius*2)]
	elif rotation == 3:
		Rshape0 = [(pos_x+radius/2, pos_y +radius*2), (pos_x+device.width*0.23+radius/2, pos_y+device.height*0.05+radius*1.5)]
		Rshape1 = [(pos_x, pos_y+radius/2), (pos_x+device.width*0.25/2, pos_y+device.height*0.1)]
		shape0 = [(pos_x,  pos_y+radius*1.5), (pos_x+radius, pos_y+radius+radius*1.5)]
	# this is when the shape0 got down	
		# masking
		shape1 = [(pos_x+device.width*0.25/2-radius/2,  pos_y+radius/2), (pos_x+device.width*0.25/2+radius, pos_y+radius+radius*0.9)]
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
    
	radius = device.height*0.05
	mid_value = (posb_y - pos_y) /2 
	

	Rshape_doublebar0 = [(pos_x, pos_y ), (posb_x, pos_y+mid_value*0.8)]
	Rshape_doublebar1 = [(pos_x, pos_y+mid_value*1.2 ), (posb_x, posb_y)]
	
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


# Init rabbitmq connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='sensor_data', exchange_type='topic')

result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue

# We request now all Sensor data and Rabbitmq values to make the graph drawing realy valuable 
channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='EVENT')
    
channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='system_vitals')


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
	
	global selected_sensor_values

	fill2 = "black"
	fill3 = "yellow"
	
	dict_graph = []

	with canvas(device, dither=True) as draw:
					
		lcars_element_elbow(device, draw, device.width*0.01,device.height*0.01,2,lcars_theme[lcars_theme_selection]["colore4"])
		lcars_element_elbow(device, draw, device.width*0.01,device.height*0.86 ,3, lcars_theme[lcars_theme_selection]["colore0"])	
		
		# selecting Values in Pandas DB via dev & dsc
		#selected_sensor_values = [{"BME680":"Thermometer"},{"BME680":"Hygrometer"},{"BME680":"Barometer"},{"BME680":"VOC"},{"BME680":"ALT"}]
		#selected_sensor_values = [{"BME680":"Barometer"},{"GENERATORS":"SineWave"},{"BMP280":"Thermometer"}]
		#selected_sensor_values = [{"GENERATORS":"SineWave"},{"GENERATORS":"CosWave"},{"GENERATORS":"SineWave2"}]
		lcars_element_graph(device, draw,device.width*0.15,device.height*0.12,device.width*0.95,device.height*0.85, selected_sensor_values, 0)
           
		radius = device.height*0.05
          
        #end locations
		w0, h0 = device.width*0.01, device.height*0.41
		w1, h1 = device.width*0.22/2, device.height*0.865
        
		Rshape0 = [(w0,  h0), (w1, h1)]
        
		# the connecting from top to bottom
		draw.rectangle(Rshape0, lcars_theme[lcars_theme_selection]["colore5"])

		if sensor_animation == 3:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.13 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.13 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		if sensor_animation == 2:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.20 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.20 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		if sensor_animation == 1:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.274 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.274 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		if sensor_animation == 0:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.345 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.345 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		lcars_element_end(device, draw, device.width*0.93,device.height*0.015,3,lcars_theme[lcars_theme_selection]["colore0"])
		lcars_element_end(device, draw, device.width*0.93,device.height*0.93,3,lcars_theme[lcars_theme_selection]["colore0"])
		
		lcars_element_doublebar(device, draw, device.width*0.27 ,device.height*0.01, device.width*0.5, device.height*0.06,0,lcars_theme[lcars_theme_selection]["colore0"],lcars_theme[lcars_theme_selection]["colore5"])
		lcars_element_doublebar(device, draw, device.width*0.51 ,device.height*0.01, device.width*0.60, device.height*0.06,0,lcars_theme[lcars_theme_selection]["colore5"],lcars_theme[lcars_theme_selection]["colore0"])
		
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
		
		lcars_element_termal_array(device, draw,device.width*0.15,device.height*0.12,device.width*0.95,device.height*0.85)
           
		radius = device.height*0.05
          
        #end locations
		w0, h0 = device.width*0.01, device.height*0.41
		w1, h1 = device.width*0.22/2, device.height*0.865
        
		Rshape0 = [(w0,  h0), (w1, h1)]
        
		# the connecting from top to bottom
		draw.rectangle(Rshape0, lcars_theme[lcars_theme_selection]["colore5"])

		if sensor_animation == 3:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.13 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.13 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		if sensor_animation == 2:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.20 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.20 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		if sensor_animation == 1:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.274 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.274 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		if sensor_animation == 0:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.345 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.345 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		lcars_element_end(device, draw, device.width*0.93,device.height*0.015,3,lcars_theme[lcars_theme_selection]["colore0"])
		lcars_element_end(device, draw, device.width*0.93,device.height*0.93,3,lcars_theme[lcars_theme_selection]["colore0"])
		
		lcars_element_doublebar(device, draw, device.width*0.27 ,device.height*0.01, device.width*0.5, device.height*0.06,0,lcars_theme[lcars_theme_selection]["colore0"],lcars_theme[lcars_theme_selection]["colore5"])
		lcars_element_doublebar(device, draw, device.width*0.51 ,device.height*0.01, device.width*0.60, device.height*0.06,0,lcars_theme[lcars_theme_selection]["colore5"],lcars_theme[lcars_theme_selection]["colore0"])
		
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
	
	file = '/home/christian/video/file.mkv'
	option = 'play'

	with canvas(device, dither=True) as draw:
					
		lcars_element_elbow(device, draw, device.width*0.01,device.height*0.01,2,lcars_theme[lcars_theme_selection]["colore4"])
		lcars_element_elbow(device, draw, device.width*0.01,device.height*0.86 ,3, lcars_theme[lcars_theme_selection]["colore0"])			
           
		radius = device.height*0.05
          
        #end locations
		w0, h0 = device.width*0.01, device.height*0.41
		w1, h1 = device.width*0.22/2, device.height*0.865
        
		Rshape0 = [(w0,  h0), (w1, h1)]
        
		# the connecting from top to bottom
		draw.rectangle(Rshape0, lcars_theme[lcars_theme_selection]["colore5"])

		if sensor_animation == 3:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.13 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.13 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		if sensor_animation == 2:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.20 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.20 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		if sensor_animation == 1:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.274 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.274 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		if sensor_animation == 0:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.345 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.345 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		lcars_element_end(device, draw, device.width*0.93,device.height*0.015,3,lcars_theme[lcars_theme_selection]["colore0"])
		lcars_element_end(device, draw, device.width*0.93,device.height*0.93,3,lcars_theme[lcars_theme_selection]["colore0"])
		
		lcars_element_doublebar(device, draw, device.width*0.27 ,device.height*0.01, device.width*0.5, device.height*0.06,0,lcars_theme[lcars_theme_selection]["colore0"],lcars_theme[lcars_theme_selection]["colore5"])
		lcars_element_doublebar(device, draw, device.width*0.51 ,device.height*0.01, device.width*0.60, device.height*0.06,0,lcars_theme[lcars_theme_selection]["colore5"],lcars_theme[lcars_theme_selection]["colore0"])
		
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
		
	####picosvideoplayer without canvis and overdrawing i hope
	lcars_element_videoframe(device, draw, device.width*0.15,device.height*0.12,device.width*0.95,device.height*0.85,file,option)
	
	
	
def wifi_band_view_build():
	global animation_step
	global sensor_animation
	global lcars_theme_selection
	
	global lcars_microfont
	global lcars_littlefont 
	global lcars_font
	global lcars_titlefont 
	global lcars_bigfont 
	global lcars_giantfont	

	with canvas(device, dither=True) as draw:
					
		lcars_element_elbow(device, draw, device.width*0.01,device.height*0.01,2,lcars_theme[lcars_theme_selection]["colore4"])
		lcars_element_elbow(device, draw, device.width*0.01,device.height*0.86 ,3, lcars_theme[lcars_theme_selection]["colore0"])	
		
		
		lcars_element_elbow_half(device, draw, device.width*0.01,device.height*0.30 ,3, lcars_theme[lcars_theme_selection]["colore0"])
		lcars_element_elbow_half(device, draw, device.width*0.01,device.height*0.44,2,lcars_theme[lcars_theme_selection]["colore4"]) 		
           
		radius = device.height*0.05
          
        #end locations
		w0, h0 = device.width*0.01, device.height*0.13
		w1, h1 = device.width*0.22/2, device.height*0.31
		
		w2, h2 = device.width*0.01, device.height*0.84
		w3, h3 = device.width*0.22/2, device.height*0.87
        
		Rshape0 = [(w0,  h0), (w1, h1)]
		
		Rshape1 = [(w2,  h2), (w3, h3)]
        
		# the connecting from top to bottom
		draw.rectangle(Rshape0, lcars_theme[lcars_theme_selection]["colore5"])
		
		draw.rectangle(Rshape1, lcars_theme[lcars_theme_selection]["colore5"])

		if sensor_animation == 3:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.56 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.56 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		if sensor_animation == 2:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.63 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.63 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		if sensor_animation == 1:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.70 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.70 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		if sensor_animation == 0:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.77 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.77 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		lcars_element_end(device, draw, device.width*0.93,device.height*0.015,3,lcars_theme[lcars_theme_selection]["colore0"])
		lcars_element_end(device, draw, device.width*0.93,device.height*0.93,3,lcars_theme[lcars_theme_selection]["colore0"])
		
		lcars_element_doublebar(device, draw, device.width*0.27 ,device.height*0.01, device.width*0.5, device.height*0.06,0,lcars_theme[lcars_theme_selection]["colore0"],lcars_theme[lcars_theme_selection]["colore5"])
		#lcars_element_doublebar(device, draw, device.width*0.51 ,device.height*0.01, device.width*0.60, device.height*0.06,0,lcars_theme[lcars_theme_selection]["colore5"],lcars_theme[lcars_theme_selection]["colore0"])
		
		
		lcars_element_doublebar(device, draw, device.width*0.27 ,device.height*0.40, device.width*0.5, device.height*0.465,0,lcars_theme[lcars_theme_selection]["colore0"],lcars_theme[lcars_theme_selection]["colore5"])
		lcars_element_doublebar(device, draw, device.width*0.51 ,device.height*0.40, device.width*0.60, device.height*0.465,0,lcars_theme[lcars_theme_selection]["colore5"],"black")
		lcars_element_doublebar(device, draw, device.width*0.61 ,device.height*0.40, device.width*0.99, device.height*0.465,0,lcars_theme[lcars_theme_selection]["colore0"],lcars_theme[lcars_theme_selection]["colore5"])		
		

		
		
		# Top Edge
		#draw.rectangle((device.width*0.7 ,device.height*0.01, device.width*0.94, device.height*0.06), fill=lcars_theme[lcars_theme_selection]["colore5"], outline=lcars_theme[lcars_theme_selection]["colore5"])
		
		bottom_line = [(device.width*0.27 , device.height*0.93), (device.width*0.93, device.height*0.93+radius)] 
		
		draw.rectangle(bottom_line,lcars_theme[lcars_theme_selection]["colore5"])
	
		## Looks like i found my overlapping box
		text = "EM CHANNEL ANALYSIS"
		left, top, right, bottom = draw.textbbox((0, 0), text)
		w, h = right - left, bottom+5 - top
		w3 = device.width*0.62

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
		
		#print("lcars_theme:", lcars_theme_selection)
		#print(lcars_theme[lcars_theme_selection])
		
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
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.13 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.13 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		if sensor_animation == 2:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.20 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.20 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		if sensor_animation == 1:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.274 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.274 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
		if sensor_animation == 0:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.345 ,3,lcars_theme[lcars_theme_selection]["colore1"])
		else:
			lcars_element_side_bar(device, draw, device.width*0.01,device.height*0.345 ,3,lcars_theme[lcars_theme_selection]["colore2"])
		
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
		elif self == "wifi_band_view":
			wifi_band_view_build()      
		elif self == "type3":
			lcars_type3_build()              
		elif self == "type4":
			lcars_type3_build()

  
# return a list of n most recent data from specific sensor defined by keys
# gets Called from pilgraph
def get_recent(tag, dsc, dev, time_ing):	
	timelength = 0
	clean_slices = []
	slices = False

	table_string = '%s_%s_%s' % (tag,dsc,dev)
	table_data = return_data_from_sql(psql_connection_lcars, table_string, time_ing)
	slices = table_data
	if type(table_data) != bool:
		timelength = len(table_data)
		for item in table_data:
			item_clean = float(str(item).strip("(, )"))
			clean_slices.append(item_clean)
		slices = clean_slices
	return slices, timelength    
	
def get_recent_termal(tag, dsc, dev):	
	items_count = 0
	clean_slices = []
	array_data = False

	table_string = '%s_%s_%s' % (tag,dsc,dev)
	table_data = return_data_from_sql_termal(psql_connection_lcars, table_string)	
	if type(table_data) != bool and len(table_data) != 0:
		array_data = ast.literal_eval(str(table_data[0]).strip("( )"))
		items_count = len(array_data)
	return array_data, items_count  
		

	
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
	
	if method.routing_key != 'EVENT':
		sensor_animation = sensor_animation + 0.5
		if sensor_animation == 4:
			sensor_animation = 0
			
	else:
    
		DICT = body.decode()
		DICT_CLEAN = ast.literal_eval(DICT)
		print('EVENT')		
		
		if DICT_CLEAN['geo']:
			print('EVENT - geo')	
			style = styles.pop()
			styles.insert(0, style)
			print('EVENT')
			
		if DICT_CLEAN['met']:
			print('EVENT - met')	
			lcars_theme_selection = lcars_theme_selection + 1
			if lcars_theme_selection == 3: 
				lcars_theme_selection = 0
				
	#update(ch, method, properties, body)

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


def return_data_from_sql(con, table_str, time_lengh_sec):
	ret = False
	now_time = time.time()
	time_past = now_time - time_lengh_sec 
	
	try:
		cur = con.cursor()
		cur.execute('select value from "' + table_str + '"  where timestamp > '+ str(time_past) + ' order by timestamp desc')
		values = cur.fetchall()
		ret = values
		cur.close()
	except psycopg2.Error as e:
		if e == "no results to fetch":
			print( e )
	return ret	
	
	
def return_data_from_sql_termal(con, table_str):
	ret = False
	now_time = time.time()
	time_past = now_time - 30
	
	try:
		cur = con.cursor()
		cur.execute('select val0, val1, val2, val3, val4, val5, val6, val7, val8, val9, val10, val11, val12, val13, val14, val15, val16, val17, val18, val19, val20, val21, val22, val23, val24, val25, val26, val27, val28, val29, val30, val31, val32, val33, val34, val35, val36, val37, val38, val39, val40, val41, val42, val43, val44, val45, val46, val47, val48, val49, val50, val51, val52, val53, val54, val55, val56, val57, val58, val59, val60, val61, val62, val63 from "' + table_str + '"  where timestamp > '+ str(time_past) + ' order by timestamp desc LIMIT 1')

		values = cur.fetchall()
		ret = values
		cur.close()
	except psycopg2.Error as e:
		if e == "no results to fetch":
			print( e )
	return ret	
	
	
		
def connect_psql(config):
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error) 		



# Prepare connection to PSQL
config = load_config()
psql_connection_lcars = connect_psql(config)
psql_connection_lcars.autocommit = True

if __name__ == "__main__":
	channel.basic_consume(queue='',on_message_callback=callback, auto_ack=True)
	# setup the thread with timer and start the IRQ reset function
	job = Job(interval=timedelta(seconds=WAIT_TIME_SECONDS), execute=animation_push)
	
	try:
		device = get_device(['--interface', 'spi', '--display', 'st7789', '--spi-port', '0', '--spi-bus-speed', '52000000', '--width', '320', '--height', '240','--mode','RGB' ])
		init(device)
		job.start()
		channel.start_consuming()
	except KeyboardInterrupt or Exception or OSError as e:
		print("Termination", e)
		sys.exit(1)
