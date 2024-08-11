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
import numpy as np
from pathlib import Path
import cv2
from PIL import Image
import PIL

from luma.core.virtual import viewport, snapshot, range_overlap
from luma.core.sprite_system import framerate_regulator
from luma.core import cmdline, error
from luma.core.render import canvas

#filename = "/home/christian/projekt/picorderOS/assets/ekmd.m4v"
#filename = "/tmp/stream.yuv"
filename = "/home/christian/projekt/picorderOS/assets/Firestorm Reveal Trailer.mp4"

def videoplayer_frame(device):
    global filename 
    # Create a video capture object, in this case we are reading the video from a file
    vid_capture = cv2.VideoCapture(filename)
    
    if (vid_capture.isOpened() == False):
        print("Error opening the video file")
        # Read fps and frame count
    else:
        # Get frame rate information
        # You can replace 5 with CAP_PROP_FPS as well, they are enumerations
        fps = vid_capture.get(5)
        print('Frames per second : ', fps,'FPS')
 
        # Get frame count
        # You can replace 7 with CAP_PROP_FRAME_COUNT as well, they are enumerations
        frame_count = vid_capture.get(7)
        print('Frame count : ', frame_count)
 

    while(vid_capture.isOpened()):
        # vid_capture.read() methods returns a tuple, first element is a bool 
        # and the second is frame
        ret, frame = vid_capture.read()
        if frame is None:
            break
        img = Image.fromarray(frame)
        if ret == True:
            #cv2.imshow('Frame',frame)
            if img.width != device.width or img.height != device.height:
                # resize video to fit device
                size = device.width, device.height
                img = img.resize(size, PIL.Image.LANCZOS)

            device.display(img.convert(device.mode))
            # 20 is in milliseconds, try to increase the value, say 50 and observe
            key = cv2.waitKey(50)

        else:
            break
                
    # Release the video capture object
    vid_capture.release()

