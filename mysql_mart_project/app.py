import os
from decimal import Decimal, InvalidOperation
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-for-your-project")

def get_db_connection():
    """Create a MySQL connection using local or hosted environment variables.

    Railway's MySQL service exposes MYSQLHOST, MYSQLUSER, MYSQLPASSWORD,
    MYSQLDATABASE, and MYSQLPORT. The MYSQL_* alternatives support local setup.
    """
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST") or os.getenv("MYSQLHOST", "localhost"),
        user=os.getenv("MYSQL_USER") or os.getenv("MYSQLUSER", "root"),
        password=os.getenv("MYSQL_PASSWORD") or os.getenv("MYSQLPASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE") or os.getenv("MYSQLDATABASE", "mysql_mart"),
        port=int(os.getenv("MYSQL_PORT") or os.getenv("MYSQLPORT", "3306"))
    )

def query_db(sql, params=(), fetch=True):
    """Run a parameterized query and always close the database connection."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(sql, params)
        if fetch:
            return cursor.fetchall()
        connection.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        connection.close()

@app.route("/")
def index():
    try:
        stats = query_db("""
            SELECT
              (SELECT COUNT(*) FROM products) AS product_count,
              (SELECT COUNT(DISTINCT customer_name) FROM orders) AS customer_count,
              (SELECT COUNT(*) FROM orders) AS order_count,
              (SELECT COALESCE(SUM(total_amount), 0) FROM orders) AS sales_total
        """)[0]
        latest_orders = query_db("""
            SELECT o.order_id, o.customer_name, o.order_date, o.total_amount, o.status
            FROM orders o ORDER BY o.order_id DESC LIMIT 5
        """)
        return render_template("index.html", stats=stats, latest_orders=latest_orders)
    except Error as exc:
        return render_template("setup_error.html", error=str(exc)), 500

@app.route("/products")
def products():
    search = request.args.get("q", "").strip()
    try:
        if search:
            items = query_db("""
                SELECT * FROM products
                WHERE product_name LIKE %s OR category LIKE %s
                ORDER BY product_id DESC
            """, (f"%{search}%", f"%{search}%"))
        else:
            items = query_db("SELECT * FROM products ORDER BY product_id DESC")
        return render_template("products.html", products=items, search=search)
    except Error as exc:
        flash(f"Database error: {exc}", "error")
        return render_template("products.html", products=[], search=search)

@app.route("/products/add", methods=["POST"])
def add_product():
    name = request.form.get("product_name", "").strip()
    category = request.form.get("category", "").strip()
    price_text = request.form.get("price", "").strip()
    stock_text = request.form.get("stock", "").strip()
    if not name or not category:
        flash("Product name and category are required.", "error")
        return redirect(url_for("products"))
    try:
        price = Decimal(price_text)
        stock = int(stock_text)
        if price < 0 or stock < 0:
            raise ValueError
    except (InvalidOperation, ValueError):
        flash("Enter a valid non-negative price and stock quantity.", "error")
        return redirect(url_for("products"))
    try:
        query_db(
            "INSERT INTO products (product_name, category, price, stock) VALUES (%s, %s, %s, %s)",
            (name, category, price, stock), fetch=False
        )
        flash("Product added to the MySQL database.", "success")
    except Error as exc:
        flash(f"Could not add product: {exc}", "error")
    return redirect(url_for("products"))

@app.route("/products/<int:product_id>/update", methods=["POST"])
def update_product(product_id):
    try:
        price = Decimal(request.form.get("price", ""))
        stock = int(request.form.get("stock", ""))
        if price < 0 or stock < 0:
            raise ValueError
        query_db("UPDATE products SET price=%s, stock=%s WHERE product_id=%s",
                 (price, stock, product_id), fetch=False)
        flash("Product updated successfully.", "success")
    except (InvalidOperation, ValueError):
        flash("Enter a valid non-negative price and stock.", "error")
    except Error as exc:
        flash(f"Could not update product: {exc}", "error")
    return redirect(url_for("products"))

@app.route("/products/<int:product_id>/delete", methods=["POST"])
def delete_product(product_id):
    try:
        query_db("DELETE FROM products WHERE product_id=%s", (product_id,), fetch=False)
        flash("Product deleted if it was not linked to an existing order.", "success")
    except Error:
        flash("This product may be linked to an order, so MySQL prevented its deletion.", "error")
    return redirect(url_for("products"))

@app.route("/orders")
def orders():
    try:
        records = query_db("SELECT * FROM orders ORDER BY order_id DESC")
        return render_template("orders.html", orders=records)
    except Error as exc:
        flash(f"Database error: {exc}", "error")
        return render_template("orders.html", orders=[])

@app.route("/orders/place", methods=["POST"])
def place_order():
    customer = request.form.get("customer_name", "").strip()
    try:
        product_id = int(request.form.get("product_id", ""))
        quantity = int(request.form.get("quantity", ""))
        if not customer or quantity < 1:
            raise ValueError
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            connection.start_transaction()
            cursor.execute("SELECT product_name, price, stock FROM products WHERE product_id=%s FOR UPDATE", (product_id,))
            product = cursor.fetchone()
            if not product:
                raise ValueError("That product was not found.")
            if product["stock"] < quantity:
                raise ValueError("There is not enough stock for that quantity.")
            total = product["price"] * quantity
            cursor.execute(
                "INSERT INTO orders (customer_name, product_id, product_name, quantity, total_amount, status) VALUES (%s,%s,%s,%s,%s,%s)",
                (customer, product_id, product["product_name"], quantity, total, "Placed")
            )
            cursor.execute("UPDATE products SET stock=stock-%s WHERE product_id=%s", (quantity, product_id))
            connection.commit()
            flash("Order placed! The order and stock update were saved in MySQL.", "success")
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()
    except ValueError as exc:
        flash(str(exc) or "Enter a valid customer, product and quantity.", "error")
    except (InvalidOperation, Error) as exc:
        flash(f"Could not place order: {exc}", "error")
    except Exception as exc:
        flash(f"Could not place order: {exc}", "error")
    return redirect(url_for("orders"))

@app.route("/notes")
def notes():
    return render_template("notes.html")

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    questions = [
        {"q": "Which SQL command retrieves records?", "options": ["GET", "SELECT", "FETCH ALL", "SHOW ROWS"], "answer": "SELECT", "explain": "SELECT retrieves data from one or more tables."},
        {"q": "Which key uniquely identifies a row?", "options": ["Foreign key", "Duplicate key", "Primary key", "Search key"], "answer": "Primary key", "explain": "A primary key uniquely identifies each row."},
        {"q": "Which clause filters rows before grouping?", "options": ["HAVING", "ORDER BY", "WHERE", "GROUP BY"], "answer": "WHERE", "explain": "WHERE filters rows before GROUP BY is applied."},
        {"q": "Which Python package connects Python to MySQL here?", "options": ["mysql-connector-python", "turtle", "random", "csv-only"], "answer": "mysql-connector-python", "explain": "mysql-connector-python provides a MySQL driver for Python."},
        {"q": "Which SQL command changes existing records?", "options": ["ALTER", "UPDATE", "CREATE", "INSERT"], "answer": "UPDATE", "explain": "UPDATE modifies values in existing rows."}
    ]
    result = None
    if request.method == "POST":
        score = sum(1 for i, q in enumerate(questions) if request.form.get(f"q{i}") == q["answer"])
        result = {"score": score, "total": len(questions), "questions": questions,
                  "answers": [request.form.get(f"q{i}", "") for i in range(len(questions))]}
    return render_template("quiz.html", questions=questions, result=result)

if __name__ == "__main__":
    # Works locally and on hosting platforms that provide a PORT variable.
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
