import sys
import os
import sqlite3
from datetime import datetime, timedelta
from planificacion import PlanificacionActividad
from utils.fecha import validar_fecha
from prettytable import PrettyTable
from utils.prettytable import tabla

DATE_FMT = "%Y-%m-%d"
DB_PATH = "FormacionDB.db"   # <-- ruta BD


def coerce_float(x, field_name):
    try:
        v = float(x)
        if field_name == "remuneracion" and v < 0:
            raise ValueError("remuneración negativa")
        if field_name == "cuota" and v < 0:
            raise ValueError("cuota negativa")
        return v
    except Exception as e:
        raise ValueError(f"Campo '{field_name}' inválido ({e})")


# ---------- Selección de colegio desde la BD ----------
def _seleccionar_colegio():
    """Muestra los colegios existentes en la BD y devuelve el nombre elegido.
       Si falla la consulta, permite escribir el nombre manualmente."""
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT id_colegio, nombre FROM colegio ORDER BY nombre;")
        rows = cur.fetchall()
    except sqlite3.OperationalError as e:
        print(f"\nAviso: no se pudo leer la tabla 'colegio' ({e}).")
        colegio = input("Escriba el nombre del colegio: ").strip()
        return colegio
    finally:
        try:
            con.close()
        except Exception:
            pass

    if not rows:
        print("\nAviso: no hay colegios registrados en la base de datos.")
        colegio = input("Escriba el nombre del colegio: ").strip()
        return colegio

    # Mostrar lista y pedir selección
    print("\nColegios disponibles:")
    for idx, (_id, nombre) in enumerate(rows, start=1):
        print(f"  {idx}) {nombre}")

    while True:
        sel = input("Seleccione el número de colegio: ").strip()
        try:
            n = int(sel)
            if 1 <= n <= len(rows):
                return rows[n-1][1]   # devolvemos el nombre
            else:
                print("Número fuera de rango. Intente de nuevo.")
        except ValueError:
            print("Entrada no válida. Introduzca un número.")


# ---------- Selección de profesor desde la BD ----------
def _consultar_profesores(filtro=None):
    """
    Devuelve lista de (id_profesor, nombre, apellidos, email) filtrando
    por nombre+apellidos si se proporciona 'filtro'.
    """
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        base = """
            SELECT id_profesor, nombre, COALESCE(apellidos, ''), COALESCE(email, '')
            FROM profesor
        """
        params = []
        if filtro:
            base += " WHERE LOWER(nombre || ' ' || COALESCE(apellidos, '')) LIKE LOWER(?)"
            params.append(f"%{filtro.strip()}%")
        base += " ORDER BY apellidos, nombre, email;"
        cur.execute(base, params)
        rows = cur.fetchall()
        return rows
    except sqlite3.OperationalError as e:
        print(f"\nAviso: no se pudo leer la tabla 'profesor' ({e}).")
        return None
    finally:
        try:
            con.close()
        except Exception:
            pass


def _seleccionar_profesor():
    """
    Permite seleccionar un profesor de la BD con filtro por nombre/apellidos.
    Devuelve el email del profesor seleccionado.
    Si no se puede consultar la BD, cae a pedir el email manualmente.
    """
    while True:
        filtro = input(
            "Filtrar profesor por nombre/apellidos "
            "(mín. 2 letras, Enter = todos): "
        ).strip()

        if filtro and len(filtro) < 2:
            print("Error: introduzca al menos 2 caracteres para filtrar.")
            continue

        rows = _consultar_profesores(filtro if filtro else None)
        if rows is None:
            # Error al leer BD -> pedir email directamente y salir
            print("No se pudo consultar la lista de profesores.")
            return input("Introduzca el email del profesor: ").strip()

        if not rows:
            print("No se encontraron profesores con ese filtro.")
            continue

        print("\nProfesores disponibles:")
        for idx, (_id, nombre, apellidos, email) in enumerate(rows, start=1):
            nom_comp = f"{nombre} {apellidos}".strip()
            print(f"  {idx}) {nom_comp} <{email}>")

        sel = input("Seleccione el número de profesor: ").strip()
        try:
            n = int(sel)
            if 1 <= n <= len(rows):
                # devolvemos el email
                return rows[n-1][3]
            else:
                print("Número fuera de rango. Intente de nuevo.")
        except ValueError:
            print("Entrada no válida. Introduzca un número.")


