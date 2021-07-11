from flask import Flask, render_template,request,redirect, session
from flask_pymongo import PyMongo
import os
from passlib.hash import pbkdf2_sha256
app = Flask(__name__)


if os.environ.get("SECRET_KEY") == None:
    file = open("secret_key.txt", "r")
    secretkey = file.read().strip()
    app.config["SECRET_KEY"] = secretkey
    print('local')
    file.close()
else:
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

if os.environ.get("MONGO_URI") == None:
    file = open("connectionstring.txt", "r")
    connectionstring = file.read().strip()
    app.config["MONGO_URI"] = connectionstring
    print('local')
    file.close()
else:
    app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
mongo = PyMongo(app)


@app.route('/')
def index():
    return render_template('user_register.html')

@app.route('/user_register', methods = ["GET","POST"])
def user_register():
    if request.method == 'GET':
        return render_template('user_register.html')
    else:
        form = request.form
        firstname = form['FirstName'].strip()
        lastname = form['LastName'].strip()
        email = form['Email'].strip()
        if email == '':
            print('email is required')
            return redirect('/user_register')
        userinfo = mongo.db.user_accounts.find_one({'email':email})
        if userinfo is not None:
            print('account already exists with this email')
            return redirect('/user_signin')
        password = form['Password']
        hashedpassword = pbkdf2_sha256.hash(password)
        record = {'firstname':firstname, 'lastname':lastname, 'email':email, 'password':hashedpassword}
        mongo.db.user_accounts.insert_one(record)
        return redirect('/user_signin')

@app.route('/user_signin', methods = ["GET","POST"])
def user_signin():
    if request.method == "GET":
        return render_template('user_signin.html')
    else:
        form = request.form
        email = form['email'].strip()
        if email == '':
            print('email is required')
            return redirect('/user_signin')
        userinfo = mongo.db.user_accounts.find_one({'email':email})
        if userinfo is None:
            print('account does not exist create an account')
            return redirect('/user_register')
        password = form['password']        
        if pbkdf2_sha256.verify(password, userinfo['password']):
            print('login succesful, welcome')
            session['user'] = email
            return redirect('/user_home')
        else:
            print('login failed, try again')
            return redirect('/user_signin')

@app.route('/user_home')
def user_home():
    if 'user' not in session:
        return redirect('/user_signin')
        
    return render_template('user_home.html')









if __name__ == "__main__":
    app.run(debug=True)