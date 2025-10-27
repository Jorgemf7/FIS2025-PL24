-- ============================================================
--  DATOS INICIALES PARA EL MÓDULO DE FORMACIÓN
-- ============================================================

-- ============================================================
--  1. COLEGIOS
-- ============================================================
INSERT INTO colegio (nombre, provincia, email_contacto) VALUES
('Colegio Oficial de Ingenieria Informatica de Asturias', 'Asturias', 'contacto@coiia.es'),
('Colegio Oficial de Ingenieria Informatica de Galicia', 'Galicia', 'info@coiig.gal'),
('Colegio Oficial de Ingenieria Informatica de Cantabria', 'Cantabria', 'info@coiican.es'),
('Colegio Oficial de Ingenieria Informatica de Castilla y León', 'Castilla y León', 'info@coiicl.es');

-- ============================================================
--  2. PROFESORES
-- ============================================================
INSERT INTO profesor (nombre, apellidos, email, telefono, remuneracion_base) VALUES
('Laura', 'Fernandez', 'laura.fernandez@uniovi.es', '600111222', 400.0),
('Carlos', 'Vazquez',   'carlos.vazquez@udc.es',    '600333444', 350.0),
('Ana', 'Rodríguez',    'ana.rodriguez@uco.es',     '600555666', 420.0),
('Javier', 'Pérez',     'javier.perez@usal.es',     '600777888', 380.0);

-- ============================================================
--  3. ACTIVIDADES FORMATIVAS
-- ============================================================

-- (1) INSCRIPCIÓN ABIERTA
INSERT INTO actividad (
    id_colegio, id_profesor, nombre, objetivos, contenidos, remuneracion,
    fecha_inicio, fecha_fin, lugar,
    fecha_apertura_inscripcion, fecha_cierre_inscripcion,
    gratuita, cuota
) VALUES
(1, 1, 'Introducción a la Inteligencia Artificial',
 'Ofrecer una visión general de IA aplicada a la ingeniería.',
 'Machine Learning, Deep Learning, Casos prácticos',
 500.0, '2025-11-10', '2025-11-12', 'Sede COIIPA, Oviedo',
 '2025-10-10', '2025-11-05', 0, 50.0);

-- (2) PLANIFICADO
INSERT INTO actividad (
    id_colegio, id_profesor, nombre, objetivos, contenidos, remuneracion,
    fecha_inicio, fecha_fin, lugar,
    fecha_apertura_inscripcion, fecha_cierre_inscripcion,
    gratuita, cuota
) VALUES
(2, 2, 'Buenas Prácticas en DevOps',
 'Actualizar competencias en CI/CD para profesionales.',
 'Pipelines, Testing, Observabilidad',
 450.0, '2025-12-02', '2025-12-02', 'Sede COG',
 '2025-11-01', '2025-11-28', 1, 0.0);

-- (3) EN CURSO
INSERT INTO actividad (
    id_colegio, id_profesor, nombre, objetivos, contenidos, remuneracion,
    fecha_inicio, fecha_fin, lugar,
    fecha_apertura_inscripcion, fecha_cierre_inscripcion,
    gratuita, cuota
) VALUES
(1, 1, 'Arquitecturas de Microservicios',
 'Patrones y mejores prácticas en sistemas distribuidos.',
 'Descomposición, API Gateway, Observabilidad, Resiliencia',
 520.0, '2025-10-21', '2025-10-23', 'Sede COIIPA, Oviedo',
 '2025-09-25', '2025-10-18', 0, 60.0);

-- (4) CERRADO
INSERT INTO actividad (
    id_colegio, id_profesor, nombre, objetivos, contenidos, remuneracion,
    fecha_inicio, fecha_fin, lugar,
    fecha_apertura_inscripcion, fecha_cierre_inscripcion,
    gratuita, cuota
) VALUES
(2, 2, 'Introducción a SQL',
 'Fundamentos de SQL para analistas de datos.',
 'SELECT, JOIN, GROUP BY, índices',
 300.0, '2025-09-10', '2025-09-10', 'Sede COG',
 '2025-08-10', '2025-09-07', 0, 30.0);

-- (5) PLANIFICADO
INSERT INTO actividad (
    id_colegio, id_profesor, nombre, objetivos, contenidos, remuneracion,
    fecha_inicio, fecha_fin, lugar,
    fecha_apertura_inscripcion, fecha_cierre_inscripcion,
    gratuita, cuota
) VALUES
(3, 3, 'Seguridad en la Nube',
 'Buenas prácticas en seguridad cloud.',
 'IAM, Cifrado, Cumplimiento, Auditoría',
 550.0, '2025-12-15', '2025-12-16', 'Sede COIICAN, Santander',
 '2025-11-25', '2025-12-10', 0, 65.0);

