import psycopg2
from app import DATABASE_CONFIG

def migrate_price_text():
    print("Łączenie z bazą danych...")
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cur = conn.cursor()

        print("Modyfikacja kolumny price w tabeli products...")
        
        # 1. Zmień typ na VARCHAR(100) (zachowując dane)
        print("   Zmiana typu na VARCHAR...")
        cur.execute("""
            ALTER TABLE products 
            ALTER COLUMN price TYPE VARCHAR(100);
        """)

        # 2. Usuń constraint NOT NULL
        print("   Usuwanie constraintu NOT NULL...")
        cur.execute("""
            ALTER TABLE products 
            ALTER COLUMN price DROP NOT NULL;
        """)

        conn.commit()
        cur.close()
        conn.close()
        print("Migracja price zakończona sukcesem! 🎉")
    except Exception as e:
        print(f"Błąd podczas migracji price: {e}")

if __name__ == "__main__":
    migrate_price_text()
