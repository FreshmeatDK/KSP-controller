import krpc

def joystickAssignments(values,vessel):
    vessel.control.pitch = -values["pitch"]/100
    vessel.control.yaw = values["yaw"]/100


def SASAssignement(cbyte,vessel):
    sasMode=((cbyte)& (0b00001111))
    
    if sasMode == 0b1011:
        vessel.control.sas_mode = vessel.control.sas_mode.target
    elif sasMode == 0b1010:
        vessel.control.sas_mode = vessel.control.sas_mode.radial
    elif sasMode == 0b1001:
        vessel.control.sas_mode = vessel.control.sas_mode.normal
    elif sasMode == 0b1000:
        vessel.control.sas_mode = vessel.control.sas_mode.prograde
    elif sasMode == 0b0111:
        vessel.control.sas_mode = vessel.control.sas_mode.stability_assist
    elif sasMode == 0b0110:
        vessel.control.sas_mode = vessel.control.sas_mode.maneuver
    elif sasMode == 0b1110:
        vessel.control.sas_mode = vessel.control.sas_mode.retrograde
    elif sasMode == 0b1101:
        vessel.control.sas_mode = vessel.control.sas_mode.anti_normal
    elif sasMode == 0b1100:
        vessel.control.sas_mode = vessel.control.sas_mode.anti_radial
    elif sasMode == 0b1110:
        vessel.control.sas_mode = vessel.control.sas_mode.anti_target
    else: 
        print("SAS malformed parameter")

def toggles(values,vessel):
    print((values["cbyte1"] & 0b01000000))
    vessel.control.sas = bool((values["cbyte1"] & 0b01000000))
    if bool((values["cbyte1"] & 0b01000000)):
        SASAssignement(values["cbyte1"],vessel)

def assignments(values,vessel):
    joystickAssignments(values,vessel)
    print(bin(values["cbyte1"]))
    
    toggles(values,vessel)