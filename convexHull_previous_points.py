import cv2
import numpy as np
import sys
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np


cap = cv2.VideoCapture('/home/stephen/Desktop/trickcrop.MP4')

out = cv2.VideoWriter('/home/stephen/Desktop/test.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 60, (720,720))




max_ball_size = 130
min_ball_size = 60
locations, areas = [], []
frame_number = 0
while True:
    
    ret, src = cap.read()
    if not ret: break
    
    # convert image to gray scale
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
     
    # blur the image
    blur = cv2.blur(gray, (3, 3))
    
    # binary thresholding of the image
    ret, thresh = cv2.threshold(blur, 170, 255, cv2.THRESH_BINARY)
    
    # find contours
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, \
            cv2.CHAIN_APPROX_SIMPLE)
    
    # create hull array for convexHull points
    hull = []
    
    # calculate points for each contour
    for i in range(len(contours)):
        hull.append(cv2.convexHull(contours[i], False))
    
    # create an empty black image
    drawing = np.zeros((thresh.shape[0], thresh.shape[1], 3), np.uint8)
    
    # draw contours and hull points
    for i in range(len(contours)):
        color_contours = (0, 255, 0) # color for contours
        color = (234, 25, 255) # color for convex hull
        # draw convex hull
        cv2.drawContours(src, hull, i, color, 2, 1)
        # draw contours
        contour_area = cv2.contourArea(contours[i])
        if contour_area>min_ball_size and contour_area<max_ball_size:
            areas.append(contour_area)
            locations.append((cv2.minEnclosingCircle(contours[i])[0], frame_number))
            cv2.drawContours(src, contours, i, color_contours, -1, 0, hierarchy)
    for point in locations:
        tail_length = 16
        if frame_number - point[1] < tail_length:
            cv2.circle(src, (int(point[0][0]), int(point[0][1])), (tail_length+point[1] - frame_number)/4, color_contours, -1)
            
            
        

    #cv2.imshow("Output", (cv2.addWeighted(drawing, .5, src, .5, 1)))
    cv2.imshow("img", src)
    out.write(src)
    frame_number+=1

    k = cv2.waitKey(1)
    if k == 27: break
cv2.destroyAllWindows()

##fig = plt.figure()
##ax = fig.add_subplot(111, projection='3d')

xs = np.array(zip(*zip(*locations)[0])[0])
ys = -np.array(zip(*zip(*locations)[0])[1]) + 350
zs = np.array(zip(*locations)[1])

##ax.scatter(xs, ys, zs, c='b', marker='o')
##
##ax.set_xlabel('X Label')
##ax.set_ylabel('Y Label')
##ax.set_zlabel('Z Label')
plt.scatter(zs,ys)
plt.show()
