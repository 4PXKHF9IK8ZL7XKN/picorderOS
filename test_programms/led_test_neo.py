#!/bin/python3
import time
#from rainbowio import colorwheel
import neopixel
import board
import random

pixels = neopixel.NeoPixel(board.D12, 39)    # Feather wiring!

# HELPERS
# a random color 0 -> 192
def random_color():
    return random.randrange(0, 7) * 32

while True:
    for dot in range(0,26,1):
        pixels[dot] = ((random_color(), 0, random_color()))
        time.sleep(0.1)




