import os
import sqlite3
from datetime import date
from utils.fecha import validar_fecha
from utils.prettytable import tabla

DB_PATH = "FormacionDB.db"
ESTADOS = ["todos", "abierto", "cerrado"]

# ============================
#       CONSULTA PRINCIPAL
# ============================

SQL = """
WITH base AS (
  SELECT
    a.id_actividad,
    a.nombre,
    a.fecha_inicio,
    a.fecha_fin,
    a.cuota,
    a.remuneracion,
    a.estado AS estado_calc
  FROM actividad a
),
mov_agg AS (
  SELECT
    id_actividad,
    IFNULL(SUM(CASE WHEN tipo='ingreso' AND confirmado=1 THEN importe END),0) AS ingresos_confirmados,
    -- GASTOS CONFIRMADOS (SIGUEN NEGATIVOS, LOS ARREGLAMOS EN PYTHON)
    IFNULL(SUM(CASE WHEN tipo='gasto'   AND confirmado=1 THEN importe END),0) AS gastos_confirmados
  FROM movimiento
  GROUP BY id_actividad
),
insc_agg AS (
  SELECT
    id_actividad,
    COUNT(*) AS num_inscripciones
  FROM inscripcion
  GROUP BY id_actividad
)
SELECT
  b.id_actividad,
  b.nombre,
  b.fecha_inicio,
  b.fecha_fin,
  b.estado_calc,

  IFNULL(m.ingresos_confirmados,0) AS ingresos_confirmados,
  IFNULL(m.gastos_confirmados,0)   AS gastos_confirmados,

  (IFNULL(i.num_inscripciones,0) * IFNULL(b.cuota,0)) AS ingresos_estimados,
  IFNULL(b.remuneracion,0) AS gastos_estimados

FROM base b
LEFT JOIN mov_agg  m ON m.id_actividad = b.id_actividad
LEFT JOIN insc_agg i ON i.id_actividad = b.id_actividad
WHERE date(b.fecha_inicio) BETWEEN ? AND ?
  AND (? = 'todos' OR b.estado_calc = ?)
ORDER BY date(b.fecha_inicio), b.nombre;
"""

# ============================
#       FUNCIONES AUXILIARES
# ============================

def _pedir_rango_por_defecto():
    hoy = date.today()
    inicio_def = f"{hoy.year}-01-01"
    fin_def    = f"{hoy.year}-12-31"

    fi_txt = input(f"Fecha inicio [YYYY-MM-DD] (por defecto {inicio_def}): ").strip() or inicio_def
    ff_txt = input(f"Fecha fin    [YYYY-MM-DD] (por defecto {fin_def}): ").strip() or fin_def

    fi = validar_fecha(fi_txt)
    ff = validar_fecha(ff_txt)

    if not fi or not ff or ff < fi:
        print("Error: Rango de fechas inválido. Inténtalo de nuevo.\n")
        return _pedir_rango_por_defecto()

    return fi_txt, ff_txt


def _pedir_estado():
    print("\nEstados disponibles:", ", ".join(ESTADOS))
    estado = input("Estado a filtrar (por defecto 'todos'): ").strip().lower() or "todos"

    if estado not in ESTADOS:
        print("Error: Estado no válido. Usando 'todos'.")
        estado = "todos"

    return estado


def _consultar(fi_txt, ff_txt, estado):
    con = sqlite3.connect(DB_PATH)
    try:
        cur = con.cursor()
        cur.execute(SQL, (fi_txt, ff_txt, estado, estado))
        return cur.fetchall()

    except sqlite3.OperationalError as e:
        msg = str(e).lower()

        # Si faltan tablas o columna estado → fallback básico
        if ("no such table" in msg or "no such column: estado" in msg):
            print("\nAviso: faltan tablas o columna 'estado'. Se mostrarán actividades sin totales económicos.")
            cur = con.cursor()
            cur.execute("""
                SELECT
                    a.id_actividad,
                    a.nombre,
                    a.fecha_inicio,
                    a.fecha_fin,
                    COALESCE(a.estado,'abierto') AS estado_calc,
                    0.0, 0.0, 0.0, 0.0
                FROM actividad a
                WHERE date(a.fecha_inicio) BETWEEN ? AND ?
                  AND (? = 'todos' OR COALESCE(a.estado,'abierto') = ?)
                ORDER BY date(a.fecha_inicio), a.nombre;
            """, (fi_txt, ff_txt, estado, estado))
            return cur.fetchall()

        else:
            raise

    finally:
        con.close()


