#!/usr/bin/python

# Import the PCA9685 module.
import Adafruit_PCA9685
import time
import random
import sys



# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685(0x40)
pwm.set_pwm_freq(60)

print("PWM Setup")
SRV_OPTIONS = []

SRV_OPTIONS.append({"SRV": 0, "DESC":"Thumb", "RANGE_MIN": 275, "RANGE_MAX": 575})
SRV_OPTIONS.append({"SRV": 1, "DESC":"Pointer", "RANGE_MIN": 300, "RANGE_MAX": 575})
SRV_OPTIONS.append({"SRV": 2, "DESC":"Middle", "RANGE_MIN": 325, "RANGE_MAX": 575})
SRV_OPTIONS.append({"SRV": 3, "DESC":"Ring", "RANGE_MIN":  275, "RANGE_MAX": 550})
SRV_OPTIONS.append({"SRV": 4, "DESC":"Pinky", "RANGE_MIN": 300, "RANGE_MAX": 575})
SRV_OPTIONS.append({"SRV": 5, "DESC":"WristFlex", "RANGE_MIN": 300, "RANGE_MAX": 600})
SRV_OPTIONS.append({"SRV": 6, "DESC":"WristTurn", "RANGE_MIN": 135, "RANGE_MAX": 650})

power_brightness = "/sys/devices/platform/leds/leds/led1/brightness"
def main():
    sleeptime = 5
    maxoff = 3
    numoff = 0
    runwell = True
    maxtimes = 100
    numtimes = 0
    print("Beginning Loop in starting fist")
    fistsalute()
    handlist = [ fistsalute, queenswave, naughty, pointy, comehere, rockon ]
    curidx = 0
    while runwell:
        try:
            curtime = int(time.time())
            curts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(curtime))
            with open(power_brightness) as read_state:
                curpwr = int(read_state.read())
            curpwr = True
            numtimes += 1
            #curidx = random.randint(0, len(handlist)-1)
            print("Picking: %s" % curidx)
            handlist[curidx]()
            if curidx == len(handlist) - 1:
                curidx = 0
            else:
                curidx += 1
            if curpwr == 0:
                numoff += 1
            else:
                numoff = 0

            if numoff >= maxoff:
                print("Power off for %s in a row @ %s - exiting" % (maxoff, curts))
                runwell = False
            elif numtimes >= maxtimes and maxtimes > 0:
                print("Max times reached @ %s - Power: %s" % (curts, curpwr))
                runwell = False
            else:
                print("Power Status @ %s: %s" % (curts, curpwr))

            time.sleep(1)
            fistsalute()
            time.sleep(sleeptime)
        except KeyboardInterrupt:
            closeitdown()
    closeitdown()







def closeitdown():
    print("Closing it down")
    pwm.set_pwm(0, 4096, 0)
    pwm.set_pwm(1, 4096, 0)
    pwm.set_pwm(2, 4096, 0)
    pwm.set_pwm(3, 4096, 0)
    pwm.set_pwm(4, 4096, 0)
    pwm.set_pwm(5, 4096, 0)
    pwm.set_pwm(6, 4096, 0)
    sys.exit(0)



#SRV_OPTIONS.append({"SRV": 0, "DESC":"Thumb", "RANGE_MIN": 275, "RANGE_MAX": 575})
#SRV_OPTIONS.append({"SRV": 1, "DESC":"Pointer", "RANGE_MIN": 300, "RANGE_MAX": 575})
#SRV_OPTIONS.append({"SRV": 2, "DESC":"Middle", "RANGE_MIN": 325, "RANGE_MAX": 600})
#SRV_OPTIONS.append({"SRV": 3, "DESC":"Ring", "RANGE_MIN":  275, "RANGE_MAX": 550})
#SRV_OPTIONS.append({"SRV": 4, "DESC":"Pinky", "RANGE_MIN": 300, "RANGE_MAX": 575})
#SRV_OPTIONS.append({"SRV": 5, "DESC":"WristFlex", "RANGE_MIN": 250, "RANGE_MAX": 650})
#SRV_OPTIONS.append({"SRV": 6, "DESC":"WristTurn", "RANGE_MIN": 225, "RANGE_MAX": 625})

#thumb: 275 in 575 out
#pointer: 300 up 575 down
#middle: 325 up 575 down
#ring: 275 up 550 down
#pinky: 300 up 575 down

#wristflex: 300 forward 600 back
#wristturn: 135 staight front of hand-  rotate twoard thum 650 back of hand forward Past straight on. 620 straigh on with back of hand
def rockon():
    print("Party on!")
    makefist()
    pwm.set_pwm(0, 0, 575)
    pwm.set_pwm(1, 0, 300)
    pwm.set_pwm(4, 0, 300)
    time.sleep(4)

def pointy():
    print("That's the guy...")
    makefist()
    pwm.set_pwm(6, 0, 135)
    pwm.set_pwm(5, 0, 300)
    pwm.set_pwm(1, 0, 300)
    time.sleep(0.5)
    pwm.set_pwm(5, 0, 350)
    time.sleep(0.4)
    pwm.set_pwm(5, 0, 300)
    time.sleep(0.4)
    pwm.set_pwm(5, 0, 350)
    time.sleep(0.4)
    pwm.set_pwm(5, 0, 300)
    time.sleep(0.4)
    pwm.set_pwm(5, 0, 350)

def comehere():
    print("I beckon")
    makefist()
    pwm.set_pwm(6, 0, 620)
    pwm.set_pwm(5, 0, 600)
    time.sleep(0.5)
    pwm.set_pwm(1, 0, 300)
    time.sleep(0.5)
    pwm.set_pwm(1, 0, 575)
    time.sleep(0.5)
    pwm.set_pwm(1, 0, 300)
    time.sleep(0.5)
    pwm.set_pwm(1, 0, 575)
    time.sleep(0.5)
    pwm.set_pwm(1, 0, 300)
    time.sleep(0.5)
    pwm.set_pwm(1, 0, 575)
    

def naughty():
    print("Oh you filthy...")
    makefist()
    pwm.set_pwm(6, 0, 620)
    pwm.set_pwm(2, 0, 325)
    time.sleep(4)

def makefist():
    print("Fists!")
    pwm.set_pwm(0, 0, 275)
    pwm.set_pwm(1, 0, 575)
    pwm.set_pwm(2, 0, 600)
    pwm.set_pwm(3, 0, 550)
    pwm.set_pwm(4, 0, 575)
    time.sleep(0.4)


def fistsalute():
    makefist()
    print("Power to the People!")
    pwm.set_pwm(5, 0, 500)
    pwm.set_pwm(6, 0, 135)

def queenswave():
    print("Waving like the queen!")
    # Set Fingers open with thumb in
    pwm.set_pwm(0, 0, 275)
    pwm.set_pwm(1, 0, 375)
    pwm.set_pwm(2, 0, 300)
    pwm.set_pwm(3, 0, 325)
    pwm.set_pwm(4, 0, 375)
    #set wrist up
    time.sleep(0.2)
    pwm.set_pwm(5, 0, 500)
    time.sleep(0.2)

    pwm.set_pwm(6, 0, 135)
    time.sleep(1)
    pwm.set_pwm(6, 0, 160)
    time.sleep(1)
    pwm.set_pwm(6, 0, 136)
    time.sleep(1)
    pwm.set_pwm(6, 0, 160)
    time.sleep(1)
    pwm.set_pwm(6, 0, 135)
    time.sleep(1)
    pwm.set_pwm(6, 0, 160)
    time.sleep(1)



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
