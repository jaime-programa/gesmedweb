-- 014_motor_reportes.sql
-- Motor de reportes paramétrico: impreso → seccion → celda

CREATE TABLE impreso (
    id_impreso     INT           NOT NULL AUTO_INCREMENT,
    nombre_reporte VARCHAR(50)   NOT NULL,
    nombre_fuente  VARCHAR(50)   NOT NULL DEFAULT 'Arial Narrow',
    explica        VARCHAR(200)  NOT NULL DEFAULT '',
    PRIMARY KEY (id_impreso),
    UNIQUE KEY uq_nombre_reporte (nombre_reporte)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;

-- orden: secuencia de ejecución dentro del mismo impreso
-- instruccion_sql: TEXT para queries largos; NULL = sección estática (solo pre_fijo en celdas)
-- parametros_in: JSON array con nombres de variables del contexto, ej: ["lk_paciente","lk_atencion"]
CREATE TABLE seccion (
    id_seccion      INT           NOT NULL AUTO_INCREMENT,
    lk_impreso      INT           NOT NULL,
    orden           INT           NOT NULL DEFAULT 1,
    instruccion_sql TEXT,
    parametros_in   JSON,
    explica         VARCHAR(200)  NOT NULL DEFAULT '',
    es_activa       TINYINT(1)    NOT NULL DEFAULT 1,
    PRIMARY KEY (id_seccion),
    CONSTRAINT fk_seccion_impreso FOREIGN KEY (lk_impreso) REFERENCES impreso (id_impreso)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;

-- variable: alias del SELECT cuyo valor se coloca en la celda; NULL = celda estática (usa pre_fijo)
-- formato: "SS.MH.MV.SH.EHV.BTRBL"
--   SS   = tamaño fuente (2 dígitos, ej: 09)
--   MH   = merge horizontal, nro de celdas (2 dígitos)
--   MV   = merge vertical,   nro de celdas (2 dígitos)
--   SH   = sombra gris %     (2 dígitos, 00=sin sombra)
--   E    = efecto fuente: N(normal) B(bold) S(subrayado) Q(cursiva)
--   H    = alinea horizontal: L(left) C(center) R(right)
--   V    = alinea vertical:   U(top)  C(center) D(bottom)
--   BTRBL = bordes top·right·bottom·left (4 dígitos 0/1, ej: 0000)
-- Ejemplo: 10.01.01.00.NCC.0000
CREATE TABLE celda (
    id_celda   INT           NOT NULL AUTO_INCREMENT,
    lk_seccion INT           NOT NULL,
    variable   VARCHAR(60),
    fila       INT           NOT NULL,
    columna    INT           NOT NULL,
    pre_fijo   VARCHAR(200)  NOT NULL DEFAULT '',
    post_fijo  VARCHAR(200)  NOT NULL DEFAULT '',
    formato    VARCHAR(20)   NOT NULL DEFAULT '09.01.01.00.NLU.0000',
    explica    VARCHAR(200)  NOT NULL DEFAULT '',
    es_activa  TINYINT(1)    NOT NULL DEFAULT 1,
    PRIMARY KEY (id_celda),
    CONSTRAINT fk_celda_seccion FOREIGN KEY (lk_seccion) REFERENCES seccion (id_seccion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;
