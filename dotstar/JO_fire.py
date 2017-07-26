#!/usr/bin/python

from collections import OrderedDict
import time
import random
from dotstar import Adafruit_DotStar

COOLING = 60
SPARKING = 60
numpixels = 60 # Number of LEDs in strip
# Here's how to control the strip from any two GPIO pins:
datapin   = 23
clockpin  = 24
strip     = Adafruit_DotStar(numpixels, datapin, clockpin)

strip.begin()           # Initialize pins for output
strip.setBrightness(255) # Limit brightness to ~1/4 duty cycle
mydelay = [0.01, 0.02, 0.03, 0.1]
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


heat = []
for x in range(numpixels):
    heat.append(random.randint(0, 5))

#fire_colors = [ 0x000000, 0xFF0000, 0xFFFF00, 0xFFFFFF ]
fire_colors = [ "#000500", "#00FF00", "#48FF00", "#48FF32" ]
gsparkitup = True
num_colors = 100
my_colors = []
colors_dict = OrderedDict()
allcolors = []

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
            allcolors.append(y)

#    while True:
#        for z in allcolors:
#            time.sleep(0.01)
#            setAllLEDS(strip, [int(z.replace("#", ''), 16)])

    try: 
        while True:                              # Loop forever
            time.sleep(random.choice(mydelay))             # Pause 20 milliseconds (~50 fps)
            FirePlace()
#            for x in range(len(fire_colors)):
#                if x == len(fire_colors) - 1:
#                    endcolor = fire_colors[0]
#                else:
#                    endcolor = fire_colors[x + 1]
#                startcolor = fire_colors[x]
#                grad = linear_gradient(startcolor, endcolor, 200)
#            
#                for x in grad['hex']:
#                    time.sleep(0.1)            
#                    c = int(x.replace("#", ''), 16)
#                    print("Setting color %s to: 0x%0.2X" % (x, c))
#                    setAllLEDS(strip, [c])

#            print grad
            
    except KeyboardInterrupt:
        print("")
        print("exiting and shutting down strip")
        setAllLEDS(strip, [0x000000])


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
    for i in range(numpixels):
        if random.randint(0, 255) < COOLING:
            tval = heat[i] - random.randint(0, ((COOLING * 10) / numpixels) + 2)
            heat[i] = tval    

    # This is supposed to be a diffusing effect I think
    k = numpixels -3
    while k > 2:
        if random.randint(0, 255) < COOLING:
            tval = (heat[k-1] + heat[ k- 2 ] + heat[ k- 2] ) / 3
            heat[k] = tval
            k = k - 1
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
        strip.setPixelColor(j, int(allcolors[newcolor].replace("#", ''), 16))
    strip.show()                               


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

