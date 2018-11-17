import krpc

def joystickAssignments(values,vessel):
    vessel.control.pitch = -values["pitch"]/100
    vessel.control.yaw = values["yaw"]/100


def SASAssignement(cbyte,vessel):
    sasMode=((cbyte)& (0b00001111))
    
    if sasMode == 0b1011:
        try:
           vessel.control.sas_mode = vessel.control.sas_mode.target
        except krpc.client.RPCError:
           print('Could not set SAS Mode - target')
           pass
    elif sasMode == 0b1010:
        try:
           vessel.control.sas_mode = vessel.control.sas_mode.radial
        except krpc.client.RPCError:
           print('Could not set SAS Mode - radial')
           pass
    elif sasMode == 0b1001:
        try:
           vessel.control.sas_mode = vessel.control.sas_mode.normal
        except krpc.client.RPCError:
           print('Could not set SAS Mode - normal')
           pass
    elif sasMode == 0b1000:
        try:
           vessel.control.sas_mode = vessel.control.sas_mode.prograde
        except krpc.client.RPCError:
           print('Could not set SAS Mode - normal')
           pass
    elif sasMode == 0b0111:
        try:
           vessel.control.sas_mode = vessel.control.sas_mode.stability_assist
        except krpc.client.RPCError:
           print('Could not set SAS Mode - stability assist')
           pass
    elif sasMode == 0b0110:
        try:
           vessel.control.sas_mode = vessel.control.sas_mode.maneuver
        except krpc.client.RPCError:
           print('Could not set SAS Mode - Maneuver')
           pass
    elif sasMode == 0b1110:
        try:
           vessel.control.sas_mode = vessel.control.sas_mode.retrograde
        except krpc.client.RPCError:
           print('Could not set SAS Mode - Retrograde')
           pass
    elif sasMode == 0b1101:
        try:
           vessel.control.sas_mode = vessel.control.sas_mode.anti_normal
        except krpc.client.RPCError:
           print('Could not set SAS Mode - Anti normal')
           pass
    elif sasMode == 0b1100:
        try:
           vessel.control.sas_mode = vessel.control.sas_mode.anti_radial
        except krpc.client.RPCError:
           print('Could not set SAS Mode - Anti radial')
           pass
    elif sasMode == 0b1110:
        try:
           vessel.control.sas_mode = vessel.control.sas_mode.anti_target
        except krpc.client.RPCError:
           print('Could not set SAS Mode - Anti target')
           pass
    else: 
        print("SAS malformed parameter")

def toggles(values,vessel):
    print((values["cbyte1"] & 0b01000000))
    vessel.control.sas = bool((values["cbyte1"] & 0b01000000))
    if bool((values["cbyte1"] & 0b01000000)):
        SASAssignement(values["cbyte1"],vessel)

def assignments(values,vessel):
    joystickAssignments(values,vessel)
    toggles(values,vessel)