-- ============================================================
-- 018_resultados_examenes.sql
-- Módulo de registro de resultados de exámenes
--   1. resultados_laboratorio  — valores numéricos o texto
--   2. resultados_imagen       — cabecera de resultado imagenológico
--   3. imagen                  — archivos JPEG vinculados al resultado
--   4. marca                   — anotaciones gráficas sobre la imagen
--
-- Convención de nombre de archivo:
--   {nro_hclinica}-{lk_atencion}-{id_imagen}.jpg
--   almacenado en la ruta configurada en configuracion.txt [IMAGENES_URL]
-- ============================================================

-- 1. Resultados de laboratorio
--    Solo uno de valor_numerico / valor_texto estará lleno.
--    en_rango aplica únicamente cuando hay valor_numerico.
CREATE TABLE resultados_laboratorio (
    id_resultado    INT             NOT NULL AUTO_INCREMENT,
    fecha_examen    DATE            NOT NULL,
    lk_paciente     INT             NULL,
    lk_examen       INT             NULL,
    lk_pedido       INT             NULL     COMMENT 'Pedido de laboratorio de origen (opcional)',
    lk_imagen_fuente INT            NULL     COMMENT 'Imagen escaneada de la que se extrajo este valor (trazabilidad OCR)',
    valor_numerico  DECIMAL(8, 2)   NULL,
    valor_texto     VARCHAR(30)     NULL,
    en_rango        VARCHAR(10)     NULL     COMMENT 'EN_RANGO | SOBRE | BAJO | NULL cuando valor_texto',
    observacion     TEXT            NULL,
    PRIMARY KEY (id_resultado),
    CONSTRAINT fk_reslab_paciente FOREIGN KEY (lk_paciente)      REFERENCES paciente                      (nro_hclinica),
    CONSTRAINT fk_reslab_examen   FOREIGN KEY (lk_examen)        REFERENCES examenes_laboratorio_catalogo  (id_examen),
    CONSTRAINT fk_reslab_pedido   FOREIGN KEY (lk_pedido)        REFERENCES examenes_laboratorio_pedido    (id_pedido),
    CONSTRAINT fk_reslab_imagen   FOREIGN KEY (lk_imagen_fuente) REFERENCES imagen                         (id_imagen)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;

-- 2. Resultados de otros exámenes (imagenología, etc.)
CREATE TABLE resultados_imagen (
    id_resultado    INT             NOT NULL AUTO_INCREMENT,
    fecha_imagen    DATE            NOT NULL,
    lk_paciente     INT             NULL,
    lk_diagnostico  INT             NULL,
    lk_examen       INT             NULL,
    lk_pedido       INT             NULL     COMMENT 'Pedido de imagen de origen (opcional)',
    hallazgos       TEXT            NULL,
    PRIMARY KEY (id_resultado),
    CONSTRAINT fk_resimg_paciente    FOREIGN KEY (lk_paciente)    REFERENCES paciente        (nro_hclinica),
    CONSTRAINT fk_resimg_diagnostico FOREIGN KEY (lk_diagnostico) REFERENCES diagnostico     (id_diagnostico),
    CONSTRAINT fk_resimg_examen      FOREIGN KEY (lk_examen)      REFERENCES examen_catalogo (id_examen),
    CONSTRAINT fk_resimg_pedido      FOREIGN KEY (lk_pedido)      REFERENCES examen_pedido   (id_examen_pedido)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;

-- 3. Imágenes vinculadas a un resultado
--    El nombre de archivo se construye en tiempo de ejecución:
--    {paciente.nro_hclinica}-{lk_atencion}-{id_imagen}.jpg
CREATE TABLE imagen (
    id_imagen           INT             NOT NULL AUTO_INCREMENT,
    lk_resultado_imagen INT             NULL,
    lk_atencion         INT             NULL     COMMENT 'Atención activa al momento de la subida; parte del nombre de archivo',
    orden               INT             NOT NULL DEFAULT 0    COMMENT 'Posición dentro del mismo resultados_imagen (0 = primera)',
    rotacion            TINYINT         NOT NULL DEFAULT 0    COMMENT 'Rotación visual en grados: 0 | 90 | 180 | 270 — no modifica el JPG',
    ubicacion           VARCHAR(80)     NULL                  COMMENT 'Ubicación anatómica (ej: cuadrante superior izquierdo)',
    detalle             VARCHAR(100)    NULL,
    PRIMARY KEY (id_imagen),
    CONSTRAINT fk_imagen_resultado FOREIGN KEY (lk_resultado_imagen) REFERENCES resultados_imagen (id_resultado),
    CONSTRAINT fk_imagen_atencion  FOREIGN KEY (lk_atencion)         REFERENCES atencion          (id_atencion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;

-- 4. Marcas gráficas sobre una imagen
--    tipo_marca: c = círculo  |  f = flecha
--    cuadrante:  posición del texto respecto al centro
--                1 = 45°  |  2 = 135°  |  3 = 225°  |  4 = 315°
--    radio:      radio del círculo  |  largo de la flecha
--    nivel:      orden de superposición (0 = más abajo)
CREATE TABLE marca (
    id_marca    INT             NOT NULL AUTO_INCREMENT,
    lk_imagen   INT             NULL,
    tipo_marca  CHAR(1)         NOT NULL DEFAULT 'c'        COMMENT 'c=círculo  f=flecha  t=texto',
    x_centro    INT             NOT NULL DEFAULT 100,
    y_centro    INT             NOT NULL DEFAULT 100,
    radio       INT             NOT NULL DEFAULT 50,
    cuadrante   TINYINT         NOT NULL DEFAULT 1          COMMENT '1=45° 2=135° 3=225° 4=315°',
    font        TINYINT         NOT NULL DEFAULT 10,
    color       CHAR(7)         NOT NULL DEFAULT '#aaaaaa',
    nivel       TINYINT         NOT NULL DEFAULT 0,
    observacion VARCHAR(30)     NULL,
    PRIMARY KEY (id_marca),
    CONSTRAINT fk_marca_imagen FOREIGN KEY (lk_imagen) REFERENCES imagen (id_imagen) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;
