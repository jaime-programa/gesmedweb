-- ============================================================
-- 015_agenda_medica.sql
-- Módulo de agenda / citas médicas
-- ============================================================

-- 1. Nuevas columnas en tabla points (médicos)
ALTER TABLE points
    ADD COLUMN modo_agenda   VARCHAR(5)   NOT NULL DEFAULT 'LIBRE'
        COMMENT 'FIJO = horario semanal fijo | LIBRE = sin horario base',
    ADD COLUMN color_agenda  VARCHAR(7)   NOT NULL DEFAULT '#3B82F6'
        COMMENT 'Color hex para distinguir al médico en el calendario',
    ADD COLUMN google_cal_id VARCHAR(200) NULL     DEFAULT NULL
        COMMENT 'Google Calendar ID del médico (para sync futuro)';

-- 2. Tipos de cita
CREATE TABLE IF NOT EXISTS tipo_cita (
    id_tipo_cita  INT AUTO_INCREMENT PRIMARY KEY,
    nombre        VARCHAR(60)  NOT NULL,
    categoria     VARCHAR(15)  NOT NULL DEFAULT 'CONSULTA'
        COMMENT 'CONSULTA | PROCEDIMIENTO | CIRUGIA',
    duracion_min  INT          NULL     DEFAULT 30
        COMMENT 'Minutos fijos. NULL para CIRUGIA (duración libre al agendar)',
    color_hex     VARCHAR(7)   NOT NULL DEFAULT '#3B82F6',
    requiere_conf TINYINT(1)   NOT NULL DEFAULT 0
        COMMENT '1 = requiere confirmación explícita antes de la cita',
    es_activo     TINYINT(1)   NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Horario semanal fijo por médico (solo aplica cuando modo_agenda = 'FIJO')
CREATE TABLE IF NOT EXISTS horario_medico (
    id_horario  INT     AUTO_INCREMENT PRIMARY KEY,
    lk_medico   INT     NOT NULL,
    dia_semana  TINYINT NOT NULL  COMMENT '0=Lun 1=Mar 2=Mié 3=Jue 4=Vie 5=Sáb 6=Dom',
    hora_inicio TIME    NOT NULL,
    hora_fin    TIME    NOT NULL,
    FOREIGN KEY (lk_medico) REFERENCES points(id_medico) ON DELETE CASCADE,
    UNIQUE KEY uq_medico_dia_inicio (lk_medico, dia_semana, hora_inicio)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Bloqueos de horario (vacaciones, feriados, ausencias puntuales)
CREATE TABLE IF NOT EXISTS bloqueo_horario (
    id_bloqueo   INT          AUTO_INCREMENT PRIMARY KEY,
    lk_medico    INT          NOT NULL,
    fecha_inicio DATETIME     NOT NULL,
    fecha_fin    DATETIME     NOT NULL,
    motivo       VARCHAR(200) NULL,
    FOREIGN KEY (lk_medico) REFERENCES points(id_medico) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Citas médicas
CREATE TABLE IF NOT EXISTS cita (
    id_cita         INT          AUTO_INCREMENT PRIMARY KEY,
    lk_paciente     INT          NULL
        COMMENT 'NULL cuando el paciente es nuevo y aún no tiene registro completo',
    lk_medico       INT          NOT NULL,
    lk_tipo_cita    INT          NOT NULL,
    inicio          DATETIME     NOT NULL,
    fin             DATETIME     NOT NULL,
    estado          VARCHAR(15)  NOT NULL DEFAULT 'AGENDADA'
        COMMENT 'AGENDADA | CONFIRMADA | COMPLETADA | CANCELADA | NO_ASISTIO',
    notas           TEXT         NULL,
    google_event_id VARCHAR(200) NULL,
    -- Datos mínimos del paciente nuevo (pendiente de completar registro)
    px_nombre       VARCHAR(150) NULL,
    px_sexo         VARCHAR(10)  NULL,
    px_celular      VARCHAR(20)  NULL,
    px_ciudad       VARCHAR(60)  NULL,
    px_seguro       VARCHAR(30)  NULL,
    FOREIGN KEY (lk_paciente)  REFERENCES paciente(nro_hclinica) ON DELETE SET NULL,
    FOREIGN KEY (lk_medico)    REFERENCES points(id_medico),
    FOREIGN KEY (lk_tipo_cita) REFERENCES tipo_cita(id_tipo_cita)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Datos iniciales de tipo_cita
INSERT INTO tipo_cita (nombre, categoria, duracion_min, color_hex, requiere_conf) VALUES
    ('Consulta Nueva',       'CONSULTA',      30,   '#3B82F6', 0),
    ('Control / Seguimiento','CONSULTA',      20,   '#10B981', 0),
    ('Procedimiento Menor',  'PROCEDIMIENTO', 60,   '#F59E0B', 1),
    ('Endoscopía',           'PROCEDIMIENTO', 45,   '#8B5CF6', 1),
    ('Cirugía',              'CIRUGIA',       NULL, '#EF4444', 1);
