#!/usr/bin/python
import cwiid
import sys
import time
import atexit
from collections import OrderedDict
import random
from dotstar import Adafruit_DotStar

mesg = False
rpt_mode = 0
wiimote = None
connected = False
turbo = False

numpixels = 60 # Number of LEDs in strip
# Here's how to control the strip from any two GPIO pins:
datapin   = 23
clockpin  = 24
strip     = Adafruit_DotStar(numpixels, datapin, clockpin)

strip.begin()           # Initialize pins for output
strip.setBrightness(255) # Limit brightness to ~1/4 duty cycle



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




colors = [0xFF0000, 0xCC00CC, 0x66CC00, 0x33FFFF, 0xFF00, 0x330099, 0xFFFF00, 0xFF, 0xFF9900, 0x33]
color_idx = 0




def main():
    #Connect to address given on command-line, if present
    print 'Put Wiimote in discoverable mode now (press 1+2)...'
    global wiimote
    global rpt_mode
    global connected
    global strip
    # Set the first pixel to red to show not connected
    strip.setPixelColor(0, 0x00FF00)    
    strip.show()


    print("Trying Connection")
    print ("Press 1+2")
    while not connected:
        try:
            wiimote = cwiid.Wiimote()
            print("Connected!")
            connected = True
            strip.setPixelColor(0, 0x0000FF) # Set to green to show connection
            strip.show()
        except:
            strip.setPixelColor(0, 0xFFFF00) # Set to yellow to show failed connections
            strip.show()
            print("Trying Again, please press 1+2")
            time.sleep(2)
            strip.setPixelColor(0, 0x00FF00) # Set back to red to show not connected
            strip.show()

            
    wiimote.mesg_callback = callback

    print("For LED we enable Button")
    rpt_mode ^= cwiid.RPT_BTN

    # Enable the messages in callback
    wiimote.enable(cwiid.FLAG_MESG_IFC);
    wiimote.rpt_mode = rpt_mode
    exit = 0
    try:
        while not exit:
            c = sys.stdin.read(1)
            exit =  handle_input(wiimote, c)
    except KeyboardInterrupt
        print("Exiting")
        setAllLEDS(strip, [0x000000])
        strip.setBrightness(0)
        strip.show()
        
    wiimote.close()


def handle_buttons(buttons):
    global turbo
    global strip
    global colors
    global color_idx

    numcolors = len(colors)

    curBright = strip.getBrightness()

    if (buttons & cwiid.BTN_B):
        print("Setting turbo True")
        turbo = True
    else:
        print("Setting turbo False")
        turbo = False

    if (buttons  & cwiid.BTN_UP):
        if turbo == True:
            newBright = curBright + 50
        else:
            newBright = curBright + 5
        if newBright > 255:
            newBright = 255
            strip.setBrightness(0)
            strip.show()
            time.sleep(0.5)
        strip.setBrightness(newBright)
        strip.show()
    elif (buttons & cwiid.BTN_DOWN):
        if turbo == True:
            newBright = curBright - 50
        else:
            newBright = curBright - 5
        if newBright < 0:
            newBright = 0
            strip.setBrightness(255)
            strip.show()
            time.sleep(0.5)
        strip.setBrightness(newBright)
        strip.show()
    elif (buttons & cwiid.BTN_LEFT):
        if color_idx == 0:
            color_idx = numcolors - 1
        else:
            color_idx = color_idx - 1
        setAllLEDS(strip, [colors[color_idx]])
    elif (buttons & cwiid.BTN_RIGHT):
        if color_idx == numcolors - 1: 
            color_idx = 0
        else:
            color_idx = color_idx + 1
        setAllLEDS(strip, [colors[color_idx]])
    elif (buttons & cwiid.BTN_1):
        print("Button 1")
    elif (buttons & cwiid.BTN_2):
        print("Button 2")
    elif (buttons & cwiid.BTN_PLUS):
        print("Plus")
    elif (buttons & cwiid.BTN_MINUS):
        print("Minus")
    elif (buttons & cwiid.BTN_A):
        print("A")
    elif (buttons & cwiid.BTN_HOME):
        print("Home")


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
