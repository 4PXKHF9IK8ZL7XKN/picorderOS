import serial,time
from pynmeagps import NMEAReader
from multiprocessing import Process,Queue,Pipe

print("INIT GPS")

# Serial UART address
port = '/dev/ttyACM0'
#baud = 9600
baud = 115200

serialPort = serial.Serial(port, baudrate = baud, timeout = 0.5)

def GPS_function():

		gps_update = {"lat" : 47.00, "lon" : 47.00, "speed" : 0.00,"altitude":0.00, "track" : 0.00, "sats":0}

		stream = serial.Serial(port, baud, timeout=3)
		nmr = NMEAReader(stream)
		(raw_data, parsed_data) = nmr.read()

		if hasattr(parsed_data, "lat"):

			if parsed_data.lat != '':
				gps_update["lat"] = float(parsed_data.lat)

			if parsed_data.lon != '':
				gps_update["lon"] = float(parsed_data.lon)


		if hasattr(parsed_data, "altitude"):

			if parsed_data.altitude != '':
				gps_update["altitude"] = float(parsed_data.altitude)


		if hasattr(parsed_data, "speed"):

			if parsed_data.speed != '':
				gps_update["speed"] = float(parsed_data.speed)

		return gps_update


print(GPS_function())
