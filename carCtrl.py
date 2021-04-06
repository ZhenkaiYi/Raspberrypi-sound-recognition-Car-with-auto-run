#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 小车的控制代码
import atexit
import configparser
import time
import wave
import os
import sys

import threading
import numpy as np
import RPi.GPIO as GPIO
from pyaudio import PyAudio, paInt16

import voice_recognize as voice  # 导入语音识别和语音合成的函数
from motor import Motor
from sense import Sense
from sound_monitor import QAudio
from RecordThread import RecordThread
from led import LED_Light

#通过调整占空比来改变小车速度，行自行发挥    
class ChangeSpeed():
    def __init__(self):

        config = configparser.ConfigParser()
        config.read("config.ini")
        EA = config.getint("car","EA")
        EB = config.getint("car","EB")  

        self.pwm1 = EA
        self.pwm2 = EB
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.pwm1,GPIO.OUT,initial = False)   
        GPIO.setup(self.pwm2,GPIO.OUT,initial = False)   
        self.left = GPIO.PWM(self.pwm1,1000)
        self.left.start(0)
        self.right = GPIO.PWM(self.pwm2,1000)
        self.right.start(0)

    def speed_change(self, duty1, duty2):
        self.left.ChangeDutyCycle(duty1)
        self.right.ChangeDutyCycle(duty2) 


class CAR():

    #控制左右转向时间，根据转弯情况修改
    delay_tr = 0.65
    delay_tl = 0.65
    delay_30 = 1

    #开启自动避障后的转弯时间
    auto_run_tr = 0.5
    auto_run_tl = 0.5
    
    #录音采样参数
    NUM_SAMPLES = 2000
    flag = 0
    saveCount = 0

    def __init__(self):

        config = configparser.ConfigParser()
        config.read("config.ini")

        IN_1 = config.getint("car","IN1")
        IN_2 = config.getint("car","IN2")
        IN_3 = config.getint("car","IN3")
        IN_4 = config.getint("car","IN4")   

        self.change_speed = ChangeSpeed()
        self.motor = Motor(IN_1, IN_2, IN_3, IN_4)
        self.sense = Sense()
        self.qaudio = QAudio(4000)
        self.led_light = LED_Light()
       # self.audio_record = RecordThread('command.wav')
       # self.audio_record.setDaemon(True)
    def CarMove(self,direction,loop):
        if direction == 'F':
            self.motor.forward()
        elif direction == 'B':
            self.motor.backward()
        elif direction == 'R':
            self.motor.turnright()
        elif direction == 'L':
            self.motor.turnleft()
        elif direction == 'A':
            self.autorun(loop)
        elif direction == 'S':
            self.motor.stop()
        elif direction == 'E':
            self.motor.gpio_release()
            exit()
        else:
            print("The input error! please input:F,B,L,R,S")
    
