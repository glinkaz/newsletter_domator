import psycopg2
import os
from app import DATABASE_CONFIG

def run_migrations():
    print("🚀 Rozpoczynam migrację bazy danych dla środowiska produkcyjnego...")
    
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cur = conn.cursor()

        # 1. Tworzenie tabeli product_images (jeśli nie istnieje)
        print("\n1. Sprawdzanie tabeli product_images...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS product_images (
                id SERIAL PRIMARY KEY,
                product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                image BYTEA NOT NULL
            );
        """)
        print("   ✅ Tabela product_images gotowa.")

        # 2. Dodawanie content_type do product_images
        print("\n2. Sprawdzanie kolumny content_type w product_images...")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='product_images' AND column_name='content_type';
        """)
        if not cur.fetchone():
            print("   ➕ Dodawanie kolumny content_type...")
            cur.execute("""
                ALTER TABLE product_images 
                ADD COLUMN content_type VARCHAR(50) DEFAULT 'image/jpeg';
            """)
        else:
            print("   ✅ Kolumna już istnieje.")

        # 3. Dodawanie content_type do products
        print("\n3. Sprawdzanie kolumny content_type w products...")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='products' AND column_name='content_type';
        """)
        if not cur.fetchone():
            print("   ➕ Dodawanie kolumny content_type...")
            cur.execute("""
                ALTER TABLE products 
                ADD COLUMN content_type VARCHAR(50) DEFAULT 'image/jpeg';
            """)
        else:
            print("   ✅ Kolumna już istnieje.")

        conn.commit()
        cur.close()
        conn.close()
        print("\n✨ Wszystkie migracje zakończone sukcesem! Baza jest gotowa.")
        
    except Exception as e:
        print(f"\n❌ Błąd krytyczny podczas migracji: {e}")

if __name__ == "__main__":
    run_migrations()
