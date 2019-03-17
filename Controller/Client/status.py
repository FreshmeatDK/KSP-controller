import krpc

def getStatus(vInfo):
    status = [0,0,0]
    if vInfo['mass'] != 0:
        status[0] = int(vInfo['mxThr']/vInfo['mass']*100) #acceleration in cm/s
        if status[0]>65535:
          status[0] = 65535
    else: status[0] = 0

    return status

    


