#!/usr/bin/python

#Libraries
import RPi.GPIO as GPIO
import time
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 #set GPIO Pins
GPIO_RELAY = 16
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_RELAY, GPIO.OUT) 

def main ():

    print("Setting to off")
    GPIO.output(GPIO_RELAY, False)

    print("Waiting 5 seconds")
    time.sleep(5)

    print("Setting to on")
    GPIO.output(GPIO_RELAY, True)

    print("Waiting 5 seconds")
    time.sleep(5)

    print("Setting to off")
    GPIO.output(GPIO_RELAY, False)
    

if __name__ == '__main__':
    main()
