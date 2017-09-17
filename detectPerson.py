# Person detection code taken from http://www.pyimagesearch.com/2015/11/09/pedestrian-detection-opencv/

from __future__ import print_function
from imutils.object_detection import non_max_suppression
from imutils import paths
import numpy as np
import argparse
import imutils
import cv2
import collections

class PrevRectUtilities:
    prev_xA = 0
    prev_yA = 0
    prev_xB = 0
    prev_yB = 0
    prev_width = 0
    prev_height = 0
    leftCounter = 0
    rightCounter = 0
    stopCounter = 0
    halfWidth = 0

def detect_turn(xA, xB):
    # Left turn
    if xA < PrevRectUtilities.halfWidth - 80:
        PrevRectUtilities.leftCounter = PrevRectUtilities.leftCounter + 1
        if PrevRectUtilities.leftCounter == 5:
            PrevRectUtilities.leftCounter = 0
            return 'Left'
        else:
            return 'Forward'
    # Right turn
    elif xB > PrevRectUtilities.halfWidth + 80:
        PrevRectUtilities.rightCounter = PrevRectUtilities.rightCounter + 1
        if PrevRectUtilities.rightCounter == 5:
            PrevRectUtilities.rightCounter = 0
            return 'Right'
        else:
            return 'Forward'
    # Don't turn
    else:
        PrevRectUtilities.leftCounter = 0
        PrevRectUtilities.rightCounter = 0
        return 'Forward'

def detect_stop(yA, yB):
    curr_height = yB - yA
    prev_height = PrevRectUtilities.yB - PrevRectUtilities.yA

    if curr_height > 1.1 * prev_height:
        PrevRectUtilities.stopCounter = PrevRectUtilities.stopCounter + 1
        if PrevRectUtilities.stopCounter == 5:
            PrevRectUtilities.stopCounter = 0
            return True
        else:
            return False
    else:
        PrevRectUtilities.stopCounter = 0
        return False

def compare_prev_rect(xA, yA, xB, yB):
    curr_width = xB - xA
    curr_height = yB - yA

    if PrevRectUtilities.prev_width != 0:
        # If the width and height of the current rectangle are within a specified number of pixels of the width and height of the previous rectangle
        if abs(PrevRectUtilities.prev_width - curr_width) < 30 and abs(PrevRectUtilities.prev_height - curr_height) < 30:
            PrevRectUtilities.xA = xA
            PrevRectUtilities.yA = yA
            PrevRectUtilities.xB = xB
            PrevRectUtilities.yB = yB
            PrevRectUtilities.prev_width = curr_width
            PrevRectUtilities.prev_height = curr_height
            return True
        # Else if current rectangle is within a specified number of pixels of the previous rectangle
        elif (xA <= PrevRectUtilities.xA + 20 and xA >= PrevRectUtilities.xA - 20) and (yA <= PrevRectUtilities.yA + 20 and yA >= PrevRectUtilities.yA - 20) and (xB <= PrevRectUtilities.xB + 20 and xB >= PrevRectUtilities.xB - 20) and (yB <= PrevRectUtilities.yB + 20 and yB >= PrevRectUtilities.yB - 20):
            PrevRectUtilities.xA = xA
            PrevRectUtilities.yA = yA
            PrevRectUtilities.xB = xB
            PrevRectUtilities.yB = yB
            PrevRectUtilities.prev_width = curr_width
            PrevRectUtilities.prev_height = curr_height
            return True
        # Else if current rectangle is completely within previous rectangle
        if xA <= PrevRectUtilities.xA and yA <= PrevRectUtilities.yA and xB <= PrevRectUtilities.xB and yB <= PrevRectUtilities.yB:
            PrevRectUtilities.xA = xA
            PrevRectUtilities.yA = yA
            PrevRectUtilities.xB = xB
            PrevRectUtilities.yB = yB
            PrevRectUtilities.prev_width = curr_width
            PrevRectUtilities.prev_height = curr_height
            return True
        else:
            return False
    else:
        PrevRectUtilities.xA = xA
        PrevRectUtilities.yA = yA
        PrevRectUtilities.xB = xB
        PrevRectUtilities.yB = yB
        PrevRectUtilities.prev_width = curr_width
        PrevRectUtilities.prev_height = curr_height
        return True

def compare_prev_inv_rect(xA, yA, xB, yB, x1A, y1A, x1B, y1B):
    curr_width = xB - xA
    curr_height = yB - yA

    prev_width = x1B - x1A
    prev_height = y1B - y1A

    if PrevRectUtilities.prev_width != 0:
        # If the width and height of the current rectangle are within a specified number of pixels of the width and height of the previous rectangle
        if abs(prev_width - curr_width) < 30 and abs(prev_height - curr_height) < 30:
            return True
        # Else if current rectangle is within a specified number of pixels of the previous rectangle
        elif (xA <= x1A + 20 and xA >= x1A - 20) and (yA <= y1A + 20 and yA >= y1A - 20) and (xB <= x1B + 20 and xB >= x1B - 20) and (yB <= y1B + 20 and yB >= y1B - 20):
            return True
        # Else if current rectangle is completely within previous rectangle
        if xA <= x1A and yA <= y1A and xB <= x1B and yB <= y1B:
            return True
        else:
            return False
    else:
        return True
 
def detect_person(image):
    # Initialize the HOG descriptor/person detector
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    # Load the image and resize it to (1) reduce detection time
    # and (2) improve detection accuracy
    image = imutils.resize(image, height=300)

    PrevRectUtilities.halfWidth = image.shape[1] / 2
    
    # Detect people in the image
    (rects, weights) = hog.detectMultiScale(image, winStride=(4, 4), padding=(8, 8), scale=1.05)
    
    # Apply non-maxima suppression to the bounding boxes using a
    # fairly large overlap threshold to try to maintain overlapping
    # boxes that are still people
    rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
    pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)

    # list for recording invalid rectangles
    history = collections.deque(maxlen=5)

    # Draw the final bounding boxes
    try:
        (xA, yA, xB, yB) = pick[0]

        # Check if previous rectangle dimensions are similar to current rectangle dimensions
        isPrevRectSimilar = compare_prev_rect(xA, yA, xB, yB)

        # Draw current rectangle if previous rectangle has similar dimensions
        if isPrevRectSimilar:
            cv2.rectangle(image, (xA, yA), (xB, yB), (0, 255, 0), 2)
            isPersonStopping = detect_stop(yA, yB)
            coords = (xA, yA, xB, yB)
        # Else draw previous rectangle
        else:
            cv2.rectangle(image, (PrevRectUtilities.xA, PrevRectUtilities.yA), (PrevRectUtilities.xB, PrevRectUtilities.yB), (0, 255, 0), 2)
            validation = True
            for h in history:
                if not compare_prev_inv_rect(xA, yA, xB, yB, h[0], h[1], h[2], h[3]):
                    validation = False
                    break
            if validation:
                PrevRectUtilities.xA = xA
                PrevRectUtilities.xB = xB
                PrevRectUtilities.yA = yA
                PrevRectUtilities.yB = yB
            
            history.append((xA, yA, xB, yB))
            coords = (PrevRectUtilities.xA, PrevRectUtilities.yA, PrevRectUtilities.xB, PrevRectUtilities.yB)
        
        # direction specifies which direction the car should go in (Left, Right, or Forward)
        direction = detect_turn(xA, xB)
    except IndexError:
        pass

    try:
        return direction, isPersonStopping, coords
    except NameError:
        return 'Person not found', True, None

prevRectUtilitiesObj = PrevRectUtilities()
