-- ==========================================
--  Reset limpio SOLO bajo demanda del usuario
--  (No se borra BD al iniciar ni al salir)
-- ==========================================
PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS inscripcion;
DROP TABLE IF EXISTS movimiento;
DROP TABLE IF EXISTS actividad;
DROP TABLE IF EXISTS profesor;
DROP TABLE IF EXISTS colegio;
DROP TABLE IF EXISTS alerta_pago;

PRAGMA foreign_keys = ON;

-- ===== Esquema base (ampliado con 'plazas' e 'inscripcion') =====
CREATE TABLE colegio (
    id_colegio INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    provincia TEXT,
    email_contacto TEXT
);

CREATE TABLE profesor (
    id_profesor INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellidos TEXT,
    email TEXT UNIQUE,
    telefono TEXT,
    remuneracion_base REAL DEFAULT 0 CHECK(remuneracion_base >= 0)
);

CREATE TABLE actividad (
    id_actividad INTEGER PRIMARY KEY AUTOINCREMENT,
    id_colegio INTEGER NOT NULL,
    id_profesor INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    objetivos TEXT,
    contenidos TEXT,
    remuneracion REAL NOT NULL CHECK(remuneracion >= 0),
    fecha_inicio TEXT NOT NULL CHECK (fecha_inicio LIKE '____-__-__'),
    fecha_fin    TEXT NOT NULL CHECK (fecha_fin    LIKE '____-__-__'),
    lugar TEXT NOT NULL,
    fecha_apertura_inscripcion TEXT NOT NULL CHECK (fecha_apertura_inscripcion LIKE '____-__-__'),
    fecha_cierre_inscripcion   TEXT NOT NULL CHECK (fecha_cierre_inscripcion   LIKE '____-__-__'),
    gratuita INTEGER NOT NULL DEFAULT 0 CHECK (gratuita IN (0,1)),
    cuota REAL DEFAULT 0 CHECK(cuota >= 0),
    plazas INTEGER NOT NULL CHECK(plazas > 0),
    CHECK (date(fecha_inicio) <= date(fecha_fin)),
    CHECK (date(fecha_apertura_inscripcion) <= date(fecha_cierre_inscripcion)),
    CHECK ( (gratuita = 1 AND cuota = 0) OR (gratuita = 0 AND cuota >= 0) ),
    UNIQUE(id_colegio, nombre),
    FOREIGN KEY (id_colegio)  REFERENCES colegio(id_colegio),
    FOREIGN KEY (id_profesor) REFERENCES profesor(id_profesor)
);

CREATE TABLE movimiento (
    id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
    id_actividad  INTEGER NOT NULL,
    tipo          TEXT    NOT NULL CHECK (tipo IN ('ingreso','gasto')),
    fecha         TEXT    NOT NULL CHECK (fecha LIKE '____-__-__'),
    importe       REAL    NOT NULL,
    descripcion   TEXT,
    categoria     TEXT    NOT NULL DEFAULT 'otro' CHECK (categoria IN ('alumno','profesor','otro')),
    confirmado    INTEGER NOT NULL DEFAULT 1 CHECK (confirmado IN (0,1)),
    CHECK ( (tipo='ingreso' AND importe > 0) OR (tipo='gasto' AND importe < 0) ),
    FOREIGN KEY (id_actividad) REFERENCES actividad(id_actividad) ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_mov_no_duplicados
ON movimiento(id_actividad, fecha, tipo, importe, IFNULL(descripcion,''), categoria);

-- Inscripciones (para reflejar "Alicia/Juan se inscriben el día X")
CREATE TABLE inscripcion (
    id_inscripcion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_actividad INTEGER NOT NULL,
    alumno TEXT NOT NULL,
    fecha TEXT NOT NULL CHECK (fecha LIKE '____-__-__'),
    FOREIGN KEY (id_actividad) REFERENCES actividad(id_actividad) ON DELETE CASCADE
);

-- ===== Carga específica de la revisión =====

-- Colegios (COIIPA y CPIICYL)
INSERT INTO colegio (nombre, provincia, email_contacto) VALUES
('Colegio Oficial de Ingenieria Informatica de Asturias', 'Asturias', 'contacto@coiipa.es'),
('Colegio Oficial de Ingenieria Informatica de Castilla y León', 'Castilla y León', 'info@cpiicyl.es');

-- Profesores (Claudio y Fanjul)
INSERT INTO profesor (nombre, apellidos, email, telefono, remuneracion_base) VALUES
('Claudio', NULL, 'claudio@colegio.es', '600000001', 0),
('Fanjul',  NULL, 'fanjul@colegio.es',  '600000002', 0);

-- Acciones formativas
-- 1) Administración de BBDD Neo4J (01/12/2025 - 05/12/2025) / Inscripción: 03/11 - 21/11
INSERT INTO actividad (
    id_colegio, id_profesor, nombre, objetivos, contenidos, remuneracion,
    fecha_inicio, fecha_fin, lugar,
    fecha_apertura_inscripcion, fecha_cierre_inscripcion,
    gratuita, cuota, plazas
) VALUES (
    (SELECT id_colegio FROM colegio WHERE nombre='Colegio Oficial de Ingenieria Informatica de Asturias'),
    (SELECT id_profesor FROM profesor WHERE email='claudio@colegio.es'),
    'Administración de BBDD Neo4J',
    'Formación práctica en Neo4J',
    'Modelo de grafos, Cypher, indexación',
    1500.0,
    '2025-12-01','2025-12-05','Sede COIIPA, Oviedo',
    '2025-11-03','2025-11-21',
    0, 200.0, 10
);

