#!/usr/bin/python


import time
import jocolors

#numpixels = 60 # Number of LEDs in strip
# Here's how to control the strip from any two GPIO pins:
#datapin   = 23
#clockpin  = 24
#strip     = Adafruit_DotStar(numpixels, datapin, clockpin)

#strip.begin()           # Initialize pins for output
#strip.setBrightness(255) # Limit brightness to ~1/4 duty cycle

#mydelay = 1.0
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
jo_strip = jocolor.jocolors(60, 23, 24, 255, 'rgb')

def main():
    global jo_strip

    colors = [0xFF0000, 0xCC00CC, 0x66CC00, 0x33FFFF, 0x00FF00, 0x330099, 0xFFFF00, 0x0000FF, 0xFF9900, 0x000033]
    numcolors = len(colors)
    cidx = 0
    try: 
        while True:                              # Loop forever
            print("Setting color to: 0x%0.2X" % colors[cidx])

            if cidx == (numcolors - 1):
                nextidx = 0
            else:
                nextidx = cidx + 1
            if cidx == (numcolors - 2):
                threeidx = 0
            elif cidx == (numcolors - 1):
                threeidx = 1
            else:
                threeidx = cidx + 2

            setAllLEDS(strip, [colors[cidx]])
            time.sleep(mydelay)             # Pause 20 milliseconds (~50 fps)

            if cidx == (numcolors -1):
                cidx = 0
            else:
                cidx += 1
    except KeyboardInterrupt:
        print("")
        print("exiting and shutting down strip")
        setAllLEDS(strip, [0x000000])
		
def setAllLEDS(strip, colorlist):
    numcolors = len(colorlist)
    
    for x in range(numpixels):
        idx = x % numcolors
        strip.setPixelColor(x, colorlist[idx])
    strip.show()        


if __name__ == "__main__":
    main()

