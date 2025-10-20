import sys
import os
import sqlite3
from datetime import datetime, timedelta
from planificacion import PlanificacionActividad
from utils.fecha import validar_fecha
from prettytable import PrettyTable 
from utils.prettytable import tabla   
from utils.cargar_archivos import cargar_csv, cargar_json


DATE_FMT = "%Y-%m-%d"

def coerce_float(x, field_name):
    try:
        v = float(x)
        if field_name == "remuneracion" and v < 0:
            raise ValueError("remuneración negativa")
        if field_name == "cuota" and v < 0:
            # permitimos 0 o >0 (si quieres impedir negativas estrictamente)
            raise ValueError("cuota negativa")
        return v
    except Exception as e:
        raise ValueError(f"Campo '{field_name}' inválido ({e})")

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
    obligatorios = ["colegio","profesor_email","nombre","objetivos","contenidos",
                    "remuneracion","fecha_inicio","fecha_fin","lugar"]
    faltan = [k for k in obligatorios if not str(reg.get(k, "")).strip()]
    if faltan:
        raise ValueError(f"Faltan campos obligatorios: {', '.join(faltan)}")

    # tipos
    reg["remuneracion"] = coerce_float(reg["remuneracion"], "remuneracion")
    fi = validar_fecha(reg["fecha_inicio"])
    ff = validar_fecha(reg["fecha_fin"])
    if not fi or not ff:
        raise ValueError("Fechas inválidas (use YYYY-MM-DD)")
    if ff < fi:
        raise ValueError("fecha_fin anterior a fecha_inicio")
    return reg

def mostrar_resumen_lote(actividades):
    cab = ["#", "Colegio", "Profesor", "Nombre", "Inicio", "Fin", "Lugar", "Cuota", "Gratuita", "Remun."]
    con = []
    for i, a in enumerate(actividades, 1):
        con.append([
            i, a["colegio"], a["profesor_email"], a["nombre"],
            a["fecha_inicio"], a["fecha_fin"], a["lugar"],
            f"{a['cuota']:.2f}", "Sí" if a["gratuita"] else "No",
            f"{a['remuneracion']:.2f}",
        ])
    print("\n Resumen de TODAS las actividades a registrar:\n")
    print(tabla(cab, con))

