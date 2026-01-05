
from flask import Flask, request, jsonify, send_file, g
from flask_cors import CORS
import psycopg2
import io
import os
from flask import Flask, request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://jola197.mikrus.xyz:20197", "http://jola197.mikrus.xyz:30197", 
"http://domatormyszniec.pl",
    "https://domatormyszniec.pl",
    "http://www.domatormyszniec.pl",
    "https://www.domatormyszniec.pl"], supports_credentials=True)

DATABASE_CONFIG = {
    # "host": os.environ.get("DB_HOST", "host.docker.internal"),
    "host": os.environ.get("DB_HOST", "0.0.0.0"),
    "database": os.environ.get("DB_NAME", "products"),
    "user": os.environ.get("DB_USER", "zuzannaglinka"),
    "password": os.environ.get("DB_PASSWORD", "password")
}

def get_db():
    """Otwiera nowe połączenie z bazą danych, jeśli jeszcze nie zostało otwarte w kontekście żądania."""
    if 'db_conn' not in g:
        print(f"DEBUG: Connecting to DB with config: {DATABASE_CONFIG}", flush=True)
        print(f"DEBUG: os.environ keys: {list(os.environ.keys())}", flush=True)
        g.db_conn = psycopg2.connect(**DATABASE_CONFIG)
    return g.db_conn

@app.teardown_request
def close_db(exception):
    """Zamyka połączenie z bazą danych po zakończeniu żądania."""
    db = g.pop('db_conn', None)
    if db is not None:
        db.close()

# --------------------
# Routes
# --------------------

@app.route("/products", methods=["GET"])
def get_products():
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT id, name, price, description, category, ceneo_url FROM products;")
        products = cur.fetchall()
        result = [
            {
                "id": p[0],
                "name": p[1],
                "price": float(p[2]),
                "description": p[3],
                "category": p[4],
                "ceneo_url": p[5]
            }
            for p in products
        ]
        return jsonify(result)
        
    except Exception as e:
        print(f"Błąd podczas pobierania produktów: {e}", flush=True)
        return jsonify({"error": "Wewnętrzny błąd serwera DB"}), 500
        
    finally:
        cur.close()

@app.route('/products', methods=['POST'])
def add_product():
    conn = get_db()
    cur = conn.cursor()
    
    name = request.form.get('name')
    price = request.form.get('price')
    description = request.form.get('description')
    category = request.form.get('category')
    photo_file = request.files.get('image')
    image = photo_file.read() if photo_file else None
    ceneo_url = request.form.get('ceneo_url')

    try:
        cur.execute(
            "INSERT INTO products (name, price, description, category, image, ceneo_url) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
            (name, price, description, category, image, ceneo_url)
        )
        product_id = cur.fetchone()[0]
        conn.commit() # Zatwierdzamy zmiany

        return jsonify({
            'id': product_id,
            'name': name,
            'price': price,
            'description': description,
            'category': category,
            'ceneo_url': ceneo_url
        }), 201
        
    except Exception as e:
        conn.rollback() 
        print(f"Błąd podczas dodawania produktu: {e}")
        return jsonify({"error": "Wewnętrzny błąd serwera DB"}), 500
        
    finally:
        cur.close()

@app.route('/product_image/<int:product_id>', methods=['GET'])
def get_product_image(product_id):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT image FROM products WHERE id = %s;", (product_id,))
        row = cur.fetchone()
        
        if row and row[0]:
            # Zwracamy obrazek
            return send_file(io.BytesIO(row[0]), mimetype='image/jpeg')
        else:
            return jsonify({'error': 'Image not found'}), 404
    except Exception as e:
        print(f"Błąd podczas pobierania obrazka: {e}")
        return jsonify({"error": "Wewnętrzny błąd serwera DB"}), 500
    finally:
        cur.close()

@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id = %s;", (product_id,))
    conn.commit()
    cur.close()
    return jsonify({"success": True})

@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Wymagane nazwa użytkownika i hasło."}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256') 

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id;",
            (username, hashed_password)
        )
        conn.commit()
        user_id = cur.fetchone()[0]
        return jsonify({"message": f"Użytkownik {username} zarejestrowany pomyślnie!", "user_id": user_id}), 201
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({"error": "Nazwa użytkownika już istnieje."}), 409
    except Exception as e:
        conn.rollback()
        print(f"Błąd rejestracji: {e}")
        return jsonify({"error": "Błąd serwera."}), 500
    finally:
        cur.close()

@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = get_db()
    cur = conn.cursor()
    
    try:
        # 1. Pobierz hash z bazy
        cur.execute(
            "SELECT id, password FROM users WHERE username = %s;",
            (username,)
        )
        user_data = cur.fetchone()

        if user_data is None:
            return jsonify({"error": "Błędna nazwa użytkownika lub hasło."}), 401

        user_id, stored_hash = user_data
        
        if check_password_hash(stored_hash, password):

            return jsonify({"message": f"Zalogowano jako {username}.", "user_id": user_id}), 200
        else:
            return jsonify({"error": "Błędna nazwa użytkownika lub hasło."}), 401
            
    except Exception as e:
        print(f"Błąd logowania: {e}")
        return jsonify({"error": "Błąd serwera."}), 500
    finally:
        cur.close()

@app.route("/products/<int:product_id>/price", methods=["PATCH"])
def update_product_price(product_id):
    data = request.json
    new_price = data.get("price")
    if new_price is None:
        return jsonify({"error": "No price provided"}), 400
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE products SET price = %s WHERE id = %s;", (new_price, product_id))
        conn.commit()
        cur.close()
        return jsonify({"success": True, "price": new_price})
    except Exception as e:
        print(f"Błąd podczas aktualizacji ceny: {e}")
        return jsonify({"error": "Wewnętrzny błąd serwera DB"}), 500

# --------------------
# Run server
# --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)