def completar_inscripciones(reg):
    """Rellena apertura/cierre si faltan (apertura = inicio-21, cierre = inicio-3)."""
    fi = validar_fecha(reg["fecha_inicio"])
    if not fi:
        raise ValueError("fecha_inicio con formato inválido (YYYY-MM-DD)")
    if not reg.get("fecha_apertura"):
        reg["fecha_apertura"] = (fi - timedelta(days=21)).strftime(DATE_FMT)
    if not reg.get("fecha_cierre"):
        reg["fecha_cierre"] = (fi - timedelta(days=3)).strftime(DATE_FMT)
    return reg


def normalizar_gratuita_y_cuota(reg):
    """Si cuota==0 → gratuita=True; si >0 → gratuita=False."""
    cuota = coerce_float(reg.get("cuota", 0), "cuota")
    reg["cuota"] = cuota
    reg["gratuita"] = True if cuota == 0 else False
    return reg


def validar_registro_base(reg):
    """Valida presencia de campos obligatorios y coherencia de fechas."""
    obligatorios = [
        "colegio", "profesor_email", "nombre", "objetivos", "contenidos",
        "remuneracion", "fecha_inicio", "fecha_fin", "lugar"
    ]
    faltan = [k for k in obligatorios if not str(reg.get(k, "")).strip()]
    if faltan:
        raise ValueError(f"Faltan campos obligatorios: {', '.join(faltan)}")

    reg["remuneracion"] = coerce_float(reg["remuneracion"], "remuneracion")
    fi = validar_fecha(reg["fecha_inicio"])
    ff = validar_fecha(reg["fecha_fin"])
    if not fi or not ff:
        raise ValueError("Fechas inválidas (use YYYY-MM-DD)")
    if ff < fi:
        raise ValueError("fecha_fin anterior a fecha_inicio")
    return reg


def mostrar_resumen_lote(actividades):
    cab = [
        "#", "Colegio", "Profesor", "Nombre", "Inicio", "Fin",
        "Lugar", "Cuota", "Gratuita", "Remun.", "Plazas"
    ]
    con = []
    for i, a in enumerate(actividades, 1):
        con.append([
            i, a["colegio"], a["profesor_email"], a["nombre"],
            a["fecha_inicio"], a["fecha_fin"], a["lugar"],
            f"{a['cuota']:.2f}", "Sí" if a["gratuita"] else "No",
            f"{a['remuneracion']:.2f}", a["plazas"]
        ])
    print("\n Resumen de TODAS las actividades a registrar:\n")
    print(tabla(cab, con))


