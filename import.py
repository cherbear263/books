import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL")) # database engine object from SQLAlchemy that manages connections to the database

def main():                                                # DATABASE_URL is an environment variable that indicates where the database lives
    db = scoped_session(sessionmaker(bind=engine))  
    books = db.execute("SELECT isbn, title, author, year FROM books").fetchall()
    for book in books:
        print(f"{book.title} {book.year}")

    f = open("books.csv")
    reader = csv.reader(f)
    next(reader, None)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
        {"isbn":isbn, "title":title, "author":author, "year":year})
        print(f"Added {title} with isbn {isbn} by author {author}")
    db.commit()

if __name__ == "__main__":
    main()
