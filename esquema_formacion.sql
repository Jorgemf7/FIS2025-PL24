
-- Reset
DROP TABLE IF EXISTS actividad;
DROP TABLE IF EXISTS profesor;
DROP TABLE IF EXISTS colegio;

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
    UNIQUE(id_colegio, nombre),
    FOREIGN KEY (id_colegio)  REFERENCES colegio(id_colegio),
    FOREIGN KEY (id_profesor) REFERENCES profesor(id_profesor)
);
