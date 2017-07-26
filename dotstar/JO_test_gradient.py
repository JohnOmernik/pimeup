#!/usr/bin/python

from collections import OrderedDict
import time
import random
from dotstar import Adafruit_DotStar

COOLING = 55
SPARKING = 120
numpixels = 60 # Number of LEDs in strip
# Here's how to control the strip from any two GPIO pins:
datapin   = 23
clockpin  = 24
strip     = Adafruit_DotStar(numpixels, datapin, clockpin)

strip.begin()           # Initialize pins for output
strip.setBrightness(255) # Limit brightness to ~1/4 duty cycle

mydelay = 0.05
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
fire_colors = [ "#000000", "#00F000", "#48F000", "#48F048" ]

num_colors = 100
my_colors = []
colors_dict = OrderedDict()
def main():
    global strip
    global fire_colors
    global my_colors

    for x in range(len(fire_colors)):
        if x == len(fire_colors) -1:
            pass
        else:
            print("Adding gradient for %s (%s) to %s (%s) with %s colors" % (fire_colors[x], hex_to_RGB(fire_colors[x]), fire_colors[x+1], hex_to_RGB(fire_colors[x+1]),  num_colors))
            gtmp = linear_gradient(fire_colors[x], fire_colors[x+1], num_colors)
            my_colors.append(gtmp['hex'])
            colors_dict[fire_colors[x] + "_2_" + fire_colors[x+1]] = gtmp['hex']

    while True:
        time.sleep(1)
        for x in colors_dict:
            print("Running through %s" % x)
            print(colors_dict[x])
            for y in colors_dict[x]:
                print("color: %s" % y)
                setAllLEDS(strip, [int(y.replace("#", ''), 16)])
                time.sleep(0.2)

    try: 
        while True:                              # Loop forever
            time.sleep(mydelay)             # Pause 20 milliseconds (~50 fps)
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
    global numpixels	
    global SPARKING
    global COOLING
    global strip
    global my_colors
    global heat
    for i in range(numpixels):
        heat[i] = 0
    
    for i in range(numpixels):
        tval = heat[i] - random.randint(0, ((COOLING * 10) / numpixels) + 2)
        if tval < 0:
            tval == 0
        heat[i] = tval    

    k = numpixels -3
    while k > 0:
        heat[k] = (heat[k-1] + heat[ k- 2] + heat[ k- 2]) / 3
        k = k - 1
        
    if random.randint(0, 255) < SPARKING:
        rval = random.randint(0, 7)
        heat[rval] = heat[rval] + random.randint(160,255)

    for j in range(numpixels):
        newcolor = int(heat[j] * (240 / 256))
        mypal = random.choice(my_colors)
        strip.setPixelColor(j, int(mypal[newcolor].replace("#", ''), 16))
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

