import cv2, numpy as np

#path to source video
source_path = '/home/stephen/Desktop/hs1.mp4'
#out path to save tracking data
output_path = '/home/stephen/Desktop/1.csv'

#parameter of lk optical flow
window_size = 16
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

#capture the source video
cap = cv2.VideoCapture(source_path)

#initialize frame_number
frame_number = 0
wait_time = 0

#fit frame to screen
#this makes entering manual input so much easier
screen_factor = 1
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
