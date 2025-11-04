from datetime import datetime
from carga_inicial import setup_formacion_db
import AñadirActividad
import RegistrarMovimientos       # <-- NUEVO: registro de ingresos/gastos
import ConsultarBalance           # <-- EXISTENTE: consultas
from utils import prettytable

import sqlite3, os

DB_NAME = "FormacionDB.db"
RUTA_SQL_REVISION = "carga_inicial/revision_2025_11.sql"     # SQL combinado (reset + datos revisión)
RUTA_SQL_ESQUEMA  = "carga_inicial/esquema_formacion.sql"    # Solo esquema (BD vacía)
RUTA_SQL_BASE_CSV = "carga_inicial/bd_base_para_csv_revision.sql"

def _ejecutar_sql(path_sql, db_path=DB_NAME):
    if not os.path.isfile(path_sql):
        print(f"Error: no se encontró {path_sql}")
        return
    con = sqlite3.connect(db_path)
    try:
        with open(path_sql, "r", encoding="utf-8") as f:
            con.executescript(f.read())
        con.commit()
        print(f"OK: BD preparada con {path_sql}")
    finally:
        con.close()


def _submenu_cargar_bd():
    opciones = [
        "Cargar datos INICIALES (setup_formacion_db)\n",
        "Cargar datos de la REVISIÓN (reset + seed)\n",
        "Preparar BD para cargar CSV de la revisión (esquema + colegios/profesores)\n",  # << CAMBIO
        "Volver atrás\n"
    ]


def _submenu_cargar_bd():
    opciones = [
        "Cargar datos INICIALES (setup_formacion_db)\n",
        "Cargar datos de la REVISIÓN (reset + seed)\n",
        "Crear BD VACÍA (solo esquema)\n",
        "Volver atrás\n"
    ]
    print("\n=== CARGA DE BASES DE DATOS ===\n")
    for i, op in enumerate(opciones, 1):
        print(f"{i}. {op}")
    try:
        n = int(input("Introduce la acción deseada: "))
    except ValueError:
        print("Opción inválida.")
        return

    if n == 1:
        print("\nCargando la base de datos inicial (puede crearla si no existe)...")
        setup_formacion_db.crear_db(DB_NAME)
        print("Base de datos creada o actualizada correctamente.")
    elif n == 2:
        print("\nEsto reseteará las tablas y cargará SOLO los datos de la revisión.")
        conf = input("¿Confirmas? (escribe 'CONFIRMAR'): ").strip()
        if conf == "CONFIRMAR":
            _ejecutar_sql(RUTA_SQL_REVISION, DB_NAME)
        else:
            print("Cancelado.")
    elif n == 3:
        print("\nEsto creará el esquema y añadirá los colegios/profesores necesarios para tus CSV.")
        conf = input("¿Confirmas? (escribe 'CONFIRMAR'): ").strip()
        if conf == "CONFIRMAR":
            _ejecutar_sql(RUTA_SQL_BASE_CSV, DB_NAME)
        else:
            print("Cancelado.")

    elif n == 4:
        return
    else:
        print("Esa opción no existe.")

def main():
    print("=== SISTEMA DE GESTIÓN DE FORMACIÓN ===\n")

    acciones_principales = [
        "Quiero realizar una inserción\n",
        "Cargar base de datos (inicial / revisión / vacía)\n",  
        "Quiero realizar consultas\n",
        "Quiero cerrar la aplicación\n"
    ]

    while True:
        print("\n¿Qué acción deseas hacer?\n")
        for i, accion in enumerate(acciones_principales, 1):
            print(f"{i}. {accion}")

        try:
            numero = int(input("Introduce la acción deseada: "))
        except ValueError:
            print("Opción inválida.")
            continue

        # --- INSERCIONES ---
        if numero == 1:
            acciones_insercion = [
                "Registrar una nueva actividad formativa (interactiva o desde CSV/JSON)\n",
                "Registrar ingresos/gastos (individual o CSV)\n",
                "Volver atrás\n"
            ]

            print("\n=== INSERCIONES ===")
            for i, accion in enumerate(acciones_insercion, 1):
                print(f"{i}. {accion}")

            try:
                n2 = int(input("Introduce la acción deseada: "))
            except ValueError:
                print("Opción inválida.")
                continue

            if n2 == 1:
                AñadirActividad.main()
            elif n2 == 2:
                RegistrarMovimientos.main()
            elif n2 == 3:
                continue
            else:
                print("Esa opción no existe.")

        # --- CARGA DE BD ---
        elif numero == 2:
            _submenu_cargar_bd()

        # --- CONSULTAS ---
        elif numero == 3:
            acciones_consultas = [
                "Consultar balance económico por actividad (ingresos/gastos, confirmados/estimados)\n",
                "Volver atrás\n"
            ]

            print("\n=== CONSULTAS ===")
            for i, accion in enumerate(acciones_consultas, 1):
                print(f"{i}. {accion}")

            try:
                n3 = int(input("Introduce la acción deseada: "))
            except ValueError:
                print("Opción inválida.")
                continue

            if n3 == 1:
                ConsultarBalance.main()
            elif n3 == 2:
                continue
            else:
                print("Esa opción no existe.")

        # --- SALIDA ---
        elif numero == 4:
            print("¡Hasta la próxima!")
            break

        else:
            print("Ese número no se encuentra entre las opciones actualmente.")

        # ¿Otra acción?
        respuesta = input("\n¿Deseas hacer otra acción? (S/n): ").strip().lower()
        if respuesta != "s" and respuesta != "":
            print("¡Hasta la próxima!")
            break

if __name__ == "__main__":
    main()
