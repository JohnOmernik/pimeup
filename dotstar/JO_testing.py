#!/usr/bin/python


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

mydelay = 1.0
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
    global strip

    try: 
        while True:                              # Loop forever
            time.sleep(mydelay)             # Pause 20 milliseconds (~50 fps)

            if cidx == (numcolors -1):
                cidx = 0
            else:
                cidx += 1
    except KeyboardInterrupt:
        print("")
        print("exiting and shutting down strip")
        setAllLEDS(strip, [0x000000])


def FirePlace():
    global numpixels	
    global SPARKING
    global COOLING

    heat = []
    for i in range(numpixels):
        heat[i] = 0
    
    for i in range(numpixels):
        tval = head[i] - random.randint(0, ((COOLING * 10) / numpixels) + 2))
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
            
 
  // Step 4.  Map from heat cells to LED colors
  for( int j = 0; j < NUM_LEDS; j++) {
    // Scale the heat value from 0-255 down to 0-240
    // for best results with color palettes.
    byte colorindex = scale8( heat[j], 240);
    leds[j] = ColorFromPalette( gPal, colorindex);
  }
}




		
def setAllLEDS(strip, colorlist):
    numcolors = len(colorlist)
    
    for x in range(numpixels):
        idx = x % numcolors
        strip.setPixelColor(x, colorlist[idx])
    strip.show()        


if __name__ == "__main__":
    main()

