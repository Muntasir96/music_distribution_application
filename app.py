from flask import *
from flask_pymongo import PyMongo
import pymongo
from json import *
from config import uri
import hashlib

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'largescale'
app.config['MONGO_URI'] = uri
mongo = PyMongo(app)

@app.route('/')
def home_page():
    return render_template("home.html")

@app.route('/download')
def download():
    return render_template("download.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/register')
def register():
    try:
        if request.method == "POST":
            username = request.form['username']
            # Password encoded with utf-8 first then hashed with SHA1
            hashed_password = hashlib.sha1((request.form['password']).encode('utf-8'))
            mongo.db.users.insert({'username': username, 'password': hashed_password})
            return redirect(url_for("stat.html"))
        return render_template("register.html")

    except Exception as e:
        flash(str(e))
    return render_template("register.html")

@app.route('/upload')
def upload():
    return render_template("upload.html")

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
    print(session['user'])
    session.pop('user', None)
    return redirect(url_for('login_page'))


# @app.before_request
# def before_request():
#     g.user = None
#     if 'user' in session:
#         g.user = session['user']

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
