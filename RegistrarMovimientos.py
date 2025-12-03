# formacion/RegistrarMovimientos.py
import os
import sqlite3
from datetime import datetime, timedelta
from utils.fecha import validar_fecha
from utils.prettytable import tabla
import math

DB_PATH = "FormacionDB.db"
CATEGORIAS = {"alumno", "profesor", "otro"}
TIPOS = {"ingreso", "gasto"}

# ---------- utilidades de BD ----------
def _con():
    return sqlite3.connect(DB_PATH)


def _buscar_actividades_por_nombre(substr):
    q = """
    SELECT
        id_actividad,
        nombre,
        fecha_inicio,
        fecha_fin,
        remuneracion,
        cuota,
        gratuita,
        fecha_apertura_inscripcion,
        fecha_cierre_inscripcion
    FROM actividad
    WHERE LOWER(nombre) LIKE LOWER(?)
    ORDER BY fecha_inicio, nombre
    """
    with _con() as con:
        cur = con.cursor()
        cur.execute(q, (f"%{substr.strip()}%",))
        return cur.fetchall()

def _get_actividad_por_id(id_actividad):
    q = """
    SELECT
        id_actividad,
        nombre,
        fecha_inicio,
        fecha_fin,
        remuneracion,
        cuota,
        gratuita,
        fecha_apertura_inscripcion,
        fecha_cierre_inscripcion
    FROM actividad
    WHERE id_actividad=?
    """
    with _con() as con:
        cur = con.cursor()
        cur.execute(q, (id_actividad,))
        return cur.fetchone()

# obtener profesor de la actividad
def _get_profesor_de_actividad(id_actividad):
    q = "SELECT id_profesor FROM actividad WHERE id_actividad=?"
    with _con() as con:
        cur = con.cursor()
        cur.execute(q, (id_actividad,))
        row = cur.fetchone()
        return row[0] if row else None

# listar alumnos inscritos en una actividad
def _listar_alumnos_de_actividad(id_actividad):
    q = """
    SELECT al.id_alumno, al.nombre, al.apellidos, al.email
    FROM inscripcion i
    JOIN alumno al ON al.id_alumno = i.id_alumno
    WHERE i.id_actividad = ?
    ORDER BY al.nombre, al.apellidos
    """
    with _con() as con:
        cur = con.cursor()
        cur.execute(q, (id_actividad,))
        return cur.fetchall()

# seleccionar alumno para una actividad
def _seleccionar_alumno_para_actividad(act):
    """
    act = fila de actividad (id, nombre, f_ini, f_fin, ...)
    Devuelve id_alumno o lanza ValueError si no hay selección posible.
    """
    id_actividad = act[0]
    alumnos = _listar_alumnos_de_actividad(id_actividad)
    if not alumnos:
        raise ValueError("no hay alumnos inscritos en esta actividad")

    print("\nAlumnos inscritos en la actividad:")
    for i, (id_al, nombre, apellidos, email) in enumerate(alumnos, 1):
        nom_completo = (nombre or "") + (" " + apellidos if apellidos else "")
        print(f"  {i}) {nom_completo.strip()} [{email}]")

    while True:
        sel = input("Seleccione nº de alumno: ").strip()
        if not sel.isdigit():
            print("Introduzca un número válido.")
            continue
        n = int(sel)
        if 1 <= n <= len(alumnos):
            return alumnos[n-1][0]
        print("Número fuera de rango.")


def _insertar_movimiento(id_actividad, tipo, fecha, importe, descripcion, categoria,
                         confirmado=1, id_alumno=None, id_profesor=None):
    q = """
    INSERT INTO movimiento
        (id_actividad, tipo, fecha, importe, descripcion, categoria,
         confirmado, id_alumno, id_profesor)
    VALUES (?,?,?,?,?,?,?,?,?)
    """
    with _con() as con:
        cur = con.cursor()
        cur.execute(q, (
            id_actividad, tipo, fecha, importe, descripcion, categoria,
            confirmado, id_alumno, id_profesor
        ))
        return cur.lastrowid

# ---------- validaciones ----------
def _coerce_importe(s):
    try:
        return float(str(s).replace(",", "."))
    except Exception:
        raise ValueError("importe no numérico")

def _validar_regla_signo(tipo, importe):
    if tipo == "ingreso" and not (importe > 0):
        raise ValueError("los ingresos deben ser positivos")
    if tipo == "gasto" and not (importe < 0):
        raise ValueError("los gastos deben ser negativos")

def _validar_categoria(cat):
    c = str(cat).strip().lower() or "otro"
    if c not in CATEGORIAS:
        raise ValueError("categoría inválida (use alumno|profesor|otro)")
    return c

def _validar_tipo(t):
    v = str(t).strip().lower()
    if v not in TIPOS:
        raise ValueError("tipo inválido (use ingreso|gasto)")
    return v

def _validar_fecha_en_actividad(fecha_txt, act, tipo):
    f_ini = validar_fecha(act[2])
    f_fin = validar_fecha(act[3])
    f_ap  = validar_fecha(act[7])
    f_ci  = validar_fecha(act[8])
    f     = validar_fecha(fecha_txt)

    if not f:
        raise ValueError("fecha con formato inválido (YYYY-MM-DD)")

    

    if tipo == "ingreso":
        # INGRESOS: apertura → fin + 2 días
        limite_sup = f_fin + timedelta(days=2)
        if f < f_ap or f > limite_sup:
            raise ValueError(
                "ingreso fuera de [apertura_inscripción .. fin_acción + 2 días]"
            )
    else:
        # GASTOS: solo que no sean antes de apertura
        if f < f_ap:
            raise ValueError("gasto anterior a la apertura de inscripción")


