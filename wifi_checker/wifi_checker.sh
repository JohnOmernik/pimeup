#!/bin/bash

# The IP for the server you wish to ping (8.8.8.8 is a public Google DNS server)
SERVER=8.8.8.8
LOOP_TIME=600
# Only send two pings, sending output to /dev/null
LAST_CHECK=0

while [ "1" == "1" ]; do
    CUR_TIME=$(date +%s)
    DELTA_TIME=$(( $CUR_TIME - $LAST_CHECK ))
    if [ "$DELTA_TIME" -gt "$LOOP_TIME" ]; then
        ping -c2 ${SERVER} > /dev/null
        # If the return code from ping ($?) is not 0 (meaning there was an error)
        if [ $? != 0 ]; then
            # Restart the wireless interface
            ifdown --force wlan0
            ifup wlan0
        fi
        LAST_CHECK="$CUR_TIME"
    fi
    sleep 30
done
