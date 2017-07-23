#!/usr/bin/python
import RPi.GPIO as GPIO                           #Import GPIO library
import time                                       #Import time library
#GPIO.setmode(GPIO.BOARD)                         #Set GPIO pin numbering
GPIO.setmode(GPIO.BCM)                            #Set GPIO BCM Numbering
pir = 6                                          #Associate BCM 6 to pir
GPIO.setup(pir, GPIO.IN)                          #Set pin as GPIO in 
print "Waiting for sensor to settle"
time.sleep(3)                                     #Waiting 2 seconds for the sensor to initiate
print "Detecting motion"
while True:
   if GPIO.input(pir):                            #Check whether pir is HIGH
      print "Motion Detected!"
      time.sleep(2)                               #D1- Delay to avoid multiple detection
   time.sleep(0.1)    
