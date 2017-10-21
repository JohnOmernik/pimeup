#!/usr/bin/python
import cwiid
import sys
import gevent
import time
import datetime
import atexit
import json
import requests
import os
from collections import OrderedDict
import random
from dotstar import Adafruit_DotStar
import socket

import alsaaudio
import wave
import struct
import math

WHOAMI = socket.gethostname()
WHATAMI = os.path.basename(__file__).replace(".py", "")

mesg = False
rpt_mode = 0
wiimote = None
connected = False
rumble = 0
numpixels = 120 # Number of LEDs in strip
lasthb = 0
hbinterval = 30

defaultColor = 0xFFFFCC
defaultBright = 255
# Here's how to control the strip from any two GPIO pins:
datapin   = 23
clockpin  = 24
strip     = Adafruit_DotStar(numpixels, datapin, clockpin)
strip.begin()           # Initialize pins for output
strip.setBrightness(255) # Limit brightness to ~1/4 duty cycle



playsound = False
normallight = True
goldlight = False

fire_colors = [ "#CCCCCC", "#33CC00", "#66CC00"]
# "#FFFF00"]
num_colors = 100
my_colors = []
colors_dict = OrderedDict()
allcolors = []
pulse_colors = []
pulse_mod = 4

eventarray = []
eventarray.append({"playsound": False, "normallight": True, "goldlight": False})
eventarray.append({"playsound": True, "normallight": False, "goldlight": True})

eventidx = 0



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
    logevent("startup", "startup", "Just started and ready to run")
    print 'Put Wiimote in discoverable mode now (press 1+2)...'
    global wiimote
    global rpt_mode
    global connected
    global strip
    global rumble
    global allcolors
    global my_colors
    global fire_colors
    global pulse_colors
    global pulse_mod
    for x in range(len(fire_colors)):
        if x == len(fire_colors) -1:
            pass
        else:
            print("Adding gradient for %s (%s) to %s (%s) with %s colors" % (fire_colors[x], hex_to_RGB(fire_colors[x]), fire_colors[x+1], hex_to_RGB(fire_colors[x+1]),  num_colors))
            gtmp = linear_gradient(fire_colors[x], fire_colors[x+1], num_colors)
            my_colors.append(gtmp['hex'])
            colors_dict[fire_colors[x] + "_2_" + fire_colors[x+1]] = gtmp['hex']
    for x in colors_dict:
        for y in colors_dict[x]:
            allcolors.append(y)

    ccnt = 0
    for x in reversed(allcolors):
        ccnt += 1
        pulse_colors.append(x)
        if ccnt > num_colors / pulse_mod:
            break
    print("Pulse colors has %s colors" % len(pulse_colors))



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
        gevent.spawn(Lights),
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

def Lights():
    global strip
    global normallight
    global goldlight
    global pulse_colors
    global all_colors
    goldon = False
    lighton = False

    while True:
        if normallight == True and lighton == False and goldlight == False:
            if goldon == True:
                setAllLEDS(strip, [0x000000])
                goldon = False
                gevent.sleep(0.001)
            strip.setBrightness(defaultBright)
            setAllLEDS(strip, [defaultColor])
            lighton = True
            gevent.sleep(0.001)
        elif goldlight == True and lighton == True and goldon == False:
            goldon = True
            for x in allcolors:
                setAllLEDS(strip, [int(x.replace("#", ''), 16)])
                gevent.sleep(0.001)
            lighton = False
        elif goldlight == True and goldon == True and lighton == False:
            for x in pulse_colors:
                setAllLEDS(strip, [int(x.replace("#", ''), 16)])
                if goldlight == False:
                    break
                gevent.sleep(0.05)
            for x in reversed(pulse_colors):
                if goldlight == False:
                    break
                setAllLEDS(strip, [int(x.replace("#", ''), 16)])
                gevent.sleep(0.05)
        gevent.sleep(0.01)



def PlaySound():
    global strip
    global playsound


    print("start playsound")
    sounds = [0, 0, 0]
    channels = 2
    rate = 44100
    size = 1024
    soundfiles = ['/home/pi/Madness_Vault_Whispers.wav']
    out_stream = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NORMAL, 'default')
    out_stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    out_stream.setchannels(channels)
    out_stream.setrate(rate)
    out_stream.setperiodsize(size)

    memsound = {}
    print("Loading Sound files to memory")
    for sf in soundfiles:
        f = open(sf, "rb")
        sfdata = f.read()
        f.close()
        memsound[sf] = cStringIO.StringIO(sfdata)

    soundreset = False

    while True:
        if playsound == True:
            print("Sound")
            if soundreset == False:
                curfile = random.choice(soundfiles)
                memsound[curfile].seek(0)
                soundreset = True
            data = memsound[curfile].read(size)
            gevent.sleep(0.001)
            while data and playsound == True:
                out_stream.write(data)
                data = memsound[curfile].read(size)
                gevent.sleep(0.001)
            playsound = False
            soundreset = False
        else:
            gevent.sleep(0.001)

    sys.exit(0)




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
    global strip
    global wiimote
    global lasthb
    global hbinterval
    try:
        while True:
            curtime = int(time.time())
            if curtime - lasthb > hbinterval:
                logevent("heartbeat", wiimote.state['battery'], "wii HB")
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
    global normallight
    global goldlight
    changed = False

    if (buttons & cwiid.BTN_A):
        previdx = eventidx
        if eventidx == 0:
            eventidx += 1
            changed = True
    if (buttons & cwiid.BTN_1):
        previdx = eventidx
        if eventidx != 0:
            eventidx = 0
            changed = True
    if changed == True:    
        curtime = int(time.time())
        goldlight = eventarray[eventidx]["goldlight"]
        normallight = eventarray[eventidx]["normallight"]
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

def setAllLEDS(strip, colorlist):
    numcolors = len(colorlist)
    for x in range(numpixels):
        idx = x % numcolors
        strip.setPixelColor(x, colorlist[idx])
    strip.show()


if __name__ == "__main__":
    main()
