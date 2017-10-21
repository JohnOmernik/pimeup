#!/usr/bin/python
import time
import random
import sys
import alsaaudio
import json
import requests
import os
import cStringIO
import socket
from collections import OrderedDict

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

    global lasthb
    global hbinterval

    sounds = [0, 0, 0]
    channels = 2
    rate = 44100
    size = 1024

    out_stream = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NORMAL, 'default')
    out_stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    out_stream.setchannels(channels)
    out_stream.setrate(rate)
    out_stream.setperiodsize(size)


    soundfiles = ['/home/pi/spencer_young.wav', '/home/pi/spencer2.wav', '/home/pi/spencer3.wav']
    memsound = {}
    print("Loading Sound files to memory")
    for sf in soundfiles:
        f = open(sf, "rb")
        sfdata = f.read()
        f.close()
        memsound[sf] = cStringIO.StringIO(sfdata)

    while True:
        curfile = random.choice(soundfiles)
        curtime = int(time.time())
        if curtime - lasthb > hbinterval:
            logevent("heartbeat", "Working", "Cur Childhood sound file: %s" % curfile)
            lasthb = curtime
        print("Playing %s frm memory" % curfile)
        memsound[curfile].seek(0)
        data = memsound[curfile].read(size)
        while data:
            out_stream.write(data)
            data = memsound[curfile].read(size)

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
