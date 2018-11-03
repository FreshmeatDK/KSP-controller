# -*- coding: <utf_8> -*-

import krpc
import time
import serial
import struct

conn = krpc.connect(name='Experiments')

arduino = serial.Serial('COM4', 9600)

def main_loop():
    global conn
    global vessel
    
    apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis')
    altitude = conn.add_stream(getattr, vessel.orbit, 'speed')

    i = 0
    connected = False

    try:
        while vessel == conn.space_center.active_vessel:
            #print(apoapsis())
            #print(altitude())
            #while not connected:
            #    serIn = arduino.read(1)
            #    connected = True
            
            apv = float(apoapsis())
            altv= float(altitude())

            arduino.write(struct.pack('<ff', apv, altv))
            #print(struct.pack('<ff', apv, altv))
            i = i+1
            
            if i > 9:
                i = 0
            arduino_ready = False
            while not arduino_ready:
                serIn = arduino.read(1)
                arduino_ready = True
            intup = struct.unpack('<B', serIn)
            thr = intup[0]/256
            if thr < 0.02:
                thr = 0
            print(thr)
            vessel.control.throttle = thr

                


    except krpc.error.RPCError:
        print("Error")
    else:
        print("Change of vessel")



while True:
    vessel = None

    while vessel==None:

        try:
            vessel = conn.space_center.active_vessel
            print("Active vessel:"+vessel.name)
            main_loop()
        except krpc.error.RPCError:
            print("Not in proper game scene")
            time.sleep(.5)
