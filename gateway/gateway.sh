#!/bin/bash
### BEGIN INIT INFO
# Provides:          gateway
# Required-Start:    $all
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:
# Short-Description: GW Heartbeat
### END INIT INFO
script="/home/pi/pimeup/gateway/gateway.py"
/usr/bin/python $script &



