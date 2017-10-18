#!/usr/bin/python
import time
import sys
import socket
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import cwiid

udp_ip = '192.168.0.130'
udp_port = 30000
tdelay = 0.2
DEBUG = 0
ACC_DEBUG = 0
BUT_DEBUG = 0
FLX_DEBUG = 0
PRC_DEBUG = 0
NET_DEBUG = 1
NETWORK = 0
#SHOWLIST = [ "Wrist", "Pinky", "Ring", "Middle", "Index", "Thumb" ]
SHOWLIST = [ "WristFlex", "WristTurn" ]
# Defaults:
mysens_thres = 3
mychng_thres = 5
# Used for Testing:
tmpsens_thres = 2
tmpchng_thres = 5
# Hardware SPI configuration: (Do not Modify)
####################
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
####################


STATUS = ""
SENSORS = [
    {"NAME": "Pinky", "TYPE": "adc", "REMOTE": 4, "MIN":1000, "MAX": 0, "CHANGES":0, "LAST": 0, "CHANGED": False, "SENS_THRES": mysens_thres, "CHNG_THRES": mychng_thres, "INVERT": False},
    {"NAME": "Ring", "TYPE": "adc", "REMOTE": 3, "MIN":1000, "MAX": 0, "CHANGES":0, "LAST": 0, "CHANGED": False, "SENS_THRES": mysens_thres, "CHNG_THRES": mychng_thres, "INVERT": False},
    {"NAME": "Middle", "TYPE": "adc", "REMOTE": 2, "MIN":1000, "MAX": 0, "CHANGES":0, "LAST": 0, "CHANGED": False, "SENS_THRES": mysens_thres, "CHNG_THRES": mychng_thres, "INVERT": False},
    {"NAME": "Index", "TYPE": "adc", "REMOTE": 1, "MIN":1000, "MAX": 0, "CHANGES":0, "LAST": 0, "CHANGED": False, "SENS_THRES": mysens_thres, "CHNG_THRES": mychng_thres, "INVERT": False},
    {"NAME": "Thumb", "TYPE": "adc", "REMOTE": 0, "MIN":1000, "MAX": 0, "CHANGES":0, "LAST": 0, "CHANGED": False, "SENS_THRES": mysens_thres, "CHNG_THRES": mychng_thres, "INVERT": False},
    {"NAME": "WristFlex", "TYPE": "acc", "REMOTE": 5, "MIN": 1000, "MAX": 0, "CHANGES":0, "LAST": 0, "CHANGED": False, "SENS_THRES": tmpsens_thres, "CHNG_THRES": mychng_thres, "INVERT": True},
    {"NAME": "WristTurn", "TYPE": "acc", "REMOTE": 6, "MIN": 1000, "MAX": 0, "CHANGES":0, "LAST": 0, "CHANGED": False, "SENS_THRES": tmpsens_thres, "CHNG_THRES": mychng_thres, "INVERT": False}
]

#SERVOS.append({"DESC":"Thumb", "RANGE_MIN": 275, "RANGE_MAX": 575, "INVERT": False})
#SERVOS.append({"DESC":"Pointer", "RANGE_MIN": 300, "RANGE_MAX": 575, "INVERT": True})
#SERVOS.append({"DESC":"Middle", "RANGE_MIN": 325, "RANGE_MAX": 575, "INVERT": True})
#SERVOS.append({"DESC":"Ring", "RANGE_MIN":  275, "RANGE_MAX": 550, "INVERT": True})
#SERVOS.append({"DESC":"Pinky", "RANGE_MIN": 300, "RANGE_MAX": 575, "INVERT": True})
#SERVOS.append({"DESC":"WristFlex", "RANGE_MIN": 300, "RANGE_MAX": 600, "INVERT": False})
#SERVOS.append({"DESC":"WristTurn", "RANGE_MIN": 135, "RANGE_MAX": 660, "INVERT": False})
#SERVOS.append({"DESC":"WristUp", "RANGE_MIN": 360, "RANGE_MAX" : 620, "INVERT": False})

rpt_mode = 0
wiimote = None
connected = False
rumble = 0
b_val = False
udp_socket = None
def main():
    global wiimote
    global rpt_mode
    global connected
    global rumble
    global NETWORK
    global b_val
    global udp_sock
    global STATUS

# Setup Network (Currently UDP)
    if NETWORK == 1:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

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
        # read the analog pin
            if b_val == True:
                if STATUS == "LIDUPHANDUP":
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
            if STATUS == "LIDUPHANDUP":
                if b_val == True:
                    procValue(5, y)
                    procValue(6, x)
            if ACC_DEBUG or DEBUG:
                print('b_val: %s - Acc Report: x=%d, y=%d, z=%d') % (b_val, x, y, z)
        else:
            print 'Unknown Report'

def handle_buttons(buttons):
    global b_val
    global status

    # The B (trigger) Button does cool things for us
    # When pressed that allows the glove sensors to be read and sent
    # It also changes what the other buttons do

    if (buttons & cwiid.BTN_B):
        if DEBUG:
            print("Setting B True")
        b_val = True
    else:
        if DEBUG:
            print("Setting B False")
        b_val = False

    if (buttons  & cwiid.BTN_UP):
        if b_val == False:
            procAction("O")
    elif (buttons & cwiid.BTN_DOWN):
        print("Down")
    elif (buttons & cwiid.BTN_LEFT):
        print("Left")
    elif (buttons & cwiid.BTN_RIGHT):
        print("Right")
    elif (buttons & cwiid.BTN_1):
        print("One")
    elif (buttons & cwiid.BTN_2):
        print("Two")
    elif (buttons & cwiid.BTN_PLUS):
        print("Plus")
    elif (buttons & cwiid.BTN_MINUS):
        print("Minus")
    elif (buttons & cwiid.BTN_A):
        # A will summon thing if B is not pressed, and put him a way if B is pressed
        if b_val == False:
            procAction("U")
        if b_val == True:"
            procAction("P")
    elif (buttons & cwiid.BTN_HOME):
        # Home Calms Servos
        procAction("0")

def sendCmd(sendstr, curname):
    global udp_sock
    if (DEBUG or NET_DEBUG):
        if curname in SHOWLIST or sendstr.find("A") == 0::
            print ("******** %s Sending this: %s " % (curname, sendstr))
    if NETWORK:
        udp_sock.sendto(sendstr, (udp_ip, udp_port))

def procAction(action):
    global SENSORS
    global b_val
    global udp_sock
    global STATUS

    if action == "U":
        if STATUS.find("LIDUP") < 0:
            procAction("O")
        sendCmd("A:U", "Action")
        STATUS = "LIDUPHANDUP"
    elif action == "O":
        sendCmd("A:O", "Action")
        STATUS = "LIDUP"
    elif action == "P":
        if STATUS.find("HANDUP") >= 0:
            sendCmd("A:P", "Action")
            STATUS = "HANDDOWN"
    elif action == "C":
        if STATUS.find("HANDDOWN") < 0:
            procAction("P")
        sendCmd("A:C", "Action")
        STATUS = "LIDDOWNHANDDOWN"
    elif action == "0":
        sendCmd("A:0", "Action")




def procValue(sens, val):
    global SENSORS
    global b_val
    global udp_sock
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
            if sendstr != "":
                sendCmd(sendstr, curname)
            sendstr = ""
    SENSORS[sens]['LAST'] = val

if __name__ == "__main__":
    main()
