import os
import psycopg2

DATABASE_CONFIG = {
    # "host": os.environ.get("DB_HOST", "host.docker.internal"),
    "host": os.environ.get("DB_HOST", "0.0.0.0"),
    "database": os.environ.get("DB_NAME", "products"),
    "user": os.environ.get("DB_USER", "zuzannaglinka"),
    "password": os.environ.get("DB_PASSWORD", "password")
}

def migrate():
    print("Connecting to database...")
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cur = conn.cursor()

        print("Adding 'visible' column...")
        cur.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS visible BOOLEAN DEFAULT TRUE;")
        
        print("Adding 'ceneo_last_price' column...")
        cur.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS ceneo_last_price NUMERIC(10, 2);")

        print("Adding 'ceneo_check_date' column...")
        cur.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS ceneo_check_date DATE;")

        conn.commit()
        cur.close()
        conn.close()
        print("Migration completed successfully! 🎉")
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate()
