import cv2, math
import numpy as np
import pandas as pd
import scipy
from scipy import signal

#------------------Enter these parameters------------------
# Path to source video - find here: https://drive.google.com/open?id=0B7QqDexrxSfwVXgwWlRUcDBiVFk
path = 'ss71_id_162'
source_path = '/home/stephen/Desktop/source_vids/' + path + '.MP4'
#source_path = '/home/stephen/Desktop/' + path + '.avi'

# Path to source data - find here: https://drive.google.com/open?id=0B7QqDexrxSfwVXgwWlRUcDBiVFk
#data_path = '/home/stephen/Desktop/source_data/' + path  + '.csv'
data_path = '/home/stephen/Desktop/source_data/' + path  + '.csv'
# Smoothing parameters
window_length, polyorder = 15, 2
# List of colors
colors = (255,0,255),(255,255,0),(0,255,255),(0,0,255),(255,0,0), (0,255,0), (255,123,0),(0,255,123)
#colors = (255,0,0),(0,0,255),(0,75,255),(0,156,255),(0,255,255), (0,255,0), (255,123,0),(0,255,123)
#colors = (1,56,255),(234,234,234),(1,56,255),(234,234,234),(1,56,255),(234,234,234),(1,56,255),(234,234,234),(1,56,255),(234,234,234),(1,56,255)
#colors = (1,56,255),(1,56,255),(45,45,45),(45,45,45),(1,56,255),(45,45,45),(1,56,255),(45,45,45),(1,56,255)

# Parameters for animation
hw = 720
#hw = 780
#hw = 848
vid_writer = cv2.VideoWriter('/home/stephen/Desktop/test.avi',
                             cv2.VideoWriter_fourcc('M','J','P','G'),
                             60, (hw,hw))

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

    alpha = np.zeros_like(img)
    foreground = np.zeros_like(img)

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
            
    background= img.copy()

    foreground = foreground.astype(float)
    background = background.astype(float)

    aalpha = alpha.copy()

    
    # Normalize the alpha mask to keep intensity between 0 and 1
    alpha = alpha.astype(float)/255
     
    # Multiply the foreground with the alpha matte
    foreground = cv2.multiply(alpha, foreground)
     
    # Multiply the background with ( 1 - alpha )
    background = cv2.multiply(1.0 - alpha, background)
     
    # Add the masked foreground and background.
    img = cv2.add(foreground, background)
    img = img/255
    img = np.array(img*255, np.uint8)

    # mat to a square aspect
    bg = np.zeros((848,848,3), np.uint8)
    bg[:,:,:] = 123,123,123
    bg[:,180:180+480] = img
    img = bg

    if hw == 780: img = img[848-780:848, 0+30:30+780] # for 780
    if hw == 720: img = img[848-720:848, 0+50:50+720] #for 720x
    
    # Show the image and wait                
    cv2.imshow('image',img)
    #cv2.imshow('alpha',aalpha)    
    
    vid_writer.write(img)
    k = cv2.waitKey(1)
    if k == 27: break
    
    # Increment frame number
    frame_number += 1
    
cv2.destroyAllWindows()
cap.release()
