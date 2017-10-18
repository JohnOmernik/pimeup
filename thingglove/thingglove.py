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
NETWORK = 0
SHOWLIST = [ "Wrist", "Pinky", "Ring", "Middle", "Index", "Thumb" ]
mythres = 2


# Hardware SPI configuration: (Do not Modify)
####################
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
####################

SENSORS = [
    {"NAME": "Pinky", "TYPE": "adc", "REMOTE": 4, "MIN":1000, "MAX": 0, "CHANGES":0, "LAST": 0, "CHANGED": False, "THRES": mythres},
    {"NAME": "Ring", "TYPE": "adc", "REMOTE": 3, "MIN":1000, "MAX": 0, "CHANGES":0, "LAST": 0, "CHANGED": False, "THRES": mythres},
    {"NAME": "Middle", "TYPE": "adc", "REMOTE": 2, "MIN":1000, "MAX": 0, "CHANGES":0, "LAST": 0, "CHANGED": False, "THRES": mythres},
    {"NAME": "Index", "TYPE": "adc", "REMOTE": 1, "MIN":1000, "MAX": 0, "CHANGES":0, "LAST": 0, "CHANGED": False, "THRES": mythres},
    {"NAME": "Thumb", "TYPE": "adc", "REMOTE": 0, "MIN":1000, "MAX": 0, "CHANGES":0, "LAST": 0, "CHANGED": False, "THRES": mythres},
    {"NAME": "Wrist", "TYPE": "acc", "REMOTE": 5, "MIN": 1000, "MAX": 0, "CHANGE":0, "LAST": 0, "CHANGED": False, "THRES": mythres}
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
                for x in range(len(SENSORS)):
                    if x['TYPE'] == 'adc':
                        flex_val = mcp.read_adc(x)
                        procValue(x, flex_val)
            time.sleep(tdelay)
    except KeyboardInterrupt:
        print("")
        print("Weee - Exiting")
        s.close()
        sys.exit(0)


def callback(mesg_list, time):
    global SENSORS
    global b_val
    for mesg in mesg_list:
        if mesg[0] == cwiid.MESG_BTN:
            handle_buttons(mesg[1])
            if DEBUG:
                print("Time: %s" % time)
                print 'Button Report: %.4X' % mesg[1]
        elif mesg[0] == cwiid.MESG_ACC:
            x = mesg[1][cwiid.X]
            y = mesg[1][cwiid.Y]
            z = mesg[1][cwiid.Z]

            if DEBUG:
                print('Acc Report: x=%d, y=%d, z=%d') % (x, y, z)
                if b_val == True:
                    provValue(5, y)
        else:
            print 'Unknown Report'

def handle_buttons(buttons):
    global b_val

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
        print("Up")
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
        print("A")
    elif (buttons & cwiid.BTN_HOME):
        print("Home")



def procValue(sens, val):
    global SENSORS
    global b_val
    global udp_sock

    curname = SENSORS[sens]['NAME']

    if val > SENSORS[s]['MAX']:
        SENSORS[sens]['MAX'] = val
    if v < SENSORS[sens]['MIN']:
        SENSORS[sens]['MIN'] = val
    if SENSORS[sens]['MAX'] == SENSORS[sens]['MIN']:
        SENSORS[sens]['MAX'] += 1

    sendval = (float(val) - SENSORS[sens]['MIN']) / (SENSORS[sens]['MAX'] - SENSORS[sens]['MIN'])
    sendval = int(sendval * 100)

    if sendval < 10:
        pad = "00"
    elif sendval < 100:
        pad = "0"
    else:
        pad = ""

    sendstr = str(SENSORS[sens]['REMOTE']) + ":" + pad + str(sendval)
    if DEBUG:
        if curname in SHOWLIST:
            print("%s - Value: %s - Min: %s - Max: %s - Sendval: %s" % (curname, val, SENSORS[sens]['MIN'], SENSORS[sens]['MAX'], sendval))

    sense_delta = abs(v - SENSORS[sens]['LAST'])

    if sense_delta > SENSORS[sens]['THRES']:
        SENSORS[sens]['CHANGES'] += 1
        if SENSORS[sens]['CHANGES'] > 5:
            if sendstr != "":
                if curname in SHOWLIST:
                    print ("******** %s - Sending this: %s " % (curname, sendstr))
                if NETWORK:
                    udp_sock.sendto(sendstr, (udp_ip, udp_port))
                sendstr = ""
    SENSORS[sens]['LAST'] = val

if __name__ == "__main__":
    main()
