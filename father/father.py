#!/usr/bin/python
import cwiid
import sys
import gevent
import time
import json
import datetime
import atexit
from collections import OrderedDict
import random
from dotstar import Adafruit_DotStar
import socket
import requests
import os
import alsaaudio
import wave
import struct
import math

WHOAMI = socket.gethostname()
WHATAMI = os.path.basename(__file__).replace(".py", "")

import RPi.GPIO as GPIO
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 #set GPIO Pins
GPIO_AIR = 16
GPIO_LIGHTS = 13
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_AIR, GPIO.OUT)
GPIO.setup(GPIO_LIGHTS, GPIO.OUT)

mesg = False
rpt_mode = 0
wiimote = None
connected = False
rumble = 0
numpixels = 288 # Number of LEDs in strip
lasthb = 0
hbinterval = 30

blacklightdelay = 1

defaultColor = 0xF0F0FF
defaultBright = 255
flashColor = 0x00FF00
flashBright = 255
# Here's how to control the strip from any two GPIO pins:
datapin   = 23
clockpin  = 24
strip     = Adafruit_DotStar(numpixels, datapin, clockpin)
hi_thres = 10
low_thres = 4
strip.begin()           # Initialize pins for output
strip.setBrightness(255) # Limit brightness to ~1/4 duty cycle



eventarray = []
eventarray.append({"playsound": False, "lightson": True, "blacklight": False})
eventarray.append({"playsound": True, "lightson": True, "blacklight": False})
eventarray.append({"playsound": False, "lightson": False, "blacklight": True})

eventidx = 0

blacklight = False
lightson = True
playsound = False
#Setting color to: 0xFF0000    # Green
#Setting color to: 0xCC00CC    # Bright Teal
#Setting color to: 0x66CC00    # Orange
#Setting color to: 0x33FFFF    # Magenta 
#Setting color to: 0xFF00      # Red
#Setting color to: 0x330099    # Lightish Blue
#Setting color to: 0xFFFF00    # YEllow 
#Setting color to: 0xFF        # Bright Blue
#Setting color to: 0xFF9900    # YEllower Gren
#Setting color to: 0x33        # Dark BLue



def main():

    #Connect to address given on command-line, if present
    print 'Put Wiimote in discoverable mode now (press 1+2)...'
    global wiimote
    global rpt_mode
    global connected
    global strip
    global rumble
    global lightson
    logevent("startup", "startup", "Just started and ready to run")
    # Set the first pixel to red to show not connected
#    strip.setPixelColor(0, 0x00FF00)    
#    strip.show()


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

def PlaySound():
    global strip
    global blacklight
    global lightson
    global playsound
    global blacklightdelay
    print("start playsound")
    sounds = [0, 0, 0]
    channels = 2
    rate = 44100
    size = 1024
    thunderfiles = ['/home/pi/father_zaps.wav']
    out_stream = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NORMAL, 'default')
    out_stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    out_stream.setchannels(channels)
    out_stream.setrate(rate)
    out_stream.setperiodsize(size)
    curstream = None
    blackon = False
    lightwhite = False
    while True:
        if lightson == True and playsound == False and blacklight == False:
            if lightwhite == False:
                lightwhite = True
                blackon = False
                print("solid white loop")
                strip.setBrightness(defaultBright)
                setAllLEDS(strip, [defaultColor])
                strip.show()
                GPIO.output(GPIO_LIGHTS, False)
                gevent.sleep(0.01)
            else:
                gevent.sleep(0.01)
        elif lightson == True and playsound == True and blacklight == False:
            lightwhite = False
            blackon = False
            print("Zapping")
            while playsound == True:
                if curstream is None:
                    curfile = random.choice(thunderfiles)
                    curstream = open(curfile, "rb")
                data = curstream.read(size)
                tstart = 0
                gevent.sleep(0.01)
                while data and playsound == True:
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
                    if sounds_avg > hi_thres:
                        strip.setBrightness(flashBright)
                        setAllLEDS(strip, [flashColor])
                    if sounds_avg < low_thres:
                        strip.setBrightness(defaultBright)
                        setAllLEDS(strip, [defaultColor])
                    gevent.sleep(0.01)
                try:
                    curstream.close()
                except:
                    pass
                curstream = None
            if playsound == False:
                try:
                    curstream.close()
                except:
                    pass
                curstream = None
        elif lightson == False and playsound == False and blacklight == True:
            if blackon == False:
                blackon = True
                lightwhite = False
                print("Black light on")
                setAllLEDS(strip, [0x000000])
                strip.show()
                time.sleep(blacklightdelay)
                GPIO.output(GPIO_LIGHTS, True)
