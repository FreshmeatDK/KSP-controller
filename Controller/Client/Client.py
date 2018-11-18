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
    
    CPacket = dict()
    
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
          
                if arduino.in_waiting < 3:
                   i = i+1
                   #print(arduino.in_waiting)
                if arduino.in_waiting > 2:
                   check = arduino.read(1)
                   #print(check[0])
                   if check[0] == 85:
                       check2 = arduino.read(1)
                       if check2[0] == 85:
                           if arduino.in_waiting == inlenght:
                               serialin = arduino.read(inlenght)
                               datain = struct.unpack('<bbbbbbbBBBBB',serialin)
                               oldPacket = CPacket
                               CPacket = dict(zip(keys,datain))
                               try:
                                  dummy = oldPacket["pitch"]
                               except KeyError:
                                   oldPacket = CPacket
                                   print("first")
                               controls.assignments(CPacket, oldPacket,vessel)
                               i = 1000
                
            
                


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
