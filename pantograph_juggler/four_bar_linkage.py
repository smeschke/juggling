import cv2
import numpy as np
import random
import math

# Parameters
hw = 1000
sholder = 300,200
motor_position = 450,400
major_linkage = 400
minor_linkage = 200
motor_cam_length = 55
minor_linkage_floor = sholder[1]+minor_linkage/2

# Variables used in program
angle = 0
increment = .09
iters = .001
vid_writer = cv2.VideoWriter('/home/stephen/Desktop/writer.avi',
                             cv2.VideoWriter_fourcc('M','J','P','G'), 20, (1000,1000))
# Calculates rotations for a part that is fixed on one end
def calculage_rotations_endpoint(fixed_point, length, iters):
    rotations, rotation = [], 0
    while rotation < 2*math.pi:
        x = math.sin(rotation)*length + fixed_point[0]
        y = math.cos(rotation)*length + fixed_point[1]
        rotations.append(((x,y),(fixed_point)))
        rotation += iters
    return rotations

# Calculates rotations for a part that is fixed in the middle
def calculate_rotations_midpoint(fixed_point, length, iters):
    rotations, rotation = [], 0
    while rotation < math.pi*2.0:
        # Calculate one endpoint
        x = math.sin(rotation)*length + fixed_point[0]
        y = math.cos(rotation)*length + fixed_point[1]
        # Calculate the other endpoint
        x1 = math.sin(rotation - math.pi)*length + fixed_point[0]
        y1 = math.cos(rotation - math.pi)*length + fixed_point[1]
        rotations.append(((x,y),(x1,y1)))
        rotation += iters
    return rotations

# Distance between two points
def distance(a,b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

# Calculate position of minor linkage
def calculate_drive_and_minor_arm_position(motor_position, sholder, hardline):
    # Get the possible positions of the drive arm
    drive_arm_positions = calculate_rotations_midpoint(motor_position, minor_linkage, iters)
    drive_arm_position = find_best_positions(drive_arm_positions, minor_linkage, sholder, hardline)
    minor_arm_position = sholder, drive_arm_position[0]
    return drive_arm_position, minor_arm_position

# Calculate position of connecting arm
def calculate_connecting_arm_position(drive_arm_position, sholder, hardline):
    # Calculate all connecting arm positions
    connecting_arm_positions = calculate_rotations_midpoint(drive_arm_position[1], minor_linkage, iters)
    connecting_arm_position = find_best_positions1(connecting_arm_positions, major_linkage, sholder, hardline)
    return connecting_arm_position

# Calculate slope
def calc_slope(position):
    a,b = position
    return (a[1]-b[1]) / (a[1]-b[0])

# Find the best fit in all the positions
def find_best_positions(positions, length, fixed_point, hardline):
    best_score = 12345678
    best_positions = (0,0), (0,0)
    # Iterate through all the positions
    for position in positions:
        score = abs(length - distance(fixed_point, position[0]))
        if score < best_score and position[0][1] < hardline:
            best_score = score
            best_positions = position
    return best_positions

# Find the best fit in all the positions
def find_best_positions1(positions, length, fixed_point, hardline):
    best_score = 12345678
    best_positions = (0,0), (0,0)
    for position in positions:
        score = abs(length*.8 - distance(fixed_point, position[0]))
        #print(position, slope)
        if score < best_score and position[0][0] < hardline:
            best_score = score
            best_positions = position
    return best_positions

# Main Loop
img = np.zeros((1000,1000,3), np.uint8)
while True: 
    x = math.sin(angle)*motor_cam_length + motor_position[0]
    y = math.cos(angle)*motor_cam_length + motor_position[1]
    drive_arm, minor_arm = calculate_drive_and_minor_arm_position((x,y), sholder, minor_linkage_floor)
    colors = [(255,255,255),(0,255,0),(123,123,123),(255,255,0)]
    center = int(x), int(y)
    radius, color, thickness = 1,(255,255,255),2
    cv2.circle(img, center, radius, color, thickness)
    bg = img.copy()
    radius, color, thickness = 15,(255,0,255),22
    cv2.circle(bg, center, radius, color, thickness)

    connecting_arm = calculate_connecting_arm_position(drive_arm, sholder,motor_position[0])
    test = sholder, connecting_arm[0]                
    for a,b in [drive_arm, minor_arm, connecting_arm, test]:      
        a = int(a[0]), int(a[1])
        b = int(b[0]), int(b[1])
        cv2.line(bg, a, b, colors.pop(), 16)
    a = connecting_arm[1]
    a = int(a[0]), int(a[1])
    center = a
    cv2.circle(img, center, 0, (0,234,123), 2)

    a = connecting_arm[1]
    a = int(a[0]), int(a[1])
    center = a
    
    #cv2.circle(bg, center, 45, (234,123,234), 0)


    vid_writer.write(bg)
    cv2.imshow('img', bg)
    k = cv2.waitKey(1)
    if angle > 4*math.pi: break
    if k == 27: break
    angle += increment
cv2.destroyAllWindows()
    
    
