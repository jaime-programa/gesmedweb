-- agregar_fks_faltantes.sql — agrega las 2 FK que mis_modelos.py declara
-- pero que faltan como CONSTRAINT real en la base de datos gesmed.
--
-- Detectado por migrations/verificar_estructura.py. Verificado sin filas
-- huérfanas antes de aplicar (0 en ambos casos).

ALTER TABLE medicamentos
    ADD CONSTRAINT fk_medicamentos_tipo
    FOREIGN KEY (tipo) REFERENCES medicamento_tipo (id_tipo);

ALTER TABLE examenes_laboratorio_pedido
    ADD CONSTRAINT fk_examenes_laboratorio_pedido_atencion
    FOREIGN KEY (lk_atencion) REFERENCES atencion (id_atencion);
