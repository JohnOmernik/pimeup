#!/usr/bin/python

from collections import OrderedDict
import time
import gevent
import random
from dotstar import Adafruit_DotStar
import sys
import alsaaudio
import wave
import struct
import math



COOLING = 60
SPARKING = 60
numpixels = 60 # Number of LEDs in strip
# Here's how to control the strip from any two GPIO pins:
datapin   = 23
clockpin  = 24
strip     = Adafruit_DotStar(numpixels, datapin, clockpin)

strip.begin()           # Initialize pins for output
strip.setBrightness(255) # Limit brightness to ~1/4 duty cycle


hi_thres = 50

mydelay = 0.04
mydelays = [0.01, 0.02, 0.03, 0.1]
heat = []
for x in range(numpixels):
    heat.append(random.randint(0, 50))

#fire_colors = [ 0x000000, 0xFF0000, 0xFFFF00, 0xFFFFFF ]
fire_colors = [ "#000500", "#00FF00", "#48FF00" ]

num_colors = 100
my_colors = []
colors_dict = OrderedDict()
allcolors = []
gsparkitup = True



def main():
    global strip
    global fire_colors
    global my_colors
    global colors_dict
    global allcolors

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

#        gevent.spawn(PlayFire),

    gevent.joinall([
        gevent.spawn(FirePlace)
    ])



def PlayFire():
    global heat
    channels = 2
    rate = 44100
    size = 1024
    out_stream = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NORMAL, 'default')
    out_stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    out_stream.setchannels(channels)
    out_stream.setrate(rate)
    out_stream.setperiodsize(size)

    try:
        while True:
            sndstream = open("crackfire.wav", "rb")
            data = sndstream.read(size)
            while data:
                out_stream.write(data)
                gevent.sleep(0.001)
                data = sndstream.read(size)
                rmsval = rms(data)
                if rmsval > hi_thres:
                    rval = random.randint(0, numpixels - 1)
                    sparkval = random.randint(160, 255)
                    print("Sparking LED %s to %s" % (rval, sparkval))
                    heat[rval] = heat[rval] + random.randint(160,255)
                gevent.sleep(0.001)
            sndstream.close()
            gevent.sleep(0.001)
    except KeyboardInterrupt:
        print("")
        print("exiting and shutting down strip")
        setAllLEDS(strip, [0x000000])
        sys.exit(0)

def FirePlace():
    global gsparkitup
    global numpixels	
    global SPARKING
    global COOLING
    global strip
    global allcolors
    global heat
    #for i in range(numpixels):
    #    heat[i] = 0
    # Heat is a value for each pixel that is 0 to 255

    # Every cycle there will be some random cololing
    # Consider adding a degree of random whether a pixel cools
    try:
        while True:
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
                print("Sparking LED %s to %s" % (rval, sparkval))
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
    except KeyboardInterrupt:
        print("")
        print("exiting and shutting down strip")
        setAllLEDS(strip, [0x000000])
        sys.exit(0)

def color_dict(gradient):
  ''' Takes in a list of RGB sub-lists and returns dictionary of
    colors in RGB and hex form for use in a graphing function
    defined later on '''
  return {"hex":[RGB_to_hex(RGB) for RGB in gradient],
      "r":[RGB[0] for RGB in gradient],
      "g":[RGB[1] for RGB in gradient],
      "b":[RGB[2] for RGB in gradient]}


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
    curr_vector = [
      int(s[j] + (float(t)/(n-1))*(f[j]-s[j]))
      for j in range(3)
    ]
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

