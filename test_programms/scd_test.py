#!/bin/python

import time
import board
import adafruit_scd4x
import busio as io

PIN_SCL = 3
PIN_SDA = 2

I2C_FRQ = 100000

i2c = io.I2C(PIN_SCL, PIN_SDA, frequency=I2C_FRQ)
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
scd4x = adafruit_scd4x.SCD4X(i2c)
print("Serial number:", [hex(i) for i in scd4x.serial_number])

scd4x.start_periodic_measurement()
#scd4x.start_periodic_measurement()
#scd4x.start_periodic_measurement()
#scd4x.start_periodic_measurement()
print("Waiting for first measurement....")

while True:
    if scd4x.data_ready:
    	print("CO2: %d ppm" % scd4x.CO2)
    	print("Temperature: %0.1f *C" % scd4x.temperature)
    	print("Humidity: %0.1f %%" % scd4x.relative_humidity)
    	print()
    time.sleep(1)
