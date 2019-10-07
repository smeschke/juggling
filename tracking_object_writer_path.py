import cv2, math, numpy as np, pandas as pd, scipy
from scipy import signal
path = 'ss855_id_884'
source_path = '/home/stephen/Desktop/source_video/' + path + '.MP4'
data_path = '/home/stephen/Desktop/tracking_data/' + path + '.csv'
outreach = 200
min_frames = 70
pairs = [[0,0],[1,1],[2,2]]
# Create output video
vid_writer = cv2.VideoWriter('/home/stephen/Desktop/writer.avi', cv2.VideoWriter_fourcc('M','J','P','G'), 120, (480,848))
# List of colors
colors = (255,255,0),(0,255,255),(255,0,255),(0,255,0),(0,0,255), (255,0,0), (255,123,0),(0,255,123),(255,0,123),(123,0,255),(123,0,123),(0,0,255),(255,0,0), (0,255,0), (255,123,0),(0,255,123),(255,255,0),(255,0,255),(0,255,255),(0,0,255),(255,0,0), (0,255,0), (255,123,0),(0,255,123),(255,255,0),(255,0,255),(0,255,255),(0,0,255),(255,0,0), (0,255,0), (255,123,0),(0,255,123)
# Read source video
cap = cv2.VideoCapture(source_path)
# Read data
df = pd.read_csv(data_path)
# Create list for smoothed data
smoothed_data = []
# Iterate through each column in the database
for i in range(int(len(df.columns)/2)):
    # Smooth the column
    window_length, polyorder = 27, 2
    x = signal.savgol_filter(df[df.columns[i*2]], window_length, polyorder)
    y = signal.savgol_filter(df[df.columns[i*2+1]], window_length, polyorder)
    smoothed_data.append(list(zip(x,y)))
def distance(a,b): return math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)
def midpoint(a,b):
    (x1, y1), (x2, y2) = a, b
    return ((x1 + x2)/2, (y1 + y2)/2)
for i in range(outreach): _,_ = cap.read()
# Start counting by frame number
frame_number = outreach
# Iterate through each frame of video
while True:
    _, img = cap.read()
    # Iterate through each pair of objects
    for pair in pairs:
        # Get the data for the leading and trailing object
        leading = smoothed_data[pair[0]]
        trailing = smoothed_data[pair[1]]
        # Create lists to store the paths
        leading_positions, trailing_positions = [],[]
        # Reset parameters
        previous_dist, current_dist, idx = 0,0,0
        # Continue while the paths converge
        while current_dist < previous_dist or idx < min_frames:
            # Get the positions of the leading and trailing objects
            leading_position = leading[frame_number-idx]
            trailing_position = trailing[frame_number+idx]
            # Add the positions to the paths            
            leading_positions.append(leading_position)
            trailing_positions.append(trailing_position)
            # Update the convergence distance
            previous_dist = current_dist
            current_dist = distance(leading_position,trailing_position)            
            idx += 1
            #if idx%2 == 0: cv2.line(img, tuple(np.array(leading_position, int)), tuple(np.array(trailing_position, int)), (123,234,123), 1)
        # Reverse the list of trailing positions
        trailing_positions.reverse()
        # Combine the lists to form a complete path
        ball_positions = leading_positions[:-1] + trailing_positions[1:]
        #print(len(ball_positions))
        # Smooth the positions
        x,y = zip(*ball_positions)
        x = signal.savgol_filter(x, 15, 3)
        y = signal.savgol_filter(y, 15, 3)
        ball_positions = list(zip(x,y))
        # Draw the smoothed lines
        for position in range(len(ball_positions)-1):
            a,b = ball_positions[position], ball_positions[position+1]
            a,b = tuple(np.array(a, int)), tuple(np.array(b, int))
            cv2.line(img, a, b, colors[pairs.index(pair)], 2)                
    # Show the image and wait
    cv2.imshow('image',img)
    vid_writer.write(img)
    k = cv2.waitKey(1)
    if k == 27: break    
    # Increment frame number
    frame_number += 1    
cv2.destroyAllWindows()
cap.release()
