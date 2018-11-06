# -*- coding: <utf_8> -*-

import krpc
import time
import serial
import struct

import joysticks

conn = krpc.connect(name='Controller')
vessel = conn.space_center.active_vessel
refframe = vessel.orbit.body.reference_frame
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis')
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')

arduino = serial.Serial('COM4', 28800)

def main_loop():
    global conn
    global vessel
    


    i = 0
    inlenght = 7
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
                   print(arduino.in_waiting)
                if arduino.in_waiting == inlenght:
                   i = 1000
                   CPacket = struct.unpack('<bbbbbbb',arduino.read(inlenght))
                   joysticks.joystickAssignments(CPacket,vessel)
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
            print("Active vessel:"+vessel.name)
            main_loop()
        except krpc.error.RPCError:
            print("Not in proper game scene")
            time.sleep(.5)
