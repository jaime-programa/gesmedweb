-- ─────────────────────────────────────────────────────────────────────────────
-- 002_diagnostico_encrypt.sql
-- Modifica columna sensible de `diagnostico` a BLOB para encriptación AES-256-GCM
-- Ejecutar como: mysql -u med_admin -p gesmed < 002_diagnostico_encrypt.sql
-- ─────────────────────────────────────────────────────────────────────────────

ALTER TABLE diagnostico
    MODIFY COLUMN observaciones BLOB DEFAULT NULL;
