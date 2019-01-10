import cv2, math, numpy as np
import cv2, math, numpy as np, pandas as pd, scipy, itertools
from scipy import signal
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

#-------------------- PARAMETERS ----------------------------
global hw, lh, lh_release_point, rh_release_point, test
hw = 1000
gray = 123,123,123
lh = True
select_release_points = False
colors = [(255,255,0),(0,255,255),(255,255,0),(0,255,255)]
left_hand_origin = -200, 0
right_hand_origin = 0, 0
time = 0
time_span = hw/2 - 1
handsize = 5
lh_release_point, rh_release_point = [0],[0]

#-------------------- END PARAMETERS ------------------------

# Mouse callback function
global click_list, x_coords_left, y_coords_left, x_coords_right, y_coords_right
x_coords_left, y_coords_left, x_coords_right, y_coords_right = [],[],[],[]
positions, click_list = [], []
def callback(event, x, y, flags, param):
    if event == 1:
        # User wants to define a release point
        if select_release_points:
            if lh: lh_release_point.append(x - hw/2)
            if not lh: rh_release_point.append(x - hw/2)
        # Add the corrdinate to the appropriate list
        else:
            click_list.append((x,y))
            if split_points((x,y)) == 'top':
                if lh:x_coords_left.append((x,y))
                else: x_coords_right.append((x,y))
            if split_points((x,y)) == 'bottom':
                if lh: y_coords_left.append((x,y))
                else: y_coords_right.append((x,y))
cv2.namedWindow('img')
cv2.setMouseCallback('img', callback)

# Gets a smooth line through a series of points
def get_smooth_line(g):
    points = g.copy()
    points.sort()
    midpoint = (points[0][1] + points[-1][1]) / 2
    points.append((hw/2, midpoint))
    points.append((hw, midpoint))
    points.sort()
    x_values, y_values = zip(*points)
    x=np.array(list(list(zip(*points))[0]))
    y=np.array(list(list(zip(*points))[1]))    
    x_new = np.linspace(x.min(), x.max(),x[-1]-x[0])
    f = interp1d(x, y, kind='quadratic')
    y_smooth=f(x_new)
    return x, y_smooth

# Splits the points up depending
def split_points(point):
    if point[0]>hw/2 and point[1]<hw/2: return 'top'
    if point[0]>hw/2 and point[1]>hw/2: return 'bottom'
    if point[0]<hw/2: return 'invalid'

# Draws a smooth
def draw_smooth_line(x, y_smooth, img, color, time):
    for i in range(len(y_smooth)-1):
        a = i+1 + x[0], int(y_smooth[i+1])      
        b = i   + x[0], int(y_smooth[i])
        cv2.line(img, tuple(np.array(a, int)), tuple(np.array(b, int)), color, 6)
    xy = hw/2+time, y_smooth[time]
    # Circle showing current time
    cv2.circle(img, tuple(np.array(xy, int)), 5, (2,123,255),5)
    return img

# Draws text on an image
def draw_text(img):
    text = 'x component values'
    org = hw/2 + 100, 50
    font, scale, color, thick = cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 1
    cv2.putText(img, text, tuple(np.array(org, int)), font, scale, color, thick, cv2.LINE_AA)
    text = 'y component values'
    org = hw/2 + 100, hw/2 + 50
    cv2.putText(img, text, tuple(np.array(org, int)), font, scale, color, thick, cv2.LINE_AA)
    org = 50,50
    if select_release_points: text = 'select release points'        
    else:
        if lh: text = 'select LEFT hand throw points'
        else: text = 'select RIGHT hand throw points'
    cv2.putText(img, text, tuple(np.array(org, int)), font, scale, color, thick, cv2.LINE_AA)
    return img

# Draw the hand on the image
def draw_hand(x_coords, y_coords, img, handsize, time, origin, release_point):
    x_coord = origin[0] + x_coords[time]
    y_coord = origin[1] + y_coords[time]
    xy = tuple(np.array((x_coord, y_coord), int))
    cv2.circle(img, xy, 5, (234,234,234), 5)
    # Draw the path of the hand
    for i in range(len(y_coords)):
        a = x_coords[i] + origin[0], y_coords[i] + origin[1]
        xy = tuple(np.array(a, int))
        cv2.circle(img, xy, 1, (123,123,123), 1)
    # Draw a the release point
    release_point = int(release_point)
    xy = tuple(np.array((x_coords[release_point] + origin[0],y_coords[release_point] + origin[1]), int))
    cv2.circle(img, xy, 1, (0,0,255), 5)
    return img

# Draws a grid of lines on the image
def draw_grid(img):
    num_lines = 10
    for g in range(num_lines*2):
        a = hw/2  * (1+g) / num_lines
        cv2.line(img, (int(hw/2),int(a)), (hw,int(a)), (123,123,123),1)
    for g in range(num_lines):
        a = hw/2  * (1+g) / num_lines
        cv2.line(img, (int(hw/2 + a),0), (int(hw/2 + a),hw), (123,123,123),1)
    return img

# Iterate through each frame of video
while True:
    # Update the time
    if time < time_span: time += 1
    else: time = 0
    
    # Create blank background image
    img = np.zeros((hw, hw, 3), np.uint8)
    img = draw_grid(img)

    # Draw lines to delinieate the image
    cv2.line(img, (int(hw/2), 0), (int(hw/2), hw), gray, 2)
    cv2.line(img, (int(hw/2), int(hw/2)), (hw, int(hw/2)), gray, 2)
    
    # Iterate through the user defined points
    for point in click_list: cv2.circle(img, point, 5, 255, 5)
    
    coords = [x_coords_left, x_coords_right, y_coords_left, y_coords_right]
    for points, color in zip(coords, colors):
        if len(points)>=2:
            # Draw the line for the x_values
            x, y_smooth = get_smooth_line(points)
            img = draw_smooth_line(x, y_smooth, img, color, time)
  
    # Draw right hand
    if len(x_coords_right)>=2 and len(y_coords_right)>=2:
        _, y = get_smooth_line(y_coords_right)
        _, x = get_smooth_line(x_coords_right)
        img = draw_hand(x, y, img, handsize, time, right_hand_origin, rh_release_point[-1])
    # Draw left hand
    if len(x_coords_left)>=2 and len(y_coords_left)>=2:
        _, y = get_smooth_line(y_coords_left)
        _, x = get_smooth_line(x_coords_left)
        img = draw_hand(x, y, img, handsize, time, left_hand_origin, lh_release_point[-1])
    
    img = draw_text(img)
    cv2.imshow('img', img)
    # Wait, and allow the user to quit with the 'esc' key
    k = cv2.waitKey(1)
    if k == 27: break

    if k == 32: lh = not lh
    if k == ord('r'): select_release_points = not select_release_points

cv2.destroyAllWindows()
