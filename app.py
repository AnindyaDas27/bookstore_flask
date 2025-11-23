from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)

# ------------------------
# MongoDB Atlas Connection
# ------------------------

MONGO_URI = os.environ.get("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["bookstore_db"]
books_collection = db["books"]
reviews_collection = db["reviews"]


# ------------------------
# Homepage – Show all books
# ------------------------
@app.route("/")
def home():
    books = list(books_collection.find())
    for book in books:
        book["_id"] = str(book["_id"])
    return render_template("index.html", books=books)


# ------------------------
# Add a new book
# ------------------------
@app.route("/add_book", methods=["POST"])
def add_book():
    title = request.form.get("title")
    author = request.form.get("author")

    if title and author:
        books_collection.insert_one({
            "title": title,
            "author": author
        })

    return redirect(url_for("home"))


# ------------------------
# Book details page
# ------------------------
@app.route("/book/<id>")
def book_detail(id):
    book = books_collection.find_one({"_id": ObjectId(id)})
    if not book:
        return "Book not found", 404

    book["_id"] = str(book["_id"])

    reviews = list(reviews_collection.find({"book_id": id}))
    for review in reviews:
        review["_id"] = str(review["_id"])

    return render_template("book_detail.html", book=book, reviews=reviews)


# ------------------------
# Add review to a book
# ------------------------
@app.route("/add_review/<id>", methods=["POST"])
def add_review(id):
    name = request.form.get("name")
    review_text = request.form.get("review")
    rating = request.form.get("rating")

    reviews_collection.insert_one({
        "book_id": id,
        "name": name,
        "review": review_text,
        "rating": rating
    })

    return redirect(url_for("book_detail", id=id))


# ------------------------
# Run the app
# ------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
