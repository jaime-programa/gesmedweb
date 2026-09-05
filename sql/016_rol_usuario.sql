-- Migración 016: campo rol en tabla points
-- Roles disponibles:
--   MEDICO_ATENCION  → acceso completo (ingresa y modifica información clínica)
--   MEDICO_CONSULTA  → solo lectura de información clínica
--   SECRETARIA       → acceso a agenda y datos personales del paciente

ALTER TABLE points
    ADD COLUMN rol VARCHAR(20) NOT NULL DEFAULT 'MEDICO_ATENCION';

-- Asignar rol inicial a usuarios existentes (todos pasan a MEDICO_ATENCION por defecto)
-- Ajustar manualmente según corresponda:
-- UPDATE points SET rol = 'MEDICO_CONSULTA' WHERE usuario = 'nombre_usuario';
-- UPDATE points SET rol = 'SECRETARIA'      WHERE usuario = 'nombre_usuario';
