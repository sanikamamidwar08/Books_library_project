from flask import Flask, render_template, request, redirect, url_for
import sqlite3

DATABASE = 'database.db'
app = Flask(__name__)

# -------------------------
# Database setup
# -------------------------
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                year INTEGER NOT NULL,
                image TEXT NOT NULL
            )
            """
        )
        conn.commit()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_books():
    conn = get_db_connection()
    books_list = conn.execute("SELECT * FROM books ORDER BY id").fetchall()
    conn.close()
    return books_list

# -------------------------
# Routes
# -------------------------
@app.route("/")
def index():
    books = get_all_books()
    return render_template("index.html", books=books)

@app.route('/add-book')
def add_book_form():
    return render_template('add_book.html')

@app.route('/add-book/submit', methods=['POST'])
def add_book_submit():
    title = request.form.get('title')
    author = request.form.get('author')
    year = request.form.get('year')
    image = request.form.get('image')

    if not (title and author and year and image):
        return "Please fill out all fields"

    try:
        year = int(year)
    except ValueError:
        return "Invalid year"

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO books (title, author, year, image) VALUES (?, ?, ?, ?)",
        (title, author, year, image)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route("/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route("/book_detail/<int:book_id>")
def book_detail(book_id):
    conn = get_db_connection()
    book = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    conn.close()
    if book:
        return render_template("book_detail.html", book=book)
    else:
        return render_template("404.html"), 404

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html", error=error), 404

# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
