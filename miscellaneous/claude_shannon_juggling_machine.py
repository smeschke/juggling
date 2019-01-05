import cv2, numpy as np, math, random
# ------------------------ PARAMETERS --------------------------------
global size, width, height, bearing_location, arm_length, paddle_length, x_origion, y_origion
global paddle_height, rotation, motor_speed, drive_arm_motor, end_length, paddle_height
global drive_arm_paddle, gravity, mass, elasticity, paddle_elasticity, n_balls, ball_space
# Size of the window
width, height = 1000,1000
# Location of the bearing that the arm rotates about
bearing_location = width/2,450
# Length from bearing to start of paddle
arm_length = 250
# Length of the paddle
paddle_length = 150
end_length,paddle_height = 120, .4
hypot = math.sqrt((arm_length + paddle_length)**2 + end_length**2) + 15
end_length = -.6
# Total Rotation and Motor Speed
total_rotation, motor_speed = .71, .0076
# Location and initial state of the paddles
current_rotation, paddle_up = 0, True
# Constants for the environment
gravity, elasticity, paddle_elasticity = .069, .8, .55
# Parameters for the floor that the balls bounce off of
floor_height, floor_start, floor_end = 720,305,1000-305
# Ball size, number, and color
size, num_balls, colors = 10, 3, [(0,255,255),(255,0,255),(255,255,0),(0,255,0),(0,0,255),(123,0,255),(0,255,255),(255,255,0),(255,0,0),(0,255,0),(0,0,255),(123,0,255),(0,255,255),(255,255,0),(255,0,0),(0,255,0),(0,0,255),(123,0,255),(0,255,255),(255,255,0),(255,0,0),(0,255,0),(0,0,255),(123,0,255)]
distance_threshold = size*.8
# Ball Spawn Locations
x_origion, y_origion = bearing_location[0] - arm_length - paddle_length + 30, bearing_location[1] - 30
# Tail length
scale = 20
frame_number, last_ball, balls, time_between_balls = 0, 0, [], 123
# ------------------------END PARAMETERS --------------------------------

vid_writer = cv2.VideoWriter('/home/stephen/Desktop/test.avi', cv2.VideoWriter_fourcc('M','J','P','G'), 120, (width,height))
        
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

# Check if a ball hits the floor in the environment
def bounce(ball):
    (x, y), (speed, angle) = ball
    # Check if the ball is above the floor, and touching the floor
    if y > floor_height - size and y < floor_height:
        # Check if the ball is vertically aligned with the floor
        if x > floor_start and x < floor_end:
            # Update the ball's y position
            y = 2*(floor_height - size) - y
            # Update angle (this only affects the y component of ball's vector)
            angle = math.pi - angle
            # Disapate some of the energy to the bounce
            speed *= elasticity
    return (x, y), (speed, angle)

# Change angle and speed by a given vector - Used to apply gravity
def accelerate(ball, vector):
    (x, y), (speed, angle) = ball
    angle, speed = addVectors((angle, speed), vector)
    return (x, y), (speed, angle)

# Draws the paddle
def draw_paddle(img, rotation):
    # Get paddle locations
    (right_paddle_start, right_paddle_end, right_line_end, right_slope, right_intercept), (left_paddle_start, left_paddle_end, left_line_end, left_slope, left_intercept) = calculate_paddle_locations(rotation)
    # Draw lines and circles
    cv2.line(img, tuple(np.array(left_paddle_start, int)), tuple(np.array(left_paddle_end, int)), (234,234,234), 2)
    cv2.line(img, tuple(np.array(right_paddle_start, int)), tuple(np.array(right_paddle_end, int)), (234,234,234), 2)
    cv2.line(img, tuple(np.array(left_paddle_end, int)), tuple(np.array(left_line_end, int)), (234,234,234), 2)
    cv2.line(img, tuple(np.array(right_paddle_end, int)), tuple(np.array(right_line_end, int)), (234,234,234), 2)
    cv2.circle(bg, tuple(np.array(left_paddle_end, int)), 5, (123,255,255), -1)
    cv2.circle(bg, tuple(np.array(right_paddle_end, int)), 5, (255,0,0), -1)
    return img

# Distance between two points
def distance(a,b): return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

