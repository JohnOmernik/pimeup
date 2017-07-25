#!/usr/bin/python

from Adafruit_PWM_Servo_Driver import PWM
import time
import sys
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

while True:
    u = raw_input("Set pulse (e to exit): ")
    if str(u) == "e": 
        sys.exit(0)
    try:
        u = int(u)
        pwm.setPWM(3, 0, u)
    except:
        print("Not an int: %s - try again" % u)




f = """
while (True):
  # Change speed of continuous servo on channel O
  pwm.setPWM(0, 0, servoMin)
  time.sleep(0.5)
  pwm.setPWM(1, 0, servoMin)
  time.sleep(0.5)
  pwm.setPWM(2, 0, servoMin)
  time.sleep(0.5)



  pwm.setPWM(0, 0, servoMax)
  time.sleep(0.5)
  pwm.setPWM(1, 0, servoMax)
  time.sleep(0.5)
  pwm.setPWM(2, 0, servoMax)
  time.sleep(0.5)



"""
