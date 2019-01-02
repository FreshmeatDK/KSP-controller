# -*- coding: <utf_8> -*-

import krpc
import controls
import time
import serial
import struct
from controls import actions, camcontrol

conn = krpc.connect(name='Controller')

arduino = serial.Serial('COM14', 38400)

def listMainParts(vessel):
    root = vessel.parts.root
    list = []
    stack = [root]
    while stack:
        part = stack.pop()
        list.append(part)
        for child in part.children:
            if (child.name != 'dockingPort2') and (child.name != 'ConstructionPort1'):
                stack.append(child)
    return list

def main_loop():
    ctrl = [0,0]
    oldCtrl = [0,0]
    connected = False
    ctrl[0] = 0
    ctrl[1] = 0
    mainParts = listMainParts(vessel) #some actions only in parts not connected by docking ports
    
    try:
      while vessel == conn.space_center.active_vessel:

          errorcode = 1
          # 0 = success, 1 = unspec/timeout, 2 = overflow
          if arduino.in_waiting > 0:
            inData=struct.unpack('<B',arduino.read())
            ctrlByteNum = 0
 
            for i in range(2):
                oldCtrl[i] = ctrl[i]

            if inData[0] == 0b10101010:
                readOp = True
                waitloop = 1
                while readOp:
                    waitloop += 1
                    if waitloop > 1000:
                        readOp = False
                    if arduino.in_waiting > 0:
                        inData=struct.unpack('<B',arduino.read())
                    if inData[0] == 0b11001100:
                        readOp = False
                        if (ctrlByteNum == 2 and errorcode == 1):
                            errorcode = 0

                    elif inData[0] == 0b00001111:
                        inData=struct.unpack('<B',arduino.read())
                        ctrl[ctrlByteNum] = inData[0]
                        ctrlByteNum += 1
                        if ctrlByteNum > 1:
                            ctrlByteNum = 1
                            errorcode = 2
                    else: 
                        if ctrlByteNum > 1:
                            ctrlByteNum = 1
                            errorcode = 2
                        ctrl[ctrlByteNum] = inData[0]
                        ctrlByteNum += 1


            if errorcode == 0: # we have success, run commands

                if (ctrl[0] != oldCtrl[0]) or (ctrl[1] != oldCtrl[1]):
                    actions(ctrl,oldCtrl,vessel, mainParts)
                    camera = (ctrl[0]&0b11100000)>>5
                    camcontrol(camera, cam)
                
               


    except krpc.error.RPCError:
        print("Error")
    else:
        print("Change of vessel")



while True:
    vessel = None

    while vessel==None:

        try:
            vessel = conn.space_center.active_vessel
            cam = conn.space_center.camera

            print("Active vessel:"+vessel.name)
            main_loop()
        except krpc.error.RPCError:
            print("Not in proper game scene")
            time.sleep(.5)
