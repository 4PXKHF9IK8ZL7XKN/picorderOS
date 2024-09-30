#!/bin/python

import busio
#import storage
import adafruit_sdcard
import digitalio
import os
import board
import RPi.GPIO as GPIO
import spidev
import time

import board
import sdcardio

sd = sdcardio.SDCard(board.SPI(),board.SDCARD_CS)
