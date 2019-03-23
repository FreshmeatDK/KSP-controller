# -*- coding: <utf_8> -*-

import krpc
import controls
import time
import serial
import struct
from controls import actions, camcontrol
from status import getStatus, getSOIbodynum

running = True
conn = None
arduino = None
while conn is None or arduino is None:
	#We do not know if the server is online, so we want python to try to connect.
	try: 
		#The next line starts the connection with the server. It describes itself to the game as controller.
		conn = krpc.connect(name='Controller')
		#Now let's connect to the Arduino
		arduino = serial.Serial('COM16', 38400)
	except ConnectionRefusedError: #error raised whe failing to connect to the server.
		print("Server offline")
		time.sleep(5) #sleep 5 seconds
		conn = None
		arduino = None
	except serial.SerialException: #error raised when failling to connect to an arduino
		#TIPP: check if the Arduino serial monitor is off! or any other program using the arduino
		print("Arduino Connection Error.")	
		time.sleep(5)
		conn = None
		arduino = None


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
    
    #cam.mode=cam.mode.automatic

    #----------------dict to hold vesseldata from streams
    vInfo = {}
    #----------------streams

    mass = conn.add_stream(getattr, vessel, 'mass')
    maxThrust = conn.add_stream(getattr, vessel, 'max_thrust')
    sigContact = conn.add_stream(getattr, vessel.comms, 'can_communicate')
    sigStr = conn.add_stream(getattr, vessel.comms, 'signal_strength')

    

    #----------------Vars
    ctrl = [0,0]
    oldCtrl = [0,0]
    connected = False
    ctrl[0] = 0
    ctrl[1] = 0

    mainParts = listMainParts(vessel) #some actions only in parts not connected by docking ports
    
    updateTime = time.perf_counter()
    sendDataTime = updateTime
    initTime = time.perf_counter()
    engineCheckTime = time.perf_counter()
    
    flameOut = False
    time.sleep(2)
    cam = conn.space_center.camera
    
    try:
      while vessel == conn.space_center.active_vessel:
          

          now = time.perf_counter()
          DataErrorcode = 1          # 0 = success, 1 = unspec/timeout, 2 = bad data
          overflow = False

          if (now - engineCheckTime > 1): #check for flameout every second.engines
            engineCheckTime = now
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
                #arduino.write(0b10101010) #send wait to arduino
                print("overflow: ",arduino.in_waiting)
                conn.ui.message("Overflow", position = conn.ui.MessagePosition.top_left)
                arduino.reset_input_buffer()
                overflow = True
            elif (now - updateTime) > 0.1:
                  updateTime = time.perf_counter()
                  conn.ui.message("Ack", position = conn.ui.MessagePosition.top_left)
                  #arduino.write(0b01010101)
               
 
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
                        if (ctrlByteNum == 2 and DataErrorcode == 1): #if we have reached two bytes
                            DataErrorcode = 0

                    elif inData[0] == 0b00001111: #escape char
                        inData=struct.unpack('<B',arduino.read())     #read another
                        ctrl[ctrlByteNum] = inData[0]                 #and copy directly
                        ctrlByteNum += 1
                        if ctrlByteNum > 1:
                            ctrlByteNum = 1
                            DataErrorcode = 2
                    else:                               #not esc, not EOF
                        if ctrlByteNum > 1:
                            ctrlByteNum = 1
                            DataErrorcode = 2
                        ctrl[ctrlByteNum] = inData[0]
                        ctrlByteNum += 1


            if DataErrorcode == 0: # we have success, run commands

                if ((ctrl[0] != oldCtrl[0]) or (ctrl[1] != oldCtrl[1]) and now-initTime > 1 ):
                    actions(ctrl,oldCtrl,vessel, mainParts)
                    camera = (ctrl[0]&0b11100000)>>5
                    camcontrol(camera, cam)
                    #initTime = time.perf_counter()

          elif (now - updateTime) > 1: #more than one second since last received comms from arduino
                  updateTime = time.perf_counter()
                  conn.ui.message("Arduino timeout", position = conn.ui.MessagePosition.top_left)
                  #arduino.write(0b01010101)

          if (now - sendDataTime) > 0.4: #send data to arduino
              vInfo['mass']=mass()              # Get info to compute status
              vInfo['mxThr']=maxThrust()
              vInfo['sig']=sigContact()
              vInfo['sigStr']=sigStr()

              status= getStatus(vInfo)
              status[2]=getSOIbodynum(vessel)

              sendDataTime = time.perf_counter()
              status[1]=(status[1] | int(flameOut))
              status[1]=(status[1] | int(overflow) << 1 )
              status[2] = getSOIbodynum(vessel)
              
              print(vInfo['sigStr'])
              print(status)

              buff = struct.pack('<BhBBB',85,status[0],status[1],status[2],170)
              print(buff)
              
              arduino.write(buff)
              
              

    except krpc.error.RPCError:
        print("Error")
    else:
        print("Change of vessel")



while running == True:
    vessel = None

    while vessel==None:

        try:
            vessel = conn.space_center.active_vessel
            

            print("Active vessel:"+vessel.name)
            main_loop()
        except krpc.error.RPCError:
            print("Not in proper game scene")
            time.sleep(.5)
