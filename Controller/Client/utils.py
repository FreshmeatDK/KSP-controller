import math

def autolanding(vessel):
    #vessel.auto_pilot.engage()
    vessel.control.sas = True
    vessel.control.sas_mode = vessel.control.sas_mode.retrograde

    body = vessel.orbit.body
    refFrame = body.reference_frame

    

    while (vessel.flight(refFrame).horizontal_speed) > 1 and vessel.flight().pitch < 80:
        
        print(vessel.flight(refFrame).horizontal_speed)
        vessel.control.throttle = 1*vessel.flight(refFrame).horizontal_speed/100

    while True:
        v_vert = vessel.flight(refFrame).vertical_speed
        fullThrust = vessel.available_thrust
        mass = vessel.mass
        a = fullThrust/mass
        g = body.surface_gravity
        alt = vessel.flight().surface_altitude
        print(v_vert, alt, a, sep = ', ')

        vessel.auto_pilot.engage()
        vessel.auto_pilot.target_pitch_and_heading(90, 0)
        dV_vert =v_vert+math.sqrt(2*g*alt)
        if dV_vert*dV_vert > 1.5*abs(a):
            if v_vert < -7:
                thr = -a/g*0.5*(v_vert+7)
                print(thr)
                vessel.control.throttle = thr
            else:
                vessel.control.throttle = 0