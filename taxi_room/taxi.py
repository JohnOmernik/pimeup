#!/usr/bin/python
import cwiid
import sys
import gevent
import time
import random

import RPi.GPIO as GPIO
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)


# Pins for Relay Box we start with -1 which means
pins = [-1, 23, 24, 25, 17, 27, 22]

for pin in pins:
    if pin > 0: # Don't "setup" if pin is -1
        GPIO.setup(pin, GPIO.OUT)

mesg = False
rpt_mode = 0
wiimote = None
connected = False
curidx = 0


def main():



    #Connect to address given on command-line, if present
    print 'Put Wiimote in discoverable mode now (press 1+2)...'
    global wiimote
    global rpt_mode
    global connected
    global strip
    # Set the first pixel to red to show not connected


    print("Trying Connection")
    print ("Press 1+2")
    while not connected:
        try:
            wiimote = cwiid.Wiimote()
            print("Connected!")
            connected = True
        except:
            print("Trying Again, please press 1+2")
            time.sleep(2)

    wiimote.mesg_callback = callback

    print("For Relay  we enable Button")
    rpt_mode ^= cwiid.RPT_BTN

    # Enable the messages in callback
    wiimote.enable(cwiid.FLAG_MESG_IFC);
    wiimote.rpt_mode = rpt_mode

    gevent.joinall([
        gevent.spawn(normal)
    ])


def normal():
    global strip
    global wiimote
    try:
        while True:
            pass
            gevent.sleep(0.5)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Exiting")
    wiimote.close()
    sys.exit()



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
