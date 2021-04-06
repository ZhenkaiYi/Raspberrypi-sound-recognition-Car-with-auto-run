#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 传感器探测障碍物类型
import configparser
import time

import RPi.GPIO as GPIO

from motor import Motor
from steering import Steering
from ultrasonic import Ultrasonic


#Define the number of all the GPIO taht used for 4wd car
class Sense():
    
    def __init__(self):

        config = configparser.ConfigParser()
        config.read("config.ini")
        
        trigger = config.getint("ultrasonic","Trigger")
        echo = config.getint("ultrasonic","Echo")
        
        servoNum = config.getint("steering","servoNum")
        InitPosition = config.getint("steering","InitPosition")
        minPosition = config.getint("steering","MinPosition")
        maxPosition = config.getint("steering","maxPosition")
        speed = config.getint("steering","speed")

        self.IN_1 = config.getint("car","IN1")
        self.IN_2 = config.getint("car","IN2")
        self.IN_3 = config.getint("car","IN3")
        self.IN_4 = config.getint("car","IN4")    

        self.Sonic = Ultrasonic(trigger,echo)
        self.Servo = Steering(servoNum, InitPosition, minPosition, maxPosition, speed)
        self.motor = Motor(self.IN_1, self.IN_2, self.IN_3, self.IN_4)

    #get obstacles type   
    def detection(self):
        distance = self.ask_distance()
        #NO Obstacles or 35cm safe distance  type 0
        if distance >= 30:
            return "Fgo"
        #Obstacles ahead
        #self.Infrared.check_distance() == "Warning"
        else :
            l_d = self.ask_distance_l()
            r_d = self.ask_distance_r()
        #Obstacles ahead&&right  =safe       type a
            if ((l_d>=30)and(r_d>=30)):
                if(l_d > r_d):
                    return "Lgo"
                else:
                    return "Rgo"
        #Obstacles ahead&&right  R>L         type b
            elif ((l_d<=30)
                and(r_d>30)):
                return "Rgo"
        #Obstacles ahead&&right  L>R         type c
            elif ((l_d>30)
                and(r_d<=30)):
                return "Lgo"
        #Obstacles ahead&&right  L&R<safe         type d
            elif ((l_d<30)
                and(r_d<30)):
                return "Bgo"
    
    def ask_distance(self):
        self.Servo.reset()     
        return self.Sonic.get_distance()
    def ask_distance_l(self):
        self.motor.stop()
        self.Servo.turnleft()
        time.sleep(0.1)
        distance = self.Sonic.get_distance()
        self.Servo.reset()
        return distance
    def ask_distance_r(self):
        self.motor.stop()
        self.Servo.turnright()
        time.sleep(0.1)
        distance = self.Sonic.get_distance()
        self.Servo.reset()
        return distance
         
if __name__ == '__main__':
    t = Sense()
    while True:
        s=t.detection()
        print(s)
        time.sleep(0.5)
