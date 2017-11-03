#!/usr/bin/python
import time
import sys
import socket
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import cwiid
import json

tdelay = 0.2
DEBUG = 0
ACC_DEBUG = 0
BUT_DEBUG = 0
FLX_DEBUG = 0
PRC_DEBUG = 0
PNG_DEBUG = 0
NET_DEBUG = 1
ACT_DEBUG = 0
NETWORK = 1
PINGTIMEOUT = 1
HOMENET = 0
ACTIONS = []
ALLOWED_KEYS = []
action_idx = 0
thingactionfile = "/home/pi/pimeup/thingbox/thingactions.json"


try:
    chknet = sys.argv[1]
    print("Chknet: %s" % chknet)
    if int(chknet) == 2: # No network command line interface
        NETWORK = 0
    elif int(chknet) == 1:  # Use home net ip of 192.168.0.130
        HOMENET = 1
    else:
        NETWORK = 1
except:
    NETWORK = 1


if HOMENET == 1:
    UDP_IP = '192.168.0.130'
else:
    UDP_IP = '192.168.1.110'

UDP_PORT = 30000
UDP_SOCK = None



#SHOWLIST = [ "WristFlex", "WristTurn", "Pinky", "Ring", "Middle", "Index", "Thumb" ]
SHOWLIST = [ "Ring", "Middle" ] 
# Defaults:
mysens_thres = 2
mychng_thres = 2
# Used for Testing:
tmpsens_thres = 2
tmpchng_thres = 10

roundval = 2
tmproundval = 3
# Hardware SPI configuration: (Do not Modify)
####################
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
####################


STATUS = ""
SENSORS = [
    {"NAME": "Pinky", "TYPE": "adc", "REMOTE": 4, "MIN":1000, "MAX": 0, "CHANGES":0, "LAST": 0, "CHANGED": False, "SENS_THRES": mysens_thres, "CHNG_THRES": mychng_thres, "INVERT": False, "ROUNDVAL": roundval, "ADJVAL": 2},
    {"NAME": "Ring", "TYPE": "adc", "REMOTE": 3, "MIN":1000, "MAX": 0, "CHANGES":0, "LAST": 0, "CHANGED": False, "SENS_THRES": mysens_thres, "CHNG_THRES": mychng_thres, "INVERT": False, "ROUNDVAL": roundval, "ADJVAL": 2},
    {"NAME": "Middle", "TYPE": "adc", "REMOTE": 2, "MIN":1000, "MAX": 0, "CHANGES":0, "LAST": 0, "CHANGED": False, "SENS_THRES": mysens_thres, "CHNG_THRES": mychng_thres, "INVERT": False, "ROUNDVAL": roundval, "ADJVAL": 2},
    {"NAME": "Index", "TYPE": "adc", "REMOTE": 1, "MIN":1000, "MAX": 0, "CHANGES":0, "LAST": 0, "CHANGED": False, "SENS_THRES": mysens_thres, "CHNG_THRES": mychng_thres, "INVERT": False, "ROUNDVAL": roundval, "ADJVAL": 2},
    {"NAME": "Thumb", "TYPE": "adc", "REMOTE": 0, "MIN":1000, "MAX": 0, "CHANGES":0, "LAST": 0, "CHANGED": False, "SENS_THRES": mysens_thres, "CHNG_THRES": mychng_thres, "INVERT": False, "ROUNDVAL": roundval, "ADJVAL": 2},
    {"NAME": "WristFlex", "TYPE": "acc", "REMOTE": 5, "MIN": 1000, "MAX": 0, "CHANGES":0, "LAST": 0, "CHANGED": False, "SENS_THRES": 3, "CHNG_THRES": mychng_thres, "INVERT": True, "ROUNDVAL": roundval, "ADJVAL": 0},
    {"NAME": "WristTurn", "TYPE": "acc", "REMOTE": 6, "MIN": 1000, "MAX": 0, "CHANGES":0, "LAST": 0, "CHANGED": False, "SENS_THRES": 3, "CHNG_THRES": mychng_thres, "INVERT": False, "ROUNDVAL": roundval, "ADJVAL": 0}
]


