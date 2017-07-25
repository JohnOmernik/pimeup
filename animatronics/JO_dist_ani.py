#!/usr/bin/python

#Libraries
import RPi.GPIO as GPIO

# Import the PCA9685 module.
import Adafruit_PCA9685

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()


import random
import time
import sys
import alsaaudio
import wave
import struct
import math
# Note if you'd like more debug output you can instead run:
# Set frequency to 60hz, good for servos.
pwm.set_pwm_freq(60)
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

 #set GPIO Pins
GPIO_TRIGGER = 17
GPIO_ECHO = 13
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

hi_thres = 40
low_thres = 20
mouthpos = 0.0
dists = [0,0,0]

sound_thres = 15
state_thres = 10
last_play_time = int(time.time())
last_avg_state = 0
last_change_state_time = int(time.time())
last_change_state_avg = 0
curstate = "u"
def main ():
    global strip
    global dists
    print("Booting Mr Bigglesworth (CTRL+C to exit)")
    try:
        while 1:
            dist = distance()
            if dist < 2000:
                dists.append(dist)
                ug = dists.pop(0)
                print ("Measured Distance = %.1f cm - Curs: %s" % (dist, dists))
                chk_dist(dists)
                time.sleep(0.5)
    except KeyboardInterrupt:
        print("Mr. Bigglesworth is watching")
        pwm.set_pwm(0, 4096, 0)
        pwm.set_pwm(1, 4096, 0)
        pwm.set_pwm(2, 4096, 0)
        GPIO.cleanup()


def chk_dist(dists):
    global curstate
    global sound_thres
    global state_thres
    global last_play_time
    global last_change_state_avg
    global last_change_state_time

    curtime = int(time.time())
    tdelta = curtime - last_change_state_time
    sdelta = curtime - last_play_time

    mydists = [ x for x in dists if x > 0]

    dist = mydists[-1]
    dist_avg = sum(mydists) / len(mydists)

    if len(mydists) < len(dists):
        print("skipping until things fill up")
        return 

    print("\t\tCurrent Average: %s - \t Current State: %s" % (dist_avg, curstate))
    play_list = ""
    new_state = ""
    force = False
    if dist_avg >= 350:
        if curstate == 'u':
            play_list = 'u'
        else:
            new_state = "u"
            play_list = 'a-u'
    elif dist_avg < 3750 and dist_avg >= 275:
        if curstate == '3':
            play_list = '3'
        else:
            if curstate == 'u':
                play_list = 'u-a'
            elif curstate == '2':
                play_list = '2-3'
            elif curstate == '1':
                force = True
                play_list = '1-3'
            new_state = '3'
    elif dist_avg < 275 and dist_avg >= 100:
        if curstate == '2':
            play_list = '2'
        else:
            if curstate == 'u':
                play_list = 'u-a'
            elif curstate == '3':
                play_list = '3-2'
            elif curstate == '1':
                force = True
                play_list = '1-2'
            new_state = '2'
    elif dist_avg < 100 and dist_avg >= 1:
        if curstate == '1':
            play_list = '1'
        else:
            if curstate == 'u':
                play_list = 'u-a'
            elif curstate == '3':
                play_list = '3-1'
                force = True
            elif curstate == '2':
                force = True
                play_list = '2-1'
            new_state = '1' 
    if new_state != "":
        if tdelta >= state_thres or force == True:
            print("Changing state from %s to %s - Sound File: %s - Forced: %s" % (curstate, new_state, play_list, force))
            curstate = new_state
            last_change_state_time = curtime
            last_change_state_avg = dist_avg
        else:
            print("Skipping this state change")

    if last_change_state_time == curtime or sdelta >= sound_thres:
        if last_change_state_time == curtime:
            print("Changing due to avg change")
        elif sdelta >= sound_thres:
            print("It's been a while - Cur: %s - Last Play: %s - Delta: %s - Sound Thres: %s" % (curtime, last_play_time, sdelta, sound_thres))

        playFile(play_list)
        last_play_time = curtime


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
    sounds['1-3'] = ['1_to_3-1.wav', '1_to_3-2.wav']
    sounds['2'] = ['2-1.wav', '2-2.wav']
    sounds['2-1'] = ['2_to_1-1.wav', '2_to_1-2.wav']
    sounds['2-3'] = ['2_to_3-1.wav', '2_to_3-2.wav']
    sounds['3'] = ['3-1.wav', '3-2.wav']
    sounds['3-2'] = ['3_to_2-1.wav', '3_to_2-2.wav']
    sounds['3-1'] = ['3_to_1-1.wav', '3_to_1-2.wav']
    sounds['a-u'] = ['any_to_undetect-1.wav', 'any_to_undetect-2.wav']
    sounds['u'] = ['undetect-1.wav', 'undetect-2.wav']
    sounds['u-a'] = ['undetect_to_3-1.wav', 'undetect_to_3-2.wav']
    
    if skey not in sounds:
        print("%s sound list not found!" % skey)
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
  pwm.set_pwm(channel, 0, pulse)

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
    pwm.set_pwm(2, 0, 300)
def eyesOpen():
    pwm.set_pwm(2, 0, 400)

def mouthOpen():
    pwm.set_pwm(0, 0, 500)

def mouthClosed():
    pwm.set_pwm(0, 0, 350)

def mouthMiddle():
    pwm.set_pwm(0, 0, 425)

def eyesRand():
    c = [375, 525]
    pwm.set_pwm(1, 0, random.choice(c))


def eyesLeft():
    pwm.set_pwm(1, 0, 375)
def eyesRight():
    pwm.set_pwm(1, 0, 525)
def eyesCenter():
    pwm.set_pwm(1, 0, 450)

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