# ---------- Modo interactivo ----------
def capturar_actividad():
    print("\n=== Registro de una nueva actividad formativa ===")

    # Colegio desde la BD
    colegio = _seleccionar_colegio()

    # Profesor desde la BD con filtro
    profesor_email = _seleccionar_profesor()

    nombre = input("Nombre de la actividad: ").strip()
    objetivos = input("Objetivos de la actividad: ").strip()
    contenidos = input("Contenidos de la actividad: ").strip()

    # Remuneración
    try:
        remuneracion = coerce_float(
            input("Remuneración (€): ").strip(),
            "remuneracion"
        )
    except ValueError as e:
        print(f"Error: {e}")
        return None

        # Fechas
    fecha_inicio_txt = input("Fecha de inicio (YYYY-MM-DD): ").strip()
    fecha_fin_txt = input("Fecha de fin (YYYY-MM-DD): ").strip()
    fi = validar_fecha(fecha_inicio_txt)
    ff = validar_fecha(fecha_fin_txt)
    if not fi or not ff:
        print("Error: Fechas inválidas (YYYY-MM-DD).")
        return None
    if ff < fi:
        print("Error: La fecha de fin no puede ser anterior a la de inicio.")
        return None

    # Nueva validación: fecha de inicio no puede ser anterior a hoy
    hoy = datetime.now().date()
    if fi < hoy:
        print(f"Error: La fecha de inicio ({fi}) no puede ser anterior a la fecha actual ({hoy}).")
        return None


    # Plazas
    try:
        plazas = int(input("Plazas (entero > 0) [10]: ").strip() or "10")
        if plazas <= 0:
            print("Error: plazas debe ser > 0.")
            return None
    except ValueError:
        print("Error: plazas inválidas.")
        return None

    lugar = input("Lugar donde se celebrará: ").strip()

    # Fechas de inscripción automáticas
    fecha_apertura = (fi - timedelta(days=21)).strftime(DATE_FMT)
    fecha_cierre = (fi - timedelta(days=3)).strftime(DATE_FMT)

    # Cuota / gratuita
    try:
        cuota = coerce_float(
            input("Cuota de inscripción (0 si gratuita): ").strip() or "0",
            "cuota"
        )
        gratuita = True if cuota == 0 else False
    except ValueError as e:
        print(f"Error: {e}")
        return None

    # Resumen de esta actividad (individual)
    cab1 = ["Campo", "Valor"]
    con1 = [
        ["Colegio", colegio],
        ["Profesor", profesor_email],
        ["Plazas", plazas],
        ["Nombre", nombre],
        ["Objetivos", objetivos],
        ["Contenidos", contenidos],
        ["Remuneración (€)", f"{remuneracion:.2f}"],
        ["Inicio", fecha_inicio_txt],
        ["Fin", fecha_fin_txt],
        ["Lugar", lugar],
        ["Apertura inscripción", fecha_apertura],
        ["Cierre inscripción", fecha_cierre],
        ["Cuota (€)", f"{cuota:.2f}"],
        ["Gratuita", "Sí" if gratuita else "No"],
    ]
    print("\n Resumen de la actividad introducida:\n")
    print(tabla(cab1, con1))

    return {
        "colegio": colegio,
        "profesor_email": profesor_email,
        "plazas": plazas,
        "nombre": nombre,
        "objetivos": objetivos,
        "contenidos": contenidos,
        "remuneracion": remuneracion,
        "fecha_inicio": fecha_inicio_txt,
        "fecha_fin": fecha_fin_txt,
        "lugar": lugar,
        "fecha_apertura": fecha_apertura,
        "fecha_cierre": fecha_cierre,
        "gratuita": gratuita,
        "cuota": cuota,
    }


def agregar_actividades_interactivas():
    actividades = []
    while True:
        reg = capturar_actividad()
        if reg:
            actividades.append(reg)
        else:
            print(" Registro descartado por errores.")
        mas = input("\n¿Desea añadir otra actividad? (s/n): ").strip().lower()
        if mas != "s":
            break
    return actividades


# ---------- Entrypoint ----------
def main():
    # Solo modo interactivo (se elimina CSV/JSON)
    actividades = agregar_actividades_interactivas()
    if not actividades:
        print("\nNo hay actividades para registrar. Saliendo.")
        return

    mostrar_resumen_lote(actividades)
    confirmar = input(
        "\n¿Desea registrar estas actividades en la base de datos? (s/n): "
    ).strip().lower()
    if confirmar != "s":
        print(" Operación cancelada. No se insertó ninguna actividad.")
        return

    ok_rows, ko_rows = [], []
    for i, a in enumerate(actividades, 1):
        try:
            new_id = PlanificacionActividad.planificar_actividad(
                nombre=a["nombre"],
                objetivos=a["objetivos"],
                contenidos=a["contenidos"],
                profesor_email=a["profesor_email"],
                colegio_nombre=a["colegio"],
                remuneracion=a["remuneracion"],
                fecha_inicio=a["fecha_inicio"],
                fecha_fin=a["fecha_fin"],
                lugar=a["lugar"],
                fecha_apertura=a["fecha_apertura"],
                fecha_cierre=a["fecha_cierre"],
                gratuita=a["gratuita"],
                cuota=a["cuota"],
                plazas=a["plazas"],  # ahora se pasa también plazas
            )
            ok_rows.append([i, a["nombre"], a["colegio"], new_id])
        except Exception as e:
            ko_rows.append([i, a["nombre"], a["colegio"], str(e)])

    if ok_rows:
        print("\n Inserciones correctas:")
        print(tabla(["#", "Actividad", "Colegio", "ID nuevo"], ok_rows))
    if ko_rows:
        print("\n Inserciones con error:")
        print(tabla(["#", "Actividad", "Colegio", "Error"], ko_rows))

    if not ko_rows:
        print("\n Proceso completado sin errores.")
    elif ok_rows:
        print("\n Proceso completado con algunos errores (las válidas se insertaron).")
    else:
        print("\n No se pudo insertar ninguna actividad.")


if __name__ == "__main__":
    main()
