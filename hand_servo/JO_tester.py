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

STATUS=""

thingfile = "/home/pi/pimeup/thingbox/thing.json"
thingactionfile = "/home/pi/pimeup/thingbox/thingactions.json"




def main():
    global SRV_OPTIONS
    global ACTIONS
    global STATUS

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
#    processAction(upact)
    while True:
        if cur_finger == -1:
            print("Current Status: %s" % STATUS)
            printServos()
            printAction()
            print("")
            srv_sel = raw_input("Servo to move or action: ")
            int_srv = -1

            if srv_sel == "e":
                print("Exiting!")
                break
            if srv_sel in ACT_SHORT:
                processAction(srv_sel)
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
    pwm.set_pwm(8, 4096, 0)
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

    pj = ""
    for line in tj.split("\n"):
        if line.strip() == "" or line.strip().find("#") == 0:
            pass
        else:
            pj += line.strip() + "\n"
    print(pj)
    return json.loads(pj)


def processAction(actKey):
    global STATUS
    act = {}
    bfound = False
    for x in ACTIONS:
        if actKey == x['KEY']:
            act = x
            bfound = True
    if bfound == True:
        new_status = act['STATUS']
        req_status = act['REQ_STATUS']
        actStr = act['ACTION']
        if req_status != "":
            if STATUS.find(req_status) < 0:
                print("Can't do it")
                print("STATUS: %s" % STATUS)
                print("req_status: %s" % req_status)
                return
        print("Running Action: %s" % act['NAME'])
        for action in actStr.split(","):
            tval = action.split(":")
            act = tval[0]
            val = tval[1]
            if act == "P":
                val = float(val)
                time.sleep(val)
            elif act == "A":
                shutdown = False
                try:
                    val = int(val)
                    if val == 0:
                        shutdown = True
                except:
                    shutdown = False
                if shutdown == True:
                    for x in range(len(SRV_OPTIONS) - 1):
                        pwm.set_pwm(x, 4096, 0)
                else:
                    processAction(val)
            else:
                act = int(act)
                val = int(val)
                if val >= 0:
                    pwm.set_pwm(act, 0, val)
                else:
                    pwm.set_pwm(act, 4096, 0)
        if new_status != "":
            STATUS = new_status

def setServoPulse(channel, pulse):
  pulseLength = 1000000                   # 1,000,000 us per second
  pulseLength /= 60                       # 60 Hz
  print "%d us per period" % pulseLength
  pulseLength /= 4096                     # 12 bits of resolution
  print "%d us per bit" % pulseLength
  pulse *= 1000
  pulse /= pulseLength
  pwm.set_pwm(channel, 0, pulse)






if __name__ == "__main__":
    main()
