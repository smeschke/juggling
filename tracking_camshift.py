import numpy as np
import cv2
cap = cv2.VideoCapture('/home/stephen/Desktop/ss663_id_82.MP4')
#stuff for the mouse callback function
global click_list
click_list = []

#create list to store tracked positions
#positions[x] = the location of the tracked object in frame x
positions = []
for i in range(100000): positions.append((0,0))
#make mouse callback function
def callback(event, x, y, flags, param):
    #if the event is a left button click
    if event == 1: click_list.append((x,y))
cv2.namedWindow('img')
cv2.setMouseCallback('img', callback)

#get initial tracking window
# take first frame of the video
ret,frame = cap.read()
cv2.imshow('img', frame)
cv2.waitKey(0)
c,r = click_list[-2]
a,b = click_list[-2], click_list[-1]
h = b[1]-a[1]
w = b[0]-a[0]
track_window = (c,r,w,h)

#get the roi_hist
def get_roi_hist(frame, c,r,w,h):    
    roi = frame[r:r+h, c:c+w]
    hsv_roi =  cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_roi, np.array((0., 60.,32.)), np.array((180.,255.,255.)))
    roi_hist = cv2.calcHist([hsv_roi],[0],mask,[180],[0,180])
    cv2.normalize(roi_hist,roi_hist,0,255,cv2.NORM_MINMAX)
    return roi_hist

roi_hist = get_roi_hist(frame, c,r,w,h)

# Setup the termination criteria, either 10 iteration or move by atleast 1 pt
term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 15, 1 )

while(1):
    ret ,frame = cap.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    dst = cv2.calcBackProject([hsv],[0],roi_hist,[0,180],1)
    # apply meanshift to get the new location
    ret, track_window = cv2.CamShift(dst, track_window, term_crit)
    # Draw it on image
    pts = cv2.boxPoints(ret)
    pts = np.int0(pts)
    img2 = cv2.polylines(frame,[pts],True, 255,2)
    cv2.imshow('img',img2)
    k = cv2.waitKey(60) & 0xff
    if k == 27:
        break
    print (track_window[2]*track_window[3])
    if k == 115 or track_window[2]*track_window[3]>1500:
        cv2.waitKey(0)
        c,r = click_list[-2]
        a,b = click_list[-2], click_list[-1]
        h = b[1]-a[1]
        w = b[0]-a[0]
        track_window = (c,r,w,h)
        roi_hist = get_roi_hist(frame, c,r,w,h)
        print (a,b)
cv2.destroyAllWindows()
cap.release()