rpt_mode = 0
wiimote = None
connected = False
rumble = 0
b_val = False

def main():
    global wiimote
    global rpt_mode
    global connected
    global rumble
    global NETWORK
    global b_val
    global UDP_SOCK
    global STATUS
    global ACTIONS
    global action_idx
    global PINGTIMEOUT
# Setup Network (Currently UDP)
    if NETWORK == 1:
        UDP_SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        UDP_SOCK.settimeout(PINGTIMEOUT)

    myact = loadfile(thingactionfile)

    for x in myact:
        if x['TYPE'] == 3: # Load the Addams Family Actions
            tact = {"NAME": x['NAME'], "KEY": x['KEY'], "DESC": x['DESC']}
            ACTIONS.append(tact)
    if DEBUG or ACT_DEBUG:
        for x in range(len(ACTIONS)):
            print("Action %s - KEY: %s - NAME: %s - DESC: %s" % (x, ACTIONS[x]['KEY'], ACTIONS[x]['NAME'], ACTIONS[x]['DESC']))


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
    # For Thing we enable ACC and Button
    rpt_mode ^= cwiid.RPT_ACC
    rpt_mode ^= cwiid.RPT_BTN

    # Enable the messages in callback
    wiimote.enable(cwiid.FLAG_MESG_IFC);
    wiimote.rpt_mode = rpt_mode

    try:
        while True:
            if b_val == True:
                if STATUS == "HANDUPLIDUP":
                    for x in range(len(SENSORS)):
                        if SENSORS[x]['TYPE'] == 'adc':
                            flex_val = mcp.read_adc(x)
                            procValue(x, flex_val)
            time.sleep(tdelay)
    except KeyboardInterrupt:
        print("")
        print("Weee - Exiting")
        sys.exit(0)


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
        elif mesg[0] == cwiid.MESG_ACC:
            x = mesg[1][cwiid.X]
            y = mesg[1][cwiid.Y]
            z = mesg[1][cwiid.Z]
            if STATUS == "HANDUPLIDUP":
                if b_val == True:
                    procValue(5, y)
                    procValue(6, x)
            if ACC_DEBUG or DEBUG:
                print('b_val: %s - Acc Report: x=%d, y=%d, z=%d') % (b_val, x, y, z)
        else:
            print 'Unknown Report'


def handle_buttons(buttons):
    global b_val
    global STATUS
    global SENSORS
    global ACTIONS
    global action_idx
    # The B (trigger) Button does cool things for us
    # When pressed that allows the glove sensors to be read and sent
    # It also changes what the other buttons do

    if (buttons & cwiid.BTN_B):
        b_val = True
    else:
        b_val = False

    if (buttons  & cwiid.BTN_UP):
        sendPing(False)
    elif (buttons & cwiid.BTN_DOWN):
        if b_val == False:
            action_idxidx = len(ACTIONS) - 1
            updateleds()
        else:
            if STATUS.find("LIDUP") < 0 and STATUS.find("HANDUP") < 0:
                procAction("B")
            else:
                print(STATUS)
    elif (buttons & cwiid.BTN_LEFT):
        if b_val == False:
            if action_idx == 0:
                action_idx = len(ACTIONS) - 1
            else:
                action_idx = action_idx - 1
            updateleds()
    elif (buttons & cwiid.BTN_RIGHT):
        if b_val == False:
            if action_idx == len(ACTIONS) - 1:
                action_idx = 0
            else:
                action_idx = action_idx + 1
            updateleds()
    elif (buttons & cwiid.BTN_A):
        if b_val == False:
            # Run Action
            procAction(str(action_idx))
        else:
            #Lock Wrist
            procAction("L")
    elif (buttons & cwiid.BTN_MINUS):
        if b_val == True:
            # Close Lid
            procAction("C")
        else:
            # Put away Thing
            procAction("D")
    elif (buttons & cwiid.BTN_HOME):
        if b_val == False:
            # Home Calms Servos
            print("Calming Servos")
            procAction("A")
        else:
            # Reset sensors
            print("Resetting Max")
            for z in SENSORS:
                z['MAX'] = 0
            print("Resetting Min")
            for z in SENSORS:
                z['MIN'] = 1000
    elif (buttons & cwiid.BTN_PLUS):
        if b_val == True:
            #Open Lid
            procAction("O")
        else:
            #Summon Thing
            procAction("U")
    elif (buttons & cwiid.BTN_1):
        if b_val == False:
            procAction("K")
        else:
            procAction("N")
    elif (buttons & cwiid.BTN_2):
        if b_val == False:
            procAction("W")
        else:
            procAction("M")
