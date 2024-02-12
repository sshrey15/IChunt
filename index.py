from flask import Flask, request, render_template, send_file
import cv2
import numpy as np
import base64
import io

app = Flask(__name__)

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

        # Subtract the reference image from the test image
        sub = cv2.subtract(g_o_img, g_def_img)
        thresh = cv2.threshold(sub , 110, 255, cv2.THRESH_BINARY)[1]

        # Apply morphological opening
        kernel = np.ones((7,7),np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        # Save the bitwise image
        im = cv2.bitwise_not(opening)

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
        im_with_keypoints = cv2.drawKeypoints(img2, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        # Convert images to base64
        _, img_encoded = cv2.imencode('.jpg', img1)
        img1_base64 = base64.b64encode(img_encoded).decode('utf-8')

        _, bitwise_encoded = cv2.imencode('.jpg', im)
        bitwise_base64 = base64.b64encode(bitwise_encoded).decode('utf-8')

        _, output_encoded = cv2.imencode('.jpg', im_with_keypoints)
        output_base64 = base64.b64encode(output_encoded).decode('utf-8')

        _, bw_encoded = cv2.imencode('.jpg', bw_img)
        bw_base64 = base64.b64encode(bw_encoded).decode('utf-8')

        return render_template('display.html', img1=img1_base64, bitwise=bitwise_base64, output=output_base64, bw=bw_base64)
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)