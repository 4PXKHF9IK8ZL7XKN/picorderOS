#!/bin/python
import busio
import board

i2c = busio.I2C(board.SCL, board.SDA)

dict = {"0x69": "AMG8833 8x8 Thermal Camera", "0x62": "SCD-41 - CO2, Temperature, Humidity Sensor" ,"0x76": "BME680 - Temperature, Humidity, Pressure and Gas Sensor", "0x5a": "mpr121 - 12-Key Capacitive Touch Sensor", "0x5b": "mpr121 - 12-Key Capacitive Touch Sensor", "0x6a":"LSM6DS3TR-C - Gyro + Accel","0x1c":"LIS3MDL - Magnetometer","0x39":"APDS9960 - Light + Gesture + Proximity", "0x44": "SHT30 - Humidity", "0x77":"BMP280 - Temp + Pressure" }

list = i2c.scan()
for item in list:
	if str(hex(item)) in dict:
		print("Address:", hex(item), " - " , dict[str(hex(item))])
	else:
		print("Address:", hex(item))
