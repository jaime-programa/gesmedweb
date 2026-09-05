-- Migración 028: añade perfil ADMIN al campo rol de la tabla points
-- Perfiles disponibles tras esta migración:
--   SECRETARIA       → agenda + datos personales
--   MEDICO_CONSULTA  → lectura clínica (Med.Lee)
--   MEDICO_ATENCION  → escritura clínica completa (Med.Prop)
--   ADMIN            → acceso total + funciones de administración

-- El campo rol ya es VARCHAR(20); no se requiere cambio de esquema.
-- Asignar perfil ADMIN al usuario administrador:
-- UPDATE points SET rol = 'ADMIN' WHERE usuario = 'nombre_usuario_admin';

-- Para consultar los roles actuales:
-- SELECT id_medico, nombre_medico, usuario, rol FROM points ORDER BY rol, nombre_medico;
