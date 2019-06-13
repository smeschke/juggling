import cv2, numpy as np, random

# How bright? Lower is more objects detected, higher is fewer. Range is 0 - 255.
brightness_constant = 175

# Capture webcam source
cap = cv2.VideoCapture(0)

# Iterate though each frame of video
while True:
    # Read img from the video
    _, img = cap.read()
    # Convert the image to gray
    imgray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    # Blur the image slightly
    blur = cv2.blur(imgray, (2, 2))
    # Threshold the image (keep only the bright white parts)
    _ ,thresh = cv2.threshold(blur,brightness_constant,255,0)
    # Show the threshold image
    cv2.imshow('thresh', thresh)
    # Find the contours in the thresholded image
    contours, _ = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    # Find the contour centers
    positions = []
    # Iterate though the contours
    for contour in contours:
        try:
            # Find the moments of the contour
            M = cv2.moments(contour)
            # Find the center of the contour
            center = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
            # Draw a circle around the center of the contour
            cv2.circle(img, center, 25, (0,255,0), 5)
        except: pass
        
    # Show the img and wait
    cv2.imshow('img', img)
    k=cv2.waitKey(100)
    if k==27: break
    
# Cleanup
cap.release()
cv2.destroyAllWindows()
