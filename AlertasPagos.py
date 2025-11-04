# GenerarAlertasPagos.py
import sqlite3
from utils.prettytable import tabla

DB_PATH = "FormacionDB.db"

def _con():
    return sqlite3.connect(DB_PATH)

def _upsert_alerta(cur, id_actividad, tipo, descripcion, id_movimiento=None, alumno_ref=None):
    """
    Inserta la alerta si no existe una igual (según ux_alerta_pago_unica).
    Devuelve True si creó alerta nueva, False si ya existía.
    """
    try:
        cur.execute("""
            INSERT INTO alerta_pago (id_actividad, id_movimiento, tipo_incidente, descripcion, alumno_ref, estado)
            VALUES (?,?,?,?,?, 'pendiente')
        """, (id_actividad, id_movimiento, tipo, descripcion, alumno_ref))
        return True
    except sqlite3.IntegrityError:
        return False

def detectar_importe_incorrecto(cur):
    """
    Ingresos de alumno cuyo importe no coincide con la cuota de la actividad (si no es gratuita).
    """
    cur.execute("""
        SELECT m.id_movimiento, m.id_actividad, a.nombre, a.cuota, m.importe
        FROM movimiento m
        JOIN actividad a ON a.id_actividad = m.id_actividad
        WHERE m.tipo='ingreso'
          AND m.categoria='alumno'
          AND a.gratuita=0
          AND CAST(ROUND(m.importe,2) AS TEXT) != CAST(ROUND(a.cuota,2) AS TEXT)
    """)
    nuevas = 0
    for id_mov, id_act, act_nombre, cuota, importe in cur.fetchall():
        desc = (f"Importe incorrecto en ingreso de alumno: importe={importe:.2f} "
                f"≠ cuota={cuota:.2f} (Actividad: {act_nombre}).")
        if _upsert_alerta(cur, id_act, "importe_incorrecto", desc, id_movimiento=id_mov):
            nuevas += 1
    return nuevas

def detectar_pendiente_fuera_plazo(cur):
    """
    Ingresos de alumno no confirmados, pasado el cierre de inscripción.
    """
    cur.execute("""
        SELECT m.id_movimiento, m.id_actividad, a.nombre, a.fecha_cierre_inscripcion, m.fecha, m.importe
        FROM movimiento m
        JOIN actividad a ON a.id_actividad = m.id_actividad
        WHERE m.tipo='ingreso'
          AND m.categoria='alumno'
          AND m.confirmado=0
          AND date('now','localtime') > date(a.fecha_cierre_inscripcion)
    """)
    nuevas = 0
    for id_mov, id_act, act_nombre, f_cierre, f_mov, importe in cur.fetchall():
        desc = (f"Ingreso de alumno pendiente de confirmación tras el cierre "
                f"(cierre={f_cierre}, mov={f_mov}, importe={importe:.2f}) en {act_nombre}.")
        if _upsert_alerta(cur, id_act, "pendiente_fuera_plazo", desc, id_movimiento=id_mov):
            nuevas += 1
    return nuevas

def detectar_duplicados(cur):
    """
    Claves con duplicidad: misma actividad, fecha, importe, descripcion, categoria.
    Genera UNA alerta por clave duplicada (no por cada fila duplicada).
    """
    cur.execute("""
        SELECT id_actividad, fecha, importe, IFNULL(descripcion,''), categoria, COUNT(*) AS n
        FROM movimiento
        WHERE tipo='ingreso' AND categoria='alumno'
        GROUP BY id_actividad, fecha, importe, IFNULL(descripcion,''), categoria
        HAVING n > 1
    """)
    nuevas = 0
    for id_act, fecha, importe, descripcion, categoria, n in cur.fetchall():
        # Busca una muestra para referenciar un id_movimiento (opcional)
        cur2 = cur.connection.cursor()
        cur2.execute("""
            SELECT id_movimiento FROM movimiento
            WHERE id_actividad=? AND fecha=? AND importe=? AND IFNULL(descripcion,'')=? AND categoria=?
            ORDER BY id_movimiento LIMIT 1
        """, (id_act, fecha, importe, descripcion, categoria))
        row = cur2.fetchone()
        id_mov = row[0] if row else None

        desc = (f"Pagos duplicados de alumno ({n} repeticiones) "
                f"en fecha={fecha}, importe={importe:.2f}, desc='{descripcion}'.")
        if _upsert_alerta(cur, id_act, "duplicado", desc, id_movimiento=id_mov):
            nuevas += 1
    return nuevas

def listar_alertas(cur, estados=("pendiente","en_revision")):
    cur.execute(f"""
        SELECT a.id_alerta, ac.nombre, a.tipo_incidente, a.descripcion, a.estado, a.fecha_generacion
        FROM alerta_pago a
        JOIN actividad ac ON ac.id_actividad = a.id_actividad
        WHERE a.estado IN ({",".join(["?"]*len(estados))})
        ORDER BY a.fecha_generacion DESC, a.id_alerta DESC
    """, estados)
    rows = cur.fetchall()
    if not rows:
        print("\nNo hay alertas en los estados seleccionados.")
        return
    cabe = ["ID", "Actividad", "Incidente", "Descripción", "Estado", "Fecha"]
    print("\nAlertas:")
    print(tabla(cabe, rows))

def generar_alertas():
    con = _con()
    try:
        cur = con.cursor()
        total = 0
        total += detectar_importe_incorrecto(cur)
        total += detectar_pendiente_fuera_plazo(cur)
        total += detectar_duplicados(cur)
        con.commit()
        print(f"\nGeneración de alertas completada. Alertas nuevas: {total}")
        listar_alertas(cur, estados=("pendiente","en_revision","resuelta"))  # muestra todas para revisión
    finally:
        con.close()

def actualizar_estado(id_alerta, nuevo_estado):
    if nuevo_estado not in ("pendiente","en_revision","resuelta"):
        print("Error: estado inválido. Use: pendiente | en_revision | resuelta")
        return
    con = _con()
    try:
        cur = con.cursor()
        cur.execute("UPDATE alerta_pago SET estado=? WHERE id_alerta=?", (nuevo_estado, id_alerta))
        if cur.rowcount == 0:
            print(f"No existe la alerta {id_alerta}.")
        else:
            con.commit()
            print(f"Alerta {id_alerta} actualizada a {nuevo_estado}.")
    finally:
        con.close()

def main():
    print("\n=== Generador de alertas de pagos (alumnos) ===")
    print("1) Generar/actualizar alertas ahora")
    print("2) Listar alertas (pendiente + en_revision)")
    print("3) Cambiar estado de una alerta")
    print("4) Salir")
    try:
        op = int(input("Opción: ").strip())
    except ValueError:
        print("Error: opción inválida")
        return

    if op == 1:
        generar_alertas()
    elif op == 2:
        con = _con()
        try:
            cur = con.cursor()
            listar_alertas(cur, estados=("pendiente","en_revision"))
        finally:
            con.close()
    elif op == 3:
        try:
            ida = int(input("ID de alerta: ").strip())
            est = input("Nuevo estado (pendiente/en_revision/resuelta): ").strip()
            actualizar_estado(ida, est)
        except ValueError:
            print("Error: ID inválido")
    else:
        print("OK")

if __name__ == "__main__":
    main()
