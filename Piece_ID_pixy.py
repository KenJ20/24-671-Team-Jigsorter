

import cv2
import numpy as np
from matplotlib import pyplot as plt
import itertools
import math
import time

def getAngle(a, b, c):
    ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    return ang + 360 if ang < 0 else ang

def getSignAngle(a, b, c):
    ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    return 1 if ang < 0 else -1
    
def findCorners(combos):
    dist_one = 0
    dist_two = 0
    dist_three = 0
    dist_four = 0
    ang1 = 0;
    ang2 = 0;
    ang3 = 0;
    ang4 = 0;
    area = 0;
    prev_area = 0
    rect = []

    for combo in combos:
        dist_one = ((combo[0][0] - combo[1][0])**2 + (combo[0][1] - combo[1][1])**2)**(1/2)
        dist_two = ((combo[1][0] - combo[2][0])**2 + (combo[1][1] - combo[2][1])**2)**(1/2)
        dist_three = ((combo[2][0] - combo[3][0])**2 + (combo[2][1] - combo[3][1])**2)**(1/2)
        dist_four = ((combo[3][0] - combo[0][0])**2 + (combo[3][1] - combo[0][1])**2)**(1/2)
        dist_diag_one = ((combo[0][0] - combo[2][0])**2 + (combo[0][1] - combo[2][1])**2)**(1/2)
        dist_diag_two = ((combo[3][0] - combo[1][0])**2 + (combo[3][1] - combo[1][1])**2)**(1/2)

        ang1 = getAngle(combo[0], combo[1], combo[2])
        ang2 = getAngle(combo[1], combo[2], combo[3])
        ang3 = getAngle(combo[2], combo[3], combo[0])
        ang4 = getAngle(combo[3], combo[0], combo[1])

        area = dist_one * dist_two

        if(area > (dist_two * dist_three)):
            area = dist_two * dist_three
        
        if(area > (dist_three * dist_four)):
            area = dist_three * dist_four

        if(area > (dist_four * dist_one)):
            area = dist_four * dist_one


        if(ang1 <= 1.1 * 90 and ang1 >= 0.9 * 90 and ang2 <= 1.1 * 90 and ang2 >= 0.9 * 90 and area > prev_area and ang3 <= 1.1 * 90 and ang3 >= 0.9 * 90 and ang4 <= 1.1 * 90 and ang4 >= 0.9 * 90):
            rect = combo
            prev_area = area

    
    return rect

