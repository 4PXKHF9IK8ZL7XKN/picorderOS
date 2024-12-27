#!/bin/python3
import time
import neopixel
import board
import random
import sys
import pika
import threading
from datetime import timedelta
import ast
import math

background = (0,0,0)
sensor_animation = 0
sensor_animation_mode = False

WAIT_TIME_SECONDS = 0.1

Pattern = 0

bio = (0,32,0)
met = (0,32,0)
geo = (0,32,0)
pwr = (32,0,0)
BTL = (0,32,0)
DDOT = (32,0,0)
BLTR = (0,32,0)
ABGD = (0,32,0)
BRB1 = (32,0,0)
BRB2 = (32,32,0)
BRB3 = (0,32,0)

ALERT_STATE_mem = 0
SENSOR_MODE_mem = 0

ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(board.D12, 39, pixel_order=ORDER)
n_dot = 39

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
    
# We request now all Sensor data and Rabbitmq values to make the graph drawing realy valuable 
channel.queue_bind(
    exchange='sensor_data', queue='', routing_key='system_vitals')

# HELPERS
# a random color 0 -> 192
def random_color():
    return random.randrange(0, 7) * 32

# Reset (all LEDs off)
def fn_dots_reset():
  global n_dot
  pixels.fill((0, 0, 0))
  pixels.show()

def fn_dots_initial():
  global background
  global n_dot
  pixels.fill(background)
  pixels.show()

def fn_dots_unload():
  global n_dot
  pixels.fill((0, 0, 0))
  
  
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)
    
