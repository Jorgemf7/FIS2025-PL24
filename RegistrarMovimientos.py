# formacion/RegistrarMovimientos.py
import os
import csv
import sqlite3
from datetime import datetime
from utils.fecha import validar_fecha
from utils.prettytable import tabla

DB_PATH = "FormacionDB.db"
CARPETA_CARGA = "archivos_carga"
CATEGORIAS = {"alumno", "profesor", "otro"}
TIPOS = {"ingreso", "gasto"}

# ---------- utilidades de BD ----------
def _con():
    return sqlite3.connect(DB_PATH)

def _buscar_actividades_por_nombre(substr):
    q = """
    SELECT id_actividad, nombre, fecha_inicio, fecha_fin, remuneracion, cuota, gratuita
    FROM actividad
    WHERE LOWER(nombre) LIKE LOWER(?) 
    ORDER BY fecha_inicio, nombre
    """
    with _con() as con:
        cur = con.cursor()
        cur.execute(q, (f"%{substr.strip()}%",))
        return cur.fetchall()

def _get_actividad_por_id(id_actividad):
    q = "SELECT id_actividad, nombre, fecha_inicio, fecha_fin FROM actividad WHERE id_actividad=?"
    with _con() as con:
        cur = con.cursor()
        cur.execute(q, (id_actividad,))
        return cur.fetchone()

def _insertar_movimiento(id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado=1):
    q = """
    INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado)
    VALUES (?,?,?,?,?,?,?)
    """
    with _con() as con:
        cur = con.cursor()
        cur.execute(q, (id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado))
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

def _validar_fecha_en_actividad(fecha_txt, act):
    fi = validar_fecha(act[2])  # fecha_inicio
    ff = validar_fecha(act[3])  # fecha_fin
    f  = validar_fecha(fecha_txt)
    if not f:
        raise ValueError("fecha inválida (YYYY-MM-DD)")
    if f < fi or f > ff:
        raise ValueError(f"fecha fuera del periodo de la actividad ({fi.date()} a {ff.date()})")

def _existe_duplicado(id_actividad, tipo, fecha, importe, descripcion, categoria):
    q = """
    SELECT 1
    FROM movimiento
    WHERE id_actividad=? AND fecha=? AND tipo=? AND importe=? AND descripcion=? AND categoria=?
    LIMIT 1
    """
    with _con() as con:
        cur = con.cursor()
        cur.execute(q, (id_actividad, fecha, tipo, importe, descripcion, categoria))
        return cur.fetchone() is not None

def _validar_cantidades_esperadas(act, tipo, importe, categoria):
    """
    act: tupla de _buscar_actividades_por_nombre
         [0]=id, [1]=nombre, [2]=f_ini, [3]=f_fin, [4]=remuneracion, [5]=cuota, [6]=gratuita
    """
    try:
        remuneracion = float(act[4])
    except Exception:
        remuneracion = 0.0
    try:
        cuota = float(act[5] or 0)
    except Exception:
        cuota = 0.0
    try:
        gratuita = int(act[6])
    except Exception:
        gratuita = 0

    # actividad gratuita -> no ingresos de alumno
    if gratuita == 1 and categoria == "alumno" and tipo == "ingreso":
        raise ValueError("actividad gratuita: no se admiten ingresos de alumno")

    # ingresos alumno -> múltiplos de cuota (>0)
    if categoria == "alumno" and tipo == "ingreso" and cuota > 0:
        ratio = importe / cuota
        if abs(ratio - round(ratio)) > 1e-3:
            raise ValueError(f"importe no válido: debe ser múltiplo de la cuota ({cuota:.2f})")

    # gasto profesor -> debe ser -remuneracion (tolerancia 0.01)
    if categoria == "profesor" and tipo == "gasto":
        if abs((importe + remuneracion)) > 0.01:
            raise ValueError(f"gasto profesor esperado = -{remuneracion:.2f}")

# ---------- interacción ----------
def _seleccionar_actividad():
    while True:
        texto = input("Buscar actividad por nombre (mín. 2 letras): ").strip()
        if len(texto) < 2:
            print("Error: introduzca al menos 2 caracteres.")
            continue
        filas = _buscar_actividades_por_nombre(texto)
        if not filas:
            print("Error: no se encontraron actividades.")
            continue
        # listado
        cab = ["#", "ID", "Nombre", "Inicio", "Fin"]
        con = []
        for i, fila in enumerate(filas, 1):
            id_a, nombre, f_ini, f_fin = fila[:4]
            con.append([i, id_a, nombre, f_ini, f_fin])
        print("\nResultados:")
        print(tabla(cab, con))
        try:
            sel = int(input("Seleccione # de actividad: ").strip())
            if sel < 1 or sel > len(filas):
                print("Error: selección fuera de rango.")
                continue
            return filas[sel-1]
        except ValueError:
            print("Error: seleccione un número válido.")

