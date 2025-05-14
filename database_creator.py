import sqlite3

DB_NAME = "hotel.db"
SCHEMA_FILE = "hotel_schema.sql"

def create_database():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            with open(SCHEMA_FILE, 'r') as f:
                schema = f.read()
                cursor.executescript(schema)
            conn.commit()
        print(f"Database '{DB_NAME}' created successfully using '{SCHEMA_FILE}'.")
    except Exception as e:
        print("Error creating database:", e)

if __name__ == "__main__":
    create_database()
