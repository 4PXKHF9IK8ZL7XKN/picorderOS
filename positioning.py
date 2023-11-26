import serial,time
from pynmeagps import NMEAReader
from multiprocessing import Process,Queue,Pipe

# Serial UART address
port = '/dev/ttyUSB0'
baud = 9600

serialPort = serial.Serial(port, baudrate = baud, timeout = 0.5)

# function to collect GPS data as a process.
def GPS_process(conn):
 while True:
	stream = serial.Serial(port, 9600, timeout=3)
	nmr = NMEAReader(stream)
	(raw_data, parsed_data) = nmr.read()
	time.sleep(0.1)
	conn.send(parsed_data)


def threaded_GPS(conn):

	item = conn.recv()

	if hasattr(item, "lat"):
			print(item.lat, ",",  item.lon)

	#gps_process.terminate()

parent_conn,child_conn = Pipe()
gps_process = Process(target=GPS_process, args=(child_conn,))
gps_process.start()


while True:
	threaded_GPS(parent_conn)