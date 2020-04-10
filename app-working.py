from flask import Flask, session, render_template, request, url_for, redirect, flash
from flask_session import Session

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

notes = []
user = 'admin'
password = 'password'

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
def admin_login():
    if request.form['password']==password and request.form['username']==user:
        session['logged_in'] = True
    else:
        flash('wrong username or password!')
    return index()

@app.route('/logout')
def logout():
    # remove the username from the session if it's not there
    session.clear()
    return redirect(url_for('index'))

@app.route('/register', methods=["POST"])
def register():
    # get form values
    # check that fields are not empty
    # check that username is not already taken
    # add user to the database
    return render_template('register.html')



if __name__ == '__main__':
    app.debug=True
    app.run()
