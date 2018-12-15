
from flask import *
from flask_pymongo import PyMongo
import pymongo
from pymongo import MongoClient
from json import *
import hashlib
import pprint
import ssl
import qrcode
import random
import string
#from io import StringIO was not working so imported StringIO
import io
import sys
import datetime
import geocoder
import json
import requests
from PIL import Image
import boto3
from botocore.client import Config
import time
import os

ip = "0.0.0.0"
ip = "10.16.35.99"
# MASAKI CHANGE THIS ^^
port = 8080


app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'largescale'
app.config['MONGO_URI'] = 'mongodb://mongodb:27017/'
mongo = PyMongo(app)



Client = MongoClient("localhost:27017")
db = Client["Library"]
userlist = db["Users"]
songlist = db["Songs"]
downloadlist = db["Downloads"]


app.secret_key = "super secret key"

@app.route('/')
def home_page():
	if 'username' not in session:
		return render_template("home.html")
	else:
		return render_template("home.html", username = session["username"])

@app.route('/<code>', methods=['GET', 'POST'])
def imagec(code):
	if(code == "favicon.ico"):
		return redirect('/')
	else:
		song = {}
		realurl = False
		for i in songlist.find({'code':code}):
			song = i
			realurl = True
		if(realurl == False):
			return "URL is invalid!"
		mydir = 'static/'
		filelist = [ f for f in os.listdir(mydir) if f.endswith(".png") ]
		for f in filelist:
			os.remove(os.path.join(mydir, f))
		host = 'localhost'
		host = "10.16.35.99"
		# MASAKI CHANGE THIS ^^
		imagelist = []
		clist = string.ascii_lowercase + string.ascii_uppercase + string.digits
		s3 = boto3.client('s3', config=Config(signature_version='s3v4')) 
		for i in range(10):
			n = 30
			gencode = ''
			for i in range(n):
				gencode = gencode + random.choice(clist)
			gencode = gencode + code
			durl = "http://" + host + ":" + str(port) + "/downloadfile/" + gencode
			img = qrcode.make(durl)
			imgname = 'static/' + str(gencode) + '.png'
			img.save(imgname)
			imagelist.append(imgname)
			downloadlist.insert({"scode":code, "dcode":gencode, "time":"None", "loc":"None", "scanned":False, "epoch":-1}) # avoid duplicates
		return render_template('home.html', username=session['username'], imagelist=imagelist)

@app.route('/download', methods = ['GET', 'POST'])
def download():
	if request.method == "POST":
		code = request.form['code']
		song = {}
		found = False
		for i in songlist.find({'code':code}):
			found = True
			song = i
		if found == False:
			if 'username' not in session:
				return render_template("download.html", message = "This code is not valid")
			else:
				return render_template("download.html", username = session["username"], message = "This code is not valid")
		else:
			if 'username' not in session:
				return render_template("download.html", song = song)
			else:
				return render_template("download.html", username = session["username"], song = song)        
	else:
		if 'username' not in session:
			return render_template("download.html")
		else:
			return render_template("download.html", username = session["username"])

@app.route('/login', methods = ['GET', 'POST'])
def login():
		if request.method == "POST":
			username = request.form['username']
			hashed_password = hashlib.sha1((request.form['password']).encode('utf-8'))
			exists = False 
			for i in userlist.find({'username':username}):
				exists = True
			if exists == True:
				match = False 
				for i in userlist.find({}):
					pprint.pprint(i)
				for i in userlist.find({'username':username, 'password':hashed_password.hexdigest()}):
					match = True
				if match == True:
					session['username'] = username
					return redirect("/")
				else:
					return render_template("login.html", message = "Username and password don't match!")
			else:
				return render_template("login.html", message = "Username does not exist!")
		else:
			return render_template("login.html")

@app.route('/register', methods = ['GET', 'POST'])
def register():
		if request.method == "POST":
			username = request.form['username']
			if request.form['password'] != request.form['password2']:
				return render_template("register.html", message = "Passwords must match!")
			hashed_password = hashlib.sha1((request.form['password']).encode('utf-8'))
			newuser = True 
			for i in userlist.find({'username':username}):
				newuser = False
			if newuser == True:
				session['username'] = username
				userlist.insert({'username': username, 'password': hashed_password.hexdigest()})
				return redirect("/")
			else:
				return render_template("register.html", message = "Username already exists!")
		else:
			return render_template("register.html")

@app.route('/upload', methods = ['GET', 'POST'])
def upload():
	if request.method == "POST":
		if 'username' not in session:
			return render_template("upload.html", message = "You have to be logged in to upload!")
		else:
			s3 = boto3.resource('s3')
			title = request.form['title']
			artist = request.form['artist']
			music = request.files['file']
			filename = request.files['file'].filename
			clist = string.ascii_lowercase + string.ascii_uppercase + string.digits
			n = 20
			gencode = ''
			for i in range(n):
				gencode = gencode + random.choice(clist)
			hashed_user = hashlib.sha1((session['username']).encode('utf-8'))
			now = datetime.datetime.now().strftime("%a, %d %B %Y %I: %M: %S %p")
			gencode = gencode + hashed_user.hexdigest()
			s3.Bucket('lswafinal-songdb').put_object(Key=(gencode + filename), Body=music, ContentDisposition=("attachment; filename="+filename))
			ms3 = boto3.client('s3', config=Config(signature_version='s3v4'))
			plink = ms3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': 'lswafinal-songdb','Key': (gencode + filename)})
			response = requests.get(plink)
			s3link = response.url
			songlist.insert({'title':title, "artist":artist, "code":gencode, "filename":filename, "username":session["username"], 'downloads':0, "time":now, 'timelist':[], 'loclist':[], 'dllist':[], 's3link':s3link})
			rpath = '/' + str(gencode)
			return redirect(rpath)
	else:
		if 'username' not in session:
			return render_template('upload.html')
		else:
			return render_template('upload.html', username=session['username'])



