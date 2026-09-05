-- ─────────────────────────────────────────────────────────────────────────────
-- 003_prescripcion_revert.sql
-- Revierte columnas de `prescripcion` a sus tipos originales.
-- ADVERTENCIA: los datos cifrados quedarán ilegibles. Restaurar backup de datos.
-- ─────────────────────────────────────────────────────────────────────────────

ALTER TABLE prescripcion
    MODIFY COLUMN concentracion VARCHAR(30) NOT NULL,
    MODIFY COLUMN indicaciones  TEXT        NOT NULL;
