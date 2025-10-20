
import sqlite3, os

HERE = os.path.dirname(__file__)

def ejecutar_script_sql(conn, path):
    with open(path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

def crear_db(dest_db="FormacionDB.db"):
    conn = sqlite3.connect(dest_db)
    try:
        ejecutar_script_sql(conn, os.path.join(HERE, "esquema_formacion.sql"))
        ejecutar_script_sql(conn, os.path.join(HERE, "datos_iniciales.sql"))
        conn.commit()
        print(f"OK: {dest_db} creada y poblada.")
    finally:
        conn.close()

if __name__ == "__main__":
    crear_db()
