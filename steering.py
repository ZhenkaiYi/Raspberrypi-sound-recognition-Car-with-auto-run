#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 超声波舵机的代码
import RPi.GPIO as GPIO
import time
import atexit
# ONE servo class

class Steering:
    max_delay = 0.2
    min_delay = 0.02  
    
    def __init__(self,channel,init_position,min_angle,max_angle,speed):
        self.channel = channel
        self.init_position = init_position
        self.position = init_position
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.speed = speed

        atexit.register(GPIO.cleanup)
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.channel,GPIO.OUT,initial = False)
        
        self.pwm = GPIO.PWM(self.channel,50)  #PWM  50hz
        self.pwm.start(2.5+self.position/360*20) #init_position
        time.sleep(Steering.max_delay)
        self.pwm.ChangeDutyCycle(0)     #clean duty cycle,avoid servo motor jitter
        time.sleep(Steering.min_delay)
        
    def forwardRotation(self):
        print("current position1: "+ str(self.position))
        
        if (self.position+self.speed) <= self.max_angle:
            self.position = self.position + self.speed
            self.pwm.ChangeDutyCycle(2.5+self.position/360*20)
            time.sleep(Steering.min_delay)
            self.pwm.ChangeDutyCycle(0)   #clean duty cycle,avoid servo motor jitter
            time.sleep(Steering.min_delay)
        print("current position2: "+ str(self.position))    
            
    def reverseRotation(self):
        print("current position1: "+ str(self.position))
        
        if (self.position-self.speed) >= self.min_angle:
            self.position = self.position - self.speed
            self.pwm.ChangeDutyCycle(2.5+self.position/360*20)
            time.sleep(Steering.min_delay)
            self.pwm.ChangeDutyCycle(0)   #clean duty cycle,avoid servo motor jitter
            time.sleep(Steering.min_delay)
        print("current position2: "+ str(self.position))
    
    def reset(self):
        
        self.position = self.init_position
        self.pwm.ChangeDutyCycle(2.5+self.position/360*20)
        time.sleep(Steering.max_delay)
        self.pwm.ChangeDutyCycle(0)      #clean duty cycle,avoid servo motor jitter
        time.sleep(Steering.min_delay)
    
    def turnleft(self):
        
        self.position = self.max_angle
        self.pwm.ChangeDutyCycle(2.5+self.position/360*20)
        time.sleep(Steering.max_delay)
        self.pwm.ChangeDutyCycle(0)      #clean duty cycle,avoid servo motor jitter
        time.sleep(Steering.min_delay)

    def turnright(self):
        
        self.position = self.min_angle
        self.pwm.ChangeDutyCycle(2.5+self.position/360*20)
        time.sleep(Steering.max_delay)
        self.pwm.ChangeDutyCycle(0)      #clean duty cycle,avoid servo motor jitter
        time.sleep(Steering.min_delay)

    def stop(self):
        self.pwm.stop()
        time.sleep(Steering.max_delay)
        GPIO.cleanup()
        
            
if __name__ == "__main__":
    steer = Steering(19,90,0,180,10)
    while True:
        direction = input("Please input direction: ")
        if direction == "F":
            steer.forwardRotation()
        elif direction == "R":
            steer.reverseRotation()
        elif direction == "S":
            steer.stop()
        elif direction == "TR":
            steer.turnright()
        elif direction == "TL":
            steer.turnleft()
        elif direction == "RE":
            steer.reset()
