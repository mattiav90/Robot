import cv2
print(cv2.__version__)

dispW = 800
dispH = 500
flip = 2

# Uncomment These next Two Lines for Pi Camera
camSet = 'nvarguscamerasrc !  video/x-raw(memory:NVMM), \
        width=3264, height=2464, format=NV12, \
        framerate=21/1 ! nvvidconv flip-method=' + str(flip) + ' ! video/x-raw, \
        width=' + str(dispW) + ', height=' + str(dispH) + ', \
        format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink'

cam = cv2.VideoCapture(camSet)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, dispW)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, dispH)

# Or, if you have a WEB cam, uncomment the next line
# cam = cv2.VideoCapture(0)

while True:
    # Grab image
    ret, img = cam.read()
    if not ret:
        break

    # Plot image
    cv2.imshow('nanoCam', img)

    # Set position
    cv2.moveWindow('nanoCam', 0, 0)

    # Convert to gray
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Find edges
    edges = cv2.Canny(gray, 100, 200)

    # Use Hough Transform to detect lines
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)

    # Create a copy of the original image to draw lines on
    line_image = np.zeros_like(img)

    # Check if any lines are detected
    shape_detected = False

    # Draw detected lines on the image
    if lines is not None:
        shape_detected = True  # Set flag if lines are detected
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Draw lines in green

    # Combine the original image with the line image
    combined = cv2.addWeighted(img, 0.8, line_image, 1, 0)

    # Plot image with lines
    cv2.imshow('Detected Lines', combined)
    cv2.moveWindow('Detected Lines', 0, 500)

    # Activate GPIO if a shape is detected
    if shape_detected:
        GPIO.output(output_pin, GPIO.HIGH)  # Activate output
    else:
        GPIO.output(output_pin, GPIO.LOW)  # Deactivate output

    if cv2.waitKey(1) == ord('q'):
        break

# Cleanup
cam.release()
GPIO.cleanup()  # Reset GPIO settings
cv2.destroyAllWindows()
