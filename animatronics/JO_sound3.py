#!/usr/bin/python

import alsaaudio
import wave
import sys
import time
import struct
import math

channels = 2
rate = 44000
size = 1024

out_stream = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NORMAL, 'default')
out_stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
out_stream.setchannels(channels)
out_stream.setrate(rate)
out_stream.setperiodsize(size)

file = open("whizzer.wav", "rb")

SHORT_NORMALIZE = (1.0/32768.0)
CHUNK = 1024
swidth = 2
thres = 30
mouthpos = 0.0

# instantiate PyAudio (1)

def rms(frame):
    count = len(frame)/swidth
    format = "%dh"%(count)
    shorts = struct.unpack( format, frame )

    sum_squares = 0.0
    for sample in shorts:
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n
        rms = math.pow(sum_squares/count,0.5);
        return rms * 10000

data = file.read(size)

def moveMouth(sig):
    global mouthpos
    if mouthpos == 0.0:
        if sig >= thres:
            print("Opening Mouth")
            mouthpos = 0.5
    if mouthpos == 0.5:
        if sig >= thres:
            print("Closing Mouth")
            mouthpos = 0.0



while data:
    out_stream.write(data)
    data = file.read(size)
    moveMouth(rms(data))

