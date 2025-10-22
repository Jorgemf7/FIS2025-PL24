import sqlite3
from datetime import date
from utils.fecha import validar_fecha
from utils.prettytable import tabla

DB_PATH = "FormacionDB.db"
ESTADOS = ["todos", "planificado", "inscripcion_abierta", "en_curso", "cerrado"]

SQL = """
WITH base AS (
  SELECT
    a.id_actividad,
    a.nombre,
    a.fecha_inicio,
    a.fecha_fin,
    a.fecha_apertura_inscripcion,
    a.fecha_cierre_inscripcion,
    CASE
      WHEN date('now','localtime') <  date(a.fecha_apertura_inscripcion) THEN 'planificado'
      WHEN date('now','localtime') BETWEEN date(a.fecha_apertura_inscripcion) AND date(a.fecha_cierre_inscripcion) THEN 'inscripcion_abierta'
      WHEN date('now','localtime') BETWEEN date(a.fecha_inicio) AND date(a.fecha_fin) THEN 'en_curso'
      WHEN date('now','localtime') >  date(a.fecha_fin) THEN 'cerrado'
      ELSE 'desconocido'
    END AS estado_calc
  FROM actividad a
)
SELECT
  b.id_actividad, b.nombre, b.fecha_inicio, b.fecha_fin, b.estado_calc,
  IFNULL(SUM(CASE WHEN m.tipo='ingreso' AND m.confirmado=1 THEN m.importe END),0) AS ingresos_confirmados,
  IFNULL(SUM(CASE WHEN m.tipo='gasto'   AND m.confirmado=1 THEN m.importe END),0) AS gastos_confirmados,
  IFNULL(SUM(CASE WHEN m.tipo='ingreso' AND m.confirmado=0 THEN m.importe END),0) AS ingresos_estimados,
  IFNULL(SUM(CASE WHEN m.tipo='gasto'   AND m.confirmado=0 THEN m.importe END),0) AS gastos_estimados
FROM base b
LEFT JOIN movimiento m ON m.id_actividad = b.id_actividad
WHERE date(b.fecha_inicio) BETWEEN ? AND ?
  AND (? = 'todos' OR b.estado_calc = ?)
GROUP BY b.id_actividad, b.nombre, b.fecha_inicio, b.fecha_fin, b.estado_calc
ORDER BY date(b.fecha_inicio), b.nombre;
"""

def _pedir_rango_por_defecto():
    """Pide fechas de inicio/fin con defecto al año en curso y valida."""
    hoy = date.today()
    inicio_def = f"{hoy.year}-01-01"
    fin_def    = f"{hoy.year}-12-31"
    fi_txt = input(f"Fecha inicio [YYYY-MM-DD] (por defecto {inicio_def}): ").strip() or inicio_def
    ff_txt = input(f"Fecha fin    [YYYY-MM-DD] (por defecto {fin_def}): ").strip() or fin_def
    fi = validar_fecha(fi_txt); ff = validar_fecha(ff_txt)
    if not fi or not ff or ff < fi:
        print("Error: Rango de fechas inválido. Inténtalo de nuevo.\n")
        return _pedir_rango_por_defecto()
    return fi_txt, ff_txt

def _pedir_estado():
    """Pide estado a filtrar con defecto 'todos'."""
    print("\nEstados disponibles:", ", ".join(ESTADOS))
    estado = input("Estado a filtrar (por defecto 'todos'): ").strip().lower() or "todos"
    if estado not in ESTADOS:
        print("Error: Estado no válido. Usando 'todos'.")
        estado = "todos"
    return estado

