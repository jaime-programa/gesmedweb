-- Permite NULL en lk_paciente para diagnostico y prescripcion.
-- Necesario en migración desde amaymed que no almacena el FK de paciente en estas tablas.
ALTER TABLE diagnostico  MODIFY lk_paciente INT NULL DEFAULT NULL;
ALTER TABLE prescripcion MODIFY lk_paciente INT NULL DEFAULT NULL;

-- Amplía noduplicados: en amaymed incluye el nombre del paciente (texto largo).
ALTER TABLE diagnostico MODIFY noduplicados VARCHAR(300) NOT NULL DEFAULT '';

-- lk_presentacion y lk_generico son Optional en el modelo pero NOT NULL en BD.
ALTER TABLE prescripcion MODIFY lk_presentacion INT NULL DEFAULT NULL;
ALTER TABLE prescripcion MODIFY lk_generico     INT NULL DEFAULT NULL;

-- atencion: lk_paciente puede quedar NULL si no se resuelve desde amaymed.
ALTER TABLE atencion MODIFY lk_paciente INT NULL DEFAULT NULL;

-- rel_atencion_diagnostico: gesmed tiene varchar(18) pero amaymed tiene varchar(20).
ALTER TABLE rel_atencion_diagnostico MODIFY noduplicarelacion VARCHAR(20) NOT NULL DEFAULT '';
