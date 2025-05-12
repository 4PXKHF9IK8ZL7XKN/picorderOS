#!/bin/python3
import time
import adafruit_dotstar as dotstar
import board
import random
import sys
import pika
import threading
from datetime import timedelta
import ast
import math

background = (0,0,0)
scannerline0 = (10,10,0)
scannerline1 = (10,10,0)
scannerlinedebug = (20,20,20)
square_RB = (10,10,0)
square_LB = (10,10,0)
square_TL = (10,10,0)
flip_lights0 = (0,96,0)
flip_lights1 = (0,96,0)
top_right_in = (96,0,0)
top_center_in = (96,0,0)

SENSOR_MODE_mem = 0

WAIT_TIME_SECONDS = 0.1

devider0 = 0
Pattern = 0
Rainbow = []

dots = dotstar.DotStar(board.D21, board.D20, 128, brightness=0.1)
n_dot = len(dots)

# Init rabbitmq connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='sensor_data', exchange_type='topic')
(0,96,0)
result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue

# We request now all Sensor data and Rabbitmq values to make the graph drawing realy valuable 
channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='EVENT')


# HELPERS
# a random color 0 -> 192
def random_color():
    return random.randrange(0, 7) * 32

# Reset (all LEDs off)
def fn_dots_reset():
  dots.fill((0, 0, 0))
  dots.show()

def fn_dots_initial():
  global Rainbow
  dots.fill(background)
  dots.show()
  
  pixr,pixg,pixb = 0,0,0
  for firstPixelHue in range(0,128,1):
    for pixel in range( 1, n_dot, 3):
      pixelHuer = firstPixelHue + ((pixel-1)  / n_dot)
      pixelHueg = firstPixelHue + (pixel / n_dot)
      pixelHueb = firstPixelHue + ((pixel+1) / n_dot)
      Rainbow.append((math.ceil(pixelHuer/3),math.ceil(pixelHueg),math.ceil(pixelHueb)))
  
def rotate_array(n):
  global Rainbow
  Rainbow = Rainbow[-n:] + Rainbow[:-n]



def fn_dots_unload():
  dots.fill((0, 0, 0))
  dots.show()
  dots.deinit()

def fn_dots_static():
# static Right Bottom Square
  dots[33] = (square_RB)
  dots[34] = (square_RB)

# static Left Bottom Square
  for static0 in range(96,104,1):
    dots[static0] = (square_LB)
  dots[39] = (square_LB)
#  dots[47] = (square_LB)
#  for static1 in range(104,120,1):
#    dots[static1] = (square_LB)
# static Left Top Square
  for static2 in range(68,72,1):
    dots[static2] = (square_TL)
# static Top Right
  dots[2] = (top_right_in)
  #dots[10] = (top_right_in)
# static Top Center
  dots[5] = (top_center_in)
  dots[13] = (top_center_in)


# Startup: Initial LED settings
fn_dots_reset()
time.sleep(1)
fn_dots_initial()
fn_dots_static()


def animation():
    global Pattern
    global background 
    global scannerline0 
    global scannerline1 
    global square_RB 
    global square_LB 
    global square_TL 
    global flip_lights 
    global top_right_in 
    global top_center_in 
    global Rainbow
    global n_dot
    global devider0
    
    while True:
      if Pattern == 0:
        for scene in range(0,8,1):
            if scene % 2 == 0:
               devider0 = devider0 + 1
            if devider0 == 8:
               devider0 = 0
            # scannerline0
            dots[80+scene] = (scannerline0)
            dots[23-scene] = (scannerline0)
            time.sleep(0.02)
            # prevent overscanning
            if scene > 0:
              dots[22-scene+2] = (background)
              dots[81+scene-2] = (background)
            # scannerline1
            # check if sequenz is even to prevent overscanning
            if scene % 2 == 0:
              dots[120+devider0] = (scannerline1)
              dots[63-devider0] = (scannerline1)
              time.sleep(0.02)
              if devider0 > 0:
                dots[62-devider0+2] = (background)
                dots[121+devider0-2] = (background)
              dots[127] = (background)
              dots[56] = (background)
            # Flip Lights Top
            # This sequenz is the switching dots
            if scene >= 4:
                # on
                dots[64] = (flip_lights0)
                #dots[72] = (flip_lights0)
                # off
                time.sleep(0.02)
                dots[65] = (background)
                #dots[73] = (background)
            else:
                # This sequenz is the switching dots
                # off
                dots[64] = (background)
                #dots[72] = (background)
                # on
                dots[65] = (flip_lights1)
                #dots[73] = (flip_lights1)
            dots.show()
            time.sleep(0.02)
        # reseting dot
        fn_dots_static()
        dots[87] = (background)
        dots[16] = (background)

        dots.show()
        time.sleep(0.01)
      elif Pattern == 1:
        fix_leds = [87,86,85,84,83,82,81,80,23,22,21,20,19,18,17,16 ] 
        fix_leds_rev = [16,17,18,19,20,21,22,23,80,81,82,83,84,85,86,87 ]
        r,g,b = scannerline0 
        
        #print("knight Rider")
        for scene in range(0,16,1):
          # scannerline0
          dots[fix_leds[scene]] = (scannerline0)
          dots[fix_leds[scene-1]] = (background)
          dots[fix_leds[scene-2]] = (background)
          dots[fix_leds[scene-3]] = (background)
          dots[fix_leds[scene-4]] = (background)
          if scene > 0:
            dots[fix_leds[scene-1]] = (round(r*0.5),round(g*0.5),round(b*0.5))
          if scene > 1:
            dots[fix_leds[scene-2]] = (round(r*0.25),round(g*0.25),round(b*0.25))
          if scene > 2:
            dots[fix_leds[scene-2]] = (round(r*0.1),round(g*0.1),round(b*0.1))
          

          time.sleep(0.02)

          dots.show()

        for scene in range(0,16,1):
          # scannerline0
          dots[fix_leds_rev[scene]] = (scannerline0)
          dots[fix_leds_rev[scene-1]] = (background)
          dots[fix_leds_rev[scene-2]] = (background)
          dots[fix_leds_rev[scene-3]] = (background)
          dots[fix_leds_rev[scene-4]] = (background)
          if scene > 0:
            dots[fix_leds_rev[scene-1]] = (round(r*0.5),round(g*0.5),round(b*0.5))
          if scene > 1:
            dots[fix_leds_rev[scene-2]] = (round(r*0.25),round(g*0.25),round(b*0.25))
          if scene > 2:
            dots[fix_leds_rev[scene-2]] = (round(r*0.1),round(g*0.1),round(b*0.1))
          

          time.sleep(0.02)
          
          dots.show()

            
        # reseting dot
        fn_dots_static()
        
      elif Pattern == 2:
        dots.fill((background))
        time.sleep(1.0)
      elif Pattern == 3:
        #print("Rainbow")
        for step in range(0,n_dot,1):
          dots[step] = Rainbow[step]
        rotate_array(-1)
      elif Pattern == 4:  
        dots.fill((random_color(),random_color(),random_color()))
        time.sleep(1.0)
      else:
        time.sleep(1.0)


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
      

