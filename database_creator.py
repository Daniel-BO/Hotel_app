import sqlite3
import bcrypt
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
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        if cursor.fetchone()[0] == 0:
          contrasenainitadmin = "admin123"    
          hashed = bcrypt.hashpw(contrasenainitadmin.encode('utf-8'), bcrypt.gensalt())
          cursor.execute("INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?,?,?)",("admin", hashed, "admin"))
        conn.commit()
    except Exception as e:
        print("Error creating database:", e)

if __name__ == "__main__":
    create_database()
