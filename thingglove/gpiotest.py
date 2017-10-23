#!/usr/bin/python


#Libraries
import RPi.GPIO as GPIO
import time
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 #set GPIO Pins
GPIO_MODE= 12
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_MODE, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


while True:
    if GPIO.input(GPIO_MODE) == 1:
        print("Pin is high")
    elif GPIO.input(GPIO_MODE) == 0:
        print("Pin is low")
    time.sleep(2)

