import cv2, numpy as np, math

#-----------------------REQUREMENTS------------------------
#
#  OPENCV 3 or 4 - https://www.learnopencv.com/install-opencv-4-on-ubuntu-18-04/
#
#  PYTHON 3
#
#  NUMPY - https://scipy.org/install.html
#
#  TESTED ON UBUNTU 18

#-----------------------INSTRUCTIONS-----------------------
#
#  CONFIGURE THE PARAMETERS (see below)
#
#  RUN THE SCRIPT
#
#  A WINDOW WILL APPEAR
#
#  CLICK ON THE OBJECT YOU WANT TO TRACK
#
#  PRESS  'F5'
#
#  THE OBJECT YOU SELECTED WILL BE TRACKED
#
#  PRESS 'F6' TO CONTINUE TO THE NEXT FRAME
#
#  IF YOU WANT TO RESET THE TRACKER, CLICK ON THE SCREEN
#  THEN PRESS 'F5'
#
#  IF YOU HAVE GREAT FAITH IN THE TRACKER, PRESS 'F7'
#  OR ACCEPT YOUR 'F8' (the fastest tracking speed)
#
#  PRESS 'F6' AT ANY TIME IF THE TRACKER IS LOST
#
#  ONCE THE VIDEO IS PAUSED, RESET THE TRACKER WITH A MOUSE CLICK
#  AND THEN PRESS 'F5'
#
#-----------------------TO CONFIGURE PARAMETERS------------
#
#
# Several parameters need to be entered for the tracker to work correctly:
#
# window_size - should be slightly larger than the object being tracked The size of this parameter is represented by the size of the blue circle
window_size = 28
#
# source_path - path to source video
source_path = '/home/stephen/Desktop/olsen/olsen.mp4'
#
# output_path to save tracking data
output_path = '/home/stephen/Desktop/2.csv'
#
# When does the tracker need to be reset?
# There is a maximum distance that the ball can travel between seccessive frames.
# If the detected location in the next frame is greater than the max distance,
# the tracker must have gotten lost. Usual range is 50 to 80
# lower means more predictable
max_distance = 90
#
# THE FOLLOWING PARAMETERS DEPEND ON VIDEO RESOLUTION AND MONITOR SIZE
# fit frame to screen
# pick a number around 1 and 2
screen_factor = 1.5
# makes the roi easier to see
# makes manual input easier
# pick around 2
roi_factor = 4 
#define the size of the roi
# try to get: roi_factor * roi_size = monitor resolution
roi_size = 200


#parameter of lk optical flow, don't mess with these
lk_params = dict(winSize = (window_size,window_size),
                 maxLevel = 5,
                 criteria = (cv2.TERM_CRITERIA_EPS |
                             cv2.TERM_CRITERIA_COUNT, 5, 0.03))
#-------------------------END OF PARAMETERS-------------------------

#mouse callback function
global click_list
positions, click_list = [], []

def callback(event, x, y, flags, param):
    if event == 1: click_list.append((x,y))
cv2.namedWindow('img')
cv2.setMouseCallback('img', callback)

def distance(a,b): return math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)

def max_distance_failure(a,b):
    is_failure = False
    if distance(a,b)> max_distance: is_failure = True
    if is_failure: print(is_failure, distance(a,b))
    return is_failure

#capture the source video
cap = cv2.VideoCapture(source_path)

#initialize frame_number
frame_number, k = 0, -1
wait_time = 0
font, scale, color, thick = cv2.FONT_HERSHEY_SIMPLEX, .8, (234,234,234), 2

#create a value for the tracker to track
#this will be reset by the user after the frist frame
#p0 is the locatin of the tracked object in the previous frame
p0 = np.array([[[0,0]]], np.float32)

