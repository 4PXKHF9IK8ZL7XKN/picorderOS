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
import socket
from luma.core.virtual import viewport, snapshot, range_overlap
from luma.core.sprite_system import framerate_regulator
from luma.core import cmdline, error
from luma.core.render import canvas

HOST = "192.168.176.133"  # Standard loopback interface address (localhost)
PORT = 1337  # Port to listen on (non-privileged ports are > 1023)

sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sd.bind((HOST, PORT))
    
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
    
def decode(s, encoding="ascii", errors="ignore"):
    return s.decode(encoding=encoding, errors=errors)

def main(device):
    r = 128
    g = 128
    b = 128
    
    chunk_size = 3

    while True:
        data, addr  = sd.recvfrom(1480)
        #print("Data:",data)
        ret = decode(data)
        array = ret.splitlines()
        X,Y = array[1].split(' ')
        print("Size;",X," ",Y)

        picture_points = array[3]
        picture_points_colores = list(picture_points)
        
        for number,point in enumerate(picture_points_colores):
            try:
                picture_points_colores[number] = int(point)
            except:
                picture_points_colores[number] = 255
                 
        chunked_list = list()
        for i in range(0, len(picture_points_colores), chunk_size):
            chunked_list.append(picture_points_colores[i:i+chunk_size])
        
        ##ret = np.array_split(picture_points, 3)
        ##chunked_list = list(chunks(picture_points_colores,int(X)) )
        
        print("chop cop:", len(chunked_list))
        
        with canvas(device, dither=True) as draw:
            if len(chunked_list) != 0:
                count_symbols = 0
                for point_X in range(0,int(X)):
                     print("count:", count_symbols )
                     if len(chunked_list) <= count_symbols:
                            print("break by:", count_symbols )
                            break
                     if len(chunked_list[count_symbols]) == 3:
                        r,g,b = chunked_list[count_symbols]
                     for point_Y in range(0,int(Y)):
                        draw.point((point_X, point_Y), fill=(r, g, b))
                        count_symbols = count_symbols + 1
                        #print("symbols",count_symbols)
        
        import cv2
import numpy as np

class VideoCaptureYUV:
    def __init__(self, filename, size):
        self.height, self.width = size
        self.frame_len = self.width * self.height * 3 / 2
        self.f = open(filename, 'rb')
        self.shape = (int(self.height*1.5), self.width)

    def read_raw(self):
        try:
            raw = self.f.read(self.frame_len)
            yuv = np.frombuffer(raw, dtype=np.uint8)
            yuv = yuv.reshape(self.shape)
        except Exception as e:
            print str(e)
            return False, None
        return True, yuv

    def read(self):
        ret, yuv = self.read_raw()
        if not ret:
            return ret, yuv
        bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_NV21)
        return ret, bgr


if __name__ == "__main__":
    #filename = "data/20171214180916RGB.yuv"
    filename = "data/20171214180916IR.yuv"
    size = (480, 640)
    cap = VideoCaptureYUV(filename, size)

    while 1:
        ret, frame = cap.read()
        if ret:
            cv2.imshow("frame", frame)
            cv2.waitKey(30)
        else:
            break
        
        
        

if __name__ == "__main__":
    try:
        device = get_device(['--interface', 'spi', '--display', 'st7789', '--spi-port', '0', '--spi-bus-speed', '52000000', '--width', '320', '--height', '240','--mode','RGB' ])
        main(device)
    except KeyboardInterrupt:
        pass
