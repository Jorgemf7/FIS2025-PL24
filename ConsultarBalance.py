import os
import sqlite3
from datetime import date, datetime
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
        if "no such table: movimiento" in msg:
            print("\nError: la tabla 'movimiento' no existe. Se mostrarán actividades sin totales económicos.")
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

def _separar_listas(rows):
    cerrados, no_cerrados = [], []
    for r in rows:
        (_id, nombre, f_ini, f_fin, estado, ing_c, gas_c, ing_e, gas_e) = r
        bal_conf = ing_c - gas_c
        bal_total_est = (ing_c + ing_e) - (gas_c + gas_e)
        if estado == "cerrado":
            cerrados.append([f_ini, nombre, estado,
                             f"{ing_c:.2f}", f"{gas_c:.2f}", f"{bal_conf:.2f}"])
        else:
            no_cerrados.append([f_ini, nombre, estado,
                                f"{ing_c:.2f}", f"{gas_c:.2f}", f"{bal_conf:.2f}",
                                f"{ing_e:.2f}", f"{gas_e:.2f}", f"{bal_total_est:.2f}"])
    return cerrados, no_cerrados

def _imprimir_listas(cerrados, no_cerrados, sufijo_titulo=""):
    print(f"\n=== Cursos CERRADOS{sufijo_titulo} ===")
    if cerrados:
        cabe_c = ["Fecha", "Nombre", "Estado", "Ingresos conf.", "Gastos conf.", "Balance conf."]
        print(tabla(cabe_c, cerrados))
    else:
        print("(ninguno en el rango/estado elegido)")
    print(f"\n=== Cursos NO CERRADOS (incluye estimados){sufijo_titulo} ===")
    if no_cerrados:
        cabe_n = ["Fecha", "Nombre", "Estado",
                  "Ing. conf.", "Gas. conf.", "Bal. conf.",
                  "Ing. est.", "Gas. est.", "Bal. total estimado"]
        print(tabla(cabe_n, no_cerrados))
    else:
        print("(ninguno en el rango/estado elegido)")

def _filtrar_por_balance(cerrados, no_cerrados, modo):
    if modo == "t":
        return cerrados, no_cerrados
    def match_pos(row):
        try: return float(row[-1]) > 0
        except ValueError: return False
    def match_neg(row):
        try: return float(row[-1]) < 0
        except ValueError: return False
    if modo == "s":
        return [r for r in cerrados if match_pos(r)], [r for r in no_cerrados if match_pos(r)]
    if modo == "d":
        return [r for r in cerrados if match_neg(r)], [r for r in no_cerrados if match_neg(r)]
    print("Error: opción de filtrado no válida. Se mostrarán todos.")
    return cerrados, no_cerrados

