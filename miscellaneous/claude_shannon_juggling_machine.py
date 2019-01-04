import cv2, numpy as np, math, random
# ------------------------ PARAMETERS --------------------------------
global size, width, height, bearing_location, arm_length, paddle_length, x_origion, y_origion
global paddle_height, rotation, motor_speed, drive_arm_motor, end_length, ggg
global drive_arm_paddle, gravity, mass, elasticity, paddle_elasticity, n_balls, ball_space
# Size of the window
width, height = 1000,1000
# Location of the bearing that the arm rotates about
bearing_location = width/2,650
# Length from bearing to start of paddle
arm_length = 150
# Length of the paddle
paddle_length = 220
end_length,ggg = 120, .4
hypot = math.sqrt((arm_length + paddle_length)**2 + end_length**2) + 15
end_length = -.4
# Amount that the paddle rotates (in Rad)
rotation = .64
# Speed that the paddle rotates (in Rad)
motor_speed = .0065
# Location that the paddle assembly starts
current_rotation = 0
# Initial state of the stroke of the paddle
paddle_up = True
# Constant for the gravity in the environment
gravity = .069
# How much the balls bounce off the paddle
paddle_elasticity = .6
# Ball size
floor_height, floor_start, floor_end = 900,305,1000-305
size = 10
distance_threshold = size
mass = 10
elasticity = .99
drag = 1
# Number of balls and spacing
n_balls, ball_space = 1, 5
x_origion, y_origion = bearing_location[0] - arm_length - paddle_length + 10, bearing_location[1] - 10
# Each ball is an element in the 'balls' list
# Each ball is represented by a double tuple: ((x_coordinate, y_coordinate), (speed, angle))
# The x and y coordinates explain position, speed and angle make a vector

vid_writer = cv2.VideoWriter('/home/stephen/Desktop/test.avi',
                             cv2.VideoWriter_fourcc('M','J','P','G'),
                             240, (width,height))

# Create a set of balls
def get_balls():
    balls, idx = [], 0    
    for xx in range(n_balls):
        for yy in range(n_balls):
            idx += 1        
            x, y = x_origion + xx*ball_space, y_origion + yy*ball_space
            color = (255 - (255/n_balls)*xx, (255/n_balls)*yy, 0)
            balls.append(((x,y), (0,0), color))
    return balls
        
# Update position base on speed and angle
def move(ball):
    (x, y), (speed, angle) = ball
    x += math.sin(angle) * speed
    y -= math.cos(angle) * speed
    return (x, y), (speed, angle)

# Sum of two vectors
def addVectors(a,b):
    (angle1, length1), (angle2, length2) = a,b    
    x  = math.sin(angle1) * length1 + math.sin(angle2) * length2
    y  = math.cos(angle1) * length1 + math.cos(angle2) * length2
    angle  = 0.5 * math.pi - math.atan2(y, x)
    length = math.hypot(x, y)
    return (angle, length)

# Check if a ball hits the boundery of the environment
def bounce(ball):
    (x, y), (speed, angle) = ball
    # There is only one boundery, the floor
    if y > floor_height - size and y < floor_height:
        if x > floor_start and x < floor_end:
            y = 2*(floor_height - size) - y
            angle = math.pi - angle
            speed *= elasticity
    return (x, y), (speed, angle)

# Change angle and speed by a given vector
def accelerate(ball, vector):
    (x, y), (speed, angle) = ball
    angle, speed = addVectors((angle, speed), vector)
    return (x, y), (speed, angle)

# Draws the paddle
def draw_paddle(img, rotation):
    # This is just trig
    left_paddle_start = bearing_location[0] + math.cos(rotation) * arm_length, bearing_location[1] + math.sin(rotation) * arm_length
    left_paddle_end = bearing_location[0] + math.cos(rotation) * (arm_length + paddle_length), bearing_location[1] + math.sin(rotation) * (arm_length + paddle_length)
    right_paddle_start = bearing_location[0] - math.cos(rotation) * arm_length, bearing_location[1] - math.sin(rotation) * arm_length
    right_paddle_end = bearing_location[0] - math.cos(rotation) * (arm_length + paddle_length), bearing_location[1] - math.sin(rotation) * (arm_length + paddle_length)
    left_paddle_start = tuple(np.array(left_paddle_start, int))
    right_paddle_start = tuple(np.array(right_paddle_start, int))
    left_paddle_end = tuple(np.array(left_paddle_end, int))
    right_paddle_end = tuple(np.array(right_paddle_end, int))
    cv2.line(img, left_paddle_start, left_paddle_end, (234,234,234), 2)
    cv2.line(img, right_paddle_start, right_paddle_end, (234,234,234), 2)

    # Draw the vertical lines at the end of the paddle
    left_line_end = bearing_location[0] + math.cos(rotation-ggg) * (hypot), bearing_location[1] + math.sin(rotation-ggg) * (hypot)
    cv2.line(img, left_paddle_end, tuple(np.array(left_line_end, int)), (234,234,234), 2)
    right_line_end = bearing_location[0] - math.cos(rotation+ggg) * (hypot), bearing_location[1] - math.sin(rotation+ggg) * (hypot)
    cv2.line(img, right_paddle_end, tuple(np.array(right_line_end, int)), (234,234,234), 2)
    return img, (left_paddle_start, left_paddle_end, right_paddle_start, right_paddle_end)

