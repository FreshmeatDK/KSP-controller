# -*- coding: <utf_8> -*-

import krpc
import time
import serial
import struct

import controls

conn = krpc.connect(name='Controller')
#vessel = conn.space_center.active_vessel

arduino = serial.Serial('COM4', 28800)

keys =["pitch","yaw","roll","tx","ty","tz","throttle","cbyte0","cbyte1","cbyte2","cbyte3","cbyte4"]

def main_loop():
    global conn
    global vessel
    


    i = 0
    inlenght = 12
    connected = False

    try:
        while vessel == conn.space_center.active_vessel:

            apv = float(apoapsis())
            altv= float(altitude())
          
            arduino.write(struct.pack('<ff', apv, altv))

            i = 0

            while i < 1000:
          
                if arduino.in_waiting !=inlenght:
                   i = i+1
                   #print(arduino.in_waiting)
                if arduino.in_waiting == inlenght:
                   i = 1000
                   serialin = struct.unpack('<bbbbbbbBBBBB',arduino.read(inlenght))
                   #print(serialin[0])
                   Cpacket = dict(zip(keys,serialin))
                   print(Cpacket["yaw"])
                   controls.assignments(Cpacket,vessel)
                if arduino.in_waiting > 3*inlenght:
                    arduino.flushInput
            
                


    except krpc.error.RPCError:
        print("Error")
    else:
        print("Change of vessel")



while True:
    vessel = None

    while vessel==None:

        try:
            vessel = conn.space_center.active_vessel
            refframe = vessel.orbit.body.reference_frame
            apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis')
            altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')

            print("Active vessel:"+vessel.name)
            main_loop()
        except krpc.error.RPCError:
            print("Not in proper game scene")
            time.sleep(.5)
