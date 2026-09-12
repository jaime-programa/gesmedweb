-- ============================================================
-- 029_interconsulta.sql
-- Módulo de Interconsulta: permite que un médico auxiliar acceda
-- temporalmente a un paciente de otro médico (principal) para
-- registrar atenciones, sin cambiar la "propiedad" del paciente.
--
-- 2 tablas:
--   solicitud_interconsulta: habilita el acceso de un médico auxiliar
--     a UN paciente puntual, mientras esté vigente (estatus='activa'
--     y fecha_expiracion no vencida). La cierra automáticamente el
--     backend (chequeo perezoso) o el médico auxiliar de forma manual.
--   interconsulta: registra, por cada atención puntual generada por
--     el auxiliar, la autoría — constancia histórica permanente, no
--     depende de que la solicitud siga vigente.
-- ============================================================

CREATE TABLE IF NOT EXISTS solicitud_interconsulta (
    id_solicitud        INT          AUTO_INCREMENT PRIMARY KEY,
    lk_paciente         INT          NOT NULL,
    lk_medico_principal INT          NOT NULL,
    lk_medico_auxiliar  INT          NOT NULL,
    fecha_solicitud     DATE         NOT NULL,
    fecha_expiracion    DATE         NOT NULL,
    motivo              TEXT         NOT NULL,
    estatus             VARCHAR(10)  NOT NULL DEFAULT 'activa'
        COMMENT 'activa | finalizada',
    FOREIGN KEY (lk_paciente)         REFERENCES paciente(nro_hclinica) ON DELETE CASCADE,
    FOREIGN KEY (lk_medico_principal) REFERENCES points(id_medico),
    FOREIGN KEY (lk_medico_auxiliar)  REFERENCES points(id_medico)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS interconsulta (
    id_interconsulta   INT  AUTO_INCREMENT PRIMARY KEY,
    lk_atencion         INT  NOT NULL,
    lk_medico_auxiliar  INT  NOT NULL,
    reporte_final       TEXT NULL,
    FOREIGN KEY (lk_atencion)        REFERENCES atencion(id_atencion) ON DELETE CASCADE,
    FOREIGN KEY (lk_medico_auxiliar) REFERENCES points(id_medico)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
