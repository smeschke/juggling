import cv2, math
import numpy as np
import pandas as pd
import scipy
from scipy import signal

# Read tracking data from file
distances = []

# Get pose data from the spreadsheet
source_path = '/home/stephen/Desktop/source_data/ss77772_id_121.csv'
df = pd.read_csv(source_path)

# Define the image scale
img_scale = 10
buffer = 200

# Smooth it out (column by column)
window_length, polyorder = 17, 2
for i in range(int(len(df.columns)/2)):
    df[df.columns[i*2]] = signal.savgol_filter(df[df.columns[i*2]], window_length, polyorder) * img_scale
    df[df.columns[i*2+1]] = signal.savgol_filter(df[df.columns[i*2+1]], window_length, polyorder) * img_scale

# List of colors
colors = (0,255,255), (255,0,255),(255,255,0), (123,123,255), (123,255,123), (255,123,123), (255,0,0),(0,255,0),(0,0,255)

# Get the max height of the data
max_height = int(max(list(df[df.columns].max())))
# Get the minimum height
min_height = int(min(list(df[df.columns].min())))
# Calculate image height]
img_height = (max_height-min_height) + buffer*2
# Get the length of the data
length = len(df[df.columns[0]].values)*img_scale
# Create image to draw on
img = np.zeros((img_height,length,3), np.uint8)
img[:,:,:] = 67,67,67

# Graph the data
idx = 0
for i in range(int(len(df.columns)/2)):
    color = colors[idx]
    y = df[df.columns[i*2+1]]
    x = df[df.columns[i*2]]
    for frame in range(len(y.values)-1):
        a = frame*img_scale, int(y[frame]) + buffer - min_height
        b = (frame+1)*img_scale, int(y[frame+1]) + buffer - min_height
        cv2.line(img, a,b, color, img_scale*2)
    idx += 1   

# Blur and resize the image
img = cv2.blur(img, (int(img_scale), int(img_scale)))
h,w,_ = img.shape
img = cv2.resize(img, (int(w/img_scale), int(h/img_scale)))
# Write the name of the trick
org, font, scale, color, thick = (12,20), cv2.FONT_HERSHEY_SIMPLEX, .75, (234,234,234), 1
cv2.putText(img, "Y-T graph for " + source_path.split('/')[-1][:-4], org, font, scale, color, thick, cv2.LINE_AA)

cv2.imshow('image',img)
cv2.imwrite('/home/stephen/Desktop/graph.png', img)
k = cv2.waitKey(0)    
cv2.destroyAllWindows()


    
