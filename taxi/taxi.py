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



    #Connect to address given on command-line, if present
    print 'Put Wiimote in discoverable mode now (press 1+2)...'
    global wiimote
    global rpt_mode
    global connected
    global strip
    # Set the first pixel to red to show not connected



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
            gevent.sleep(0.01)
            curtime = int(time.time())
            if curtime - lasthb > hbinterval:
                curts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(curtime))
                outrec = OrderedDict()
                outrec['ts'] = curts
                outrec['host'] = WHOAMI
                outrec['script'] = WHATAMI
                outrec['event_type'] = "battery"
                outrec['event_data'] = wiimote.state['battery']
                outrec['event_desc'] = "Wii remote battery status update"
                sendlog(outrec, False)
                outrec = None
                lasthb = curtime
    except KeyboardInterrupt:
        print("Exiting")
    wiimote.close()
    sys.exit()


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
        curtime = int(time.time())
        curts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(curtime))
        outrec = OrderedDict()
        outrec['ts'] = curts
        outrec['host'] = WHOAMI
        outrec['script'] = WHATAMI
        outrec['event_type'] = "index_change"
        outrec['event_data'] = OrderedDict({"previdx": curidx, "prevval": curval, "newidx": nextidx, "newval": nextval})
        outrec['event_desc'] = "Event list index changed from %s to %s" % (curidx, nextidx)
        sendlog(outrec, False)
        outrec = None


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
