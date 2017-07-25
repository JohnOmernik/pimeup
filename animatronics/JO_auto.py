#!/usr/bin/python

from Adafruit_PWM_Servo_Driver import PWM
import time
import random
import sys
import alsaaudio
import wave
import sys
import struct
import math

# Initialise the PWM device using the default address
pwm = PWM(0x40)
# Note if you'd like more debug output you can instead run:
#pwm = PWM(0x40, debug=True)
pwm.setPWMFreq(60)                        # Set frequency to 60 Hz


hi_thres = 40
low_thres = 20
mouthpos = 0.0

def main():
    channels = 2
    rate = 44000
    size = 1024
    out_stream = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NORMAL, 'default')
    out_stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    out_stream.setchannels(channels)
    out_stream.setrate(rate)
    out_stream.setperiodsize(size)

   # file = open("whizzer.wav", "rb")
    file = open("drhorrible.wav", "rb")

    data = file.read(size)
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
        data = file.read(size)
        moveMouth(rms(data))

    mouthClosed()
    eyesCenter()

    time.sleep(5)
    pwm.setPWM(0, 4096, 0)
    pwm.setPWM(1, 4096, 0)
    pwm.setPWM(2, 4096, 0)
    sys.exit(0)
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




def setServoPulse(channel, pulse):
  pulseLength = 1000000                   # 1,000,000 us per second
  pulseLength /= 60                       # 60 Hz
  print "%d us per period" % pulseLength
  pulseLength /= 4096                     # 12 bits of resolution
  print "%d us per bit" % pulseLength
  pulse *= 1000
  pulse /= pulseLength
  pwm.setPWM(channel, 0, pulse)


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






if __name__ == "__main__":
    main()
