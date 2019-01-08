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
paddle_length = 80
end_length,paddle_height = 60, .2
hypot = math.sqrt((arm_length + paddle_length)**2 + end_length**2) 
end_length = -.6
# Total Rotation and Motor Speed
total_rotation, motor_speed = .15, .0099
# Location and initial state of the paddles
current_rotation, paddle_up = 0, True
# Constants for the environment
gravity, elasticity, paddle_elasticity = .069, .75, .505
# Parameters for the floor that the balls bounce off of
floor_height, floor_start, floor_end = 720,305,1000-305
# Ball size, number, and color
size, num_balls, colors = 12, 5, [(0,255,255),(255,0,255),(255,255,0),(0,255,0),(0,0,255)]
#size, num_balls, colors = 12, 5, []
##for i in range(986):
##    colors.append((0,random.randint(234,255),random.randint(123,255)))
##    colors.append((random.randint(123,255),0,random.randint(234,255)))
##    colors.append((random.randint(123,255),random.randint(234,255),0))
# Ball Spawn Locations
spawn_variance = 0
x_origion, y_origion = bearing_location[0] - (arm_length + paddle_length/2), bearing_location[1] - 5
# Tail length
scale = 20
frame_number, balls, time_between_balls = 0, [], 55
last_ball = -time_between_balls
motor_speed, total_rotation, floor_height, arm_length = (0.0138, 0.506, 537, 250)
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
    right_paddle, left_paddle = calculate_paddle_locations(rotation)
    # Iterate though the paddles
    for paddle_start, paddle_end, line_end in [right_paddle, left_paddle]:
        # Draw a line for each part of the paddle
        cv2.line(img, tuple(np.array(paddle_start, int)), tuple(np.array(paddle_end, int)), (234,234,234), 4)
        cv2.line(img, tuple(np.array(line_end, int)), tuple(np.array(paddle_end, int)), (234,234,234), 4)
    return img

# Distance between two points
def distance(a,b): return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def get_spawn_location(current_rotation):
    # Get current paddle locations  
    (right_paddle_start, right_paddle_end, _), (left_paddle_start, left_paddle_end, _) = calculate_paddle_locations(current_rotation)
    # Calculate the height at the midpoint of the paddle
    midpoint_height = -size + (right_paddle_start[1] + right_paddle_end[1])/2
    return midpoint_height
    

# Checks for paddle collisions
def paddle_collision(ball, current_rotation, previous_current_rotation):
    (x, y), (speed, angle) = ball
    # Get current paddle locations  
    (right_paddle_start, right_paddle_end, _), (left_paddle_start, left_paddle_end, _) = calculate_paddle_locations(current_rotation)
    # Get previous paddle locations
    (pright_paddle_start, pright_paddle_end, _), (pleft_paddle_start, pleft_paddle_end, _) = calculate_paddle_locations(previous_current_rotation)
    # Compute the length from the bearing_location to the ball
    length = distance((x,y), bearing_location)
    # Make the paddles into a list
    right_paddle = (right_paddle_start, right_paddle_end, _), (pright_paddle_start, pright_paddle_end, _)
    left_paddle = (left_paddle_start, left_paddle_end, _), (pleft_paddle_start, pleft_paddle_end, _)
    paddles = [right_paddle, left_paddle]
    # Iterate though the paddles
    for paddle in paddles:
        # Assign human-readable variable names
        (paddle_start, paddle_end, _),(p_paddle_start, p_paddle_end, _) = paddle
        # Check if the ball collides with the paddle
        if ball_line_collision(ball, (paddle_start, paddle_end),(p_paddle_start, p_paddle_end)):
            # Reflect the direction that the ball is traveling
            angle = -angle + (current_rotation + angle)
            # Calculate the point that the ball collides with
            a = bearing_location[0] + math.cos(current_rotation) * length, bearing_location[1] + math.sin(current_rotation) * length
            b = bearing_location[0] +  math.cos(current_rotation+motor_speed) * length, bearing_location[1] + math.sin(current_rotation+motor_speed) * length
            # Calculate the speed of the point that the ball collides with
            speed2 = distance(a, b)
            # Add the vectors - I can't explain this part
            angle, speed = addVectors((angle, speed), (current_rotation, speed2))
            # Dampen the bounce
            speed *= paddle_elasticity        
    return (x, y), (speed, angle)

# Calculates the location of various parts of the paddle base on the paddle's current rotation
def calculate_paddle_locations(rotation):
    # Calculate the locations of the parts of the RIGHT paddle
    right_paddle_start = bearing_location[0] - math.cos(rotation) * arm_length, bearing_location[1] - math.sin(rotation) * arm_length
    right_paddle_end = bearing_location[0] - math.cos(rotation) * (arm_length + paddle_length), bearing_location[1] - math.sin(rotation) * (arm_length + paddle_length)
    right_line_end = bearing_location[0] - math.cos(rotation+paddle_height) * (hypot), bearing_location[1] - math.sin(rotation+paddle_height) * (hypot)
    right_paddle = (right_paddle_start, right_paddle_end, right_line_end)
    
    # Calculate the locations of the parts of the LEFT paddle
    left_paddle_start = bearing_location[0] + math.cos(rotation) * arm_length, bearing_location[1] + math.sin(rotation) * arm_length
    left_paddle_end = bearing_location[0] + math.cos(rotation) * (arm_length + paddle_length), bearing_location[1] + math.sin(rotation) * (arm_length + paddle_length)
    left_line_end = bearing_location[0] + math.cos(rotation-paddle_height) * (hypot), bearing_location[1] + math.sin(rotation-paddle_height) * (hypot)  
    left_paddle = (left_paddle_start, left_paddle_end, left_line_end)

    return right_paddle, left_paddle

