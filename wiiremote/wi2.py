#!/usr/bin/python

import cwiid
import time

def main():
    connected = False
    print("Trying Connection")
    print ("Press 1+2")
    while not connected:
        try:
            wiimote = cwiid.Wiimote()
            print("Connected!")
            connected = True
        except:
            print("Trying Again, please press 1+2")
            time.sleep(1)

    wiimote.mesg_callback = callback
    wiimote.enable(cwiid.FLAG_MESG_IFC | cwiid.FLAG_CONTINUOUS | cwiid.FLAG_REPEAT_BTN)
    wiimote.rpt_mode = cwiid.RPT_NUNCHUK | cwiid.RPT_ACC | cwiid.RPT_BTN | cwiid.RPT_CLASSIC | cwiid.RPT_STATUS

    

    while True:
     # Messages will be sent to callback function
        pass

    wiimote.disable(cwiid.FLAG_MESG_IFC)

#----------------------------------------------------------------------
def callback (mesg_list, ctime):
    print("%s - %s" % (mesg_list, ctime))
#    time.sleep(0.2)
    #for (message, data) in mesg_list:
    #    print(mesg_list)
    #    time.sleep(delay)
#        if message == cwiid.MESG_ACC:
#            print data
#        elif message == cwiid.MESG_MOTIONPLUS:
#            print data
 #       elif message == cwiid.MESG_BTN:
 #           if data & cwiid.BTN_HOME:
 ##               global loop
 #               loop = False
 #           else:
 #               pass
 #   callback_active = False

#----------------------------------------------------------------------
if __name__ == "__main__": 
    main()
