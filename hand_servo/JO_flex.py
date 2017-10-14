#!/usr/bin/python

import time
import random
import sys
import socket
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008


# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

tdelay = 0.2
DEBUG = 0
NETWORK = 1
SHOWLIST = [ "Pinky", "Index", "Thumb" ]

SENSORS = [
    {"NAME": "Pinky", "REMOTE": 4, "MIN":1000, "MAX": 0, "CHANGES":0, "LAST": 0, "CHANGED": False, "THRES": 5},
    {"NAME": "Ring", "REMOTE": 3, "MIN":1000, "MAX": 0, "CHANGES":0, "LAST": 0, "CHANGED": False, "THRES": 5},
    {"NAME": "Middle", "REMOTE": 2, "MIN":1000, "MAX": 0, "CHANGES":0, "LAST": 0, "CHANGED": False, "THRES": 5},
    {"NAME": "Index", "REMOTE": 1, "MIN":1000, "MAX": 0, "CHANGES":0, "LAST": 0, "CHANGED": False, "THRES": 5},
    {"NAME": "Thumb", "REMOTE": 0, "MIN":1000, "MAX": 0, "CHANGES":0, "LAST": 0, "CHANGED": False, "THRES": 5}
]


#SERVOS.append({"DESC":"Thumb", "RANGE_MIN": 275, "RANGE_MAX": 575, "INVERT": False})
#SERVOS.append({"DESC":"Pointer", "RANGE_MIN": 300, "RANGE_MAX": 575, "INVERT": True})
#SERVOS.append({"DESC":"Middle", "RANGE_MIN": 325, "RANGE_MAX": 575, "INVERT": True})
#SERVOS.append({"DESC":"Ring", "RANGE_MIN":  275, "RANGE_MAX": 550, "INVERT": True})
#SERVOS.append({"DESC":"Pinky", "RANGE_MIN": 300, "RANGE_MAX": 575, "INVERT": True})
#SERVOS.append({"DESC":"WristFlex", "RANGE_MIN": 300, "RANGE_MAX": 600, "INVERT": False})
#SERVOS.append({"DESC":"WristTurn", "RANGE_MIN": 135, "RANGE_MAX": 660, "INVERT": False})
#SERVOS.append({"DESC":"WristUp", "RANGE_MIN": 360, "RANGE_MAX" : 620, "INVERT": False})




def main():
    #flex sensor


    if NETWORK == 1:
        TCP_IP = '192.168.0.130'
        TCP_PORT = 30000
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((TCP_IP, TCP_PORT))
        except:
            print("Error connecting to %s:%s" % (TCP_IP, TCP_PORT))
            sys.exit(1)
    else:
        s = ""


    try:
        while True:
        # read the analog pin
            for x in range(len(SENSORS)):
                flex_val = mcp.read_adc(x)
                procValue(x, flex_val, s)
            time.sleep(tdelay)
    except KeyboardInterrupt:
        print("")
        print("Weee - Exiting")
        s.close()
        sys.exit(0)


def procValue(s, v, c):
    global SENSORS

    curname = SENSORS[s]['NAME']

    if v > SENSORS[s]['MAX']:
        SENSORS[s]['MAX'] = v
    if v < SENSORS[s]['MIN']:
        SENSORS[s]['MIN'] = v
    if DEBUG:
        print(SENSORS[s])
    if SENSORS[s]['MAX'] == SENSORS[s]['MIN']:
        SENSORS[s]['MAX'] += 1
    if DEBUG:
        print ("v: %s" %v)
        print ("Max: %s" % SENSORS[s]['MAX'])
        print ("Min: %s" % SENSORS[s]['MIN'])

    sendval = (float(v) - SENSORS[s]['MIN']) / (SENSORS[s]['MAX'] - SENSORS[s]['MIN'])
    sendval = int(sendval * 100)

    if sendval < 10:
        pad = "00"
    elif sendval < 100:
        pad = "0"
    else:
        pad = ""

    sendstr = str(SENSORS[s]['REMOTE']) + ":" + pad + str(sendval)
    if DEBUG:
        print("Sendval: %s" % sendval)

    sense_delta = abs(v - SENSORS[s]['LAST'])

    if sense_delta > SENSORS[s]['THRES']:
        SENSORS[s]['CHANGES'] += 1
        if SENSORS[s]['CHANGES'] > 5:
            if sendstr != "":
                if curname in SHOWLIST:
                    print ("******** %s - Sending this: %s " % (curname, sendstr))
                if NETWORK:
                    c.send(sendstr)
                sendstr = ""
    SENSORS[s]['LAST'] = v

if __name__ == "__main__":
    main()
