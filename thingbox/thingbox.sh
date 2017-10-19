#!/bin/bash
### BEGIN INIT INFO
# Provides:          thingbox
# Required-Start:    $all
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:
# Short-Description: thingbox bootstrap
### END INIT INFO

script="/home/pi/pimeup/thingbox/thingbox.py"
cd /home/pi/pimeup/thingbox
sleep 10 && /usr/bin/python $script &



