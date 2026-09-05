-- ─────────────────────────────────────────────────────────────────────────────
-- 001_paciente_revert.sql
-- Revierte columnas de `paciente` a sus tipos originales.
-- ADVERTENCIA: los datos cifrados (BLOB) quedarán ilegibles como VARCHAR.
-- Usar solo si se restaura también el backup de datos plaintext.
-- ─────────────────────────────────────────────────────────────────────────────

ALTER TABLE paciente
    MODIFY COLUMN nombre_completo VARCHAR(120) NOT NULL,
    MODIFY COLUMN cedula_id       VARCHAR(20)  DEFAULT NULL;
