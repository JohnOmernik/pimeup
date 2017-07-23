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
last_dist = 0
last_dist_time = 0

def main ():
    print("PIR Module Test (CTRL+C to exit)")
    try:
        GPIO.add_event_detect(GPIO_IR, GPIO.RISING, callback=MOTION)
        while 1:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Quit")
        GPIO.cleanup()

def MOTION(PIR_PIN):
    global last_dist
    global last_dist_time
    dist = distance()
    d_time = int(time.time())
    print("%s\tOh hay I saw something" % d_time)
    if dist < 2000:
        print("%s\tI think I spot you at %.1f cm" % (d_time, dist))    
        last_dist = dist
        last_dist_time = d_time
    else:
        if last_dist > 0:
            del_time = d_time - last_dist_time
            print("%s\tYa know I feel like you are hanging around and only %s seconds ago you were at %.1f cm away" % (d_time, del_time, last_dist))
        else:
            print("%s\tPretty Sneaky... " % d_time)


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
