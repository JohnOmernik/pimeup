#!/usr/bin/python
import Adafruit_PCA9685
import time
import random
import sys
import socket
import json
from socket import error as socket_error


# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685(0x40)
pwm.set_pwm_freq(60)

SRV_OPTIONS = []
ACTIONS = {}

STATUS = ""
try:
    chknet = sys.argv[1]
    print("Chknet: %s" % chknet)
    if int(chknet) == 1:
        NETWORK = 0
    else:
        NETWORK = 1
except:
    NETWORK = 1

thingfile = "/home/pi/pimeup/thingbox/thing.json"
thingactionfile = "/home/pi/pimeup/thingbox/thingactions.json"
STATUS_OPT = [ 'LIDUP', 'HANDUPLIDUP', 'HANDDOWNLIDUP', 'HANDDOWNLIDDOWN' ]
DEBUG = 0
NET_DEBUG = 1

UDP_IP = '192.168.0.130'
UDP_PORT = 30000
UDP_BUFFER_SIZE = 5

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

    if NETWORK:
        print("Listening on %s:%s" % (UDP_IP, UDP_PORT))
        sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
        sock.bind((UDP_IP, UDP_PORT))
    try:
        while True:
            if NETWORK:
                data, addr = sock.recvfrom(UDP_BUFFER_SIZE)
            else:
                data = raw_input("Please Enter Raw Command: ")
            if not data:
                continue
            else:
                if DEBUG or NET_DEBUG:
                    print("Recieved Data Update: %s" % data)

                tdata = data.split(":")
                if len(tdata) !=2 and len(tdata) != 4:
                    print("Ignoring Bad Data: %s" % data)
                    continue
                else:
                    cmdkey = tdata[0]
                    cmdval = tdata[1]
                    if str(cmdkey) == "A" and cmdval in ACT_SHORT:
                        processAction(cmdval)
                    elif str(cmdkey) == "S" and cmdval != "":
                        if cmdval in STATUS_OPT:
                            STATUS = cmdval
                        else:
                            print("Status needs to be in %s" % STATUS_OPT)
                    else:
                        try:
                            cmdkey = int(cmdkey)
                            cmdval = int(cmdval)
                        except:
                            print("cmdkey must be A or an integer")
                            continue
                        setfingerperc(cmdkey, cmdval)
    except socket_error:
        exitGracefully()
    except KeyboardInterrupt:
        exitGracefully()


def setfingerperc(cmdkey, cmdorigval, ignorestatus=False):
    global SRV_OPTIONS
    global STATUS
    if STATUS.find("HANDUP") >= 0 or ignorestatus:
        if SRV_OPTIONS[cmdkey]["INVERT"] == True:
            cmdval = abs(cmdorigval - 100)
        else:
            cmdval = cmdorigval
        setval = (cmdval * (SRV_OPTIONS[cmdkey]['RANGE_MAX'] - SRV_OPTIONS[cmdkey]['RANGE_MIN']) / 100) + SRV_OPTIONS[cmdkey]['RANGE_MIN']
        if DEBUG or NET_DEBUG:
            print("Setting Servo: %s (%s) to %s percent - (%s)" % (cmdkey, SRV_OPTIONS[cmdkey]['DESC'], cmdorigval, setval))
        pwm.set_pwm(cmdkey, 0, setval)
    else:
        print("Will not preform commands due to STATUS: %s" % STATUS)

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
                    for x in range(len(SRV_OPTIONS)):
                        pwm.set_pwm(x, 4096, 0)
                else:
                    processAction(val)
            else:
                act = int(act)
                val = int(val)
                setfingerperc(act, val, True)
        if new_status != "":
            STATUS = new_status

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

def exitGracefully():
    print("")
    print("ok Bye")
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
