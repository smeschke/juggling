import cv2, math, numpy as np, pandas as pd, scipy, itertools
from scipy import signal
from scipy.interpolate import interp1d

#-------------------- PARAMETERS ----------------------------
global hw, lh, lh_release_point, rh_release_point, test, left_hand_path_x, left_hand_path_y, right_hand_path_x
global right_hand_path_y, path_line_thickness, white, adjust_path_points
white = (255,255,255)
grid_img = cv2.imread('/home/stephen/Desktop/grid_img.png')
hw = grid_img.shape[0]
select_release_points, lh, adjust_path_points, recompute = False, False, False, False
colors = [(255,255,0),(0,255,255),(255,255,0),(0,255,255)]
left_hand_origin, right_hand_origin = (-120,0), (120,0)
time, time_span = 0, hw/2-1
lh_release_point, rh_release_point = [30],[288]
balls = []
num_balls = 50
gravity = .013
catch_threshold, throw_threshold = 50, 200
# scale down the movements of the arms
movement_scale = .5
path_line_thickness = 1
adjust_point, adjust_list = 0, 0
left_hand_full, right_hand_full = False, False
#-------------------- END PARAMETERS ------------------------

# Mouse callback function
global click_list, x_coords_left, y_coords_left, x_coords_right, y_coords_right
x_coords_left, y_coords_left, x_coords_right, y_coords_right = [],[],[],[]
# These are good coordinates to start with
x_coords_left = [(504, 351), (752, 156), (994, 349), (664, 186), (609, 329), (874, 152), (925, 182)]
y_coords_left = [(664, 651), (855, 856), (542, 563)]
x_coords_right = [(505, 350), (748, 153), (989, 351), (713, 237), (840, 152), (681, 317), (614, 338), (878, 295), (791, 118), (917, 339)]
y_coords_right = [(659, 864), (875, 645), (742, 817), (781, 625)]

x_coords_left, y_coords_left, x_coords_right, y_coords_right = ([(504, 351), (752, 156), (994, 349), (664, 186), (609, 337), (874, 140), (937, 182)], [(664, 651), (855, 856), (542, 563)], [(505, 350), (748, 157), (989, 351), (713, 237), (840, 152), (681, 317), (614, 338), (878, 295), (791, 118), (917, 339)], [(659, 864), (875, 645), (742, 817), (781, 625)])
positions, click_list = [], []
def callback(event, x, y, flags, param):
    if event == 1:
        click_list.append((x,y))
        # User wants to define a release point
        if select_release_points:
            if lh: lh_release_point.append(int(x - hw/2))
            if not lh: rh_release_point.append(int(x - hw/2))
        # Add the corrdinate to the appropriate list
        if not select_release_points and not adjust_path_points:            
            if split_points((x,y)) == 'top':
                if lh:x_coords_left.append((x,y))
                else: x_coords_right.append((x,y))
            if split_points((x,y)) == 'bottom':
                if lh: y_coords_left.append((x,y))
                else: y_coords_right.append((x,y))
cv2.namedWindow('img')
cv2.setMouseCallback('img', callback)    

# Gets a smooth line through a series of points
def get_smooth_line(input_points):
    # Copy the points to avoid a Python memory error
    points = input_points.copy()
    # Sort the points by x values
    points.sort()
    # Calculate a midpoint between the first and last point
    midpoint = (points[0][1] + points[-1][1]) / 2
    # Add the midpoint to the beginning of the string and to the end
    points.append((hw/2, midpoint))
    points.append((hw, midpoint))
    # Sort the points again
    points.sort()
    # Unzip into arrays
    x_values, y_values = zip(*points)
    x = np.array(list(list(zip(*points))[0]))
    y = np.array(list(list(zip(*points))[1]))
    # Use linespace to get an array of x values
    x_new = np.linspace(x.min(), x.max(),x[-1]-x[0])
    # Use 'interp1d' to get a quadratic smoothing function <--- this is the heavy lifting
    f = interp1d(x, y, kind='quadratic')
    # Compute the new values
    y_smooth=f(x_new)
    return x, y_smooth

# Splits the points up into top and bottom (x or y component)
def split_points(point):
    if point[0]>hw/2 and point[1]<hw/2: return 'top'
    if point[0]>hw/2 and point[1]>hw/2: return 'bottom'
    # User clicked in the animator part (left side of screen)
    if point[0]<hw/2: return 'invalid'

