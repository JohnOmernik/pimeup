#!/usr/bin/python
from flask import Flask, abort, jsonify, request
import json

app = Flask(__name__)

@app.route('/hauntlogs', methods=['POST'])
def hauntlogs():
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


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050, debug=True)
