#!/usr/bin/python
import time

power_brightness = "/sys/devices/platform/leds/leds/led1/brightness"


while True:
    power_brightness = "/sys/devices/platform/leds/leds/led1/brightness"
    with open(power_brightness) as read_state:
        curpwr = int(read_state.read())
    print("Cur Power: %s" % curpwr)
    time.sleep(2)
