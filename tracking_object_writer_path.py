import cv2, math, numpy as np, pandas as pd, scipy
from scipy import signal

path = 'ss9151_id_993'
source_path = '/home/stephen/Desktop/' + path + '.MP4'
data_path = '/home/stephen/Desktop/' + path + '.csv'

path = 'ss5_id_412'
source_path = '/home/stephen/Desktop/source_video/' + path + '.MP4'
data_path = '/home/stephen/Desktop/tracking_data/' + path + '.csv'

outreach = 35
min_frames = 20
#pairs = [[0,2],[1,3],[2,4],[3,0],[4,1]]
#pairs = [[0,1],[1,2],[2,0]]#,[3,0],[4,1]]
#pairs = [[0,2],[1,3],[2,4],[3,5],[4,6],[5,0],[6,1]]
#pairs = [[0,2],[1,3],[2,0],[3,1]]
import itertools
pairs = list(itertools.permutations([0,1,2,3,4], 2))

# Smoothing parameters
window_length, polyorder = 27, 2
# List of colors
colors = (255,255,0),(0,255,255),(255,0,255),(0,255,0),(0,0,255), (255,0,0), (255,123,0),(0,255,123),(255,0,123),(123,0,255),(123,0,123),(0,0,255),(255,0,0), (0,255,0), (255,123,0),(0,255,123),(255,255,0),(255,0,255),(0,255,255),(0,0,255),(255,0,0), (0,255,0), (255,123,0),(0,255,123),(255,255,0),(255,0,255),(0,255,255),(0,0,255),(255,0,0), (0,255,0), (255,123,0),(0,255,123)
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

def distance(a,b): return math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)

for i in range(outreach): _,_ = cap.read()

# Start counting by frame number
frame_number = outreach
# Iterate through each frame of video
while True:
    _, img = cap.read()
    graph = np.zeros_like(img)
    #img = np.zeros_like(img)
    # Break out if the video is over
    try: img.shape
    except: break
    
    for pair in pairs:
        ball0 = smoothed_data[pair[0]]
        ball1 = smoothed_data[pair[1]]    
        b1 = ball1[frame_number:frame_number + outreach]
        b0 = ball0[frame_number-outreach:frame_number]
        b1, b0 = [],[]

        previous_dist = 987789
        current_dist = previous_dist -1
        idx = outreach
        while current_dist < previous_dist:
            a, b = ball0[frame_number-(outreach-idx)], ball1[frame_number-(idx-outreach)]            
            previous_dist = current_dist

            if outreach-idx < min_frames: current_dist -= 1
            else: current_dist = distance(a,b)
            
            idx -= 1
            #print(current_dist, previous_dist, current_dist-previous_dist)
            #cv2.circle(img, tuple(np.array(a, int)), 2, (0,255,255),-1)
            #cv2.circle(img, tuple(np.array(b, int)), 2, (255,255,0),-1)
            #cv2.line(img, tuple(np.array(a, int)), tuple(np.array(b, int)), (123,234,123), 1)
            #cv2.imshow('image', img)
            #cv2.waitKey()
            b1.append(a)
            b0.append(b)
        #print(idx)
        b0.reverse()

        
        cv2.circle(graph, tuple(np.array(b1[0], int)), 10, (0,255,255),-1)
        cv2.circle(graph, tuple(np.array(b0[-1], int)), 10, (255,255,0),-1)
        for position in range(len(b1)-1):
            a,b = b1[position], b1[position+1]
            a,b = tuple(np.array(a, int)), tuple(np.array(b, int))
            cv2.line(graph, a, b, (0,255,255), 3)
        for position in range(len(b1)-1):
            a,b = b0[position], b0[position+1]
            a,b = tuple(np.array(a, int)), tuple(np.array(b, int))
            cv2.line(graph, a, b, (255,255,0), 3)
        no_path = graph.copy()      

        try:
            ball_positions = b1 + b0
            x,y = zip(*ball_positions)
            window_length = int(len(x)*.5)
            if window_length//2 == window_length/2: window_length -= 1
            x = signal.savgol_filter(x, window_length, polyorder)
            y = signal.savgol_filter(y, window_length, polyorder)
            ball_positions = list(zip(x,y))
            for position in range(len(ball_positions)-1):
                a,b = ball_positions[position], ball_positions[position+1]
                a,b = tuple(np.array(a, int)), tuple(np.array(b, int))
                cv2.line(img, a, b, colors[pairs.index(pair)], 4)
                cv2.line(graph, a, b, (255,0,255), 2)
        except: pass

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
