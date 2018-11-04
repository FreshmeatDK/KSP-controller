# -*- coding: <utf_8> -*-

import krpc
import time
import serial
import struct

conn = krpc.connect(name='Experiments')

arduino = serial.Serial('COM4', 28800)

def main_loop():
    global conn
    global vessel
    
    apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis')
    altitude = conn.add_stream(getattr, vessel.orbit, 'speed')

    i = 0
    inlenght = 7
    connected = False
    intup = struct.Struct('b b b b b b B')

    try:
        while vessel == conn.space_center.active_vessel:
            #print(apoapsis())

            #while not connected:
            #    serIn = arduino.read(1)
            #    connected = True
            
            apv = float(apoapsis())
            altv= float(altitude())
          
            arduino.write(struct.pack('<ff', apv, altv))
            #print(struct.pack('<ff', apv, altv))
            print(altv)

            while arduino.in_waiting !=inlenght:
                pass
            
            intup = struct.unpack('<bbbbbbB',arduino.read(inlenght))

            
                


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
