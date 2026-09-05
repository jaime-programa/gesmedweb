-- 010_create_lista_signosvitales.sql
-- Catálogo de tipos de signo vital.
-- codigo: clave programática estable para referencias en Python (no usar id numérico).
-- orden_display: controla el orden del formulario desde la BD sin tocar código.
-- valor_min / valor_max: rango de validación clínica en backend.
-- Ejecutar ANTES de 011_migrate_signosvitales.sql.

CREATE TABLE IF NOT EXISTS lista_signosvitales (
    id_signo_vital  INT(11)      NOT NULL AUTO_INCREMENT,
    nombre          VARCHAR(60)  NOT NULL,
    codigo          VARCHAR(20)  NOT NULL,
    unidad          VARCHAR(20)  DEFAULT NULL,
    decimales       TINYINT      NOT NULL DEFAULT 1,
    valor_min       DECIMAL(6,2) DEFAULT NULL,
    valor_max       DECIMAL(6,2) DEFAULT NULL,
    orden_display   TINYINT      NOT NULL DEFAULT 99,
    es_activo       TINYINT      NOT NULL DEFAULT 1,
    PRIMARY KEY (id_signo_vital),
    UNIQUE KEY uq_codigo (codigo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Seed: 9 signos vitales básicos
INSERT IGNORE INTO lista_signosvitales
    (id_signo_vital, nombre, codigo, unidad, decimales, valor_min, valor_max, orden_display)
VALUES
    (1, 'Peso',               'PESO',  'kg',   2,   0.50, 300.00, 1),
    (2, 'Talla',              'TALLA', 'cm',   1,  30.00, 250.00, 2),
    (3, 'Temperatura',        'TEMP',  'ºC',   1,  30.00,  43.00, 3),
    (4, 'Perímetro Cefálico', 'PCEF',  'cm',   1,  20.00,  65.00, 4),
    (5, 'T.A. Sistólica',     'TAS',   'mmHg', 0,  50.00, 250.00, 5),
    (6, 'T.A. Diastólica',    'TAD',   'mmHg', 0,  30.00, 150.00, 6),
    (7, 'Frec. Cardíaca',     'FC',    'lpm',  0,  30.00, 300.00, 7),
    (8, 'Frec. Respiratoria', 'FR',    'rpm',  0,   8.00,  80.00, 8),
    (9, 'Saturación O₂',      'SAT',   '%',    1,  50.00, 100.00, 9);
