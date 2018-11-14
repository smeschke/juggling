import cv2, math, numpy as np

#h,s,v range of the object to be tracked
color_values = 42,91,73,88,221,151
color_values = 104,148,66,120,255,161
color_values = 156,65,84,189,192,204 #andrew olsen pink
color_values = 100,60,50,170,255,185 #pink
#color_values = 19,37,151,50,206,255 # yellow
#color_values = 105,130,0,130,228,128 #blue
#color_values = 50,38,101,83,204,255 #green
#color_values = 19,0,218,255,241,255
color_values = 142,106,43,159,255,146
color_values = 120,113,60,167,255,255
color_values = 120,110,0,193,255,255
#color_values = 128,127,24,169,241,255
threshold_value = 0

# When does the tracker need to be reset?
# There is a maximum distance that the ball can travel between seccessive frames.
# If the detected location in the next frame is greater than the max distance,
# the tracker must have gotten lost.
max_distance = 35

# how big is a ball? This will affect snapping
#13 is good
ball_size = 15
contour_ball_size = 30

# how far can the snap be applied?
global max_snap_distance
max_snap_distance = 9


output_path = '/home/stephen/Desktop/data/5.csv'

cap = cv2.VideoCapture('/home/stephen/Desktop/trick_1up4up_id_150.MP4')

p_imgs, history_length, history_idx = [], 80, 0

#takes an image, and a lower and upper bound
#returns only the parts of the image in bounds
def only_color(frame, color_valeus, p_position):
    mask = np.zeros((frame.shape[0], frame.shape[1]), np.uint8)
    mask = cv2.circle(mask, p_position, max_snap_distance, 255, -1)
    frame = cv2.bitwise_and(frame, frame, mask=mask)
    #cv2.imshow('temp mask', frame)
    #cv2.waitKey(0)
    
    
    b,r,g,b1,r1,g1 = color_values
    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # define range of blue color in HSV
    lower = np.array([b,r,g])
    upper = np.array([b1,r1,g1])
    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower, upper)
    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(frame,frame, mask= mask)
    #cv2.imshow('mask', mask)
    return res, mask

#finds the largest contour in a list of contours
#returns a single contour
def largest_contour(contours):
    c = max(contours, key=cv2.contourArea)
    return c[0]

#takes an image and the threshold value returns the contours
def get_contours(im, threshold_value):
    imgray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    _ ,thresh = cv2.threshold(imgray,threshold_value,255,0)
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

def find_ball_by_color(img, color_values, ball_position):
    img, mask = only_color(img, color_values, ball_position)
    
    #find the contours in the image
    contours = get_contours(img, threshold_value)
    #if there are contours found in the image:
    nearest_ball = 23456789
    nearest_snap_possibility = (9876,9867)
    #iterate through the contours
    for contour in contours:
        # check if a contour is big enough to be considered a ball
        if cv2.contourArea(contour)>contour_ball_size:
            center = contour_center(contour)
            #print(center)
            # if this contour is the nearest one to the ball, it is the most likely snap position
            if distance(center, ball_position) < nearest_ball:
                nearest_snap_possibility = center
    return nearest_snap_possibility

def distance(a,b): return math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)

def max_distance_failure(a,b):
    is_failure = False
    if distance(a,b)> max_distance:
        is_failure = True
        print("Max distance failure: ", distance(a,b))
    return is_failure

#parameter of lk optical flow
lk_params = dict(winSize = (ball_size, ball_size),
                 maxLevel = 5,
                 criteria = (cv2.TERM_CRITERIA_EPS |
                             cv2.TERM_CRITERIA_COUNT, 5, 0.03))

#mouse callback function
global click_list
positions, click_list = [], []

def callback(event, x, y, flags, param):
    if event == 1: click_list.append((x,y))
cv2.namedWindow('img')
cv2.setMouseCallback('img', callback)

#initialize frame_number
frame_number = 0
wait_time = 0

#fit frame to screen
#this makes entering manual input so much easier
screen_factor = 1
#get a bigger monitor

