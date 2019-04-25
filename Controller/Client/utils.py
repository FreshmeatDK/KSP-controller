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



def autoDescent(vessel, vInfo, ap, s):
    #assuming autopilot is engaged

    if s == 1:
        ap.reference_frame = vessel.orbital_reference_frame
        ap.target_direction = (0,-1,0)
        angVel = la.norm(np.array(vInfo['angVelVec']))
        if vInfo['dPitch'] < 10 and vInfo['dHead'] < 10 and angVel<0.1:
            s = 2

    if s == 2:
        ap.reference_frame = vessel.surface_velocity_reference_frame
        ap.target_direction = (0, -1, 0)
        if vInfo['hSpeed'] < 10:
            vessel.control.throttle = 3/vInfo['a']
        else:
            vessel.control.throttle = 1
        if vInfo['hSpeed'] < 1 or vInfo['pitch'] > 80:
            s = 3

    if s == 3:
        ap.target_direction = (-0.1, -1, 0)
        vessel.control.throttle = vInfo['g']/vInfo['a']
        if vInfo['hSpeed'] < 0.3:
            s = 4

    if s == 4:
        ap.reference_frame = vessel.surface_reference_frame
        ap.target_pitch = 90
        v_rate = vInfo['v_vert']*vInfo['v_vert']/(2*abs(vInfo['a']-vInfo['g'])*vInfo['alt'])

        if vInfo['alt']<10:
            if vInfo['v_vert'] < -2:
                thr = (2-vInfo['v_vert'])/2
            else:
                thr = v_rate

        elif v_rate > 0.8 :
            if vInfo['v_vert'] < -4:
                thr = v_rate*1.2
            else:
                thr = 0
        else:
            thr = 0
        vessel.control.throttle = thr
        #
        #print(thr, vInfo['alt'], vInfo['v_vert'])
        if vInfo['alt'] < 1:
            s = 0
            

    return s