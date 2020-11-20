""" This is where we import data from the csv file"""
#isbn,title,author,year----- header removed from CSV
import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")


def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn,title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn,:title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"Added book : {isbn} :: {title} by {author } ({year})")
    db.commit()

if __name__ == "__main__":
    main()
