import cv2, math, numpy as np

# Path to source video:
output_path = '/home/stephen/Desktop/1.csv'
cap = cv2.VideoCapture('/home/stephen/Desktop/source_vids/ss3_id_110.MP4')

# Mouse callback function
global click_list
positions, click_list = [], []
def callback(event, x, y, flags, param):
    if event == 1: click_list.append((x,y))
cv2.namedWindow('img')
cv2.setMouseCallback('img', callback)

# ROI - Region of Interest (where the juggling ball is)

# Define the size of the roi
roi_size = 200
# Make the roi size easier to see
roi_factor = 4
# Define the offset of the roi
x_offset, y_offset = 0,0
proceed_to_next_frame = True

# Iterate through each frame of video
while True:
    # If a user has made a click
    if proceed_to_next_frame:
        # Read frame of video
        _, img = cap.read()
        # Break if the video is over
        try:h,w,e = img.shape
        except: break

    # Get the length of the click_list
    click_list_length = len(click_list)

    # Draw the previous ball positions on the screen
    try:
        for idx in range(35):
            a = positions[-(idx+2)][0], positions[-(idx+2)][1]
            b = positions[-(idx+1)][0], positions[-(idx+1)][1]
            cv2.line(img, a,b, (0,255,255), 3)
            cv2.circle(img, b, 2, 255, 2)
    except: pass

    # If the user has past the first frame, create the ROI
    if len(positions)>0:
        # Get the previous position
        x_offset, y_offset = positions[-1]
        # Create a background that is bigger than the roi - avoid error when ball nears edge
        bg = np.zeros((img.shape[0]+roi_size, img.shape[1]+roi_size, 3), np.uint8)
        # Paste the image onto the background
        bg[int(roi_size/2):int(roi_size/2)+img.shape[0], int(roi_size/2):int(roi_size/2)+img.shape[1]] = img
        # Get the roi from the background
        roi = bg[y_offset:y_offset+roi_size, x_offset:x_offset+roi_size]
        #create crosshairs on roi
        cv2.line(roi, (int(roi_size/2),0), (int(roi_size/2),roi_size), (123,234,123), 1)
        cv2.line(roi, (0,int(roi_size/2)), (roi_size,int(roi_size/2)), (123,234,123), 1)
        roi_h, roi_w, _ = roi.shape
        roi = cv2.resize(roi, (roi_w * roi_factor, roi_h * roi_factor))
    
    # Show frame
    if len(positions) == 0: cv2.imshow('img', img)
    else: cv2.imshow('img', roi)
    
    # Wait, and allow the user to quit with the 'esc' key
    k = cv2.waitKey(1)
    if k == 27: break    
    
    # Check if there has been a new click
    if click_list_length != len(click_list):
        # There has been a new click! Get the value
        user_input = click_list[-1]
        # Did the user click on the roi?
        if len(positions) != 0 :
            # Resize the users click back to the coordinate system of the source image
            user_input = click_list[-1]
            user_input = int(user_input[0]/roi_factor),int(user_input[1]/roi_factor)
            user_input = x_offset + user_input[0] - int(roi_size/2), y_offset + user_input[1] - int(roi_size/2)        

        # Add the ball position to the data
        positions.append(user_input)
        # Print
        print(user_input, x_offset, y_offset)
        # Tell the program to go to the next image
        proceed_to_next_frame = True
    else: proceed_to_next_frame = False

cv2.destroyAllWindows()
cap.release()

print ('finished tracking')

#write data
import csv
with open(output_path, 'w') as csvfile:
    fieldnames = ['x_position', 'y_position']
    writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
    writer.writeheader()
    for position in positions:
        x, y = position[0], position[1]
        writer.writerow({'x_position': x, 'y_position': y})

print( 'finished writing data')