def sendCmd(sendstr, curname):
    global UDP_SOCK
    if len(sendstr) < 5:
        u = len(sendstr)
        p = 5 - u
        tpad  =  p * ":"
        tsendstr = sendstr + tpad
        print("Making sendstr (%s) into %s" % (sendstr, tsendstr))
        sendstr = tsendstr

    if (DEBUG or NET_DEBUG):
        if curname in SHOWLIST or sendstr.find("A") == 0:
            print ("******** %s Sending this: %s " % (curname, sendstr))
    if NETWORK:
        UDP_SOCK.sendto(sendstr, (UDP_IP, UDP_PORT))

def updateleds():
    global action_idx
    global wiimote
    wiimote.led = action_idx

def sendPing(auto):
    global wiimote
    global UDP_SOCK
    global action_idx
    sendtime = 0
    recvtime = 0
    bresp = False
    if auto == True:
        strping = "PINGA"
    else:
        strping = "PINGM"
    sendtime = int(time.time())
    UDP_SOCK.sendto(strping, (UDP_IP, UDP_PORT))
     #If data is received back from server, print
    strresult = ""
    try:
        resp, srv = UDP_SOCK.recvfrom(5)
        recvtime = int(time.time())
        totaltime = recvtime - sendtime
        strresult = "Ping Response in %s secs: %s" % (totaltime, resp)
        bresp = True
    except socket.timeout:
        strresult = "Ping Timeout - %s " % PINGTIMEOUT
        bresp = False
    if DEBUG or PNG_DEBUG:
        print(strresult)
    if auto == False:
        wiimote.led = 0
        time.sleep(1)
        if bresp == True:
            wiimote.led = 1
            time.sleep(0.2)
            wiimote.led = 2
            time.sleep(0.2)
            wiimote.led = 4
            time.sleep(0.2)
            wiimote.led = 8
            time.sleep(0.2)
            wiimote.led = 0
            time.sleep(0.2)
            wiimote.led = 8
            time.sleep(0.2)
            wiimote.led = 4
            time.sleep(0.2)
            wiimote.led = 2
            time.sleep(0.2)
            wiimote.led = 1
            time.sleep(0.2)
            wiimote.led = 0
            time.sleep(1)
        else:
            wiimote.led = 15
            time.sleep(0.2)
            wiimote.led = 0
            time.sleep(0.2)
            wiimote.led = 15
            time.sleep(0.2)
            wiimote.led = 0
            time.sleep(0.2)
            wiimote.led = 15
            time.sleep(0.2)
            wiimote.led = 0
            time.sleep(0.2)
        updateleds()

def roundval(val, rnd):
    modval = val % rnd
    retval = 0
    if modval != 0:
        if float(modval) / float(rnd) >= 0.5:
            retval = val + (rnd - modval)
        else:
            retval = val - modval
    else:
        retval = val
    return retval