window = 30

@app.route('/downloadfile/<code>')
def downloadfile(code):
	clist = string.ascii_lowercase + string.ascii_uppercase + string.digits 
	gencode = ''
	n = 50   
	for i in range(n):
		gencode = gencode + random.choice(clist)
	if 'unique' not in session:
		session['unique'] = gencode
	ip = ""
	if request.headers.getlist("X-Forwarded-For"):
	   ip = request.headers.getlist("X-Forwarded-For")[0]
	else:
		ip = request.remote_addr
	cpic = session['unique'] + code # get the client ip code
	song = {}
	scode = ""
	scanned = False
	for i in downloadlist.find({'dcode':code}):
		scode = i['scode']
	for i in songlist.find({'code':scode}):
		song = i
	#ip = "67.243.240.102"
	gurl = "http://api.ipstack.com/" + str(ip) + "?access_key=1e8045f7688859a698512a0abf267f5b"
	response = requests.get(gurl)    
	json_data = json.loads(response.text)
	here = "Country: " +  str(json_data["country_name"]) + " | Region: " + str(json_data["region_name"]) + " | City: " +str(json_data["city"]) + " | Latitude: " +str(json_data["latitude"]) + " | Longitude: " +str(json_data["longitude"])
	now = datetime.datetime.now().strftime("%a, %d %B %Y %I:%M:%S %p")
	#now = request.args.get("time")
	epoch = -1
	for i in downloadlist.find({'dcode':code}):
	 scanned = i['scanned']
	 epoch = i['epoch']
	if scanned == False:
		downloadlist.update_one({"dcode":code} , {"$set": {"time":now, "loc":here, "epoch":int(time.time()), "scanned":True}}) # avoid duplicates
	if epoch == -1 or (epoch + window) > int(time.time()):
			s3 = boto3.client('s3', config=Config(signature_version='s3v4'))
			file = s3.get_object(Bucket='lswafinal-songdb', Key=scode+song['filename'])
			return Response(file['Body'].read(),mimetype='audio/mpeg',headers={"Content-Disposition": "attachment;filename="+song['filename']})
			#return redirect(song['s3link'])
	else:
    		return "This QR HAS EXPIRED!"

@app.route('/user')
def user():
	return render_template("user.html")

@app.route('/stat')
def stat():
	if 'username' not in session:
		return render_template("home.html", message = "You must be logged in to your stats!")
	else:
		mysonglist = []
		for i in songlist.find({'username':session['username']}):
			song = i
			code = song['code']
			timelist = song['timelist']
			loclist = song['loclist']
			dllist = song['dllist']
			for j in downloadlist.find({'scode':code}):
				if j['scanned'] == True and j['dcode'] not in dllist:
					#timelist.append(j['time'])
					#loclist.append(j['loc'])
					dllist.append(j['dcode'])
			songlist.find_one_and_update({'code':code}, {"$set": {'timelist':timelist}})
			songlist.find_one_and_update({'code':code}, {"$set": {'loclist':loclist}})
			songlist.find_one_and_update({'code':code}, {"$set": {'downloads':len(dllist)}})
		for i in songlist.find({'username':session['username']}):
			mysonglist.append(i)
		if(len(mysonglist) > 0):
			return render_template("stat.html", list = mysonglist)
		else:
			return render_template("stat.html")

@app.route('/stat/<code>')
def statc(code):
	if 'username' not in session:
		return render_template("home.html", message = "You must be logged in to your stats!")
	else:
		song = {}
		for i in songlist.find({'code':code}):
			song = i
		if song['username'] == session['username']:
			timelist = song['timelist']
			loclist = song['loclist']
			dllist = song['dllist']
			for j in downloadlist.find({'scode':code}):
				if j['scanned'] == True and j['dcode'] not in dllist:
					timelist.append(j['time'])
					loclist.append(j['loc'])
					dllist.append(j['dcode'])
			songlist.find_one_and_update({'code':code}, {"$set": {'dllist':dllist}})
			songlist.find_one_and_update({'code':code}, {"$set": {'timelist':timelist}})
			songlist.find_one_and_update({'code':code}, {"$set": {'loclist':loclist}})
			songlist.find_one_and_update({'code':code}, {"$set": {'downloads':len(dllist)}})
			for i in songlist.find({'code':code}):
				song = i
			return render_template("stat.html", song = song)
		else:
			return render_template("home.html", message = "Illegal Access!", username = session["username"])




	


	


@app.route('/logout')
def logout_redirect():
	session.pop('username', None)
	return redirect("/")


if __name__ == '__main__':
	app.run(host=ip, port=port, debug=True)