def callback(ch, method, properties, body):
  global scannerline1
  global square_LB
  global scannerline0
  global background
  global square_RB
  global square_TL
  global flip_lights0
  global top_right_in
  global top_center_in
  global Pattern
  global flip_lights1
  global SENSOR_MODE_mem
  
  DICT = body.decode()
  DICT_CLEAN = ast.literal_eval(DICT)

  if SENSOR_MODE_mem != DICT_CLEAN['SENSOR_MODE']:

    if DICT_CLEAN['SENSOR_MODE'] == 0:
      Pattern = 0
      scannerline1 = (255,255,0)
      square_LB = (10,10,0)
      
      flip_lights0 = (0,96,0)
      flip_lights1 = (0,96,0)
      background = (0,0,0)
      scannerline0 = (255,255,0)
      square_RB = (10,10,0)
      square_TL = (10,10,0)
      flip_lights = (0,96,0)
      top_right_in = (96,0,0)
      top_center_in = (96,0,0)
    
    elif DICT_CLEAN['SENSOR_MODE'] == 1:
      Pattern = 0
      scannerline1 = (255,255,0)
      square_LB = (0,0,255)   
      
      flip_lights0 = (0,96,0)
      flip_lights1 = (96,0,0)
      background = (0,0,0)
      scannerline0 = (255,255,0)
      square_RB = (10,10,0)
      square_TL = (0,0,255)
      flip_lights = (0,96,0)
      top_right_in = (96,0,0)
      top_center_in = (96,0,0)
    
    elif DICT_CLEAN['SENSOR_MODE'] == 2:
      Pattern = 0
      scannerline1 = (255,0,0)
      square_LB = (10,0,0)
      
      flip_lights0 = (96,0,0)
      flip_lights1 = (0,96,0)
      background = (0,0,0)
      scannerline0 = (255,0,0)
      square_RB = (10,10,0)
      square_TL = (10,10,0)
      top_right_in = (96,0,0)
      top_center_in = (96,0,0)
      
      
    elif DICT_CLEAN['SENSOR_MODE'] == 3:
      Pattern = 0
      scannerline1 = (0,0,255)
      square_LB = (0,0,255)
      
      flip_lights0 = (0,96,0)
      flip_lights1 = (96,0,0)
      background = (0,0,0)
      scannerline0 = (0,0,255)
      square_RB = (10,10,0)
      square_TL = (0,0,255)
      top_right_in = (96,0,0)
      top_center_in = (96,0,0)
    elif DICT_CLEAN['SENSOR_MODE'] == 4:
      Pattern = 1  
      flip_lights0 = (0,0,0)
      flip_lights1 = (0,0,0)
      scannerline1 = (0,0,0)
      square_LB = (0,0,0)
      background = (0,0,0)
      scannerline0 = (255,0,0)
      square_RB = (0,0,0)
      square_TL = (0,0,0)
      top_right_in = (0,0,0)
      top_center_in = (0,0,0)
    elif DICT_CLEAN['SENSOR_MODE'] == 5:
      background = (96,96,96)
      Pattern = 2
    elif DICT_CLEAN['SENSOR_MODE'] == 6:
      background = (0,0,0)
      Pattern = 4
    elif DICT_CLEAN['SENSOR_MODE'] == 7:
      background = (0,0,0)
      Pattern = 3
    else:
      Pattern = 2
      
      flip_lights0 = (0,0,0)
      flip_lights1 = (0,0,0)
      scannerline1 = (0,0,0)
      square_LB = (0,0,0)
      background = (0,0,0)
      scannerline0 = (0,0,0)
      square_RB = (0,0,0)
      square_TL = (0,0,0)
      top_right_in = (0,0,0)
      top_center_in = (0,0,0)
    # update background once
    dots.fill((background))
    SENSOR_MODE_mem = DICT_CLEAN['SENSOR_MODE']
  
if __name__ == "__main__":
	channel.basic_consume(queue='',on_message_callback=callback, auto_ack=True)
	# setup the thread with timer and start the IRQ reset function
	LED1_job = Job(interval=timedelta(seconds=WAIT_TIME_SECONDS), execute=animation)
	
	try:
		LED1_job.start()
		channel.start_consuming()
	except KeyboardInterrupt or Exception or OSError as e:
		print("Termination", e)
		sys.exit(1)

