import time
from pySerialTransfer import pySerialTransfer as txfer
from struct import *

link = txfer.SerialTransfer("COM3")
if __name__ == '__main__':
    try:
        link.open()
        time.sleep(2) # allow some time for the Arduino to completely reset
        
        send_size = 0
        
        ###################################################################
        # Send a list
        ###################################################################
        
        data = pack("HBBBB", 4, 1, 2, 3, 4)

        for index in range(len(data)):
            link.txBuff[index + send_size] = data[index]
        send_size += len(data)
        
        ###################################################################
        # Transmit all the data to send in a single packet
        ###################################################################
        link.send(send_size)
        
        ###################################################################
        # Wait for a response and report any errors while receiving packets
        ###################################################################
        while not link.available():
            if link.status < 0:
                if link.status == -1:
                    print('ERROR: CRC_ERROR')
                elif link.status == -2:
                    print('ERROR: PAYLOAD_ERROR')
                elif link.status == -3:
                    print('ERROR: STOP_BYTE_ERROR')
        
        ###################################################################
        # Parse response list
        ###################################################################
        
        returnVal = unpack("HBBBB", bytes(link.rxBuff[0:6]))
        
        ###################################################################
        # Display the received data
        ###################################################################
        print('SENT: {} {} {} {} {}'.format(4, 1, 2, 3, 4))
        print('RCVD: {}'.format(returnVal))
        print(' ')
    
    except KeyboardInterrupt:
        link.close()
    
    except:
        import traceback
        traceback.print_exc()
        
        link.close()