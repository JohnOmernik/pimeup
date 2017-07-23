#!/usr/bin/python

#Libraries
import RPi.GPIO as GPIO
import time
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 #set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24
GPIO_IR = 6 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(GPIO_IR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 

def main ():
    prev_ir_state = False
    curr_ir_state = False

    try:
        while True:
            time.sleep(0.1)
            prev_ir_state = curr_ir_state
            curr_ir_state = GPIO.input(GPIO_IR)
            if curr_ir_state != prev_ir_state:
                new_state = "HIGH" if curr_ir_state else "LOW"
                if new_state == "HIGH":
                    dist = distance()
                    if dist > 2000:
                        print("Somethings moving around me, but I can't see it")
                    else:
                        print("I caught you moving and you are standing %.1f cm in front of me" % dist)
            

        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
 
if __name__ == '__main__':
    main()
