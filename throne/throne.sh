#!/bin/bash
### BEGIN INIT INFO
# Provides:          throne
# Required-Start:    $all
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:
# Short-Description: Throne
### END INIT INFO
DAEMON="throne"
# Force 3.5mm audio if Pi 3
sudo amixer cset numid=3 1
script="/home/pi/pimeup/${DAEMON}/${DAEMON}.py"
/usr/bin/python $script &



