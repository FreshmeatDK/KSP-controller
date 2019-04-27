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
    offset = 0

    if s == 1:
        vessel.control.legs = True

        ap.reference_frame = vessel.orbital_reference_frame
        ap.target_direction = (0,-1,0)
        angVel = la.norm(np.array(vInfo['angVelVec']))
        if vInfo['dPitch'] < 10 and vInfo['dHead'] < 10 and angVel<0.1:
            s = 2

    if s == 2:
        box = vessel.bounding_box(vessel.reference_frame)
        offset = box[1][2]
        s = 3

    if s == 3:
        ap.reference_frame = vessel.surface_velocity_reference_frame
        ap.target_direction = (0, -1, 0)
        if vInfo['hSpeed'] < 10:
            vessel.control.throttle = 3/vInfo['a']
        else:
            vessel.control.throttle = 1
        if vInfo['hSpeed'] < 1 or vInfo['pitch'] > 80:
            s = 4

    if s == 4:
        ap.target_direction = (-0.1, -1, 0)
        vessel.control.throttle = vInfo['g']/vInfo['a']
        if vInfo['hSpeed'] < 0.2:
            s = 5

    if s == 5:
        ap.reference_frame = vessel.surface_velocity_reference_frame
        if vInfo['v_vert'] < 0:
            ap.target_direction = (0, -1, 0)
            if ap.target_pitch > 10:
                ap.target_pitch = 10
        else:
            ap.target_direction = (0, 1, 0)

        v_rate = vInfo['v_vert']*vInfo['v_vert']/(2*abs(vInfo['a']-vInfo['g'])*vInfo['alt'])

        if vInfo['alt']<15*vInfo['g']:
            print('low')
            if vInfo['v_vert'] < -2:
                thr = (vInfo['g']-vInfo['v_vert']+1)/vInfo['a']
            else:
                thr = (vInfo['g']-1)/vInfo['a']

        elif v_rate > 0.7 and vInfo['alt'] < 1000:
            if vInfo['v_vert'] < -4:
                thr = v_rate*1.4
            else:
                thr = 0
        elif v_rate > 0.9 :
            if vInfo['v_vert'] < -4:
                thr = v_rate*1.2
            else:
                thr = 0
        else:
            thr = 0
        
        #
        #print(vInfo['sit'], vInfo['alt'])
        if vInfo['alt'] < 1+offset or vInfo['sit'] == 'VesselSituation.landed' :
            s = 0
            print('out')
            thr = 0
        for leg in vessel.parts.legs:
            if leg.is_grounded:
                print('TD')
                s=0
                thr = 0
        vessel.control.throttle = thr
    return s