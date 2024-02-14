# Import the required modules
import cv2
import numpy as np

# Define the HSV lower and upper bounds for the color of the leads
lower_hsv = np.array([0, 0, 0])
upper_hsv = np.array([179, 255, 255])

# Create a window to display the video and the trackbars
cv2.namedWindow('Video')
cv2.createTrackbar('Hue min', 'Video', lower_hsv[0], 179, lambda x: None)
cv2.createTrackbar('Hue max', 'Video', upper_hsv[0], 179, lambda x: None)
cv2.createTrackbar('Sat min', 'Video', lower_hsv[1], 255, lambda x: None)
cv2.createTrackbar('Sat max', 'Video', upper_hsv[1], 255, lambda x: None)
cv2.createTrackbar('Val min', 'Video', lower_hsv[2], 255, lambda x: None)
cv2.createTrackbar('Val max', 'Video', upper_hsv[2], 255, lambda x: None)

# Capture the video from the webcam
#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture('./videos/video1.mp4')   #comment and switch to webcam
for i in range(0, 20):
	(grabbed, frame) = cap.read()
# Loop until the user presses 'q' key
while True:
    # Read a frame from the video
    ret, frame = cap.read()
    
    # Check if the frame is valid
    if not ret:
        break
    frame = cv2.resize(frame, (720, 580))  # added for ic
    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Get the trackbar values
    lower_hsv[0] = cv2.getTrackbarPos('Hue min', 'Video')
    upper_hsv[0] = cv2.getTrackbarPos('Hue max', 'Video')
    lower_hsv[1] = cv2.getTrackbarPos('Sat min', 'Video')
    upper_hsv[1] = cv2.getTrackbarPos('Sat max', 'Video')
    lower_hsv[2] = cv2.getTrackbarPos('Val min', 'Video')
    upper_hsv[2] = cv2.getTrackbarPos('Val max', 'Video')

    # Create a mask based on the HSV range
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
    
    
    # Find the contours of the masked image
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    

    # Loop over the contours
    for cnt in contours:
        # Calculate the area of the contour
        area = cv2.contourArea(cnt)

        # Filter out small or large areas
        if area < 50 or area > 2000:
            continue

        # Draw a bounding rectangle around the contour
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
      
        # Calculate the width and length of the lead in pixels
        lead_width = w
        lead_length = h
        ##print (lead_width,lead_length)
        # Perform judgement control on measured dimensions
        # You can define your own criteria and logic here
        # For example, if the lead width is less than 10 pixels or more than 20 pixels,
        # then mark it as defective with a red circle
        #if lead_width < 10 or lead_width > 20:
        if lead_width >5 :    
            cv2.circle(frame, (x + w // 2, y + h // 2), 3, (0, 0, 255), -1)
            cv2.putText(frame, f"Width: {lead_width:.2f} px", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.putText(frame, f"Length: {lead_length:.2f} px", (x + w , y + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            print (lead_width,lead_length)
        

    # Display the original frame and the masked frame
    cv2.imshow('Video', frame)
    cv2.imshow('Mask', mask)

    # Wait for a key press
    key = cv2.waitKey(2) & 0xFF

  

# Release the video capture object and destroy all windows
cap.release()
cv2.destroyAllWindows()


