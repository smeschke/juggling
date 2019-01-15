import cv2, math, numpy as np, pandas as pd, scipy, random
from scipy import signal
# path to data and source video
path = 'ss615_id_502'
df = pd.read_csv('/home/stephen/Desktop/source_data/'+path+'.csv')
cap = cv2.VideoCapture('/home/stephen/Desktop/source_vids/'+path+'.MP4')
# Smoothing parameters
window_length, polyorder = 21, 2
# List of colors
colors = (255,0,0),(0,255,0),(0,0,255),(0,255,255)
# Parameters for animation
spawn_size = 20
size_decrement = .25
speed_constant = 12
ball_size = 80
vid_writer = cv2.VideoWriter('/home/stephen/Desktop/writer.avi',
                             cv2.VideoWriter_fourcc('M','J','P','G'),
                             120, (480,848))
# Create list for smoothed data
stars_list, smoothed_data = [], []
# Iterate through each column in the database
for i in range(int(len(df.columns)/2)):
    # Smooth the column
    x = signal.savgol_filter(df[df.columns[i*2]], window_length, polyorder)*10
    y = signal.savgol_filter(df[df.columns[i*2+1]], window_length, polyorder)*10
    # Add the smoothed data to the smoothed_data list
    smoothed_data.append(list(zip(x,y)))

    # Create lists of stars
    stars = np.zeros((300,5), np.float32)
    for i in range(stars.shape[0]): stars[i] = 100,100,.01,.01,spawn_size+i*size_decrement
    stars_list.append(stars)

# Function that spawns a new star
def new_star(position, spawn_size, speed_constant, ball_size):
    x, y = position[0] + random.randint(-ball_size,ball_size), position[1] + random.randint(-ball_size,ball_size)
    dx = speed_constant * (random.random()-.5)
    dy = speed_constant * (random.random()-.5)
    return x, y, dx, dy, spawn_size

# Iterate through each frame of video
frame_number = 0
while True:

    # Grab image and resize (resize so that stars can be drawn in greater resolution)
    _, img = cap.read()
    height, width, _ = img.shape
    img = cv2.resize(img, (width*10,height*10))

    # Iterate though each ball in the smoothed data
    for ball in range(len(smoothed_data)):

        # Get the appropriate ball position and list of stars
        position = smoothed_data[ball][frame_number]
        stars = stars_list[ball]
        
        # Move the stars in the x and y direction, and make the size smaller
        stars[:,0] = stars[:,0] + stars[:,2]
        stars[:,1] = stars[:,1] + stars[:,3]
        stars[:,4] = stars[:,4] - size_decrement

        # Iterate through the stars
        for i in range(stars.shape[0]):
            x, y, _, _, size = stars[i]
            # Draw the star
            cv2.circle(img, (int(x),int(y)), int(size), colors[ball], thickness=-1)
            # If star is too old, get a new one
            if size < 1: stars[i] = new_star(position, spawn_size, speed_constant, ball_size)
        # Update the master list of stars
        stars_list[ball] = stars

    # Resize, show, wait, write, etc...
    img = cv2.resize(img, (width, height))
    cv2.imshow('image',img)
    frame_number+=1
    vid_writer.write(img)
    k = cv2.waitKey(1)
    if k == 27: break
    
cv2.destroyAllWindows()
cap.release()
