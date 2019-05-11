import  krpc
import serial
import struct

def serialReceive(arduino, conn):

    ctrl = [0,0,0,0]
    DataErrorcode = 1          # 0 = success, 1 = unspec/timeout, 2 = bad data
    overflow = 1
 
    ctrlByteNum = 0
    
    if arduino.in_waiting > 80:
        #arduino.write(0b10101010) #send wait to arduino
        print("overflow: ",arduino.in_waiting)
        #conn.ui.message("Overflow", position = conn.ui.MessagePosition.top_left)
        arduino.reset_input_buffer()
        overflow = 1
    else:          # Acknowledge that we have data, disabled for now
        #conn.ui.message("Ack", position = conn.ui.MessagePosition.top_left)
        #arduino.write(0b01010101)
        overflow = 0

        inData=struct.unpack('<B',arduino.read())
        print(inData[0])
        if inData[0] == 0b10101010: #start char (=170)
            readOp = True
            waitloop = 1
            while readOp:
                waitloop += 1
                if waitloop > 1000: #timeout
                    readOp = False   #leave
                    DataErrorcode = 1
                if arduino.in_waiting > 0:
                    inData=struct.unpack('<B',arduino.read())
                    print("inData ", inData[0])
                if inData[0] == 0b11001100: #EOF char (=204)
                    readOp = False
                    if (ctrlByteNum == 3 and DataErrorcode == 1): #if we have reached three bytes
                        DataErrorcode = 0

                elif inData[0] == 0b00001111: #escape char (=15)
                    inData=struct.unpack('<B',arduino.read())     #read another
                    print("inDataesc ", inData[0])
                    ctrl[ctrlByteNum] = inData[0]                 #and copy directly
                    ctrlByteNum += 1
                    if ctrlByteNum > 2:
                        ctrlByteNum = 2
                        DataErrorcode = 2
                else:                               #not esc, not EOF
                    if ctrlByteNum > 2:
                        ctrlByteNum = 2
                        DataErrorcode = 2
                    ctrl[ctrlByteNum] = inData[0]
                    ctrlByteNum += 1
        LRC = 0b0
        
        for i in range(2):
            LRC = LRC^ctrl[i]
        #print("LRC: ", LRC)
       #if LRC != ctrl[2]:
       #     DataErrorcode = 2
    ctrl[3] = DataErrorcode # Last byte holds errorcode
    ctrl[3] = ctrl[3] | ( overflow << 7)
    print(ctrl, DataErrorcode, overflow)
    return ctrl