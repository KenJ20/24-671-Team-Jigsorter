

'''
    The following code is for a puzzle sorting system for the Electromechanical
    systems design course (24-671) at Carnegie Mellon University. The code below
    is responsible for displaying system status to the user.
    
    Author: Remington Frank
'''

import I2C_LCD_driver
from time import *
import RPi.GPIO as GPIO
import time

# Initialize LCD screen
teamlcd = I2C_LCD_driver.lcd()

def runningScreen(piecesMeasured):
    remain = piecesMeasured % 3
    
    # Convert integer value to a string to be concatenated below
    piecesMeasured = str(piecesMeasured)
    
    # Display running screen
    if remain == 0:
        teamlcd.lcd_display_string("Running.", 1, 4)
    elif remain == 1:
        teamlcd.lcd_display_string("Running..", 1, 4)
    else:
        teamlcd.lcd_display_string("Running...", 1, 4)
    
    # Provide an updated count of the quantity of sorted pieces
    teamlcd.lcd_display_string("Pieces Sorted: " + piecesMeasured, 2, 2)
