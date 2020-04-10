import os
from flask import Flask, session, render_template, request, url_for, redirect, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
notes = []


@app.route('/', methods=["GET", "POST"])
def index():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        if session.get("notes") is None:
            session["notes"] = []
        if request.method=="POST":
            note = request.form.get("note")
            session["notes"].append(note)
        return render_template("index.html", notes=session["notes"])

@app.route('/login', methods=["GET", "POST"])
def login():

    username = request.form.get('username')
    password = request.form.get('password')

    # check to see if username exists
    if db.execute("SELECT * FROM users WHERE (username = :username) AND (password = :password)" , {"username":username, "password":password}).rowcount == 0:
        flash("username doesn't exist or password doesn't match")
        return redirect(url_for('index'))
    else:
        session['logged_in'] = True

    return index()

@app.route('/logout')
def logout():
    # remove the username from the session if it's not there
    session.clear()
    return redirect(url_for('index'))

@app.route('/register', methods=["GET","POST"])
def register():
    if request.method=="POST":
        # get form values
        username = request.form.get('username')
        password = request.form.get('password')
        # check that fields are not empty
        if username == None or password == None:
            flash('You must enter all fields')
            return redirect('index')
        # check that username is not already taken
        if db.execute("SELECT * FROM users WHERE (username = :username)" , {"username":username}).rowcount > 0:
            flash("That username already exists")
            return redirect(url_for('index'))
        # add user to the database
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                {"username": username, "password": password})
        db.commit()
        flash("successfully registered")
        return redirect(url_for('index'))
    return render_template('register.html')



if __name__ == '__main__':
    app.debug=True
    app.run()
