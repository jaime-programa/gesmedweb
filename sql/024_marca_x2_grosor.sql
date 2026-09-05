-- Migración 024: añade coordenadas de segundo punto y grosor a tabla marca
-- x2/y2 → cola de flecha (el primer punto x_centro/y_centro es la punta)
-- grosor → grosor de línea en píxeles

ALTER TABLE marca
    ADD COLUMN x2     INT     NOT NULL DEFAULT 0 COMMENT 'Flecha: x inicio (cola). Círculo/texto: 0',
    ADD COLUMN y2     INT     NOT NULL DEFAULT 0 COMMENT 'Flecha: y inicio (cola). Círculo/texto: 0',
    ADD COLUMN grosor TINYINT NOT NULL DEFAULT 2 COMMENT 'Grosor de línea en píxeles';
