import cv2, numpy as np, random

# Capture webcam source
cap = cv2.VideoCapture(0)

# Write video
vid_writer = cv2.VideoWriter('/home/stephen/Desktop/juggling_ar.avi',
                             cv2.VideoWriter_fourcc('M','J','P','G'),
                             24, (640,480))

# Required for trackbars
def nothing(arg): pass

# Takes img and color, returns parts of img that are that color
def only_color(frame, hsv_range):
    (b,r,g,b1,r1,g1) = hsv_range
    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # define range of blue color in HSV
    lower = np.array([b,r,g])
    upper = np.array([b1,r1,g1])
    # Threshold the HSV img to get only blue colors
    mask = cv2.inRange(hsv, lower, upper)
    # Bitwise-AND mask and original img
    res = cv2.bitwise_and(frame,frame, mask= mask)
    return res, mask

# Finds the contours in an img
def get_contours(im):
    imgray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    _ ,thresh = cv2.threshold(imgray,0,255,0)
    _, contours, _ = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    return contours

# Finds the center of a contour
def contour_center(c):
    M = cv2.moments(c)
    center = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
    return center

# Takes img, returns location of ball
def get_ball_locations(img, hsv_range, max_size, min_size):
    # Segment the img by color
    img, mask = only_color(img, (h,s,v,h1,s1,v1))
    # Find the contours in the img
    contours = get_contours(img)
    # If no ball is found, the default position is 0,0
    positions = []
    # Iterate though the contours:
    for contour in contours:
        area = cv2.contourArea(contour)
        if area>min_size and area<max_size: positions.append(contour_center(contour))
    if len(positions)==0: positions.append((0,0))
    return img, positions

# Spawns a new star
def new_star(position, spawn_size, speed_constant, ball_size):
    x, y = position[0] + random.randint(-ball_size,ball_size), position[1] + random.randint(-ball_size,ball_size)
    dx = speed_constant * (random.random()-.5)
    dy = speed_constant * (random.random()-.5)
    return x, y, dx, dy, spawn_size

# Setup trackbars
cv2.namedWindow('img')
cv2.createTrackbar('h', 'img', 28,255, nothing)
cv2.createTrackbar('s', 'img', 128,255, nothing)
cv2.createTrackbar('v', 'img', 17,255, nothing)
cv2.createTrackbar('h1', 'img', 39,255, nothing)
cv2.createTrackbar('s1', 'img', 255,255, nothing)
cv2.createTrackbar('v1', 'img', 255,255, nothing)
cv2.createTrackbar('min_ball_size', 'img', 20,9876, nothing)
cv2.createTrackbar('max_ball_size', 'img', 6243,9876, nothing)
trails_switch = '0 : Trails Off \n1 : ON'
cv2.createTrackbar(trails_switch, 'img',0,1,nothing)
lines_switch = '0 : lines Off \n1 : ON'
cv2.createTrackbar(lines_switch, 'img',0,1,nothing)
stars_switch = '0 : stars Off \n1 : ON'
cv2.createTrackbar(stars_switch, 'img',0,1,nothing)

# Create array of stars
stars = np.zeros((200,5), np.float32)
for i in range(stars.shape[0]): stars[i] = 100,100,.01,.01,3+i*.20
trail_paths = []
max_trail_length = 23

# Iterate though each frame of video
while True:
    
    # Get trackbar values
    h= cv2.getTrackbarPos('h', 'img')
    s= cv2.getTrackbarPos('s', 'img')
    v= cv2.getTrackbarPos('v', 'img')
    h1= cv2.getTrackbarPos('h1', 'img')
    s1= cv2.getTrackbarPos('s1', 'img')
    v1= cv2.getTrackbarPos('v1', 'img')
    min_size = cv2.getTrackbarPos('min_ball_size', 'img')
    max_size = cv2.getTrackbarPos('max_ball_size', 'img')
    show_trails = cv2.getTrackbarPos(trails_switch,'img')
    show_lines = cv2.getTrackbarPos(lines_switch,'img')
    show_stars = cv2.getTrackbarPos(stars_switch,'img')
    
    
    # Read img from the video
    _, img = cap.read()

    # Get the locations of the ball in the img    
    _, positions = get_ball_locations(img, (h,s,v,h1,s1,v1), max_size, min_size)

    # Show the ball trails
    if show_trails==1:
        trail_paths.append(positions)
        for path in trail_paths:
            for position in path: cv2.circle(img, position, 5, (13,255,123), 5)
        if len(trail_paths)>max_trail_length: trail_paths = trail_paths[-max_trail_length:]

    # Show the stars
    if show_stars==1:
        # Draw the stars on the image
        for x,y,_,_, size in stars: cv2.circle(img, (int(x),int(y)), int(size), (255,255,0), thickness=-1)
        # Move the stars in the x and y direction, and make the size smaller
        stars[:,0] = stars[:,0] + stars[:,2]
        stars[:,1] = stars[:,1] + stars[:,3]
        stars[:,4] = stars[:,4] - .2
        # Get rid of stars that are too small
        for i in range(stars.shape[0]):
            if stars[i][4] < 1: stars[i] = new_star(positions[random.randint(0, len(positions)-1)], 3, 9, 20)

    # Draw lines between the balls
    if show_lines==1:
        for i in range(len(positions)): cv2.line(img, positions[i], positions[i-1], (0,255,0), 9)
        
    # Show the masked image
    cv2.imshow('mask', only_color(img, (h,s,v,h1,s1,v1))[1])
            
    #show the img and wait
    cv2.imshow('img1', img)
    vid_writer.write(img)
    k=cv2.waitKey(1)
    if k==27: break
    
#release the video to avoid memory leaks, and close the window
cap.release()
cv2.destroyAllWindows()
