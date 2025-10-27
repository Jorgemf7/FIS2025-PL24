from datetime import datetime
from carga_inicial import setup_formacion_db
import AñadirActividad
import RegistrarMovimientos       # <-- NUEVO: registro de ingresos/gastos
import ConsultarBalance           # <-- EXISTENTE: consultas
from utils import prettytable


def main():

    print("=== SISTEMA DE GESTIÓN DE FORMACIÓN ===\n")

    # --- Carga inicial de la base de datos ---
    db_name = 'FormacionDB.db'
    schema_sql = 'cargainicial/schema.sql'
    data_sql = 'cargainicial/data.sql'

    acciones_principales = [
        "Quiero realizar una inserción\n",
        "Quiero cargar los datos iniciales\n",
        "Quiero realizar consultas\n",
        "Quiero cerrar la aplicación\n"
    ]

    print("¿Qué acción deseas hacer?\n")
    for i, accion in enumerate(acciones_principales, 1):
        print(f"{i}. {accion}")

    numero = int(input("Introduce la acción deseada: "))

    while numero != len(acciones_principales):

        # --- INSERCIONES ---
        if numero == 1:
            acciones_insercion = [
                "Registrar una nueva actividad formativa (interactiva o desde CSV/JSON)\n",
                "Registrar ingresos/gastos (individual o CSV)\n",  # <-- NUEVA OPCIÓN
                "Volver atrás\n"
            ]

            print("¿Qué inserción deseas realizar?")
            for i, accion in enumerate(acciones_insercion, 1):
                print(f"{i}. {accion}")

            n2 = int(input("Introduce la acción deseada: "))

            if n2 == 1:
                AñadirActividad.main()
            elif n2 == 2:
                RegistrarMovimientos.main()   # <-- NUEVA FUNCIÓN AQUÍ
            elif n2 == 3:
                return main()
            else:
                print("Esa opción no existe.")
                break

        # --- CARGA INICIAL ---
        elif numero == 2:
            print("\nCargando la base de datos inicial...")
            setup_formacion_db.crear_db(db_name, schema_sql, data_sql)
            print("Base de datos creada o actualizada correctamente.")

        # --- CONSULTAS ---
        elif numero == 3:
            acciones_consultas = [
                "Consultar balance económico por actividad (ingresos/gastos, confirmados/estimados)\n",
                "Volver atrás\n"
            ]

            print("\n¿Qué consulta deseas realizar?")
            for i, accion in enumerate(acciones_consultas, 1):
                print(f"{i}. {accion}")

            n3 = int(input("Introduce la acción deseada: "))

            if n3 == 1:
                ConsultarBalance.main()
            elif n3 == 2:
                return main()
            else:
                print("Esa opción no existe.")
                break

        # --- SALIDA ---
        elif numero == 4:
            print("¡Hasta la próxima!")
            break

        else:
            print("Ese número no se encuentra entre las opciones actualmente.")
            break

        respuesta = input("\n¿Deseas hacer otra acción? (S/n): ").lower()
        if respuesta == "s":
            return main()
        else:
            print("¡Hasta la próxima!")
            break


if __name__ == "__main__":
    main()
