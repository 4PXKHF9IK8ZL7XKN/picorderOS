#!/bin/python3
import time
import adafruit_dotstar as dotstar
import board
import random
#import neopixel

background = (128,0,0)

#dots = dotstar.DotStar(board.D20, board.D13, 128, brightness=0.01) 
#dots = dotstar.DotStar(board.D6, board.D5, 128, brightness=0.02)
dots = dotstar.DotStar(board.D21, board.D20, 128, brightness=0.01)
#pixels = neopixel.NeoPixel(board.D12, 30)    # Feather wiring!

n_dot = len(dots)

# HELPERS
# a random color 0 -> 192
def random_color():
    return random.randrange(0, 7) * 32

# Reset (all LEDs off)
def fn_dots_reset():
  dots.fill((0, 0, 0))
  dots.show()

def fn_dots_initial():
  dots.fill(background)
  dots.show()

def fn_dots_unload():
  dots.fill((0, 0, 0))
  dots.show()
  dots.deinit()

# Startup: Initial LED settings
fn_dots_reset()
time.sleep(1)
fn_dots_initial()


# Then run the blinking loop (simplified test with only 4 LEDs)
try:
  while True:
    for scene in range(0,8,1):
        dots[120+scene] = (0, 0, 255)
        dots[63-scene] = (0, 0, 255)
        dots[63-scene+1] = (background)
        dots[120+scene-1] = (background)
        dots.show()
        time.sleep(0.1)
    # reseting dot
    dots.fill((random_color(), random_color(), random_color()))
    #pixels.fill((random_color(), random_color(), random_color()))
    dots[56] = (background)
    dots[127] = (background)

    #dots[39] = (0, 0, 0)
    #dots[38] = (0, 30, 0)
    #dots[96] = (0, 0, 0)
    #dots[97] = (0, 30, 0)
    dots.show()
    time.sleep(0.5)

except KeyboardInterrupt:
  fn_dots_unload()



