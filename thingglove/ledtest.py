#!/usr/bin/python
import cwiid
import time

wiimote = None
rpt_mode = 0
connected = False
rumble = 0
BUT_DEBUG = False
DEBUG = False
b_val = False
curidx = 0
# Max 16 actions assigned here

actionlist = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

def main():
    global wiimote
    global rpt_mode
    global connected
    global rumble
    global b_val
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
    rpt_mode ^= cwiid.RPT_BTN

    # Enable the messages in callback
    wiimote.enable(cwiid.FLAG_MESG_IFC);
    wiimote.rpt_mode = rpt_mode

    while True:
        time.sleep(1)


def callback(mesg_list, time):
    global b_val
    for mesg in mesg_list:
        if mesg[0] == cwiid.MESG_BTN:
            handle_buttons(mesg[1])
            if BUT_DEBUG or DEBUG:
                print("Time: %s" % time)
                print 'Button Report: %.4X' % mesg[1]
        else:
            print 'Unknown Report'


def updateleds():
    global curidx
    global wiimote
    wiimote.led = curidx



def handle_buttons(buttons):
    global b_val
    global curidx
    global actionlist
    # The B (trigger) Button does cool things for us
    # When pressed that allows the glove sensors to be read and sent
    # It also changes what the other buttons do

    if (buttons & cwiid.BTN_B):
        b_val = True
    else:
        b_val = False

    if (buttons  & cwiid.BTN_UP):
        if b_val == False:
            curidx = 0
            updateleds()
    elif (buttons & cwiid.BTN_DOWN):
        if b_val == False:
            curidx = len(actionlist) - 1
            updateleds()
    elif (buttons & cwiid.BTN_LEFT):
        if b_val == False:
            if curidx == 0:
                curidx = len(actionlist) - 1
            else:
                curidx = curidx - 1
            updateleds()
    elif (buttons & cwiid.BTN_RIGHT):
        if b_val == False:
            if curidx == len(actionlist) - 1:
                curidx = 0
            else:
                curidx = curidx + 1
            updateleds()

    elif (buttons & cwiid.BTN_1):
        pass
    elif (buttons & cwiid.BTN_2):
        pass
    elif (buttons & cwiid.BTN_PLUS):
        pass
    elif (buttons & cwiid.BTN_MINUS):
        pass
    elif (buttons & cwiid.BTN_A):
        if b_val == False:
            print("Running IDX: %s" % curidx)
        elif b_val == True:
            pass
    elif (buttons & cwiid.BTN_HOME):
        pass
if __name__ == "__main__":
    main()


