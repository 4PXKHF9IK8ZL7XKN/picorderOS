#!/bin/python3
import time
from rainbowio import colorwheel
import adafruit_dotstar as dotstar
import board
import random

dots = dotstar.DotStar(board.D20, board.D13, 128, brightness=0.01)

# HELPERS
# a random color 0 -> 192
def random_color():
    return random.randrange(0, 7) * 32

while True:
    # Fill each dot with a random color
    dots.fill((random_color(), random_color(), random_color()))





