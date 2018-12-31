import cv2, numpy as np, math

global size, width, height, bearing_location, arm_length, paddle_length, paddle_height, rotation, motor_speed, drive_arm_motor, drive_arm_paddle, gravity, mass, elasticity
width, height = 987,987
bearing_location = width/2,456
arm_length = 234
paddle_length, paddle_height = 234,56
rotation = .2
motor_speed = .01
current_rotation = .01
paddle_up = True
gravity = .01
seed_locations = []
size = 10
balls = [[(123,12),(0,0)],[(789,-102),(0,0)]] # list of balls that contains a [(ball_x, ball_y), (speed, angle)]
mass = 10
elasticity = .8
drag = 1

# Particle experiences drag
def experienceDrag(ball):
    (x, y), (speed, angle) = ball
    speed *= drag
    return (x, y), (speed, angle)

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

# Function that checks for collisions between balls
def collide(p1, p2):
    """ Tests whether two particles overlap
        If they do, make them bounce, i.e. update their angle, speed and position """
    dx, dy = p1[0][0] - p2[0][0], p1[0][1] - p2[0][1]    
    dist = math.hypot(dx, dy)
    # Check if particles overlap
    if dist < size * 2:
        angle = math.atan2(dy, dx) + 0.5 * math.pi
        total_mass = mass + mass

        # Make them bounce (Update speed and angle)
        (p1[1][1], p1[1][0]) = addVectors((p1[1][1], p1[1][0]*(mass-mass)/(2*mass)), (angle, 2*p2[1][0]*mass/(2*mass)))
        (p2[1][1], p2[1][1]) = addVectors((p2[1][1], p2[1][0]*(mass-mass)/(2*mass)), (angle+math.pi, 2*p1[1][0]*mass/(2*mass)))
        elasticity = elasticity * elasticity
        p1[1][0] *= elasticity
        p2[1][0] *= elasticity

        # Update position
        overlap = 0.5*(p1.size + p2.size - dist+1)
        p1[0][0] += math.sin(angle)*overlap
        p1[0][1] -= math.cos(angle)*overlap
        p2[0][0] -= math.sin(angle)*overlap
        p2[0][1] += math.cos(angle)*overlap

    # Return collided or uncollided points
    return p1, p2

# Check if a ball hits the boundery of the environment
def bounce(ball):
    (x, y), (speed, angle) = ball    
    if x > width - size:
        x = 2*(width - size) - x
        angle = - angle
        speed *= elasticity

    elif x < size:
        x = 2*size - x
        angle = - angle
        speed *= elasticity

    if y > height - size:
        y = 2*(height - size) - y
        angle = math.pi - angle
        speed *= elasticity

    elif y < size:
        y = 2*size - y
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
    return img, (left_paddle_start, left_paddle_end, right_paddle_start, right_paddle_end)

def distance(a,b): return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

# Checks for paddle collisions
def paddle_collision(ball, rotation):
    (x, y), (speed, angle) = ball
    collision = False
    # Check if the ball hits the line
    right_paddle_start = bearing_location[0] - math.cos(rotation) * arm_length, bearing_location[1] - math.sin(rotation) * arm_length
    right_paddle_end = bearing_location[0] - math.cos(rotation) * (arm_length + paddle_length), bearing_location[1] - math.sin(rotation) * (arm_length + paddle_length)
    dx = right_paddle_end[0] - right_paddle_start[0]
    dy = right_paddle_end[1] - right_paddle_start[1]
    steps = 654
    distances = []
    for i in range(steps):
        fff = i/steps
        x_position = dx * fff + right_paddle_start[0]
        y_position = dy * fff + right_paddle_start[1]
        # Check for collision
        distances.append(distance((x_position, y_position), ball[0]))
        if distance((x_position, y_position), ball[0]) < size:
            # There has been a collision
            collision =  True
            angle = -angle + (rotation - angle)

    left_paddle_start = bearing_location[0] + math.cos(rotation) * arm_length, bearing_location[1] + math.sin(rotation) * arm_length
    left_paddle_end = bearing_location[0] + math.cos(rotation) * (arm_length + paddle_length), bearing_location[1] + math.sin(rotation) * (arm_length + paddle_length)
    dx = left_paddle_end[0] - left_paddle_start[0]
    dy = left_paddle_end[1] - left_paddle_start[1]
    steps = 123
    for i in range(steps):
        fff = i/steps
        x_position = dx * fff + left_paddle_start[0]
        y_position = dy * fff + left_paddle_start[1]        
        # Check for collision
        distances.append(distance((x_position, y_position), ball[0]))
        if distance((x_position, y_position), ball[0]) < size:
            # There has been a collision
            collision =  True
            angle = -angle + (rotation + angle)
    return (x, y), (speed, angle)
    
while True:
    # Create background
    bg = np.zeros((height, width, 3), np.uint8)
    bg[:,:,:] = 123,123,123

    # Create list to store updated poisitions
    new_balls = []

    # Update the paddle's position
    if paddle_up: current_rotation += motor_speed
    else: current_rotation -= motor_speed
    if abs(current_rotation) > rotation: paddle_up = not paddle_up
    bg, current_paddle_locations = draw_paddle(bg, current_rotation)
            
    for ball in balls:
        vector = 0,-.1
        ball = move(ball)
        ball = bounce(ball)
        ball = accelerate(ball, vector)
        ball = paddle_collision(ball, current_rotation)
        print(ball)
        new_balls.append(ball)
        xy = tuple(np.array(ball[0], int))
        cv2.circle(bg, xy, size, 255, -1)
    balls = new_balls
    cv2.imshow('bg', bg)

    
    k = cv2.waitKey(1)

    
    if k == 27: break
cv2.destroyAllWindows()
         

