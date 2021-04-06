#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# LED指示灯

import RPi.GPIO as GPIO
import time
import configparser

class LED_Light(object):
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.led1 = config.getint("led","LED1")
        self.led2 = config.getint("led","LED2") 

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.led1,GPIO.OUT,initial = True)   
        GPIO.setup(self.led2,GPIO.OUT,initial = True)  

    def led(self, led_num, state):
        if led_num == 1 and state == True:
             GPIO.output(self.led1,False)
        elif led_num == 1 and state == False:
            GPIO.output(self.led1,True)
        if led_num == 2 and state == True:
             GPIO.output(self.led2,False)
        elif led_num == 2 and state == False:
            GPIO.output(self.led2,True)   
    def led_gpio_release(self):
        self.led(1,False) 
        self.led(1,False) 
        GPIO.cleanup()

if __name__ == '__main__':
    led_light = LED_Light()
    led_light.led(1, True)
    time.sleep(2)
    led_light.led_gpio_release()