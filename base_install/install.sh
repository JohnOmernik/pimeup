#!/bin/bash

sudo apt-get update && sudo apt-get upgrade -y

sudo apt-get install -y python-dev rfkill build-essential python3 python3-pip libcwiid1 python3-dev python-smbus python-alsaaudio python-cwiid python-gevent

sudo pip3 install wtforms gevent rpi.gpio && pip install rpi.gpio wtforms



echo "Undisabling Bluetooth"
sudo rfkill unblock bluetooth

# Dotstar LEDs
git clone https://github.com/adafruit/Adafruit_DotStar_Pi && cd Adafruit_DotStar_Pi && sudo python setup.py install && cd ..

# Adafruit GPIO Library
git clone https://github.com/adafruit/Adafruit_Python_GPIO.git && cd Adafruit_Python_GPIO && sudo python setup.py install && cd ..

# Adafruit PWM Servo Library
git clone https://github.com/adafruit/Adafruit_Python_PCA9685.git && cd Adafruit_Python_PCA9685 && sudo python setup.py install && cd ..


# Adafruit Motor Hat
git clone https://github.com/adafruit/Adafruit-Motor-HAT-Python-Library && cd Adafruit-Motor-HAT-Python-Library && sudo python setup.py install && cd ..


echo "Updating sound driver to prefer USB audio"
sudo tee /etc/asound.conf << EOF
pcm.!default  {
 type hw card 1
}
ctl.!default {
 type hw card 1
}
EOF