def rainbow_cycle(wait):
    for j in range(255):
        for i in range(n_dot):
            pixel_index = (i * 256 // n_dot) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)


def fn_dots_static():
  global bio
  global met
  global geo
  global pwr
  global BTL

  #print("static")
  pixels[8] = (bio)
  pixels[9] = (met)
  pixels[10] = (geo)
  pixels[14] = (pwr)
  pixels[15] = (pwr)
  pixels[16] = (BTL)
  pixels[17] = (BTL)
  pixels[18] = (BTL)
  pixels[19] = (DDOT)
  pixels[20] = (DDOT)
  pixels[21] = (DDOT)
  pixels[22] = (DDOT)

# Startup: Initial LED settings
fn_dots_reset()
time.sleep(1)
fn_dots_initial()
fn_dots_static()

def ABGD_Sequenzer(): 
  global background
  global sensor_animation
  global sensor_animation_mode
  if sensor_animation_mode:
    if sensor_animation == 3:
      pixels[0] = (ABGD)
      pixels[1] = (ABGD)
      
      pixels[2] = (background)
      pixels[3] = (background)
      
      pixels[4] = (background)
      pixels[5] = (background)
      
      pixels[6] = (background)
      pixels[7] = (background)
    
    if sensor_animation == 2:
      pixels[0] = (background)
      pixels[1] = (background)
      
      pixels[2] = (ABGD)
      pixels[3] = (ABGD)
      
      pixels[4] = (background)
      pixels[5] = (background)
      
      pixels[6] = (background)
      pixels[7] = (background)
                
    if sensor_animation == 1:
      pixels[0] = (background)
      pixels[1] = (background)
      
      pixels[2] = (background)
      pixels[3] = (background)
      
      pixels[4] = (ABGD)
      pixels[5] = (ABGD)
      
      pixels[6] = (background)
      pixels[7] = (background)
   
    if sensor_animation == 0:
      pixels[0] = (background)
      pixels[1] = (background)
      
      pixels[2] = (background)
      pixels[3] = (background)
      
      pixels[4] = (background)
      pixels[5] = (background)
      
      pixels[6] = (ABGD)
      pixels[7] = (ABGD)
  else:
    if sensor_animation == 0:
      pixels[0] = (ABGD)
      pixels[1] = (ABGD)
      
      pixels[2] = (background)
      pixels[3] = (background)
      
      pixels[4] = (background)
      pixels[5] = (background)
      
      pixels[6] = (background)
      pixels[7] = (background)
    
    if sensor_animation == 1:
      pixels[0] = (background)
      pixels[1] = (background)
      
      pixels[2] = (ABGD)
      pixels[3] = (ABGD)
      
      pixels[4] = (background)
      pixels[5] = (background)
      
      pixels[6] = (background)
      pixels[7] = (background)
                
    if sensor_animation == 2:
      pixels[0] = (background)
      pixels[1] = (background)
      
      pixels[2] = (background)
      pixels[3] = (background)
      
      pixels[4] = (ABGD)
      pixels[5] = (ABGD)
      
      pixels[6] = (background)
      pixels[7] = (background)
   
    if sensor_animation == 3:
      pixels[0] = (background)
      pixels[1] = (background)
      
      pixels[2] = (background)
      pixels[3] = (background)
      
      pixels[4] = (background)
      pixels[5] = (background)
      
      pixels[6] = (ABGD)
      pixels[7] = (ABGD)
              
def animation():
    global Pattern
    global background 
    global BLTR
    global ABGD
    global BRB1
    global BRB2
    global BRB3
    global sensor_animation
    
    while True:
      if Pattern == 0:      
        for scene in range(0,4,1):
          ABGD_Sequenzer()
          if scene == 0:
            pixels[23] = (BLTR)
            pixels[24] = (background) 
            pixels[25] = (background)
            pixels[26] = (background) 
                        
            pixels[11] = (BRB1)
            pixels[12] = (background)
            pixels[13] = (background)
            
            ABGD_Sequenzer()
                           
          if scene == 1:
            pixels[23] = (background)
            pixels[24] = (BLTR) 
            pixels[25] = (background)
            pixels[26] = (background)              
             
            pixels[11] = (background)
            pixels[12] = (background)
            pixels[13] = (BRB3)
            
            ABGD_Sequenzer()
                   
          if scene == 2:
            pixels[23] = (background)
            pixels[24] = (background) 
            pixels[25] = (BLTR)
            pixels[26] = (background)  
                        
            pixels[11] = (background)
            pixels[12] = (BRB2)
            pixels[13] = (background)    
            
            ABGD_Sequenzer()        
                        
          if scene == 3:
            pixels[23] = (background)
            pixels[24] = (background) 
            pixels[25] = (background)
            pixels[26] = (BLTR)  
                        
            pixels[11] = (background)
            pixels[12] = (background)
            pixels[13] = (background)   
            
            ABGD_Sequenzer()
                        
          time.sleep(0.3)
      elif Pattern == 1:
        print("1")
        
        time.sleep(1.0)
      elif Pattern == 2:
        pixels.fill(background)
        time.sleep(1.0)
      elif Pattern == 3:
        rainbow_cycle(0.01)
      elif Pattern == 4:  
        pixels.fill((random_color(),random_color(),random_color()))
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
  global Pattern
  global sensor_animation
  global BTL
  global sensor_animation_mode
  global background
  global ALERT_STATE_mem
  global SENSOR_MODE_mem
   
  if method.routing_key != 'EVENT':
    sensor_animation = sensor_animation + 0.5
    if sensor_animation == 4:
      sensor_animation = 0
			
  else:
  
    DICT = body.decode()
    DICT_CLEAN = ast.literal_eval(DICT)
    #print('EVENT')	
    #print(DICT_CLEAN)   
    
    if ALERT_STATE_mem != DICT_CLEAN['ALERT_STATE']:
    
      if DICT_CLEAN['ALERT_STATE'] == 0:
        BTL = (0,32,0)
      elif DICT_CLEAN['ALERT_STATE'] == 1:
        BTL = (32,32,0)
      elif DICT_CLEAN['ALERT_STATE'] == 2:
        BTL = (32,0,0)
      elif DICT_CLEAN['ALERT_STATE'] == 3:
        BTL = (0,0,32)
      elif DICT_CLEAN['ALERT_STATE'] == 4:
        BTL = (10,10,32)
      elif DICT_CLEAN['ALERT_STATE'] == 5:
        BTL = (32,32,32)
      else:
        BTL = (0,64,0)
      fn_dots_static()  
        
      ALERT_STATE_mem = DICT_CLEAN['ALERT_STATE']
      
    if SENSOR_MODE_mem != DICT_CLEAN['SENSOR_MODE']:
    
      if DICT_CLEAN['SENSOR_MODE'] == 0:
        Pattern = 0
        background = (0,0,0)
        BTL = (0,32,0)
        sensor_animation_mode = False
        fn_dots_static()
      
      elif DICT_CLEAN['SENSOR_MODE'] == 1:
        Pattern = 0
        BTL = (0,32,0)
        sensor_animation_mode = True
      
      elif DICT_CLEAN['SENSOR_MODE'] == 2:
        Pattern = 0
        fn_dots_static()
        sensor_animation_mode = False
        
      elif DICT_CLEAN['SENSOR_MODE'] == 3:
        Pattern = 0
        BTL = (0,32,0)
        fn_dots_static()    
        sensor_animation_mode = True 

      elif DICT_CLEAN['SENSOR_MODE'] == 4:
        Pattern = 0
        BTL = (0,32,0)
        sensor_animation_mode = True 
        fn_dots_static()     

      elif DICT_CLEAN['SENSOR_MODE'] == 5:
        background = (96,96,96)
        Pattern = 2
        sensor_animation_mode = True
        fn_dots_static()      
        
      elif DICT_CLEAN['SENSOR_MODE'] == 6:
        background = (0,0,0)
        Pattern = 4
        sensor_animation_mode = True 
        fn_dots_static()     
        
      elif DICT_CLEAN['SENSOR_MODE'] == 7:
        background = (0,0,0)
        Pattern = 3
        sensor_animation_mode = True 
        fn_dots_static()     
        
      else:
        Pattern = 2
        background = (0,0,0)
        scannerline1 = (0,0,0)
        fn_dots_static()        
        
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

