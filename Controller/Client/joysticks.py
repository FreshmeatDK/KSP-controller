import krpc

def joystickAssignments(values,vessel):
    vessel.control.pitch = -values[0]/100
    vessel.control.yaw = values[1]/100

