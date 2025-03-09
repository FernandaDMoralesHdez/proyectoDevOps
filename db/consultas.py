import sqlite3

DB_NAME = "db/temperaturas.db"

def ver_registros():
    """Muestra todos los registros de temperatura almacenados."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM registros ORDER BY id ASC")
        registros = cursor.fetchall()
        
        print("ID | Timestamp           | Temperature (°C)")
        print("-" * 40)
        for row in registros:
            print(f"{row[0]:<3} | {row[1]:<20} | {row[2]:<5}")

if __name__ == "__main__":
    ver_registros()
