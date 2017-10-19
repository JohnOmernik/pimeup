#!/bin/bash
### BEGIN INIT INFO
# Provides:          thingglove
# Required-Start:    $all
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:
# Short-Description: thingglove bootstrap
### END INIT INFO
script="/home/pi/pimeup/thingglove/thingglove.py"
/usr/bin/python $script &



