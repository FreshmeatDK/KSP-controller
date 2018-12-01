# -*- coding: <utf_8> -*-

import krpc
import time
import serial
import struct

conn = krpc.connect(name='Controller')

arduino = serial.Serial('COM9', 9600)

def main_loop():

    connected = False

    try:
      while vessel == conn.space_center.active_vessel:
         if arduino.in_waiting > 0:
            inData=struct.unpack('<B',arduino.read())
            ctrl=inData[0]
            #print(bin(ctrl))
            
            solar=(ctrl & 0b00001000)
            if solar:
               for Solar_Panel in vessel.parts.solar_panels:
                   Solar_Panel.deployed=True
            else:
               for Solar_Panel in vessel.parts.solar_panels:
                   Solar_Panel.deployed=False
            
            radiator =(ctrl&0b00000100)
            if radiator:
                for Radiator in vessel.parts.radiators:
                    Radiator.deployed=True
            else:
                for Radiator in vessel.parts.radiators:
                    Radiator.deployed=False

            cbay =(ctrl&0b00000010)
            if cbay:
                for Bay in vessel.parts.cargo_bays:
                    Bay.open=True
            else:
                for Bay in vessel.parts.cargo_bays:
                    Bay.open=False 

            engine =(ctrl & 0b00000001)
            if engine:
                for Engine in vessel.parts.engines:
                    try:
                        Engine.mode='AirBreathing'
                    except:
                        pass
                    try:
                        Engine.mode='Wet'
                    except:
                        pass

            else:
                for Engine in vessel.parts.engines:
                    try:
                        Engine.mode='ClosedCycle'
                    except:
                        pass
                    try:
                        Engine.mode='Dry'
                    except:
                        pass
            
            camera = (ctrl&0b11100000)>>5
            print(camera)
            if camera == 1:
                try:
                    vessel.camera.mode=CameraMode.automatic
                except:
                    pass
            if camera == 2:
                try:
                    vessel.camera.mode=CameraMode.map
                except:
                    pass

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
