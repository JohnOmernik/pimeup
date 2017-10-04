#!/usr/bin/python
import cwiid
import sys
import gevent
import time
import random
import json
import requests
import os
import socket
from collections import OrderedDict
import RPi.GPIO as GPIO
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

WHOAMI = socket.gethostname()
WHATAMI = os.path.basename(__file__).replace(".py", "")

# Pins for Relay Box we start with -1 which means
pins = [-1, 23, -1, 24, -1, 25, -1, 17, -1,  27]

for pin in pins:
    if pin > 0: # Don't "setup" if pin is -1
        GPIO.setup(pin, GPIO.OUT)
lasthb = 0
hbinterval = 30

mesg = False
rpt_mode = 0
wiimote = None
connected = False
curidx = 0
rumble = 0 

def main():

    logevent("startup", "startup", "Just started and ready to run")
    #Connect to address given on command-line, if present
    print 'Put Wiimote in discoverable mode now (press 1+2)...'
    global wiimote
    global rpt_mode
    global connected
    global strip
    global rumble


    print("Trying Connection")
    print ("Press 1+2")
    while not connected:
        try:
            wiimote = cwiid.Wiimote()
            print("Connected!")
            connected = True
            rumble ^= 1
            wiimote.rumble = rumble
            time.sleep(2)
            rumble ^= 1
            wiimote.rumble = rumble
            logevent("wii", "connect", "Wii remote just synced up")
        except:
            print("Trying Again, please press 1+2")
            time.sleep(2)


    wiimote.mesg_callback = callback

    print("For LED we enable Button")
    rpt_mode ^= cwiid.RPT_BTN

    # Enable the messages in callback
    wiimote.enable(cwiid.FLAG_MESG_IFC);
    wiimote.rpt_mode = rpt_mode

    gevent.joinall([
        gevent.spawn(normal)
    ])


def normal():
    global wiimote
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
    wiimote.close()
    sys.exit()

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




def handle_buttons(buttons):
    global curidx
    global pins
    curval = pins[curidx]
    bPress = False
    
    if (buttons & cwiid.BTN_A):
        bPress = True
        if curidx == len(pins) - 1:
            nextidx = 0
        else:
            nextidx =  curidx + 1
    elif (buttons & cwiid.BTN_2):
        bPress = True
        nextidx = 1
    elif (buttons & cwiid.BTN_1):
        bPress = True
        nextidx = 0

    if bPress == True:
        nextval = pins[nextidx]
        if curval > 0:
            GPIO.output(curval, False)
        if nextval > 0:
            GPIO.output(nextval, True)
        #Button Pressed Log event!
        logevent("index_change", OrderedDict({"previdx": curidx, "prevval": curval, "newidx": nextidx, "newval": nextval}), "Event list index changed from %s to %s" % (curidx, nextidx))
        curidx = nextidx        
        

def callback(mesg_list, time):
    
    for mesg in mesg_list:
        if mesg[0] == cwiid.MESG_BTN:
            handle_buttons(mesg[1])
#            print("Time: %s" % time)
#            print 'Button Report: %.4X' % mesg[1]
        else:
            print 'Unknown Report'



if __name__ == "__main__":
    main()
