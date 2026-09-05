-- 004_paciente_campos_extra_revert.sql
-- Revierte los campos de BLOB a sus tipos originales.
ALTER TABLE paciente
  MODIFY COLUMN direccion_reside  VARCHAR(255) NOT NULL DEFAULT '',
  MODIFY COLUMN tf_celular        VARCHAR(30)  NOT NULL DEFAULT '',
  MODIFY COLUMN email             VARCHAR(150) DEFAULT NULL,
  MODIFY COLUMN observacion       TEXT         DEFAULT NULL;
