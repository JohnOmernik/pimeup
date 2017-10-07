#!/usr/bin/python
from flask import Flask, abort, jsonify, request
import json
import socket
import os
import sys
import time
from collections import OrderedDict

WHOAMI = socket.gethostname()
WHATAMI = os.path.basename(__file__).replace(".py", "")

BSCONFIG = {}
bsreload = 60
chktime = 60
bslastreload = 0
bsfile = "/home/zetaadm/pimeup/hauntlogs/bootstrap.ini"
hauntini = "/home/zetaadm/pimeup/hauntlogs/haunt.ini"

app = Flask(__name__)

@app.route('/hauntlogs', methods=['POST'])
def hauntlogs():
    loadbs()
    global BSCONFIG
    logdir = "/home/pi/pimeup/hauntlogs/logs"
    if not request.json:
        abort(400)
    mylog = request.json

    if not "host" in mylog:
        myhost = "unknown"
    else:
        myhost = mylog['host']

    logfile = logdir + "/" + myhost + ".log"
    f = open(logfile, "a")
    f.write(json.dumps(mylog) + "\n")
    f.close()

    return jsonify({'status':'OK'}), 201

@app.route('/bootstrap/<node>', methods=['GET'])
def bootstrap(node):
    loadbs()
    global BSCONFIG
    global chktime
    outjson = BSCONFIG[node]
    if chktime not in outjson:
        outjson['chktime'] = chktime
    return jsonify(outjson), 200


def loadbs():
    global BSCONFIG
    global bslastreload
    global bsreload
    global bsfile
    global chktime
    curtime = int(time.time())
    if curtime - bslastreload >= bsreload: 
        print("Loading bootstrap")
        f = open(bsfile, "r")
        rawbs = f.read()
        f.close()
        BSCONFIG = json.loads(rawbs)
        bslastreload = curtime
        print("Loading Haunt INI")
        h = open(hauntini, "r")
        rawini = h.read()
        h.close()
        j = json.loads(rawini)
        bsreload = j['bsreload']
        chktime = j['chktime']
        logevent("conf_reload", "Success", "The Haunt config was reloaded")

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
    print(outrec)
#    sendlog(outrec, False)
    outrec = None

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050, debug=False)
