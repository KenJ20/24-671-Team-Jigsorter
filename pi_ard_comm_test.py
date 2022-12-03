

'''
    The following code is for a puzzle sorting system for the Electromechanical
    systems design course (24-671) at Carnegie Mellon University. The code below
    is responsible for communication between the Raspberry Pi and Arduino in the
    system. Camera -> Motor communications.
    
    Author: Remington Frank
'''

# /dev/ttyACM0

import serial
import time

def ArduinoComm(message):
    if __name__ == '__main__':
        ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        ser.reset_input_buffer()
        
        printString = ''
        waiting = True
        
        # Convert values in array to a single string
        for value in message:
            printString += str(value)
        
        # This will have to be thoroughly tested
        while waiting:
            # Convert string to bytes and write to Arduino serial
            ser.write(bytes(printString, 'utf-8'))
            
            # Undo commenting below for debugging
            line = ser.readline().decode('utf-8').rstrip()
            
            # Arduino should send a 1 if it successfully reads the command
            if line != '' and int(line) == 1:
                waiting = False
                
            print(line)
            time.sleep(1)
