from apscheduler.schedulers.background import BackgroundScheduler
import requests
from bs4 import BeautifulSoup
import re
import datetime
import atexit
from flask import Flask, request, jsonify, send_file, g
from flask_cors import CORS
import psycopg2
import io
import os
from flask import Flask, request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", 
"http://jola197.mikrus.xyz:20197", 
"http://jola197.mikrus.xyz:30197", 
"http://domatormyszyniec.pl",
    "https://domatormyszyniec.pl",
    "http://www.domatormyszyniec.pl",
    "https://www.domatormyszyniec.pl"], supports_credentials=True)

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
# Routes
# --------------------
# --- CENEO PRICE CHECK SCHEDULER ---
def scrape_single_product(prod_id, prod_price, ceneo_url):
    """Refactored helper to scrape one product, used by daily job and immediate triggers."""
    if not prod_price or not ceneo_url:
        return

    # Log processing attempt
    print(f"[CENEO] Processing product {prod_id} (Price: {prod_price})", flush=True)

    try:
        # Create separate DB connection for this thread
        with psycopg2.connect(**DATABASE_CONFIG) as conn:
            with conn.cursor() as cur:
                # Try to convert our price to float for comparison
                our_price_float = None
                try:
                    if prod_price:
                        # Clean price string (handle "1 200,00", "1200.00", etc)
                        clean_price = str(prod_price).replace(',', '.').replace(' ', '').replace('\xa0', '')
                        our_price_float = float(clean_price)
                except ValueError:
                    print(f"[CENEO] Product {prod_id} has invalid price format '{prod_price}'. Skipping.", flush=True)
                    return 
                
                ceneo_last_price = None
                is_visible = True
                try:
                    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
                    r = requests.get(ceneo_url, headers=headers, timeout=10)
                    if r.status_code == 200:
                        soup = BeautifulSoup(r.text, 'html.parser')
                        
                        # Strategy 1: Look for Meta tags (Most reliable, insensitive to UI changes)
                        price_meta = soup.select_one('meta[itemprop="price"]')
                        if not price_meta:
                            price_meta = soup.select_one('meta[property="product:price:amount"]')
                        
                        if price_meta and price_meta.get('content'):
                             try:
                                 ceneo_last_price = float(price_meta['content'].replace(',', '.'))
                                 print(f"[CENEO] Found price via META tag: {ceneo_last_price}", flush=True)
                             except:
                                 pass
                        
                        # Strategy 2: Look for data-price attribute (Visual elements)
                        if ceneo_last_price is None:
                            price_tag = soup.select_one('[data-price]')
                            if price_tag:
                                ceneo_last_price = float(price_tag['data-price'].replace(',', '.'))

                        # Strategy 3: Fallback text search
                        if ceneo_last_price is None:
                            # Fallback text search
                            price_text = soup.find(string=re.compile(r'\d+[\.,]?\d*\s*zł'))
                            if price_text:
                                match = re.search(r'(\d+[\.,]?\d*)', price_text)
                                if match:
                                    ceneo_last_price = float(match.group(1).replace(',', '.'))
                        
                        if ceneo_last_price is None:
                             print(f"[CENEO] Product {prod_id}: Page loaded but NO PRICE found. Selector failed.", flush=True)
                    else:
                         print(f"[CENEO] Product {prod_id}: HTTP Error {r.status_code}", flush=True)
                    
                    # Comparison Logic
                    if ceneo_last_price is not None:
                        # If Ceneo price is LOWER than our price -> Hide
                        if ceneo_last_price < our_price_float:
                            is_visible = False
                        
                        print(f"[CENEO] Result for {prod_id}: Our={our_price_float}, Ceneo={ceneo_last_price}. Visible={is_visible}", flush=True)
                        
                        cur.execute(
                            "UPDATE products SET ceneo_last_price=%s, ceneo_check_date=%s, visible=%s WHERE id=%s",
                            (ceneo_last_price, datetime.date.today(), is_visible, prod_id)
                        )
                        conn.commit()
                except Exception as e:
                    print(f"[CENEO] Error processing product {prod_id}: {e}", flush=True)
    except Exception as e:
         print(f"[CENEO] DB Error in single scrape: {e}", flush=True)

def check_ceneo_prices():
    print("[CENEO] Daily price check started", flush=True)
    try:
        # Create a new connection since this runs in a thread
        with psycopg2.connect(**DATABASE_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, price, ceneo_url FROM products WHERE ceneo_url IS NOT NULL AND ceneo_url != ''")
                products = cur.fetchall()
                
                for prod in products:
                    prod_id, prod_price, ceneo_url = prod
                    scrape_single_product(prod_id, prod_price, ceneo_url)
                    
    except Exception as e:
        print(f"[CENEO] Scheduler Error: {e}", flush=True)

# Start scheduler logic
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_ceneo_prices, trigger="interval", days=1)
scheduler.start()

