#!/usr/bin/python
import Adafruit_PCA9685
import time
import random
import sys
import socket
import json
from socket import error as socket_error
import RPi.GPIO as GPIO
import cwiid


#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 #set GPIO Pins
GPIO_MODE= 12
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_MODE, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685(0x40)
pwm.set_pwm_freq(60)

SRV_OPTIONS = []
ACTIONS = {}
HOMENET = 0
NETWORK = 1
STATUS = ""
wiimode = 0

if GPIO.input(GPIO_MODE) == 1:
    print("Wii mode is enabled!  (Network and command line will not function)")
    wiimode = 1
elif GPIO.input(GPIO_MODE) == 0:
    print("Wii mode is not enabled")
    wiimode = 0

try:
    chknet = sys.argv[1]
    print("Chknet: %s" % chknet)
    if int(chknet) == 2: # No network command line interface
        NETWORK = 0
        wiimode = 0 # We reset this back
    elif int(chknet) == 1 and wiimode == 0:  # Use home net ip of 192.168.0.130
        HOMENET = 1
except:
    if wiimode == 0:
        NETWORK = 1
    else:
        NETWORK = 0

thingfile = "/home/pi/pimeup/thingbox/thing.json"
thingactionfile = "/home/pi/pimeup/thingbox/thingactions.json"
STATUS_OPT = [ 'LIDUP', 'HANDUPLIDUP', 'HANDDOWNLIDUP', 'HANDDOWNLIDDOWN' ]
DEBUG = 0
BUT_DEBUG = 0
NET_DEBUG = 1
if HOMENET == 1:
    UDP_IP = '192.168.0.130'
else:
    UDP_IP = '192.168.1.110'
print("UDP IP is %s" % UDP_IP)
UDP_PORT = 30000
UDP_BUFFER_SIZE = 5


rpt_mode = 0
wiimote = None
connected = False
rumble = 0
b_val = False

def main():
    global SRV_OPTIONS
    global ACTIONS
    global STATUS
    global wiimote
    global rumble
    global rpt_mode
    global connected
    global b_val

    SRV_OPTIONS = loadfile(thingfile)
    ACTIONS = loadfile(thingactionfile)
    for x in SRV_OPTIONS:
        print(x)
    printActions()
    cur_finger = -1
    ACT_SHORT = []
    upact = ""
    downact = ""
    STATUS="HANDDOWNLIDDOWN"
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
    if wiimode == 1:
        # Setup Wii remote
        print ("Press 1+2 to connect Wii")
        while not connected:
            try:
                wiimote = cwiid.Wiimote()
                print("Connected!")
                connected = True
                rumble ^= 1
                wiimote.rumble = rumble
                time.sleep(2)
                rumble ^= 1
                wiimote.rumble = rumble
            except:
                print("Trying Again, please press 1+2")
                time.sleep(2)

            # Now setup Wii Callback, Buttons, and Accelerometer
        wiimote.mesg_callback = callback
        # For Thing box mode we enable  Button
        rpt_mode ^= cwiid.RPT_BTN

        # Enable the messages in callback
        wiimote.enable(cwiid.FLAG_MESG_IFC);
        wiimote.rpt_mode = rpt_mode

    try:
        while True:
            if NETWORK:
                data, addr = sock.recvfrom(UDP_BUFFER_SIZE)
            elif wiimode == 0:
                data = raw_input("Please Enter Raw Command: ")
            else: # This is wii mode
                time.sleep(0.5)
                continue
            if data:
                if DEBUG or NET_DEBUG:
                    print("Recieved Data Update: %s" % data)
                if data == "i":
                    for x in SRV_OPTIONS:
                        print(x)
                    printActions()
                elif len(data) == 1:
                    data = "A:" + data
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

def handle_buttons(buttons):
    global b_val
    global STATUS
    global SENSORS

    # The B (trigger) Button does cool things for us
    # When pressed that allows the glove sensors to be read and sent
    # It also changes what the other buttons do

    if (buttons & cwiid.BTN_B):
        b_val = True
    else:
        b_val = False

    if (buttons  & cwiid.BTN_UP):
        if b_val == True:
            processAction("O")
    elif (buttons & cwiid.BTN_DOWN):
        if b_val == True:
            processAction("C")
    elif (buttons & cwiid.BTN_LEFT):
        processAction("W")
    elif (buttons & cwiid.BTN_RIGHT):
        if b_val == True:
           processAction("B")
    elif (buttons & cwiid.BTN_1):
        if b_val == False:
            processAction("M")
        else:
            processAction("S")
    elif (buttons & cwiid.BTN_2):
        if b_val == True:
            processAction("F")
        else:
            processAction("P")
    elif (buttons & cwiid.BTN_PLUS):
        processAction("G")
    elif (buttons & cwiid.BTN_MINUS):
        # Locks the wrist up
        processAction("L")
    elif (buttons & cwiid.BTN_A):
        # A will summon thing if B is not pressed, and put him a way if B is pressed
        if b_val == False:
            processAction("U")
        elif b_val == True:
            processAction("D")
    elif (buttons & cwiid.BTN_HOME):
        # Home Calms Servos
        processAction("A")


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


def callback(mesg_list, time):
    global SENSORS
    global b_val
    global STATUS
    for mesg in mesg_list:
        if mesg[0] == cwiid.MESG_BTN:
            handle_buttons(mesg[1])
            if BUT_DEBUG or DEBUG:
                print("Time: %s" % time)
                print 'Button Report: %.4X' % mesg[1]
        else:
            print 'Unknown Report'



def printActions():
    type_dict = {}
    type_dict['0'] = "Maintaining the Thing"
    type_dict['1'] = "Single Actions"
    type_dict['2'] = "Neat Actions"
    type_dict['3'] = "Addams Family Macros"

    for t in range(4):
        print("")
        print("------------------------------------------------")
        print("Type %s - %s" % (t, type_dict[str(t)]))
        for x in ACTIONS:
            if x['TYPE'] == t:
                print("\t%s - %s\t\t%s" % (x['KEY'], x['NAME'], x['DESC']))
        print("")



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
                        if x != 5 and x != 7:
                            pwm.set_pwm(x, 4096, 0)
                else:
                    processAction(val)
            else:
                act = int(act)
                val = int(val)
                if val == -10:
                    pwm.set_pwm(act, 4096, 0)
                else:
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
#    print(pj)
    return json.loads(pj)

def exitGracefully():
    print("")
    print("ok Bye")
    pwm.set_pwm(0, 4096, 0)
    pwm.set_pwm(1, 4096, 0)
    pwm.set_pwm(2, 4096, 0)
    pwm.set_pwm(3, 4096, 0)
    pwm.set_pwm(4, 4096, 0)
#    pwm.set_pwm(5, 4096, 0)
    pwm.set_pwm(6, 4096, 0)
#    pwm.set_pwm(7, 4096, 0)
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
