-- 011_migrate_signosvitales.sql
-- Reemplaza la tabla signosvitales de columnas fijas por un modelo EAV.
--
-- La tabla anterior (10 columnas fijas) se renombra a signosvitales_old
-- como respaldo antes de eliminarla.  Si no hay datos que conservar puedes
-- ejecutar: DROP TABLE IF EXISTS signosvitales_old;
--
-- Ejecutar DESPUÉS de 010_create_lista_signosvitales.sql.
-- Requiere que la tabla 'atencion' ya exista.

-- ── 1. Backup de la tabla anterior ───────────────────────────────────────────
-- Si signosvitales_old ya existe de una ejecución anterior, la borramos primero.
DROP TABLE IF EXISTS signosvitales_old;

-- Renombrar solo si la tabla original todavía tiene la estructura de columnas fijas.
-- El RENAME falla silenciosamente si signosvitales no existe; usamos un bloque
-- condicional con procedimiento para hacerlo seguro.
DROP PROCEDURE IF EXISTS _migra_sv;
DELIMITER $$
CREATE PROCEDURE _migra_sv()
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.COLUMNS
        WHERE table_schema = DATABASE()
          AND table_name   = 'signosvitales'
          AND column_name  = 'peso_kg'        -- columna propia del modelo viejo
    ) THEN
        RENAME TABLE signosvitales TO signosvitales_old;
    END IF;
END$$
DELIMITER ;
CALL _migra_sv();
DROP PROCEDURE IF EXISTS _migra_sv;

-- ── 2. Nueva tabla EAV ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS signosvitales (
    id              INT(11)      NOT NULL AUTO_INCREMENT,
    lk_atencion     INT(11)      NOT NULL,
    lk_signo_vital  INT(11)      NOT NULL,
    valor           DECIMAL(6,2) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_atencion_signo (lk_atencion, lk_signo_vital),
    KEY fk_sv_atencion    (lk_atencion),
    KEY fk_sv_tipo        (lk_signo_vital),
    CONSTRAINT fk_sv_atencion   FOREIGN KEY (lk_atencion)    REFERENCES atencion          (id_atencion),
    CONSTRAINT fk_sv_tipo       FOREIGN KEY (lk_signo_vital) REFERENCES lista_signosvitales (id_signo_vital)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
