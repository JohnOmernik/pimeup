#!/usr/bin/python
import time
import sys


# Import the PCA9685 module.
import Adafruit_PCA9685

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685(0x40)



# ===========================================================================
# Example Code
# ===========================================================================

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
  pwm.set_pwm(channel, 0, pulse)

pwm.set_pwm_freq(60)

pwm.set_pwm(0, 4096, 0)
pwm.set_pwm(1, 4096, 0)
pwm.set_pwm(2, 4096, 0)

