-- 004_paciente_campos_extra_encrypt.sql
-- Cambia direccion_reside, tf_celular, email y observacion a BLOB.
-- Ejecutar ANTES de correr encrypt_existing_data.py.
ALTER TABLE paciente
  MODIFY COLUMN direccion_reside  BLOB         NOT NULL,
  MODIFY COLUMN tf_celular        BLOB         NOT NULL,
  MODIFY COLUMN email             BLOB         DEFAULT NULL,
  MODIFY COLUMN observacion       BLOB         DEFAULT NULL;
