#!/usr/bin/python
import time
import random
import sys
import alsaaudio
import wave
import struct
import json
import socket
import requests
import cStringIO
import os
from collections import OrderedDict
import math
from dotstar import Adafruit_DotStar


WHOAMI = socket.gethostname()
WHATAMI = os.path.basename(__file__).replace(".py", "")

#m = alsaaudio.Mixer('PCM')
#current_volume = m.getvolume() # Get the current Volume
#print("Cur Vol: %s " % current_volume)
#m.setvolume(100) # Set the volume to 70%.
#current_volume = m.getvolume() # Get the current Volume
#print("Cur Vol: %s " % current_volume)

numpixels = 120 # Number of LEDs in strip
# Here's how to control the strip from any two GPIO pins:
datapin   = 23
clockpin  = 24
defaultColor = 0x000099
defaultBright = 128
flashColor = 0xFFFFFF
flashBright = 128
lasthb = 0
hbinterval = 30
strip     = Adafruit_DotStar(numpixels, datapin, clockpin)
strip.setBrightness(defaultBright)
strip.begin()           # Initialize pins for output

hi_thres = 50
low_thres = 40
beat = False

def main():
    global strip
    global beat
    global lasthb
    global hbinterval

    logevent("startup", "startup", "Just started and ready to run")

    strip.setBrightness(defaultBright)
    setAllLEDS(strip, [defaultColor])
    strip.show()
    sounds = [0, 0, 0]

    channels = 2
    rate = 44100
    size = 1024
    out_stream = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NORMAL, 'default')
    out_stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    out_stream.setchannels(channels)
    out_stream.setrate(rate)
    out_stream.setperiodsize(size)

    soundfiles = ['/home/pi/torture_audio.wav']
    memsound = {}
    print("Loading Sound files to memory")
    for sf in soundfiles:
        f = open(sf, "rb")
        sfdata = f.read()
        f.close()
        memsound[sf] = cStringIO.StringIO(sfdata)


    while True:
        curtime = int(time.time())
        if curtime - lasthb > hbinterval:
            logevent("heartbeat", "Working", "Standard HB")
            lasthb = curtime

        curfile = random.choice(soundfiles)
        memsound[curfile].seek(0)
        data = memsound[curfile].read(size)
        while data:
            out_stream.write(data)
            data = memsound[curfile].read(size)
            rmsval = rms(data)
            sounds.append(rmsval)
            ug = sounds.pop(0)
            try:
                sounds_avg = sum(sounds) / len(sounds)
            except:
                sounds_avg = 0
            if sounds_avg > hi_thres and beat == False:
                strip.setBrightness(flashBright)
                setAllLEDS(strip, [flashColor])
                beat = True
            if sounds_avg < low_thres and beat == True:
                strip.setBrightness(defaultBright)
                setAllLEDS(strip, [defaultColor])
                beat = False

    sys.exit(0)


def logevent(etype, edata, edesc):
    global WHOAMI
    global WHATAMI

    curtime = int(time.time())
    curts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(curtime))
    outrec = OrderedDict()
    outrec['ts'] = curts
    outrec['host'] = WHOAMI
    outrec['script'] = WHATAMI
    outrec['event_type'] = etype
    outrec['event_data'] = edata
    outrec['event_desc'] = edesc
    sendlog(outrec, False)
    outrec = None


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

def sendlog(log, debug):
    logurl = "http://hauntcontrol:5050/hauntlogs"
    try:
        r = requests.post(logurl, json=log)
        if debug:
            print("Posted to %s status code %s" % (logurl, r.status_code))
            print(json.dumps(log))
    except:
        if debug:
            print("Post to %s failed timed out?" % logurl)
            print(json.dumps(log))




if __name__ == "__main__":
    main()
