import krpc
import utils
from utils import autolanding


def actions(ctrl, oldCtrl, vessel, partlist, conn):
    if ((ctrl[0] & 0b00001000) != (oldCtrl[0] & 0b00001000)): # Solar panels
        solar=(ctrl[0] & 0b00001000)
        if solar:
            for part in partlist:
                if part.solar_panel != None:
                    Panel = part.solar_panel
                    try:
                        Panel.deployed = True
                    except:
                        pass
        else:
            for part in partlist:
                if part.solar_panel != None:
                    Panel = part.solar_panel
                    try:
                        Panel.deployed = False
                    except:
                        pass

            
    if ((ctrl[0] & 0b00000100) !=(oldCtrl[0] & 0b00000100)): # Radiators
        radiator =(ctrl[0] & 0b00000100)
        if radiator:
             for part in partlist:
                if part.radiator != None:
                    Radiator = part.radiator
                    try:
                        Radiator.deployed = True
                    except:
                        pass
        else:
            for part in partlist:
                if part.radiator != None:
                    Radiator = part.radiator
                    try:
                        Radiator.deployed = False
                    except:
                        pass

    if ((ctrl[0] & 0b00000010) != (oldCtrl[0] & 0b00000010)): # Cargo Bays
        cbay =(ctrl[0] & 0b00000010)

        if cbay:
            for part in partlist:
                if part.cargo_bay != None:
                    Bay = part.cargo_bay
                    try:
                        Bay.open = True
                    except:
                        pass
        else:
            for part in partlist:
                if part.cargo_bay != None:
                    Bay = part.cargo_bay
                    try:
                        Bay.open = False
                    except:
                        pass

    if ((ctrl[0] & 0b00010000) != (oldCtrl[0] & 0b00010000)): # Reaction Wheels
        rwheels=(ctrl[0] & 0b00010000)
        if rwheels:
            for ReactionWheel in vessel.parts.reaction_wheels:
                ReactionWheel.active = True
        else:
            for ReactionWheel in vessel.parts.reaction_wheels:
                ReactionWheel.active = False

    if ((ctrl[0] & 0b00000001) != (oldCtrl[0] & 0b00000001)): # Activate reserve battery
         state = bool((ctrl[0] & 0b00000001))
         batCapacity = vessel.resources.max('ElectricCharge')
         for respart in vessel.parts.all:
            for bat in respart.resources.with_resource('ElectricCharge'):
                if ((bat.max*20 < batCapacity) or (bat.amount < 20)) and bat.amount < 1001:
                    bat.enabled = not(bool(ctrl[0] & 0b00000001))


    if ((ctrl[1] & 0b00000001) !=(oldCtrl[1] & 0b00000001)): # Switch engine mode
        engine =(ctrl[1] & 0b00000001)
        print('diff')
        if engine:
            print('yes')
            for Engine in vessel.parts.engines:
                try:
                    Engine.mode='AirBreathing'
                except:
                    pass
                try:
                    Engine.mode='Wet'
                except:
                    pass

        else:
            print('no')
            for Engine in vessel.parts.engines:
                try:
                    Engine.mode='ClosedCycle'
                except:
                    pass
                try:
                    Engine.mode='Dry'
                except:
                    pass

    if ((ctrl[1] & 0b00000010) !=(oldCtrl[1] & 0b00000010) and (ctrl[1] & 0b00000010)): # Deploy parachutes
        for Parachute in vessel.parts.parachutes:
            Parachute.deploy()

    if ((ctrl[1] & 0b00000100) !=(oldCtrl[1] & 0b00000100) and (ctrl[1] & 0b00000100)): # Run repeatable science experiments
        DoneExperimentList = []
        for Experiment in vessel.parts.experiments:
            if (Experiment.has_data == False) and (Experiment.rerunnable == True) and (Experiment.available == True) and (Experiment.inoperable == False):
                ExpPart = Experiment.part
                if ExpPart.name not in DoneExperimentList: # Make sure only one of each type is run
                    try:
                        Experiment.run()
                        DoneExperimentList.append(ExpPart.name)
                    except:
                        pass
     
    if ((ctrl[1] & 0b00001000) !=(oldCtrl[1] & 0b00001000) and (ctrl[1] & 0b00001000)): # Run all science experiments
        DoneExperimentList = []
        for Experiment in vessel.parts.experiments:
            if (Experiment.has_data == False) and (Experiment.available == True) and (Experiment.inoperable == False):
                ExpPart = Experiment.part
                if ExpPart.name not in DoneExperimentList:
                    try:
                        Experiment.run()
                        DoneExperimentList.append(ExpPart.name)
                    except:
                        pass

    if ((ctrl[1] & 0b00010000) == True): # Execute autolander routine
          vessel.control.input_mode=vessel.control.input_mode.override
          autolanding(vessel, conn)
          vessel.control.input_mode=vessel.control.input_mode.additive

def camcontrol(camera, cam):
     if camera == 1:
        if cam.mode != cam.mode.automatic:
            try:
                cam.mode=cam.mode.automatic
                    
            except:
                pass
     elif camera == 2:
        if cam.mode != cam.mode.map:
            try:
                cam.mode=cam.mode.map
                    
            except:
                cam.mode=cam.mode.automatic
     elif camera == 3:
            if cam.mode != cam.mode.iva:
                try:
                    cam.mode=cam.mode.iva
                    
                except:
                    cam.mode=cam.mode.automatic
     elif camera == 4:
        if cam.mode != cam.mode.free:
            try:
                cam.mode=cam.mode.free
                    
            except:
                cam.mode=cam.mode.automatic
     elif camera == 5:
        if cam.mode != cam.mode.chase:
            try:
                cam.mode=cam.mode.chase
                    
            except:
                cam.mode=cam.mode.automatic
     elif camera == 6:
        if cam.mode != cam.mode.locked:
            try:
                cam.mode=cam.mode.locked
                    
            except:
                cam.mode=cam.mode.automatic
     elif camera == 7:
        if cam.mode != cam.mode.orbital:
            try:
                cam.mode=cam.mode.orbital
                    
            except:
                cam.mode=cam.mode.automatic