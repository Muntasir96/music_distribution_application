
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
from io import StringIO
import datetime
import geocoder
import json
import requests
from PIL import Image



ip = "192.168.1.213"
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

@app.route('/<code>')
def imagec(code):
    song = {}
    for i in songlist.find({'code':code}):
        song = i
    print(song)
    imgname = 'static/image/' + str(song['code']) + '.png'
    return render_template("image.html", username = session["username"], image = imgname)



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
            title = request.form['title']
            artist = request.form['artist']
            music = request.files['file']
            filename = request.files['file'].filename
            clist = string.ascii_lowercase + string.ascii_uppercase + string.digits 
            n = 40
            gencode = ''
            for i in range(n):
                gencode = gencode + random.choice(clist)
            hashed_user = hashlib.sha1((session['username']).encode('utf-8'))
            now = datetime.datetime.now().strftime("%a, %d %B %Y %I:%M:%S %p")
            gencode = gencode + hashed_user.hexdigest()
            songlist.insert({'title': title, 'artist':artist, 'code':gencode, 'filename': filename, 'username': session['username'], 'downloads': 0, 'time':now, 'timelist':[], 'loclist':[], 'dllist':[]})
            #host = "104.196.173.11"
            host = ip
            durl = "http://" + host + ":" + str(port) + "/downloadfile/" + gencode
            img = qrcode.make(durl) # img is a png image
            imgname = 'static/image/' + str(gencode) + '.png'
            mscname = 'static/music/' + str(filename)
            img.save(imgname)
            music.save(mscname)
            if 'username' not in session:
                return render_template("upload.html", image = imgname)
            else:
                return render_template("upload.html", username = session["username"], image = imgname)
    else:
        if 'username' not in session:
            return render_template("upload.html")
        else:
            return render_template("upload.html", username = session["username"])





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
    cpic = str(ip) + session['unique'] + code # get the client ip code
    song = {}
    print(session)
    for i in songlist.find({'code':code}):
        song = i
    gurl = "http://api.ipstack.com/" + str(ip) + "?access_key=1e8045f7688859a698512a0abf267f5b"
    response = requests.get(gurl)    
    json_data = json.loads(response.text)
    here = str(json_data["region_name"])
    now = datetime.datetime.now().strftime("%a, %d %B %Y %I:%M:%S %p")
    downloadlist.update_one({"cpic":cpic} , {"$set": {"code":code, "cpic":cpic, "time":now, "loc":here}} , upsert =True) # avoid duplicates
    filename = song['filename']
    path = "static/music/" + filename
    return send_file(path, attachment_filename=filename, as_attachment=True)

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
            for j in downloadlist.find({'code':code}):
                if j['cpic'] not in dllist:
                    timelist.append(j['time'])
                    loclist.append(j['loc'])
                    dllist.append(j['cpic'])
            songlist.find_one_and_update({'code':code}, {"$set": {'dllist':dllist}})
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
            for j in downloadlist.find({'code':code}):
                if j['cpic'] not in dllist:
                    timelist.append(j['time'])
                    loclist.append(j['loc'])
                    dllist.append(j['cpic'])
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
