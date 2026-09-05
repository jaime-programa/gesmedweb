-- ============================================================
-- 021_imagen_rotacion.sql
-- Añade rotación temporal a imagen, formaliza tipo texto en marca
-- y agrega trazabilidad OCR en resultados_laboratorio.
-- Parche sobre BD que ya tiene 018, 019 y 020 aplicados.
-- ============================================================

--ALTER TABLE imagen
    ADD COLUMN rotacion TINYINT NOT NULL DEFAULT 0
        COMMENT 'Rotación visual en grados: 0 | 90 | 180 | 270 — no modifica el JPG';

-- Actualiza el comentario de tipo_marca para documentar el nuevo valor 't'
ALTER TABLE marca
    MODIFY COLUMN tipo_marca CHAR(1) NOT NULL DEFAULT 'c'
        COMMENT 'c=círculo  f=flecha  t=texto';

-- Trazabilidad: imagen escaneada que originó el valor extraído por OCR
ALTER TABLE resultados_laboratorio
    ADD COLUMN lk_imagen_fuente INT NULL
        COMMENT 'Imagen escaneada de la que se extrajo este valor (trazabilidad OCR)',
    ADD CONSTRAINT fk_reslab_imagen
        FOREIGN KEY (lk_imagen_fuente) REFERENCES imagen (id_imagen);
