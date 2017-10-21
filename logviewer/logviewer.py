#!/usr/bin/python3
from flask import Flask, abort, jsonify, request
import subprocess
import io
import json
import socket
import os
import sys
import time
from collections import OrderedDict

WHOAMI = socket.gethostname()
WHATAMI = os.path.basename(__file__).replace(".py", "")

logrefresh = 5
lastrefresh = 0
numlogs = 10
app = Flask(__name__)

curtime = int(time.time())
curday = time.strftime('%Y-%m-%d', time.localtime(curtime))

logdir = "/home/pi/pimeup/hauntlogs/logs/" + curday
people = {}
displaylogs = {}
stats = {}

def reloaddisplay():
    global displaylogs


    for filename in os.listdir(logdir):


        p = subprocess.Popen(['tail', '-' + str(numlogs), logdir + "/" + filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retcode = None
        output = "["
        while retcode is None:
            retcode = p.poll() #returns None while subprocess is running
            try:
                for line in io.TextIOWrapper(p.stdout, encoding="utf-8"):
                    output = output + line + ","
            except:
                break
        output = output[0:-1]
        output += "]"
        try:
            jlast = json.loads(output)
        except:
            print(output)
        displaylogs[filename.replace(".log", "")] = jlast


def gatherstats():
    global displaylogs
    global stats
    global people
    curtime = int(time.time())
    people = {}
    for x in displaylogs.keys():
        tstat = {}
        tstat["piname"] = x
        tstat["bsname"] = ""
        tstat["roomname"] = ""
        tstat["lastts"] = ""
        tstat["lastroomhb"] = ""
        tstat["lastbshb"] = ""
        tstat["wiilevel"] = 0

        for y in displaylogs[x]:
            logtime = int(time.mktime(time.strptime(y['ts'], '%Y-%m-%d %H:%M:%S')))
            if y['script'].find("bspimeup") >= 0:
                tstat["bsname"] = y['script']
                tstat["lastbshb"] = y['ts']
            else:
                tstat["roomname"] = y['script']
                tstat["lastroomhb"] = y['ts']
            tstat["lastts"] = y['ts']
            if y['event_desc'] == 'wii HB':
                tstat["wiilevel"] = y['event_data']
            if y['script'].find("bspimeup") < 0 and y['event_type'].find('heartbeat') < 0:
                if curtime - logtime < 30:
                    if x not in people:
                        people[x] = []
                    people[x].append(y)
        tstat["lastepoch"] = int(time.mktime(time.strptime(tstat['lastts'], '%Y-%m-%d %H:%M:%S')))
        tstat["tdelta"] = curtime - tstat["lastepoch"]
        if tstat["tdelta"] >= 60:
            tstat["WARNING"] = "THISROOMDELTA IS LARGER then 60"
        stats[x] = tstat


    
@app.route('/showlogs', methods=['GET'])
def showlogs():
    global logrefresh
    global lastrefresh
    global logdir
    global curday
    curtime = int(time.time())
    tday = time.strftime('%Y-%m-%d', time.localtime(curtime))
    if tday != curday:
        curday = tday
        logdir = "/home/pi/pimeup/hauntlogs/logs/" + curday


    curtime = int(time.time())
    if curtime - lastrefresh >= logrefresh:
        reloaddisplay()
        gatherstats()



    return jsonify(displaylogs), 201
@app.route('/showstats', methods=['GET'])
def showstats():
    global logrefresh
    global lastrefresh
    global logdir
    global curday
    curtime = int(time.time())
    tday = time.strftime('%Y-%m-%d', time.localtime(curtime))
    if tday != curday:
        curday = tday
        logdir = "/home/pi/pimeup/hauntlogs/logs/" + curday

    curtime = int(time.time())
    if curtime - lastrefresh >= logrefresh:
        reloaddisplay()
        gatherstats()


    out = {}
    for x in stats:
        if x not in out:
            out[x] = stats[x]
    for x in people:
        out[x]["people"] = people[x]
    
    return jsonify(out), 201


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5060, debug=True)
