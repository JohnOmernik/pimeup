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

#m = alsaaudio.Mixer('PCM')
#current_volume = m.getvolume() # Get the current Volume
#print("Cur Vol: %s " % current_volume)
#m.setvolume(100) # Set the volume to 70%.
#current_volume = m.getvolume() # Get the current Volume
#print("Cur Vol: %s " % current_volume)



numpixels = 60 # Number of LEDs in strip
# Here's how to control the strip from any two GPIO pins:
datapin   = 23
clockpin  = 24

colors = [  0x0000FF, 0xFF0000,  0x00FFFF, 0x000000]

curcolor = random.choice(colors)
colortimer = -1
defaultBright = 255

strip = Adafruit_DotStar(numpixels, datapin, clockpin)
strip.setBrightness(defaultBright)
strip.begin()           # Initialize pins for output

hi_thres = 100

beat = False
def main():
    global strip
    global curcolor
    global colortimer
    sounds = [0, 0, 0]
    playsound = False

    if playsound == True:
        channels = 2
        rate = 44100
        size = 1024
        out_stream = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NORMAL, 'default')
        out_stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        out_stream.setchannels(channels)
        out_stream.setrate(rate)
        out_stream.setperiodsize(size)

    strip.setBrightness(defaultBright)
    setAllLEDS(strip, [curcolor])
    strip.show()

    soundfiles = ['/home/pi/heartbeat.wav']

    while True:
        if playsound == True:
            curfile = random.choice(soundfiles)
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

                if sounds_avg > hi_thres:
                    newcolor = curcolor
                    while newcolor == curcolor:
                        newcolor = random.choice(colors)
                    setAllLEDS(strip, [newcolor])
                    curcolor = newcolor
            curstream.close()
        else:
            newcolor = curcolor
            while newcolor == curcolor:
                newcolor = random.choice(colors)
            setAllLEDS(strip, [newcolor])
            curcolor = newcolor

            if colortimer == -1:
                mysleep = random.randint(2, 10)
            else:
                mysleep = colortimer

#            print("Sleeping for %s" % mysleep)
            time.sleep(mysleep)

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
