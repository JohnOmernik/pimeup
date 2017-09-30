#!/bin/bash
### BEGIN INIT INFO
# Provides:          taxi
# Required-Start:    $all
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:
# Short-Description: taxi
### END INIT INFO
DAEMON="taxi"
script="/home/pi/pimeup/taxi/taxi.py"
/usr/bin/python $script &



