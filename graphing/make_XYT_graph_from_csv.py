import cv2, math
import numpy as np
import pandas as pd
import scipy
from scipy import signal

# Read tracking data from file
distances = []

# Get pose data from the spreadsheet
df = pd.read_csv('/home/stephen/Desktop/663_tracking.csv')

# Smooth it out (column by column)
smoothed_data = []
window_length, exponent = 23, 2
for i in range(int(len(df.columns)/2)):
    df[str(i*2)] = signal.savgol_filter(df[str(i*2)], window_length, exponent)
    df[str(i*2+1)] = signal.savgol_filter(df[str(i*2+1)], window_length, exponent)

#list of colors
colors = (0,255,255), (0,255,255), (255,0,255), (255,0,255),(0,255,0), (255,0,255), (0,255,255), (255,255,0), (255,0,0),(0,255,0)

# Create image to draw on
# Alter these values, depending on the height of the data, and the number of frames
img = np.zeros((800,5000,3), np.uint8)

# Start with the first frame
p_values = df.values[0]
frame = 0

# Iterate though each frame
for values in df.values:
    frame_increment  = 4
    frame += frame_increment
    idx = 0
    for value, p_value in zip(values, p_values):
        color = colors[int(idx)]
        idx += .5
        # Draw only the y values (this is a YT graph)
        if list(values).index(value)%2!=0:
            cv2.line(img, (frame-frame_increment, int(p_value)), (frame, int(value)), color, 6)
    p_values = values

# Crop the image so that it looks nice
img = img[0:876, :]
cv2.imshow('image',img)
cv2.imwrite('/home/stephen/Desktop/graph.png', img)
k = cv2.waitKey(0)
    
cv2.destroyAllWindows()


    
