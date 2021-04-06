#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#小车电机控制代码

import RPi.GPIO as GPIO


class Motor():
         
    def __init__(self, in_1, in_2, in_3, in_4):

        self.IN1 = in_1
        self.IN2 = in_2
        self.IN3 = in_3
        self.IN4 = in_4

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)  #avoid GPIO warning
        GPIO.setup(self.IN1,GPIO.OUT,initial = False)
        GPIO.setup(self.IN2,GPIO.OUT,initial = False)
        GPIO.setup(self.IN3,GPIO.OUT,initial = False)
        GPIO.setup(self.IN4,GPIO.OUT,initial = False)     

     
    def stop(self):
        #Rest all the GPIO as LOW
        GPIO.output(self.IN1,False)
        GPIO.output(self.IN2,False)
        GPIO.output(self.IN3,False)
        GPIO.output(self.IN4,False)
        
    def forward(self):
 #       self.reset()
        GPIO.output(self.IN1,True)
        GPIO.output(self.IN2,False)
        GPIO.output(self.IN3,True)
        GPIO.output(self.IN4,False)
    
    def backward(self):
 #       self.reset()
        GPIO.output(self.IN1,False)
        GPIO.output(self.IN2,True)
        GPIO.output(self.IN3,False)
        GPIO.output(self.IN4,True)
    
    def turnright(self):
 #       self.reset()
        GPIO.output(self.IN1,True)
        GPIO.output(self.IN2,False)
        GPIO.output(self.IN3,False)
        GPIO.output(self.IN4,True)
    
    def turnleft(self):
 #       self.reset()
        GPIO.output(self.IN1,False)
        GPIO.output(self.IN2,True)
        GPIO.output(self.IN3,True)
        GPIO.output(self.IN4,False)
    
    def gpio_release(self):
        GPIO.output(self.IN1,False)
        GPIO.output(self.IN2,False)
        GPIO.output(self.IN3,False)
        GPIO.output(self.IN4,False)
        GPIO.cleanup()        

    #def set_speed(self,speed1,speed2):
    #    self.left = GPIO.PWM(self.pwm1,1000)
    #    self.left.start(speed1)
    #    self.right = GPIO.PWM(self.pwm2,1000)
    #    self.right.start(speed2)

    #def change_speed(self, duty1, duty2):
    #    self.left.ChangeDutyCycle(duty1)
    #    self.right.ChangeDutyCycle(duty2) 
#Define the number of all the GPIO taht used for 4wd car