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
import alsaaudio


WHOAMI = socket.gethostname()
m = alsaaudio.Mixer('PCM')
current_volume = m.getvolume() # Get the current Volume#
print("Cur Vol: %s " % current_volume)
m.setvolume(100) # Set the volume to 70%.
current_volume = m.getvolume() # Get the current Volume
print("New Cur Vol: %s " % current_volume)

WHOAMI = socket.gethostname()

import RPi.GPIO as GPIO
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 #set GPIO Pins
GPIO_RELAY = 16
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_RELAY, GPIO.OUT)

mesg = False
rpt_mode = 0
wiimote = None
connected = False
turbo = False
rumble = 0
numpixels = 60 # Number of LEDs in strip
lasthb = 0
hbinterval = 30

# Here's how to control the strip from any two GPIO pins:
datapin   = 23
clockpin  = 24
strip     = Adafruit_DotStar(numpixels, datapin, clockpin)

strip.begin()           # Initialize pins for output
strip.setBrightness(255) # Limit brightness to ~1/4 duty cycle

mydelays = [0.01]
heat = []
for x in range(numpixels):
    heat.append(random.randint(0, 50))

#Fireplace Effect

brokenlight = False
light = False


LIGHTON = 60
LIGHTOFF = 15
COOLING = 60
SPARKING = 60
gsparkitup = True
fire_colors = [ "#000033", "#0033FF", "#0099FF", "#00FFFF"]
num_colors = 100
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
      #  print("Color: %s" % hex_to_RGB(y))
            allcolors.append(y)

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
        except:
            print("Trying Again, please press 1+2")
            time.sleep(2)


    wiimote.mesg_callback = callback

    print("For LED we enable Button")
    rpt_mode ^= cwiid.RPT_BTN

    # Enable the messages in callback
    wiimote.enable(cwiid.FLAG_MESG_IFC);
    wiimote.rpt_mode = rpt_mode

#    print(wiimote.state)

    gevent.joinall([
        gevent.spawn(normal),
        gevent.spawn(FirePlace),
        gevent.spawn(PlaySound),
    ])


def normal():
    global strip
    global wiimote
    global lasthb
    global hbinterval
    try:
        while True:
            gevent.sleep(0.01)
            time.sleep(0.001)
            curtime = int(time.time())
            if curtime - lasthb > hbinterval:
                curts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(curtime))
                outrec = OrderedDict()
                outrec['ts'] = curts
                outrec['battery'] = wiimote.state['battery']
                outrec['host'] = WHOAMI
                print(json.dumps(outrec))
                outrec = None
                lasthb = curtime

    except KeyboardInterrupt:
        print("Exiting")
        setAllLEDS(strip, [0x000000])
        strip.setBrightness(0)
        strip.show()
    wiimote.close()
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

    soundfiles = ['/home/pi/torture_audio.wav']
    curstream = None
    while True:
        curfile = random.choice(soundfiles)
        curstream = open(curfile, "rb")
        gevent.sleep(0.001)
        if curstream is not None:
            data = curstream.read(size)
            while data:
                out_stream.write(data)
                data = curstream.read(size)
                gevent.sleep(0.001)
            curstream.close()
            print("Looping Sound")





def FirePlace():
    global gsparkitup
    global numpixels
    global SPARKING
    global COOLING
    global strip
    global allcolors
    global heat
    global fireplace

    # Every cycle there will be some random cololing
    # Consider adding a degree of random whether a pixel cools

    try:
        while True:
            if fireplace == True:
                for i in range(numpixels):
                    if random.randint(0, 255) < COOLING:
                        tval = heat[i] - random.randint(0, ((COOLING * 10) / numpixels) + 2)
                        heat[i] = tval
                gevent.sleep(random.choice(mydelays))

    # This is supposed to be a diffusing effect I think
                k = numpixels -3
                while k > 2:
                    if random.randint(0, 255) * 2 < COOLING:
                        tval = (heat[k-1] + heat[ k- 2 ] + heat[ k- 2] ) / 3
                        heat[k] = tval
                        k = k - 1
                gevent.sleep(random.choice(mydelays))

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
#        print("Pixel: %s has a heat value of %s and a newcolor idx of %s" % (j, heat[j], newcolor))
#                print("Setting Color: %s" % hex_to_RGB(allcolors[newcolor]))
#   
#                 print("Setting color to: 0x%0.2X" % int(allcolors[newcolor].replace("#", ''), 16))
                    strip.setPixelColor(j, int(allcolors[newcolor].replace("#", ''), 16))
                gevent.sleep(random.choice(mydelays))
                strip.show()
                gevent.sleep(random.choice(mydelays))
            else:
                gevent.sleep(0.1)
    except KeyboardInterrupt:
        print("")
        print("exiting and shutting down strip")
        setAllLEDS(strip, [0x000000])
        sys.exit(0)



def handle_buttons(buttons):
    global heat
    global strip
    global fireplace


    if (buttons & cwiid.BTN_A):
        print("Squirting")
        GPIO.output(GPIO_RELAY, True)
    else:
        GPIO.output(GPIO_RELAY, False)



def clearall():
    global strip
    global fireplace
    global brokenlight
    global danceparty
    fireplace = False
    danceparty = False
    brokenlight = False
    setAllLEDS(strip, [0x000000])


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