# --------- Exportación a PDF ---------
def _exportar_pdf(cerrados, no_cerrados, etiqueta=""):
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    except Exception:
        print("Error: Para exportar a PDF necesitas instalar reportlab (pip install reportlab).")
        return

    import os
    os.makedirs("informes", exist_ok=True)
    fname = f"informe_balance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    path = os.path.join("informes", fname)

    # Página en apaisado + márgenes pequeños para ganar ancho útil
    pagesize = landscape(A4)
    LEFT, RIGHT, TOP, BOTTOM = 24, 24, 24, 24
    doc = SimpleDocTemplate(path, pagesize=pagesize,
                            leftMargin=LEFT, rightMargin=RIGHT,
                            topMargin=TOP, bottomMargin=BOTTOM)

    # Ancho útil disponible
    from reportlab.lib.pagesizes import mm
    page_w, _ = pagesize
    avail_w = page_w - LEFT - RIGHT

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    h2_style = styles["Heading2"]
    cell_style = ParagraphStyle(
        "cell",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        spaceAfter=0,
    )

    def P(txt):  # envuelve texto para que quiebre líneas si hace falta
        return Paragraph(str(txt), cell_style)

    elems = []
    titulo = "Informe de balance económico por actividad" + (f"{etiqueta}" if etiqueta else "")
    elems.append(Paragraph(titulo, title_style))
    elems.append(Spacer(1, 6))

    # ---- Tabla CERRADOS
    elems.append(Paragraph("Cursos CERRADOS", h2_style))
    if cerrados:
        cabe_c = ["Fecha", "Nombre", "Estado", "Ingresos conf.", "Gastos conf.", "Balance conf."]
        data_c = [ [P(x) for x in cabe_c] ] + [ [P(x) for x in row] for row in cerrados ]

        # proporciones (suman 1.0): fecha, nombre, estado, num, num, num
        ratios_c = [0.10, 0.40, 0.15, 0.12, 0.12, 0.11]
        col_w_c = [r * avail_w for r in ratios_c]

        t_c = Table(data_c, colWidths=col_w_c, repeatRows=1)
        t_c.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
        ]))
        elems.append(t_c)
    else:
        elems.append(Paragraph("No hay cursos cerrados en el rango.", styles["Normal"]))
    elems.append(Spacer(1, 10))

    # ---- Tabla NO CERRADOS
    elems.append(Paragraph("Cursos NO CERRADOS (incluye estimados)", h2_style))
    if no_cerrados:
        cabe_n = ["Fecha", "Nombre", "Estado",
                  "Ing. conf.", "Gas. conf.", "Bal. conf.",
                  "Ing. est.", "Gas. est.", "Bal. total estimado"]
        data_n = [[P(x) for x in cabe_n]] + [[P(x) for x in row] for row in no_cerrados]

        # ¡IMPORTANTE! Ratios que suman <= 1.00
        # fecha, nombre, estado, 6 columnas numéricas
        ratios_n = [0.09, 0.41, 0.12, 0.06, 0.06, 0.06, 0.06, 0.06, 0.08]  # total = 1.00
        col_w_n = [r * avail_w for r in ratios_n]

        t_n = Table(data_n, colWidths=col_w_n, repeatRows=1)
        t_n.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
            # menos padding para ganar ancho útil
            ("LEFTPADDING", (0,0), (-1,-1), 2),
            ("RIGHTPADDING",(0,0), (-1,-1), 2),
        ]))
        elems.append(t_n)
    else:
        elems.append(Paragraph("No hay cursos no cerrados en el rango.", styles["Normal"]))


    doc.build(elems)
    print(f"Informe guardado en: {path}")


def _preguntar_exportar(cerrados, no_cerrados, etiqueta=""):
    resp = input("\n¿Desea exportar este resultado a PDF en la carpeta 'informes'? (s/n): ").strip().lower()
    if resp == "s":
        _exportar_pdf(cerrados, no_cerrados, etiqueta)

# --------- Flujo principal ---------
def main():
    print("\n=== Consulta de Ingresos, Gastos y Balance Económico ===")
    fi_txt, ff_txt = _pedir_rango_por_defecto()
    estado = _pedir_estado()
    rows = _consultar(fi_txt, ff_txt, estado)

    # Informe completo
    cerrados, no_cerrados = _separar_listas(rows)
    _imprimir_listas(cerrados, no_cerrados)
    _preguntar_exportar(cerrados, no_cerrados, etiqueta=" (informe completo)")

    # Post-filtro interactivo
    while True:
        print("\nFiltrar por balance:")
        print("  s) Solo superávit")
        print("  d) Solo deficitario")
        print("  t) Todos")
        print("  n) Salir")
        op = input("Selecciona una opción [s/d/t/n]: ").strip().lower()

        if op == "n":
            break
        if op not in ("s", "d", "t"):
            print("Error: opción inválida.")
            continue

        c_fil, n_fil = _filtrar_por_balance(cerrados, no_cerrados, op)
        suf = {"s": " (solo superávit)", "d": " (solo deficitarios)", "t": " (todos)"}[op]
        _imprimir_listas(c_fil, n_fil, sufijo_titulo=suf)
        _preguntar_exportar(c_fil, n_fil, etiqueta=suf)

if __name__ == "__main__":
    main()