#main loop
while True:
    #read frame of video
    _, img = cap.read()
    try:h,w,e = img.shape
    except: break
    img = cv2.resize(img, (int(w*screen_factor), int(h*screen_factor)))
    try: old_gray = img_gray.copy()
    except: old_gray  =cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    try: img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    except: break

    #try and track using optical flow
    p1, _, _ = cv2.calcOpticalFlowPyrLK(old_gray, img_gray,p0, None, **lk_params)

    #convert the coordinates to integers
    xy  = int(p1[0][0][0]), int(p1[0][0][1])

    # check for a max distance failure
    if max_distance_failure(p0[0][0], p1[0][0]):
        wait_time = 0 #stop the tracker
        p1 = p0 # get rid of the erronious tracker value
        xy  = int(p1[0][0][0]), int(p1[0][0][1])
    else: p0 = p1 #update p0 to p1

    #make circle around object to show trackin gpoint   
    cv2.circle(img, xy, window_size, (255,2,1), 1)
    
    #show the roi
    #--create background image
    bg = np.zeros((img.shape[0]+roi_size, img.shape[1]+roi_size, 3), np.uint8)
    bg[int(roi_size/2):int(roi_size/2)+img.shape[0], int(roi_size/2):int(roi_size/2)+img.shape[1]] = img
    roi = bg[xy[1]:xy[1]+roi_size, xy[0]:xy[0]+roi_size]
    #create crosshairs on roi
    cv2.line(roi, (int(roi_size/2),0), (int(roi_size/2),roi_size), (123,234,123), 1)
    cv2.line(roi, (0,int(roi_size/2)), (roi_size,int(roi_size/2)), (123,234,123), 1)
    #resize roi to make it easier to see
    roi = cv2.resize(roi, (roi_size*roi_factor, roi_size*roi_factor))

    if wait_time == 0:
        if k == 194:            
            cv2.putText(roi, "TRACKER HAS BEEN RESET", (50,50), font, scale, color, thick, cv2.LINE_AA)
            cv2.putText(roi, "TRACKER IS PAUSED", (50,75), font, scale, color, thick, cv2.LINE_AA)
            cv2.putText(roi, "click on the screen then press 'F5' to reset tracker.", (50,100), font, scale, color, thick, cv2.LINE_AA)
            cv2.putText(roi, "OR press 'F6' to continue tracking to next frame.", (50,125), font, scale, color, thick, cv2.LINE_AA)
            cv2.putText(roi, "OR press 'F7' to continue tracking on play.", (50,150), font, scale, color, thick, cv2.LINE_AA)
        else:
            cv2.putText(roi, "TRACKER IS PAUSED", (50, 50), font, scale, color, thick, cv2.LINE_AA)
            cv2.putText(roi, "click on the screen then press 'F5' to reset tracker.", (50,75), font, scale, color, thick, cv2.LINE_AA)
            cv2.putText(roi, "OR press 'F6' to continue tracking the next frame.", (50,100), font, scale, color, thick, cv2.LINE_AA)
            cv2.putText(roi, "OR press 'F7' to continue tracking on play.", (50,125), font, scale, color, thick, cv2.LINE_AA)
    else:
        cv2.putText(roi, "Press 'F6 to pause the video", (50,50), font, scale, color, thick, cv2.LINE_AA)
    
    
     
    #show frame and wait
    #if this is the first frame, get a click from the image
    if len(positions) == 0:
        cv2.putText(img, "CLICK ON OBJECT TO BE TRACKED", (50,50), font, scale, color, thick, cv2.LINE_AA)
        cv2.putText(img, "THEN PRESS 'F5'", (50,75), font, scale, color, thick, cv2.LINE_AA)
        cv2.imshow('img', img)
    else:
        cv2.imshow('img', roi)
    k = cv2.waitKey(wait_time)
    if k ==27: break
    if k == 195: #F6
        wait_time = 0
        
    if k == 196: #F7
        wait_time = 100
        
    if k == 197: #F8
        wait_time = 1
    #if the user has presses 's', resset the tracking location
    if k == 194: #F5
        user_input = click_list[-1]
        #if the user input is in the roi_frame, convert the coordinates to be in the img frame
        if len(positions) > 0:
            #convert clicks from xy in the roi_frame to the xy in the img frame
            user_input = xy[0]+user_input[0]/roi_factor, xy[1]+user_input[1]/roi_factor
            user_input = user_input[0]-int(roi_size/2), user_input[1]-int(roi_size/2)            
        p0 = np.array([[user_input]], np.float32)
        xy = user_input
        wait_time = 0    

    #add tracked location to data
    positions.append((int(xy[0]/screen_factor),int(xy[1]/screen_factor)))

cv2.destroyAllWindows()
cap.release()

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

print ('finished writing data')
