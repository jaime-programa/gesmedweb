-- 005_create_medicamento_tipo.sql
-- Tabla de clasificación de medicamentos.
-- Tipo 1 = catálogo oficial, Tipo 2 = añadido en consulta por el médico.
CREATE TABLE IF NOT EXISTS medicamento_tipo (
    id_tipo      INT(2)       NOT NULL AUTO_INCREMENT,
    nombre_tipo  VARCHAR(20)  NOT NULL,
    PRIMARY KEY (id_tipo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Seed inicial (INSERT IGNORE evita error si ya existen)
INSERT IGNORE INTO medicamento_tipo (id_tipo, nombre_tipo) VALUES
    (1, 'catalogo'),
    (2, 'añadido');
