# -*- coding: <utf_8> -*-

import krpc
import controls
import time
import serial
import struct
from controls import actions, camcontrol

conn = krpc.connect(name='Controller')

arduino = serial.Serial('COM16', 38400)

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
    time.sleep(1)
    updateTime = time.perf_counter()
    initTime = time.perf_counter()
    engineCheckTime = time.perf_counter()
    print('init')
    flameOut = False

    try:
      while vessel == conn.space_center.active_vessel:
          now = time.perf_counter()
          errorcode = 1          # 0 = success, 1 = unspec/timeout, 2 = overflow
          
          if (now - engineCheckTime > 1): #check for flameout every second.engines
            decoupleList = vessel.parts.in_decouple_stage(vessel.control.current_stage-1)
            engineList = vessel.parts.engines
            flameOut = False
            for Engine in engineList:
                if not (Engine.has_fuel):
                    flameOut = True
                    print('Flameout')

          if arduino.in_waiting > 0:
            inData=struct.unpack('<B',arduino.read())
            ctrlByteNum = 0
            if arduino.in_waiting > 80:
                arduino.write(0b10101010) #send wait to arduino
                print("overflow: ",arduino.in_waiting)
                conn.ui.message("Overflow", position = conn.ui.MessagePosition.top_left)
                arduino.reset_input_buffer()
            elif (now - updateTime) > 0.1:
                  updateTime = time.perf_counter()
                  conn.ui.message("Ack", position = conn.ui.MessagePosition.top_left)
                  arduino.write(0b01010101)
 
            for i in range(2):
                oldCtrl[i] = ctrl[i]

            if inData[0] == 0b10101010: #start char
          
                readOp = True
                waitloop = 1
                while readOp:
                    waitloop += 1
                    if waitloop > 1000: #timeout
                        readOp = False   #leave
                    if arduino.in_waiting > 0:
                        inData=struct.unpack('<B',arduino.read())
                    if inData[0] == 0b11001100: #EOF char
                        readOp = False
                        if (ctrlByteNum == 2 and errorcode == 1): #if we have reached two bytes
                            errorcode = 0

                    elif inData[0] == 0b00001111: #escape char
                        inData=struct.unpack('<B',arduino.read())     #read another
                        ctrl[ctrlByteNum] = inData[0]                 #and copy directly
                        ctrlByteNum += 1
                        if ctrlByteNum > 1:
                            ctrlByteNum = 1
                            errorcode = 2
                    else:                               #not esc, not EOF
                        if ctrlByteNum > 1:
                            ctrlByteNum = 1
                            errorcode = 2
                        ctrl[ctrlByteNum] = inData[0]
                        ctrlByteNum += 1


            if errorcode == 0: # we have success, run commands

                if ((ctrl[0] != oldCtrl[0]) or (ctrl[1] != oldCtrl[1]) and now-initTime > 1 ):
                    actions(ctrl,oldCtrl,vessel, mainParts)
                    camera = (ctrl[0]&0b11100000)>>5
                    camcontrol(camera, cam)

          elif (now - updateTime) > 1: #more than one second since last received comms from arduino
                  updateTime = time.perf_counter()
                  conn.ui.message("Arduino timeout", position = conn.ui.MessagePosition.top_left)
                  arduino.write(0b01010101)


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
