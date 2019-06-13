import cv2, math
import numpy as np
import pandas as pd
import scipy
from scipy import signal

#------------------Enter these parameters------------------
# Path to source video - find here: https://drive.google.com/open?id=0B7QqDexrxSfwVXgwWlRUcDBiVFk
source_path = '/home/stephen/Desktop/ss5_id_321.MP4'
# Path to source data - find here: https://drive.google.com/open?id=0B7QqDexrxSfwVXgwWlRUcDBiVFk
data_path = '/home/stephen/Desktop/ss5_id_321.csv'
# Smoothing parameters
window_length, polyorder = 15, 2
# List of colors
colors = (255,0,255),(255,255,0),(0,255,255),(0,0,255),(255,0,0), (0,255,0), (255,123,0),(0,255,123)

# Create video writer
vid_writer = cv2.VideoWriter('/home/stephen/Desktop/test.avi',
                             cv2.VideoWriter_fourcc('M','J','P','G'),
                             60, (480,848))

# Read source video
cap = cv2.VideoCapture(source_path)

# Read data
df = pd.read_csv(data_path)
# Create list for smoothed data
smoothed_data = []
# Iterate through each column in the database
for i in range(int(len(df.columns)/2)):
    # Smooth the column
    x = signal.savgol_filter(df[df.columns[i*2]], window_length, polyorder)
    y = signal.savgol_filter(df[df.columns[i*2+1]], window_length, polyorder)
    #y = df[df.columns[i*2+1]]
    #x = df[df.columns[i*2]]
    # Add the smoothed data to the smoothed_data list
    smoothed_data.append(list(zip(x,y)))

# Start counting by frame number
frame_number = 0
# Iterate through each frame of video
while True:
    _, img = cap.read()
    img = np.zeros_like(img)
    img[:,:,:] = 123,123,123
    # Break out if the video is over
    try: img.shape
    except: break

    # Iterate though each ball in the smoothed data
    p = []
    for ball in smoothed_data:
        # Get the ball color
        color = colors[smoothed_data.index(ball)]        
        position = tuple(ball[frame_number])
        p.append(position)
    for i in range(len(p)):
        a = p[i]
        b = p[i-1]
        tt = 6
        a = int(a[0]), int(a[1])
        b = int(b[0]), int(b[1])
        cv2.line(img, a, b, colors[i], tt)
        
    # Show the image and wait                
    cv2.imshow('image',img)    
    vid_writer.write(img)
    k = cv2.waitKey(1)
    if k == 27: break
    
    # Increment frame number
    frame_number += 1
    
cv2.destroyAllWindows()
cap.release()
