-- ─────────────────────────────────────────────────────────────────────────────
-- 001_paciente_encrypt.sql
-- Modifica columnas sensibles de `paciente` a BLOB para encriptación AES-256-GCM
--
-- PRERREQUISITO: ejecutar mysqldump antes de correr este script.
--   mysqldump -u med_admin -p gesmed > backup_gesmed_YYYYMMDD.sql
--
-- NOTA: los datos existentes quedan en las columnas con su tipo cambiado.
--   El orquestador trunca y re-puebla la tabla con datos cifrados desde amaymed.
--
-- Ejecutar como: mysql -u med_admin -p gesmed < 001_paciente_encrypt.sql
-- ─────────────────────────────────────────────────────────────────────────────

ALTER TABLE paciente
    MODIFY COLUMN nombre_completo BLOB        NOT NULL,
    MODIFY COLUMN cedula_id       BLOB        DEFAULT NULL;
