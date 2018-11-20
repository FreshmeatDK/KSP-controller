# -*- coding: <utf_8> -*-

import krpc
import time
import serial
import struct

import controls

conn = krpc.connect(name='Controller')

arduino = serial.Serial('COM4', 28800)

keys =["pitch","yaw","roll","tx","ty","tz","throttle","cbyte0","cbyte1","cbyte2","cbyte3","cbyte4"]




def main_loop():
    
    CPacket = dict()
    
    count = 0

    inlenght = 12
    connected = False

    try:
        while vessel == conn.space_center.active_vessel:




            i = 0
            j = 0
            while i < 1000:
                
                i = i+1
                
                #if arduino.in_waiting < 3:
                   
                   #print(arduino.in_waiting)

                if arduino.in_waiting > 2:
                   print(arduino.in_waiting)
                   check = arduino.read(1)
                   #print(check[0])
                   if check[0] == 85:
                       #check2 = arduino.read(1)
                       if check[0] == 85:
                           if arduino.in_waiting <= inlenght:
                               serialin = arduino.read(inlenght)
                               datain = struct.unpack('<bbbbbbbBBBBB',serialin)
                               oldPacket = CPacket
                               CPacket = dict(zip(keys,datain))
                               print(i)
                               try:
                                  dummy = oldPacket["pitch"]
                               except KeyError:
                                   oldPacket = CPacket
                                   print("first")
                               apv = float(apoapsis())
                               t_apv = int(t_ap())
                               pev = float(periapsis())
                               t_pev = int(t_pe())
                               altv= float(altitude())
                               altsv = float(surf_alt())
                               v_surfv = float(v_surf())
                               v_orbv = float(v_orb())
                               count = count +1

                               buffer = struct.pack('<BIffIIffff', 85, count, apv, pev, t_apv, t_pev, altv, altsv, v_orbv, v_surfv)
                               arduino.write(buffer)
                               controls.assignments(CPacket, oldPacket,vessel)
                               i = 1000
                           else:
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
            orb_frame = vessel.orbit.body.non_rotating_reference_frame
            sur_frame = vessel.orbit.body.reference_frame
            
            #streams:  orbital
            apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
            t_ap = conn.add_stream(getattr, vessel.orbit, 'time_to_apoapsis')
            periapsis = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')
            t_pe = conn.add_stream(getattr, vessel.orbit, 'time_to_periapsis')

            #streams: flight
            altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
            surf_alt = conn.add_stream(getattr, vessel.flight(), 'surface_altitude')
            v_surf = conn.add_stream(getattr, vessel.flight(sur_frame), 'speed')
            v_orb = conn.add_stream(getattr, vessel.flight(orb_frame), 'speed')


            print("Active vessel:"+vessel.name)
            main_loop()
        except krpc.error.RPCError:
            print("Not in proper game scene")
            time.sleep(.5)
