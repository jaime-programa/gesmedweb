-- Migración 023: ampliar columna rotacion de TINYINT UNSIGNED a SMALLINT
-- Motivo: TINYINT UNSIGNED llega a 255; el valor 270 (tercera rotación) desborda.

ALTER TABLE imagen
    MODIFY COLUMN rotacion SMALLINT NOT NULL DEFAULT 0
    COMMENT '0|90|180|270 — nunca modifica el JPG físico';
