import numpy as np
import cv2 as cv
face_cascade = cv.CascadeClassifier('/home/mavis/opencv/data/haarcascades/haarcascade_frontalface_default.xml')
eye_cascade = cv.CascadeClassifier('/home/mavis/opencv/data/haarcascades/haarcascade_eye.xml')

class VideoCamera(object):
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.video = cv.VideoCapture(0)
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        success, img = self.video.read()
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in faces:
            cv.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)
            for (ex,ey,ew,eh) in eyes:
                cv.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
            
            # We are using Motion JPEG, but OpenCV defaults to capture raw images,
            # so we must encode it into JPEG in order to correctly display the
            # video stream.
        ret, jpeg = cv.imencode('.jpg', img)
        return jpeg.tobytes()
