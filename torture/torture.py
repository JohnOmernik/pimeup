#!/usr/bin/python
import cwiid
import sys
import gevent
import time
import json
import os
import requests
import datetime
import gevent
import atexit
import cStringIO
from collections import OrderedDict
import random
from dotstar import Adafruit_DotStar
import socket
import alsaaudio

#m = alsaaudio.Mixer('PCM')
#current_volume = m.getvolume() # Get the current Volume#
#print("Cur Vol: %s " % current_volume)
#m.setvolume(100) # Set the volume to 70%.
#current_volume = m.getvolume() # Get the current Volume
#print("New Cur Vol: %s " % current_volume)

WHOAMI = socket.gethostname()
WHATAMI = os.path.basename(__file__).replace(".py", "")


numpixels = 120 # Number of LEDs in strip
lasthb = 0
hbinterval = 30

# Here's how to control the strip from any two GPIO pins:
datapin   = 23
clockpin  = 24
strip     = Adafruit_DotStar(numpixels, datapin, clockpin)

strip.begin()           # Initialize pins for output
strip.setBrightness(255) # Limit brightness to ~1/4 duty cycle

mydelays = [0.1]
heat = []
for x in range(numpixels):
    heat.append(random.randint(0, 50))

#Fireplace Effect

COOLING = 50
SPARKING = 90
gsparkitup = True
fire_colors = [ "#000033", "#0033FF", "#0099FF", "#00FFFF"]
num_colors = 30
my_colors = []
colors_dict = OrderedDict()
allcolors = []

fireplace = True

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
    global allcolors
    global color_dict
    global my_colors
    global num_colors
    global fire_colors

    logevent("startup", "startup", "Just started and ready to run")

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


    gevent.joinall([
        gevent.spawn(FirePlace),
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
    global lasthb
    global hbinterval

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
#        curtime = int(time.time())
#        if curtime - lasthb > hbinterval:
#            logevent("heartbeat", "Working", "Standard HB")
#            lasthb = curtime
        curfile = random.choice(soundfiles)
        gevent.sleep(0.001)
        memsound[curfile].seek(0)
        data = memsound[curfile].read(size)
        while data:
            out_stream.write(data)
            data = memsound[curfile].read(size)
            gevent.sleep(0.001)


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

def FirePlace():
    global gsparkitup
    global numpixels
    global SPARKING
    global COOLING
    global strip
    global allcolors
    global heat
    global fireplace
    global hbinterval
    global lasthb
    # Every cycle there will be some random cololing
    # Consider adding a degree of random whether a pixel cools

    try:
        while True:
            if fireplace == True:
                curtime = int(time.time())
                if curtime - lasthb > hbinterval:
                    logevent("heartbeat", "Working", "Standard HB for torture room")
                    lasthb = curtime

                for i in range(numpixels):
                    if random.randint(0, 255) < COOLING:
                        tval = heat[i] - random.randint(0, ((COOLING * 10) / numpixels) + 2)
                        heat[i] = tval
                gevent.sleep(0.1)

    # This is supposed to be a diffusing effect I think
                k = numpixels -3
                while k > 2:
                    if random.randint(0, 255) * 2 < COOLING:
                        tval = (heat[k-1] + heat[ k- 2 ] + heat[ k- 2] ) / 3
                        heat[k] = tval
                        k = k - 1
                gevent.sleep(0.1)

    # Now let's see if we set any sparks!
                if gsparkitup == True:
                    if random.randint(0, 255) < SPARKING:
                        rval = random.randint(0, numpixels - 1)
                        sparkval = random.randint(160, 255)
                        heat[rval] = heat[rval] + random.randint(160,255)

    # Now, actually set the pixels based on a scaled representation of all pixels
                for j in range(numpixels):

                    if heat[j] > 255:
                        heat[j] = 255
                    if heat[j] < 0:
                        heat[j] = 0
                    newcolor = int((heat[j] * len(allcolors)) / 256)
                    strip.setPixelColor(j, int(allcolors[newcolor].replace("#", ''), 16))
                strip.show()
                gevent.sleep(0.1)
            else:
                gevent.sleep(0.1)
    except KeyboardInterrupt:
        print("")
        print("exiting and shutting down strip")
        setAllLEDS(strip, [0x000000])
        sys.exit(0)



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


def setAllLEDS(strip, colorlist):
    numcolors = len(colorlist)
    for x in range(numpixels):
        idx = x % numcolors
        strip.setPixelColor(x, colorlist[idx])
    strip.show()


if __name__ == "__main__":
    main()
