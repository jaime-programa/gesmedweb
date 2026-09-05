-- ─────────────────────────────────────────────────────────────────────────────
-- 002_diagnostico_revert.sql
-- Revierte columna `observaciones` de `diagnostico` a su tipo original.
-- ADVERTENCIA: los datos cifrados quedarán ilegibles. Restaurar backup de datos.
-- ─────────────────────────────────────────────────────────────────────────────

ALTER TABLE diagnostico
    MODIFY COLUMN observaciones MEDIUMTEXT DEFAULT NULL;
