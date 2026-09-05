-- 008_create_prescripcion_cuidados.sql
-- Encabezado de prescripción: cuidados generales para toda la receta.
-- Una sola fila por atención (UNIQUE en lk_atencion).
CREATE TABLE IF NOT EXISTS prescripcion_cuidados (
    id_cuidados        INT(11)  NOT NULL AUTO_INCREMENT,
    lk_atencion        INT(11)  NOT NULL,
    cuidados_generales TEXT     DEFAULT NULL,
    fecha_emision      DATE     DEFAULT NULL,
    PRIMARY KEY (id_cuidados),
    UNIQUE KEY uk_cuidados_atencion (lk_atencion),
    CONSTRAINT fk_cuidados_atencion FOREIGN KEY (lk_atencion) REFERENCES atencion (id_atencion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
