import numpy as np
import argparse
import cv2
import imutils
import threading
import time
import os
from time import sleep
from collections import deque
from imutils.video import VideoStream


# Import Cascade Library
face_cascade = cv2.CascadeClassifier('/home/mavis/opencv/data/haarcascades/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('/home/mavis/opencv/data/haarcascades/haarcascade_eye.xml')

# Class untuk bypass parameter objek terdeteksi atau tidak
class CancellationToken:
   def __init__(self):
	   self.is_cancelled = False

   def cancel(self):
	   self.is_cancelled = True

   def new(self):
	   self.is_cancelled = False 


cancellationToken = CancellationToken()

'''
 define the lower and upper boundaries of the "color"
 ball in the HSV color space, then initialize the
 list of tracked points
'''

#greencolor
# greenLower = (29, 86, 6)
# greenUpper = (64, 255, 255)

#orangecolor
orangeLower = (9, 232,18)
orangeUpper = (31, 265, 256)
'''
using deque , a list-like data structure with super fast appends and 
pops to maintain a list of the past N (x, y)-locations of the ball 
in our video stream. Maintaining such a queue allows us to draw the 
“contrail” of the ball as its being tracked. max is 64
'''
pts = deque(maxlen=64)
# allow the camera or video file to warm up
time.sleep(2.0)

class VideoCamera(object):
	def __init__(self):
		# Using OpenCV to capture from device 0. If you have trouble capturing
		# from a webcam, comment the line below out and use a video file
		# instead.
		self.video = cv2.VideoCapture(2)
		# If you decide to use video.mp4, you must have this file in the folder
		# as the main.py.
		# self.video = cv2.VideoCapture('video.mp4')
	
	def __del__(self):
		self.video.release()

	# Just Show Frame only	
	def get_frame(self):
		success, img = self.video.read()
		# We are using Motion JPEG, but OpenCV defaults to capture raw images,
		# so we must encode it into JPEG in order to correctly display the
		# video stream.
		ret, jpeg = cv2.imencode('.jpg', img)
		return jpeg.tobytes()

	# CASCADE FUNCTION
	def get_frame_cascade(self):
		success, img = self.video.read()
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		faces = face_cascade.detectMultiScale(gray, 1.3, 5)
		for (x,y,w,h) in faces:
			cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,0),0)
			roi_gray = gray[y:y+h, x:x+w]
			roi_color = img[y:y+h, x:x+w]
			eyes = eye_cascade.detectMultiScale(roi_gray)
			
			# dari frame yg telah dideteksi, kemudian di crop pada area wajah saja
			cropped = img[ y : y+h, x : x+w ]
			resize = cv2.resize(cropped,(92,112))
			
			for (ex,ey,ew,eh) in eyes:
				cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
				cancellationToken.cancel()
				print("Face is Detected !")
				if(cancellationToken.is_cancelled):
					#cv2.imwrite("tes"+time.strftime("_%H:%M:%S %a,%d %b %Y")+".jpg",resize)
					cancellationToken.new()
			# We are using Motion JPEG, but OpenCV defaults to capture raw images,
			# so we must encode it into JPEG in order to correctly display the
			# video stream.
		ret, jpeg = cv2.imencode('.jpg', img)
		return jpeg.tobytes()

	def get_frame_ball_track(self):
		success, frame = self.video.read()
		# handle the frame from VideoCapture or VideoStream
		#frame = frame[1] if args.get("video", False) else frame
		# We are using Motion JPEG, but OpenCV defaults to capture raw images,
		# so we must encode it into JPEG in order to correctly display the
		# video stream.
		# resize the frame, blur it, and convert it to the HSV
		# color space
		frame = imutils.resize(frame, width=600)
		blurred = cv2.GaussianBlur(frame, (11, 11), 0)
		hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

		# construct a mask for the color "orange", then perform
		# a series of dilations and erosions to remove any small
		# blobs left in the mask
		mask = cv2.inRange(hsv, orangeLower, orangeUpper)
		mask = cv2.erode(mask, None, iterations=2)
		mask = cv2.dilate(mask, None, iterations=2)

		# find contours in the mask and initialize the current
		# (x, y) center of the ball
		cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)
		cnts = imutils.grab_contours(cnts)
		center = None

		# only proceed if at least one contour was found
		if len(cnts) > 0:
			# find the largest contour in the mask, then use
			# it to compute the minimum enclosing circle and
			# centroid
			c = max(cnts, key=cv2.contourArea)
			((x, y), radius) = cv2.minEnclosingCircle(c)
			M = cv2.moments(c)
			center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

			# only proceed if the radius meets a minimum size
			if radius > 10:
				# draw the circle and centroid on the frame,
				# then update the list of tracked points
				cv2.circle(frame, (int(x), int(y)), int(radius),
					(0, 255, 255), 2)
				cv2.circle(frame, center, 5, (0, 0, 255), -1)

		# update the points queue
		pts.appendleft(center)
		

		# loop over the set of tracked points
		for i in range(1, len(pts)):
			# if either of the tracked points are None, ignore
			# them
			if pts[i - 1] is None or pts[i] is None:
				continue

			# otherwise, compute the thickness of the line and
			# draw the connecting lines
			thickness = int(np.sqrt( 64 / float(i + 1)) * 2.5)
			cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

		# show the frame to our screen
		#cv2.imshow("Frame", frame)
		#key = cv2.waitKey(1) & 0xFF

		ret, jpeg = cv2.imencode('.jpg', frame)
		return jpeg.tobytes()

