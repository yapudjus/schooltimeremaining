from logging import ERROR, error
from flask import Flask, render_template, redirect, request, sessions, url_for, session, flash
import json
import sys

from flask import current_app
import flask
from urllib.parse import urlparse, urljoin

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


app = Flask(__name__)

app = Flask(__name__)
app.config['ENV'] = 'development'
app.secret_key = 'thereoncewasashipthatputtosea'

with open('users.json') as f:
    user = json.load(f)

@app.route("/")
def root():
    return redirect(url_for("home"))

@app.route("/home")
def home():
    return render_template('home.html', width=50)

# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username not in user : error = 'user doesn\'t exist'
        elif user[username]["password"] != password : error = 'wrong password'
        else:
            session['user'] = username
            return redirect(url_for('settings'))
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username not in user : error = 'user doesn\'t exist'
        elif user[username]["password"] != password : error = 'wrong password'
        else:
            session['user'] = username
            print(f'user {username} logged in')
            return redirect(url_for('settings'))
    return render_template('register.html', error=error)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    e = None
    if('user' in session and session['user'] in user):
        if request.method == 'POST':
            edusername = request.form['username']
            edpassword = request.form['password']
        return render_template("settings.html", error=e)
    return render_template("loginerror.html")

@app.route('/logout')
def logout():
    session.pop('user')
    return render_template("logout.html")

if __name__ == "__main__":
    app.run(port=800, host='m.yapudjusowndomain.fr', debug=True)