from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)

# -----------------------------
# MongoDB Atlas Connection
# -----------------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://Anindya:Anindya1234@cluster0.ztibttn.mongodb.net/?retryWrites=true&w=majority")

client = MongoClient(MONGO_URI)
db = client["bookstore_db"]
books_collection = db["books"]
reviews_collection = db["reviews"]


# -----------------------------
# Homepage – List All Books
# -----------------------------
@app.route("/")
def home():
    books = list(books_collection.find())
    for book in books:
        book["_id"] = str(book["_id"])
    return render_template("index.html", books=books)


# -----------------------------
# Book Detail Page (GET + POST for review)
# -----------------------------
@app.route("/book/<book_id>", methods=["GET", "POST"])
def book_detail(book_id):

    # Handle Review Submission
    if request.method == "POST":
        username = request.form.get("username")
        comment = request.form.get("comment")
        rating = request.form.get("rating")

        review = {
            "book_id": book_id,
            "username": username,
            "comment": comment,
            "rating": int(rating)
        }

        reviews_collection.insert_one(review)
        return redirect(url_for("book_detail", book_id=book_id))

    # GET — show the page
    book = books_collection.find_one({"_id": ObjectId(book_id)})
    if not book:
        return "Book not found", 404

    book["_id"] = str(book["_id"])

    # All reviews for this book
    reviews = list(reviews_collection.find({"book_id": book_id}))

    return render_template("book_detail.html", book=book, reviews=reviews)


# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
