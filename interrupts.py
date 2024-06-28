#!/usr/bin/env python3          
                                
# SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple test of the MPR121 capacitive touch sensor library.
# Will print out a message when any of the 12 capacitive touch inputs of the
# board are touched.  Open the serial REPL after running to see the output.
# Author: Tony DiCola
import sys
import time
import board
import busio
import signal
import RPi.GPIO as GPIO
import adafruit_mpr121
import threading
from datetime import timedelta
from pygame import mixer

# Import MPR121 module.
#import adafruit_mpr121

BUTTON_GPIOA = 17
BUTTON_GPIOB = 27

WAIT_TIME_SECONDS = 0.5

i2c = busio.I2C(board.SCL, board.SDA)
mpr121A = adafruit_mpr121.MPR121(i2c)
mpr121B = adafruit_mpr121.MPR121(i2c)

# Create I2C bus.
#i2c = busio.I2C(board.SCL, board.SDA)

# Create MPR121 object.
#mpr121 = adafruit_mpr121.MPR121(i2c)

# Note you can optionally change the address of the device:
mpr121A = adafruit_mpr121.MPR121(i2c, address=0x5A)
mpr121B = adafruit_mpr121.MPR121(i2c, address=0x5B)

def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

def button_callbackB(channel):
    #print("B Button pressed:", GPIO.input(BUTTON_GPIOB))
    for i in range(12):
        if mpr121B[i].value:
            print('Input B {} touched!'.format(i))
            alert.play()
    

def button_callbackA(channel):
    #print("A Button pressed:", GPIO.input(BUTTON_GPIOA))
    for i in range(12):
        if mpr121A[i].value:
            print('Input A {} touched!'.format(i))
            alert.play()

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

def reset():
    if not GPIO.input(17) or not GPIO.input(27):
        for i in range(12):
            null = mpr121B[i].value
            null = mpr121A[i].value

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_GPIOA, GPIO.IN)
    GPIO.setup(BUTTON_GPIOB, GPIO.IN)

    GPIO.add_event_detect(BUTTON_GPIOA, GPIO.BOTH, callback=button_callbackA, bouncetime=50)
    GPIO.add_event_detect(BUTTON_GPIOB, GPIO.BOTH, callback=button_callbackB, bouncetime=50) 

    mixer.init()
    alert=mixer.Sound('assets/beep.wav')

    job = Job(interval=timedelta(seconds=WAIT_TIME_SECONDS), execute=reset)
    job.start()

    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()
