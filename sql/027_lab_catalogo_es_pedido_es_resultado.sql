ALTER TABLE examenes_laboratorio_catalogo
    ADD COLUMN es_pedido    TINYINT(1) NULL DEFAULT 1,
    ADD COLUMN es_resultado TINYINT(1) NULL DEFAULT 1,
    ADD COLUMN lk_padre     INT        NULL DEFAULT NULL,
    ADD CONSTRAINT fk_lab_catalogo_padre
        FOREIGN KEY (lk_padre) REFERENCES examenes_laboratorio_catalogo(id_examen)
        ON DELETE SET NULL;
