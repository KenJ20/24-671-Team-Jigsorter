



'''
    The following code is for a puzzle sorting system for the Electromechanical
    systems design course (24-671) at Carnegie Mellon University. The code below
    is responsible for the main operations of the system: accepting an input from
    the user -> relaying information to the rest of the system.
    
    Author: Remington Frank
'''

import I2C_LCD_driver
from time import *
import RPi.GPIO as GPIO
import time
import auto_pic_test
from auto_pic_test import *
import run_screen
from run_screen import *

# Initialize pins on Pi and prep IO communications
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(29, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(31, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Define necessary variables
globTime = time.time()
pressTime1 = 0
pressTime2 = 0

select = 0

# Initialize LCD screen
teamlcd = I2C_LCD_driver.lcd()

# Two selection options for sorting: color and shape
teamlcd.lcd_display_string("Color", 1, 4)
teamlcd.lcd_display_string("Shape", 2, 4)


while True:
    # Display which value is currently being selected
    teamlcd.lcd_display_string("   ", (not select) + 1, 0)
    teamlcd.lcd_display_string("-->", select + 1, 0)
    
    # Check button press
    if GPIO.input(29) == GPIO.HIGH:
        globTime = time.time()
        
        # If new press, selection is made
        if abs(globTime - pressTime2) >= 0.25:
            pressTime2 = time.time()
            teamlcd.lcd_clear()
            
            # Display running screen
            runningScreen(0)
            ArduinoComm("start")
            
            # Begin running machine
            runMachine(select)
            print("Running machine")
            
            # Once machine running completed, display on screen
            completeScreen()
    
    # Check button press
    if GPIO.input(31) == GPIO.HIGH:
        globTime = time.time()
        
        # If new press, iterate through selection modes
        if abs(globTime - pressTime1) >= 0.25:
            pressTime1 = time.time()
            select = (not select)
            print("Button 1 pressed")
            
            
def completeScreen():
    teamlcd.lcd_display_string("Sorting Completed", 1, 2)
    time.sleep(10)
