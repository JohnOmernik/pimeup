#!/usr/bin/python

#from Adafruit_PWM_Servo_Driver import PWM
import time
import random
import sys
import socket
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)


# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25
 
# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)



# Initialise the PWM device using the default address
#pwm = PWM(0x40)
# Note if you'd like more debug output you can instead run:
#pwm = PWM(0x40, debug=True)
#pwm.setPWMFreq(60)                        # Set frequency to 60 Hz

DEBUG = 1

SENSORS = {}
SENSORS["MIDDLE"] = {"ADC": 0, "REMOTE": 4, "MIN":1000, "MAX": 0, "CHANGES":0, "LAST": 0, "CHANGED": False, "THRES": 5}


def main():
    #flex sensor
    TCP_IP = '192.168.0.122'
    TCP_PORT = 30000
    tdelay = 0.2
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
    except:
        print("Error connecting to %s:%s" % (TCP_IP, TCP_PORT))
        sys.exit(1)


    try:
        while True:
        # read the analog pin
            flex_middle = readadc(SENSORS['MIDDLE']['ADC'], SPICLK, SPIMOSI, SPIMISO, SPICS)
            procValue('MIDDLE', flex_middle, s)            
            time.sleep(tdelay)
    except KeyboardInterrupt:
        print("")
        print("Weee - Exiting")
        s.close()
        GPIO.cleanup()  
        sys.exit(0)


def procValue(s, v, c):
    global SENSORS

    if v > SENSORS[s]['MAX']:
        SENSORS[s]['MAX'] = v
    if v < SENSORS[s]['MIN']:
        SENSORS[s]['MIN'] = v
    print(SENSORS[s])
    
    if SENSORS[s]['MAX'] == SENSORS[s]['MIN']:
        SENSORS[s]['MAX'] += 1
    if DEBUG:
        print ("v: %s" %v)
        print ("Max: %s" % SENSORS[s]['MAX'])
        print ("Min: %s" % SENSORS[s]['MIN'])

    sendval = (float(v) - SENSORS[s]['MIN']) / (SENSORS[s]['MAX'] - SENSORS[s]['MIN'])
    sendval = int(sendval * 100)

    sendstr = str(SENSORS[s]['REMOTE']) + ":" + str(sendval)

    print("Sendval: %s" % sendval)

    sense_delta = abs(v - SENSORS[s]['LAST'])
    if sense_delta > SENSORS[s]['THRES']:
        SENSORS[s]['CHANGES'] += 1
        if SENSORS[s]['CHANGES'] > 5:
            if sendstr != "":
                print ("**********************Sending this: %s " % sendstr)
                c.send(sendstr)
                sendstr = ""
    SENSORS[s]['LAST'] = v
            # Now send the changes to the server!
            



# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
    if ((adcnum > 7) or (adcnum < 0)):
        return -1
    GPIO.output(cspin, True)
    GPIO.output(clockpin, False)  # start clock low
    GPIO.output(cspin, False)     # bring CS low
 
    commandout = adcnum
    commandout |= 0x18  # start bit + single-ended bit
    commandout <<= 3    # we only need to send 5 bits here
    for i in range(5):
        if (commandout & 0x80):
            GPIO.output(mosipin, True)
        else:
            GPIO.output(mosipin, False)
        commandout <<= 1
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)
 
    adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
    for i in range(12):
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)
        adcout <<= 1
        if (GPIO.input(misopin)):
            adcout |= 0x1
 
    GPIO.output(cspin, True)
        
    adcout >>= 1       # first bit is 'null' so drop it
    return adcout



if __name__ == "__main__":
    main()
