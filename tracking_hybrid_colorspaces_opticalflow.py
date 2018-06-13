import cv2, math, numpy as np

#h,s,v range of the object to be tracked
color_values = 42,91,73,88,221,151
color_values = 104,148,66,120,255,161

threshold_value = 0

output_path = '/home/stephen/Desktop/blue.csv'

cap = cv2.VideoCapture('/home/stephen/Desktop/531.avi')

#takes an image, and a lower and upper bound
#returns only the parts of the image in bounds
def only_color(frame, (b,r,g,b1,r1,g1)):
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

def find_ball_by_color(img, color_values):
    img, mask = only_color(img, color_values)
    
    #find the contours in the image
    contours = get_contours(img, threshold_value)
    #if there are contours found in the image:
    if len(contours)>0:
        try:
            #sort the contours by area
            c = max(contours, key=cv2.contourArea)
            img = cv2.drawContours(img, c ,-1, (0,0,255), 14)
            return contour_center(c)
        except: return (4567,4567)
    else: return (4567,4567)

def distance(a,b): return math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)

#parameter of lk optical flow
window_size = 34
lk_params = dict(winSize = (window_size,window_size),
                 maxLevel = 5,
                 criteria = (cv2.TERM_CRITERIA_EPS |
                             cv2.TERM_CRITERIA_COUNT, 5, 0.03))

#mouse callback function
positions, click_list = [], []
global click_list
def callback(event, x, y, flags, param):
    if event == 1: click_list.append((x,y))
cv2.namedWindow('img')
cv2.setMouseCallback('img', callback)

#initialize frame_number
frame_number = 0
wait_time = 0

#fit frame to screen
#this makes entering manual input so much easier
screen_factor = 2
#get a bigger monitor

#define the size of the roi
roi_size = 400
roi_factor = 2 #makes the roi easier to see

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

    #get teh ball location by color and compare it to xy, if it is close, snap it to the color
    snap_position = find_ball_by_color(img, color_values)
    if distance(snap_position, xy)< 128:
        xy = snap_position
        p1 = np.array([[[snap_position[0], snap_position[1]]]], np.float32)

    #update p0 to p1
    p0 = p1

    #make circle around object to show trackin gpoint    
    cv2.circle(img, xy, window_size, (255,2,1), 1)

    #show the roi
    #--create background image
    bg = np.zeros((img.shape[0]+roi_size, img.shape[1]+roi_size, 3), np.uint8)
    bg[roi_size/2:roi_size/2+img.shape[0], roi_size/2:roi_size/2+img.shape[1]] = img
    roi = bg[xy[1]:xy[1]+roi_size, xy[0]:xy[0]+roi_size]
    #create crosshairs on roi
    cv2.line(roi, (roi_size/2,0), (roi_size/2,roi_size), (123,234,123), 1)
    cv2.line(roi, (0,roi_size/2), (roi_size,roi_size/2), (123,234,123), 1)
    #resize roi to make it easier to see
    roi = cv2.resize(roi, (roi_size*roi_factor, roi_size*roi_factor))
        
    #show frame and wait
    #if this is the first frame, get a click from the image
    if len(positions) == 0:
        cv2.imshow('img', img)
    else:
        cv2.imshow('img', roi)
        cv2.imshow('roi', img)
    k = cv2.waitKey(wait_time)
    if k ==27: break
    if k == 195: wait_time = 0
    if k == 196: wait_time = 100
    if k == 197: wait_time = 1
    #if the user has presses 's', resset the tracking location
    if k == 194: #F5
        user_input = click_list[-1]
        #if the user input is in the roi_frame, convert the coordinates to be in the img frame
        if len(positions) > 0:
            #convert clicks from xy in the roi_frame to the xy in the img frame
            user_input = xy[0]+user_input[0]/roi_factor, xy[1]+user_input[1]/roi_factor
            user_input = user_input[0]-roi_size/2, user_input[1]-roi_size/2            
        p0 = np.array([[user_input]], np.float32)
        xy = user_input
        wait_time = 0    

    #add tracked location to data
    positions.append((int(xy[0]/screen_factor),int(xy[1]/screen_factor)))

cv2.destroyAllWindows()
cap.release()

print 'finished tracking'

#write data
import csv
with open(output_path, 'w') as csvfile:
    fieldnames = ['x_position', 'y_position']
    writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
    writer.writeheader()
    for position in positions:
        x, y = position[0], position[1]
        writer.writerow({'x_position': x, 'y_position': y})

print 'finished writing data'
