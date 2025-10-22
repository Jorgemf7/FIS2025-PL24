
-- Reset
DROP TABLE IF EXISTS actividad;
DROP TABLE IF EXISTS profesor;
DROP TABLE IF EXISTS colegio;
DROP TABLE IF EXISTS movimiento;

-- Tabla de colegios
CREATE TABLE colegio (
    id_colegio INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    provincia TEXT,
    email_contacto TEXT
);

-- Tabla de profesores (único profesor por actividad en este sprint)
CREATE TABLE profesor (
    id_profesor INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellidos TEXT,
    email TEXT UNIQUE,
    telefono TEXT,
    remuneracion_base REAL DEFAULT 0 CHECK(remuneracion_base >= 0)
);

-- Tabla de actividades planificadas
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
    -- Reglas de coherencia básicas columna a columna
    CHECK (date(fecha_inicio) <= date(fecha_fin)),
    CHECK (date(fecha_apertura_inscripcion) <= date(fecha_cierre_inscripcion)),
    CHECK (date(fecha_cierre_inscripcion) <= date(fecha_inicio)),
    CHECK ( (gratuita = 1 AND cuota = 0) OR (gratuita = 0 AND cuota >= 0) ),
    UNIQUE(id_colegio, nombre), -- Evita duplicar el mismo nombre en el mismo colegio
    FOREIGN KEY (id_colegio)  REFERENCES colegio(id_colegio),
    FOREIGN KEY (id_profesor) REFERENCES profesor(id_profesor)
);


-- Movimientos económicos por actividad formativa
CREATE TABLE IF NOT EXISTS movimiento (
    id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
    id_actividad  INTEGER NOT NULL,
    tipo          TEXT    NOT NULL CHECK (tipo IN ('ingreso','gasto')),
    fecha         TEXT    NOT NULL CHECK (fecha LIKE '____-__-__'), -- YYYY-MM-DD
    importe       REAL    NOT NULL CHECK (importe >= 0),
    descripcion   TEXT,
    confirmado    INTEGER NOT NULL DEFAULT 0 CHECK (confirmado IN (0,1)),
    FOREIGN KEY (id_actividad) REFERENCES actividad(id_actividad) ON DELETE CASCADE
);

-- Índices recomendados
CREATE INDEX IF NOT EXISTS idx_mov_actividad ON movimiento(id_actividad);
CREATE INDEX IF NOT EXISTS idx_mov_fecha     ON movimiento(fecha);
CREATE INDEX IF NOT EXISTS idx_mov_tipo      ON movimiento(tipo);
