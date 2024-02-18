from flask import Flask, request, render_template,redirect, send_file, send_from_directory,url_for
from PIL import Image
from google.cloud import vision
from google.cloud.vision import ImageAnnotatorClient

import pytesseract
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import base64
import io
import time
import serial
import os

ser = serial.Serial(port='COM8', baudrate=9600, timeout=0.05, bytesize=8, stopbits=serial.STOPBITS_ONE,parity=serial.PARITY_NONE, xonxoff=False, rtscts=False, dsrdtr=False)
ser.close()

app = Flask(__name__)


def test_and_ic():
    ser = serial.Serial(port='COM8', baudrate=9600, timeout=1, bytesize=8, stopbits=serial.STOPBITS_ONE,parity=serial.PARITY_NONE, xonxoff=False, rtscts=False, dsrdtr=False)
    
    try:
        time.sleep(2)  # wait for the Arduino to reset
        ser.write(b'AND')  # send 'AND' to the Arduino
        result = ser.readline().decode('utf-8')  # read the response from the Arduino
        return result
    finally:
        ser.close()

def test_nor_ic():
    ser = serial.Serial(port='COM8', baudrate=9600, timeout=1, bytesize=8, stopbits=serial.STOPBITS_ONE,parity=serial.PARITY_NONE, xonxoff=False, rtscts=False, dsrdtr=False)
    
    try:
        time.sleep(2)  # wait for the Arduino to reset
        ser.write(b'NOR')  # send 'NOR' to the Arduino
        result = ser.readline().decode('utf-8')  # read the response from the Arduino
        return result
    finally:
        ser.close()

def end_connection():
    ser = serial.Serial(port='COM8', baudrate=9600, timeout=1, bytesize=8, stopbits=serial.STOPBITS_ONE,parity=serial.PARITY_NONE, xonxoff=False, rtscts=False, dsrdtr=False)
    
    try:
        time.sleep(2)  # wait for the Arduino to reset
        ser.write(b'OFF')  # send 'END' to the Arduino
        result = ser.readline().decode('utf-8')  # read the response from the Arduino
        return result
    finally:
        ser.close()



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

        # defectdetection@defectdetection-414419.iam.gserviceaccount.com // SERVICE ACCOUNT

   
       


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
    return render_template('upload.html', ictest_url=url_for('home'))
@app.route('/ictest')
def home():
    return render_template('home.html')

@app.route('/test_ic', methods=['POST'])
def test_ic():
    ic_type = request.form.get('ic_type')
    if ic_type == 'AND':
        result = test_and_ic()
    elif ic_type == 'NOR':
        result = test_nor_ic()
    elif ic_type == 'OFF':
        result = end_connection()
    else:
        result = 'Invalid IC type'
    return render_template('result.html', result=result)





if __name__ == '__main__':
    app.run(debug=True)