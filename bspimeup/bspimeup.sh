#!/bin/bash
### BEGIN INIT INFO
# Provides:          bspimeup
# Required-Start:    $all
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:
# Short-Description: Pimeup bootstrap
### END INIT INFO
script="/home/pi/pimeup/bspimeup/bspimeup.py"
/usr/bin/python $script &



