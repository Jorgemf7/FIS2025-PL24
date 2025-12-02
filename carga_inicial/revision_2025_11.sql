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
DROP TABLE IF EXISTS alumno;

PRAGMA foreign_keys = ON;

-- ===== Esquema base (ampliado con 'plazas', 'inscripcion' y 'alumno') =====
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

-- Nueva tabla ALUMNO
CREATE TABLE alumno (
    id_alumno INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellidos TEXT,
    email TEXT UNIQUE,
    telefono TEXT
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
    estado TEXT NOT NULL DEFAULT 'abierto' CHECK (estado IN ('abierto','cerrado')),
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

    -- NUEVO: asociación opcional a alumno/profesor
    id_alumno     INTEGER,
    id_profesor   INTEGER,

    CHECK ( (tipo='ingreso' AND importe > 0) OR (tipo='gasto' AND importe < 0) ),

    -- Coherencia básica: si categoria='alumno' → id_alumno relleno, si 'profesor' → id_profesor
    CHECK (
        (categoria = 'alumno'   AND id_alumno IS NOT NULL AND id_profesor IS NULL) OR
        (categoria = 'profesor' AND id_profesor IS NOT NULL AND id_alumno IS NULL) OR
        (categoria = 'otro'     AND id_alumno IS NULL     AND id_profesor IS NULL)
    ),

    FOREIGN KEY (id_actividad) REFERENCES actividad(id_actividad) ON DELETE CASCADE,
    FOREIGN KEY (id_alumno)    REFERENCES alumno(id_alumno)      ON DELETE SET NULL,
    FOREIGN KEY (id_profesor)  REFERENCES profesor(id_profesor)  ON DELETE SET NULL
);


CREATE UNIQUE INDEX IF NOT EXISTS ux_mov_no_duplicados
ON movimiento(id_actividad, fecha, tipo, importe, IFNULL(descripcion,''), categoria);

-- Inscripciones (ligadas a alumno por id_alumno)
CREATE TABLE inscripcion (
    id_inscripcion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_actividad INTEGER NOT NULL,
    id_alumno   INTEGER NOT NULL,
    fecha TEXT NOT NULL CHECK (fecha LIKE '____-__-__'),
    FOREIGN KEY (id_actividad) REFERENCES actividad(id_actividad) ON DELETE CASCADE,
    FOREIGN KEY (id_alumno)    REFERENCES alumno(id_alumno)     ON DELETE CASCADE
);

-- ===== Carga específica de la revisión =====

-- Colegios (COIIPA y CPIICYL)
INSERT INTO colegio (nombre, provincia, email_contacto) VALUES
('Colegio Oficial de Ingenieria Informatica de Asturias', 'Asturias', 'contacto@coiipa.es'),
('Colegio Oficial de Ingenieria Informatica de Castilla y León', 'Castilla y León', 'info@cpiicyl.es');

-- Profesores
-- Neo4J -> Raquel (remuneración de la actividad: 750€)
-- Scrum Master -> Claudio (remuneración de la actividad: 1400€)
INSERT INTO profesor (nombre, apellidos, email, telefono, remuneracion_base) VALUES
('Raquel',  NULL, 'raquel@colegio.es',  '600000001', 0),
('Claudio', NULL, 'claudio@colegio.es', '600000002', 0);

-- Alumnos (Alicia, Juan, Mónica, Pablo)
INSERT INTO alumno (nombre, apellidos, email, telefono) VALUES
('Alicia', NULL, 'alicia@example.com', NULL),
('Juan',   NULL, 'juan@example.com',   NULL),
('Mónica', NULL, 'monica@example.com', NULL),
('Pablo',  NULL, 'pablo@example.com',  NULL);

-- Acciones formativas
-- 1) Administración de BBDD Neo4J
INSERT INTO actividad (
    id_colegio, id_profesor, nombre, objetivos, contenidos, remuneracion,
    fecha_inicio, fecha_fin, lugar,
    fecha_apertura_inscripcion, fecha_cierre_inscripcion,
    gratuita, cuota, plazas
) VALUES (
    (SELECT id_colegio FROM colegio WHERE nombre='Colegio Oficial de Ingenieria Informatica de Asturias'),
    (SELECT id_profesor FROM profesor WHERE email='raquel@colegio.es'),
    'Administración de BBDD Neo4J',
    'Formación práctica en Neo4J',
    'Modelo de grafos, Cypher, indexación',
    750.0,
    '2025-12-26','2025-12-30','Sede COIIPA, Oviedo',
    '2025-12-01','2025-12-21',
    0, 400.0, 4
);

-- 2) Scrum Master
INSERT INTO actividad (
    id_colegio, id_profesor, nombre, objetivos, contenidos, remuneracion,
    fecha_inicio, fecha_fin, lugar,
    fecha_apertura_inscripcion, fecha_cierre_inscripcion,
    gratuita, cuota, plazas
) VALUES (
    (SELECT id_colegio FROM colegio WHERE nombre='Colegio Oficial de Ingenieria Informatica de Castilla y León'),
    (SELECT id_profesor FROM profesor WHERE email='claudio@colegio.es'),
    'Scrum Master',
    'Marco Scrum y rol de Scrum Master',
    'Eventos, artefactos, métricas',
    1400.0,
    '2025-10-01','2025-10-08','Sede CPIICYL, Valladolid',
    '2025-09-01','2025-09-19',
    0, 500.0, 6
);

