PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS inscripcion;
DROP TABLE IF EXISTS movimiento;
DROP TABLE IF EXISTS actividad;
DROP TABLE IF EXISTS profesor;
DROP TABLE IF EXISTS colegio;

PRAGMA foreign_keys = ON;

-- ---- COLEGIO ----
CREATE TABLE colegio (
    id_colegio INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    provincia TEXT,
    email_contacto TEXT
);

-- ---- PROFESOR ----
CREATE TABLE profesor (
    id_profesor INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellidos TEXT,
    email TEXT UNIQUE,
    telefono TEXT,
    remuneracion_base REAL DEFAULT 0 CHECK(remuneracion_base >= 0)
);

-- ---- ACTIVIDAD ----
-- incluye 'plazas' y las fechas de inscripción
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

-- ---- MOVIMIENTO ----
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

CREATE INDEX IF NOT EXISTS idx_mov_actividad ON movimiento(id_actividad);
CREATE UNIQUE INDEX IF NOT EXISTS ux_mov_no_duplicados
ON movimiento(id_actividad, fecha, tipo, importe, IFNULL(descripcion,''), categoria);

-- ---- (Opcional) INSCRIPCION ----
CREATE TABLE inscripcion (
    id_inscripcion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_actividad INTEGER NOT NULL,
    alumno TEXT NOT NULL,
    fecha TEXT NOT NULL CHECK (fecha LIKE '____-__-__'),
    FOREIGN KEY (id_actividad) REFERENCES actividad(id_actividad) ON DELETE CASCADE
);

-- ==== SEED MÍNIMO PARA CARGAR LOS CSV ====

-- Colegios EXACTAMENTE con los nombres de tu CSV
INSERT INTO colegio (nombre, provincia, email_contacto) VALUES
('Colegio Oficial de Ingenieria Informatica de Asturias', 'Asturias', 'contacto@coiipa.es'),
('Colegio Oficial de Ingenieria Informatica de Castilla y León', 'Castilla y León', 'info@cpiicyl.es');

-- Profesores EXACTAMENTE con los emails de tu CSV
INSERT INTO profesor (nombre, apellidos, email, telefono, remuneracion_base) VALUES
('Claudio', NULL, 'claudio@colegio.es', '600000001', 0),
('Fanjul',  NULL, 'fanjul@colegio.es',  '600000002', 0);