def _consultar(fi_txt, ff_txt, estado):
    """Ejecuta la consulta de agregados. Maneja la ausencia de tabla movimiento con LEFT JOIN."""
    con = sqlite3.connect(DB_PATH)
    try:
        cur = con.cursor()
        cur.execute(SQL, (fi_txt, ff_txt, estado, estado))
        return cur.fetchall()
    except sqlite3.OperationalError as e:
        # Si no existe la tabla movimiento, muestra confirmados/estimados como 0.
        msg = str(e).lower()
        if "no such table: movimiento" in msg:
            print("\nError: la tabla 'movimiento' no existe. Se mostrarán actividades sin totales económicos.")
            # Reintentar sin JOIN para listar solo actividades + estado
            cur = con.cursor()
            cur.execute("""
                WITH base AS (
                  SELECT
                    a.id_actividad, a.nombre, a.fecha_inicio, a.fecha_fin,
                    a.fecha_apertura_inscripcion, a.fecha_cierre_inscripcion,
                    CASE
                      WHEN date('now','localtime') <  date(a.fecha_apertura_inscripcion) THEN 'planificado'
                      WHEN date('now','localtime') BETWEEN date(a.fecha_apertura_inscripcion) AND date(a.fecha_cierre_inscripcion) THEN 'inscripcion_abierta'
                      WHEN date('now','localtime') BETWEEN date(a.fecha_inicio) AND date(a.fecha_fin) THEN 'en_curso'
                      WHEN date('now','localtime') >  date(a.fecha_fin) THEN 'cerrado'
                      ELSE 'desconocido'
                    END AS estado_calc
                  FROM actividad a
                )
                SELECT b.id_actividad, b.nombre, b.fecha_inicio, b.fecha_fin, b.estado_calc,
                       0.0, 0.0, 0.0, 0.0
                FROM base b
                WHERE date(b.fecha_inicio) BETWEEN ? AND ?
                  AND (? = 'todos' OR b.estado_calc = ?)
                ORDER BY date(b.fecha_inicio), b.nombre;
            """, (fi_txt, ff_txt, estado, estado))
            return cur.fetchall()
        else:
            raise
    finally:
        con.close()

def _pintar(rows):
    """Separa cerrados / no cerrados y pinta tablas con confirmados/estimados."""
    cerrados, no_cerrados = [], []
    for r in rows:
        (_id, nombre, f_ini, f_fin, estado,
         ing_c, gas_c, ing_e, gas_e) = r
        bal_conf = ing_c - gas_c
        bal_total_est = (ing_c + ing_e) - (gas_c + gas_e)

        if estado == "cerrado":
            cerrados.append([
                f_ini, nombre, estado,
                f"{ing_c:.2f}", f"{gas_c:.2f}", f"{bal_conf:.2f}"
            ])
        else:
            no_cerrados.append([
                f_ini, nombre, estado,
                f"{ing_c:.2f}", f"{gas_c:.2f}", f"{bal_conf:.2f}",
                f"{ing_e:.2f}", f"{gas_e:.2f}", f"{bal_total_est:.2f}"
            ])

    if cerrados:
        print("\n=== Cursos CERRADOS ===")
        cabe_c = ["Fecha", "Nombre", "Estado", "Ingresos conf.", "Gastos conf.", "Balance conf."]
        print(tabla(cabe_c, cerrados))
    else:
        print("\n=== Cursos CERRADOS ===")
        print("(ninguno en el rango/estado elegido)")

    if no_cerrados:
        print("\n=== Cursos NO CERRADOS (incluye estimados) ===")
        cabe_n = ["Fecha", "Nombre", "Estado",
                  "Ing. conf.", "Gas. conf.", "Bal. conf.",
                  "Ing. est.", "Gas. est.", "Bal. total estimado"]
        print(tabla(cabe_n, no_cerrados))
    else:
        print("\n=== Cursos NO CERRADOS ===")
        print("(ninguno en el rango/estado elegido)")

def main():
    print("\n=== Consulta de Ingresos, Gastos y Balance Económico ===")
    fi_txt, ff_txt = _pedir_rango_por_defecto()
    estado = _pedir_estado()
    rows = _consultar(fi_txt, ff_txt, estado)
    _pintar(rows)

if __name__ == "__main__":
    main()