def _alta_individual():
    print("\n=== Alta individual de movimiento ===")
    act = _seleccionar_actividad()
    id_actividad, nombre, f_ini, f_fin = act[:4]
    print(f"Actividad seleccionada: {nombre} ({f_ini} a {f_fin})")

    fecha = input("Fecha (YYYY-MM-DD): ").strip()
    _validar_fecha_en_actividad(fecha, act)

    importe = _coerce_importe(input("Importe (positivo => ingreso / negativo => gasto): "))
    if importe == 0:
        print("Error: el importe no puede ser 0.")
        return

    tipo = "ingreso" if importe > 0 else "gasto"
    # Validación de coherencia (mantiene la semántica centralizada)
    _validar_regla_signo(tipo, importe)

    descripcion = input("Descripción: ").strip()
    categoria = _validar_categoria(input("Categoría (alumno/profesor/otro) [otro]: ") or "otro")
    confirmado = 1  # si quieres pedirlo, cámbialo aquí

    # Validación contra cantidades esperadas de la actividad
    _validar_cantidades_esperadas(act, tipo, importe, categoria)

    # Duplicado
    if _existe_duplicado(id_actividad, tipo, fecha, importe, descripcion, categoria):
        print("Error: movimiento duplicado.")
        return

    # Resumen
    cabe = ["Campo","Valor"]
    cont = [
        ["Actividad", f"{nombre} (ID {id_actividad})"],
        ["Fecha", fecha],
        ["Importe", f"{importe:.2f}"],
        ["Tipo", tipo],
        ["Descripción", descripcion],
        ["Categoría", categoria],
        ["Confirmado", confirmado],
    ]
    print("\nResumen a registrar:")
    print(tabla(cabe, cont))
    if (input("¿Confirmar registro? (s/n): ").strip().lower() == "s"):
        try:
            new_id = _insertar_movimiento(id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado)
            print(f"Movimiento insertado con ID {new_id}.")
        except sqlite3.IntegrityError as e:
            print(f"Error: {e}")
    else:
        print("Operación cancelada.")

def _cargar_csv():
    print("\n=== Carga masiva CSV ===")
    print(f"Los archivos deben estar en la carpeta: {CARPETA_CARGA}")
    nombre = input("Nombre del archivo CSV (ej: movimientos.csv): ").strip()
    ruta = os.path.join(CARPETA_CARGA, nombre)
    if not os.path.isfile(ruta):
        print("Error: archivo no encontrado.")
        return

    ok, ko = [], []
    with open(ruta, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fila_n = 0
        for row in reader:
            fila_n += 1
            try:
                # Campos requeridos en CSV
                act_nombre = (row.get("actividad_nombre") or "").strip()
                if not act_nombre:
                    raise ValueError("actividad_nombre vacío")
                # busca 1 coincidencia exacta por nombre; si hay varias, pide ID de nuevo
                candidatos = _buscar_actividades_por_nombre(act_nombre)
                # filtra por coincidencia exacta de nombre si existen varias
                exactos = [r for r in candidatos if r[1].lower() == act_nombre.lower()]
                if not exactos:
                    raise ValueError(f"actividad '{act_nombre}' no encontrada")
                if len(exactos) > 1:
                    raise ValueError(f"actividad '{act_nombre}' ambigua (existen varias con ese nombre)")

                act = exactos[0]
                id_actividad = act[0]

                tipo = _validar_tipo(row.get("tipo",""))
                fecha = (row.get("fecha") or "").strip()
                _validar_fecha_en_actividad(fecha, act)
                importe = _coerce_importe(row.get("importe",""))
                _validar_regla_signo(tipo, importe)
                descripcion = (row.get("descripcion") or "").strip()
                categoria = _validar_categoria(row.get("categoria","otro"))
                _validar_cantidades_esperadas(act, tipo, importe, categoria)

                if _existe_duplicado(id_actividad, tipo, fecha, importe, descripcion, categoria):
                    raise ValueError("duplicado")

                new_id = _insertar_movimiento(id_actividad, tipo, fecha, importe, descripcion, categoria, 1)
                ok.append([fila_n, act_nombre, tipo, fecha, f"{importe:.2f}", descripcion, categoria, new_id])
            except Exception as e:
                ko.append([fila_n, (row.get('actividad_nombre') or ''), str(e)])

    if ok:
        print("\nInserciones correctas:")
        print(tabla(["#","Actividad","Tipo","Fecha","Importe","Descripción","Categoría","ID"], ok))
    if ko:
        print("\nInserciones con error:")
        print(tabla(["#","Actividad","Error"], ko))

def main():
    print("\n=== Registro de ingresos y gastos ===")
    while True:
        print("\nOpciones:")
        print("  1) Alta individual")
        print("  2) Carga masiva (CSV)")
        print("  3) Salir")
        try:
            op = int(input("Seleccione una opción: ").strip())
        except ValueError:
            print("Error: introduzca un número válido.")
            continue

        if op == 1:
            _alta_individual()
        elif op == 2:
            _cargar_csv()
        elif op == 3:
            break
        else:
            print("Error: opción inválida.")

if __name__ == "__main__":
    main()
