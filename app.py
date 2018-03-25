from flask import Flask, request, render_template, g, redirect, Response, session, escape, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import hashlib
import urllib
import sys
import time
import requests
import string
import json
from datetime import datetime
from pytz import timezone
from gcp_filtrate import filter

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./app.db'#/home/prokingsley/devfest/app.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
salt = 'cdea050d7d604afea194572ef22d5297'


class User(db.Model):
    username = db.Column(db.String(80), primary_key=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

class Record(db.Model):
	username = db.Column(db.String(80), primary_key=True, nullable=False)
	time = db.Column(db.DateTime, primary_key=True, nullable=False, default=datetime.utcnow)
	calories = db.Column(db.String(120), nullable=False)
	spending = db.Column(db.String(120), nullable=False)
	
	def __repr__(self):
        	return '<User %r>' % self.username

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
tz = timezone('EST')

@app.route('/')
def index():
    print("hi")
    return render_template("index.html")

@app.route('/record', methods=['POST','GET'])
def record():
	if request.method == 'POST':
	    uname = request.form['username']
	    calories = request.form['calories']
	    spending = request.form['spending']
	    dtime = datetime.now(tz)
	    record_created = Record(username = uname, time = dtime, calories=calories, spending=spending)
	    try:
	        db.session.add(record_created)
	        db.session.commit()
	    except:
	        err_msg = "Recording calories failed!"
	        context = dict(data = err_msg)
	        return render_template("index.html", **context)
	    return redirect(url_for('index'))
	else:
		records = Record.query.filter_by(username=session['username'])
		return render_template("record.html", records = records)

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    if request.method == 'POST':
        uname = request.form['username']
        pwd = hashlib.sha512(request.form['password'] + salt).hexdigest()
        app.logger.info('%s logged in successfully', uname)
        user_created = User(username = uname, password = pwd)
        try:
            db.session.add(user_created)
            db.session.commit()
        except:
            err_msg = "Signing up failed!"
            context = dict(data = err_msg)
            return render_template("index.html", **context)
        session['username'] = uname
        return redirect(url_for('index'))
    err_msg = "HTTP Request not supported!"
    context = dict(data = err_msg)
    return render_template("index.html", **context)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    uname = request.form['username']
    pwd = hashlib.sha512(request.form['password'] + salt).hexdigest()
    try:
        temp = User.query.filter_by(username=uname).first()
        if temp == None or temp.password != pwd:
            err_msg = "incorrect username or password"
            context = dict(data = err_msg)
            print ("no such user")
            return render_template("index.html", **context)
        else:
            session['username'] = uname
            return redirect(url_for('index'))
    except:
        err_msg = "connection to DB failed"
        context = dict(data = err_msg)
        return render_template("index.html", **context)

@app.route('/logout', methods=['GET'])
def logout():
	session.clear()
	return redirect(url_for('index'))

@app.route('/receipt', methods=['POST'])
def receipt():
	food_list = filter((request.files['photo'].read()))
	print(food_list)
	#food_list = [('shakeburger', '490', '2', '5.19'), ('smokeshack', '770', '1', '6.69')]
        price_init = 0
        cal_init = 0
        for food in food_list:
            price_init += food[2]
            cal_init += food[1]
	return render_template("analysis.html", food_list = food_list, price_init=price_init, cal_init=cal_init)

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == "__main__":
	db.create_all()
	app.run(host='0.0.0.0', port = 5000)
