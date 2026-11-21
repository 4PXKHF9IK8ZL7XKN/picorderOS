#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
import smbus
from gpiozero import *
from evdev import UInput, AbsInfo, ecodes as e
import RPi.GPIO   

CST816D_ADDRESS = 0x15

CST816D_LCD_TOUCH_MAX_POINTS = 2

rotation = 270

TP_INT   = 4
TP_RST   = 17

# Anpassen an die tatsächlichen Maximalwerte deines Touchpanels:
MAX_X = 320
MAX_Y = 240

caps = {
    e.EV_KEY: [e.BTN_TOUCH],
    e.EV_ABS: [
        (e.ABS_X, AbsInfo(0, 0, MAX_X - 1, 0, 0, 0)),
        (e.ABS_Y, AbsInfo(0, 0, MAX_Y - 1, 0, 0, 0)),
    ],
}

class cst816d():
    def __init__(self):
        self.GPIO = RPi.GPIO
        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.setwarnings(False)
        # #Initialize I2C
        self.I2C = smbus.SMBus(1)
        # self.GPIO.setup(TP_INT, self.GPIO.IN,self.GPIO.PUD_UP)
        self.GPIO.setup(TP_RST, self.GPIO.OUT)
        # self.GPIO.add_event_detect(TP_INT,self.GPIO.FALLING,self.Int_Callback,5) 
        # pass
        self.GPIO_TP_INT = Button(TP_INT)                                                  # 使用GPIO Zero库中的Button类
        # self.GPIO_TP_RST = DigitalOutputDevice(TP_RST,active_high = True,initial_value =True)   # 使用GPIO Zero库中的DigitalOutputDevice类
        # self.GPIO_TP_INT.when_pressed = self.Int_Callback  # 中断函数
        
        self.coordinates = [{"x": 0, "y": 0} for _ in range(CST816D_LCD_TOUCH_MAX_POINTS)]
        self.point_count = 0
        self.touch_rst()
    
    def Int_Callback(self):
        self.read_touch_data()
    
    #Reset  复位    
    def touch_rst(self):
        self.GPIO.output(TP_RST, 0)  
        time.sleep(1 / 1000.0)
        self.GPIO.output(TP_RST, 1)  
        time.sleep(50 / 1000.0)
        
        
    def write_cmd(self, cmd):
        self.I2C.write_byte(CST816D_ADDRESS, data)

    def read_bytes(self, reg_addr, length):
        # 发送寄存器地址并读取多个字节
        data = self.I2C.read_i2c_block_data(CST816D_ADDRESS, reg_addr, length)
        return data
    
    def read_touch_data(self):
        TOUCH_NUM_REG = 0x02
        TOUCH_XY_REG = 0x03
        
        buf = self.read_bytes(TOUCH_NUM_REG, 1)
        
        if buf and buf[0] != 0:
            self.point_count = buf[0]
            buf = self.read_bytes(TOUCH_XY_REG, 6 * self.point_count)
            for i in range(2):
                self.coordinates[i]["x"] = 0
                self.coordinates[i]["y"] = 0
            
            if buf:
                for i in range(self.point_count):
                    self.coordinates[i]["x"] = ((buf[(i * 6) + 0] & 0x0f) << 8) + buf[(i * 6) + 1]
                    self.coordinates[i]["y"] = ((buf[(i * 6) + 2] & 0x0f) << 8) + buf[(i * 6) + 3]
    
    def get_touch_xy(self):
        point = self.point_count
        # 将触摸点数重置为 0
        self.point_count = 0

        if point != 0:
            # 返回触摸状态和坐标
            return point, self.coordinates
        else:
            # 返回 0 和空坐标列表
            return 0 , []
            
            
def rotate_touch(x, y, width, height, rotation):
    if rotation == 0:
        return x, y
    elif rotation == 90:      # im Uhrzeigersinn
        return height - 1 - y, x
    elif rotation == 180:
        return width - 1 - x, height - 1 - y
    elif rotation == 270:     # im Uhrzeigersinn
        return y, width - 1 - x
    else:
        raise ValueError("rotation muss 0, 90, 180 oder 270 sein")  


def main_routine():
    touch = cst816d()
    was_pressed = False
    pressed = False
    
    with UInput(
        events=caps,
        name="CST816D Touchscreen",
        input_props=[e.INPUT_PROP_DIRECT],
        ) as ui: 
            while True:
                touch.read_touch_data()
                point, coordinates = touch.get_touch_xy()
                # x, y, pressed = read_touch()
                if point != 0 and coordinates:
                    pressed = True
                    # Begrenze Werte auf den angegebenen Bereich.
                    xi = max(0, min(MAX_X - 1, int(coordinates[0]['x'])))
                    yi = max(0, min(MAX_Y - 1, int(coordinates[0]['y'])))
                    
                    x, y = rotate_touch(xi, yi, MAX_Y, MAX_X, rotation=270)

                    ui.write(e.EV_KEY, e.BTN_TOUCH, 1)
                    ui.write(e.EV_ABS, e.ABS_X, x)
                    ui.write(e.EV_ABS, e.ABS_Y, y)
                    ui.syn()
                    #print(f"point 1 coordinates: x={coordinates[0]['x']}, y={coordinates[0]['y']}")
                else:
                    was_pressed = False
                    ui.write(e.EV_KEY, e.BTN_TOUCH, 0)
                    ui.syn()
                was_pressed = pressed
                    
                time.sleep(0.02)

if __name__=='__main__':
	main_routine()
