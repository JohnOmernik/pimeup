#!/usr/bin/python
import cwiid
import sys
import time

menu = '''1: toggle LED 1
2: toggle LED 2
3: toggle LED 3
4: toggle LED 4
5: toggle rumble
a: toggle accelerometer reporting
b: toggle button reporting
m: toggle messages
p: print this menu
r: request status message ((t) enables callback output)
s: print current state
t: toggle status reporting
x: exit'''

mesg = False
led = 0
rpt_mode = 0
rumble = 0
erect_state = 0 # Thing is down (1 is up)
erect_change = 0.0
erect_thres = 1.0
def main():

    #Connect to address given on command-line, if present
    print 'Put Wiimote in discoverable mode now (press 1+2)...'
    global wiimote

    global connected
    connected = False
    print("Trying Connection")
    print ("Press 1+2")
    while not connected:
        try:
            wiimote = cwiid.Wiimote()
            print("Connected!")
            connected = True
        except:
            print("Trying Again, please press 1+2")
            time.sleep(1)


    wiimote.mesg_callback = callback

    print("For Thing we enable ACC and Button")
    w = handle_input(wiimote, 'b')
    i = handle_input(wiimote, 'a')
    print menu
    exit = 0
    while not exit:
        c = sys.stdin.read(1)
        exit =  handle_input(wiimote, c)
    wiimote.close()

def handle_input(wiimote, instr):
    global led
    global mesg
    global rumble
    global rpt_mode
    retval = 0
    c = instr
    if c == '1':
        print("Toggling LED1")
        led ^= cwiid.LED1_ON
        wiimote.led = led
    elif c == '2':
        print("Toggling LED2")
        led ^= cwiid.LED2_ON
        wiimote.led = led
    elif c == '3':
        print("Toggling LED3")
        led ^= cwiid.LED3_ON
        wiimote.led = led
    elif c == '4':
        print("Toggling LED4")
        led ^= cwiid.LED4_ON
        wiimote.led = led
    elif c == '5':
        print("Toggling Rumble")
        rumble ^= 1
        wiimote.rumble = rumble
    elif c == 'a':
        print("Toggling Report Accelorometer")
        rpt_mode ^= cwiid.RPT_ACC
        wiimote.rpt_mode = rpt_mode
    elif c == 'b':
        print("Toggling Button Reports")
        rpt_mode ^= cwiid.RPT_BTN
        wiimote.rpt_mode = rpt_mode
    elif c == 'm':
        print("Toggle messages")
        mesg = not mesg
        if mesg:
            wiimote.enable(cwiid.FLAG_MESG_IFC);
        else:
            wiimote.disable(cwiid.FLAG_MESG_IFC);
    elif c == 'p':
        print menu
    elif c == 'r':
        print("Requesting Status")
        wiimote.request_status()
    elif c == 's':
        print("Printing State")
        print_state(wiimote.state)
    elif c == 't':
        print("Toggling Status Reporting")
        rpt_mode ^= cwiid.RPT_STATUS
        wiimote.rpt_mode = rpt_mode
    elif c == 'x':
        exit = -1;
        retval = -1        
    elif c == '\n':
        pass
    else:
        print 'invalid option'
    return retval

def print_state(state):
    print 'Report Mode:',
    for r in ['STATUS', 'BTN', 'ACC', 'IR', 'NUNCHUK', 'CLASSIC', 'BALANCE', 'MOTIONPLUS']:
        if state['rpt_mode'] & eval('cwiid.RPT_' + r):
            print r,
    print

    print 'Active LEDs:',
    for led in ['1','2','3','4']:
        if state['led'] & eval('cwiid.LED' + led + '_ON'):
            print led,
    print

    print 'Rumble:', state['rumble'] and 'On' or 'Off'

    print 'Battery:', int(100.0 * state['battery'] / cwiid.BATTERY_MAX)

    if 'buttons' in state:
        print 'Buttons:', state['buttons']

    if 'acc' in state:
        print 'Acc: x=%d y=%d z=%d' % (state['acc'][cwiid.X],
                                       state['acc'][cwiid.Y],
                                       state['acc'][cwiid.Z])

    if 'ir_src' in state:
        valid_src = False
        print 'IR:',
        for src in state['ir_src']:
            if src:
                valid_src = True
                print src['pos'],

        if not valid_src:
            print 'no sources detected'
        else:
            print

    if state['ext_type'] == cwiid.EXT_NONE:
        print 'No extension'
    elif state['ext_type'] == cwiid.EXT_UNKNOWN:
        print 'Unknown extension attached'
    elif state['ext_type'] == cwiid.EXT_NUNCHUK:
        if state.has_key('nunchuk'):
            print 'Nunchuk: btns=%.2X stick=%r acc.x=%d acc.y=%d acc.z=%d' % \
              (state['nunchuk']['buttons'], state['nunchuk']['stick'],
               state['nunchuk']['acc'][cwiid.X],
               state['nunchuk']['acc'][cwiid.Y],
               state['nunchuk']['acc'][cwiid.Z])
    elif state['ext_type'] == cwiid.EXT_CLASSIC:
        if state.has_key('classic'):
            print 'Classic: btns=%.4X l_stick=%r r_stick=%r l=%d r=%d' % \
              (state['classic']['buttons'],
               state['classic']['l_stick'], state['classic']['r_stick'],
               state['classic']['l'], state['classic']['r'])
    elif state['ext_type'] == cwiid.EXT_BALANCE:
        if state.has_key('balance'):
            print 'Balance: right_top=%d right_bottom=%d left_top=%d left_bottom=%d' % \
              (state['balance']['right_top'], state['balance']['right_bottom'],
               state['balance']['left_top'], state['balance']['left_bottom'])
    elif state['ext_type'] == cwiid.EXT_MOTIONPLUS:
        if state.has_key('motionplus'):
            print 'MotionPlus: angle_rate=(%d,%d,%d)' % state['motionplus']['angle_rate']

def callback(mesg_list, time):
    global erect_state
    global erect_change
    global erect_thres
    for mesg in mesg_list:
        if mesg[0] == cwiid.MESG_BTN:
            print("Time: %s" % time)
            print 'Button Report: %.4X' % mesg[1]


        elif mesg[0] == cwiid.MESG_ACC:
            x = mesg[1][cwiid.X]
            y = mesg[1][cwiid.Y]
            z = mesg[1][cwiid.Z]

            thing_state = 0 # Down
            thing_state = 1 # Up
            
            if y > 115:
                thing_state = 0
            elif y < 110 :
                thing_state = 1
            if thing_state != erect_state:
                if time - erect_change > erect_thres:
                    print("Time: %s" % time)
                    if thing_state == 1:
                        print("Putting Thing up")
                    else:
                        print("Putting Thing Down")
                    erect_state = thing_state
                    erect_change = time                
#            print 'Acc Report: x=%d, y=%d, z=%d' % \
 #                 (mesg[1][cwiid.X], mesg[1][cwiid.Y], mesg[1][cwiid.Z])

        elif mesg[0] ==  cwiid.MESG_ERROR:
            print "Error message received"
            global wiimote
            wiimote.close()
            exit(-1)
        else:
            print 'Unknown Report'


if __name__ == "__main__":
    main()