#下面的代码都是用于避障的函数，里面所有的loop都是之后要用到的。    
    #the methods is used to strategy and run
    def backx(self,loop):
        while loop:
            self.motor.backward()
            time.sleep(0.5)
            self.motor.stop()
            l_d = self.sense.ask_distance_l()
            r_d = self.sense.ask_distance_r()
            if r_d > 30 and r_d >= l_d:
                #get a safe distance
                self.motor.backward()
                time.sleep(0.6)
                #turn right 90
                self.motor.turnright()
                time.sleep(self.auto_run_tr)
                break
            if l_d > 30 and l_d > r_d:
                #get a safe distance
                self.motor.backward()
                time.sleep(0.6)
                #turn left 90
                self.motor.turnleft()
                time.sleep(self.auto_run_tl)
                break
            
     #run and strategy
    def autorun(self,loop):
        self.audio_record = RecordThread()
        self.audio_record.setDaemon(True)        
        self.audio_record.start()
        try:   
            while True:
                time.sleep(0.001)
                self.change_speed.speed_change(80,80)
                #get obstacle type
                strategy = self.sense.detection()
                if strategy == "Fgo":
                    self.motor.forward()
                elif strategy == "Bgo":
                    self.backx(loop)
                elif strategy == "Lgo":
                    #turn left 90
                    self.motor.turnleft()
                    time.sleep(self.auto_run_tr)  
                elif strategy == "Rgo":
                    #turn left 90
                    self.motor.turnright()
                    time.sleep(self.auto_run_tr)

                with open('command.txt','r',encoding='utf-8') as f:
                    command = f.read()
                    if command.find('停') != -1 or command.find('止') != -1:   
                        self.led_light.led(1,True)
                        self.led_light.led(2,False)              
                        print("自动避障停止")
                        break

        except KeyboardInterrupt:
                print("")
                print("stop the car")
                self.motor.gpio_release()
                exit()

    # Analysis command  通过操作文件识别命令  
    def recognizeCommand(self, filename):
        enStop = 0
        enRun = 1
        enBack = 2
        enLeft = 3
        enRight = 4
        autoRun = 5
        car_State = 0
        breakRecordFlag=0
        self.motor.stop()
        file = filename
        f = open(file,'r',)
        out = f.read()
        command = out
        f.close()   # close file aviod exception
        #print(command)
        if  command.find('前') != -1 :#or command.find('向') != -1:
            print("向前")
            car_State = 1
        elif command.find('后') != -1 :#or  command.find('向') != -1:
            print ("向后")
            car_State = 2
        elif command.find('左') != -1 :#and command.find('转') != -1:
            print ('左转弯')
            car_State = 3
        elif command.find('右') != -1 :#and command.find('转') != -1:
            print ('右转弯')
            car_State = 4
        elif command.find('自') != -1 and command.find('动') != -1 or command.find('避') != -1 or command.find('障') != -1:
            car_State = 5
            print ('自动避障')
        elif command.find('拜') != -1:
            breakRecordFlag = 1
        elif command.find('识') != -1 and command.find('别') != -1 and command.find('错') != -1 and command.find('误') != -1:
            print ('语音识别出错')
        else:
            print ('指令错误')
            car_State = 0
        #向前
        if car_State == enRun:
            print('向前！')
            self.motor.forward()
            self.change_speed.speed_change(80,80)
            time.sleep(self.delay_30)
            car_State = 0
        #向后
        elif car_State == enBack :
            self.motor.backward()
            self.change_speed.speed_change(80,80)
            time.sleep(self.delay_30)
            car_State = 0
        #左转弯
        elif car_State == enLeft :
            self.motor.turnleft()
            self.change_speed.speed_change(80,80)
            time.sleep(self.delay_tr)
            car_State = 0
        #右转弯
        elif car_State == enRight :
            self.motor.turnright()
            self.change_speed.speed_change(80,80)
            time.sleep(self.delay_tr)
            car_State = 0
        #自动避障
        elif car_State == autoRun:
            self.led_light.led(1,False)
            self.led_light.led(2,True)
            self.autorun(True)
        #stop
        elif car_State == enStop:
            self.motor.stop()
        else:
            self.motor.stop()

        return breakRecordFlag
    
    #调用科大讯飞语音识别SDK，识别率一般
    def monitor(self):
        try:
            while True:
                self.qaudio.sound_detect()
                breakFlag = self.recognizeCommand('result.txt') #Analysis command       
                self.motor.stop() 
                if breakFlag == 1:
                    breakFlag = 0
                    break

        except KeyboardInterrupt:
            print('Car Stop!')
            self.qaudio.close()
            self.motor.gpio_release()
            GPIO.cleanup()
            exit()
            
    #save data to filename  
    def save_wave_file(self,filename,data):  
        wf = wave.open(filename,'wb')
        wf.setnchannels(1)      #set channel
        wf.setsampwidth(2)      #采样字节  1 or 2
        wf.setframerate(16000)  #采样频率  8K or 16K
        wf.writeframes(b"".join(data))
        wf.close()
    # baidu SST  check the voice volumn record 5s
    
    def monitor_baidu(self): 
        self.led_light.led(1,True)
        pa = PyAudio()
        stream = pa.open(format = paInt16,
                        channels=1,
                        rate=16000,
                        input=True,
                        frames_per_buffer=self.NUM_SAMPLES)
        print('开始缓存录音')
        audioBuffer = []
        rec = []
        audioFlag = False
        timeFlag = False
        try:
            while True:   
                data = stream.read(self.NUM_SAMPLES,exception_on_overflow = False)
                audioBuffer.append(data)                       #录音源文件
                audioData = np.fromstring(data,dtype=np.short) #字符串创建矩阵
                largeSampleCount = np.sum(audioData > 2000)
                temp = np.max(audioData)
                print(temp)
                if temp > 3000 and audioFlag == False:  #3000 according different mic
                    audioFlag = True #开始录音
                    print("检测到语音信号，开始录音")
                    begin = time.time()
                    print(temp)
                if audioFlag:
                    end = time.time()
                    if end-begin > 5:
                        timeFlag = 1 #5s录音结束
                    if largeSampleCount > 20:
                        self.saveCount = 3
                    else:
                        self.saveCount -=1
                    if self.saveCount <0:
                        self.saveCount =0
                    if self.saveCount >0:
                        rec.append(data)
                    else:
                        if len(rec) >0 or timeFlag:
                            
                            self.save_wave_file('result.wav',rec) # 保存检测的语音
                            voice.identify_synthesize('result.wav') # 调用百度语音实现语音识别和语音合成
                            
                            rec = []
                            audioFlag = False
                            timeFlag = 0
                            
                            breakFlag=self.recognizeCommand('result.txt')  #Analysis command
                            self.motor.stop()
                            if breakFlag == 1:
                                breakFlag = 0
                                break
            print("The end!")
            stream.stop_stream()
            stream.close()
            pa.terminate()
            GPIO.cleanup()
            sys.exit()                  
        except KeyboardInterrupt:
            stream.stop_stream()
            stream.close()
            pa.terminate()
            GPIO.cleanup()
            sys.exit()          

if __name__=='__main__':
    RaspCar=CAR()
    while(True):
        RaspCar.monitor_baidu()                 #调用百度语音识别api
        #RaspCar.monitor()                      #调用科大讯飞语音识别api


        #以下代码用作手动控制和测试，输入指令控制小车动作
        direction = input("Please input direction:")
        print(direction)
        RaspCar.CarMove(direction,True)   
        RaspCar.change_speed.speed_change(60,60)
        time.sleep(0.8)
        direction = "S"
        RaspCar.CarMove(direction,True)
