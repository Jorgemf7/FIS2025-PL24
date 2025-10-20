
import sqlite3
from datetime import date

DB_PATH = "FormacionDB.db"

class PlanificacionActividad:
    @staticmethod
    def _connect():
        return sqlite3.connect(DB_PATH)

    @staticmethod
    def planificar_actividad(
        nombre, objetivos, contenidos, profesor_email, colegio_nombre,
        remuneracion, fecha_inicio, fecha_fin, lugar,
        fecha_apertura, fecha_cierre, gratuita=False, cuota=0.0
    ):
        # Validaciones mínimas de negocio (además de los CHECK de la BD)
        if not nombre or not colegio_nombre or not profesor_email:
            raise ValueError("Nombre de actividad, colegio y email de profesor son obligatorios.")
        if gratuita and float(cuota) != 0.0:
            raise ValueError("Si la actividad es gratuita, la cuota debe ser 0.")

        con = PlanificacionActividad._connect()
        try:
            cur = con.cursor()
            # Resolver claves por nombre/email
            cur.execute("SELECT id_colegio FROM colegio WHERE nombre = ?", (colegio_nombre,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Colegio no encontrado: {colegio_nombre}")
            id_colegio = row[0]

            cur.execute("SELECT id_profesor FROM profesor WHERE email = ?", (profesor_email,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Profesor no encontrado por email: {profesor_email}")
            id_profesor = row[0]

            # Insertar actividad
            cur.execute(
                '''
                INSERT INTO actividad (
                    id_colegio, id_profesor, nombre, objetivos, contenidos, remuneracion,
                    fecha_inicio, fecha_fin, lugar, fecha_apertura_inscripcion, fecha_cierre_inscripcion,
                    gratuita, cuota
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    id_colegio, id_profesor, nombre, objetivos, contenidos, float(remuneracion),
                    fecha_inicio, fecha_fin, lugar, fecha_apertura, fecha_cierre,
                    1 if gratuita else 0, float(cuota)
                )
            )
            con.commit()
            return cur.lastrowid
        finally:
            con.close()

    @staticmethod
    def listar_actividades(filtro_colegio=None):
        con = PlanificacionActividad._connect()
        try:
            cur = con.cursor()
            base = '''
                SELECT a.id_actividad, c.nombre as colegio, p.email as profesor_email,
                       a.nombre, a.fecha_inicio, a.fecha_fin, a.lugar,
                       a.fecha_apertura_inscripcion, a.fecha_cierre_inscripcion,
                       a.gratuita, a.cuota, a.remuneracion
                FROM actividad a
                JOIN colegio c ON a.id_colegio = c.id_colegio
                JOIN profesor p ON a.id_profesor = p.id_profesor
            '''
            params = []
            if filtro_colegio:
                base += " WHERE c.nombre = ?"
                params.append(filtro_colegio)
            base += " ORDER BY date(a.fecha_inicio)"
            cur.execute(base, params)
            return cur.fetchall()
        finally:
            con.close()
