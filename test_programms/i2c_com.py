#!/bin/python
#  Raspberry Pi I2C Master
#  Raspberry Pi Master for Arduino Slave
#  i2c_master_pi.py
#  Connects to Arduino via I2C
  
#  DroneBot Workshop 2019
#  https://dronebotworkshop.com
 
from smbus2 import SMBus
 
addr = 0x1b # bus address
bus = SMBus(1) # indicates /dev/ic2-1

numb = 1
out_str = ""
array_return = []

print ("Send Request")
bus.write_byte(addr, 1) # switch it on
with SMBus(1) as bus:
    # Read a block of 16 bytes from address 80, offset 0
    block = bus.read_i2c_block_data(addr, 0, 16)
    # Returned value is a list of 16 bytes
    for item in block:
        array_return.append(chr(item))
    out_str = out_str.join(array_return)
    print(out_str)
bus.close()


