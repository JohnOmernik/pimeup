#!/usr/bin/python
import time
import random
import sys
import alsaaudio
import wave
import struct
import math
import json
import requests
import os
import socket
import gevent
from collections import OrderedDict
#from dotstar import Adafruit_DotStar



WHOAMI = socket.gethostname()
WHATAMI = os.path.basename(__file__).replace(".py", "")

#m = alsaaudio.Mixer('PCM')
#current_volume = m.getvolume() # Get the current Volume
#print("Cur Vol: %s " % current_volume)
#m.setvolume(100) # Set the volume to 70%.
#current_volume = m.getvolume() # Get the current Volume
#print("Cur Vol: %s " % current_volume)

hbinterval = 30
lasthb = 0


def main():
    logevent("startup", "startup", "Just started and ready to run")

    gevent.joinall([
        gevent.spawn(normal),
        gevent.spawn(PlaySound),
    ])

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



def normal():
    global lasthb
    global hbinterval
    try:
        while True:
            curtime = int(time.time())
            if curtime - lasthb > hbinterval:
                logevent("heartbeat", "Working", "Standard HB")
                lasthb = curtime
            gevent.sleep(0.001)
    except KeyboardInterrupt:
        print("Exiting")
    sys.exit()

def PlaySound():
    sounds = [0, 0, 0]


    channels = 2
    rate = 44100
    size = 1024
    out_stream = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NORMAL, 'default')
    out_stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    out_stream.setchannels(channels)
    out_stream.setrate(rate)
    out_stream.setperiodsize(size)

  #  strip.setBrightness(defaultBright)
  #  setAllLEDS(strip, [defaultColor])
  #  strip.show()

    thunderfiles = ['/home/pi/spencer_young.wav', '/home/pi/spencer2.wav', '/home/pi/spencer3.wav']

    while True:
        curfile = random.choice(thunderfiles)
        curstream = open(curfile, "rb")
        data = curstream.read(size)
        tstart = 0
        while data:
            tstart += 1
            out_stream.write(data)
            data = curstream.read(size)
        curstream.close()
	gevent.sleep(0.001)

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