# ---------- Modo interactivo ----------
def capturar_actividad():
    print("\n=== Registro de una nueva actividad formativa ===")
    colegio = input("Nombre del colegio: ").strip()
    profesor_email = input("Email del profesor: ").strip()
    nombre = input("Nombre de la actividad: ").strip()
    objetivos = input("Objetivos de la actividad: ").strip()
    contenidos = input("Contenidos de la actividad: ").strip()

    # Remuneración
    try:
        remuneracion = coerce_float(input("Remuneración (€): ").strip(), "remuneracion")
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

    lugar = input("Lugar donde se celebrará: ").strip()

    # Fechas de inscripción automáticas
    fecha_apertura = (fi - timedelta(days=21)).strftime(DATE_FMT)
    fecha_cierre = (fi - timedelta(days=3)).strftime(DATE_FMT)

    # Cuota / gratuita
    try:
        cuota = coerce_float(input("Cuota de inscripción (0 si gratuita): ").strip() or "0", "cuota")
        gratuita = True if cuota == 0 else False
    except ValueError as e:
        print(f"Error: {e}")
        return None

    # Resumen de esta actividad (individual)
    cab1 = ["Campo", "Valor"]
    con1 = [
        ["Colegio", colegio],
        ["Profesor", profesor_email],
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



def normalizar_y_validar_lote(registros):
    normalizados = []
    errores = []
    for idx, raw in enumerate(registros, start=1):
        try:
            reg = {
                "colegio": str(raw.get("colegio","")).strip(),
                "profesor_email": str(raw.get("profesor_email","")).strip(),
                "nombre": str(raw.get("nombre","")).strip(),
                "objetivos": str(raw.get("objetivos","")).strip(),
                "contenidos": str(raw.get("contenidos","")).strip(),
                "remuneracion": raw.get("remuneracion",""),
                "fecha_inicio": str(raw.get("fecha_inicio","")).strip(),
                "fecha_fin": str(raw.get("fecha_fin","")).strip(),
                "lugar": str(raw.get("lugar","")).strip(),
                "fecha_apertura": str(raw.get("fecha_apertura","")).strip() or None,
                "fecha_cierre": str(raw.get("fecha_cierre","")).strip() or None,
                "cuota": raw.get("cuota", 0),
            }
            reg = validar_registro_base(reg)
            reg = completar_inscripciones(reg)
            reg = normalizar_gratuita_y_cuota(reg)
            normalizados.append(reg)
        except Exception as e:
            errores.append([idx, raw.get("nombre","<sin nombre>"), str(e)])
    return normalizados, errores

def agregar_actividades_desde_archivo(ruta):
    ext = os.path.splitext(ruta)[1].lower()
    if ext == ".json":
        registros = cargar_json(ruta)
    elif ext == ".csv":
        registros = cargar_csv(ruta)
    else:
        raise ValueError("Formato no soportado. Use .json o .csv")

    actividades, errores_pre = normalizar_y_validar_lote(registros)

    if errores_pre:
        print("\n Registros descartados en validación previa:")
        print(tabla(["#", "Actividad", "Error"], errores_pre))

    if not actividades:
        print("\n No hay registros válidos para insertar.")
        return

    mostrar_resumen_lote(actividades)
    confirmar = input("\n¿Desea registrar estas actividades en la base de datos? (s/n): ").strip().lower()
    if confirmar != "s":
        print("Error: Operación cancelada. No se insertó ninguna actividad.")
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

# ---------- Entrypoint ----------
if __name__ == "__main__":
    # Carpeta fija donde buscar archivos de carga
    CARPETA_CARGA = os.path.join(os.path.dirname(__file__), "archivos_carga")

    print("¿Cómo quieres cargar actividades?")
    print("  1) Interactivo (introducir actividades a mano)")
    print("  2) Desde archivo (CSV/JSON)")
    modo = input("Selecciona 1 o 2: ").strip()

    if modo == "2":
        # Modo carga desde archivo en carpeta fija
        print(f"\n Los archivos deben estar en: {CARPETA_CARGA}")
        if not os.path.exists(CARPETA_CARGA):
            print(f"Error: La carpeta '{CARPETA_CARGA}' no existe. Créala y añade los archivos CSV/JSON.")
            sys.exit(1)

        # Mostrar archivos disponibles
        disponibles = [f for f in os.listdir(CARPETA_CARGA) if f.lower().endswith((".csv", ".json"))]
        if not disponibles:
            print("Error: No se encontraron archivos .csv o .json en la carpeta de carga.")
            sys.exit(1)

        print("\nArchivos disponibles para cargar:")
        for i, f in enumerate(disponibles, 1):
            print(f"  {i}) {f}")

        sel = input("\nSelecciona el número del archivo a cargar: ").strip()
        try:
            idx = int(sel) - 1
            ruta = os.path.join(CARPETA_CARGA, disponibles[idx])
        except (ValueError, IndexError):
            print("Error: Selección inválida. Saliendo.")
            sys.exit(1)

        # Validar extensión y cargar
        ext = os.path.splitext(ruta)[1].lower()
        if ext not in (".csv", ".json"):
            print("Error: Error: extensión no válida. Use .csv o .json.")
            sys.exit(1)

        print(f"\n Cargando archivo seleccionado: {disponibles[idx]}")
        try:
            agregar_actividades_desde_archivo(ruta)
        except Exception as e:
            print(f"Error: Error al cargar el archivo: {e}")

    else:
        # Modo interactivo (tu flujo actual)
        actividades = agregar_actividades_interactivas()
        if not actividades:
            print("\nNo hay actividades para registrar. Saliendo.")
            sys.exit(0)
        mostrar_resumen_lote(actividades)
        confirmar = input("\n¿Desea registrar estas actividades en la base de datos? (s/n): ").strip().lower()
        if confirmar != "s":
            print(" Operación cancelada. No se insertó ninguna actividad.")
            sys.exit(0)

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
                )
                ok_rows.append([i, a["nombre"], a["colegio"], new_id])
            except Exception as e:
                ko_rows.append([i, a["nombre"], a["colegio"], str(e)])

        if ok_rows:
            print("\nInserciones correctas:")
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



