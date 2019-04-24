# -*- coding: <utf_8> -*-

import krpc
import status
import controls
import time
import serial
import struct
import utils
import serialcomms
from serialcomms import serialReceive
from utils import autolanding, listMainParts, autolander_new
from controls import actions, camcontrol
from status import getStatus, getSOIbodynum

running = True
conn = None
arduino = None



def main_loop():
    
    
    #cam.mode=cam.mode.automatic

    #----------------dict to hold vesseldata from streams
    vInfo = {}
    #----------------streams

    body = vessel.orbit.body
    refFrame = body.reference_frame
    flight = vessel.flight(refFrame)
    flightS = vessel.flight(vessel.surface_reference_frame)

    ap = vessel.auto_pilot

    dPitch = conn.add_stream(getattr, ap, 'pitch_error')
    dHead = conn.add_stream(getattr, ap, 'heading_error')
    angVelVec = conn.add_stream(vessel.angular_velocity, vessel.orbital_reference_frame)
    hSpeed = conn.add_stream(getattr, flight, 'horizontal_speed')
    pitch = conn.add_stream(getattr, flightS, 'pitch')
    alt = conn.add_stream(getattr, flight, 'surface_altitude')
    v_vert = conn.add_stream(getattr, flight, 'vertical_speed')
    mass = conn.add_stream(getattr, vessel, 'mass')
    maxThrust = conn.add_stream(getattr, vessel, 'available_thrust')
    sigContact = conn.add_stream(getattr, vessel.comms, 'can_communicate')
    sigStr = conn.add_stream(getattr, vessel.comms, 'signal_strength')
    g = conn.add_stream(getattr, body, 'surface_gravity')
                             


    #----------------Vars
    ctrl = [0,0,1]
    oldCtrl = [0,0,1]
    connected = False

    mainParts = listMainParts(vessel) #some actions only in parts not connected by docking ports
    
    updateTime = time.perf_counter()
    sendDataTime = updateTime
    initTime = time.perf_counter()
    engineCheckTime = time.perf_counter()
    
    flameOut = False
    autolanderStage = 0
    time.sleep(2)
    #cam = conn.space_center.camera
    overflow = 1                # Serial overflow from arduino
    
    try:
      while vessel == conn.space_center.active_vessel:
          now = time.perf_counter()

          try:
              vInfo['dPitch'] = dPitch()
          except:
              vInfo['dPitch'] = 0
          try:
              vInfo['dHead'] = dHead()
          except:
              vInfo['dHead'] = 0
          vInfo['angVelVec']  =angVelVec()
          vInfo['hSpeed'] = hSpeed()
          vInfo['pitch'] = pitch()
          vInfo['alt'] = alt()
          vInfo['v_vert'] = v_vert()
          vInfo['mass'] = mass()
          vInfo['mxThr'] = maxThrust()
          vInfo['sig'] = sigContact()
          vInfo['sigStr'] = sigStr()
          vInfo['g'] = g()
          if vInfo['mass'] != 0:
            vInfo['a'] = int(vInfo['mxThr']/vInfo['mass']*100) #acceleration in cm/s

                    
          if (now - engineCheckTime > 1): #check for flameout every second.engines
            engineCheckTime = now
            engineList = vessel.parts.engines
            flameOut = False
            for Engine in engineList:
                if not (Engine.has_fuel):
                    flameOut = True
                    print('Flameout')

          for i in range(3):
            oldCtrl[i] = ctrl[i]      
          
          if arduino.in_waiting > 0:
              if (now - updateTime) > 0.025 or overflow == 1:
                  ctrl = serialReceive(arduino, conn)
                  updateTime = time.perf_counter()

          if (ctrl[2]& 0b00000111) == 0: # we have success, run commands

                if ((ctrl[0] != oldCtrl[0]) or (ctrl[1] != oldCtrl[1]) and now-initTime > 1 ): #now - inittime: delay after connection to ensure KSP ready
                    actions(ctrl,oldCtrl,vessel, mainParts,conn)
                    

                    #camera = (ctrl[0]&0b11100000)>>5
                    #camcontrol(camera, cam)

          else:
            for i in range(3): # reset ctrl
                ctrl[i] = oldCtrl[i]
            if (now - updateTime) > 1: #more than one second since last received comms from arduino
                updateTime = time.perf_counter()
                conn.ui.message("Arduino timeout", position = conn.ui.MessagePosition.top_left)
                #arduino.write(0b01010101)
          
          overflow = (ctrl[2] & 0b10000000) >> 7
          
          if ((ctrl[1] & 0b00010000) == 0b10000): # Execute autolander routine
              #print("debug")
              if autolanderStage == 0:
                  autolanderStage = 1
          
          if autolanderStage > 0:
              ap.engage()
              autolanderStage =autolander_new(vessel, vInfo, ap, autolanderStage)
          else:
              ap.disengage()


          if (now - sendDataTime) > 0.4: #send data to arduino

              status= getStatus(vInfo) # Compute status bytes from streams
              status[2]=getSOIbodynum(vessel)

              sendDataTime = time.perf_counter()
              status[1]=(status[1] | int(flameOut))
              status[1]=(status[1] | int(overflow) << 1 )
              buff = struct.pack('<BhBBB',85,status[0],status[1],status[2],170)
              arduino.write(buff)
              
              

    except krpc.error.RPCError:
        print("Error")
    else:
        print("Change of vessel")


#-------------------------------Init sequence---------------------------------------------------------------

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


#--------------------------------Main loop---------------------------------------------------------------

while running == True:
    vessel = None

    while vessel==None:
        time.sleep(.5)
        try:
            vessel = conn.space_center.active_vessel
            

            print("Active vessel:"+vessel.name)
            main_loop()
        except krpc.error.RPCError:
            print("Not in proper game scene")
            time.sleep(.5)
