#!/usr/bin/python

import time
import random
import sys
import json
import socket
import requests
import os
import subprocess

from collections import OrderedDict


WHOAMI = socket.gethostname()
WHATAMI_BASE = os.path.basename(__file__).replace(".py", "")
WHATAMI = WHATAMI_BASE + " - " WHOAMI
bsurl = "http://HAUNTCONTROL:5050/bootstrap/" + WHOAMI

gitpull = "/home/pi/pimeup/bspimeup/gitpull.sh"

myroom = "init"
myscript = ""
running = False
chktime = 60
lastchktime = 0
roomprocess = None
initialgit = False
def main():
    global gitpull
    global initialgit
    global chktime
    global myroom
    global myscript
    global running
    global roomprocess
    global lastchktime
    global WHATAMI
    global WHATAMI_BASE
    global WHOAMI


    # First check if we need to git pull
    if initialgit == False:
        gitproc = subprocess.Popen([gitpull])
        gitstatus = subprocess.Popen.poll(gitproc) 
        while gitstatus is None:
            print("Running git")
            time.sleep(2)
            gitstatus = subprocess.Popen.poll(gitproc)
        logevent("initialgit", gitstatus, "The initial git returned %s" % gitstatus)
        initialgit = True
    while True:
        curtime = int(time.time())
        if cutime - lastchktime >= chktime:
            if myroom != "init":
                # Get Wii remote update
            logevent("heartbeat", myroom, "Heartbeat and conf check for %s" % myroom)
            # Get current config
            resp = requests.get(bsurl)
            curconf = resp.json
            # See if we need to update how often we check
            if chktime != curconf['chktime']:
                logevent("update_chktime", myroom, "Updating checktime from %s to %s" % (chktime, curconf['chktime'])
                chktime = curconf['chktime']
            # Is our room not set, or did our room change
            if myroom != curcon['myroom']:
                myroom = curcon['myroom']
                WHATAMI = WHATAMI_BASE + " - " + myroom
                logevent("roomset", myroom, "setting room to %s" % myroom)
                myscript = "/home/pi/pimeup/%s/%s.py" % (myroom, myroom)
            # Are we currently running
            if running == False:
                # Should we be running?
                if curconf['run'] == 1:
                    roomprocess = subprocess.Popen(['python', myscript])
                    logevent("roomstart", myroom, "Starting room %s" % myroom)
            else:
                # If we are running and our process is exited, let's fix that
                curstatus = subprocess.Popen.poll(roomprocess)
                if curstatus != None:
                # The process has exited, let's restart it by setting the loop to be False
                    logevent("roomfail", myroom, "Room %s was supposed to be running but is not gonna try again")
                    running = False
                    lastchktime = 0
                # At this point is the config asking us to be stopped?
                if curconf['run'] != 1:
                    logevent("roomstop", myroom, "Room %s is now stopping")
                    subprocess.Popen.terminate(roomprocess)
                    running = False

            # Update the last check time
            lastchktime = curtime
            time.sleep(5)

def logevent(etype, edata, edesc):
    global WHOAMI
    global WHATAMI

    curtime = int(time.time())
    curts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(curtime))
    outrec = OrderedDict()
    outrec['ts'] = curts
    outrec['host'] = WHOAMI
    outrec['script'] = WHATAMI
    outrec['event_type'] = etype
    outrec['event_data'] = edata
    outrec['event_desc'] = edesc
    sendlog(outrec, False)
    outrec = None


def sendlog(log, debug):
    logurl = "http://hauntcontrol:5050/hauntlogs"
    try:
        r = requests.post(logurl, json=log)
        if debug:
            print("Posted to %s status code %s" % (logurl, r.status_code))
            print(json.dumps(log))
    except:
        if debug:
            print("Post to %s failed timed out?" % logurl)
            print(json.dumps(log))



if __name__ == "__main__":
    main()
