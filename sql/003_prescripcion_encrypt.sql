-- ─────────────────────────────────────────────────────────────────────────────
-- 003_prescripcion_encrypt.sql
-- Modifica columnas sensibles de `prescripcion` a BLOB para encriptación AES-256-GCM
-- Ejecutar como: mysql -u med_admin -p gesmed < 003_prescripcion_encrypt.sql
-- ─────────────────────────────────────────────────────────────────────────────

ALTER TABLE prescripcion
    MODIFY COLUMN concentracion BLOB NOT NULL,
    MODIFY COLUMN indicaciones  BLOB NOT NULL;