# Checks for paddle collisions
def paddle_collision(ball, rotation):
    (x, y), (speed, angle) = ball
    # Get paddle Locations
    (right_paddle_start, right_paddle_end, right_line_end, right_slope, right_intercept), (left_paddle_start, left_paddle_end, left_line_end, left_slope, left_intercept) = calculate_paddle_locations(rotation)
    
    # Check if the ball collides with the line that connects the paddles
    if abs(x*left_slope + left_intercept - y) < distance_threshold:
        hit_right, hit_left, hit_paddle = False, False, False
        # Determine which paddle the ball is positioned over
        if x > left_paddle_start[0] and x < left_paddle_end[0]: hit_paddle, hit_left = True, True
        if x < right_paddle_start[0] and x > right_paddle_end[0]: hit_right, hit_paddle = True, True
        # If the ball hits either paddle
        if hit_paddle:
            # Reflect the direction that the ball is traveling
            angle = -angle + (rotation + angle)
            angle2 = rotation
            # Calculate distance from the center of the bearing to the ball
            length = distance((x,y), bearing_location)
            if hit_right:
                # Reverse the angle of the paddle if it is going down
                if not paddle_up: angle2 = angle2 - math.pi
                # Calculate the point that the ball collides with
                a = bearing_location[0] - math.cos(rotation) * length, bearing_location[1] - math.sin(rotation) * length
                b = bearing_location[0] - math.cos(rotation+motor_speed) * length, bearing_location[1] - math.sin(rotation+motor_speed) * length
            if hit_left:
                # Reverse the angle of the paddle if it is going up
                if paddle_up: angle2 = angle2 - math.pi
                # Calculate the point that the ball collides with
                a = bearing_location[0] + math.cos(rotation) * length, bearing_location[1] + math.sin(rotation) * length
                b = bearing_location[0] +  math.cos(rotation+motor_speed) * length, bearing_location[1] + math.sin(rotation+motor_speed) * length
            # Calculate the speed of the point that the ball collides with
            speed2 = distance(a, b)
            # Add the vectors
            angle, speed = addVectors((angle, speed), (angle2, speed2))
            # Dampen the bounce
            speed *= paddle_elasticity
    return (x, y), (speed, angle)

# Calculates the location of various parts of the paddle base on the paddle's current rotation
def calculate_paddle_locations(rotation):
    # Check if the ball hits the line
    right_paddle_start = bearing_location[0] - math.cos(rotation) * arm_length, bearing_location[1] - math.sin(rotation) * arm_length
    right_paddle_end = bearing_location[0] - math.cos(rotation) * (arm_length + paddle_length), bearing_location[1] - math.sin(rotation) * (arm_length + paddle_length)
    right_line_end = bearing_location[0] - math.cos(rotation+paddle_height) * (hypot), bearing_location[1] - math.sin(rotation+paddle_height) * (hypot)
    right_dx, right_dy = right_paddle_end[0] - right_paddle_start[0], right_paddle_end[1] - right_paddle_start[1]    
    right_intercept = right_paddle_start[1] - right_paddle_start[0]*right_dy/right_dx
    
    # Get the location of the paddle
    left_paddle_start = bearing_location[0] + math.cos(rotation) * arm_length, bearing_location[1] + math.sin(rotation) * arm_length
    left_paddle_end = bearing_location[0] + math.cos(rotation) * (arm_length + paddle_length), bearing_location[1] + math.sin(rotation) * (arm_length + paddle_length)
    left_line_end = bearing_location[0] + math.cos(rotation-paddle_height) * (hypot), bearing_location[1] + math.sin(rotation-paddle_height) * (hypot)
    left_dx, left_dy = left_paddle_end[0] - left_paddle_start[0], left_paddle_end[1] - left_paddle_start[1]    
    left_intercept = left_paddle_start[1] - left_paddle_start[0]*left_dy/left_dx

    right_paddle = (right_paddle_start, right_paddle_end, right_line_end, right_dy/right_dx, right_intercept)
    left_paddle = (left_paddle_start, left_paddle_end, left_line_end, left_dy/left_dx, left_intercept)

    return right_paddle, left_paddle

