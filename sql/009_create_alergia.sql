-- 009_create_alergia.sql
-- Alergias conocidas del paciente.
CREATE TABLE IF NOT EXISTS alergia (
    id_alergia        INT(11)      NOT NULL AUTO_INCREMENT,
    lk_paciente       INT(11)      NOT NULL,
    sustancia_alergia VARCHAR(100) NOT NULL,
    detalles          TEXT         DEFAULT NULL,
    fecha_reportada   DATE         DEFAULT NULL,
    PRIMARY KEY (id_alergia),
    KEY fk_alergia_paciente (lk_paciente),
    CONSTRAINT fk_alergia_paciente FOREIGN KEY (lk_paciente) REFERENCES paciente (nro_hclinica)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
