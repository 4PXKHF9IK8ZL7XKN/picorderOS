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

background = (0,0,0)
scannerline0 = (10,10,0)
scannerline1 = (10,10,0)
square_RB = (10,10,0)
square_LB = (10,10,0)
square_TL = (10,10,0)
flip_lights = (0,96,0)
top_right_in = (96,0,0)
top_center_in = (96,0,0)

WAIT_TIME_SECONDS = 0.1

devider0 = 0

dots = dotstar.DotStar(board.D21, board.D20, 128, brightness=0.5)
n_dot = len(dots)

# Init rabbitmq connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='sensor_data', exchange_type='topic')

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
  dots.fill(background)
  dots.show()

def fn_dots_unload():
  dots.fill((0, 0, 0))
  dots.show()
  dots.deinit()

def fn_dots_static():
# static Right Bottom Square
  dots[48] = (square_RB)
  dots[49] = (square_RB)
  dots[40] = (square_RB)
  dots[41] = (square_RB)
# static Left Bottom Square
  for static0 in range(104,120,1):
    dots[static0] = (square_LB)
  dots[47] = (square_LB)
  dots[55] = (square_LB)
# static Left Top Square
  for static1 in range(104,120,1):
    dots[static1] = (square_LB)
  for static2 in range(76,80,1):
    dots[static2] = (square_TL)
# static Top Right
  dots[2] = (top_right_in)
  dots[10] = (top_right_in)
# static Top Center
  dots[5] = (top_center_in)
  dots[13] = (top_center_in)


# Startup: Initial LED settings
fn_dots_reset()
time.sleep(1)
fn_dots_initial()
fn_dots_static()


def animation():
    global background 
    global scannerline0 
    global scannerline1 
    global square_RB 
    global square_LB 
    global square_TL 
    global flip_lights 
    global top_right_in 
    global top_center_in 
  
    global devider0
    while True:
      for scene in range(0,8,1):
          if scene % 2 == 0:
             devider0 = devider0 + 1
          if devider0 == 8:
             devider0 = 0
          # scannerline0
          dots[96+scene] = (scannerline0)
          dots[39-scene] = (scannerline0)
          time.sleep(0.02)
          # prevent overscanning
          if scene > 0:
            dots[38-scene+2] = (background)
            dots[97+scene-2] = (background)
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
          if scene >= 4:
              # on
              dots[64] = (flip_lights)
              dots[72] = (flip_lights)
              # off
              time.sleep(0.02)
              dots[65] = (background)
              dots[73] = (background)
          else:
              # off
              dots[64] = (background)
              dots[72] = (background)
              # on
              dots[65] = (flip_lights)
              dots[73] = (flip_lights)
          dots.show()
          time.sleep(0.02)
      # reseting dot
      #dots.fill((random_color(), random_color(), random_color()))
      fn_dots_static()
      dots[103] = (background)
      dots[32] = (background)

      #dots[127] = (background)
      #dots[56] = (background)

      dots.show()
      time.sleep(0.01)


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
  global flip_lights
  global top_right_in
  global top_center_in
  
  DICT = body.decode()
  DICT_CLEAN = ast.literal_eval(DICT)
  print('EVENT')	
  print(DICT_CLEAN)   
  if DICT_CLEAN['SENSOR_MODE'] == 0:
    scannerline1 = (10,10,0)
    square_LB = (10,10,0)
    
    background = (0,0,0)
    scannerline0 = (10,10,0)
    square_RB = (10,10,0)
    square_TL = (10,10,0)
    flip_lights = (0,96,0)
    top_right_in = (96,0,0)
    top_center_in = (96,0,0)
  
  elif DICT_CLEAN['SENSOR_MODE'] == 1:
    scannerline1 = (0,255,0)
    square_LB = (0,10,0)
    
    background = (0,0,0)
    scannerline0 = (10,10,0)
    square_RB = (10,10,0)
    square_TL = (10,10,0)
    flip_lights = (0,96,0)
    top_right_in = (96,0,0)
    top_center_in = (96,0,0)
  
  elif DICT_CLEAN['SENSOR_MODE'] == 2:
    scannerline1 = (255,0,0)
    square_LB = (10,0,0)
    
    background = (0,0,0)
    scannerline0 = (10,10,0)
    square_RB = (10,10,0)
    square_TL = (10,10,0)
    flip_lights = (0,96,0)
    top_right_in = (96,0,0)
    top_center_in = (96,0,0)
    
    
  elif DICT_CLEAN['SENSOR_MODE'] == 3:
    scannerline1 = (0,0,255)
    square_LB = (0,0,10)
    
    background = (0,0,0)
    scannerline0 = (10,10,0)
    square_RB = (10,10,0)
    square_TL = (10,10,0)
    flip_lights = (0,96,0)
    top_right_in = (96,0,0)
    top_center_in = (96,0,0)
 
    
    
  else:
    scannerline1 = (0,0,255)
    square_LB = (0,0,255)
    background = (0,0,0)
    scannerline0 = (0,0,0)
    square_RB = (0,0,0)
    square_TL = (0,0,0)
    flip_lights = (0,0,0)
    top_right_in = (0,0,0)
    top_center_in = (0,0,0)


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

