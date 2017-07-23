#!/usr/bin/python

from Adafruit_PWM_Servo_Driver import PWM
import time
import sys
import curses
import pygame
stdscr = curses.initscr()
curses.cbreak()
stdscr.keypad(1)

stdscr.addstr(0,10,"Hit 'q' to quit")
stdscr.refresh()


# ===========================================================================
# Example Code
# ===========================================================================

# Initialise the PWM device using the default address
pwm = PWM(0x40)
# Note if you'd like more debug output you can instead run:
#pwm = PWM(0x40, debug=True)

servoMin = 150  # Min pulse length out of 4096
servoMax = 600  # Max pulse length out of 4096

def setServoPulse(channel, pulse):
  pulseLength = 1000000                   # 1,000,000 us per second
  pulseLength /= 60                       # 60 Hz
  print "%d us per period" % pulseLength
  pulseLength /= 4096                     # 12 bits of resolution
  print "%d us per bit" % pulseLength
  pulse *= 1000
  pulse /= pulseLength
  pwm.setPWM(channel, 0, pulse)

pwm.setPWMFreq(60)                        # Set frequency to 60 Hz

#little low = 150
#
# Beak - 300 to 500
# Channel 0
# Eye Turns - 400 - 600
# Channel 1
# Eye Blink
# Channel 2 300-500

def eyesBlink():
    pwm.setPWM(2, 0, 400)
    time.sleep(0.25)
    pwm.setPWM(2, 0, 300)
    time.sleep(0.25)
    pwm.setPWM(2, 0, 400)

def mouthOpen():
    pwm.setPWM(0, 0, 500)

def mouthClosed():
    pwm.setPWM(0, 0, 350)

def mouthMiddle():
    pwm.setPWM(0, 0, 425)


def eyesLeft():
    pwm.setPWM(1, 0, 375)
def eyesRight():
    pwm.setPWM(1, 0, 525)
def eyesCenter():
    pwm.setPWM(1, 0, 450)

def goTime():
    time.sleep(0.15)
    mouthOpen()
    time.sleep(0.20)
    mouthClosed()
    time.sleep(0.10)
    mouthOpen()
    time.sleep(0.15)
    mouthClosed()
    time.sleep(0.60)
    



import pygame
pygame.mixer.init()
pygame.mixer.music.load("whizzer.wav")
pygame.mixer.music.play()
played = 0
while pygame.mixer.music.get_busy() == True:
    if played == 0:
        goTime()
        played = 1
    continue





key = ''
while key != ord('q'):
    key = stdscr.getch()
    stdscr.addch(20,25,key)
    stdscr.refresh()

    
    if key == ord('i'):
        mouthOpen()
    elif key == ord('o'):
        mouthMiddle()
    elif key == ord('p'):
        mouthClosed()
    elif key == ord('a'):
        eyesLeft()
    elif key == ord('s'):
        eyesCenter()
    elif key == ord('d'):
        eyesRight()
    elif key == ord('c'):
        eyesBlink()
    else:
        print("oops")

pwm.setPWM(0, 4096, 0)
pwm.setPWM(1, 4096, 0)
pwm.setPWM(2, 4096, 0)
sys.exit()

curses.endwin()



