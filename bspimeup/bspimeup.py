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
WHATAMI = WHATAMI_BASE + " - " + WHOAMI
bsurl = "http://HAUNTCONTROL:5050/bootstrap/" + WHOAMI


gitpull = "/home/pi/pimeup/bspimeup/gitpull.sh"

btstatus = -1
myroom = "init"
myscript = ""
running = False
chktime = 60
lastchktime = 0
roomprocess = None
def main():
    global btstatus
    global gitpull
    global chktime
    global myroom
    global myscript
    global running
    global roomprocess
    global lastchktime
    global WHATAMI
    global WHATAMI_BASE
    global WHOAMI

    # Initial Startup sleep to ensure domain resolution is working - This could be changed to a check of DNS rather than a race condition
    time.sleep(10)
    curconf = None
    oldconf = None
    # First run git pull
    runcmd([gitpull])
    while True:
        curtime = int(time.time())
        if curtime - lastchktime >= chktime:
            if myroom != "init":
                # Get Wii remote update
                logevent("bspimeup", myroom, "Heartbeat and conf check for %s" % myroom)
            # Get current config
            oldconf = curconf
            try:
                resp = requests.get(bsurl)
                curconf = json.loads(resp.text)
                print(curconf)
            except:
                logevent("bspimeup", myroom, "Failed to get pimeup config")
                curconf = oldconf

            # Now that we have the config, we are going to check all the various things to update            
            if curconf != None:
            # Example Record: "VADERPI3": {"room": "vault", "gitpull": 0, "reboot": 0, "shutdown": 0, "run": 1, "btstatus": 1, "chktime": 60},
            # See if we need to update the Bluetooth status
                try:
                    newbt = curconf['btstatus']
                except:
                    newbt = -1
                if newbt != btstatus:
                    updatebt(newbt)
                    btstatus = newbt                    
            # See if we need to update how often we check
                if chktime != curconf['chktime']:
                    logevent("update_chktime", myroom, "Updating checktime from %s to %s" % (chktime, curconf['chktime']))
                    chktime = curconf['chktime']
            # Is our room not set, or did our room change
                if myroom != curconf['room']:
                    myroom = curconf['room']
                    WHATAMI = WHATAMI_BASE + " - " + myroom
                    logevent("roomset", myroom, "setting room to %s" % myroom)
                    myscript = "/home/pi/pimeup/%s/%s.py" % (myroom, myroom)
            # Do you want me to update code from Git
                if curconf['gitpull'] == 1:
                    runcmd([gitpull])
            # Do you want to reboot?
                if curconf['reboot'] == 1:
                    if running == True:
                        # Let's stop our room before the reboot
                        logevent("roomstop", myroom, "Room %s is now stopping")
                        subprocess.Popen.terminate(roomprocess)
                        running = False
                    reboot()
                if curconf['shutdown'] == 1:
                    if running == True:
                        # Let's stop our room before the shutdown
                        logevent("roomstop", myroom, "Room %s is now stopping")
                        subprocess.Popen.terminate(roomprocess)
                        running = False
                    shutdown()
                if curconf['fsck'] == 1:
                    if running == True:
                        # Let's stop our room before the shutdown
                        logevent("roomstop", myroom, "Room %s is now stopping")
                        subprocess.Popen.terminate(roomprocess)
                        running = False
                    fsckreboot()
            # Are we currently running
                if running == False:
                # Should we be running?
                    if curconf['run'] == 1:
                        print("Running: %s" % myscript)
                        roomprocess = subprocess.Popen(['python', myscript])
                        logevent("roomstart", myroom, "Starting room %s" % myroom)
                        running = True
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

def fsckreboot():
    logevent("shutdown", "fsckreboot", "Shutting down with -rF (halt and run fsck) being issued now")
    runcmd(['sudo', 'shutdown', '-rF', 'now'])


def shutdown():
    # Logging now because the run command won't actually return
    logevent("shutdown", "halt", "Shutting down with -h (halt) being issued now")
    runcmd(['sudo', 'shutdown', '-h', 'now'])


def reboot():
    # Logging now because the run command won't actually return
    logevent("shutdown", "reboot", "Shutting down with -r (reboot) being issued now")
    runcmd(['sudo', 'shutdown', '-r', 'now'])
    

def runcmd(cmd):
    runprocess = subprocess.Popen(cmd)
    runstatus = subprocess.Popen.poll(runprocess)
    runcount = 0 
    while runstatus == None and runcount <= 10:
        time.sleep(2)
        runcount += 1
        runstatus = subprocess.Popen.poll(runprocess)
    if runstatus is None:
        runstatus = "Timedout"
    logevent("cmd", " ".join(cmd), "Command result: %s" % runstatus)

def updatebt(newbt):
    if newbt == 0:
        btstr = "block"
    elif newbt == 1:
        btstr = "unblock"
    mycmd = ['sudo', 'rfkill', btstr, 'bluetooth']
    runcmd(mycmd)


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