# Distance between two points
def distance(a,b): return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

# Takes a line (in the form of two points) and a point
# Returns true if the point is above the line, false if the point is below the line
def is_above(a, b, point):
    dy, dx = a[1]-b[1], a[0]-b[0]
    intercept = a[1] - a[0]*dy/dx
    #print(point[0]*dy/dx + intercept, dy/dx, intercept) 
    if point[0]*dy/dx + intercept < point[1]: return False
    else: return True        

# Checks for paddle collisions
def paddle_collision(ball, rotation):
    (x, y), (speed, angle) = ball
    collision = False
    
    # Check if the ball hits the line
    right_paddle_start = bearing_location[0] - math.cos(rotation) * arm_length, bearing_location[1] - math.sin(rotation) * arm_length
    right_paddle_end = bearing_location[0] - math.cos(rotation) * (arm_length + paddle_length), bearing_location[1] - math.sin(rotation) * (arm_length + paddle_length)
    
    # Get the location of the paddle
    left_paddle_start = bearing_location[0] + math.cos(rotation) * arm_length, bearing_location[1] + math.sin(rotation) * arm_length
    left_paddle_end = bearing_location[0] + math.cos(rotation) * (arm_length + paddle_length), bearing_location[1] + math.sin(rotation) * (arm_length + paddle_length)

    paddle_start, paddle_end = left_paddle_end, right_paddle_end
    cv2.circle(bg, tuple(np.array(paddle_start, int)), 5, (123,255,255), -1)
    cv2.circle(bg, tuple(np.array(paddle_end, int)), 5, (123,12,12), -1)
    #print(paddle_start, paddle_end)
    dx = paddle_end[0] - paddle_start[0]
    dy = paddle_end[1] - paddle_start[1]
    intercept = paddle_start[1] - paddle_start[0]*dy/dx
    # Check if the ball has hit the line
    #print(abs(ball[0][0]*dy/dx + intercept - ball[0][1]))
    if abs(ball[0][0]*dy/dx + intercept - ball[0][1]) < distance_threshold:
        # Check if the ball is above the line vertically
        hit_right, hit_left, hit_paddle = False, False, False        
        #print(ball[0][0], left_paddle_start[0], left_paddle_end[0], right_paddle_start[0], right_paddle_end[0])
        if ball[0][0] > left_paddle_start[0] and ball[0][0] < left_paddle_end[0]: hit_paddle, hit_left = True, True
        if ball[0][0] < right_paddle_start[0] and ball[0][0] > right_paddle_end[0]: hit_right, hit_paddle = True, True
        if hit_paddle:        
            # Check if the ball is above the line
            if is_above(paddle_start, paddle_end, ball[0]):
                # Ball has hit the line from the top
                angle = -angle + (rotation + angle)
                angle2 = rotation                
                length = distance((x,y), bearing_location)
                if hit_right:
                    if not paddle_up: angle2 = angle2 - math.pi
                    a = bearing_location[0] - math.cos(rotation) * length, bearing_location[1] - math.sin(rotation) * length
                    b = bearing_location[0] - math.cos(rotation+motor_speed) * length, bearing_location[1] - math.sin(rotation+motor_speed) * length
                    speed2 = distance(a, b)
                    angle, speed = addVectors((angle, speed), (angle2, speed2))
                    speed *= paddle_elasticity
                    #cv2.waitKey(0)
                if hit_left:
                    if paddle_up: angle2 = angle2 - math.pi
                    a = bearing_location[0] + math.cos(rotation) * length, bearing_location[1] + math.sin(rotation) * length
                    b = bearing_location[0] +  math.cos(rotation+motor_speed) * length, bearing_location[1] + math.sin(rotation+motor_speed) * length
                    speed2 = distance(a, b)
                    angle, speed = addVectors((angle, speed), (angle2, speed2))
                    speed *= paddle_elasticity
                    #cv2.waitKey(0)
    return (x, y), (speed, angle)