def processImage(give_image):
    # Open image
    img = cv2.imread(give_image)

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_gray = cv2.medianBlur(img_gray, ksize=5)
    thresh = cv2.threshold(img_gray, 40, 255, cv2.THRESH_BINARY)[1]
    #thresh = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, \
            #cv2.THRESH_BINARY, 11, 2)
    thresh = cv2.blur(thresh, ksize=(3, 3))

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    crn = cv2.cornerHarris(thresh, 7, 7, 0.03)
    crn = cv2.dilate(crn, None)

    #crn = cv2.convertScaleAbs( crn )
    cornershow = crn.copy()
    refineshow = crn.copy()
    pointshow = crn.copy()

    w, h = thresh.shape
    cands = []
    for y in range(0, h):
        for x in range(0, w):
            if crn[x, y] > 10:
                cv2.circle(cornershow, (y, x), 1, (255,0,25))
                cands.append((y, x))


    keep = []
    keep.append(cands[0])
    strength = 0
    dist = 0

    for val in cands:
        for point in keep:
            dist = ((val[0] - point[0])**2 + (val[1] - point[1])**2)**(1/2)

            if(dist > 15):
                strength += 1

        if(strength == len(keep)):
            keep.append(val)

        strength = 0

    max_height = 0;
    min_height = keep[0][1];

    for kept in keep:
        if(kept[1] > max_height):
            max_height = kept[1]
        if(kept[1] < min_height):
            min_height = kept[1]

    # Todo: Ensure that male connections are not erased. Only get rid of points
    # in true middle of piece. Then get the combinations of these points, only
    # including 4 at a time. Create a function that takes in this list, evaluates
    # the area created by the points, as well as the angularity. Return the set of
    # four points with the best rectangularity. Continue to edge detection

    simp = []
    for pnt in keep:
        cv2.circle(pointshow, pnt, 1, (255,0,25))
        if(pnt[1] < 0.90*max_height and pnt[1] > 1.15*min_height):
            pass
        else:
            simp.append(pnt)


    for pt in simp:
        cv2.circle(refineshow, pt, 4, (255,0,0))

    coms = list(itertools.permutations(keep, 4))
    coms2 = []

    for sets in coms:
        if sets[0][0] < sets[2][0] and sets[0][0] < sets[3][0] and sets[1][0] < sets[2][0] and sets[1][0] < sets[3][0]:
            if sets[0][1] < sets[1][1] and sets[0][1] < sets[2][1] and sets[3][1] < sets[1][1] and sets[3][1] < sets[2][1]:
                coms2.append(sets)

    rect = findCorners(coms2)

    edges = cv2.Canny(thresh, 100, 200)
    for point in rect:
        cv2.circle(edges, point, 4, (255,0,0))

    plt.subplot(1, 1, 1)
    plt.imshow(edges)
    plt.show()

    # Rotate the image for identification to work
    baseLine = (rect[0][0]+50, rect[0][1])
    rotateAngle = getAngle(rect[3], rect[0], baseLine)
    sign = getSignAngle(rect[3], rect[0], baseLine)

    if(rotateAngle > 180): rotateAngle = 360 - rotateAngle

    M = cv2.getRotationMatrix2D((h // 2, w // 2), rotateAngle*sign, 1.0)
    rotated = cv2.warpAffine(img, M, (h, w))

    print(rotateAngle)

    return pieceID(rotated)

def pieceID(give_image):
    # Open image
    img = give_image

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_gray = cv2.medianBlur(img_gray, ksize=5)
    thresh = cv2.threshold(img_gray, 40, 255, cv2.THRESH_BINARY)[1]
    #thresh = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, \
            #cv2.THRESH_BINARY, 11, 2)
    thresh = cv2.blur(thresh, ksize=(3, 3))

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    crn = cv2.cornerHarris(thresh, 7, 7, 0.03)
    crn = cv2.dilate(crn, None)

    #crn = cv2.convertScaleAbs( crn )
    cornershow = crn.copy()
    refineshow = crn.copy()
    pointshow = crn.copy()

    w, h = thresh.shape
    cands = []
    for y in range(0, h):
        for x in range(0, w):
            if crn[x, y] > 10:
                cv2.circle(cornershow, (y, x), 1, (255,0,25))
                cands.append((y, x))


    keep = []
    keep.append(cands[0])
    strength = 0
    dist = 0

    for val in cands:
        for point in keep:
            dist = ((val[0] - point[0])**2 + (val[1] - point[1])**2)**(1/2)

            if(dist > 15):
                strength += 1

        if(strength == len(keep)):
            keep.append(val)

        strength = 0

    max_height = 0;
    min_height = keep[0][1];

    for kept in keep:
        if(kept[1] > max_height):
            max_height = kept[1]
        if(kept[1] < min_height):
            min_height = kept[1]

    # Todo: Ensure that male connections are not erased. Only get rid of points
    # in true middle of piece. Then get the combinations of these points, only
    # including 4 at a time. Create a function that takes in this list, evaluates
    # the area created by the points, as well as the angularity. Return the set of
    # four points with the best rectangularity. Continue to edge detection

    simp = []
    for pnt in keep:
        cv2.circle(pointshow, pnt, 1, (255,0,25))
        if(pnt[1] < 0.90*max_height and pnt[1] > 1.15*min_height):
            pass
        else:
            simp.append(pnt)


    for pt in simp:
        cv2.circle(refineshow, pt, 4, (255,0,0))

    coms = list(itertools.permutations(keep, 4))
    coms2 = []

    for sets in coms:
        if sets[0][0] < sets[2][0] and sets[0][0] < sets[3][0] and sets[1][0] < sets[2][0] and sets[1][0] < sets[3][0]:
            if sets[0][1] < sets[1][1] and sets[0][1] < sets[2][1] and sets[3][1] < sets[1][1] and sets[3][1] < sets[2][1]:
                coms2.append(sets)

    rect = findCorners(coms2)

    edges = cv2.Canny(thresh, 100, 200)
    for point in rect:
        cv2.circle(edges, point, 4, (255,0,0))

    plt.subplot(1, 1, 1)
    plt.imshow(edges)
    plt.show()

    # Need to sort through all "corners" detected
    # We know corner points
    # If the other corner points in that region are:
    # <y = inner, >y = outer, ~= y == straight edge

    edge1 = [] # left edge
    edge2 = [] # right edge
    edge3 = [] # upper edge
    edge4 = [] # lower edge
    yvals = []
    xvals = []

    for click in keep:
        yvals.append(click[1])
        xvals.append(click[0])

    avgY = sum(yvals) / len(yvals)
    avgX = sum(xvals) / len(xvals)

    #plt.subplot(1, 1, 1)
    #plt.imshow(pointshow)
    #plt.show()

    # x (increases down), y (increases right)
    maxX = 0
    maxY = 0
    minX = 1000
    minY = 1000
    for corner in rect:
        if corner[0] > maxX: maxX = corner[0]
        if corner[0] < minX: minX = corner[0]
        if corner[1] > maxY: maxY = corner[1]
        if corner[1] < minY: minY = corner[1]

    centerX = (minX + maxX) / 2
    centerY = (minY + maxY) / 2

    for pair in keep:
        if pair in rect:
            pass;
        else:
            # left and right edges
            if pair[0] < (minX + ((maxX - minX) * 0.25)) or pair[0] > (maxX - ((maxX - minX) * 0.25)):
                # left edge
                if pair[0] < centerX:
                    edge1.append(pair)
                # right edge
                else:
                    edge3.append(pair)
            else:
                if pair[1] > centerY:
                    edge2.append(pair)
                else:
                    edge4.append(pair)


    sumE1 = 0
    sumE2 = 0
    sumE3 = 0
    sumE4 = 0

    for pairs in edge1:
        sumE1 += pairs[0]

    for pairs in edge2:
        sumE2 += pairs[1]

    for pairs in edge3:
        sumE3 += pairs[0]

    for pairs in edge4:
        sumE4 += pairs[1]

    pieceType = 0

    # Todo: Hypothesize, I believe we can assume there are no points detected for straight edges
    # might not need to do the geometry stuff and just say if the edge array is empty, then
    # that side is a straight edge.

    if len(edge1) == 0:
        pieceType += 1
    #else:
        #avgE1 = sumE1 / len(edge1)
        # Check shape of side 1
        #if avgE1 < (minX + 5) and avgE1 > (minX - 5):
            #pieceType += 1
        #else:
            #pieceType += 0

    if len(edge2) == 0:
        pieceType += 1
    #else:
        #avgE2 = sumE2 / len(edge2)
        # Check shape of side 2
        #if avgE2 > (maxY - 5) and avgE2 < (maxY + 5):
            #pieceType += 1
        #else:
            #pieceType += 0

    if len(edge3) == 0:
        pieceType += 1
    #else:
        #avgE3 = sumE3 / len(edge3)
        # Check shape of side 3
        #if avgE3 > (maxX - 5) and avgE3 < (maxX + 5):
            #pieceType += 1
        #else:
            #pieceType += 0

    if len(edge4) == 0:
        pieceType += 1
    #else:
        #avgE4 = sumE4 / len(edge4)
        # Check shape of side 4
        #if avgE4 > (minX - 5) and avgE4 < (minX + 5):
            #pieceType += 1
        #else:
            #pieceType += 0

    #if pieceType == 0: print("Middle Piece!")
    #elif pieceType == 1: print("Edge Piece!")
    #else: print("Corner Piece!")
    #plt.subplot(1, 1, 1)
    #plt.imshow(edges)
    #plt.show()

    return pieceType

def main():
    start = time.time()
    image = ""
    pType = 0
    pTypes1 = []
    correct = 0

    # Trial 1
    trueTypes1 = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0]

    for i in range(11, 42):
        image = "image" + str(i) + ".png"
        pType = pieceID(image)
        pTypes1.append(pType)
    
    end = time.time()

    for j in range(len(trueTypes1)):
        if(trueTypes1[j] == pTypes1[j]):
            correct += 1
    
    percCorr = correct / len(trueTypes1)

    print("Trial 1 -")
    print(f'Percent Correct: {percCorr * 100}')
    print(f'Time Elapsed: {end - start}')
    #print(pTypes1)

    # Trial 2
    correct = 0
    start = time.time()
    pTypes2 = []

    trueTypes2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]

    for k in range(42, 57):
        image = "image" + str(k) + ".png"
        pType = pieceID(image)
        pTypes2.append(pType)
    
    end = time.time()

    for l in range(len(trueTypes2)):
        if(trueTypes2[l] == pTypes2[l]):
            correct += 1
    
    percCorr = correct / len(trueTypes2)

    print("Trial 2 -")
    print(f'Percent Correct: {percCorr * 100}')
    print(f'Time Elapsed: {end - start}')