# ---------- interacción ----------
def _listar_todas_actividades():
    q = """
    SELECT
        id_actividad,
        nombre,
        fecha_inicio,
        fecha_fin,
        remuneracion,
        cuota,
        gratuita,
        fecha_apertura_inscripcion,
        fecha_cierre_inscripcion
    FROM actividad
    ORDER BY fecha_inicio, nombre
    """
    with _con() as con:
        cur = con.cursor()
        cur.execute(q)
        return cur.fetchall()


def _seleccionar_actividad():
    """
    Muestra todas las actividades y permite:
      - introducir un NÚMERO para seleccionar la actividad de la lista actual
      - introducir TEXTO (>=2 letras) para filtrar por nombre
      - pulsar ENTER para volver a ver TODAS
    """
    base = _listar_todas_actividades()
    if not base:
        print("No hay actividades registradas en la base de datos.")
        return None

    filtradas = base[:]

    while True:
        # Añadimos las fechas de inscripción en el listado
        cab = ["#", "ID", "Nombre", "Inicio", "Fin",
               "Apertura insc.", "Cierre insc."]

        con = []
        for i, fila in enumerate(filtradas, 1):
            (
                id_a,
                nombre,
                f_ini,
                f_fin,
                remuneracion,
                cuota,
                gratuita,
                f_ap,
                f_ci,
            ) = fila
            con.append([i, id_a, nombre, f_ini, f_fin, f_ap, f_ci])

        print("\nActividades disponibles:")
        print(tabla(cab, con))

        print("\nIntroduce:")
        print("  - un NÚMERO para seleccionar esa actividad")
        print("  - un TEXTO (≥2 letras) para filtrar por nombre")
        print("  - ENTER vacío para ver TODAS de nuevo")

        entrada = input("Selección / filtro: ").strip()

        if entrada == "":
            filtradas = base[:]
            continue

        if entrada.isdigit():
            n = int(entrada)
            if 1 <= n <= len(filtradas):
                return filtradas[n-1]
            else:
                print("Error: número fuera de rango.")
                continue

        if len(entrada) < 2:
            print("Error: introduzca al menos 2 caracteres para filtrar.")
            continue

        needle = entrada.lower()
        nuevas = [fila for fila in base if needle in fila[1].lower()]
        if not nuevas:
            print("No se encontraron actividades que coincidan con ese texto.")
            continue

        filtradas = nuevas



def _alta_individual():
    print("\n=== Alta individual de movimiento ===")
    act = _seleccionar_actividad()
    if act is None:
        return
    id_actividad, nombre, f_ini, f_fin = act[:4]
    print(f"Actividad seleccionada: {nombre} ({f_ini} a {f_fin})")

    # 1) Tipo primero (ingreso / gasto)
    tipo = _validar_tipo(input("Tipo (ingreso/gasto): ").strip())

    # 2) Fecha, validada inmediatamente según el tipo y la actividad
    while True:
        fecha = input("Fecha (YYYY-MM-DD) [ENTER para cancelar]: ").strip()
        if fecha == "":
            print("Operación cancelada.")
            return
        try:
            _validar_fecha_en_actividad(fecha, act, tipo)
            break
        except ValueError as e:
            print(f"Error en la fecha: {e}")

    # 3) Importe sin signo
    try:
        importe_base = _coerce_importe(input("Importe (valor absoluto, p.ej. 100): "))
    except ValueError as e:
        print(f"Error: {e}")
        return

    if importe_base == 0:
        print("Error: el importe no puede ser 0.")
        return

    # Convertimos a signo correcto según tipo
    importe = importe_base if tipo == "ingreso" else -importe_base
    try:
        _validar_regla_signo(tipo, importe)
    except ValueError as e:
        print(f"Error: {e}")
        return

    descripcion = input("Descripción: ").strip()
    categoria = _validar_categoria(input("Categoría (alumno/profesor/otro) [otro]: ") or "otro")
    confirmado = 1

    id_alumno = None
    id_profesor = None
    try:
        if categoria == "alumno":
            id_alumno = _seleccionar_alumno_para_actividad(act)
        elif categoria == "profesor":
            id_profesor = _get_profesor_de_actividad(id_actividad)
            if id_profesor is None:
                raise ValueError("la actividad no tiene profesor asociado en la BD")
    except ValueError as e:
        print(f"Error al asociar movimiento: {e}")
        return

    cabe = ["Campo","Valor"]
    cont = [
        ["Actividad", f"{nombre} (ID {id_actividad})"],
        ["Fecha", fecha],
        ["Importe (con signo)", f"{importe:.2f}"],
        ["Tipo", tipo],
        ["Descripción", descripcion],
        ["Categoría", categoria],
        ["ID alumno", id_alumno if id_alumno is not None else "-"],
        ["ID profesor", id_profesor if id_profesor is not None else "-"],
        ["Confirmado", confirmado],
    ]
    print("\nResumen a registrar:")
    print(tabla(cabe, cont))
    if (input("¿Confirmar registro? (s/n): ").strip().lower() == "s"):
        try:
            new_id = _insertar_movimiento(
                id_actividad, tipo, fecha, importe, descripcion, categoria,
                confirmado, id_alumno, id_profesor
            )
            print(f"Movimiento insertado con ID {new_id}.")
        except sqlite3.IntegrityError as e:
            print(f"Error: {e}")
    else:
        print("Operación cancelada.")


def main():
    print("\n=== Registro de ingresos y gastos ===")
    while True:
        print("\nOpciones:")
        print("  1) Alta individual")
        print("  2) Salir")
        try:
            op = int(input("Seleccione una opción: ").strip())
        except ValueError:
            print("Error: introduzca un número válido.")
            continue

        if op == 1:
            _alta_individual()
        elif op == 2:
            break
        else:
            print("Error: opción inválida.")

if __name__ == "__main__":
    main()
