
-- Datos iniciales
INSERT INTO colegio (nombre, provincia, email_contacto) VALUES
('Colegio Oficial de Ingenieria Informatica de Asturias', 'Asturias', 'contacto@coiia.es'),
('Colegio Oficial de Ingenieria Informatica de Galicia', 'Galicia', 'info@coiig.gal');

INSERT INTO profesor (nombre, apellidos, email, telefono, remuneracion_base) VALUES
('Laura', 'Fernandez', 'laura.fernandez@uniovi.es', '600111222', 400.0),
('Carlos', 'Vazquez',   'carlos.vazquez@udc.es',    '600333444', 350.0);

-- Una actividad gratuita y otra con cuota
INSERT INTO actividad (
    id_colegio, id_profesor, nombre, objetivos, contenidos, remuneracion,
    fecha_inicio, fecha_fin, lugar, fecha_apertura_inscripcion, fecha_cierre_inscripcion cuota
) VALUES
(1, 1, 'Introduccion a la IA',
 'Ofrecer una vision general de IA aplicada a la ingenieria.',
 'ML, DL, casos practicos',
 500.0, '2025-11-10', '2025-11-12', 'Sede COIIPA, Oviedo', '2025-10-10', '2025-11-05',  50.0),
(2, 2, 'Buenas practicas en DevOps',
 'Actualizar competencias en CI/CD para profesionales.',
 'Pipelines, testing, observabilidad',
 450.0, '2025-12-02', '2025-12-02', 'Sede COG', '2025-11-01', '2025-11-28',  0.0);
