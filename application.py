import os
import requests
from flask import Flask, session, render_template, request, url_for, redirect, flash, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "T9NKrplU03zECQlrMhIFg", "isbns": "9781632168146"})
print(res.json())

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
notes = []


@app.route('/', methods=["GET", "POST"])
def index():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:

        return render_template("search.html")

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
        user = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
        user_id = user.id
        session['user_id'] = user_id
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


@app.route('/search', methods=['GET', 'POST'])
def search():

    if request.method=="POST":
        term = '%' + request.form.get("search_term") + '%'
        term = term.upper()
        books = db.execute("SELECT * FROM books WHERE (upper(title) like :term) OR (upper(author) like :term) OR (isbn like :term)", {"term": term }).fetchall()
        for book in books:
            print(f"found: {book.title}")
        if books is None:
            print(f"Search returned no books")
            flash("sorry, no results. Please try another search term.")
            return redirect(url_for('search'))
        return render_template('search_results.html', books=books)

    return render_template('search.html')

@app.route('/search/<isbn>', methods=['GET','POST'])
def display(isbn):
    # connect to goodreads API
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "T9NKrplU03zECQlrMhIFg", "isbns": isbn})
    data = res.json()
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {'isbn': isbn}).fetchone()
    book_id = book.id
    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {'book_id': book_id}).fetchall()
    return render_template("view_book.html", book=book, data=data, reviews=reviews)

@app.route('/review/<isbn>', methods=['GET', 'POST'])
def review(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {'isbn': isbn}).fetchone()    # the user must be logged in
    book_id = book.id

    # take the username from the session or redirect to login
    if not session.get('logged_in'):
        return render_template('login.html')
    user_id = session.get("user_id")
    print(f"your user id is {user_id}")
    if request.method=="POST":
        # take the values from the form
        rating = request.form.get('rating')
        review = request.form.get('review')
        print(f"User with user id of {user_id} has given the following review for {book_id}:\n \
        the rating is {rating} and the review is {review}")
        # rating and review can't be empty
        if review:
            if rating:
                if db.execute("SELECT * FROM reviews WHERE (user_id = :user_id) AND (book_id = :book_id)" , {"user_id":user_id, "book_id":book_id}).rowcount == 0:
                    
                    # add review to reviews table
                    db.execute("INSERT INTO reviews (user_id, book_id, rating, review) VALUES (:user_id, :book_id, :rating, :review)",
                                {"user_id": user_id, "book_id": book_id, "rating": rating, "review": review})
                    db.commit()
                    flash("thanks for submitting your review!")
                    return redirect(url_for('display', isbn=isbn))
                else:
                    flash("you can only submit one rating per book")

            else: 
                flash("You must submit a rating")
        else:
            flash("you must submit a review")

    return render_template('review.html', book=book, isbn=isbn)

@app.route("/api/books/<isbn>")
def book_api(isbn):
    ''' Return details about a single book '''
    # Make sure book exists

    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {'isbn': isbn}).fetchone()
    if book is None:
        return render_template('404.html')
    
    # get book details from goodreads
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "T9NKrplU03zECQlrMhIFg", "isbns": isbn})
    data = res.json()
    return jsonify({
        "title": book.title,
        "author": book.title,
        "year": book.year,
        "review_count": data['books'][0]['ratings_count'],
        "average_score": data['books'][0]['average_rating']
    })

if __name__ == '__main__':
    app.debug=True
    app.run()
