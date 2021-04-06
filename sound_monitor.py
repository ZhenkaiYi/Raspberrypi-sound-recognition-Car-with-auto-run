#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#声音检测，然后调用科大讯飞SDK进行语音识别
import pyaudio
import numpy as np
import time
import os
import sys

class QAudio():

    CHUNK = 512
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 48000

    def __init__(self, dense):
        self.paudio = None
        self.stream = None
        self.dense = dense

    def open(self):

        self.paudio = pyaudio.PyAudio()
        self.stream = self.paudio.open(format=self.FORMAT,
                                       channels=self.CHANNELS,
                                       rate=self.RATE,
                                       input=True,
                                       frames_per_buffer=self.CHUNK)

    def read(self):
        data = self.stream.read(self.CHUNK)
        return data

    def close(self):
        self.stream.close()
        self.paudio.terminate()


    def sound_detect(self):
        self.open()
        os.close(sys.stderr.fileno())
        print("开始聆听...")
        cnt = 0
        try:
            while True:
                data = self.read()
                audio_data = np.fromstring(data, dtype=np.short)
                temp = np.max(audio_data)
                print(temp)     
                start = time.time()                    
                if(temp>self.dense):
                    end = time.time()
                    if(end - start < 0.01):
                        cnt += 1
                    else:
                        cnt -= 1
                if(cnt >= 10):
                    cnt = 0
                    print("开始录音...")
                    os.system('arecord -d 2 -r 16000 -c 1 -t wav -f S16_LE command.wav')
                    os.system('./iat_sample')
                    self.close()
                    break
                #print(f'当前声音强度值： {"*"*(temp//100)}')
        except KeyboardInterrupt:
                self.close()
if __name__ == '__main__':
    qa = QAudio(4000)
    qa.sound_detect()
    with open('./command.txt', 'r',encoding='utf-8') as fp:
        print(fp.read())
