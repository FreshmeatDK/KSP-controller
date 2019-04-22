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

    while dPitch() > 10 or dHead() > 10 or angVel>0.1:
        angVel = la.norm(np.array( angVelVec() ))

    angVelVec.remove()
    dPitch.remove()
    dHead.remove()

    flightS = vessel.flight(vessel.surface_reference_frame)
    hSpeed = conn.add_stream(getattr, flight, 'horizontal_speed')
    pitch = conn.add_stream(getattr, flightS, 'pitch')

    ap.reference_frame = vessel.surface_velocity_reference_frame
    ap.target_direction = (0, -1, 0)
    

    while (hSpeed()) > 1 and pitch() < 80:

        print(hSpeed(), pitch())
        vessel.control.throttle = (hSpeed()+1)/20
        time.sleep(0.05)
    
        
    ap.target_direction = (-0.1, -1, 0)
    while hSpeed() > 0.3:
        print(hSpeed(), pitch())
        vessel.control.throttle = (hSpeed()+1)/20
    
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

    ap.target_pitch = 90

    while alt()>1:
        
        a = fullThrust()/mass()
        v_rate = v_vert()*v_vert()/(2*abs(a-g)*alt())

        if alt()<10:
            if v_vert() < -2:
                thr = (2-v_vert())/2
            else:
                thr = v_rate

        elif v_rate > 0.8 :
            if v_vert() < -4:
                thr = v_rate*1.2
            else:
                thr = 0
        else:
            thr = 0

        vessel.control.throttle = thr
    
    ap.disengage()
    vessel.control.throttle = 0
 

