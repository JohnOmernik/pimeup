#!/usr/bin/python
import cwiid
import sys
import time
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
import atexit

# create a default object, no changes to I2C address or frequency
mh = Adafruit_MotorHAT(addr=0x60)


mesg = False
led = 0
rpt_mode = 0
rumble = 0
erect_state = 0 # Thing is down (1 is up)
erect_change = 0.0
erect_thres = 1.0
turbo = False
# Motor state 0 is stopped, 50 is normal, 100 is with trigger down

left_motor_state = 0   
right_motor_state = 0 
def main():
    #Connect to address given on command-line, if present
    print 'Put Wiimote in discoverable mode now (press 1+2)...'
    global wiimote
    global rpt_mode
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
    rpt_mode ^= cwiid.RPT_ACC
    rpt_mode ^= cwiid.RPT_BTN

    # Enable the messages in callback
    wiimote.enable(cwiid.FLAG_MESG_IFC);

#    print(dir(cwiid))
#    sys.exit(0)

    wiimote.rpt_mode = rpt_mode
    exit = 0
    while not exit:
        c = sys.stdin.read(1)
        exit =  handle_input(wiimote, c)
    wiimote.close()


def handle_buttons(buttons):
    global left_motor_state
    global right_motor_state
    global turbo
    new_left_state = 0
    new_right_state = 0

    if (buttons & cwiid.BTN_B):
        print("Setting turbo True")
        turbo = True
    else:
        print("Setting turbo False")
        turbo = False

    if (buttons  & cwiid.BTN_UP):
        if turbo == True:
            print("Fast Forward!")
            new_left_state += 100
            new_right_state += 100
        else:
            print("Slow forward")
            new_left_state += 50
            new_right_state += 50
    elif (buttons & cwiid.BTN_DOWN):
        if turbo == True:
            new_left_state += -100
            new_right_state += -100
        else:
            new_left_state += -50
            new_right_state += -50
    elif (buttons & cwiid.BTN_LEFT):
        if turbo == True:
            new_right_state += 50
            new_left_state += -50
        else:
            new_right_state += 25
            new_left_state += -25
    elif (buttons & cwiid.BTN_RIGHT):
        if turbo == True:
            new_right_state += -50
            new_left_state += 50
        else:
            new_right_state += -25
            new_left_state += 25
    else:  # No directions are pressed, if the state of either motor is > 0 then we clear
        new_right_state = 0
        new_left_state = 0



    if new_right_state > 100:
        new_right_state = 100
    elif new_right_state < -100:
        new_right_state = -100
    if new_left_state > 100:
        new_left_state = 100
    elif new_left_state < -100:
        new_left_state = -100


    if left_motor_state != new_left_state or right_motor_state != new_right_state:
        left_motor_state = new_left_state
        right_motor_state = new_right_state
        setMotors()



    if (buttons & cwiid.BTN_1):
        print("Button 1")
    elif (buttons & cwiid.BTN_2):
        print("Button 2")
    elif (buttons & cwiid.BTN_PLUS):
        print("Plus")
    elif (buttons & cwiid.BTN_MINUS):
        print("Minus")
    elif (buttons & cwiid.BTN_A):
        print("A")
    elif (buttons & cwiid.BTN_HOME):
        print("Home")


#BTN_1', 'BTN_2', 'BTN_A', 'BTN_B', 'BTN_DOWN', 'BTN_HOME', 'BTN_LEFT', 'BTN_MINUS', 'BTN_PLUS', 'BTN_RIGHT', 'BTN_UP',


def speedTranslator(speed):
    sp = 0
    di = Adafruit_MotorHAT.FORWARD
    if speed == 0:
        pass
    elif abs(speed) == 25:
        sp = 64
    elif abs(speed) == 50:
        sp = 128
    elif abs(speed) == 75:
        sp = 192
    elif abs(speed) == 100:
        sp = 255
    if speed < 0:
        di = Adafruit_MotorHAT.BACKWARD

    return sp, di        

def setMotors():
    global left_motor_state
    global right_motor_state


    ls, ld = speedTranslator(left_motor_state)
    rs, rd = speedTranslator(right_motor_state)

    print("Changing Speed!-----------------------")
    print("\tSetting the left motor to speed: %s - Direction: %s" % (ls, ld))
    print("\tSetting the right motor to speed: %s - Direction: %s" % (rs, rd))
    print("")

    lm = mh.getMotor(1)
    rm = mh.getMotor(2)

    # set the speed to start, from 0 (off) to 255 (max speed)
    lm.setSpeed(ls) 
    lm.run(ld)
    rm.setSpeed(rs)
    rm.run(rd)




def callback(mesg_list, time):
    global erect_state
    global erect_change
    global erect_thres
    
    for mesg in mesg_list:
        if mesg[0] == cwiid.MESG_BTN:
            handle_buttons(mesg[1])
#            print("Time: %s" % time)
 #           print 'Button Report: %.4X' % mesg[1]


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

        else:
            print 'Unknown Report'

# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
#    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
#   mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)


if __name__ == "__main__":
    main()