# Draws a smooth
def draw_smooth_line(x, y_smooth, img, color, time):
    for i in range(len(y_smooth)-1):
        a = i+1 + x[0], int(y_smooth[i+1])      
        b = i   + x[0], int(y_smooth[i])
        cv2.line(img, tuple(np.array(a, int)), tuple(np.array(b, int)), color, path_line_thickness)
    # Get the positions at the current time
    xy = hw/2+time, y_smooth[time]
    # Draw circles on the path at the current time
    cv2.circle(img, tuple(np.array(xy, int)), 3, white,1)
    return img

# Moves ball and applies gravity
def move_ball(ball):
    (x,y), (dx, dy), hand = ball
    # Move the ball in the x direction by speed dx
    x += dx
    # Move the ball in the y direction by speed dy
    y += dy
    # Apply gravity to the ball
    dy += gravity
    return (x,y), (dx, dy), hand

# Draws text on an image
def draw_text(img):
    # Define some text parameters
    font, scale, color, thick, org = cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 1, (10,50)
    # User is selecting release points
    if select_release_points: text = 'select release points'
    # User wants to alter path points
    if adjust_path_points: text = 'adjust path points'
    # User is selecting path points
    if not adjust_path_points and not select_release_points:
        # User is selecing path points for the left hand
        if lh: text = 'select LEFT hand throw points'
        # User is selecting path points for the right hand
        else: text = 'select RIGHT hand throw points'
    # Draw text on the image
    cv2.putText(img, text, tuple(np.array(org, int)), font, scale, color, thick, cv2.LINE_AA)
    return img

# Draw the hand on the image - the hand is represented by a circle
def draw_hand(x_coords, y_coords, img, time, origin, release_point, color):
    # Get the x and y coordinates for the hand
    x_coord = origin[0] + x_coords[time]
    y_coord = origin[1] + y_coords[time]
    xy = tuple(np.array((x_coord, y_coord), int))
    # Draw a circle showing the location of the hand
    cv2.circle(img, xy, 15, white, 5)
    # Draw the path of the hand - iterate though each value in the path
    for i in range(len(y_coords)):
        # Get the location of that value
        xy = x_coords[i] + origin[0], y_coords[i] + origin[1]
        xy = tuple(np.array(xy, int))
        # Draw a circle at that value
        cv2.circle(img, xy, 1, color, 1)
    # Now, draw a the release point
    release_point = int(release_point)
    # Get the location of the release point
    release_point_location = tuple(np.array((x_coords[release_point] + origin[0],y_coords[release_point] + origin[1]), int))
    # Draw a circle around the release point
    cv2.circle(img, release_point_location, 1, white, 5)
    return img

# Takes path data and time, returns spawn location and velocity vector
def get_new_ball(x,y,time):
    # Find the location of the hand
    xy = x[time], y[time]
    # Find the velocity vector
    dxy = xy[0] - x[time-1], xy[1] - y[time-1]
    return xy, dxy

# Returns the distance between two points
def distance(a,b): return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

# Compute paths
_, left_hand_path_y = get_smooth_line(y_coords_left)
_, left_hand_path_x = get_smooth_line(x_coords_left)
_, right_hand_path_y = get_smooth_line(y_coords_right)
x_points, right_hand_path_x = get_smooth_line(x_coords_right)

