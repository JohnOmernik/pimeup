#!/usr/bin/python

# Import the PCA9685 module.
import Adafruit_PCA9685
import time
import random
import sys

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685(0x40)
pwm.set_pwm_freq(60)

SRV_OPTIONS = []

SRV_OPTIONS.append({"SRV": 0, "DESC":"Thumb", "RANGE_MIN": 275, "RANGE_MAX": 575})
SRV_OPTIONS.append({"SRV": 1, "DESC":"Pointer", "RANGE_MIN": 300, "RANGE_MAX": 575})
SRV_OPTIONS.append({"SRV": 2, "DESC":"Middle", "RANGE_MIN": 325, "RANGE_MAX": 575})
SRV_OPTIONS.append({"SRV": 3, "DESC":"Ring", "RANGE_MIN":  275, "RANGE_MAX": 550})
SRV_OPTIONS.append({"SRV": 4, "DESC":"Pinky", "RANGE_MIN": 300, "RANGE_MAX": 575})
SRV_OPTIONS.append({"SRV": 5, "DESC":"WristFlex", "RANGE_MIN": 300, "RANGE_MAX": 600})
SRV_OPTIONS.append({"SRV": 6, "DESC":"WristTurn", "RANGE_MIN": 135, "RANGE_MAX": 660})
SRV_OPTIONS.append({"SRV": 7, "DESC":"WristUp", "RANGE_MIN": 360, "RANGE_MAX" : 620})

def main():

    cur_finger = -1

    while True:
        if cur_finger == -1:
            printServos()
            print("")
            srv_sel = raw_input("Servo to move: ")
            int_srv = -1

            if srv_sel == "e":
                print("Exiting!")
                break
            try:
                int_srv = int(srv_sel)
            except:
                print("Selected Servors must be an integer in  this list:")
                printServos()
                continue

            for y in SRV_OPTIONS:
                if int_srv == y['SRV']:
                    cur_finger = int_srv
                    break

            if cur_finger == int_srv:
                continue
            else:
                print("Servo provided (%s) not in the following List: Please try again")
                printServos()
        else:
            for y in SRV_OPTIONS:
                if cur_finger == y['SRV']:
                    mysrv = y
                    break

            
            print("Currently working with Servo: %s - Press q to quit this" % cur_finger)
            printServo(mysrv)
            while True:
                mv = raw_input("Enter Servo Value: ")
                if mv == 'q':
                    cur_finger = -1
                    break
                else:
                    try:
                        myval = int(mv)
                    except:
                        print("You must enter a integer")
                        continue
                    pwm.set_pwm(cur_finger, 0, myval)
        



    pwm.set_pwm(0, 4096, 0)
    pwm.set_pwm(1, 4096, 0)
    pwm.set_pwm(2, 4096, 0)
    pwm.set_pwm(3, 4096, 0)
    pwm.set_pwm(4, 4096, 0)
    pwm.set_pwm(5, 4096, 0)
    pwm.set_pwm(6, 4096, 0)
    sys.exit(0)


def printServos():
    print ("All Available Servos: ")
    for x in SRV_OPTIONS:
        printServo(x)



def printServo(s):
    print("Servo Number: %s - Desc: %s - Min Movement: %s - Max Movement: %s" % (s['SRV'], s['DESC'], s['RANGE_MIN'], s['RANGE_MAX']))

def setServoPulse(channel, pulse):
  pulseLength = 1000000                   # 1,000,000 us per second
  pulseLength /= 60                       # 60 Hz
  print "%d us per period" % pulseLength
  pulseLength /= 4096                     # 12 bits of resolution
  print "%d us per bit" % pulseLength
  pulse *= 1000
  pulse /= pulseLength
  pwm.set_pwm(channel, 0, pulse)


#little low = 150
#
# Beak - 300 to 500
# Channel 0
# Eye Turns - 400 - 600
# Channel 1
# Eye Blink
# Channel 2 300-500




if __name__ == "__main__":
    main()
