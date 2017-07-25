#!/usr/bin/python

#Libraries
import RPi.GPIO as GPIO
from neopixel import *
from Adafruit_PWM_Servo_Driver import PWM
import random
import time
import sys
import alsaaudio
import wave
import struct
import math

# Initialise the PWM device using the default address
pwm = PWM(0x40)
# Note if you'd like more debug output you can instead run:
#pwm = PWM(0x40, debug=True)
pwm.setPWMFreq(60)                        # Set frequency to 60 Hz

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

# LED strip configuration:
LED_COUNT      = 1      # Number of LED pixels.
LED_PIN        = 12      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering
 
 #set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24
GPIO_IR = 6 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(GPIO_IR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 

hi_thres = 40
low_thres = 20
mouthpos = 0.0

last_dist = 0
last_dist_time = 0
curstate = "u"
strip = ""
# Setup Sound files


# Start the LED Driver
#strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
#strip.begin()

def main ():
    global strip
    print("Booting Mr Bigglesworth (CTRL+C to exit)")
    try:
        GPIO.add_event_detect(GPIO_IR, GPIO.RISING, callback=MOTION)
        while 1:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Quit")
#        ledOff(strip, [0])
        GPIO.cleanup()


def MOTION(PIR_PIN):
    global last_dist
    global last_dist_time
    global strip
    global curstate

    dist = distance()
    d_time = int(time.time())

    if dist > 2000:
        colorSet(strip, [0], 'magenta')
        if curstate != "u":
            playFile('a-u')
        else:
            playFile('u')
        curstate = 'u'
        colorSet(strip, [0], 'magenta')
    elif dist < 300 and dist >= 200:
        if curstate == 'u':
            playFile('u-a')
        elif curstate == '2':
            playFile('2-3')
        elif curstate == '1':
            playFile('1-2')
            time.sleep(2)
            playFile('2-3')
        elif curstate == '3':
            playFile('3')
        curstate = '3'
        colorSet(strip, [0], 'blue')
    elif dist < 200 and dist >= 100:
        if curstate == 'u':
            playFile('u-a')
        elif curstate == '2':
            playFile('2')
        elif curstate == '1':
            playFile('1-2')
        elif curstate == '3':
            playFile('3-2')
        curstate = '2'
        colorSet(strip, [0], 'yellow')
    elif dist < 100 and dist >= 1:
        if curstate == 'u':
            playFile('u-a')
        elif curstate == '2':
            playFile('2-1')
        elif curstate == '1':
            playFile('1')
        elif curstate == '3':
            playFile('3-2')
            time.sleep(2)
            playFile('2-1')
        curstate = '1'
        colorSet(strip, [0], 'red')   


def playFile(skey):

    out_stream = None
    out_stream = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NORMAL, 'default')
    out_stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    out_stream.setchannels(2)
    out_stream.setrate(44000)
    out_stream.setperiodsize(1024)

    base_dir = "./sound_files"
    sounds = {}
    sounds['1'] = ['1-1.wav', '1-2.wav', '1-3.wav']
    sounds['1-2'] = ['1_to_2-1.wav', '1_to_2-2.wav']
    sounds['2'] = ['2-1.wav', '2-2.wav']
    sounds['2-1'] = ['2_to_1-1.wav', '2_to_1-2.wav']
    sounds['2-3'] = ['2_to_3-1.wav', '2_to_3-2.wav']
    sounds['3'] = ['3-1.wav', '3-2.wav']
    sounds['3-2'] = ['3_to_2-1.wav', '3_to_2-2.wav']
    sounds['a-u'] = ['any_to_undetect-1.wav', 'any_to_undetect-2.wav']
    sounds['u'] = ['undetect-1.wav', 'undetect-2.wav']
    sounds['u-a'] = ['Undetect_to_3-1.wav', 'Undetect_to_3-2.wav']
    
    if skey not in sounds:
        return 0
    fname = base_dir + "/" + random.choice(sounds[skey])

    file = open(fname, "rb")
    data = file.read(1024)
    tstart = 0
    while data:
        tstart += 1
        if tstart == 1:
            eyesCenter()

        if tstart % 400 == 0:
            eyesClosed()
        elif tstart % 425 == 0:
            eyesOpen()
        elif tstart % 500 == 0:
            eyesRand()
        elif tstart % 575 == 0:
            eyesCenter()

        out_stream.write(data)
        data = file.read(1024)
        moveMouth(rms(data, 1024))
    file.close()
    out_stream.close()
    mouthClosed()
    eyesCenter()

def setServoPulse(channel, pulse):
  pulseLength = 1000000                   # 1,000,000 us per second
  pulseLength /= 60                       # 60 Hz
  print "%d us per period" % pulseLength
  pulseLength /= 4096                     # 12 bits of resolution
  print "%d us per bit" % pulseLength
  pulse *= 1000
  pulse /= pulseLength
  pwm.setPWM(channel, 0, pulse)

def moveMouth(sig):
    global mouthpos
    global hi_thres
    global low_thres
    if mouthpos == 0.0:
        if sig >= hi_thres:
            mouthMiddle()
            mouthpos = 0.5
    if mouthpos == 0.5:
        if sig < low_thres:
            mouthClosed()
            mouthpos = 0.0


def rms(frame, CHUNK):
    SHORT_NORMALIZE = (1.0/32768.0)
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

#little low = 150
#
# Beak - 300 to 500
# Channel 0
# Eye Turns - 400 - 600
# Channel 1
# Eye Blink
# Channel 2 300-500

def eyesClosed():
    pwm.setPWM(2, 0, 300)
def eyesOpen():
    pwm.setPWM(2, 0, 400)

def mouthOpen():
    pwm.setPWM(0, 0, 500)

def mouthClosed():
    pwm.setPWM(0, 0, 350)

def mouthMiddle():
    pwm.setPWM(0, 0, 425)

def eyesRand():
    c = [375, 525]
    pwm.setPWM(1, 0, random.choice(c))


def eyesLeft():
    pwm.setPWM(1, 0, 375)
def eyesRight():
    pwm.setPWM(1, 0, 525)
def eyesCenter():
    pwm.setPWM(1, 0, 450)



def colorSet(strip, leds, scolor):
    h = """
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
    elif scolor == "off":
        ledOff(strip, leds)
    else:
        print("Bad Color Choices")
    """
def ledOff(strip, leds, brightness=0):
    for l in leds:
        strip.setPixelColor(l, Color(0,0,0,brightness))
    strip.show()

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



def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
 
if __name__ == '__main__':
    main()
