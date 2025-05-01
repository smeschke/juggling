import cv2
import numpy as np
cap = cv2.VideoCapture('/home/smeschke/Desktop/juggling_4_23/5cSpatial_sbs_1800.mp4')
# === CONFIGURATION ===
HSV_LOWER = np.array([0, 167, 133])
HSV_UPPER = np.array([14, 255, 255])
MAX_FRAMES = 30
# Get video properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
if fps == 0: fps = 90  # fallback if webcam returns 0

# Setup video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or 'XVID' for .avi
out = cv2.VideoWriter('/home/smeschke/Desktop/output_segment_overlay.mp4', fourcc, fps, (frame_width, frame_height))

# === INITIALIZE ===

history = []  # Store the last 100 segmented color images

def segment_color(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, HSV_LOWER, HSV_UPPER)
    result = cv2.bitwise_and(frame, frame, mask=mask)
    return result

def segment_mask(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    return cv2.inRange(hsv, HSV_LOWER, HSV_UPPER)

def segment_color(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, HSV_LOWER, HSV_UPPER)
    return cv2.bitwise_and(frame, frame, mask=mask)

segmented_history = []  # Store last 100 segmented COLOR images

while True:
    ret, frame = cap.read()
    #frame = cv2.resize(frame, (345,345))
    
    if not ret:
        break

    # Segment current frame and store it
    segmented = segment_color(frame)
    segmented_history.append(segmented)
    if len(segmented_history) > MAX_FRAMES:
        segmented_history.pop(0)

    # Combine all previous segmented color images
    combined_overlay = np.zeros_like(frame)
    for past in segmented_history:
        # Use max to keep any non-zero color
        combined_overlay = np.maximum(combined_overlay, past)

    # Create a mask from the combined overlay
    overlay_gray = cv2.cvtColor(combined_overlay, cv2.COLOR_BGR2GRAY)
    overlay_mask = cv2.threshold(overlay_gray, 1, 255, cv2.THRESH_BINARY)[1]

    # Apply mask to blend combined_overlay onto the current frame
    inverse_mask = cv2.bitwise_not(overlay_mask)
    background = cv2.bitwise_and(frame, frame, mask=inverse_mask)
    final_frame = cv2.add(background, combined_overlay)

    # Display the result
    cv2.imshow("Segmented History on Current Frame", final_frame)
    cv2.imshow('tes', combined_overlay)
    out.write(final_frame)


    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()

cap.release()
out.release()
cv2.destroyAllWindows()

