import cv2, math
import numpy as np
import pandas as pd
import scipy
from scipy import signal

#------------------Enter these parameters------------------
# Path to source video - find here: https://drive.google.com/open?id=0B7QqDexrxSfwVXgwWlRUcDBiVFk
source_path = '/home/stephen/Desktop/ss642_id_140.MP4'
# Path to source data - find here: https://drive.google.com/open?id=0B7QqDexrxSfwVXgwWlRUcDBiVFk
data_path = '/home/stephen/Desktop/ss642_id_140.csv'
# Smoothing parameters
window_length, polyorder = 15, 2
# List of colors
colors = (0,255,255),  (255,0,255),(255,255,0), (123,123,255), (123,255,123), (255,123,123), (255,0,0),(0,255,0)
# Parameters for animation
tail_length, tail_thickness = 15, .8

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
    # Add the smoothed data to the smoothed_data list
    smoothed_data.append(list(zip(x,y)))

# Start counting by frame number
frame_number = 0
# Iterate through each frame of video
while True:
    _, img = cap.read()
    # Break out if the video is over
    try: img.shape
    except: break

    # Iterate though each ball in the smoothed data
    for ball in smoothed_data:

        # Get the ball color
        color = colors[smoothed_data.index(ball)]
        
        # Iterate though each frame in tail length
        for tail in range(tail_length):
            # Get the ball position as tuple, so like: (x,y)
            position = tuple(ball[frame_number-tail])
            position = int(position[0]), int(position[1])
            # Get the ball position from the previous frame
            previous_position = tuple(ball[frame_number-(tail+1)])
            previous_position = int(previous_position[0]), int(previous_position[1])
            # Avoid looping from the front to the back of the list
            if tail+1-frame_number<0 and int((tail_length-tail)*tail_thickness)>0:                
                # Draw the line                
                cv2.line(img, position, previous_position, color, int((tail_length-tail)*tail_thickness))

    # Show the image and wait                
    cv2.imshow('image',img)
    k = cv2.waitKey(1)
    if k == 27: break
    
    # Increment frame number
    frame_number += 1
    
cv2.destroyAllWindows()
cap.release()
