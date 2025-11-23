from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)

# ------------------------------------------
# MongoDB Atlas Connection using ENV VAR
# ------------------------------------------
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise Exception("MONGO_URI environment variable not set!")

client = MongoClient(MONGO_URI)

# Database & Collections
db = client["bookstore_db"]
books_collection = db["books"]
reviews_collection = db["reviews"]


# ------------------------------------------
# Homepage – Show all books
# ------------------------------------------
@app.route("/")
def home():
    books = list(books_collection.find())
    for book in books:
        book["_id"] = str(book["_id"])
    return render_template("index.html", books=books)


# ------------------------------------------
# Add a new book
# ------------------------------------------
@app.route("/add_book", methods=["POST"])
def add_book():
    title = request.form.get("title")
    author = request.form.get("author")
    description = request.form.get("description")

    if title and author:
        books_collection.insert_one({
            "title": title,
            "author": author,
            "description": description
        })
    return redirect(url_for("home"))


# ------------------------------------------
# Book detail page + Reviews
# ------------------------------------------
@app.route("/book/<book_id>")
def book_detail(book_id):
    book = books_collection.find_one({"_id": ObjectId(book_id)})
    if book:
        book["_id"] = str(book["_id"])

    reviews = list(reviews_collection.find({"book_id": book_id}))
    return render_template("book_detail.html", book=book, reviews=reviews)


# ------------------------------------------
# Add a review to a book
# ------------------------------------------
@app.route("/add_review/<book_id>", methods=["POST"])
def add_review(book_id):
    name = request.form.get("name")
    review = request.form.get("review")

    if name and review:
        reviews_collection.insert_one({
            "book_id": book_id,
            "name": name,
            "review": review
        })

    return redirect(url_for("book_detail", book_id=book_id))


# ------------------------------------------
# Run the app (for local development)
# Render uses Gunicorn, not this
# ------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
