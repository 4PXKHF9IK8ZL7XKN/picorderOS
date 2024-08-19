#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

GPS_DATA = [37.7820885,-122.3045112,'local']
# USS Hornet - Sea, Air and Space Museum (Alameda) , Pavel Knows ;)

BME680 = [[0,-40,85,'Thermometer','\xB0','BME680','timestamp','latitude','longitude','rabbitmq_tag'],[0,0,100,'Hygrometer','%','BME680','timestamp','latitude','longitude','rabbitmq_tag'],[0,300,1100,'Barometer','hPa','BME680','timestamp','latitude','longitude','rabbitmq_tag'],[0,0,500,'VOC','ppm','BME680','timestamp','latitude','longitude','rabbitmq_tag'],[0,-50,1100,'ALT','m','BME680','timestamp','latitude','longitude','rabbitmq_tag']]
SYSTEMVITALES = [[0,0,'inf','Timer','t','RaspberryPi','timestamp','latitude','longitude','rabbitmq_tag'],[0,0,4,'INDICATOR','IND','RaspberryPi','timestamp','latitude','longitude','rabbitmq_tag'],[0,-25,100,'CpuTemp','\xB0','RaspberryPi','timestamp','latitude','longitude','rabbitmq_tag'],[0,0,400,'CpuPercent','%','RaspberryPi','timestamp','latitude','longitude','rabbitmq_tag'],[0,0,4800000,'VirtualMemory','b','RaspberryPi','timestamp','latitude','longitude','rabbitmq_tag'],[0,0,100,'disk_usage','%','RaspberryPi','timestamp','latitude','longitude','rabbitmq_tag'],[0,0,100000,'BytesSent','b','RaspberryPi','timestamp','latitude','longitude','rabbitmq_tag'],[0,0,100000,'BytesReceived','b','RaspberryPi','timestamp','latitude','longitude','rabbitmq_tag']]
GENERATORS = [[0,-100,100,'SineWave','','GENERATORS','timestamp','latitude','longitude','rabbitmq_tag'],[0,-500,500,'TangentWave','','GENERATORS','timestamp','latitude','longitude','rabbitmq_tag'],[0,-100,100,'CosWave','','GENERATORS','timestamp','latitude','longitude','rabbitmq_tag'],[0,-100,100,'SineWave2','','GENERATORS','timestamp','latitude','longitude','rabbitmq_tag']]
SENSEHAT = [[0,-40,120,'Thermometer','\xB0','SENSEHAT','timestamp','latitude','longitude','rabbitmq_tag'],[0,0,100,'Hygrometer','%','SENSEHAT','timestamp','latitude','longitude','rabbitmq_tag'],[0,260,1260,'Barometer','hPa','SENSEHAT','timestamp','latitude','longitude','rabbitmq_tag'],[0,-500,500,'MagnetX','G','SENSEHAT','timestamp','latitude','longitude','rabbitmq_tag'],[0,-500,500,'MagnetY','G','SENSEHAT','timestamp','latitude','longitude','rabbitmq_tag'],[0,-500,500,'MagnetZ','G','SENSEHAT','timestamp','latitude','longitude','rabbitmq_tag'],[0,-500,500,'"AccelX','g','SENSEHAT','timestamp','latitude','longitude','rabbitmq_tag'],[0,-500,500,'"AccelY','g','SENSEHAT','timestamp','latitude','longitude','rabbitmq_tag'],[0,-500,500,'"AccelZ','g','SENSEHAT','timestamp','latitude','longitude','rabbitmq_tag']]
TERMALFRAME = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,'timestamp','latitude','longitude','rabbitmq_tag']
APDS9960 = [[0,0,255,'proximity','IND','APDS9960','timestamp','latitude','longitude','rabbitmq_tag'],[0,0,255,'gesture','IND','APDS9960','timestamp','latitude','longitude','rabbitmq_tag'],[0,0,65535,'red','IND','APDS9960','timestamp','latitude','longitude','rabbitmq_tag'],[0,0,65535,'green','IND','APDS9960','timestamp','latitude','longitude','rabbitmq_tag'],[0,0,65535,'blue','IND','APDS9960','timestamp','latitude','longitude','rabbitmq_tag'],[0,0,65535,'infra_red','IND','APDS9960','timestamp','latitude','longitude','rabbitmq_tag']]
LIS3MDL = [[0,-1000,1000,'uTesla_X','uT','LIS3MDL','timestamp','latitude','longitude','rabbitmq_tag'],[0,-1000,1000,'uTesla_Y','uT','LIS3MDL','timestamp','latitude','longitude','rabbitmq_tag'],[0,-1000,1000,'uTesla_Z','uT','LIS3MDL','timestamp','latitude','longitude','rabbitmq_tag']]
LSM6DS3 = [[0,-2500,2500,'accel_X','G','LSM6DS3','timestamp','latitude','longitude','rabbitmq_tag'],[0,-2500,2500,'accel_Y','G','LSM6DS3','timestamp','latitude','longitude','rabbitmq_tag'],[0,-2500,2500,'accel_Z','G','LSM6DS3','timestamp','latitude','longitude','rabbitmq_tag'],[0,-2500,2500,'gyro_X','G','LSM6DS3','timestamp','latitude','longitude','rabbitmq_tag'],[0,-2500,2500,'gyro_Y','G','LSM6DS3','timestamp','latitude','longitude','rabbitmq_tag'],[0,-2500,2500,'gyro_Z','G','LSM6DS3','timestamp','latitude','longitude','rabbitmq_tag']]
SCD4X = [[0,400,5000,'CO2','ppm','SCD4X','timestamp','latitude','longitude','rabbitmq_tag'],[0,-10,60,'Thermometer','\xB0','SCD4X','timestamp','latitude','longitude','rabbitmq_tag'],[0,0,100,'Hygrometer','%','SCD4X','timestamp','latitude','longitude','rabbitmq_tag']]
SHT30 = [[0,-40,85,'Thermometer','\xB0','SHT30','timestamp','latitude','longitude','rabbitmq_tag'],[0,0,100,'Hygrometer','%','SHT30','timestamp','latitude','longitude','rabbitmq_tag']]
BMP280 = [[0,-40,85,'Thermometer','\xB0','BMP280','timestamp','latitude','longitude','rabbitmq_tag'],[0,300,1100,'Barometer','hPa','BMP280','timestamp','latitude','longitude','rabbitmq_tag'],[0,-50,1100,'ALT','m','BMP280','timestamp','latitude','longitude','rabbitmq_tag']]
