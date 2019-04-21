import math
import time
import numpy as np
import numpy.linalg as la

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

def autolanding(vessel,conn):
    body = vessel.orbit.body
    refFrame = body.reference_frame
    flight = vessel.flight(refFrame)

    ap = vessel.auto_pilot
    ap.engage()
    ap.reference_frame = vessel.orbital_reference_frame
    ap.target_direction = (0,-1,0)

    dPitch = conn.add_stream(getattr, ap, 'pitch_error')
    dHead = conn.add_stream(getattr, ap, 'heading_error')
    angVelVec = conn.add_stream(vessel.angular_velocity, vessel.orbital_reference_frame)
    angVel = la.norm(np.array(angVelVec()))
    angVelS=str(round(angVel,3))

    while dPitch() > 10 or dHead() > 10 or angVel>0.1:
        angVel = la.norm(np.array( angVelVec() ))

    angVelVec.remove()
    dPitch.remove()
    dHead.remove()
    ap.disengage()

    flightS = vessel.flight(vessel.surface_reference_frame)
    hSpeed = conn.add_stream(getattr, flight, 'horizontal_speed')
    pitch = conn.add_stream(getattr, flightS, 'pitch')

    while (hSpeed()) > 1 and pitch() < 87:
        vessel.control.sas = True
        vessel.control.sas_mode = vessel.control.sas_mode.retrograde
        print(hSpeed(), pitch())
        vessel.control.throttle = 1*hSpeed()/20
        time.sleep(0.05)
 
    vessel.control.sas = False
    hSpeed.remove()
    pitch.remove()
    
    alt = conn.add_stream(getattr, flight, 'surface_altitude')
    v_vert = conn.add_stream(getattr, flight, 'vertical_speed')
    fullThrust = conn.add_stream(getattr, vessel, 'available_thrust')
    mass = conn.add_stream(getattr, vessel, 'mass')
    
    g = body.surface_gravity
    gStr = str(round(g,2))
    altStr = str(round(alt(),0))

    ap.reference_frame = vessel.surface_reference_frame
    ap.engage()
    ap.target_pitch = 90

    while alt()>1:

        
        v_vertStr = str(round(v_vert(),2))

        a = fullThrust()/mass()
        aStr = str(round(a,2))
        
       
        
        altV=alt()
        altStr = str(round(alt(),0))

        printStr = "v "+ v_vertStr + " a " + aStr
        v_rate = v_vert()*v_vert()/(2*abs(a-g)*alt())

        if  v_rate > 0.8 :
            if v_vert() < -4:
                thr = v_rate*1.2
                print(thr)
                vessel.control.throttle = thr
            else:
                vessel.control.throttle = 0
        else:
            vessel.control.throttle = 0
    print("Done")
 

