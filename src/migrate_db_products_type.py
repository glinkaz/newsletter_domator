import os
import psycopg2
from app import DATABASE_CONFIG

def migrate_db_products_type():
    print("Łączenie z bazą danych...")
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cur = conn.cursor()

        print("Sprawdzanie i dodawanie kolumny content_type do tabeli products...")
        
        # Sprawdź czy kolumna istnieje
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='products' AND column_name='content_type';
        """)
        
        if not cur.fetchone():
            print("Dodawanie kolumny content_type...")
            cur.execute("""
                ALTER TABLE products 
                ADD COLUMN content_type VARCHAR(50) DEFAULT 'image/jpeg';
            """)
            print("Kolumna dodana!")
        else:
            print("Kolumna content_type już istnieje.")

        conn.commit()
        cur.close()
        conn.close()
        print("Migracja products zakończona sukcesem!")
    except Exception as e:
        print(f"Błąd podczas migracji products: {e}")

if __name__ == "__main__":
    migrate_db_products_type()
