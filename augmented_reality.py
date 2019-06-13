import cv2, numpy as np, random

# Capture webcam source
cap = cv2.VideoCapture(0)
#cap = cv2.VideoCapture('path_to_video')

# Write video
#vid_writer = cv2.VideoWriter('/home/stephen/Desktop/juggling_ar.avi', cv2.VideoWriter_fourcc('M','J','P','G'), 25, (640,480))

# Required for trackbars
def nothing(arg): pass

# Heart shape
heart_shape = np.array([[[[38,9]],[[39,8]],[[45,8]],[[46,9]],[[50,9]],[[51,10]],[[53,10]],[[54,11]],[[55,11]],[[56,12]],[[57,12]],[[58,13]],[[59,13]],[[62,16]],[[63,15]],[[64,15]],[[66,13]],[[67,13]],[[68,12]],[[69,12]],[[70,11]],[[72,11]],[[73,10]],[[76,10]],[[77,9]],[[87,9]],[[88,10]],[[91,10]],[[92,11]],[[93,11]],[[94,12]],[[95,12]],[[96,13]],[[97,13]],[[98,14]],[[99,14]],[[107,22]],[[107,23]],[[109,25]],[[109,26]],[[110,27]],[[110,28]],[[111,29]],[[111,31]],[[112,32]],[[112,34]],[[113,35]],[[113,49]],[[112,50]],[[112,53]],[[111,54]],[[111,55]],[[110,56]],[[110,57]],[[109,58]],[[109,59]],[[108,60]],[[108,61]],[[97,72]],[[97,73]],[[75,95]],[[75,96]],[[63,108]],[[62,108]],[[41,87]],[[41,86]],[[18,63]],[[18,62]],[[16,60]],[[16,59]],[[14,57]],[[14,56]],[[13,55]],[[13,53]],[[12,52]],[[12,49]],[[11,48]],[[11,34]],[[12,33]],[[12,31]],[[13,30]],[[13,28]],[[14,27]],[[14,26]],[[15,25]],[[15,24]],[[18,21]],[[18,20]],[[23,15]],[[24,15]],[[26,13]],[[27,13]],[[29,11]],[[31,11]],[[32,10]],[[34,10]],[[35,9]]]], np.int32)

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
    contours, _ = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
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
    if len(positions)==0: positions.append((-200,-200))
    return img, positions

# Spawns a new star
def new_star(position, spawn_size, speed_constant, ball_size, color):
    x, y = position[0] + random.randint(-ball_size,ball_size), position[1] + random.randint(-ball_size,ball_size)
    dx = speed_constant * (random.random()-.5)
    dy = speed_constant * (random.random()-.5)
    return x, y, dx, dy, spawn_size, color

# Setup trackbars
cv2.namedWindow('img')
cv2.createTrackbar('h', 'img', 28,255, nothing)
cv2.createTrackbar('s', 'img', 128,255, nothing)
cv2.createTrackbar('v', 'img', 17,255, nothing)
cv2.createTrackbar('h1', 'img', 71,255, nothing)
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
hearts_switch = '0 : hearts Off \n1 : ON'
cv2.createTrackbar(hearts_switch, 'img',1,1,nothing)

# Create array of stars
stars = np.zeros((200,6), np.float32)
colors = [(255,255,0),(0,255,255),(255,0,255)]
for i in range(stars.shape[0]): stars[i] = -100,-100,.01,.01,3+i*.20, random.randint(0,2)
# Create array of hearts
hearts = np.zeros((25,6), np.float32)
for i in range(hearts.shape[0]): hearts[i] = -123,-123,0,0,3+i*.2, 1
# Parameters for trails
trail_paths, max_trail_length = [], 23

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
    show_hearts = cv2.getTrackbarPos(hearts_switch,'img')
    
    # Read img from the video
    _, img = cap.read()

    # Get the locations of the ball in the img    
    mask, positions = get_ball_locations(img, (h,s,v,h1,s1,v1), max_size, min_size)

    # Show the ball trails
    if show_trails==1:
        trail_paths.append(positions)
        for path in trail_paths:
            for position in path: cv2.circle(img, position, 5, (13,255,123), 5)
        if len(trail_paths)>max_trail_length: trail_paths = trail_paths[-max_trail_length:]

    # Show the stars
    if show_stars==1:
        # Draw the stars on the image
        for x,y,_,_, size, color in stars: cv2.circle(img, (int(x),int(y)), int(size), colors[int(color)], thickness=-1)
        # Move the stars in the x and y direction, and make the size smaller
        stars[:,0] = stars[:,0] + stars[:,2]
        stars[:,1] = stars[:,1] + stars[:,3]
        stars[:,4] = stars[:,4] - .2
        # Get rid of stars that are too small
        for i in range(stars.shape[0]):
            if stars[i][4] < 1: stars[i] = new_star(positions[random.randint(0, len(positions)-1)], 3, 15, 20, random.randint(0,2))

    # Draw lines between the balls
    if show_lines==1:
        for i in range(len(positions)): cv2.line(img, positions[i], positions[i-1], (0,255,0), 9)

    # Draw hearts
    if show_hearts == 1:
        # Iterate though each heart
        for x,y,_,_, size, color in hearts:
            # Copy the heart shape
            this_heart = heart_shape.copy()
            # Resize the heart shape and translate it by x,y
            this_heart[:,:,:,0] = .1*heart_shape[:,:,:,0]*size + x
            this_heart[:,:,:,1] = .1*heart_shape[:,:,:,1]*size + y
            # Draw the contours around the heart
            cv2.drawContours(img, this_heart, 0, colors[int(color)], -1)
            
        # Move the hearts in the x and y direction, and make the size smaller
        hearts[:,0] = hearts[:,0] + hearts[:,2]
        hearts[:,1] = hearts[:,1] - abs(hearts[:,3])
        hearts[:,4] = hearts[:,4] - .05
        # Replace hearts that are too small
        for i in range(hearts.shape[0]):
            if hearts[i][4] < 1:
                hearts[i] = new_star(positions[random.randint(0, len(positions)-1)], 3, 9, 20, random.randint(0,2))
        
    # Show the masked image
    cv2.imshow('img', mask)
            
    # Show the img and wait
    cv2.imshow('ar', img)
    #vid_writer.write(img)
    k=cv2.waitKey(1)
    if k==27: break
    
# Cleanup
cap.release()
cv2.destroyAllWindows()
