#!/bin/bash
### BEGIN INIT INFO
# Provides:          spencer
# Required-Start:    $all
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:
# Short-Description: Spencer Zapping
### END INIT INFO
DAEMON="spencer"
script="/home/pi/pimeup/${DAEMON}/${DAEMON}.py"
/usr/bin/python $script &



