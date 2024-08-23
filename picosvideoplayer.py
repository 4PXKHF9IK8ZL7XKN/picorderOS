#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-2023 Richard Hull and contributors
# See LICENSE.rst for details.
# PYTHON_ARGCOMPLETE_OK

"""
Display a video clip.

Make sure to install the av system packages:

  $ sudo apt-get install -y libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libavresample-dev libavfilter-dev

And the pyav package (might take a while):

  $ sudo -H pip install av
"""

import sys
import time
import numpy as np
from pathlib import Path
import cv2
from PIL import Image, ImageDraw
import PIL

from luma.core.virtual import viewport, snapshot, range_overlap
from luma.core.sprite_system import framerate_regulator
from luma.core import cmdline, error

#filename = "/home/christian/projekt/picorderOS/assets/ekmd.m4v"
#filename = "/tmp/stream.yuv"
#filename = "/home/christian/projekt/picorderOS/assets/Firestorm Reveal Trailer.mp4"



def videoplayer_frame(device, draw, pos_ax,pos_ay,pos_bx,pos_by,filename):

	desktop = draw._image
	background = Image.new(device.mode, device.size)
	background.paste(desktop, (int(0), int(0)))

	frame_x = int(pos_bx - pos_ax)
	frame_y = int(pos_by - pos_ay)
	if frame_x is not None and frame_y is not None:
		frame_set = True

	# Create a video capture object, in this case we are reading the video from a file
	vid_capture = cv2.VideoCapture(filename)
    
	if (vid_capture.isOpened() == False):
		print("Error opening the video file")
        # Read fps and frame count
	else:
		# Get frame rate information
		fps = vid_capture.get(cv2.CAP_PROP_FPS)
 
        # Get frame count
        # You can replace 7 with CAP_PROP_FRAME_COUNT as well, they are enumerations
		frame_count = vid_capture.get(7)
 
 	# used to record the time when we processed last frame 
	prev_frame_time = 0
  
	# used to record the time at which we processed current frame 
	new_frame_time = 0 
	fps_count = 0
	frame_no = 0	
	starttime = time.time()
	


	while(vid_capture.isOpened()):
		# vid_capture.read() methods returns a tuple, first element is a bool 
		# and the second is frame
		frame_exists, frame = vid_capture.read()
		
		if frame_exists:
			img = Image.fromarray(frame)
			time_dis_millis = (time.time() - starttime) * 1000
			# Performance debug
			##print("distance", time_dis_millis, vid_capture.get(cv2.CAP_PROP_POS_MSEC))
			if time_dis_millis <  vid_capture.get(cv2.CAP_PROP_POS_MSEC):
				if img.width != device.width or img.height != device.height:
		            
					# resize video to fit device
					if frame_set:
						size = frame_x, frame_y
					else:
						size = device.width, device.height
					img = img.resize(size, PIL.Image.LANCZOS)
					
				background.paste(img, (int(pos_ax), int(pos_ay)))
				device.display(background)
				#device.display(img.convert(device.mode))
			new_frame_time = time.time() 
			fps_count = 1/(new_frame_time-prev_frame_time) 
			prev_frame_time = new_frame_time 
			fps_count = int(fps_count) 
			# Performance debug
			##print("for frame : " + str(frame_no) + "   timestamp is: ", str(vid_capture.get(cv2.CAP_PROP_POS_MSEC)), "fps:", fps_count)
			frame_no += 1
		else:
			break
                 
            # 20 is in milliseconds, try to increase the value, say 50 and observe
            #key = cv2.waitKey(1)
                
	# Release the video capture object
	vid_capture.release()
	return

