#!/usr/bin/python

# Import the PCA9685 module.
import Adafruit_PCA9685
import time
import random
import sys
import json
# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685(0x40)
pwm.set_pwm_freq(60)

SRV_OPTIONS = []
ACTIONS = {}


thingfile = "/home/pi/pimeup/thingbox/thing.json"
thingactionfile = "/home/pi/pimeup/thingbox/thingactions.json"




def main():
    global SRV_OPTIONS
    global ACTIONS

    SRV_OPTIONS = loadfile(thingfile)
    ACTIONS = loadfile(thingactionfile)

    cur_finger = -1
    ACT_SHORT = []
    upact = ""
    downact = ""
    for x in ACTIONS:
        if x['KEY'] == "U":
            upact = x['ACTION']
        if x['KEY'] == "P":
            downact = x['ACTION']
        ACT_SHORT.append(x['KEY'])
    processAction(upact)
    while True:
        if cur_finger == -1:
            printServos()
            printAction()
            print("")
            srv_sel = raw_input("Servo to move or action: ")
            int_srv = -1

            if srv_sel == "e":
                print("Exiting!")
                break
            if srv_sel in ACT_SHORT:
                for x in ACTIONS:
                    if srv_sel == x['KEY']:
                        print("Running Action: %s" % x['NAME'])
                        processAction(x['ACTION'])
            else:
                try:
                    int_srv = int(srv_sel)
                except:
                    print("Selected Servors must be an integer or action in this list:")
                    printServos()
                    printAction()
                    continue

                for y in SRV_OPTIONS:
                    if int_srv == y['IDX']:
                        cur_finger = int_srv
                        break

                if cur_finger == int_srv:
                    continue
                else:
                    print("Servo provided (%s) not in the following List: Please try again")
                    printServos()
        else:
            for y in SRV_OPTIONS:
                if cur_finger == y['IDX']:
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


    processAction(downact)
    time.sleep(2)
    pwm.set_pwm(0, 4096, 0)
    pwm.set_pwm(1, 4096, 0)
    pwm.set_pwm(2, 4096, 0)
    pwm.set_pwm(3, 4096, 0)
    pwm.set_pwm(4, 4096, 0)
    pwm.set_pwm(5, 4096, 0)
    pwm.set_pwm(6, 4096, 0)
    pwm.set_pwm(7, 4096, 0)
    sys.exit(0)


def printServos():
    print("")
    print ("All Available Servos: ")
    print("==============================")
    for x in SRV_OPTIONS:
        printServo(x)
    print("")


def printServo(s):
    print("Servo Number: %s - Desc: %s - Min Movement: %s - Max Movement: %s - Notes: %s" % (s['IDX'], s['DESC'], s['RANGE_MIN'], s['RANGE_MAX'], s['NOTES']))


def printAction():
    print("")
    print("Available Actions: ")
    print("==============================")
    for x in ACTIONS:
        print("\t%s - %s - %s" % (x['KEY'], x['NAME'], x['DESC']))
    print("")

def loadfile(f):
    o = open(f, "rb")
    tj = o.read()
    o.close()
    return json.loads(tj)


def processAction(actStr):

    for action in actStr.split(","):
        tval = action.split(":")
        act = tval[0]
        val = tval[1]
        if act == "P":
            val = float(val)
            time.sleep(val)
        else:
            act = int(act)
            val = int(val)
            if val >= 0:
                pwm.set_pwm(act, 0, val)
            else:
                pwm.set_pwm(act, 4096, 0)



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
