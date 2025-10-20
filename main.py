from datetime import datetime
from carga_inicial import setup_formacion_db
import AñadirActividad
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
        "Quiero cerrar la aplicación\n"
    ]

    print("¿Qué acción deseas hacer?\n")
    for i, accion in enumerate(acciones_principales, 1):
        print(f"{i}. {accion}")

    numero = int(input("Introduce la acción deseada: "))

    while numero != len(acciones_principales):

        if numero == 1:
            acciones_insercion = [
                "Registrar una nueva actividad formativa (interactiva o desde CSV/JSON)\n",
                "Volver atrás\n"
            ]

            print("¿Qué inserción deseas realizar?")
            for i, accion in enumerate(acciones_insercion, 1):
                print(f"{i}. {accion}")

            n2 = int(input("Introduce la acción deseada: "))

            if n2 == 1:
                # Llama directamente al script AñadirActividad
                AñadirActividad.main()
            elif n2 == 2:
                return main()
            else:
                print("Esa opción no existe.")
                break

        elif numero == 2:
            print("\nCargando la base de datos inicial...")
            setup_formacion_db.crear_db(db_name, schema_sql, data_sql)
            print("✅ Base de datos creada o actualizada correctamente.")

        elif numero == 3:
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