-- (6) INSCRIPCIÓN ABIERTA
INSERT INTO actividad (
    id_colegio, id_profesor, nombre, objetivos, contenidos, remuneracion,
    fecha_inicio, fecha_fin, lugar,
    fecha_apertura_inscripcion, fecha_cierre_inscripcion,
    gratuita, cuota
) VALUES
(4, 4, 'Docker Avanzado',
 'Profundizar en contenedores y despliegues modernos.',
 'Dockerfile avanzado, multi-stage, redes, rendimiento',
 480.0, '2025-12-05', '2025-12-06', 'Sede COIICL, Valladolid',
 '2025-10-15', '2025-11-30', 0, 70.0);

-- (7) EN CURSO
INSERT INTO actividad (
    id_colegio, id_profesor, nombre, objetivos, contenidos, remuneracion,
    fecha_inicio, fecha_fin, lugar,
    fecha_apertura_inscripcion, fecha_cierre_inscripcion,
    gratuita, cuota
) VALUES
(1, 3, 'Data Science con Python',
 'Curso intensivo en análisis de datos con Python y librerías científicas.',
 'Pandas, NumPy, Scikit-learn, Matplotlib',
 600.0, '2025-10-20', '2025-10-24', 'Sede COIIPA, Oviedo',
 '2025-09-25', '2025-10-18', 0, 80.0);

-- (8) CERRADO
INSERT INTO actividad (
    id_colegio, id_profesor, nombre, objetivos, contenidos, remuneracion,
    fecha_inicio, fecha_fin, lugar,
    fecha_apertura_inscripcion, fecha_cierre_inscripcion,
    gratuita, cuota
) VALUES
(3, 4, 'Introducción a Redes Neuronales',
 'Taller introductorio sobre Deep Learning y frameworks actuales.',
 'Perceptrones, TensorFlow, PyTorch',
 400.0, '2025-09-05', '2025-09-06', 'Sede COIICAN, Santander',
 '2025-08-01', '2025-09-01', 1, 0.0);

-- ============================================================
--  4. MOVIMIENTOS ECONÓMICOS
--  (ajustados a las reglas: ingresos > 0, gastos < 0, fecha dentro del periodo)
--  columnas: id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado
-- ============================================================

-- Actividad 1 (INSCRIPCIÓN ABIERTA, 2025-11-10..12)
INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado) VALUES
(1,'ingreso','2025-11-10',  600.00,'Matrículas confirmadas','alumno',1),
(1,'gasto'  ,'2025-11-11', -280.00,'Honorarios profesor','profesor',1),
(1,'gasto'  ,'2025-11-12',  -50.00,'Material didáctico','otro',1),
(1,'ingreso','2025-11-12',  100.00,'Inscripciones de última hora','alumno',0);

-- Actividad 2 (PLANIFICADO, 2025-12-02)
INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado) VALUES
(2,'ingreso','2025-12-02',  400.00,'Preinscripciones (día del curso)','alumno',0),
(2,'gasto'  ,'2025-12-02', -150.00,'Material (presupuesto)','otro',0);

-- Actividad 3 (EN CURSO, 2025-10-21..23)
INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado) VALUES
(3,'ingreso','2025-10-21',  380.00,'Matrículas confirmadas (primer corte)','alumno',1),
(3,'gasto'  ,'2025-10-22', -150.00,'Alquiler aula','otro',1),
(3,'ingreso','2025-10-23',  120.00,'Inscripciones en curso','alumno',0);

-- Actividad 4 (CERRADO, 2025-09-10)
INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado) VALUES
(4,'ingreso','2025-09-10',  420.00,'Matrículas confirmadas','alumno',1),
(4,'gasto'  ,'2025-09-10', -180.00,'Honorarios profesor','profesor',1),
(4,'gasto'  ,'2025-09-10',  -40.00,'Material','otro',1);

-- Actividad 5 (PLANIFICADO, 2025-12-15..16)
INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado) VALUES
(5,'ingreso','2025-12-15',  300.00,'Preinscripciones estimadas','alumno',0),
(5,'gasto'  ,'2025-12-16', -220.00,'Aula (presupuesto)','otro',0);

-- Actividad 6 (INSCRIPCIÓN ABIERTA, 2025-12-05..06)
INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado) VALUES
(6,'ingreso','2025-12-05',  210.00,'Matrículas confirmadas (tempranas)','alumno',1),
(6,'ingreso','2025-12-06',  140.00,'Matrículas previstas','alumno',0),
(6,'gasto'  ,'2025-12-06', -120.00,'Material (presupuesto)','otro',0);

-- Actividad 7 (EN CURSO, 2025-10-20..24)
INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado) VALUES
(7,'ingreso','2025-10-20',  700.00,'Inscripciones confirmadas','alumno',1),
(7,'gasto'  ,'2025-10-21', -300.00,'Profesorado y materiales','profesor',1),
(7,'ingreso','2025-10-24',  100.00,'Pagos pendientes','alumno',0);

-- Actividad 8 (CERRADO, 2025-09-05..06)
INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, categoria, confirmado) VALUES
(8,'ingreso','2025-09-05',  350.00,'Inscripciones confirmadas','alumno',1),
(8,'gasto'  ,'2025-09-06', -220.00,'Gastos del evento','otro',1);

-- ============================================================
-- FIN DE LOS DATOS INICIALES
-- ============================================================