#                GPIO.output(GPIO_AIR, True)
                gevent.sleep(0.01)
            else:
                gevent.sleep(0.01)
 #               time.sleep(2)
#                GPIO.output(GPIO_LIGHTS, False)

    sys.exit(0)



def normal():
    global strip
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
        setAllLEDS(strip, [0x000000])
        strip.setBrightness(0)
        strip.show()
    wiimote.close()
    sys.exit()




def handle_buttons(buttons):
    global strip
    global eventarray
    global eventidx
    global playsound
    global lightson
    global blacklight


    if (buttons & cwiid.BTN_A):
        previdx = eventidx
        if eventidx == len(eventarray) - 1:
            eventidx = 0
        else:
            eventidx += 1
        print("Setting index to: %s" % eventidx)
        blacklight = eventarray[eventidx]["blacklight"]
        lightson = eventarray[eventidx]["lightson"]
        playsound = eventarray[eventidx]["playsound"]
        logevent("index_change", eventarray[eventidx], "Event list index changed from %s to %s" % (previdx, eventidx))


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



#BTN_1', 'BTN_2', 'BTN_A', 'BTN_B', 'BTN_DOWN', 'BTN_HOME', 'BTN_LEFT', 'BTN_MINUS', 'BTN_PLUS', 'BTN_RIGHT', 'BTN_UP',

def color_dict(gradient):
    ''' Takes in a list of RGB sub-lists and returns dictionary of
    colors in RGB and hex form for use in a graphing function
    defined later on '''
    return {"hex":[RGB_to_hex(RGB) for RGB in gradient],
      "r":[RGB[0] for RGB in gradient],
      "g":[RGB[1] for RGB in gradient],
      "b":[RGB[2] for RGB in gradient]}



def linear_gradient(start_hex, finish_hex="#FFFFFF", n=10):
    ''' returns a gradient list of (n) colors between
    two hex colors. start_hex and finish_hex
    should be the full six-digit color string,
    inlcuding the number sign ("#FFFFFF") '''
  # Starting and ending colors in RGB form
    s = hex_to_RGB(start_hex)
    f = hex_to_RGB(finish_hex)
  # Initilize a list of the output colors with the starting color
    RGB_list = [s]
  # Calcuate a color at each evenly spaced value of t from 1 to n
    for t in range(1, n):
    # Interpolate RGB vector for color at the current value of t
        curr_vector = [ int(s[j] + (float(t)/(n-1))*(f[j]-s[j])) for j in range(3)]
    # Add it to our list of output colors
        RGB_list.append(curr_vector)

    return color_dict(RGB_list)




def hex_to_RGB(hex):
    ''' "#FFFFFF" -> [255,255,255] '''
  # Pass 16 to the integer function for change of base
    return [int(hex[i:i+2], 16) for i in range(1,6,2)]


def RGB_to_hex(RGB):
    ''' [255,255,255] -> "#FFFFFF" '''
  # Components need to be integers for hex to make sense
    RGB = [int(x) for x in RGB]
    return "#"+"".join(["0{0:x}".format(v) if v < 16 else
            "{0:x}".format(v) for v in RGB])



def callback(mesg_list, time):

    for mesg in mesg_list:
        if mesg[0] == cwiid.MESG_BTN:
            handle_buttons(mesg[1])
#            print("Time: %s" % time)
 #           print 'Button Report: %.4X' % mesg[1]
        else:
            print 'Unknown Report'

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




def setAllLEDS(strip, colorlist):
    numcolors = len(colorlist)
    for x in range(numpixels):
        idx = x % numcolors
        strip.setPixelColor(x, colorlist[idx])
    strip.show()


if __name__ == "__main__":
    main()