# Checks for paddle end collisions
def paddle_end_collision(ball, rotation):
    (x, y), (speed, angle) = ball
    (right_paddle_start, right_paddle_end, right_line_end, right_slope, right_intercept), (left_paddle_start, left_paddle_end, left_line_end, left_slope, left_intercept) = calculate_paddle_locations(rotation)    

    # Check for right paddle
    dx = right_line_end[0] - right_paddle_end[0]
    dy = right_line_end[1] - right_paddle_end[1]
    intercept = right_paddle_end[1] - right_paddle_end[0]*dy/dx
    # Check if the ball has hit the line
    if abs(x*dy/dx + intercept - y) < distance_threshold:
        # Check if the ball on the line horizontally    
        if y < right_paddle_end[1] and y > right_line_end[1]:
            x, y = x+30, y-5
            angle = angle + rotation               
            speed *= paddle_elasticity

    # check for left paddle
    dx = left_line_end[0] - left_paddle_end[0]
    dy = left_line_end[1] - left_paddle_end[1]
    intercept = left_paddle_end[1] - left_paddle_end[0]*dy/dx
    # Check if the ball has hit the line
    if abs(x*dy/dx + intercept - y) < distance_threshold:
        # Check if the ball on the line horizontally    
        if y < left_paddle_end[1] and y > left_line_end[1]:                
            x, y = x-30, y-5
            angle = -angle + rotation    
            speed *= paddle_elasticity
        
    return (x, y), (speed, angle)

# Main Loop
while True:

    # If there are fewer than the desired number of balls in the environment, try to add one
    if len(balls) < num_balls:
        # If the paddle is in the right part of the stroke, and it has been a partial stroke since the last ball
        if abs(current_rotation)<.04 and paddle_up and abs(frame_number-last_ball) > time_between_balls:
            # Add a ball
            balls.append(((x_origion , y_origion), (0,0), colors.pop(0)))
            # Reset the variable that tracks when the last ball was dropped
            last_ball = frame_number
        
    # Create background
    bg = np.zeros((height, width, 3), np.uint8)
    bg[:,:,:] = 123,123,123
    cv2.line(bg, (floor_start, floor_height),(floor_end, floor_height),(0,0,0),3)

    # Create list to store updated poisitions
    new_balls = []

    # Update the paddle's position
    if paddle_up: current_rotation += motor_speed
    else: current_rotation -= motor_speed
    # If the paddle has reached it's maximum rotation, change direction
    if abs(current_rotation) > total_rotation: paddle_up = not paddle_up
    # Draw paddle
    bg = draw_paddle(bg, current_rotation)

    # Iterate though each ball and apply movement, gravity, bounce, and collisions
    for ball in balls:
        color = ball[2]
        ball = ball[0], ball[1]
        vector = 0,-gravity
        ball = move(ball)
        ball = bounce(ball)
        ball = accelerate(ball, vector)
        ball = paddle_collision(ball, current_rotation)
        ball = paddle_end_collision(ball, current_rotation)

        # Check if the ball has bounced out of the environment
        (x, y), (speed, angle) = ball
        if speed!=0 and x>0 and x<width and y>0 and y<height:
            # Check if ball is resting on bouncing surface
            if speed < .2 and abs(y-floor_height) < size*1.5: pass
            # Ball is currently being juggled and should remain in play
            else: new_balls.append((ball[0], ball[1], color))
        # Draw the ball
        cv2.circle(bg, tuple(np.array((x,y), int)), size, color, -1)

        # Draw speed and angle using a vector
        vector_end = x + math.cos(angle+math.pi/2)*scale*speed, y + math.sin(angle+math.pi/2)*scale*speed        
        cv2.line(bg, tuple(np.array((x,y), int)), tuple(np.array(vector_end, int)), color, 5)

    # Update list of balls
    balls = new_balls

    # Show Image and Wait
    cv2.imshow('bg', bg)
    if frame_number>2 and frame_number%2 ==0: vid_writer.write(cv2.addWeighted(bg, .5, p_img, .5, 1))
    p_img = bg.copy()
    frame_number += 1
    k = cv2.waitKey(1)
    if k == 115: print(frame_number)
    if k == 27: break
cv2.destroyAllWindows()