# Checks for paddle end collisions
def paddle_end_collision(ball, current_rotation, previous_current_rotation):
    (x, y), (speed, angle) = ball
    # Get locations of paddle
    (_, right_paddle_end, right_line_end), (_, left_paddle_end, left_line_end) = calculate_paddle_locations(current_rotation)
    # Get locations of paddle in previous frame
    (_, pright_paddle_end, pright_line_end), (_, pleft_paddle_end, pleft_line_end) = calculate_paddle_locations(previous_current_rotation)
    # Check for collisions on the left side of the paddle
    if ball_line_collision(ball, (left_paddle_end, left_line_end),(pleft_paddle_end, pleft_line_end)): x, y = x-5, y
    # Check for collisions on the right side of the paddle
    if ball_line_collision(ball, (right_paddle_end, right_line_end),(pright_paddle_end, pright_line_end)): x, y = x+5, y
    return (x, y), (speed, angle)

# Function that checks for a collision between a line and a ball
def ball_line_collision(ball, line1, line2):
    # Create a blank image
    img_line = np.zeros((height, width), np.uint8)
    # Make a four sided polygon that bounds the line and the previous location of the line
    points = np.array([line1[0], line1[1], line2[1], line2[0]])
    cv2.fillPoly(img_line, np.int32([points]), 255)
    # Calculate the area of the polygon
    area_line = sum(sum(img_line))
    # Now, black out the area of the ball
    cv2.circle(img_line, (int(ball[0][0]), int(ball[0][1])), size, 0, -1)
    # Calculate the new area
    area_ball_line = sum(sum(img_line))
    # If the areas are the same, they do not overlapp, and there is no collision
    if area_line != area_ball_line: return True
    else: return False
    
previous_current_rotation, data, juggling = 0, [], True
# Main Loop
while juggling:

    # If there are fewer than the desired number of balls in the environment, try to add one
    if len(balls) < num_balls:
        # If the paddle is in the right part of the stroke, and it has been a partial stroke since the last ball
        if abs(current_rotation)<.1 and paddle_up and abs(frame_number-last_ball) > time_between_balls:
            if len(colors) > 0:
                # Add a ball
                xy = x_origion + random.randint(-spawn_variance, spawn_variance), get_spawn_location(current_rotation)
                balls.append((xy, (0,0), colors.pop(0)))
                # Reset the variable that tracks when the last ball was dropped
                last_ball = frame_number
        # If there are no more balls stop juggling and quit the program
        if len(colors)==0 and len(balls) == 0: juggling = False
        
        
    # Create background
    bg = np.zeros((height, width, 3), np.uint8)
    bg[:,:,:] = 12,12,12
    cv2.line(bg, (floor_start, floor_height),(floor_end, floor_height),(234,234,234),3)

    # Create list to store updated poisitions
    new_balls = []

    # Update the paddle's position
    if paddle_up: current_rotation += motor_speed
    else: current_rotation -= motor_speed
    # If the paddle has reached it's maximum rotation, change direction
    if abs(current_rotation) > total_rotation: paddle_up = not paddle_up
    # Draw paddle
    bg = draw_paddle(bg, current_rotation)

    current_positions = []


    # Iterate though each ball and apply movement, gravity, bounce, and collisions
    for ball in balls:        
        color = ball[2]
        ball = ball[0], ball[1]
        current_positions.append(ball[0])
        vector = 0,-gravity
        ball = move(ball)
        ball = bounce(ball)
        ball = accelerate(ball, vector)
        ball = paddle_collision(ball, current_rotation, previous_current_rotation)
        ball = paddle_end_collision(ball, current_rotation, previous_current_rotation)

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
        #cv2.line(bg, tuple(np.array((x,y), int)), tuple(np.array(vector_end, int)), color, 5)

    # Update list of balls
    balls = new_balls
    while len(current_positions) < num_balls: current_positions.append((0,0))
    data.append(current_positions)

    # Show Image and Wait
    cv2.imshow('bg', bg)
    #if frame_number>2 and frame_number%2 ==0: vid_writer.write(cv2.addWeighted(bg, .5, p_img, .5, 1))
    vid_writer.write(bg)
    p_img = bg.copy()
    frame_number += 1
    k = cv2.waitKey(1)
    # Use left hand to adjust movement (speed and total rotation)
    if k == ord('e'): motor_speed += .001
    if k == ord('d'): motor_speed -= .001
    if k == ord('f'): total_rotation += .001
    if k == ord('s'): total_rotation -= .001
    # Use the right hand to adjust the paddle length and bounce floor elevation
    if k == ord('i'): arm_length += 1
    if k == ord('k'): arm_length -= 1
    if k == ord('j'): floor_height += 1
    if k == ord('l'): floor_height -= 1
    # Spacebar to clear the balls
    if k == 32: balls = []    
    if k != -1: print('motor_speed: '+ str(motor_speed), ' total_rotation: ' + str(total_rotation), ' floor_height: ' + str(floor_height), ' arm_length: ' + str(arm_length))
    if k == 27: break

    # Remember the previous rotation
    previous_current_rotation = current_rotation
cv2.destroyAllWindows()

# Write the data
import pandas as pd
a,b,c,d,e = zip(*data)
for idx, data in zip([1,2,3,4,5],[a,b,c,d,e]):
    print(idx, len(data))
    df = pd.DataFrame(np.array(data))
    df.to_csv('/home/stephen/Desktop/data/'+str(idx)+'.csv', index = False)
