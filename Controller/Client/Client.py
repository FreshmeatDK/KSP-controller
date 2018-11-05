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
    inlenght = 8
    connected = False
    intup =[0,0,0,0,0,0,0] #struct.Struct('b b b b b b B')

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
            #print(altv)

            i = 0

            while i < 1000:
                #print(i)
                if arduino.in_waiting !=inlenght:
                    i = i+1
                    #print(arduino.in_waiting)
                if arduino.in_waiting == inlenght:
                    #print(i)
                    i = 1000
                    intup = struct.unpack('<bbbbbbbb',arduino.read(inlenght))

            
            thr = int(intup[5])
            print(intup)

            
                


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
