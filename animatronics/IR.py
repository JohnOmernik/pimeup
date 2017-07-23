#!/usr/bin/python

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
PIR_PIN = 6
GPIO.setup(PIR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
time.sleep(10)
def main ():
    print("PIR Module Test (CTRL+C to exit)")

    try:
        GPIO.add_event_detect(PIR_PIN, GPIO.RISING, callback=MOTION)
        while 1:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Quit")
        GPIO.cleanup()

def MOTION(PIR_PIN):
    print("Motion Detected!")

if __name__ == '__main__':
    main()
