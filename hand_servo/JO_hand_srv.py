#!/usr/bin/python
import Adafruit_PCA9685
import time
import random
import sys
import socket
from socket import error as socket_error

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685(0x40)
pwm.set_pwm_freq(60)

SRV_OPTIONS = []
SERVOS = {}



SERVOS['0'] = {"DESC":"Jaw Movement", "RANGE_MIN": 300, "RANGE_MAX": 500}
SERVOS['1'] = {"DESC":"Eye Movement", "RANGE_MIN": 400, "RANGE_MAX": 600}
SERVOS['2'] = {"DESC":"Eye Blink", "RANGE_MIN": 300, "RANGE_MAX": 500}
SERVOS['3'] = {"DESC":"Thumb", "RANGE_MIN": 275, "RANGE_MAX": 575, "INVERT": False}}
SERVOS['4'] = {"DESC":"Pointer", "RANGE_MIN": 300, "RANGE_MAX": 575, "INVERT":True}
SERVOS['5'] = {"DESC":"Middle", "RANGE_MIN": 325, "RANGE_MAX": 600, "INVERT": True}
SERVOS['6'] = {"DESC":"Ring", "RANGE_MIN":  275, "RANGE_MAX": 550, "INVERT": True}
SERVOS['7'] = {"DESC":"Pinky", "RANGE_MIN": 300, "RANGE_MAX": 575, "INVERT": True}



def main():

    TCP_IP = '192.168.0.122'
    TCP_PORT = 30000
    BUFFER_SIZE = 10  # Normally 1024, but we want fast response
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)
    # This Blocks!
    conn, addr = s.accept()
    straddr = str(addr[0]) + ":" + str(addr[1])
    print("Connection address: %s" % straddr)
    try:
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data: 
                continue
            else:
                tdata = data.split(":")
                if len(tdata) != 2:
                    print("Ignoring Bad Data: %s" % data)
                    continue
                else:
                    SRV_NUM = tdata[0]
                    SRV_VAL = int(tdata[1])
                    if SERVOS[SRV_NUM]["INVERT"] == True:
                        SRV_VAL = abs(SRV_VAL - 100)
                    print("Recieved Data Update: %s" % data)
                    setval = (SRV_VAL * (SERVOS[SRV_NUM]['RANGE_MAX'] - SERVOS[SRV_NUM]['RANGE_MIN']) / 100) + SERVOS[SRV_NUM]['RANGE_MIN']
                    print("Setting Servo: %s (%s) to %s" % (tdata[0], SERVOS[tdata[0]]['DESC'], setval))
                    pwm.set_pwm(int(tdata[0]), 0, setval)
    except socket_error:
        exitGracefully()
    except KeyboardInterrupt:
        exitGracefully()


def exitGracefully():
    print("")
    print("ok Bye")
    pwm.set_pwm(0, 4096, 0)
    pwm.set_pwm(1, 4096, 0)
    pwm.set_pwm(2, 4096, 0)
    pwm.set_pwm(3, 4096, 0)
    pwm.set_pwm(4, 4096, 0)
    pwm.set_pwm(5, 4096, 0)
    pwm.set_pwm(6, 4096, 0)
    pwm.set_pwm(7, 4096, 0)
    sys.exit(0)

if __name__ == "__main__":
    main()
