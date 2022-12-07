


'''
Object detection with OpenCV
    Adapted from the original code developed by Adrian Rosebrock
    Visit original post: https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
    Adapted from code by Marcelo Rovai - MJRoBot.org @ 7Feb2018
    
    The code below is adapted from the above to track puzzle pieces using color
    masking. The following code is for a puzzle sorting system for the Electromechanical
    systems design course (24-671) at Carnegie Mellon University.
    
    Author: Remington Frank
'''

# import the necessary packages
from collections import deque
import numpy as np
import argparse
import imutils
import cv2
import Piece_ID_color_v1
from Piece_ID_color_v1 import *
import Piece_ID_pixy
from Piece_ID_pixy import *
import run_screen
from run_screen import *
import serial
import time

def runMachine(sortMethod):
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video",
        help="path to the (optional) video file")
    ap.add_argument("-b", "--buffer", type=int, default=64,
        help="max buffer size")
    args = vars(ap.parse_args())

    # define the lower and upper boundaries of the "white object"
    # (or "puzzle piece") in the HSV color space, then initialize the
    # list of tracked points
    colorLower = (0, 0, 150)
    colorUpper = (255, 255, 255)
    pts = deque(maxlen=args["buffer"])
    imageCaptured = 0
    piecesIdentified = 0
    
    binNum = 0
    
    numGreen = 0
    numBlue = 0
    numRed = 0
    numWhite = 0
    numBlack = 0
    
    numMid = 0
    numEdge = 0
    numCorn = 0
     
    # if a video path was not supplied, grab the reference
    # to the webcam
    if not args.get("video", False):
        camera = cv2.VideoCapture(0)
     
    # otherwise, grab a reference to the video file
    else:
        camera = cv2.VideoCapture(args["video"])

    # keep looping
    while True:
        # grab the current frame
        (grabbed, frame) = camera.read()
     
        # if we are viewing a video and we did not grab a frame,
        # then we have reached the end of the video
        if args.get("video") and not grabbed:
            break
     
        # resize the frame, inverted ("vertical flip" w/ 180degrees),
        # blur it, and convert it to the HSV color space
        frame = imutils.resize(frame, width=600)
        frame = imutils.rotate(frame, angle=180)
        # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
     
        # construct a mask for the color "green", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv2.inRange(hsv, colorLower, colorUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        
        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None
     
        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            
            # Below, we are going to crop the image so that we can
            # send the smallest image possible to the I.D. algorithms
            # thus making the I.D. of the piece a quicker process.
            left = 0
            right = 600
            up = 0
            down = 600
            
            if center[1] - radius < 0:
                up = 0
            else:
                up = round(center[1] - radius)
                
            if center[1] + radius > 600:
                down = 600
            else:
                down = round(center[1] + radius)
                
            if center[0] - radius < 0:
                left = 0
            else:
                left = round(center[0] - radius)
                
            if center[0] + radius > 600:
                right = 600
            else:
                right = round(center[0] + radius)
            
            # Image is cropped using the cv2 bounding circle's radius
            try:
                crop_frame = frame[up:down, left:right]
            except:
                crop_frame = frame
                
            print(center)
            
            # Once the piece is in the center of the frame, we will send its captured image
            # to the piece I.D. algorithms. We also mark that the piece has been recorded, awaiting
            # for it to exit a given range before searching/accepting the next piece
            if center[0] <= 310 and center[0] >= 290 and center[1] < 400 and not imageCaptured:
                imageCaptured = 1
                
                # Classify puzzle piece and send to Arduino. Message to arduino is condensed into a string
                # of integers. First integer is the method which the piece was sorted (color/shape). Second
                # integer is the classification of the piece.
                if not(sortMethod):
                    colorPerc = (pieceIDColor(crop_frame))[1]
                    maxIndex = (pieceIDColor(crop_frame))[0]
                    piecesIdentified += 1
                    print(colorPerc)
                    
                    if (maxIndex == 0):
                        numGreen += 1
                        binNum = 0
                    elif (maxIndex == 1):
                        numRed += 1
                        binNum = 1
                    elif(maxIndex == 2):
                        numBlue += 1
                        binNum = 2
                    elif(maxIndex == 3):
                        numWhite += 1
                        binNum = 3
                        
                    
                    # Send I.D. classification to Arduino for sorting
                    ArduinoComm(binNum)
                    time.sleep(10)
                else:
                    pieceType = pieceID(crop_frame)
                    piecesIdentified += 1
                    print(pieceType)
                    
                    if(pieceType == 0):
                        numMid += 1
                        binNum = 0
                        
                        if(numMid > 100 and numMid < 200):
                            binNum = 1
                        elif(numMid > 200 and numMid < 300):
                            binNum = 2
                        elif(numMid > 300 and numMid < 400):
                            binNum = 5
                    
                    elif(pieceType == 1):
                        numEdge += 1
                        binNum = 4
                    else:
                        binNum = 5
                    
                    # Send I.D. classification to Arduino for sorting
                    ArduinoComm(binNum)
                    time.sleep(10)
                
                # Might need to add a feature to wait for a response from the Arduino telling this system
                # that the puzzle piece has been finished storing so that it can accept a new input. Or just
                # have all inputs to the Arduino be stored into an array such that the first index is the most
                # current puzzle piece
                
                # Update the UI screen to show quantity of pieces sorted
                runningScreen(piecesIdentified)
                
            # reset image capture status once previous piece has exited range
            if center[0] > 315:
                imageCaptured = 0
                
            # only proceed if the radius meets a minimum size
            if radius > 10:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(frame, (int(x), int(y)), int(radius),
                    (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
            
        # update the points queue
        pts.appendleft(center)
        
            # loop over the set of tracked points
        for i in range(1, len(pts)):
            # if either of the tracked points are None, ignore
            # them
            if pts[i - 1] is None or pts[i] is None:
                continue
     
            # otherwise, compute the thickness of the line and
            # draw the connecting lines
            thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
            cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
     
        # show the frame to our screen
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
     
        # if the 'q' key is pressed, stop the loop
        if key == ord("q") or piecesIdentified == 100:
            break
     
    # cleanup the camera and close any open windows
    camera.release()
    cv2.destroyAllWindows()
    
def ArduinoComm(message):
    print(__name__)
    if __name__ == 'auto_pic_test':
        ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        ser.reset_input_buffer()
        
        waiting = True
        #print(message)
        
        if type(message) != str:
            message = str(message)
        
        # Convert values in array to a single string

        # This will have to be thoroughly tested
        while waiting:
            # Convert string to bytes and write to Arduino serial
            ser.write(bytes(message, 'utf-8'))
            
            # Undo commenting below for debugging
            line = ser.readline().decode('utf-8').rstrip()
            print(line)
            # Arduino should send a 1 if it successfully reads the command
            if line == 'F' or line == 'accepted':
                waiting = False
                
            print(line)
            #time.sleep(1)
