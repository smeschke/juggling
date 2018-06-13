import cv2
import numpy as np


vid_writer = cv2.VideoWriter('/home/stephen/Desktop/peter_every_out.avi',
                             cv2.VideoWriter_fourcc('M','J','P','G'),
                             60, (620,1000))


#read tracking data from file
import csv
positions1 = []
with open('/home/stephen/Desktop/trick_5bHalfShower_id_85.csv', 'r') as csvfile:
    data = csv.reader(csvfile)
    for row in data:
        try: x,y = int(row[0]), int(row[1])
        except: x,y = 0,0
        positions1.append((x,y))
##positions2 = []
##with open('/home/stephen/Desktop/2.csv', 'r') as csvfile:
##    data = csv.reader(csvfile)
##    for row in data:
##        try: x,y = int(row[0]), int(row[1])
##        except: x,y = 0,0
##        positions2.append((x,y))
##positions3 = []
##with open('/home/stephen/Desktop/3.csv', 'r') as csvfile:
##    data = csv.reader(csvfile)
##    for row in data:
##        try: x,y = int(row[0]), int(row[1])
##        except: x,y = 0,0
##        positions3.append((x,y))
##positions4 = []
##with open('/home/stephen/Desktop/4.csv', 'r') as csvfile:
##    data = csv.reader(csvfile)
##    for row in data:
##        try: x,y = int(row[0]), int(row[1])
##        except: x,y = 0,0
##        positions4.append((x,y))


#read source video
cap = cv2.VideoCapture('/home/stephen/Desktop/IMG_1230.MOV')


#start counting by frame number
frame_number = 0
while True:
    _, img = cap.read()
    #_, img1 = cap.read()
    #img = cv2.addWeighted(img, .5, img1, .5, 1)
    #try: img = np.zeros_like(img)
    try: d = img.shape
    except: break
    tail_length = 20
    for i in range(tail_length):
        
        cv2.circle(img, positions1[frame_number-i], tail_length-i, (255,0,0), -1)
        #cv2.circle(img, positions2[frame_number], 20, (0,255,0), -1)
        #cv2.circle(img, positions3[frame_number], 20, (0,0,255), -1)
        #cv2.circle(img, positions4[frame_number], 10, (255,123,0), 5)
        #cv2.line(img, positions1[frame_number], positions2[frame_number], (234,12,12), 2)
        #cv2.line(img, positions3[frame_number], positions4[frame_number], (12,12,234), 2)
        
    cv2.imshow('image',img)
    k = cv2.waitKey(1)
    if k == 27: break
    

    frame_number += 1
    vid_writer.write(img)
    
cv2.destroyAllWindows()


    
