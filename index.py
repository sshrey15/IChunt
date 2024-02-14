from flask import Flask, request, render_template, send_file, send_from_directory
from PIL import Image
import pytesseract
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import base64
import io
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

def process_video(filepath):
    # Define the HSV lower and upper bounds for the color of the leads
    lower_hsv = np.array([0, 0, 0])
    upper_hsv = np.array([179, 255, 255])

    # Capture the video from the uploaded file
    cap = cv2.VideoCapture(filepath)

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (640, 480))

    # Loop until the video ends
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            # Convert the frame to HSV color space
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Create a mask based on the HSV range
            mask = cv2.inRange(hsv, lower_hsv, upper_hsv)

            # Find the contours of the masked image
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Loop over the contours
            w = h = 0
            for cnt in contours:
                # Calculate the area of the contour
                area = cv2.contourArea(cnt)

                # Filter out small or large areas
                if area < 50 or area > 2000:
                    continue

                # Draw a bounding rectangle around the contour
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            lead_width = w
            lead_length = h
            # Write the frame into the file 'output.mp4'
            frame = cv2.resize(frame, (640, 480))
            out.write(frame)

        else:
            break

    # Release everything when job is finished
    cap.release()
    out.release()

    return 'output.mp4'


@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the files from the POST request
        file1 = request.files['file1']  # reference image
        file2 = request.files['file2']  # test image

        # Save the files to a temporary location
        file1.save('temp1.jpg')
        file2.save('temp2.jpg')

        # Load the images using OpenCV
        img1 = cv2.imread('temp1.jpg')
        img1 = cv2.resize(img1, (640, 480))
        img2 = cv2.imread('temp2.jpg')
        img2 = cv2.resize(img2, (640, 480))

        # Convert the images to grayscale
        g_o_img = cv2.cvtColor(img1, cv2.COLOR_BGR2LAB)[...,0]
        
        g_def_img = cv2.cvtColor(img2, cv2.COLOR_BGR2LAB)[...,0]

        #apply canny edge detecttion
        edges1 = cv2.Canny(g_o_img, threshold1=30, threshold2=100)
        edges2 = cv2.Canny(g_def_img, threshold1=30, threshold2=100)

         # Convert images to base64
        _, edges1_encoded = cv2.imencode('.jpg', edges1)
        edges1_base64 = base64.b64encode(edges1_encoded).decode('utf-8')

        _, edges2_encoded = cv2.imencode('.jpg', edges2)
        edges2_base64 = base64.b64encode(edges2_encoded).decode('utf-8')

        # Subtract the reference image from the test image
       
        add = cv2.subtract(g_def_img,g_o_img )
        thresh = cv2.threshold(add , 110, 255, cv2.THRESH_BINARY)[1]

        # Apply morphological opening
        kernel = np.ones((7,7),np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        im = cv2.bitwise_not(opening)

        if im is None:
            return "Error: Could not create bitwise image"

        # Calculate the percentage of error
        total_pixels = np.prod(im.shape)
        white_pixels = np.count_nonzero(im)
        black_pixels = total_pixels - white_pixels
        error_percentage = round((black_pixels / total_pixels) * 100, 2)

        # Save the bitwise image
   

        # Detect blobs
        params = cv2.SimpleBlobDetector_Params()
        params.filterByInertia = False
        params.filterByConvexity = False
        params.filterByCircularity = False
        detector = cv2.SimpleBlobDetector_create(params)
        keypoints = detector.detect(im)

   
       


        # Convert the image to black and white
        bw_img = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        # Draw circles around the blobs
        im_with_keypoints = cv2.drawKeypoints(img2, keypoints, np.array([]), (0,100,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        # Convert images to base64
        _, img_encoded = cv2.imencode('.jpg', img1)
        img1_base64 = base64.b64encode(img_encoded).decode('utf-8')

        _, bitwise_encoded = cv2.imencode('.jpg', im)
        bitwise_base64 = base64.b64encode(bitwise_encoded).decode('utf-8')

        _, output_encoded = cv2.imencode('.jpg', im_with_keypoints)
        output_base64 = base64.b64encode(output_encoded).decode('utf-8')

        _, bw_encoded = cv2.imencode('.jpg', bw_img)
        bw_base64 = base64.b64encode(bw_encoded).decode('utf-8')

        return render_template('display.html', img1=img1_base64, bitwise=bitwise_base64, output=output_base64, bw=bw_base64, error_percentage=error_percentage, edges1=edges1_base64, edges2=edges2_base64)
    return render_template('upload.html')






@app.route('/process', methods=['GET'])
def process():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part', 400

        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        output_filepath = process_video(filepath)

        return send_from_directory(app.config['UPLOAD_FOLDER'], output_filepath, as_attachment=True, mimetype='video/mp4')
    return render_template('process.html')


if __name__ == '__main__':
    app.run(debug=True)