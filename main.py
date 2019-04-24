#!/usr/bin/env python
#
# Project: Video Streaming with Flask
# Author: Log0 <im [dot] ckieric [at] gmail [dot] com>
# Date: 2014/12/21
# Website: http://www.chioka.in/
# Description:
# Modified to support streaming out with webcams, and not just raw JPEGs.
# Most of the code credits to Miguel Grinberg, except that I made a small tweak. Thanks!
# Credits: http://blog.miguelgrinberg.com/post/video-streaming-with-flask
#
# Usage:
# 1. Install Python dependencies: cv2, flask. (wish that pip install works like a charm)
# 2. Run "python main.py".
# 3. Navigate the browser to the local webpage.
from flask import Flask, render_template, Response,redirect,request,session
from function import VideoCamera
import cv2
import threading

app = Flask(__name__)
app.secret_key='12345678'
index_func=[{'object_detection':'Ball Tracking'}, {'object_detection':'Haar Cascade'}]

@app.route('/')
def index():
	return render_template('index.html',index_func=index_func)
	
def gen_cascade(camera):
	while True:
		frame = camera.get_frame_cascade()

		yield (b'--frame\r\n'
			   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def gen_ball_track(camera):
	while True:
		frame = camera.get_frame_ball_track()
		yield (b'--frame\r\n'
			   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
	index=request.args.get('index', None)
	if index=='1':
		return Response(gen_ball_track(VideoCamera()),
						mimetype='multipart/x-mixed-replace; boundary=frame')
	elif index=='2':
		return Response(gen_cascade(VideoCamera()),
						mimetype='multipart/x-mixed-replace; boundary=frame')
	else:
		return redirect('/')
		# return Response(gen(VideoCamera()),
		# 				mimetype='multipart/x-mixed-replace; boundary=frame')
	index==None

@app.route('/test' , methods=['GET', 'POST'])
def test():
	select = request.form.get('func_select',None)
	print(select)
	if select=='Ball Tracking':
		return render_template('ball.html')
	elif select=='Haar Cascade':
		
		return render_template('haar.html')
	else:
		return redirect('/') # just to see what select is
		
if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True,threaded=True)
	
	
