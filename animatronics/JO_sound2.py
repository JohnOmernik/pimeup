#!/usr/bin/python


import pyaudio
import wave
import sys
import time
import struct
import math

SHORT_NORMALIZE = (1.0/32768.0)
CHUNK = 1024
swidth = 2 
thres = 30
mouthpos = 0.0
wf = wave.open('whizzer.wav', 'rb')

# instantiate PyAudio (1)
p = pyaudio.PyAudio()

def rms(frame):
    count = len(frame)/swidth
    format = "%dh"%(count)
    shorts = struct.unpack( format, frame )

    sum_squares = 0.0
    for sample in shorts:
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n
        rms = math.pow(sum_squares/count,0.5);
        return rms * 1000



# define callback (2)
def callback(in_data, frame_count, time_info, status):
    global mouthpos
    data = wf.readframes(frame_count)
#    print("Sig: %s" % rms(data))
#    sig = rms(data)
#    if mouthpos == 0.0:
#        if sig >= thres:
#            print("Opening Mouth")
#            mouthpos = 0.5
#    if mouthpos == 0.5:
#        if sig >= thres:
#            print("Closing Mouth")
#            mouthpos = 0.0

    return (data, pyaudio.paContinue)



# open stream using callback (3)
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                stream_callback=callback)

# start the stream (4)
stream.start_stream()

# wait for stream to finish (5)
while stream.is_active():
    time.sleep(0.5)

# stop stream (6)
stream.stop_stream()
stream.close()
wf.close()

# close PyAudio (7)
p.terminate()
