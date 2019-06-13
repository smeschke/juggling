import cv2, math
import numpy as np
import pandas as pd
import scipy
from scipy import signal

# Read data and video
path = 'ss5_id_321'
df = pd.read_csv('/home/stephen/Desktop/'+path+'.csv')
cap = cv2.VideoCapture('/home/stephen/Desktop/'+path+'.MP4')
# Create video out file
w,h = 480,848
vid_writer = cv2.VideoWriter('/home/stephen/Desktop/interpolated.avi',
                             cv2.VideoWriter_fourcc('M','J','P','G'),
                             30, (w,h))

def dist(a,b): return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

# Smooth out the data
smoothed_data = []
window_length, polyorder = 3, 2
for i in range(int(len(df.columns)/2)):
    #x = signal.savgol_filter(df[df.columns[i*2]], window_length, polyorder)
    #y = signal.savgol_filter(df[df.columns[i*2+1]], window_length, polyorder)
    y = df[df.columns[i*2+1]]
    x = df[df.columns[i*2]]
    smoothed_data.append(list(zip(x,y)))

# Make a list for the interpolated positions
positions = []
# Iterate through each frame in the video
for frame_number in range(len(smoothed_data[0])-1):
    frame_positions = []
    frame_positions_interpolate = []
    # Iterate through each ball in the data
    for ball_number in range(len(smoothed_data)):
        # Get the first point
        a = smoothed_data[ball_number][frame_number]
        # Get the second point
        b = smoothed_data[ball_number][frame_number+1]
        # Find the midpoint
        a_b = (a[0]+b[0])/2, (a[1]+b[1])/2
        frame_positions.append(a[0])
        frame_positions.append(a[1])
        frame_positions_interpolate.append(a_b[0])
        frame_positions_interpolate.append(a_b[1])
    positions.append(frame_positions)
    positions.append(frame_positions_interpolate)

# Write the data to a .csv file
df = pd.DataFrame(np.array(positions))
df.to_csv('/home/stephen/Desktop/interpolated.csv', index = False)

# Read source video
_, img = cap.read()
p_img = np.zeros_like(img)

# Iterate through each frame in the source video
while True:
    # Creat a blended image blend_image that is between img and p_img
    blend_image = cv2.addWeighted(img, .5, p_img, .5, 1)
    # Write the blended image
    vid_writer.write(blend_image)
    cv2.imshow('img', blend_image)
    k = cv2.waitKey(1)
    # Write the image that comes after the blended image
    vid_writer.write(img)
    cv2.imshow('img', img)
    k = cv2.waitKey(1)
    if k == 27: break
    # Save the previous frame (for blending)
    p_img = img.copy()
    # Read the next frame (unless the video is over)
    _, img = cap.read()
    try: d = img.shape
    except: break    

cv2.destroyAllWindows()