-- 2) Scrum Master (01/10/2025 - 31/10/2025) / Inscripción: 01/09 - 19/09
INSERT INTO actividad (
    id_colegio, id_profesor, nombre, objetivos, contenidos, remuneracion,
    fecha_inicio, fecha_fin, lugar,
    fecha_apertura_inscripcion, fecha_cierre_inscripcion,
    gratuita, cuota, plazas
) VALUES (
    (SELECT id_colegio FROM colegio WHERE nombre='Colegio Oficial de Ingenieria Informatica de Castilla y León'),
    (SELECT id_profesor FROM profesor WHERE email='fanjul@colegio.es'),
    'Scrum Master',
    'Marco Scrum y rol de SM',
    'Eventos, artefactos, métricas',
    2500.0,
    '2025-10-01','2025-10-31','Sede CPIICYL, Valladolid',
    '2025-09-01','2025-09-19',
    0, 500.0, 8
);

-- Inscripciones
-- Neo4J
INSERT INTO inscripcion (id_actividad, alumno, fecha)
SELECT a.id_actividad, 'Alicia', '2025-11-03' FROM actividad a WHERE a.nombre='Administración de BBDD Neo4J';
INSERT INTO inscripcion (id_actividad, alumno, fecha)
SELECT a.id_actividad, 'Juan',   '2025-11-03' FROM actividad a WHERE a.nombre='Administración de BBDD Neo4J';

-- Scrum Master
INSERT INTO inscripcion (id_actividad, alumno, fecha)
SELECT a.id_actividad, 'Alicia', '2025-09-01' FROM actividad a WHERE a.nombre='Scrum Master';
INSERT INTO inscripcion (id_actividad, alumno, fecha)
SELECT a.id_actividad, 'Juan',   '2025-09-03' FROM actividad a WHERE a.nombre='Scrum Master';

-- Movimientos (ingresos/gastos)
-- Neo4J: ingresos durante periodo de inscripción
INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado)
SELECT a.id_actividad, 'ingreso','2025-11-04', 150.0, 'Pago Alicia (parcial)', 'alumno', 1 FROM actividad a WHERE a.nombre='Administración de BBDD Neo4J';
INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado)
SELECT a.id_actividad, 'ingreso','2025-11-03', 100.0, 'Pago Juan (1º parcial)', 'alumno', 1 FROM actividad a WHERE a.nombre='Administración de BBDD Neo4J';
INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado)
SELECT a.id_actividad, 'ingreso','2025-11-04', 100.0, 'Pago Juan (2º parcial por aviso)', 'alumno', 1 FROM actividad a WHERE a.nombre='Administración de BBDD Neo4J';

-- Scrum Master: ingresos en septiembre, gasto al profesor el 03/11
INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado)
SELECT a.id_actividad, 'ingreso','2025-09-04', 550.0, 'Pago Alicia', 'alumno', 1 FROM actividad a WHERE a.nombre='Scrum Master';
INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado)
SELECT a.id_actividad, 'ingreso','2025-09-04', 500.0, 'Pago Juan',   'alumno', 1 FROM actividad a WHERE a.nombre='Scrum Master';
INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado)
SELECT a.id_actividad, 'gasto','2025-11-03', -3025.0, 'Pago profesor', 'profesor', 1 FROM actividad a WHERE a.nombre='Scrum Master';
