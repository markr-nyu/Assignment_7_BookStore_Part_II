from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3

app = Flask(__name__)
DATABASE = "bookstore.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # SQLite normally gives us rows as tuples, where we access values by position (row[2])
                                    # The row factory lets us access values by column name instead (row["title"] or {{ row.title }})
    return conn


@app.route("/", methods=["GET"])
def home():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM category
        ORDER BY categoryName
    """)
    categories = cursor.fetchall()

    conn.close()

    return render_template("index.html", categories=categories)


@app.route("/category", methods=["GET"])
def category():
    category_id = request.args.get("categoryId", type=int)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM category
        ORDER BY categoryName
    """)
    categories = cursor.fetchall()

    cursor.execute("""
        SELECT *
        FROM category
        WHERE categoryId = ?
    """, (category_id,))
    selected_category = cursor.fetchone()

    cursor.execute("""
        SELECT *
        FROM book
        WHERE categoryId = ?
        ORDER BY title
    """, (category_id,))
    books = cursor.fetchall()

    conn.close()

    return render_template(
        "category.html",
        categories=categories,
        selectedCategory=selected_category,
        books=books,
        searchTerm=None,
        nothingFound=False
    )


@app.route("/search", methods=["POST"])
def search():
    term = request.form.get("search", "").strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM category
        ORDER BY categoryName
    """)
    categories = cursor.fetchall()

    cursor.execute("""
        SELECT *
        FROM book
        WHERE lower(title) LIKE lower(?)
        ORDER BY title
    """, (f"%{term}%",))
    books = cursor.fetchall()

    conn.close()

    return render_template(
        "category.html",
        categories=categories,
        selectedCategory=None,
        books=books,
        searchTerm=term,
        nothingFound=(len(books) == 0)
    )

@app.route("/book", methods=["GET"])
def book_detail():
    book_id = request.args.get("bookId", type=int)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM category ORDER BY categoryName
    """)
    categories = cursor.fetchall()

    cursor.execute("""
        SELECT book.*, category.categoryName
        FROM book
        JOIN category ON book.categoryId = category.categoryId
        WHERE book.bookId = ?
    """, (book_id,))
    book = cursor.fetchone()

    conn.close()

    return render_template(
        "book_detail.html",
        book=book,
        categories=categories
    )

@app.route("/add-book", methods=["GET", "POST"])
def add_book():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM category ORDER BY categoryName
    """)
    categories = cursor.fetchall()

    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        isbn = request.form.get("isbn")
        price = request.form.get("price", type=float)
        image = request.form.get("image")
        category_id = request.form.get("categoryId", type=int)

        cursor.execute("""
            INSERT INTO book (categoryId, title, author, isbn, price, image, readNow)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (category_id, title, author, isbn, price, image))

        conn.commit()
        conn.close()

        return redirect(url_for("home"))

    conn.close()
    return render_template("add_book.html", categories=categories)


@app.errorhandler(Exception)
def handle_error(e):
    return render_template("error.html", error=e), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
    return render_template("error.html", error=e), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
