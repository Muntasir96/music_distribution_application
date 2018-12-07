
from flask import *
from flask_pymongo import PyMongo
import pymongo
from pymongo import MongoClient
from json import *
from config import uri
import hashlib
import pprint
import ssl
import qrcode
import random
import string
from io import StringIO


app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'largescale'
app.config['MONGO_URI'] = uri
mongo = PyMongo(app)


Client = MongoClient("localhost:27017")
db = Client["Library"]
userlist = db["Users"]
songlist = db["Songs"]



currentuser = {"logged":False, "username":""}



@app.route('/')
def home_page():
    if currentuser['logged'] == False:
        return render_template("home.html")
    else:
        return render_template("home.html", username = currentuser["username"])


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
            if currentuser['logged'] == False:
                return render_template("download.html", message = "This code is not valid")
            else:
                return render_template("download.html", username = currentuser["username"], message = "This code is not valid")
        else:
            if currentuser['logged'] == False:
                return render_template("download.html", song = song)
            else:
                return render_template("download.html", username = currentuser["username"], song = song)        
    else:
        if currentuser['logged'] == False:
            return render_template("download.html")
        else:
            return render_template("download.html", username = currentuser["username"])

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
                print("pass is" + hashed_password.hexdigest())
                for i in userlist.find({}):
                    pprint.pprint(i)
                for i in userlist.find({'username':username, 'password':hashed_password.hexdigest()}):
                    match = True
                if match == True:
                    currentuser['logged'] = True
                    currentuser['username'] = username
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
            print(username + " " + hashed_password.hexdigest())
            newuser = True 
            for i in userlist.find({'username':username}):
                newuser = False
            if newuser == True:
                currentuser['logged'] = True
                currentuser['username'] = username
                userlist.insert({'username': username, 'password': hashed_password.hexdigest()})
                return redirect("/")
            else:
                return render_template("register.html", message = "Username already exists!")
        else:
            return render_template("register.html")

@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    if request.method == "POST":
        if currentuser['logged'] == False:
            return render_template("upload.html", message = "You have to be logged in to upload!")
        else:
            title = request.form['title']
            artist = request.form['artist']
            music = request.files['file']
            filename = request.files['file'].filename
            print(music)
            print(type(music))
            print(music.name)
            print(filename)
            clist = string.ascii_lowercase + string.ascii_uppercase + string.digits 
            n = 4
            gencode = ''
            for i in range(n):
                gencode = gencode + random.choice(clist)
            songlist.insert({'title': title, 'artist':artist, 'code':gencode, 'filename': filename})
            img = qrcode.make(gencode) # img is a png image
            imgname = 'static/image/' + str(gencode) + '.png'
            mscname = 'static/music/' + str(filename)
            img.save(imgname)
            music.save(mscname)
            if currentuser['logged'] == False:
                return render_template("upload.html", image = imgname)
            else:
                return render_template("upload.html", username = currentuser["username"], image = imgname)
    else:
        if currentuser['logged'] == False:
            return render_template("upload.html")
        else:
            return render_template("upload.html", username = currentuser["username"])


@app.route('/downloadfile/<filename>')
def downloadfile(filename):
    path = "static/music/" + filename
    return send_file(path, attachment_filename=filename, as_attachment=True)
    


@app.route('/user')
def user():
    return render_template("user.html")

@app.route('/stat')
def stat():
    return render_template("stat.html")

@app.route('/mongo', methods=['GET'])
def mongo_test():
    output = []
    for f in mongo.db.song.find():
        f.pop('_id')
        output.append(f)
    return jsonify({'result' : output})

@app.route('/logout')
def logout_redirect():
    currentuser['logged'] = False
    currentuser['username'] = ""
    return redirect("/")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)