def _separar_listas(rows):
    cerrados, no_cerrados = [], []

    for r in rows:
        (_id, nombre, f_ini, f_fin, estado, ing_c, gas_c, ing_e, gas_e) = r

        # Arreglamos aquí: los gastos confirmados vienen NEGATIVOS en la BD
        gas_c = abs(gas_c)

        # Balance confirmado: ingresos_confirmados - gastos_confirmados (ya positivos)
        bal_conf = ing_c - gas_c

        # Balance TOTAL estimado: ingresos_estimados - gastos_estimados
        bal_total_est = ing_e - gas_e

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

    return cerrados, no_cerrados


def _imprimir_listas(cerrados, no_cerrados, sufijo_titulo=""):
    print(f"\n=== Cursos CERRADOS{sufijo_titulo} ===")
    if cerrados:
        cabe_c = ["Fecha", "Nombre", "Estado", "Ingresos conf.", "Gastos conf.", "Balance conf."]
        print(tabla(cabe_c, cerrados))
    else:
        print("(ninguno en el rango / estado elegido)")

    print(f"\n=== Cursos NO CERRADOS (incluye estimados){sufijo_titulo} ===")
    if no_cerrados:
        cabe_n = [
            "Fecha", "Nombre", "Estado",
            "Ing. conf.", "Gas. conf.", "Bal. conf.",
            "Ing. est.", "Gas. est.", "Bal. total estimado"
        ]
        print(tabla(cabe_n, no_cerrados))
    else:
        print("(ninguno en el rango / estado elegido)")


def _filtrar_por_balance(cerrados, no_cerrados, modo):

    if modo == "t":
        return cerrados, no_cerrados

    def ok_pos(row):
        try: return float(row[-1]) > 0
        except: return False

    def ok_neg(row):
        try: return float(row[-1]) < 0
        except: return False

    if modo == "s":
        return [r for r in cerrados if ok_pos(r)], [r for r in no_cerrados if ok_pos(r)]
    if modo == "d":
        return [r for r in cerrados if ok_neg(r)], [r for r in no_cerrados if ok_neg(r)]

    print("Opción inválida, mostrando todos.")
    return cerrados, no_cerrados

# ============================
#       MAIN
# ============================

def main():
    print("\n=== Consulta de Ingresos, Gastos y Balance Económico ===")

    fi_txt, ff_txt = _pedir_rango_por_defecto()
    estado = _pedir_estado()

    rows = _consultar(fi_txt, ff_txt, estado)

    cerrados, no_cerrados = _separar_listas(rows)
    _imprimir_listas(cerrados, no_cerrados)

    # Filtros adicionales
    while True:
        print("\nFiltrar por balance:")
        print("  s) Solo superávit")
        print("  d) Solo deficitario")
        print("  t) Todos")
        print("  n) Salir")

        op = input("Selecciona opción: ").strip().lower()

        if op == "n":
            break

        if op not in ("s", "d", "t"):
            print("Opción inválida.")
            continue

        c_fil, n_fil = _filtrar_por_balance(cerrados, no_cerrados, op)
        suf = {"s": " (solo superávit)", "d": " (solo deficitarios)", "t": " (todos)"}[op]

        _imprimir_listas(c_fil, n_fil, sufijo_titulo=suf)

if __name__ == "__main__":
    main()
