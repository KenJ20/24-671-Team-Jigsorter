

'''
    The following code is for a puzzle sorting system for the Electromechanical
    systems design course (24-671) at Carnegie Mellon University. The code below
    is responsible for identifying and classifying the puzzle pieces by their
    colors. The possible sorting groups are as follows: R, G, B, Bl, W.
    
    Author: Remington Frank
'''

import cv2
import numpy as np
#import matplotlib.pyplot as plt

def pieceIDColor(give_image):
    img = give_image
    
    cv2.imshow("Frame3", img)

    # Converting image to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #plt.figure(figsize=(20,8))
    #plt.imshow(img_rgb)
    #plt.show()

    # Converting RGB to HSV
    img_hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
    #plt.figure(figsize=(20,8))
    #plt.imshow(img_hsv)
    #plt.show()

    # Green bounds
    green_low = np.array([25,52,72])
    green_up = np.array([102,255,255])

    # Red bounds
    red_low = np.array([0,70,50])
    red_up = np.array([10,255,255])

    # Blue bounds
    blue_low = np.array([90,50,70])
    blue_up = np.array([128,255,255])

    # White bounds
    wht_low = np.array([0,0,50])
    wht_up = np.array([255,255,255])

    # Green Masked Image
    mask_g = cv2.inRange(img_hsv, green_low, green_up)
    res_g = cv2.bitwise_and(img, img, mask=mask_g)

    # Red Masked Image
    mask_r = cv2.inRange(img_hsv, red_low, red_up)
    res_r = cv2.bitwise_and(img, img, mask=mask_r)

    # Blue Masked Image
    mask_b = cv2.inRange(img_hsv, blue_low, blue_up)
    res_b = cv2.bitwise_and(img, img, mask=mask_b)


    # White Masked Image
    mask_w = cv2.inRange(img_hsv, wht_low, wht_up)
    res_w = cv2.bitwise_and(img, img, mask=mask_w)

    # Calculating Percentages
    perc_grn = (mask_g==255).mean()
    perc_red = (mask_r==255).mean()
    perc_blue = (mask_b==255).mean()
    perc_wht = (mask_w==255).mean()

    print(f'Percent Green: {perc_grn}')
    print(f'Percent Red: {perc_red}')
    print(f'Percent Blue: {perc_blue}')
    print(f'Percent White: {perc_wht}')

    # Plot green area
    #plt.figure(figsize=(20,8))
    #plt.imshow(res_g)
    #plt.show()

    # Plot red area
    #plt.figure(figsize=(20,8))
    #plt.imshow(res_r)
    #plt.show()

    # Plot blue area
    #plt.figure(figsize=(20,8))
    #plt.imshow(res_b)
    #plt.show()

    # Plot white area
    #plt.figure(figsize=(20,8))
    #plt.imshow(res_w)
    #plt.show()

    # Finding the main color of the puzzle piece
    color_perc = [perc_grn, perc_red, perc_blue, perc_wht]
    max_index = color_perc.index(max(color_perc))

    # Todo: Incorporate method for detecting if max color is black
    # based off of proportions of the other colors.
    
    return (max_index, color_perc)

def main():
    #(color, color_perc) = pieceIDColor(image)

    for k in range(42, 57):
        image = "image" + str(k) + ".png"
        (color, color_perc) = pieceIDColor(image)
        print(color)

    # Color: 0 - green, 1 - red, 2 - blue, 3 - white
    #return color