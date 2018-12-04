from flask import *
from config import DB, secret_key
# from flask_pymongo import PyMongo
import pymongo
from json import *

app = Flask(__name__)
# app.config['SECRET_KEY'] = secret_key
# app.config['MONGO_URI'] = 'mongodb+srv://largescale:largescaleproject@largescale-ushui.mongodb.net/test?retryWrites=true'
# app.config['MONGO_DBNAME'] = 'music_distribution'
# mongo = PyMongo(app)
# mongo = pymongo.MongoClient(mongo, maxPoolSize=50, connect=False)

# db = pymongo.database.Database(mongo, 'largescale')
# col = pymongo.collection.Collection(db, 'music_distribution')
# doc_list = list(col.find().limit(5))
# col_results = json.loads(dumps(doc_list))

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

# @app.route('/uploads/<path:filename>')
# def upload_file(filename):
#     return mongo.send_file(filename)

# @app.route('/add_user')
# def add_user():
#     user = mongo.db.users
#     user.insert({'name': 'Anthony'})
#     return 'Added User!'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
