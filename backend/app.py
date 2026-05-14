from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import time

app = Flask(__name__)
CORS(app)

while True:
    try:
        conn = psycopg2.connect(
            host="postgres-service",
            database="shoplite",
            user="postgres",
            password="admin123"
        )

        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            price INTEGER,
            image VARCHAR(500),
            quantity INTEGER
        )
        """)

        conn.commit()

        cur.close()

        print("PostgreSQL connected successfully")

        break

    except Exception as e:
        print("Waiting for PostgreSQL...", e)
        time.sleep(5)

cart = []

@app.route("/api/products", methods=["GET"])
def get_products():
    cur = conn.cursor()

    cur.execute("SELECT * FROM products")

    rows = cur.fetchall()

    products = []

    for row in rows:
        products.append({
            "id": row[0],
            "name": row[1],
            "price": row[2],
            "image": row[3],
            "quantity": row[4]
        })

    cur.close()

    return jsonify(products)

@app.route("/api/products", methods=["POST"])
def add_product():
    data = request.json

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO products (name, price, image, quantity)
        VALUES (%s, %s, %s, %s)
        """,
        (
            data["name"],
            data["price"],
            data["image"],
            data["quantity"]
        )
    )

    conn.commit()

    cur.close()

    return jsonify({"message": "Product added"})

@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM products WHERE id = %s",
        (product_id,)
    )

    conn.commit()

    cur.close()

    return jsonify({"message": "Product deleted"})

@app.route("/api/products/<int:product_id>/increase", methods=["PUT"])
def increase_quantity(product_id):
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE products
        SET quantity = quantity + 1
        WHERE id = %s
        """,
        (product_id,)
    )

    conn.commit()

    cur.close()

    return jsonify({"message": "Quantity increased"})

@app.route("/api/products/<int:product_id>/decrease", methods=["PUT"])
def decrease_quantity(product_id):
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE products
        SET quantity = quantity - 1
        WHERE id = %s AND quantity > 0
        """,
        (product_id,)
    )

    conn.commit()

    cur.close()

    return jsonify({"message": "Quantity decreased"})

@app.route("/api/cart", methods=["GET"])
def get_cart():
    return jsonify(cart)

@app.route("/api/cart", methods=["POST"])
def add_to_cart():
    data = request.json

    cart.append(data)

    return jsonify({"message": "Added to cart"})

@app.route("/api/cart/<int:index>", methods=["DELETE"])
def remove_from_cart(index):
    cart.pop(index)

    return jsonify({"message": "Item removed"})

@app.route("/api/checkout", methods=["POST"])
def checkout():
    cur = conn.cursor()

    for item in cart:
        cur.execute(
            """
            UPDATE products
            SET quantity = quantity - 1
            WHERE id = %s AND quantity > 0
            """,
            (item["id"],)
        )

    conn.commit()

    cart.clear()

    cur.close()

    return jsonify({"message": "Payment successful"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