#define the size of the roi
roi_size = 800
roi_factor = 1 #makes the roi easier to see

#create a value for the tracker to track
#this will be reset by the user after the frist frame
#p0 is the locatin of the tracked object in the previous frame
p0 = np.array([[[0,0]]], np.float32)


#main loop
while True:
    #read frame of video
    if history_idx == 0:
        _, img = cap.read()
        p_imgs.append(img)
    else:
        img = p_imgs.pop(0)
        history_idx -= 1
    try:h,w,e = img.shape
    except: break
    img = cv2.resize(img, (int(w*screen_factor), int(h*screen_factor)))
    try: old_gray = img_gray.copy()
    except: old_gray  =cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    try: img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    except: break

    # draw the previous ball positions on the screen
    try:
        for idx in range(35):
            a = positions[-(idx+2)][0]* screen_factor, positions[-(idx+2)][1]*screen_factor
            b = positions[-(idx+1)][0]* screen_factor, positions[-(idx+1)][1]*screen_factor
            cv2.line(img, a,b, (0,255,255), 3)
    except: pass    


    #try and track using optical flow
    p1, _, _ = cv2.calcOpticalFlowPyrLK(old_gray, img_gray,p0, None, **lk_params)

    #convert the coordinates to integers
    xy  = int(p1[0][0][0]), int(p1[0][0][1])

    #get the ball location by color and compare it to xy, if it is close, snap it to the color
    snap_position = find_ball_by_color(img, color_values, xy)
    #print (xy, snap_position)
    cv2.circle(img, snap_position, 20, (255,255,0), 1)
    if distance(snap_position, xy) < max_snap_distance:
        xy = snap_position
        #print("snap position")
        p1 = np.array([[[snap_position[0], snap_position[1]]]], np.float32)

    # check for a max distance failure
    if max_distance_failure(p0[0][0], p1[0][0]):
        wait_time = 0 #stop the tracker
        p1 = p0 # get rid of the erronious tracker value
        xy  = int(p1[0][0][0]), int(p1[0][0][1])
    else: p0 = p1 #update p0 to p1
    

    #make circle around object to show trackin gpoint    
    cv2.circle(img, xy, ball_size, (255,2,1), 1)

    #show the roi
    #--create background image
    bg = np.zeros((img.shape[0]+roi_size, img.shape[1]+roi_size, 3), np.uint8)
    bg[int(roi_size/2):int(roi_size/2)+img.shape[0], int(roi_size/2):int(roi_size/2)+img.shape[1]] = img
    roi = bg[xy[1]:xy[1]+roi_size, xy[0]:xy[0]+roi_size]
    #create crosshairs on roi
    cv2.line(roi, (int(roi_size/2),0), (int(roi_size/2),roi_size), (123,234,123), 1)
    cv2.line(roi, (0,int(roi_size/2)), (roi_size,int(roi_size/2)), (123,234,123), 1)
    #resize roi to make it easier to see
    try: roi = cv2.resize(roi, (roi_size*roi_factor, roi_size*roi_factor))
    except: roi = proi.copy()
    proi = roi.copy()
        
    #show frame and wait
    #if this is the first frame, get a click from the image
    if len(positions) == 0:
        cv2.imshow('img', img)
    else:
        cv2.imshow('img', roi)
        #cv2.imshow('roi', mask)
    k = cv2.waitKey(wait_time)
    if k ==27: break
    if k == 195: wait_time = 0
    if k == 196: wait_time = 25
    if k == 197: wait_time = 1
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

    
    if len(p_imgs)>history_length: p_imgs.pop(0)
    if k < 194 and k >10:
        wait_time = 0
        history_idx = history_length
        positions = positions[:-history_length]

cv2.destroyAllWindows()
cap.release()

print ('finished tracking')

#write data
import csv
with open(output_path, 'w') as csvfile:
    fieldnames = ['x_position', 'y_position']
    writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
    writer.writeheader()
    for position in positions:
        x, y = position[0], position[1]
        writer.writerow({'x_position': x, 'y_position': y})

print( 'finished writing data')
