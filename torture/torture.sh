#!/bin/bash
### BEGIN INIT INFO
# Provides:          torture
# Required-Start:    $all
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:
# Short-Description: Torture Chanmber
### END INIT INFO
DAEMON="torture"
script="/home/pi/pimeup/${DAEMON}/${DAEMON}.py"
/usr/bin/python $script &



