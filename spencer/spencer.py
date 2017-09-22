#!/usr/bin/python
#Gateway
import time
import random
import sys
import alsaaudio
import wave
import sys
import struct
import math
from dotstar import Adafruit_DotStar

m = alsaaudio.Mixer('PCM')
current_volume = m.getvolume() # Get the current Volume
#print("Cur Vol: %s " % current_volume)
m.setvolume(100) # Set the volume to 70%.
current_volume = m.getvolume() # Get the current Volume
#print("Cur Vol: %s " % current_volume)



numpixels = 60 # Number of LEDs in strip
# Here's how to control the strip from any two GPIO pins:
datapin   = 23
clockpin  = 24
defaultColor = 0x990000
defaultBright = 128
flashColor = 0xFF9933
flashBright = 255

strip     = Adafruit_DotStar(numpixels, datapin, clockpin)
strip.setBrightness(defaultBright)
strip.begin()           # Initialize pins for output

hi_thres = 6
low_thres = 5

beat = False
def main():
    global strip
    global beat

    sounds = [0, 0, 0]


    channels = 1
    rate = 44100
    size = 1024
    out_stream = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NORMAL, 'default')
    out_stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    out_stream.setchannels(channels)
    out_stream.setrate(rate)
    out_stream.setperiodsize(size)

    strip.setBrightness(defaultBright)
    setAllLEDS(strip, [defaultColor])
    strip.show()

    thunderfiles = ['/home/pi/haunt_electric.wav']

    while True:
        curfile = random.choice(thunderfiles)
        curstream = open(curfile, "rb")

        data = curstream.read(size)
        tstart = 0
        while data:
            tstart += 1
            out_stream.write(data)
            data = curstream.read(size)
            rmsval = rms(data)
            sounds.append(rmsval)
            ug = sounds.pop(0)
            try:
                sounds_avg = sum(sounds) / len(sounds)
            except:
                sounds_avg = 0
#            print(sounds_avg)
            if sounds_avg > hi_thres and beat == False:
                strip.setBrightness(flashBright)
                setAllLEDS(strip, [flashColor])
                beat = True 
            if sounds_avg < low_thres and beat == True:
                strip.setBrightness(defaultBright)
                setAllLEDS(strip, [defaultColor])
                beat = False
        curstream.close()

    sys.exit(0)

def setAllLEDS(strip, colorlist):
    for x in range(numpixels):
        strip.setPixelColor(x, colorlist[0])
    strip.show()

def rms(frame):
    SHORT_NORMALIZE = (1.0/32768.0)
    CHUNK = 1024
    swidth = 2

    count = len(frame)/swidth
    format = "%dh"%(count)
    shorts = struct.unpack( format, frame )

    sum_squares = 0.0
    for sample in shorts:
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n
        rms = math.pow(sum_squares/count,0.5);
        return rms * 10000



if __name__ == "__main__":
    main()
