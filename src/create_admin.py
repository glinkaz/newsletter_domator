import psycopg2
from werkzeug.security import generate_password_hash
import sys
import os

DATABASE_CONFIG = {
    "host": "localhost",
    "database": "products",
    "user": "zuzannaglinka",
    "password": "password"
}

def create_initial_user(username, password):

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256') 

    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cur = conn.cursor()
        
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id;",
            (username, hashed_password)
        )
        conn.commit()
        user_id = cur.fetchone()[0]
        
        print(f"\n✅ Sukces: Użytkownik '{username}' utworzony z ID: {user_id}")
        print("   W bazie danych zapisany jest hash hasła, a nie jawne hasło.")

    except psycopg2.IntegrityError:
        print(f"\n❌ Błąd: Użytkownik o nazwie '{username}' już istnieje w bazie danych.")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"\n❌ Wystąpił błąd DB: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Użycie: python create_admin.py <username> <temporary_password>")
    else:
        username = sys.argv[1]
        password = sys.argv[2]
        create_initial_user(username, password)