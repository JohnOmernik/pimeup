#!/bin/bash
### BEGIN INIT INFO
# Provides:          Childhood
# Required-Start:    $all
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:
# Short-Description: Childhood Room
### END INIT INFO
DAEMON="childhood"
script="/home/pi/pimeup/${DAEMON}/${DAEMON}.py"
/usr/bin/python $script &