# Main Loop
while True:
    
    # Get the length of the click_list
    click_list_length = len(click_list)
    
    # Update the time
    if time < time_span: time += 1
    else: time = 0
    
    # Create blank background image
    img = grid_img.copy()

    # Draw the paths from the release points
    left_path = get_new_ball(left_hand_path_x,left_hand_path_y, lh_release_point[-1])[0], get_new_ball(left_hand_path_x,left_hand_path_y, lh_release_point[-1])[1], 'none'    
    right_path = get_new_ball(right_hand_path_x,right_hand_path_y, rh_release_point[-1])[0], get_new_ball(right_hand_path_x,right_hand_path_y, rh_release_point[-1])[1], 'none'

    for i in range(1000):
        xxx = tuple(np.array((left_path[0][0]+left_hand_origin[0], left_path[0][1]), int))
        cv2.circle(img, xxx, 1, white, 1)
        left_path = move_ball(left_path)
    for i in range(1000):
        xxx = tuple(np.array((right_path[0][0]+right_hand_origin[0], right_path[0][1]), int))
        cv2.circle(img, xxx, 1, white, 1)
        right_path = move_ball(right_path)

    # Draw the release points
    release_point = hw/2 + rh_release_point[-1], right_hand_path_x[int(rh_release_point[-1])]
    cv2.circle(img, tuple(np.array(release_point, int)), 5, (123,235,24), 2)
    release_point = hw/2 + rh_release_point[-1], right_hand_path_y[int(rh_release_point[-1])]
    cv2.circle(img, tuple(np.array(release_point, int)), 5, (123,235,24), 2)
    release_point = hw/2 + lh_release_point[-1], left_hand_path_x[int(lh_release_point[-1])]
    cv2.circle(img, tuple(np.array(release_point, int)), 5, (123,235,24), 2)
    release_point = hw/2 + lh_release_point[-1], left_hand_path_y[int(lh_release_point[-1])]
    cv2.circle(img, tuple(np.array(release_point, int)), 5, (123,235,24), 2)
    
    # Draw the smooth lines
    # Make a master list to iterate though
    paths = [right_hand_path_x, left_hand_path_x, right_hand_path_y, left_hand_path_y]
    # Iterate though each path
    for path, color in zip(paths, colors):
        # Draw a smooth line of the path on the image
        img = draw_smooth_line(x_points, path, img, color, time)

    # Draw the circles that show user input
    # Iterate though the listS of listS of coordinates
    coordinate_lists = [x_coords_right, x_coords_left, y_coords_right, y_coords_left]
    for coordinate_list, color in zip(coordinate_lists, colors):
        # Iterate though each point in the list of coordinates
        for point in coordinate_list:
            # Draw a circle representing user input
            cv2.circle(img, point, 2, color, 2)

    # Does the user want to adjust the paths
    if adjust_path_points:
        # Get the appropriate path to alter
        coordinate_list = coordinate_lists[adjust_list]
        # Check to make sure the point the user wants to alter isn't beyond the length of the list
        if adjust_point > len(coordinate_list)-1: temp_adjust_point = len(coordinate_list)-1
        else: temp_adjust_point = adjust_point
        # Get the coordinate of the point to be altered
        xy = coordinate_list[temp_adjust_point]
        # Draw a circle around the point to be altered
        cv2.circle(img, xy, 12, white, 12)
        if k != -1:
            try:
                # User has pressed '4' on the number pad, move the point to the right
                if k == 180: coordinate_list[adjust_point] = xy[0]-1, xy[1]
                # User has pressed '8' on the number pad, move the point up
                if k == 184: coordinate_list[adjust_point] = xy[0], xy[1]-1
                # User has pressed '6' on the number pad, move the point to the left
                if k == 182: coordinate_list[adjust_point] = xy[0]+1, xy[1]
                # User has pressed '2' on the number pad, move the point down
                if k == 178: coordinate_list[adjust_point] = xy[0], xy[1]+1
                recompute = True
            except: print('invalid attempt')
                    
  
    # Draw right hand
    if len(x_coords_right)>=2 and len(y_coords_right)>=2:
        img = draw_hand(right_hand_path_x, right_hand_path_y, img, time, right_hand_origin, rh_release_point[-1], colors[0])
    # Draw left hand
    if len(x_coords_left)>=2 and len(y_coords_left)>=2:
        img = draw_hand(left_hand_path_x, left_hand_path_y, img, time, left_hand_origin, lh_release_point[-1], colors[1])

    # Try to spawn a ball
    if len(balls) < num_balls:
        # Is the left hand near the relese point?
        if time == lh_release_point[-1] and not left_hand_full:
            # Get spawn location for the left hand
            ball = get_new_ball(left_hand_path_x,left_hand_path_y, time)
            # Alter the locations so that they match up with the hand origin
            ball = (ball[0][0]+left_hand_origin[0], ball[0][1]), ball[1], 'none'
            # Add the ball to the list of balls
            balls.append(ball)
        # Is the right hand near the release point?
        if time == rh_release_point[-1] and not right_hand_full:
            # Similar to left hand - duplicate comments ommited
            ball = get_new_ball(right_hand_path_x,right_hand_path_y, time)
            ball = (ball[0][0]+right_hand_origin[0], ball[0][1]), ball[1], 'none'
            balls.append(ball)
            
    # Create a temporary list - if balls are have not been dropped, they will be added to this list
    new_balls = []
    # Iterate though each of the balls
    for ball in balls:

        #print(ball)
        
        # Move the balls
        ball = move_ball(ball)

        # Is the ball near the left hand
        left_hand_location = left_hand_path_x[time] + left_hand_origin[0], left_hand_path_y[time] + left_hand_origin[1]
        left_hand_throw_location = left_hand_path_x[int(lh_release_point[-1])] + left_hand_origin[0], left_hand_path_y[int(lh_release_point[-1])] + left_hand_origin[1]
        if distance(ball[0], left_hand_location) < catch_threshold and distance(ball[0], left_hand_throw_location) > throw_threshold:
            ball = left_hand_location, ball[1], 'left'
            #print('snap')
            left_hand_full = True
        a,b = left_hand_location, ball[0]
        #cv2.line(img, tuple(np.array(a, int)), tuple(np.array(b, int)), white, 1)
        # Is the ball near the right hand
        right_hand_location = right_hand_path_x[time] + right_hand_origin[0], right_hand_path_y[time] + right_hand_origin[1]
        right_hand_throw_location = right_hand_path_x[int(rh_release_point[-1])] + right_hand_origin[0], right_hand_path_y[int(rh_release_point[-1])] + right_hand_origin[1]
        if distance(ball[0], right_hand_location) < catch_threshold and distance(ball[0], right_hand_throw_location) > throw_threshold:
            ball = right_hand_location, ball[1], 'right'
            #print('snap')
            right_hand_full = True
        a,b = right_hand_location, ball[0]
        #cv2.line(img, tuple(np.array(a, int)), tuple(np.array(b, int)), white, 1)
        
        # If the ball is in the left hand, snap it to the left and location
        if ball[2] == 'left': ball = left_hand_location, ball[1], 'left'

        # If the ball passes the release point and is in the hand, release it
        if ball[2] == 'left' and time == lh_release_point[-1]:
            new_ball = get_new_ball(left_hand_path_x,left_hand_path_y, time)
            ball = (new_ball[0][0]+left_hand_origin[0], new_ball[0][1]), new_ball[1], 'none'
            #ball = ball[0], ball[1], 'none'
            left_hand_full = False
            
        # If the ball is in the right hand, snap it to the right and location
        if ball[2] == 'right': ball = right_hand_location, ball[1], 'right'

        # If the ball passes the release point and is in the hand, release it
        if ball[2] == 'right' and time == rh_release_point[-1]:
            new_ball = get_new_ball(right_hand_path_x,right_hand_path_y, time)
            ball = (new_ball[0][0]+right_hand_origin[0], new_ball[0][1]), new_ball[1], 'none'
            right_hand_full = False
        
        # Draw a circle showing the location of the ball
        cv2.circle(img, tuple(np.array(ball[0], int)), 15, (255,0,255), -1)
        # If the ball has not fallen below the screen, add it to the temporary list
        if ball[0][1] < hw: new_balls.append((ball[0], ball[1], ball[2]))
    # The temporary list becomes the list of balls
    balls = new_balls

    # Draw some text on the image for instructions
    img = draw_text(img)
    # Show the image
    cv2.imshow('img', img)
    # Wait, grap user input
    k = cv2.waitKey(1)
    # 'ESC' to quit
    if k == 27: break
    # 'Space Bar' to switch input from left to right
    if k == 32: lh = not lh
    # 'r' to select release points
    if k == ord('r'):
        select_release_points = not select_release_points
        adjust_path_points = False
    # 'p' to select path points
    if k == ord('p'):
        adjust_path_points = not adjust_path_points
        select_release_points = False
    # left or right cursor to select the point to adjust
    if k == 83: adjust_point += 1
    if k == 81: adjust_point -=1
    if adjust_point < 0: adjust_point = 0
    # up or down to select the list to adjust
    if k == 84: adjust_list += 1
    if k == 82: adjust_list -=1
    if adjust_list < 0: adjust_list = 0
    if adjust_list > 3: adjust_list = 3

    # If the click list length does not equal that from before, recompute the paths to account for the new data
    if len(click_list) != click_list_length or recompute:
        _, left_hand_path_y = get_smooth_line(y_coords_left)
        _, left_hand_path_x = get_smooth_line(x_coords_left)
        _, right_hand_path_y = get_smooth_line(y_coords_right)
        _, right_hand_path_x = get_smooth_line(x_coords_right)
        left_path = get_new_ball(left_hand_path_x,left_hand_path_y, lh_release_point[-1])[0], get_new_ball(left_hand_path_x,left_hand_path_y, lh_release_point[-1])[1], 'none'
        right_path = get_new_ball(right_hand_path_x,right_hand_path_y, rh_release_point[-1])[0], get_new_ball(right_hand_path_x,right_hand_path_y, rh_release_point[-1])[1], 'none'    
        recompute = False

cv2.destroyAllWindows()
