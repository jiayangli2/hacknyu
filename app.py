from flask import Flask, request, render_template, g, redirect, Response, session, escape, url_for, jsonify
import os
import hashlib
import urllib
import sys
import time
import requests
import string
import boto3
import json

app = Flask(__name__)


def detect_text(encoded_img):
	session = boto3.Session()
	credentials = session.get_credentials()
	client = session.client('rekognition','us-east-1')

	response = client.detect_text(Image={'Bytes': encoded_img})
	food_set = set()
	for text in response['TextDetections']:
	    item = (text['DetectedText'].replace(' ', '').lower())
	    item = ''.join(x for x in item if x.isalpha())
	    food_set.add(item)
	return list(food_set)

#def filter(response):
	# food_list = [('shakeburger', '490', '2', '5.19')]
	# return food_list


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/receipt', methods=['POST'])
def receipt():
	#food_list = detect_text((request.files['photo'].read()))
	#print(food_list)
	food_list = [('shakeburger', '490', '2', '5.19'), ('smokeshack', '770', '1', '6.69')]
	return render_template("analysis.html", food_list = food_list, price_init=25.25, cal_init=1250)

if __name__ == "__main__":
    app.run()
