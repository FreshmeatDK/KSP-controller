import krpc
import math
import numpy as np
import numpy.linalg as la

def getStatus(vInfo):
    status = [0,0,0]

    
    #dir = np.array(vInfo['dir'])
    #prograde = np.array(vInfo['prograde'])


    #dev=math.acos(vInfo['dir'][1])
    #dev=math.acos(np.dot(dir,prograde))

    if vInfo['mass'] != 0:
        status[0] = int(vInfo['mxThr']/vInfo['mass']*100) #acceleration in cm/s
        if status[0]>65535:
          status[0] = 65535
    else: status[0] = 0

    #print(dev, prograde, dir)

    if vInfo['sigStr'] < 0.00001: mask = 0b00001100 # lvl 3 at bit 4-5
    elif vInfo['sigStr'] < 0.05: mask = 0b00001000 # lvl 2 at bit 4-5
    elif vInfo['sigStr'] < 0.25: mask = 0b0000100 # lvl 1 at bit 4-5
    else: mask = 0b00000000                        # lvl 0 at bit 4-5 go green
    status[1] = (status[1] & 0b11110011) | mask    # leave other bits, add result at bit 4-5
    return status

def getSOIbodynum(vessel):

    name = vessel.orbit.body.name
    
    name = name.casefold()

    if name == "ciro": SOINum = 200#                   GPP bodies (the why we cant use KSPSerialIO SOInum)
    elif name == "icarus": SOINum = 210
    elif name == "thalia": SOINum = 220
    elif name == "eta": SOINum = 221
    elif name == "niven": SOINum = 230
    elif name == "gael": SOINum = 240
    elif name == "iota": SOINum = 241
    elif name == "ceti": SOINum = 242
    elif name == "tellumo": SOINum = 250
    elif name == "lili": SOINum = 251
    elif name == "gratian": SOINum = 260
    elif name == "geminus": SOINum = 261
    elif name == "otho": SOINum = 270
    elif name == "augustus": SOINum = 271
    elif name == "hephaestus": SOINum = 272
    elif name == "jannah": SOINum = 273
    elif name == "gauss": SOINum = 280
    elif name == "loki": SOINum = 281
    elif name == "catullus": SOINum = 282
    elif name == "tarsiss": SOINum = 283
    elif name == "nero": SOINum = 290
    elif name == "hadrian": SOINum = 291
    elif name == "narisse": SOINum = 292
    elif name == "muse": SOINum = 293
    elif name == "minona": SOINum = 294
    elif name == "agrippina": SOINum = 295
    elif name == "julia": SOINum = 296
    elif name == "hox": SOINum = 310
    elif name == "argo": SOINum = 311
    elif name == "grannus": SOINum = 400
    
    elif name == "kerbol": SOINum = 100#               Kerbol Bodies (As we are going to send info anyway)
    elif name == "moho": SOINum = 110
    elif name == "eve": SOINum = 120
    elif name == "gilly": SOINum = 121
    elif name == "kerbin": SOINum = 130
    elif name == "mun": SOINum = 131
    elif name == "minmus": SOINum = 132
    elif name == "duna": SOINum = 140
    elif name == "ike": SOINum = 141
    elif name == "dres": SOINum = 150
    elif name == "jool": SOINum = 160
    elif name == "laythe": SOINum = 161
    elif name == "vall": SOINum = 162
    elif name == "tylo": SOINum = 163
    elif name == "bop": SOINum = 164
    elif name == "pol": SOINum = 165
    elif name == "eeloo": SOINum = 170

    else: SOINum = 255

    return SOINum