-- =======================
-- Inscripciones
-- =======================

-- Neo4J
INSERT INTO inscripcion (id_actividad, id_alumno, fecha)
SELECT a.id_actividad, al.id_alumno, '2025-12-01'
FROM actividad a
JOIN alumno al ON al.nombre='Alicia'
WHERE a.nombre='Administración de BBDD Neo4J';

INSERT INTO inscripcion (id_actividad, id_alumno, fecha)
SELECT a.id_actividad, al.id_alumno, '2025-12-01'
FROM actividad a
JOIN alumno al ON al.nombre='Juan'
WHERE a.nombre='Administración de BBDD Neo4J';

-- Scrum Master
INSERT INTO inscripcion (id_actividad, id_alumno, fecha)
SELECT a.id_actividad, al.id_alumno, '2025-09-01'
FROM actividad a
JOIN alumno al ON al.nombre='Alicia'
WHERE a.nombre='Scrum Master';

INSERT INTO inscripcion (id_actividad, id_alumno, fecha)
SELECT a.id_actividad, al.id_alumno, '2025-09-03'
FROM actividad a
JOIN alumno al ON al.nombre='Juan'
WHERE a.nombre='Scrum Master';

INSERT INTO inscripcion (id_actividad, id_alumno, fecha)
SELECT a.id_actividad, al.id_alumno, '2025-09-03'
FROM actividad a
JOIN alumno al ON al.nombre='Mónica'
WHERE a.nombre='Scrum Master';

INSERT INTO inscripcion (id_actividad, id_alumno, fecha)
SELECT a.id_actividad, al.id_alumno, '2025-09-10'
FROM actividad a
JOIN alumno al ON al.nombre='Pablo'
WHERE a.nombre='Scrum Master';

-- =======================
-- Movimientos (ingresos/gastos)
-- =======================

-- Neo4J: ingresos (Alicia y Juan)
INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado, id_alumno)
SELECT a.id_actividad, 'ingreso','2025-12-02', 300.0, 'Pago Alicia (parcial)', 'alumno', 1,
       al.id_alumno
FROM actividad a
JOIN alumno   al ON al.nombre='Alicia'
WHERE a.nombre='Administración de BBDD Neo4J';

INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado, id_alumno)
SELECT a.id_actividad, 'ingreso','2025-12-01', 100.0, 'Pago Juan (1º parcial)', 'alumno', 1,
       al.id_alumno
FROM actividad a
JOIN alumno   al ON al.nombre='Juan'
WHERE a.nombre='Administración de BBDD Neo4J';

INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado, id_alumno)
SELECT a.id_actividad, 'ingreso','2025-12-02', 100.0, 'Pago Juan (2º parcial por aviso)', 'alumno', 1,
       al.id_alumno
FROM actividad a
JOIN alumno   al ON al.nombre='Juan'
WHERE a.nombre='Administración de BBDD Neo4J';

-- Scrum Master: ingresos (Alicia, Juan, Mónica, Pablo)
INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado, id_alumno)
SELECT a.id_actividad, 'ingreso','2025-09-04', 550.0, 'Pago Alicia', 'alumno', 1,
       al.id_alumno
FROM actividad a
JOIN alumno   al ON al.nombre='Alicia'
WHERE a.nombre='Scrum Master';

INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado, id_alumno)
SELECT a.id_actividad, 'ingreso','2025-09-04', 500.0, 'Pago Juan', 'alumno', 1,
       al.id_alumno
FROM actividad a
JOIN alumno   al ON al.nombre='Juan'
WHERE a.nombre='Scrum Master';

INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado, id_alumno)
SELECT a.id_actividad, 'ingreso','2025-09-04', 500.0, 'Pago Mónica', 'alumno', 1,
       al.id_alumno
FROM actividad a
JOIN alumno   al ON al.nombre='Mónica'
WHERE a.nombre='Scrum Master';

INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado, id_alumno)
SELECT a.id_actividad, 'ingreso','2025-09-10', 500.0, 'Pago Pablo', 'alumno', 1,
       al.id_alumno
FROM actividad a
JOIN alumno   al ON al.nombre='Pablo'
WHERE a.nombre='Scrum Master';

-- Scrum Master: gastos (gasto NEGATIVO, asociado al profesor de la actividad)
INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado, id_profesor)
SELECT a.id_actividad, 'gasto','2025-10-13', -1500.0, 'Pago profesor', 'profesor', 1,
       p.id_profesor
FROM actividad a
JOIN profesor p ON p.id_profesor = a.id_profesor
WHERE a.nombre='Scrum Master';
