import os
from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

#DATABASE_URL="postgres://rncatekbuhjois:c6d20fb8f9652a90c5ef0c2a8e3d8a0e15bfb6292b59ca609c87588745111654@ec2-35-169-254-43.compute-1.amazonaws.com:5432/d40bt8q1gl37m6"
app = Flask(__name__)
app.secret_key='projectbooks'
# ------ Check for environment variable ---------
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
# ---- Configure session to use filesystem ------
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
# ------------ Set up database---------------------
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
# -----------    Declare functions ------------------
def valid_login(user_id, password):
    if db.execute("SELECT * FROM users WHERE user_id= :user_id AND password =:password",{"user_id":user_id, "password":password}).rowcount == 0:
        return False
    db.execute("SELECT * FROM users WHERE user_id= :user_id AND password =:password",{"user_id":user_id, "password":password})
    return True
def valid_registration(user_id):
    if db.execute("SELECT * FROM users WHERE user_id= :user_id", { "user_id":user_id}).rowcount == 0:
        return True
def registers(user_id, password):
    db.execute("INSERT INTO users VALUES (:user_id, :password)",{"user_id":user_id, "password":password})
    db.commit()


# --------------    ROUTES  -------------------------
@app.route("/")
def index():
    if 'user_id' in session:
        return render_template("search.html",user_id=session['user_id'])
    return render_template("login.html")

@app.route("/login",methods=['POST','GET'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form.get("user_id"), request.form.get("password")):
            session['user_id']= request.form.get("user_id")
            return render_template("search.html", user_id=session['user_id'])
        else:
            error='Invalid Username/Password'
        return render_template('login.html', error=error)
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('user_id',None)
    return redirect(url_for('login'))

@app.route("/register",methods=['POST','GET'])
def register():
    error = None
    if request.method == 'POST':
        if valid_registration (request.form.get("user_id")):
            registers(request.form.get("user_id"), request.form.get("password"))
            session['user_id']= request.form.get("user_id")
            return render_template("search.html",user_id=session['user_id'] )
        else:
            error='Username taken'
    return render_template('register.html', error=error)

@app.route("/search")
def search():
    if 'user_id' in session:
        return render_template("search.html")
    else:
        return render_template("login.html")


@app.route("/results", methods=["POST"])
def results():
    to_search=request.form.get("to_search")
    keyword="%"+to_search+"%"
    books1 = db.execute("SELECT * FROM books WHERE title LIKE :keyword OR author LIKE :keyword OR isbn LIKE :keyword", { "keyword":keyword}).fetchall()
    return render_template("results.html", books1=books1, user_id=session['user_id'])

@app.route("/bookinfo/<string:isbn>", methods=['POST','GET'])
def bookinfo(isbn):
    # Select from DB
    # PROBABLY USE JOIN TO GET ALL COMMENTS OF THIS BOOK
    if request.method=='POST':
        #user enters a review. 
        review=request.form.get("review")

        db.execute("INSTERT INTO reviews (user_id, review, book_id) VALUES (:user_id, :review, :book_id)", { "user_id":session['user_id'],"review":review,"book_id":book_id})
    book=db.execute("SELECT * from books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    # ACCESS rating from API
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "nod4FP1rMrbxf6yj42v7Wg", "isbns": {isbn}})
    res=res.json()
    rating=res ['books'][0]['average_rating']
    
    return render_template("book.html", book=book, rating=rating,user_id=session['user_id'])

@app.route("/api/<string:isbn>") # this works
def get_api(isbn):
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "nod4FP1rMrbxf6yj42v7Wg", "isbns": {isbn}})
    return res.json()