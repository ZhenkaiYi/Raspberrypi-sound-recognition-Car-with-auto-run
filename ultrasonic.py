#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#超声波代码
import RPi.GPIO as GPIO
import time


class Ultrasonic():
    def __init__(self,trig_pin,echo_pin):
        self.trig_pin=trig_pin
        self.echo_pin=echo_pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.trig_pin,GPIO.OUT,initial=False)
        GPIO.setup(self.echo_pin,GPIO.IN)

    def get_distance(self):
        GPIO.output(self.trig_pin,GPIO.LOW)
        time.sleep(0.000002)
        GPIO.output(self.trig_pin,GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self.trig_pin,GPIO.LOW)

        while GPIO.input(self.echo_pin) == 0:
            pass
        t1=time.time()
        while GPIO.input(self.echo_pin) == 1:
            pass
        t2=time.time()
        distance=(t2-t1)*340/2*100
        return distance 

if __name__ == '__main__':
    try:
        while True:
            ultr = Ultrasonic(20,21)
            dis = ultr.get_distance()
            print(dis)
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()