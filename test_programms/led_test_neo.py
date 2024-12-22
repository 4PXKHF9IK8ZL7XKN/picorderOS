#!/bin/python3
import time
#from rainbowio import colorwheel
import neopixel
import board
import random

pixels = neopixel.NeoPixel(board.D21, 30)    # Feather wiring!

# HELPERS
# a random color 0 -> 192
def random_color():
    return random.randrange(0, 7) * 32

while True:
	pixels.fill((random_color(), random_color(), random_color()))
	time.sleep(1)




