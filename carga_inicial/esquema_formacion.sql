-- Reset
DROP TABLE IF EXISTS movimiento;
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
    CHECK (date(fecha_inicio) <= date(fecha_fin)),
    CHECK (date(fecha_apertura_inscripcion) <= date(fecha_cierre_inscripcion)),
    CHECK (date(fecha_cierre_inscripcion) <= date(fecha_inicio)),
    CHECK ( (gratuita = 1 AND cuota = 0) OR (gratuita = 0 AND cuota >= 0) ),
    UNIQUE(id_colegio, nombre),
    FOREIGN KEY (id_colegio)  REFERENCES colegio(id_colegio),
    FOREIGN KEY (id_profesor) REFERENCES profesor(id_profesor)
);

-- Movimientos económicos por actividad formativa
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

CREATE TABLE IF NOT EXISTS alerta_pago (
    id_alerta       INTEGER PRIMARY KEY AUTOINCREMENT,
    id_actividad    INTEGER NOT NULL,
    id_movimiento   INTEGER,                         -- opcional: referencia al movimiento implicado
    tipo_incidente  TEXT NOT NULL                    -- 'importe_incorrecto' | 'duplicado' | 'pendiente_fuera_plazo'
                  CHECK (tipo_incidente IN ('importe_incorrecto','duplicado','pendiente_fuera_plazo')),
    descripcion     TEXT NOT NULL,
    alumno_ref      TEXT,                            -- opcional (no hay tabla de alumnos)
    estado          TEXT NOT NULL DEFAULT 'pendiente' -- 'pendiente' | 'en_revision' | 'resuelta'
                  CHECK (estado IN ('pendiente','en_revision','resuelta')),
    fecha_generacion TEXT NOT NULL DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (id_actividad)  REFERENCES actividad(id_actividad)  ON DELETE CASCADE,
    FOREIGN KEY (id_movimiento) REFERENCES movimiento(id_movimiento) ON DELETE CASCADE
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_mov_actividad ON movimiento(id_actividad);
CREATE INDEX IF NOT EXISTS idx_mov_fecha     ON movimiento(fecha);
CREATE INDEX IF NOT EXISTS idx_mov_tipo      ON movimiento(tipo);
CREATE INDEX IF NOT EXISTS idx_alerta_estado ON alerta_pago(estado);
CREATE INDEX IF NOT EXISTS idx_alerta_actividad ON alerta_pago(id_actividad);

-- Antiduplicados
CREATE UNIQUE INDEX IF NOT EXISTS ux_mov_no_duplicados
ON movimiento(id_actividad, fecha, tipo, importe, IFNULL(descripcion,''), categoria);

-- Evita alertas duplicadas para el mismo hecho (si ya existe una igual, no crear otra)
-- Clave de idempotencia: (tipo, actividad, movimiento?, alumno_ref)
CREATE UNIQUE INDEX IF NOT EXISTS ux_alerta_pago_unica
ON alerta_pago (tipo_incidente, id_actividad, IFNULL(id_movimiento,-1), IFNULL(alumno_ref,''));