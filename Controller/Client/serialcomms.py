import  krpc
import serial
import struct

def serialReceive(arduino, conn):

    ctrl = [0,0,0]
    DataErrorcode = 1          # 0 = success, 1 = unspec/timeout, 2 = bad data
    overflow = 1
    inData=struct.unpack('<B',arduino.read())
    ctrlByteNum = 0
    
    if arduino.in_waiting > 80:
        #arduino.write(0b10101010) #send wait to arduino
        print("overflow: ",arduino.in_waiting)
        #conn.ui.message("Overflow", position = conn.ui.MessagePosition.top_left)
        arduino.reset_input_buffer()
        overflow = 0
    #else:          # Acknowledge that we have data, disabled for now
        #conn.ui.message("Ack", position = conn.ui.MessagePosition.top_left)
        #arduino.write(0b01010101)

    if inData[0] == 0b10101010: #start char
          
        readOp = True
        waitloop = 1
        while readOp:
            waitloop += 1
            if waitloop > 1000: #timeout
                readOp = False   #leave
            if arduino.in_waiting > 0:
                inData=struct.unpack('<B',arduino.read())
            if inData[0] == 0b11001100: #EOF char
                readOp = False
                if (ctrlByteNum == 2 and DataErrorcode == 1): #if we have reached two bytes
                    DataErrorcode = 0

            elif inData[0] == 0b00001111: #escape char
                inData=struct.unpack('<B',arduino.read())     #read another
                ctrl[ctrlByteNum] = inData[0]                 #and copy directly
                ctrlByteNum += 1
                if ctrlByteNum > 1:
                    ctrlByteNum = 1
                    DataErrorcode = 2
            else:                               #not esc, not EOF
                if ctrlByteNum > 1:
                    ctrlByteNum = 1
                    DataErrorcode = 2
                ctrl[ctrlByteNum] = inData[0]
                ctrlByteNum += 1


    ctrl[2] = DataErrorcode # Last byte holds errorcode
    ctrl[2] = ctrl[2] & (0b10000000 * overflow)
    return ctrl