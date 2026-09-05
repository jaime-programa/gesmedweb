-- ============================================================
-- 017_fix_fk_geodata_to_gesmed.sql
-- Corrige las FK de atencion y diagnostico que apuntaban a
-- geodata.points (tabla de credenciales oculta, ya en desuso).
-- Ahora todas las referencias apuntan a gesmed.points.
--
-- Verificar nombres de constraintS antes de correr:
--   SHOW CREATE TABLE atencion\G
--   SHOW CREATE TABLE diagnostico\G
-- ============================================================

-- ── atencion ────────────────────────────────────────────────
-- FK: lk_medico → geodata.points.id_medico
-- Nombre auto-asignado por MariaDB: atencion_ibfk_2
ALTER TABLE atencion
    DROP FOREIGN KEY atencion_ibfk_2;

ALTER TABLE atencion
    ADD CONSTRAINT atencion_ibfk_2
        FOREIGN KEY (lk_medico)
        REFERENCES gesmed.points (id_medico)
        ON UPDATE CASCADE;

-- ── diagnostico ─────────────────────────────────────────────
-- FK: lk_medico → geodata.points.id_medico
-- Nombre confirmado en el error: diagnostico_ibfk_3
ALTER TABLE diagnostico
    DROP FOREIGN KEY diagnostico_ibfk_3;

ALTER TABLE diagnostico
    ADD CONSTRAINT diagnostico_ibfk_3
        FOREIGN KEY (lk_medico)
        REFERENCES gesmed.points (id_medico)
        ON UPDATE CASCADE;

-- Nota: las tablas horario_medico, bloqueo_horario y cita
-- fueron creadas en la migración 015 con REFERENCES points(id_medico)
-- dentro del contexto de gesmed, por lo tanto ya apuntan a gesmed.points
-- y no necesitan corrección.
