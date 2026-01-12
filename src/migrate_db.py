import os
import psycopg2
from app import DATABASE_CONFIG

def migrate_db():
    print("Łączenie z bazą danych...")
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cur = conn.cursor()

        print("Tworzenie tabeli product_images...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS product_images (
                id SERIAL PRIMARY KEY,
                product_id INT REFERENCES products(id) ON DELETE CASCADE,
                image BYTEA
            );
        """)

        conn.commit()
        cur.close()
        conn.close()
        print("Migracja zakończona sukcesem! Tabela product_images została utworzona.")
    except Exception as e:
        print(f"Błąd podczas migracji: {e}")

if __name__ == "__main__":
    migrate_db()
