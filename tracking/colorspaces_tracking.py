# Import libraries
import cv2, numpy as np

# H,S,V range of the object to be tracked

h,s,v,h1,s1,v1 = 0,184,128,20,255,255 #RED

# Find these values using hsv_color_picker.py
#h,s,v,h1,s1,v1 = 156,74,76,166,255,255 #pink
#h,s,v,h1,s1,v1 = 27,0,0,82,190,255 #GREEN

# Define data's output path
output_path = '/home/stephen/Desktop/red_ball.csv'

# Define the source path
cap = cv2.VideoCapture('/home/stephen/Desktop/source_vids/ss3_id_16.MP4')

# Takes image and color, returns parts of image that are that color
def only_color(frame, hsv_range):
    (b,r,g,b1,r1,g1) = hsv_range
    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # define range of blue color in HSV
    lower = np.array([b,r,g])
    upper = np.array([b1,r1,g1])
    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower, upper)
    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(frame,frame, mask= mask)
    return res, mask

#finds the largest contour in a list of contours
#returns a single contour
def largest_contour(contours):
    c = max(contours, key=cv2.contourArea)
    return c[0]

#takes an image and the threshold value returns the contours
def get_contours(im, threshold_value):
    imgray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    _ ,thresh = cv2.threshold(imgray,0,255,0)
    _, contours, _ = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    return contours

#finds the center of a contour
#takes a single contour
#returns (x,y) position of the contour
def contour_center(c):
    M = cv2.moments(c)
    try: center = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
    except: center = 0,0
    return center

# Create list to save data
frame_number, positions = 0, []

# Iterate though each frame of video
while True:
    
    # Read image from the video
    _, img = cap.read()
    

    # Chech if the video is over
    try: l = img.shape
    except: break

    img_copy = img.copy()
    
    # Segment the image by color
    img, mask = only_color(img, (h,s,v,h1,s1,v1))

    # Find the contours in the image
    contours = get_contours(img, 0)

    # If there are contours found in the image:
    if len(contours)>0:
        try:
            # Sort the contours by area
            c = max(contours, key=cv2.contourArea)
            # Draw the contours on the image
            img = cv2.drawContours(img_copy, c ,-1, (0,0,255), 14)
            # Add the data from the contour to the list
            positions.append(contour_center(c))
        except: pass

    # If no data point got added, add another one
    if len(positions) < frame_number: positions.append((0,0))
    frame_number += 1
    #show the image and wait
    cv2.imshow('img', img_copy)
    #cv2.imshow('img', cv2.resize(img, (480,700)))
    k=cv2.waitKey(1)
    if k==27: break
    
#release the video to avoid memory leaks, and close the window
cap.release()
cv2.destroyAllWindows()

#remove unused parts of the list
positions = positions[:frame_number]

print('finished tracking')
#write data
import csv
with open(output_path, 'w') as csvfile:
    fieldnames = ['x_position', 'y_position']
    writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
    writer.writeheader()
    for position in positions:
        x, y = position[0], position[1]
        writer.writerow({'x_position': x, 'y_position': y})

print('finished writing data')
