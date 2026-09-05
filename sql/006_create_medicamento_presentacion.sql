-- 006_create_medicamento_presentacion.sql
-- Formas farmacéuticas / presentaciones (cápsulas, comprimidos, ampollas, etc.)
CREATE TABLE IF NOT EXISTS medicamento_presentacion (
    id_presentacion      INT(11)      NOT NULL AUTO_INCREMENT,
    nombre_presentacion  VARCHAR(30)  NOT NULL,
    en_uso               TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id_presentacion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
