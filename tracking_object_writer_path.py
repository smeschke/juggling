import cv2, math, numpy as np, pandas as pd, scipy
from scipy import signal

path = 'trick_5bhalfshower_id_994'
source_path = '/home/stephen/Desktop/' + path + '.MP4'
data_path = '/home/stephen/Desktop/' + path + '.csv'
# Smoothing parameters
window_length, polyorder = 27, 2
# List of colors
colors = (255,255,0),(0,255,255),(255,0,255),(0,255,0),(0,0,255), (255,0,255), (255,123,0),(0,255,123),(255,0,123),(123,0,255),(123,0,123),(0,0,255),(255,0,0), (0,255,0), (255,123,0),(0,255,123),(255,255,0),(255,0,255),(0,255,255),(0,0,255),(255,0,0), (0,255,0), (255,123,0),(0,255,123),(255,255,0),(255,0,255),(0,255,255),(0,0,255),(255,0,0), (0,255,0), (255,123,0),(0,255,123)
# Parameters for animation
tail_length = 34
tail_thickness = 15/tail_length
hw = 720 #780, 848
vid_writer = cv2.VideoWriter('/home/stephen/Desktop/writer.avi',
                             cv2.VideoWriter_fourcc('M','J','P','G'),
                             120, (480,848))

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
    smoothed_data.append(list(zip(x,y)))

import math
def distance(a,b): return math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)

pairs = [[0,2]]#,[1,3],[2,4],[3,0],[4,1]]

outreach = 35
near_dist = 2
for i in range(outreach): _,_ = cap.read()

# Start counting by frame number
frame_number = outreach
# Iterate through each frame of video
while True:
    _, img = cap.read()
    graph = np.zeros_like(img)
    # Break out if the video is over
    try: img.shape
    except: break
    
    for pair in pairs:
        ball0 = smoothed_data[pair[0]]
        ball1 = smoothed_data[pair[1]]    
        b1 = ball1[frame_number-10:frame_number + outreach]
        b0 = ball0[frame_number-outreach:frame_number+10]
        
        cv2.circle(graph, tuple(np.array(b1[10], int)), 10, (0,255,255),-1)
        cv2.circle(graph, tuple(np.array(b0[-10], int)), 10, (255,255,0),-1)
        for position in range(len(b1)-1):
            a,b = b1[position], b1[position+1]
            a,b = tuple(np.array(a, int)), tuple(np.array(b, int))
            cv2.line(graph, a, b, (0,255,255), 3)
        for position in range(len(b1)-1):
            a,b = b0[position], b0[position+1]
            a,b = tuple(np.array(a, int)), tuple(np.array(b, int))
            cv2.line(graph, a, b, (255,255,0), 3)
        no_path = graph.copy()
        
       
                    
        ball_positions = b1 + b0
        x,y = zip(*ball_positions)
        window_length = int(len(x)*.5)
        if window_length//2 == window_length/2: window_length -= 1
        if window_length <3: polyorder = window_length-1
        x = signal.savgol_filter(x, window_length, polyorder)
        y = signal.savgol_filter(y, window_length, polyorder)
        ball_positions = list(zip(x,y))
        for position in range(len(ball_positions)-1):
            a,b = ball_positions[position], ball_positions[position+1]
            a,b = tuple(np.array(a, int)), tuple(np.array(b, int))
            cv2.line(img, a, b, colors[pairs.index(pair)], 4)
            cv2.line(graph, a, b, (255,0,255), 2)

    bg = np.zeros((848,848,3), np.uint8)
    bg[:,:,:] = 123,123,123
    bg[:,180:180+480] = img
    img = bg
    if hw == 780: img = img[848-780:848, 0+30:30+780] # for 780 top
    if hw == 720: img = img[780-720:780, 0+50:50+720] #for 720x bottom
    
    # Show the image and wait
    cv2.imshow('image',img)
    cv2.imshow('graph',graph)  
    
    vid_writer.write(graph)
    imgcc = img.copy()
    k = cv2.waitKey(1)
    if k == 115:
        cv2.imwrite('/home/stephen/Desktop/path.png', graph)
        cv2.imwrite('/home/stephen/Desktop/no_path.png', no_path)
    if k == 27: break
    
    # Increment frame number
    frame_number += 1
    
cv2.destroyAllWindows()
cap.release()
