#!/usr/bin/python

import time
from dotstar import Adafruit_DotStar
import gevent.monkey
gevent.monkey.patch_all()
from flask import Flask, request, render_template, jsonify, make_response
from wtforms import Form, BooleanField, HiddenField, TextField, TextAreaField, widgets, SelectMultipleField, RadioField
import hashlib
import re
import random
from time import strftime


numpixels = 60 # Number of LEDs in strip
# Here's how to control the strip from any two GPIO pins:
datapin   = 23
clockpin  = 24
strip     = Adafruit_DotStar(numpixels, datapin, clockpin)

strip.begin()           # Initialize pins for output
strip.setBrightness(32) # Limit brightness to ~1/4 duty cycle

# Flask setup    
app = Flask(__name__)


class colorform(Form):
    redval = HiddenField('redval', validators=[])
    greenval = HiddenField('greenval', validators=[])
    blueval = HiddenField('blueval', validators=[])
    brightval = HiddenField('brightval', validators=[])



def Color(red, green, blue, white = 0):
    return (white << 24) | (red << 8)| (green << 16) | blue
def setAllLEDS(strip, colorlist):
    numcolors = len(colorlist)

    for x in range(numpixels):
        idx = x % numcolors
        strip.setPixelColor(x, colorlist[idx])
    strip.show()

@app.route('/', methods=['GET', 'POST'])
def index():
    global strip

#Setting color to: 0xFF0000    # Green
#Setting color to: 0xCC00CC    # Bright Teal
#Setting color to: 0x66CC00    # Orange
#Setting color to: 0x33FFFF    # Magenta 
#Setting color to: 0xFF00      # Red
#Setting color to: 0x330099    # Lightish Blue
#Setting color to: 0xFFFF00    # YEllow 
#Setting color to: 0xFF        # Bright Blue
#Setting color to: 0xFF9900    # YEllower Gren
#Setting color to: 0x33        # Dark BLue
    colors = [0xFF0000, 0xCC00CC, 0x66CC00, 0x33FFFF, 0x00FF00, 0x330099, 0xFFFF00, 0x0000FF, 0xFF9900, 0x000033]
    numcolors = len(colors)



    form = colorform(request.form)
    redval = form.redval.data

    if redval is None:
        redval = 255
        blueval = 0
        greenval = 0
        brightval = 32
    else:
        redval = int(form.redval.data)
        greenval = int(form.greenval.data)
        blueval = int(form.blueval.data)
        brightval = int(form.brightval.data)

        print("Values are: Red: %s - Green: %s - Blue: %s - Brightness: %s" % (redval, blueval, greenval, brightval))
        mycolor = Color(redval, greenval, blueval)
        print("Hex Color is: 0x%0.2X" % mycolor)
        print("Brightness is: %s" % brightval)
        strip.setBrightness(brightval)
        setAllLEDS(strip, [mycolor])
    return render_template('index.html', redval=redval, greenval=greenval, blueval=blueval, brightval=brightval)




if __name__ == '__main__':
    #app.run()
    import gevent.wsgi
    import werkzeug.serving

    @werkzeug.serving.run_with_reloader
    def runServer():
        app.debug = True

        server = gevent.wsgi.WSGIServer(('0.0.0.0', 5000), app)
        server.serve_forever()

