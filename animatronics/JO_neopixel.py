#!/usr/bin/python
# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
import time

from neopixel import *


# LED strip configuration:
LED_COUNT      = 60      # Number of LED pixels.
LED_PIN        = 12      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering



def main():
    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
    # Intialize the library (must be called once before other functions).
    strip.begin()
    mycolors = ['red', 'green', 'blue', 'magenta', 'yellow', 'cyan']
    myleds = range(60)
    mydelay = 2
    while True:
        for x in mycolors:
            colorSet(strip, myleds, x)
            time.sleep(mydelay)


def colorSet(strip, leds, scolor):
    print("Changing these LEDS to %s - %s" % (scolor, leds))
    if scolor == "red":
        solidRed(strip, leds)
    elif scolor == "green":
        solidGreen(strip, leds)
    elif scolor == "blue":
        solidBlue(strip, leds)
    elif scolor == "magenta":
        solidMagenta(strip, leds)
    elif scolor == "yellow":
        solidYellow(strip, leds)
    elif scolor == "cyan":
        solidCyan(strip, leds)
    else:
        print("Bad Color Choices")


def solidRed(strip, leds, brightness=255):
    for l in leds:
        strip.setPixelColor(l, Color(255,0,0,brightness))
    strip.show()
def solidCyan(strip, leds, brightness=255):
    for l in leds:
        strip.setPixelColor(l, Color(0,255,255,brightness))
    strip.show()
def solidYellow(strip, leds, brightness=255):
    for l in leds:
        strip.setPixelColor(l, Color(255,255,0,brightness))
    strip.show()
def solidGreen(strip, leds,brightness=255):
    for l in leds:
        strip.setPixelColor(l, Color(0,255,0,brightness))
    strip.show()
def solidBlue(strip, leds, brightness=255):
    for l in leds:
        strip.setPixelColor(l, Color(0,0,255,brightness))
    strip.show()
def solidMagenta(strip, leds, brightness=255):
    for l in leds:
        strip.setPixelColor(l, Color(255,0,255,brightness))
    strip.show()


# Main program logic follows:
if __name__ == '__main__':
    main()
