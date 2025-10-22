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
-- ============================================================

-- Actividad 1 (INSCRIPCIÓN ABIERTA)
INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, confirmado) VALUES
(1,'ingreso','2025-10-15', 600.00,'Matrículas confirmadas',1),
(1,'gasto'  ,'2025-10-17', 280.00,'Honorarios profesor',1),
(1,'gasto'  ,'2025-10-19',  50.00,'Material didáctico',1),
(1,'ingreso','2025-10-20', 100.00,'Inscripciones pendientes',0);

-- Actividad 2 (PLANIFICADO)
INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, confirmado) VALUES
(2,'ingreso','2025-11-10', 400.00,'Preinscripciones estimadas',0),
(2,'gasto'  ,'2025-11-25', 150.00,'Material (presupuesto)',0);

-- Actividad 3 (EN CURSO)
INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, confirmado) VALUES
(3,'ingreso','2025-10-20', 380.00,'Matrículas confirmadas (primer corte)',1),
(3,'gasto'  ,'2025-10-21', 150.00,'Alquiler aula (confirmado)',1),
(3,'ingreso','2025-10-22', 120.00,'Inscripciones en curso (estimado)',0);

-- Actividad 4 (CERRADO)
INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, confirmado) VALUES
(4,'ingreso','2025-09-05', 420.00,'Matrículas confirmadas',1),
(4,'gasto'  ,'2025-09-09', 180.00,'Honorarios profesor',1),
(4,'gasto'  ,'2025-09-09',  40.00,'Material',1);

-- Actividad 5 (PLANIFICADO)
INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, confirmado) VALUES
(5,'ingreso','2025-11-30', 300.00,'Preinscripciones estimadas',0),
(5,'gasto'  ,'2025-12-14', 220.00,'Aula (presupuesto)',0);

-- Actividad 6 (INSCRIPCIÓN ABIERTA)
INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, confirmado) VALUES
(6,'ingreso','2025-10-18', 210.00,'Matrículas confirmadas (tempranas)',1),
(6,'ingreso','2025-10-25', 140.00,'Matrículas previstas (estimado)',0),
(6,'gasto'  ,'2025-11-15', 120.00,'Material (presupuesto)',0);

-- Actividad 7 (EN CURSO)
INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, confirmado) VALUES
(7,'ingreso','2025-10-20', 700.00,'Inscripciones confirmadas',1),
(7,'gasto'  ,'2025-10-21', 300.00,'Profesorado y materiales',1),
(7,'ingreso','2025-10-22', 100.00,'Pagos pendientes',0);

-- Actividad 8 (CERRADO)
INSERT INTO movimiento (id_actividad, tipo, fecha, importe, descripcion, confirmado) VALUES
(8,'ingreso','2025-09-03', 350.00,'Inscripciones confirmadas',1),
(8,'gasto'  ,'2025-09-06', 220.00,'Gastos del evento',1);

-- ============================================================
-- FIN DE LOS DATOS INICIALES
-- ============================================================
