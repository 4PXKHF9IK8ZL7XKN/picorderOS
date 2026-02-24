import pika
import time
from random import randint

DEBUG = True

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

    
def declare_channel():
    # Setup Channels for Sensors
    channel.exchange_declare(exchange='sensor_data', exchange_type='topic')
    channel.queue_declare(queue='sensor_metadata')
    
def publish(IN_routing_key,data):
    
    routing_key = str(IN_routing_key)
    message = str(data)
    time_unix = time.time()
    channel.basic_publish(
        exchange='', routing_key=routing_key, body=message)
    if DEBUG:
    	print(f" {time_unix} [x] Sent {routing_key}:{message}")
    
def disconnect():
    connection.close()

def sensor_process():
	#meta_massage = '[{"dr_opening": True },{"dr_closing": False},{"warble": False},{"alert": False},{"sensor_alert": False}]'
	#publish('audio',meta_massage)
	#time.sleep(1)
	meta_massage = '[{"dr_opening": False },{"dr_closing": False},{"warble": False},{"alert": False},{"sensor_alert": True}]'
	publish('audio',meta_massage)
	#time.sleep(3)







def main():
	declare_channel()
	sensor_process()

if __name__ == "__main__":
    try:
        main()
        disconnect()
    except KeyboardInterrupt:
        pass