def procAction(action):
    global SENSORS
    global b_val
    global UDP_SOCK
    global STATUS
    myact = ""
    if action == "U":
        if STATUS.find("LIDUP") < 0:
            procAction("O")
        myact = "A:U"
        STATUS = "HANDUPLIDUP"
    elif action == "O":
        if STATUS.find("LIDUP") < 0:
            myact = "A:O"
            STATUS = "LIDUP"
    elif action == "D":
        if STATUS.find("HANDUP") >= 0:
            myact = "A:D"
            STATUS = "HANDDOWNLIDUP"
    elif action == "C":
        if STATUS.find("HANDDOWN") >= 0 or STATUS.find("HANDUP") < 0:
            myact = "A:C"
            STATUS = "HANDDOWNLIDDOWN"
    elif action == "B":
        if STATUS.find("LIDDOWN") >= 0 or STATUS.find("LIDUP") < 0:
            myact = "A:B"
    elif action == "A":
        myact = "A:A"
    elif action == "L":
        if STATUS.find("LIDUP") >= 0:
            myact = "A:L"
            STATUS = "HANDUPLIDUP"
    else:
        # This could block some actions
        if STATUS.find("HANDUP") >= 0 or action in ALLOWED_KEYS:
            myact = "A:" + action
    if myact != "":
        sendCmd(myact, "Action")
        if DEBUG or ACT_DEBUG:
            print("Sending Action: %s" % myact)




def procValue(sens, val):
    global SENSORS
    global b_val
    global UDP_SOCK
    global STATUS

    curname = SENSORS[sens]['NAME']
    if (DEBUG or PRC_DEBUG) and curname in SHOWLIST:
        print("Proc for %s" % curname)

    if val > SENSORS[sens]['MAX']:
        SENSORS[sens]['MAX'] = val
    if val < SENSORS[sens]['MIN']:
        SENSORS[sens]['MIN'] = val
    
    if SENSORS[sens]['MAX'] == SENSORS[sens]['MIN']:
        SENSORS[sens]['MAX'] += 1

    sendval = (float(val) - SENSORS[sens]['MIN']) / (SENSORS[sens]['MAX'] - SENSORS[sens]['MIN'])
    sendval = int(sendval * 100)
    sendval = roundval(sendval, SENSORS[sens]['ROUNDVAL'])

    if SENSORS[sens]['INVERT'] == True:
        sendval = 100 - sendval
    if sendval < 10:
        pad = "00"
    elif sendval < 100:
        pad = "0"
    else:
        pad = ""

    sendstr = str(SENSORS[sens]['REMOTE']) + ":" + pad + str(sendval)
    if (DEBUG or FLX_DEBUG or PRC_DEBUG) and curname in SHOWLIST:
        print("%s - Value: %s - Min: %s - Max: %s - Last: %s - sens_thres: %s - chng_thres: %s - Sendval: %s" % (curname, val, SENSORS[sens]['MIN'], SENSORS[sens]['MAX'], SENSORS[sens]['LAST'], SENSORS[sens]['SENS_THRES'], SENSORS[sens]['CHNG_THRES'], sendval))

    sense_delta = abs(val - SENSORS[sens]['LAST'])
    if (DEBUG or PRC_DEBUG) and curname in SHOWLIST:
        print("Sense_Delta: %s" % sense_delta)
    if sense_delta >= SENSORS[sens]['SENS_THRES']:

        SENSORS[sens]['CHANGES'] += 1
        if SENSORS[sens]['CHANGES'] > SENSORS[sens]['CHNG_THRES']:
            if val > SENSORS[sens]['MAX']:
                SENSORS[sens]['MAX'] = val
            else:
                SENSORS[sens]['MAX'] = SENSORS[sens]['MAX'] - SENSORS[sens]['ADJVAL']
            if val < SENSORS[sens]['MIN']:
                SENSORS[sens]['MIN'] = val
            else:
                SENSORS[sens]['MIN'] = SENSORS[sens]['MIN'] + SENSORS[sens]['ADJVAL']
            if SENSORS[sens]['MAX'] == SENSORS[sens]['MIN']:
                SENSORS[sens]['MAX'] += 1


            if sendstr != "":
                if sendstr.find("3:") == 0:
                    pass
                elif sendstr.find("2:") == 0:
                    sendCmd(sendstr, curname)
                    newstr = sendstr.replace("2:", "3:")
                    sendCmd(newstr, curname)
                else:
                    sendCmd(sendstr, curname)
            sendstr = ""
    SENSORS[sens]['LAST'] = val

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

if __name__ == "__main__":
    main()
