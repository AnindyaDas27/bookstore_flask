from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)

# --- Mongo Connection ---
MONGO_URI = os.getenv("MONGO_URI")  # Make sure this is set in Render
client = MongoClient(MONGO_URI)

db = client["bookstore_db"]
books_collection = db["books"]
reviews_collection = db["reviews"]

@app.route("/")
def home():
    books = list(books_collection.find())
    return render_template("index.html", books=books)

@app.route("/add_book", methods=["POST"])
def add_book():
    title = request.form.get("title")
    author = request.form.get("author")

    if title and author:
        books_collection.insert_one({"title": title, "author": author})

    return redirect(url_for("home"))

@app.route("/book/<book_id>")
def book_detail(book_id):
    try:
        book = books_collection.find_one({"_id": ObjectId(book_id)})
    except:
        return "Invalid book ID", 400

    reviews = list(reviews_collection.find({"book_id": ObjectId(book_id)}))

    return render_template("book_detail.html", book=book, reviews=reviews)

@app.route("/book/<book_id>/review", methods=["POST"])
def add_review(book_id):
    name = request.form.get("name")
    review_text = request.form.get("review")
    rating = request.form.get("rating")

    if name and review_text and rating:
        reviews_collection.insert_one({
            "book_id": ObjectId(book_id),
            "name": name,
            "review": review_text,
            "rating": int(rating)
        })

    return redirect(url_for("book_detail", book_id=book_id))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