# Checks for paddle end collisions
def paddle_end_collision(ball, rotation):
    (x, y), (speed, angle) = ball
    collision = False
    
    # Check if the ball hits the line
    right_paddle_end = bearing_location[0] - math.cos(rotation) * (arm_length + paddle_length), bearing_location[1] - math.sin(rotation) * (arm_length + paddle_length)
    right_line_end = bearing_location[0] - math.cos(rotation+ggg) * (hypot), bearing_location[1] - math.sin(rotation+ggg) * (hypot)
    
    # Get the location of the paddle
    left_paddle_end = bearing_location[0] + math.cos(rotation) * (arm_length + paddle_length), bearing_location[1] + math.sin(rotation) * (arm_length + paddle_length)
    left_line_end = bearing_location[0] + math.cos(rotation-ggg) * (hypot), bearing_location[1] + math.sin(rotation-ggg) * (hypot)    

    # check for right paddle
    #print(paddle_start, paddle_end)
    dx = right_line_end[0] - right_paddle_end[0]
    dy = right_line_end[1] - right_paddle_end[1]
    intercept = right_paddle_end[1] - right_paddle_end[0]*dy/dx
    # Check if the ball has hit the line
    #print(abs(ball[0][0]*dy/dx + intercept - ball[0][1]))
    if abs(ball[0][0]*dy/dx + intercept - ball[0][1]) < distance_threshold:
        # Check if the ball on the line horizontally    
        if ball[0][1] < right_paddle_end[1] and ball[0][1] > right_line_end[1]:
                # Ball has hit the line from the top
                #angle2 = rotation
                #length = distance((x,y), bearing_location)
                #a = bearing_location[0] - math.cos(rotation) * length, bearing_location[1] - math.sin(rotation) * length
                #b = bearing_location[0] - math.cos(rotation+motor_speed) * length, bearing_location[1] - math.sin(rotation+motor_speed) * length
                #speed2 = distance(a, b)
                #angle, _ = addVectors((angle, 0), (angle2, 0))
                speed *= paddle_elasticity
                angle = -angle + rotation
                x += 10
                #cv2.waitKey(0)

    # check for left paddle
    #print(paddle_start, paddle_end)
    dx = left_line_end[0] - left_paddle_end[0]
    dy = left_line_end[1] - left_paddle_end[1]
    intercept = left_paddle_end[1] - left_paddle_end[0]*dy/dx
    # Check if the ball has hit the line
    #print(abs(ball[0][0]*dy/dx + intercept - ball[0][1]))
    if abs(ball[0][0]*dy/dx + intercept - ball[0][1]) < distance_threshold:
        # Check if the ball on the line horizontally    
        if ball[0][1] < left_paddle_end[1] and ball[0][1] > left_line_end[1]:
                # Ball has hit the line from the top
##                angle = angle + (rotation + angle)                
##                angle2 = rotation
##                speed2 = 0
##                length = distance((x,y), bearing_location)
##                a = bearing_location[0] - math.cos(rotation) * length, bearing_location[1] - math.sin(rotation) * length
##                b = bearing_location[0] - math.cos(rotation+motor_speed) * length, bearing_location[1] - math.sin(rotation+motor_speed) * length
##                speed2 = distance(a, b)
##                angle, _ = addVectors((angle, 0), (angle2, speed2))                
                speed *= paddle_elasticity
                #cv2.waitKey(0)
                angle = -angle + rotation
                x -= 10

                
    return (x, y), (speed, angle)

# Get list of balls
balls = get_balls()
frame_number = 0
# Main loop
while len(balls)>0:

    # Create background
    bg = np.zeros((height, width, 3), np.uint8)
    bg[:,:,:] = 123,123,123
    cv2.line(bg, (floor_start, floor_height),(floor_end, floor_height),(0,0,0),3)

    # Create list to store updated poisitions
    new_balls = []

    # Update the paddle's position
    if paddle_up: current_rotation += motor_speed
    else: current_rotation -= motor_speed
    if abs(current_rotation) > rotation: paddle_up = not paddle_up
    bg, current_paddle_locations = draw_paddle(bg, current_rotation)
            
    for ball in balls:
        color = ball[2]
        ball = ball[0], ball[1]
        vector = 0,-gravity
        ball = move(ball)
        ball = bounce(ball)
        ball = accelerate(ball, vector)
        ball = paddle_collision(ball, current_rotation)
        ball = paddle_end_collision(ball, current_rotation)
        #print(ball)
        
        #print(ball)
        if ball[1][0]!=0 and ball[0][0]>0 and ball[0][0]<width and ball[0][1]>0 and ball[0][1]<height:
            if ball[1][0] < .2 and abs(ball[0][1]-floor_height) < size*1.5: pass
            else: new_balls.append((ball[0], ball[1], color))
        xy = tuple(np.array(ball[0], int))
        cv2.circle(bg, xy, size, color, -1)
        a  = xy
        fff = 12
        b = fff* ball[1][0] * math.sin(ball[1][1]) + ball[0][0], fff * ball[1][0] * math.cos(ball[1][1]) + ball[0][1]
        b = tuple(np.array(b, int))
        cv2.line(bg, a, b, color, 3)
    balls = new_balls
    cv2.imshow('bg', bg)
    vid_writer.write(bg)
    
    frame_number += 1
    k = cv2.waitKey(1)    
    if k == 27: break
cv2.destroyAllWindows()
         

