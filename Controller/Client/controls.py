import krpc


def actions(ctrl, oldCtrl, vessel, partlist):
     if ((ctrl[0] & 0b00001000) != (oldCtrl[0] & 0b00001000)):
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

            
     if ((ctrl[0] & 0b00000100) !=(oldCtrl[0] & 0b00000100)):
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

     if ((ctrl[0] & 0b00000010) != (oldCtrl[0] & 0b00000010)):
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

     if ((ctrl[0] & 0b00010000) != (oldCtrl[0] & 0b00010000)):
        rwheels=(ctrl[0] & 0b00010000)
        if rwheels:
            for ReactionWheel in vessel.parts.reaction_wheels:
                ReactionWheel.active = True
        else:
            for ReactionWheel in vessel.parts.reaction_wheels:
                ReactionWheel.active = False

     if ((ctrl[0] & 0b00000001) != (oldCtrl[0] & 0b00000001)):
         state = bool((ctrl[0] & 0b00000001))
         batCapacity = vessel.resources.max('ElectricCharge')
         for respart in vessel.parts.all:
            for bat in respart.resources.with_resource('ElectricCharge'):
                if ((bat.max*20 < batCapacity) or (bat.amount < 20)) and bat.amount < 1001:
                    bat.enabled = not(bool(ctrl[0] & 0b00000001))

     if ((ctrl[1] & 0b00000001) !=(oldCtrl[1] & 0b00000001)):
        engine =(ctrl[1] & 0b00000001)
        if engine:
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
            for Engine in vessel.parts.engines:
                try:
                    Engine.mode='ClosedCycle'
                except:
                    pass
                try:
                    Engine.mode='Dry'
                except:
                    pass

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