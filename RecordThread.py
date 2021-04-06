#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Class Record a wav in new thread

import threading
import os
import sys

class RecordThread(threading.Thread):
   
    def __init__(self, audiofile='command.wav'):
        threading.Thread.__init__(self)

    def run(self):
        try:
            while True:
                print("开始录音...")
                os.system('arecord -d 3 -r 16000 -c 1 -t wav -f S16_LE command.wav')
                os.system('./iat_sample')
        except KeyboardInterrupt:
            exit()
    

if __name__ == '__main__':
    audio_record = RecordThread('demo.wav')
    #audio_record = RecordThread.RecordThread('record.wav')  