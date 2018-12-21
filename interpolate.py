import cv2, math
import numpy as np
import pandas as pd
import scipy
from scipy import signal



path = 'k4'
df = pd.read_csv('/home/stephen/Desktop/'+path+'.csv')
cap = cv2.VideoCapture('/home/stephen/Desktop/'+path+'.avi')
# interpolate video
hw = 1000
vid_writer = cv2.VideoWriter('/home/stephen/Desktop/interpolated.avi',
                             cv2.VideoWriter_fourcc('M','J','P','G'),
                             30, (hw,hw))

def dist(a,b): return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

#smooth it out
smoothed_data = []
window_length, polyorder = 3, 2
for i in range(int(len(df.columns)/2)):
    #x = signal.savgol_filter(df[df.columns[i*2]], window_length, polyorder)
    #y = signal.savgol_filter(df[df.columns[i*2+1]], window_length, polyorder)
    y = df[df.columns[i*2+1]]
    x = df[df.columns[i*2]]
    smoothed_data.append(list(zip(x,y)))

positions = []
for frame_number in range(len(smoothed_data[0])-1):
    frame_positions = []
    frame_positions_interpolate = []
    for ball_number in range(len(smoothed_data)):
        a = smoothed_data[ball_number][frame_number]
        b = smoothed_data[ball_number][frame_number+1]
        a_b = (a[0]+b[0])/2, (a[1]+b[1])/2
        frame_positions.append(a[0])
        frame_positions.append(a[1])
        frame_positions_interpolate.append(a_b[0])
        frame_positions_interpolate.append(a_b[1])
    positions.append(frame_positions)
    positions.append(frame_positions_interpolate)

df = pd.DataFrame(np.array(positions))
df.to_csv('/home/stephen/Desktop/interpolated.csv', index = False)

#read source video#
_, img = cap.read()
p_img = np.zeros_like(img)

while True:
    
    blend_image = cv2.addWeighted(img, .5, p_img, .5, 1)

    vid_writer.write(blend_image)

    cv2.imshow('img', blend_image)
    k = cv2.waitKey(1)

    vid_writer.write(img)
    cv2.imshow('img', img)
    k = cv2.waitKey(1)
    if k == 27: break

    p_img = img.copy()
    _, img = cap.read()
    try: d = img.shape
    except: break    

cv2.destroyAllWindows()


    