# Check prices immediately on startup (in a separate thread if needed, but here simple call is fine)
# Note: This might block startup slightly, but ensures user sees results.
from threading import Thread
Thread(target=check_ceneo_prices).start()

atexit.register(lambda: scheduler.shutdown())

@app.route("/products", methods=["GET"])
def get_products():
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT id, name, price, description, category, ceneo_url, content_type, visible, ceneo_last_price FROM products;")
        products = cur.fetchall()
        result = [
            {
                "id": p[0],
                "name": p[1],
                "price": p[2], # Return as string or content from DB
                "description": p[3],
                "category": p[4],
                "ceneo_url": p[5],
                "content_type": p[6] or 'image/jpeg',
                "visible": p[7] if p[7] is not None else True,
                "ceneo_last_price": float(p[8]) if p[8] is not None else None
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
    ceneo_url = request.form.get('ceneo_url')
    
    # Obsługa wielu zdjęć
    images = request.files.getlist('images')
    
    # Pierwsze zdjęcie jako okładka
    cover_image = None
    cover_mimetype = 'image/jpeg'
    
    if images:
        cover_image = images[0].read()
        cover_mimetype = images[0].mimetype or 'image/jpeg'
        images[0].seek(0) # Reset pointer

    # Konwersja pustego stringa na None (dla bazy danych NULL)
    if not price or price.strip() == "":
        price = None

    try:
        cur.execute(
            "INSERT INTO products (name, price, description, category, image, content_type, ceneo_url) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (name, price, description, category, cover_image, cover_mimetype, ceneo_url)
        )
        product_id = cur.fetchone()[0]
        
        # Zapisz wszystkie pliki do tabeli product_images z typem zawartości
        for img in images:
            img_data = img.read()
            mimetype = img.mimetype or 'image/jpeg' # Default to jpeg
            cur.execute(
                "INSERT INTO product_images (product_id, image, content_type) VALUES (%s, %s, %s)",
                (product_id, img_data, mimetype)
            )
            
        conn.commit()

        return jsonify({
            'id': product_id,
            'name': name,
            'price': price,
            'description': description,
            'category': category,
            'ceneo_url': ceneo_url,
            'content_type': cover_mimetype
        }), 201
        
    except Exception as e:
        conn.rollback() 
        print(f"Błąd podczas dodawania produktu: {e}")
        return jsonify({"error": "Wewnętrzny błąd serwera DB"}), 500
        
    finally:
        cur.close()
        
        # --- TRIGGER IMMEDIATE CENEO CHECK ---
        if ceneo_url and ceneo_url.strip():
             Thread(target=scrape_single_product, args=(product_id, price, ceneo_url)).start()

@app.route('/product_image/<int:product_id>', methods=['GET'])
def get_product_image(product_id):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT image, content_type FROM products WHERE id = %s;", (product_id,))
        row = cur.fetchone()
        
        if row and row[0]:
            content_type = row[1] or 'image/jpeg'
            return send_file(io.BytesIO(row[0]), mimetype=content_type)
        else:
            return jsonify({'error': 'Image not found'}), 404
    except Exception as e:
        print(f"Błąd podczas pobierania obrazka: {e}")
        return jsonify({"error": "Wewnętrzny błąd serwera DB"}), 500
    finally:
        cur.close()

@app.route('/product_images/<int:product_id>', methods=['GET'])
def get_product_gallery_ids(product_id):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, content_type FROM product_images WHERE product_id = %s ORDER BY id ASC;", (product_id,))
        rows = cur.fetchall()
        # Return list of objects {id, content_type}
        gallery = [{"id": row[0], "content_type": row[1]} for row in rows]
        return jsonify(gallery)
    except Exception as e:
        print(f"Błąd podczas pobierania galerii: {e}")
        return jsonify({"error": "DB Error"}), 500
    finally:
        cur.close()

@app.route('/images/<int:image_id>', methods=['GET'])
def get_gallery_image(image_id):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT image, content_type FROM product_images WHERE id = %s;", (image_id,))
        row = cur.fetchone()
        if row and row[0]:
            content_type = row[1] or 'image/jpeg'
            return send_file(io.BytesIO(row[0]), mimetype=content_type)
        else:
            return jsonify({'error': 'Image not found'}), 404
    except Exception as e:
        print(f"Błąd pobierania zdjęcia z galerii: {e}")
        return jsonify({"error": "DB Error"}), 500
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
    # Allow updating to None or empty string if that's the intent, or just new string
    # if new_price is None: ... (Previously we required it, now let's allow string updates)
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
    finally:
        # Retrieve ceneo_url to check
        try:
             conn2 = get_db()
             cur2 = conn2.cursor()
             cur2.execute("SELECT ceneo_url FROM products WHERE id=%s", (product_id,))
             row = cur2.fetchone()
             if row and row[0]: # ceneo_url exists
                  Thread(target=scrape_single_product, args=(product_id, new_price, row[0])).start()
        except:
             pass

# --------------------
# Run server
# --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)