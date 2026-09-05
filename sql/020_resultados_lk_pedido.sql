-- ============================================================
-- 020_resultados_lk_pedido.sql
-- Vincula resultados con pedidos de exámenes de atenciones
-- anteriores (relación opcional, sin obligatoriedad).
--
-- Nota: 018 y 019 ya aplicados — este script agrega solo
-- los campos nuevos sobre las tablas existentes.
-- ============================================================

ALTER TABLE resultados_laboratorio
    ADD COLUMN lk_pedido INT NULL
        COMMENT 'Pedido de laboratorio de origen (opcional)',
    ADD CONSTRAINT fk_reslab_pedido
        FOREIGN KEY (lk_pedido)
        REFERENCES examenes_laboratorio_pedido (id_pedido);

ALTER TABLE resultados_imagen
    ADD COLUMN lk_pedido INT NULL
        COMMENT 'Pedido de imagen de origen (opcional)',
    ADD CONSTRAINT fk_resimg_pedido
        FOREIGN KEY (lk_pedido)
        REFERENCES examen_pedido (id_examen_pedido);
