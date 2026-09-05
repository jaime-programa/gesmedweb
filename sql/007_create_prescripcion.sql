-- 007_create_prescripcion.sql
-- Ítems de prescripción (un registro por medicamento prescrito).
-- concentracion e indicaciones nacen como BLOB (encriptados desde el inicio).
-- Ejecutar DESPUÉS de 006_create_medicamento_presentacion.sql.
CREATE TABLE IF NOT EXISTS prescripcion (
    id_prescripcion    INT(11)  NOT NULL AUTO_INCREMENT,
    lk_paciente        INT(11)  DEFAULT NULL,
    lk_atencion        INT(11)  DEFAULT NULL,
    fecha_prescripcion DATE     NOT NULL,
    concentracion      BLOB     NOT NULL,
    cantidad           INT(3)   NOT NULL DEFAULT 1,
    lk_presentacion    INT(11)  DEFAULT NULL,
    indicaciones       BLOB     NOT NULL,
    lk_generico        INT(11)  DEFAULT NULL,
    PRIMARY KEY (id_prescripcion),
    KEY fk_px_paciente    (lk_paciente),
    KEY fk_px_atencion    (lk_atencion),
    KEY fk_px_presentacion (lk_presentacion),
    KEY fk_px_generico    (lk_generico),
    CONSTRAINT fk_px_paciente     FOREIGN KEY (lk_paciente)     REFERENCES paciente                (nro_hclinica),
    CONSTRAINT fk_px_atencion     FOREIGN KEY (lk_atencion)     REFERENCES atencion                (id_atencion),
    CONSTRAINT fk_px_presentacion FOREIGN KEY (lk_presentacion) REFERENCES medicamento_presentacion (id_presentacion),
    CONSTRAINT fk_px_generico     FOREIGN KEY (lk_generico)     REFERENCES medicamentos             (cod_gen)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
