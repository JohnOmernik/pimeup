#!/usr/bin/python
#Gateway
import time
import random
import sys
import cwiid
import json
import gevent
from collections import OrderedDict
import alsaaudio
import wave
import sys
import struct
import math
from dotstar import Adafruit_DotStar
import socket


WHOAMI = socket.gethostname()
m = alsaaudio.Mixer('PCM')
current_volume = m.getvolume() # Get the current Volume
print("Cur Vol: %s " % current_volume)
m.setvolume(100) # Set the volume to 70%.
current_volume = m.getvolume() # Get the current Volume
print("Cur Vol: %s " % current_volume)

mesg = False
rpt_mode = 0
wiimote = None
connected = False
rumble = 0


numpixels = 264 # Number of LEDs in strip
# Here's how to control the strip from any two GPIO pins:
datapin   = 23
clockpin  = 24
fire_colors = [ "#001100", "#005500", "#00FF00", "#33FFFF", "#FFFFFF" ]
outtimes = {}

mydelays = [0.001]
#, 0.02, 0.03, 0.1, 0.15]
heat = []

heat = []
for x in range(numpixels):
    heat.append(30)
COOLING = 15
num_colors = 100
my_colors = []
colors_dict = OrderedDict()
allcolors = []

fireplacestarttime = 0
soundstarttime = 0
curplay = 66
lasthb = 0
hbinterval = 10
fireplace = True
fireplacestart = False
soundstart = False
soundplaying = False
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

strip     = Adafruit_DotStar(numpixels, datapin, clockpin)
strip.setBrightness(255)
strip.begin()           # Initialize pins for output


def main():
    global strip
    global allcolors
    global firecolors

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
        gevent.spawn(normal),
        gevent.spawn(FirePlace),
        gevent.spawn(playSound),
    ])

def normal():
    global strip
    global lasthb
    global hbinterval
    global soundstart
    global curplay
    global fireplacestart
    global fireplacestarttime
    global soundstarttime
    global heat
    global outtimes
    global soundplaying
    try:
        while True:
            gevent.sleep(0.001)
            curtime = int(time.time())
            # Just not doing anything
            #if curtime - fireplacestarttime > curplay or curtime - soundstarttime > curplay:
            #    # Well time to reset
            #    print("Reseting")
            #    print(heat)
            #    fireplacestart = True
            #    soundstart = True
            #    soundplaying = False
            #    fireplacestarttime = curtime
            #    soundstarttime = curtime
            #    outtimes = {}
            #    gevent.sleep(0.001)
            #else:
            #   if (curtime - fireplacestarttime) % 5 == 0:
            #        if str(curtime) not in outtimes:
            #            curheat = sum(heat) / float(len(heat))
            #            print("Current offset: %s - Avg Heat: %s" % (curtime - fireplacestarttime, curheat))
            #            outtimes[str(curtime)] = 1

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
    sys.exit()

def playSound():
    global soundstart
    global fireplacestart
    global soundplaying
    sounds = [0, 0, 0]
    channels = 2
    rate = 44100
    size = 1024
    out_stream = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NORMAL, 'default')
    out_stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    out_stream.setchannels(channels)
    out_stream.setrate(rate)
    out_stream.setperiodsize(size)


    soundfiles = ['/home/pi/tool_mantra.wav']
    curstream = None
    while True:
        if soundstart == True:
            if curstream is not None:
                curstream.close()
            curfile = random.choice(soundfiles)
            curstream = open(curfile, "rb")
            tstart = 0
            soundstart = False
            soundplaying = True
            fireplacestart = True
        if curstream is not None:
            data = curstream.read(size)
            while data:
                tstart += 1
                out_stream.write(data)
                data = curstream.read(size)
                gevent.sleep(0.001)
            curstream.close()
            curstream = None
            soundplaying = False
        else:
            soundplaying = False
        gevent.sleep(0.001)


def FirePlace():
    global numpixels
    global COOLING
    global strip
    global allcolors
    global heat
    global fireplacestart
    global fireplace
    # Every cycle there will be some random cololing
    # Consider adding a degree of random whether a pixel cools

    try:
        while True:
            #If we see start then reset all to 255
            if fireplacestart == True:
                for i in range(numpixels):
                    heat[i] = 255
                fireplacestart = False


            if fireplace == True:
                for i in range(numpixels):
                    if random.randint(0, 255) < COOLING:
                        tval = heat[i] - random.randint(0, ((COOLING * 10) / numpixels) + 2)
                        heat[i] = tval
                gevent.sleep(random.choice(mydelays))

    # This is supposed to be a diffusing effect I think
#                k = numpixels -3
 #               while k > 2:
  #                  if random.randint(0, 255) * 2 < COOLING:
   #                     tval = (heat[k-1] + heat[ k- 2 ] + heat[ k- 2] ) / 3
    #                    heat[k] = tval
     #                   k = k - 1
      #          gevent.sleep(random.choice(mydelays))

    # Now, actually set the pixels based on a scaled representation of all pixels
                for j in range(numpixels):

                    if heat[j] > 255:
                        heat[j] = 255
                    if heat[j] < 0:
                        heat[j] = 0
                    newcolor = int((heat[j] * len(allcolors)) / 256)
                    strip.setPixelColor(j, int(allcolors[newcolor].replace("#", ''), 16))
                gevent.sleep(random.choice(mydelays))
                strip.show()
                gevent.sleep(random.choice(mydelays))
            else:
                gevent.sleep(0.001)
    except KeyboardInterrupt:
        print("")
        print("exiting and shutting down strip")
        setAllLEDS(strip, [0x000000])
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

def handle_buttons(buttons):
    global heat
    global strip
    global soundstart
    global soundplaying
    
    if (buttons & cwiid.BTN_A):
        print("soundplaying in A: %s" % soundplaying)
        if soundplaying == False:
            print("making soundstart true")
            soundstart = True

    gevent.sleep(0.001)


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
        else:
            print 'Unknown Report'

if __name__ == "__main__":
    main()
