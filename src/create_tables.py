import os
import io
import psycopg2
from werkzeug.security import generate_password_hash
import getpass

DATABASE_CONFIG = {
    "host": os.environ.get("DB_HOST", "0.0.0.0"),
    "database": os.environ.get("DB_NAME", "products"),
    "user": os.environ.get("DB_USER", "zuzannaglinka"),
    "password": os.environ.get("DB_PASSWORD", "password")
}

def init_db():
    print("Łączenie z bazą danych...")
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cur = conn.cursor()

        print("Tworzenie tabeli users...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(200) NOT NULL
            );
        """)

        print("Tworzenie tabeli products...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                price NUMERIC(10, 2) NOT NULL,
                description TEXT,
                category VARCHAR(50),
                image TEXT,
                ceneo_url VARCHAR(500)
            );
        """)

        print("Sprawdzanie czy istnieje admin...")
        cur.execute("SELECT * FROM users WHERE username = 'admin';")
        if not cur.fetchone():
            print("--- Tworzenie konta administratora ---")
            password = getpass.getpass("Wymyśl bezpieczne hasło dla admina: ")
            
            if not password:
                print("Nie podano hasła! Użytkownik nie został utworzony.")
            else:
                hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
                cur.execute("INSERT INTO users (username, password) VALUES (%s, %s);", ('admin', hashed_pw))
                print("Konto admina zostało bezpiecznie utworzone.")
        else:
            print("Admin już istnieje (nie zmieniam hasła).")

        conn.commit()
        cur.close()
        conn.close()
        print("Inicjalizacja bazy zakończona sukcesem! 🎉")
    except Exception as e:
        print(f"Błąd podczas inicjalizacji bazy: {e}")

if __name__ == "__main__":
    init_db()
