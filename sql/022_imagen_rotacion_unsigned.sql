-- Migración 022: ampliar columna rotacion de TINYINT a TINYINT UNSIGNED
-- Motivo: TINYINT con signo solo llega a 127; los valores 180 y 270 desbordan.

ALTER TABLE imagen
    MODIFY COLUMN rotacion TINYINT UNSIGNED NOT NULL DEFAULT 0
    COMMENT '0|90|180|270 — nunca modifica el JPG físico';
