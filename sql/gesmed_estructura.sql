-- phpMyAdmin SQL Dump
-- version 5.0.4
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost
-- Tiempo de generación: 04-09-2026 a las 23:23:53
-- Versión del servidor: 10.4.17-MariaDB
-- Versión de PHP: 8.0.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `gesmed`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `alergia`
--

CREATE TABLE `alergia` (
  `id_alergia` int(11) NOT NULL,
  `lk_paciente` int(11) NOT NULL,
  `sustancia_alergia` varchar(100) NOT NULL,
  `detalles` text DEFAULT NULL,
  `fecha_reportada` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `antecedente_familiar`
--

CREATE TABLE `antecedente_familiar` (
  `id_antecedente` int(11) NOT NULL,
  `lk_paciente` int(11) NOT NULL,
  `descripcion` blob NOT NULL,
  `fecha_registro` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `atencion`
--

CREATE TABLE `atencion` (
  `id_atencion` int(11) NOT NULL,
  `lk_paciente` int(11) DEFAULT NULL,
  `lk_medico` int(11) NOT NULL,
  `fecha_atencion` timestamp NOT NULL DEFAULT current_timestamp(),
  `motivo_consulta` varchar(250) COLLATE utf8_spanish2_ci NOT NULL,
  `revision_sistemas` mediumtext COLLATE utf8_spanish2_ci NOT NULL,
  `subjetivo` mediumtext COLLATE utf8_spanish2_ci NOT NULL,
  `objetivo` mediumtext COLLATE utf8_spanish2_ci NOT NULL,
  `analisis` mediumtext COLLATE utf8_spanish2_ci NOT NULL,
  `plan` mediumtext COLLATE utf8_spanish2_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci;

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `atencion_amaymed`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `atencion_amaymed` (
`id_atencion` int(11)
,`clave` varchar(45)
);

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `atencion_amaymed_gesmed`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `atencion_amaymed_gesmed` (
`id_atencion_amaymed` int(11)
,`id_atencion_gesmed` int(11)
);

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `atencion_gesmed`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `atencion_gesmed` (
`id_atencion` int(11)
,`clave` varchar(45)
);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `bloqueo_horario`
--

CREATE TABLE `bloqueo_horario` (
  `id_bloqueo` int(11) NOT NULL,
  `lk_medico` int(11) NOT NULL,
  `fecha_inicio` datetime NOT NULL,
  `fecha_fin` datetime NOT NULL,
  `motivo` varchar(200) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `certificado`
--

CREATE TABLE `certificado` (
  `id_certificado` int(11) NOT NULL,
  `lk_atencion` int(11) NOT NULL,
  `fecha_certificado` datetime NOT NULL DEFAULT current_timestamp(),
  `reposo_desde` date NOT NULL,
  `reposo_hasta` date NOT NULL,
  `contingencia` varchar(200) NOT NULL DEFAULT '',
  `presenta_sintomas` tinyint(4) NOT NULL DEFAULT 0,
  `aislamiento` tinyint(4) NOT NULL DEFAULT 0,
  `ocupacion` varchar(200) NOT NULL DEFAULT '',
  `lugar_trabajo` varchar(200) NOT NULL DEFAULT '',
  `observacion` varchar(800) NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cie10`
--

CREATE TABLE `cie10` (
  `cod_cie10` varchar(11) COLLATE utf8_spanish2_ci NOT NULL,
  `grupo` varchar(120) COLLATE utf8_spanish2_ci NOT NULL,
  `categoria` varchar(120) COLLATE utf8_spanish2_ci NOT NULL,
  `nomdiagnostico` varchar(254) COLLATE utf8_spanish2_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cita`
--

CREATE TABLE `cita` (
  `id_cita` int(11) NOT NULL,
  `lk_paciente` int(11) DEFAULT NULL COMMENT 'NULL cuando el paciente es nuevo y aún no tiene registro completo',
  `lk_medico` int(11) NOT NULL,
  `lk_tipo_cita` int(11) NOT NULL,
  `inicio` datetime NOT NULL,
  `fin` datetime NOT NULL,
  `estado` varchar(15) NOT NULL DEFAULT 'AGENDADA' COMMENT 'AGENDADA | CONFIRMADA | COMPLETADA | CANCELADA | NO_ASISTIO',
  `notas` text DEFAULT NULL,
  `google_event_id` varchar(200) DEFAULT NULL,
  `px_nombre` varchar(150) DEFAULT NULL,
  `px_sexo` varchar(10) DEFAULT NULL,
  `px_celular` varchar(20) DEFAULT NULL,
  `px_ciudad` varchar(60) DEFAULT NULL,
  `px_seguro` varchar(30) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `diagnostico`
--

CREATE TABLE `diagnostico` (
  `id_diagnostico` int(11) NOT NULL,
  `lk_paciente` int(11) DEFAULT NULL,
  `lk_cie10` varchar(11) COLLATE utf8_spanish2_ci NOT NULL,
  `tipo` varchar(14) COLLATE utf8_spanish2_ci NOT NULL,
  `fecha_diagnostico` date NOT NULL,
  `fecha_inicio_aparente` date NOT NULL,
  `lk_medico` int(11) NOT NULL,
  `observaciones` blob DEFAULT NULL,
  `noduplicados` varchar(300) COLLATE utf8_spanish2_ci NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci;

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `diagnostico_amaymed`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `diagnostico_amaymed` (
`id_diagnostico` int(8)
,`noduplicados` varchar(32)
);

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `diagnostico_amaymed_gesmed`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `diagnostico_amaymed_gesmed` (
`id_diagnostico_amaymed` int(8)
,`id_diagnostico_gesmed` int(11)
);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `examenes_laboratorio_catalogo`
--

CREATE TABLE `examenes_laboratorio_catalogo` (
  `id_examen` int(11) NOT NULL,
  `nombre_examen` varchar(120) COLLATE utf8mb4_spanish2_ci NOT NULL,
  `lk_grupo` int(11) DEFAULT NULL,
  `activo` int(11) NOT NULL,
  `unidad` varchar(15) COLLATE utf8mb4_spanish2_ci DEFAULT NULL,
  `minimo` decimal(6,2) DEFAULT NULL,
  `maximo` decimal(6,2) DEFAULT NULL,
  `es_pedido` tinyint(1) DEFAULT 1,
  `es_resultado` tinyint(1) DEFAULT 1,
  `lk_padre` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `examenes_laboratorio_grupo`
--

CREATE TABLE `examenes_laboratorio_grupo` (
  `id_grupo` int(11) NOT NULL,
  `nombre_grupo` varchar(80) COLLATE utf8mb4_spanish2_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `examenes_laboratorio_pedido`
--

CREATE TABLE `examenes_laboratorio_pedido` (
  `id_pedido` int(11) NOT NULL,
  `lk_paciente` int(11) DEFAULT NULL,
  `lk_atencion` int(11) DEFAULT NULL,
  `fecha_pedido` date NOT NULL,
  `lk_examen` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `examen_catalogo`
--

CREATE TABLE `examen_catalogo` (
  `id_examen` int(11) NOT NULL,
  `lk_examen_tipo` int(11) NOT NULL DEFAULT 0,
  `examen_alias` varchar(15) NOT NULL DEFAULT '',
  `examen_nombre` varchar(40) NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `examen_pedido`
--

CREATE TABLE `examen_pedido` (
  `id_examen_pedido` int(11) NOT NULL,
  `lk_atencion` int(11) NOT NULL,
  `lk_catalogo` int(11) NOT NULL,
  `lk_diagnostico` int(11) NOT NULL,
  `detalle_pedido` varchar(150) NOT NULL DEFAULT 'Favor realizar un'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `examen_tipo`
--

CREATE TABLE `examen_tipo` (
  `id_examen_tipo` int(11) NOT NULL,
  `examen_tipo` varchar(40) NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `horario_medico`
--

CREATE TABLE `horario_medico` (
  `id_horario` int(11) NOT NULL,
  `lk_medico` int(11) NOT NULL,
  `dia_semana` tinyint(4) NOT NULL COMMENT '0=Lun 1=Mar 2=Mié 3=Jue 4=Vie 5=Sáb 6=Dom',
  `hora_inicio` time NOT NULL,
  `hora_fin` time NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `imagen`
--

CREATE TABLE `imagen` (
  `id_imagen` int(11) NOT NULL,
  `lk_resultado_imagen` int(11) DEFAULT NULL,
  `lk_atencion` int(11) DEFAULT NULL COMMENT 'Atención activa al momento de la subida; parte del nombre de archivo',
  `ubicacion` varchar(80) COLLATE utf8mb4_spanish2_ci DEFAULT NULL COMMENT 'Ubicación anatómica (ej: cuadrante superior izquierdo)',
  `detalle` varchar(100) COLLATE utf8mb4_spanish2_ci DEFAULT NULL,
  `orden` int(11) NOT NULL DEFAULT 0 COMMENT 'Posición de la imagen dentro del mismo resultados_imagen (0 = primera)',
  `rotacion` smallint(6) NOT NULL DEFAULT 0 COMMENT '0|90|180|270 — nunca modifica el JPG físico'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `lista_signosvitales`
--

CREATE TABLE `lista_signosvitales` (
  `id_signo_vital` int(11) NOT NULL,
  `nombre` varchar(60) NOT NULL,
  `codigo` varchar(20) NOT NULL,
  `unidad` varchar(20) DEFAULT NULL,
  `decimales` tinyint(4) NOT NULL DEFAULT 1,
  `valor_min` decimal(6,2) DEFAULT NULL,
  `valor_max` decimal(6,2) DEFAULT NULL,
  `orden_display` tinyint(4) NOT NULL DEFAULT 99,
  `es_activo` tinyint(4) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `marca`
--

CREATE TABLE `marca` (
  `id_marca` int(11) NOT NULL,
  `lk_imagen` int(11) DEFAULT NULL,
  `tipo_marca` char(1) COLLATE utf8mb4_spanish2_ci NOT NULL DEFAULT 'c' COMMENT 'c=círculo  f=flecha  t=texto',
  `x_centro` int(11) NOT NULL DEFAULT 100,
  `y_centro` int(11) NOT NULL DEFAULT 100,
  `radio` int(11) NOT NULL DEFAULT 50,
  `cuadrante` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=45° 2=135° 3=225° 4=315°',
  `font` tinyint(4) NOT NULL DEFAULT 10,
  `color` char(7) COLLATE utf8mb4_spanish2_ci NOT NULL DEFAULT '#aaaaaa',
  `nivel` tinyint(4) NOT NULL DEFAULT 0,
  `observacion` varchar(30) COLLATE utf8mb4_spanish2_ci DEFAULT NULL,
  `x2` int(11) NOT NULL DEFAULT 0 COMMENT 'Flecha: x inicio (cola)',
  `y2` int(11) NOT NULL DEFAULT 0 COMMENT 'Flecha: y inicio (cola)',
  `grosor` tinyint(4) NOT NULL DEFAULT 2 COMMENT 'Grosor de línea en píxeles'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `medicamentos`
--

CREATE TABLE `medicamentos` (
  `cod_gen` int(11) NOT NULL,
  `nombre_generico` varchar(80) COLLATE utf8_spanish2_ci NOT NULL,
  `nombre_comercial` varchar(30) COLLATE utf8_spanish2_ci NOT NULL,
  `tipo` int(2) NOT NULL DEFAULT 1,
  `es_activo` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `medicamento_presentacion`
--

CREATE TABLE `medicamento_presentacion` (
  `id_presentacion` int(11) NOT NULL,
  `nombre_presentacion` varchar(30) NOT NULL,
  `en_uso` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `medicamento_tipo`
--

CREATE TABLE `medicamento_tipo` (
  `id_tipo` int(2) NOT NULL,
  `nombre_tipo` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `paciente`
--

CREATE TABLE `paciente` (
  `nro_hclinica` int(11) NOT NULL,
  `nombre_completo` blob NOT NULL,
  `sexo` varchar(10) COLLATE utf8_spanish2_ci NOT NULL DEFAULT 'Femenino',
  `estado_civil` varchar(25) COLLATE utf8_spanish2_ci NOT NULL,
  `fecha_nacimiento` date NOT NULL,
  `pais_nacimiento` varchar(60) COLLATE utf8_spanish2_ci NOT NULL,
  `grupo_sanguineo` varchar(15) COLLATE utf8_spanish2_ci NOT NULL,
  `cedula_id` blob DEFAULT NULL,
  `seguro` varchar(25) COLLATE utf8_spanish2_ci DEFAULT NULL,
  `ciudad_reside` varchar(25) COLLATE utf8_spanish2_ci NOT NULL,
  `direccion_reside` blob NOT NULL,
  `tf_celular` blob NOT NULL,
  `email` blob DEFAULT NULL,
  `observacion` blob DEFAULT NULL,
  `es_activo` tinyint(1) NOT NULL DEFAULT 1,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci;

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `paciente_pk`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `paciente_pk` (
`nro_hclinica` int(11)
,`nombre_completo` blob
);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `points`
--

CREATE TABLE `points` (
  `id_medico` int(11) NOT NULL,
  `nombre_medico` varchar(80) COLLATE utf8mb4_spanish2_ci NOT NULL,
  `especialidad` varchar(60) COLLATE utf8mb4_spanish2_ci NOT NULL,
  `cod_especialidad` varchar(15) COLLATE utf8mb4_spanish2_ci NOT NULL,
  `celular` varchar(15) COLLATE utf8mb4_spanish2_ci NOT NULL,
  `email` varchar(50) COLLATE utf8mb4_spanish2_ci NOT NULL,
  `usuario` varchar(15) COLLATE utf8mb4_spanish2_ci NOT NULL,
  `clave` varchar(255) COLLATE utf8mb4_spanish2_ci NOT NULL,
  `permisos` varchar(15) COLLATE utf8mb4_spanish2_ci NOT NULL,
  `estado` tinyint(1) NOT NULL DEFAULT 1,
  `modo_agenda` varchar(5) COLLATE utf8mb4_spanish2_ci NOT NULL DEFAULT 'LIBRE' COMMENT 'FIJO = horario semanal fijo | LIBRE = sin horario base',
  `color_agenda` varchar(7) COLLATE utf8mb4_spanish2_ci NOT NULL DEFAULT '#3B82F6' COMMENT 'Color hex para distinguir al médico en el calendario',
  `google_cal_id` varchar(200) COLLATE utf8mb4_spanish2_ci DEFAULT NULL COMMENT 'Google Calendar ID del médico (para sync futuro)',
  `rol` varchar(20) COLLATE utf8mb4_spanish2_ci NOT NULL DEFAULT 'MEDICO_ATENCION'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `prescripcion`
--

CREATE TABLE `prescripcion` (
  `id_prescripcion` int(11) NOT NULL,
  `lk_paciente` int(11) DEFAULT NULL,
  `lk_atencion` int(11) NOT NULL,
  `fecha_prescripcion` date NOT NULL,
  `concentracion` blob NOT NULL,
  `cantidad` int(2) NOT NULL,
  `lk_presentacion` int(11) DEFAULT NULL,
  `indicaciones` blob NOT NULL,
  `lk_generico` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `prescripcion_cuidados`
--

CREATE TABLE `prescripcion_cuidados` (
  `id_cuidados` int(11) NOT NULL,
  `lk_atencion` int(11) NOT NULL,
  `cuidados_generales` text DEFAULT NULL,
  `fecha_emision` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `registro`
--

CREATE TABLE `registro` (
  `id` int(11) NOT NULL,
  `nombre` varchar(255) COLLATE utf8mb4_spanish2_ci NOT NULL,
  `puerto` varchar(255) COLLATE utf8mb4_spanish2_ci NOT NULL,
  `cod_error` varchar(255) COLLATE utf8mb4_spanish2_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `rel_atencion_diagnostico`
--

CREATE TABLE `rel_atencion_diagnostico` (
  `id_relacion` int(11) NOT NULL,
  `lk_atencion` int(11) NOT NULL,
  `lk_diagnostico` int(11) NOT NULL,
  `noduplicarelacion` varchar(20) COLLATE utf8_spanish2_ci NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reporte_celda`
--

CREATE TABLE `reporte_celda` (
  `id_celda` int(11) NOT NULL,
  `lk_seccion` int(11) NOT NULL,
  `variable` varchar(60) COLLATE utf8mb4_spanish2_ci DEFAULT NULL,
  `fila` int(11) NOT NULL,
  `columna` int(11) NOT NULL,
  `pre_fijo` varchar(200) COLLATE utf8mb4_spanish2_ci NOT NULL DEFAULT '',
  `post_fijo` varchar(200) COLLATE utf8mb4_spanish2_ci NOT NULL DEFAULT '',
  `formato` varchar(22) COLLATE utf8mb4_spanish2_ci NOT NULL DEFAULT '09.01.01.00.NLU.0000.N',
  `explica` varchar(200) COLLATE utf8mb4_spanish2_ci NOT NULL DEFAULT '',
  `es_activa` tinyint(1) NOT NULL DEFAULT 1,
  `tipo_celda` char(1) COLLATE utf8mb4_spanish2_ci NOT NULL DEFAULT 'D'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reporte_imagen`
--

CREATE TABLE `reporte_imagen` (
  `id_imagen` int(11) NOT NULL,
  `lk_impreso` int(11) NOT NULL,
  `nombre_archivo` varchar(80) NOT NULL,
  `celda` varchar(10) NOT NULL,
  `ancho` int(11) NOT NULL DEFAULT 100,
  `alto` int(11) NOT NULL DEFAULT 40,
  `orden` int(11) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reporte_impreso`
--

CREATE TABLE `reporte_impreso` (
  `id_impreso` int(11) NOT NULL,
  `nombre_reporte` varchar(50) COLLATE utf8mb4_spanish2_ci NOT NULL,
  `nombre_fuente` varchar(50) COLLATE utf8mb4_spanish2_ci NOT NULL DEFAULT 'Arial Narrow',
  `explica` varchar(200) COLLATE utf8mb4_spanish2_ci NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reporte_seccion`
--

CREATE TABLE `reporte_seccion` (
  `id_seccion` int(11) NOT NULL,
  `lk_impreso` int(11) NOT NULL,
  `orden` int(11) NOT NULL DEFAULT 1,
  `instruccion_sql` text COLLATE utf8mb4_spanish2_ci DEFAULT NULL,
  `parametros_in` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`parametros_in`)),
  `explica` varchar(200) COLLATE utf8mb4_spanish2_ci NOT NULL DEFAULT '',
  `es_activa` tinyint(1) NOT NULL DEFAULT 1,
  `modo_bucle` char(1) COLLATE utf8mb4_spanish2_ci NOT NULL DEFAULT 'N',
  `paso_fila` int(11) NOT NULL DEFAULT 1,
  `max_iteraciones` int(11) NOT NULL DEFAULT 10,
  `lk_seccion_ancla` int(11) DEFAULT NULL,
  `ancla_gap` int(11) NOT NULL DEFAULT 0,
  `condicion_activa_sql` text COLLATE utf8mb4_spanish2_ci DEFAULT NULL,
  `campo_grupo` varchar(60) COLLATE utf8mb4_spanish2_ci DEFAULT NULL,
  `num_columnas` int(11) NOT NULL DEFAULT 1,
  `paso_columna` int(11) NOT NULL DEFAULT 0,
  `slot_height` int(11) NOT NULL DEFAULT 10,
  `titulo_seccion` varchar(200) COLLATE utf8mb4_spanish2_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `resultados_imagen`
--

CREATE TABLE `resultados_imagen` (
  `id_resultado` int(11) NOT NULL,
  `fecha_imagen` date NOT NULL,
  `lk_paciente` int(11) DEFAULT NULL,
  `lk_diagnostico` int(11) DEFAULT NULL,
  `lk_examen` int(11) DEFAULT NULL,
  `hallazgos` text COLLATE utf8mb4_spanish2_ci DEFAULT NULL,
  `lk_pedido` int(11) DEFAULT NULL COMMENT 'Pedido de imagen de origen (opcional)',
  `alias` varchar(80) COLLATE utf8mb4_spanish2_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `resultados_laboratorio`
--

CREATE TABLE `resultados_laboratorio` (
  `id_resultado` int(11) NOT NULL,
  `fecha_examen` date NOT NULL,
  `lk_paciente` int(11) DEFAULT NULL,
  `lk_examen` int(11) DEFAULT NULL,
  `valor_numerico` decimal(8,2) DEFAULT NULL,
  `valor_texto` varchar(30) COLLATE utf8mb4_spanish2_ci DEFAULT NULL,
  `en_rango` varchar(10) COLLATE utf8mb4_spanish2_ci DEFAULT NULL COMMENT 'BAJO | EN_RANGO | SOBRE | ALTO | NULL cuando valor_texto',
  `observacion` text COLLATE utf8mb4_spanish2_ci DEFAULT NULL,
  `lk_pedido` int(11) DEFAULT NULL COMMENT 'Pedido de laboratorio de origen (opcional)',
  `lk_imagen_fuente` int(11) DEFAULT NULL COMMENT 'Imagen escaneada de la que se extrajo este valor (trazabilidad OCR)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `seguro_medico`
--

CREATE TABLE `seguro_medico` (
  `id_seguro` int(11) NOT NULL,
  `nombre_seguro` varchar(25) COLLATE utf8_spanish2_ci NOT NULL,
  `condiciones` mediumtext COLLATE utf8_spanish2_ci NOT NULL,
  `esta_activo` tinyint(4) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `signosvitales`
--

CREATE TABLE `signosvitales` (
  `id` int(11) NOT NULL,
  `lk_atencion` int(11) NOT NULL,
  `lk_signo_vital` int(11) NOT NULL,
  `valor` decimal(6,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tipo_cita`
--

CREATE TABLE `tipo_cita` (
  `id_tipo_cita` int(11) NOT NULL,
  `nombre` varchar(60) NOT NULL,
  `categoria` varchar(15) NOT NULL DEFAULT 'CONSULTA' COMMENT 'CONSULTA | PROCEDIMIENTO | CIRUGIA',
  `duracion_min` int(11) DEFAULT 30 COMMENT 'Minutos fijos. NULL para CIRUGIA (duración libre al agendar)',
  `color_hex` varchar(7) NOT NULL DEFAULT '#3B82F6',
  `requiere_conf` tinyint(1) NOT NULL DEFAULT 0 COMMENT '1 = requiere confirmación explícita antes de la cita',
  `es_activo` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura para la vista `atencion_amaymed`
--
DROP TABLE IF EXISTS `atencion_amaymed`;

CREATE ALGORITHM=UNDEFINED DEFINER=`med_admin`@`localhost` SQL SECURITY DEFINER VIEW `atencion_amaymed`  AS SELECT `a`.`id_atencion` AS `id_atencion`, concat(substr(`a`.`motivo_consulta`,1,9),substr(`a`.`subjetivo`,1,9),substr(`a`.`objetivo`,1,9),substr(`a`.`analisis`,1,9),substr(`a`.`plan`,1,9)) AS `clave` FROM `amaymed`.`atencion` AS `a` ;

-- --------------------------------------------------------

--
-- Estructura para la vista `atencion_amaymed_gesmed`
--
DROP TABLE IF EXISTS `atencion_amaymed_gesmed`;

CREATE ALGORITHM=UNDEFINED DEFINER=`med_admin`@`localhost` SQL SECURITY DEFINER VIEW `atencion_amaymed_gesmed`  AS SELECT `amed`.`id_atencion` AS `id_atencion_amaymed`, `gmed`.`id_atencion` AS `id_atencion_gesmed` FROM (`atencion_amaymed` `amed` join `atencion_gesmed` `gmed`) WHERE `amed`.`clave` = `gmed`.`clave` ;

-- --------------------------------------------------------

--
-- Estructura para la vista `atencion_gesmed`
--
DROP TABLE IF EXISTS `atencion_gesmed`;

CREATE ALGORITHM=UNDEFINED DEFINER=`med_admin`@`localhost` SQL SECURITY DEFINER VIEW `atencion_gesmed`  AS SELECT `a`.`id_atencion` AS `id_atencion`, concat(substr(`a`.`motivo_consulta`,1,9),substr(`a`.`subjetivo`,1,9),substr(`a`.`objetivo`,1,9),substr(`a`.`analisis`,1,9),substr(`a`.`plan`,1,9)) AS `clave` FROM `atencion` AS `a` ;

-- --------------------------------------------------------

--
-- Estructura para la vista `diagnostico_amaymed`
--
DROP TABLE IF EXISTS `diagnostico_amaymed`;

CREATE ALGORITHM=UNDEFINED DEFINER=`med_admin`@`localhost` SQL SECURITY DEFINER VIEW `diagnostico_amaymed`  AS SELECT `ad`.`id_diagnostico` AS `id_diagnostico`, concat(`ad`.`cod_cie10`,'.',`ad`.`cod_cie10`,'.',lpad(`pg`.`nro_hclinica`,8,'0')) AS `noduplicados` FROM (`amaymed`.`diagnostico` `ad` join `paciente_pk` `pg`) WHERE `ad`.`nombre_paciente` = `pg`.`nombre_completo` ;

-- --------------------------------------------------------

--
-- Estructura para la vista `diagnostico_amaymed_gesmed`
--
DROP TABLE IF EXISTS `diagnostico_amaymed_gesmed`;

CREATE ALGORITHM=UNDEFINED DEFINER=`med_admin`@`localhost` SQL SECURITY DEFINER VIEW `diagnostico_amaymed_gesmed`  AS SELECT `ad`.`id_diagnostico` AS `id_diagnostico_amaymed`, `gd`.`id_diagnostico` AS `id_diagnostico_gesmed` FROM (`diagnostico_amaymed` `ad` join `diagnostico` `gd`) WHERE `ad`.`noduplicados` = `gd`.`noduplicados` ;

-- --------------------------------------------------------

--
-- Estructura para la vista `paciente_pk`
--
DROP TABLE IF EXISTS `paciente_pk`;

CREATE ALGORITHM=UNDEFINED DEFINER=`med_admin`@`localhost` SQL SECURITY DEFINER VIEW `paciente_pk`  AS SELECT `p`.`nro_hclinica` AS `nro_hclinica`, `p`.`nombre_completo` AS `nombre_completo` FROM `paciente` AS `p` ;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `alergia`
--
ALTER TABLE `alergia`
  ADD PRIMARY KEY (`id_alergia`),
  ADD KEY `fk_alergia_paciente` (`lk_paciente`);

--
-- Indices de la tabla `antecedente_familiar`
--
ALTER TABLE `antecedente_familiar`
  ADD PRIMARY KEY (`id_antecedente`),
  ADD KEY `fk_af_paciente` (`lk_paciente`);

--
-- Indices de la tabla `atencion`
--
ALTER TABLE `atencion`
  ADD PRIMARY KEY (`id_atencion`),
  ADD KEY `lk_paciente` (`lk_paciente`),
  ADD KEY `lk_medico` (`lk_medico`);

--
-- Indices de la tabla `bloqueo_horario`
--
ALTER TABLE `bloqueo_horario`
  ADD PRIMARY KEY (`id_bloqueo`),
  ADD KEY `lk_medico` (`lk_medico`);

--
-- Indices de la tabla `certificado`
--
ALTER TABLE `certificado`
  ADD PRIMARY KEY (`id_certificado`),
  ADD KEY `fk_cert_atencion` (`lk_atencion`);

--
-- Indices de la tabla `cie10`
--
ALTER TABLE `cie10`
  ADD PRIMARY KEY (`cod_cie10`);

--
-- Indices de la tabla `cita`
--
ALTER TABLE `cita`
  ADD PRIMARY KEY (`id_cita`),
  ADD KEY `lk_paciente` (`lk_paciente`),
  ADD KEY `lk_medico` (`lk_medico`),
  ADD KEY `lk_tipo_cita` (`lk_tipo_cita`);

--
-- Indices de la tabla `diagnostico`
--
ALTER TABLE `diagnostico`
  ADD PRIMARY KEY (`id_diagnostico`),
  ADD UNIQUE KEY `noduplicados` (`noduplicados`),
  ADD KEY `lk_paciente` (`lk_paciente`),
  ADD KEY `lk_cie10` (`lk_cie10`),
  ADD KEY `lk_medico` (`lk_medico`);

--
-- Indices de la tabla `examenes_laboratorio_catalogo`
--
ALTER TABLE `examenes_laboratorio_catalogo`
  ADD PRIMARY KEY (`id_examen`),
  ADD KEY `lk_grupo` (`lk_grupo`),
  ADD KEY `fk_lab_catalogo_padre` (`lk_padre`);

--
-- Indices de la tabla `examenes_laboratorio_grupo`
--
ALTER TABLE `examenes_laboratorio_grupo`
  ADD PRIMARY KEY (`id_grupo`);

--
-- Indices de la tabla `examenes_laboratorio_pedido`
--
ALTER TABLE `examenes_laboratorio_pedido`
  ADD PRIMARY KEY (`id_pedido`),
  ADD KEY `lk_paciente` (`lk_paciente`),
  ADD KEY `lk_examen` (`lk_examen`),
  ADD KEY `fk_examenes_laboratorio_pedido_atencion` (`lk_atencion`);

--
-- Indices de la tabla `examen_catalogo`
--
ALTER TABLE `examen_catalogo`
  ADD PRIMARY KEY (`id_examen`),
  ADD KEY `fk_ec_tipo` (`lk_examen_tipo`);

--
-- Indices de la tabla `examen_pedido`
--
ALTER TABLE `examen_pedido`
  ADD PRIMARY KEY (`id_examen_pedido`),
  ADD KEY `fk_ep_atencion` (`lk_atencion`),
  ADD KEY `fk_ep_catalogo` (`lk_catalogo`),
  ADD KEY `fk_ep_diagnostico` (`lk_diagnostico`);

--
-- Indices de la tabla `examen_tipo`
--
ALTER TABLE `examen_tipo`
  ADD PRIMARY KEY (`id_examen_tipo`);

--
-- Indices de la tabla `horario_medico`
--
ALTER TABLE `horario_medico`
  ADD PRIMARY KEY (`id_horario`),
  ADD UNIQUE KEY `uq_medico_dia_inicio` (`lk_medico`,`dia_semana`,`hora_inicio`);

--
-- Indices de la tabla `imagen`
--
ALTER TABLE `imagen`
  ADD PRIMARY KEY (`id_imagen`),
  ADD KEY `fk_imagen_resultado` (`lk_resultado_imagen`),
  ADD KEY `fk_imagen_atencion` (`lk_atencion`);

--
-- Indices de la tabla `lista_signosvitales`
--
ALTER TABLE `lista_signosvitales`
  ADD PRIMARY KEY (`id_signo_vital`),
  ADD UNIQUE KEY `uq_codigo` (`codigo`);

--
-- Indices de la tabla `marca`
--
ALTER TABLE `marca`
  ADD PRIMARY KEY (`id_marca`),
  ADD KEY `fk_marca_imagen` (`lk_imagen`);

--
-- Indices de la tabla `medicamentos`
--
ALTER TABLE `medicamentos`
  ADD PRIMARY KEY (`cod_gen`),
  ADD KEY `fk_medicamentos_tipo` (`tipo`);

--
-- Indices de la tabla `medicamento_presentacion`
--
ALTER TABLE `medicamento_presentacion`
  ADD PRIMARY KEY (`id_presentacion`);

--
-- Indices de la tabla `medicamento_tipo`
--
ALTER TABLE `medicamento_tipo`
  ADD PRIMARY KEY (`id_tipo`);

--
-- Indices de la tabla `paciente`
--
ALTER TABLE `paciente`
  ADD PRIMARY KEY (`nro_hclinica`),
  ADD KEY `seguro` (`seguro`);

--
-- Indices de la tabla `points`
--
ALTER TABLE `points`
  ADD PRIMARY KEY (`id_medico`);

--
-- Indices de la tabla `prescripcion`
--
ALTER TABLE `prescripcion`
  ADD PRIMARY KEY (`id_prescripcion`),
  ADD KEY `lk_paciente` (`lk_paciente`),
  ADD KEY `lk_atencion` (`lk_atencion`),
  ADD KEY `lk_presentacion` (`lk_presentacion`),
  ADD KEY `lk_generico` (`lk_generico`);

--
-- Indices de la tabla `prescripcion_cuidados`
--
ALTER TABLE `prescripcion_cuidados`
  ADD PRIMARY KEY (`id_cuidados`),
  ADD UNIQUE KEY `uk_cuidados_atencion` (`lk_atencion`);

--
-- Indices de la tabla `registro`
--
ALTER TABLE `registro`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `rel_atencion_diagnostico`
--
ALTER TABLE `rel_atencion_diagnostico`
  ADD PRIMARY KEY (`id_relacion`),
  ADD UNIQUE KEY `noduplicarelacion` (`noduplicarelacion`),
  ADD KEY `lk_atencion` (`lk_atencion`),
  ADD KEY `lk_diagnostico` (`lk_diagnostico`);

--
-- Indices de la tabla `reporte_celda`
--
ALTER TABLE `reporte_celda`
  ADD PRIMARY KEY (`id_celda`),
  ADD KEY `fk_celda_seccion` (`lk_seccion`);

--
-- Indices de la tabla `reporte_imagen`
--
ALTER TABLE `reporte_imagen`
  ADD PRIMARY KEY (`id_imagen`),
  ADD KEY `fk_ri_impreso` (`lk_impreso`);

--
-- Indices de la tabla `reporte_impreso`
--
ALTER TABLE `reporte_impreso`
  ADD PRIMARY KEY (`id_impreso`),
  ADD UNIQUE KEY `uq_nombre_reporte` (`nombre_reporte`);

--
-- Indices de la tabla `reporte_seccion`
--
ALTER TABLE `reporte_seccion`
  ADD PRIMARY KEY (`id_seccion`),
  ADD KEY `fk_seccion_impreso` (`lk_impreso`);

--
-- Indices de la tabla `resultados_imagen`
--
ALTER TABLE `resultados_imagen`
  ADD PRIMARY KEY (`id_resultado`),
  ADD KEY `fk_resimg_paciente` (`lk_paciente`),
  ADD KEY `fk_resimg_diagnostico` (`lk_diagnostico`),
  ADD KEY `fk_resimg_examen` (`lk_examen`),
  ADD KEY `fk_resimg_pedido` (`lk_pedido`);

--
-- Indices de la tabla `resultados_laboratorio`
--
ALTER TABLE `resultados_laboratorio`
  ADD PRIMARY KEY (`id_resultado`),
  ADD KEY `fk_reslab_paciente` (`lk_paciente`),
  ADD KEY `fk_reslab_examen` (`lk_examen`),
  ADD KEY `fk_reslab_pedido` (`lk_pedido`),
  ADD KEY `fk_reslab_imagen` (`lk_imagen_fuente`);

--
-- Indices de la tabla `seguro_medico`
--
ALTER TABLE `seguro_medico`
  ADD PRIMARY KEY (`id_seguro`),
  ADD UNIQUE KEY `nombre_seguro` (`nombre_seguro`);

--
-- Indices de la tabla `signosvitales`
--
ALTER TABLE `signosvitales`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_atencion_signo` (`lk_atencion`,`lk_signo_vital`),
  ADD KEY `fk_sv_atencion` (`lk_atencion`),
  ADD KEY `fk_sv_tipo` (`lk_signo_vital`);

--
-- Indices de la tabla `tipo_cita`
--
ALTER TABLE `tipo_cita`
  ADD PRIMARY KEY (`id_tipo_cita`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `alergia`
--
ALTER TABLE `alergia`
  MODIFY `id_alergia` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `antecedente_familiar`
--
ALTER TABLE `antecedente_familiar`
  MODIFY `id_antecedente` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `atencion`
--
ALTER TABLE `atencion`
  MODIFY `id_atencion` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `bloqueo_horario`
--
ALTER TABLE `bloqueo_horario`
  MODIFY `id_bloqueo` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `certificado`
--
ALTER TABLE `certificado`
  MODIFY `id_certificado` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `cita`
--
ALTER TABLE `cita`
  MODIFY `id_cita` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `diagnostico`
--
ALTER TABLE `diagnostico`
  MODIFY `id_diagnostico` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `examenes_laboratorio_catalogo`
--
ALTER TABLE `examenes_laboratorio_catalogo`
  MODIFY `id_examen` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `examenes_laboratorio_grupo`
--
ALTER TABLE `examenes_laboratorio_grupo`
  MODIFY `id_grupo` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `examenes_laboratorio_pedido`
--
ALTER TABLE `examenes_laboratorio_pedido`
  MODIFY `id_pedido` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `examen_catalogo`
--
ALTER TABLE `examen_catalogo`
  MODIFY `id_examen` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `examen_pedido`
--
ALTER TABLE `examen_pedido`
  MODIFY `id_examen_pedido` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `examen_tipo`
--
ALTER TABLE `examen_tipo`
  MODIFY `id_examen_tipo` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `horario_medico`
--
ALTER TABLE `horario_medico`
  MODIFY `id_horario` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `imagen`
--
ALTER TABLE `imagen`
  MODIFY `id_imagen` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `lista_signosvitales`
--
ALTER TABLE `lista_signosvitales`
  MODIFY `id_signo_vital` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `marca`
--
ALTER TABLE `marca`
  MODIFY `id_marca` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `medicamentos`
--
ALTER TABLE `medicamentos`
  MODIFY `cod_gen` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `medicamento_presentacion`
--
ALTER TABLE `medicamento_presentacion`
  MODIFY `id_presentacion` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `medicamento_tipo`
--
ALTER TABLE `medicamento_tipo`
  MODIFY `id_tipo` int(2) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `paciente`
--
ALTER TABLE `paciente`
  MODIFY `nro_hclinica` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `points`
--
ALTER TABLE `points`
  MODIFY `id_medico` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `prescripcion`
--
ALTER TABLE `prescripcion`
  MODIFY `id_prescripcion` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `prescripcion_cuidados`
--
ALTER TABLE `prescripcion_cuidados`
  MODIFY `id_cuidados` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `registro`
--
ALTER TABLE `registro`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `rel_atencion_diagnostico`
--
ALTER TABLE `rel_atencion_diagnostico`
  MODIFY `id_relacion` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `reporte_celda`
--
ALTER TABLE `reporte_celda`
  MODIFY `id_celda` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `reporte_imagen`
--
ALTER TABLE `reporte_imagen`
  MODIFY `id_imagen` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `reporte_impreso`
--
ALTER TABLE `reporte_impreso`
  MODIFY `id_impreso` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `reporte_seccion`
--
ALTER TABLE `reporte_seccion`
  MODIFY `id_seccion` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `resultados_imagen`
--
ALTER TABLE `resultados_imagen`
  MODIFY `id_resultado` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `resultados_laboratorio`
--
ALTER TABLE `resultados_laboratorio`
  MODIFY `id_resultado` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `seguro_medico`
--
ALTER TABLE `seguro_medico`
  MODIFY `id_seguro` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `signosvitales`
--
ALTER TABLE `signosvitales`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tipo_cita`
--
ALTER TABLE `tipo_cita`
  MODIFY `id_tipo_cita` int(11) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `alergia`
--
ALTER TABLE `alergia`
  ADD CONSTRAINT `fk_alergia_paciente` FOREIGN KEY (`lk_paciente`) REFERENCES `paciente` (`nro_hclinica`);

--
-- Filtros para la tabla `antecedente_familiar`
--
ALTER TABLE `antecedente_familiar`
  ADD CONSTRAINT `fk_af_paciente` FOREIGN KEY (`lk_paciente`) REFERENCES `paciente` (`nro_hclinica`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `atencion`
--
ALTER TABLE `atencion`
  ADD CONSTRAINT `atencion_ibfk_1` FOREIGN KEY (`lk_paciente`) REFERENCES `paciente` (`nro_hclinica`) ON UPDATE CASCADE,
  ADD CONSTRAINT `atencion_ibfk_2` FOREIGN KEY (`lk_medico`) REFERENCES `points` (`id_medico`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `bloqueo_horario`
--
ALTER TABLE `bloqueo_horario`
  ADD CONSTRAINT `bloqueo_horario_ibfk_1` FOREIGN KEY (`lk_medico`) REFERENCES `points` (`id_medico`) ON DELETE CASCADE;

--
-- Filtros para la tabla `certificado`
--
ALTER TABLE `certificado`
  ADD CONSTRAINT `fk_cert_atencion` FOREIGN KEY (`lk_atencion`) REFERENCES `atencion` (`id_atencion`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `cita`
--
ALTER TABLE `cita`
  ADD CONSTRAINT `cita_ibfk_1` FOREIGN KEY (`lk_paciente`) REFERENCES `paciente` (`nro_hclinica`) ON DELETE SET NULL,
  ADD CONSTRAINT `cita_ibfk_2` FOREIGN KEY (`lk_medico`) REFERENCES `points` (`id_medico`),
  ADD CONSTRAINT `cita_ibfk_3` FOREIGN KEY (`lk_tipo_cita`) REFERENCES `tipo_cita` (`id_tipo_cita`);

--
-- Filtros para la tabla `diagnostico`
--
ALTER TABLE `diagnostico`
  ADD CONSTRAINT `diagnostico_ibfk_1` FOREIGN KEY (`lk_paciente`) REFERENCES `paciente` (`nro_hclinica`) ON UPDATE CASCADE,
  ADD CONSTRAINT `diagnostico_ibfk_2` FOREIGN KEY (`lk_cie10`) REFERENCES `cie10` (`cod_cie10`) ON UPDATE CASCADE,
  ADD CONSTRAINT `diagnostico_ibfk_3` FOREIGN KEY (`lk_medico`) REFERENCES `points` (`id_medico`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `examenes_laboratorio_catalogo`
--
ALTER TABLE `examenes_laboratorio_catalogo`
  ADD CONSTRAINT `examenes_laboratorio_catalogo_ibfk_1` FOREIGN KEY (`lk_grupo`) REFERENCES `examenes_laboratorio_grupo` (`id_grupo`),
  ADD CONSTRAINT `fk_lab_catalogo_padre` FOREIGN KEY (`lk_padre`) REFERENCES `examenes_laboratorio_catalogo` (`id_examen`) ON DELETE SET NULL;

--
-- Filtros para la tabla `examenes_laboratorio_pedido`
--
ALTER TABLE `examenes_laboratorio_pedido`
  ADD CONSTRAINT `examenes_laboratorio_pedido_ibfk_1` FOREIGN KEY (`lk_paciente`) REFERENCES `paciente` (`nro_hclinica`),
  ADD CONSTRAINT `examenes_laboratorio_pedido_ibfk_2` FOREIGN KEY (`lk_examen`) REFERENCES `examenes_laboratorio_catalogo` (`id_examen`),
  ADD CONSTRAINT `fk_examenes_laboratorio_pedido_atencion` FOREIGN KEY (`lk_atencion`) REFERENCES `atencion` (`id_atencion`);

--
-- Filtros para la tabla `examen_catalogo`
--
ALTER TABLE `examen_catalogo`
  ADD CONSTRAINT `fk_ec_tipo` FOREIGN KEY (`lk_examen_tipo`) REFERENCES `examen_tipo` (`id_examen_tipo`);

--
-- Filtros para la tabla `examen_pedido`
--
ALTER TABLE `examen_pedido`
  ADD CONSTRAINT `fk_ep_atencion` FOREIGN KEY (`lk_atencion`) REFERENCES `atencion` (`id_atencion`),
  ADD CONSTRAINT `fk_ep_catalogo` FOREIGN KEY (`lk_catalogo`) REFERENCES `examen_catalogo` (`id_examen`),
  ADD CONSTRAINT `fk_ep_diagnostico` FOREIGN KEY (`lk_diagnostico`) REFERENCES `diagnostico` (`id_diagnostico`);

--
-- Filtros para la tabla `horario_medico`
--
ALTER TABLE `horario_medico`
  ADD CONSTRAINT `horario_medico_ibfk_1` FOREIGN KEY (`lk_medico`) REFERENCES `points` (`id_medico`) ON DELETE CASCADE;

--
-- Filtros para la tabla `imagen`
--
ALTER TABLE `imagen`
  ADD CONSTRAINT `fk_imagen_atencion` FOREIGN KEY (`lk_atencion`) REFERENCES `atencion` (`id_atencion`),
  ADD CONSTRAINT `fk_imagen_resultado` FOREIGN KEY (`lk_resultado_imagen`) REFERENCES `resultados_imagen` (`id_resultado`);

--
-- Filtros para la tabla `marca`
--
ALTER TABLE `marca`
  ADD CONSTRAINT `fk_marca_imagen` FOREIGN KEY (`lk_imagen`) REFERENCES `imagen` (`id_imagen`) ON DELETE CASCADE;

--
-- Filtros para la tabla `medicamentos`
--
ALTER TABLE `medicamentos`
  ADD CONSTRAINT `fk_medicamentos_tipo` FOREIGN KEY (`tipo`) REFERENCES `medicamento_tipo` (`id_tipo`);

--
-- Filtros para la tabla `prescripcion`
--
ALTER TABLE `prescripcion`
  ADD CONSTRAINT `prescripcion_ok_ibfk_1` FOREIGN KEY (`lk_generico`) REFERENCES `medicamentos` (`cod_gen`) ON UPDATE CASCADE,
  ADD CONSTRAINT `prescripcion_ok_ibfk_2` FOREIGN KEY (`lk_paciente`) REFERENCES `paciente` (`nro_hclinica`) ON UPDATE CASCADE,
  ADD CONSTRAINT `prescripcion_ok_ibfk_3` FOREIGN KEY (`lk_atencion`) REFERENCES `atencion` (`id_atencion`),
  ADD CONSTRAINT `prescripcion_ok_ibfk_4` FOREIGN KEY (`lk_presentacion`) REFERENCES `medicamento_presentacion` (`id_presentacion`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `prescripcion_cuidados`
--
ALTER TABLE `prescripcion_cuidados`
  ADD CONSTRAINT `fk_cuidados_atencion` FOREIGN KEY (`lk_atencion`) REFERENCES `atencion` (`id_atencion`);

--
-- Filtros para la tabla `rel_atencion_diagnostico`
--
ALTER TABLE `rel_atencion_diagnostico`
  ADD CONSTRAINT `rel_atencion_diagnostico_ibfk_1` FOREIGN KEY (`lk_atencion`) REFERENCES `atencion` (`id_atencion`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `rel_atencion_diagnostico_ibfk_3` FOREIGN KEY (`lk_diagnostico`) REFERENCES `diagnostico` (`id_diagnostico`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `reporte_celda`
--
ALTER TABLE `reporte_celda`
  ADD CONSTRAINT `fk_celda_seccion` FOREIGN KEY (`lk_seccion`) REFERENCES `reporte_seccion` (`id_seccion`);

--
-- Filtros para la tabla `reporte_imagen`
--
ALTER TABLE `reporte_imagen`
  ADD CONSTRAINT `fk_ri_impreso` FOREIGN KEY (`lk_impreso`) REFERENCES `reporte_impreso` (`id_impreso`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `reporte_seccion`
--
ALTER TABLE `reporte_seccion`
  ADD CONSTRAINT `fk_seccion_impreso` FOREIGN KEY (`lk_impreso`) REFERENCES `reporte_impreso` (`id_impreso`);

--
-- Filtros para la tabla `resultados_imagen`
--
ALTER TABLE `resultados_imagen`
  ADD CONSTRAINT `fk_resimg_diagnostico` FOREIGN KEY (`lk_diagnostico`) REFERENCES `diagnostico` (`id_diagnostico`),
  ADD CONSTRAINT `fk_resimg_examen` FOREIGN KEY (`lk_examen`) REFERENCES `examen_catalogo` (`id_examen`),
  ADD CONSTRAINT `fk_resimg_paciente` FOREIGN KEY (`lk_paciente`) REFERENCES `paciente` (`nro_hclinica`),
  ADD CONSTRAINT `fk_resimg_pedido` FOREIGN KEY (`lk_pedido`) REFERENCES `examen_pedido` (`id_examen_pedido`);

--
-- Filtros para la tabla `resultados_laboratorio`
--
ALTER TABLE `resultados_laboratorio`
  ADD CONSTRAINT `fk_reslab_examen` FOREIGN KEY (`lk_examen`) REFERENCES `examenes_laboratorio_catalogo` (`id_examen`),
  ADD CONSTRAINT `fk_reslab_imagen` FOREIGN KEY (`lk_imagen_fuente`) REFERENCES `imagen` (`id_imagen`),
  ADD CONSTRAINT `fk_reslab_paciente` FOREIGN KEY (`lk_paciente`) REFERENCES `paciente` (`nro_hclinica`),
  ADD CONSTRAINT `fk_reslab_pedido` FOREIGN KEY (`lk_pedido`) REFERENCES `examenes_laboratorio_pedido` (`id_pedido`);

--
-- Filtros para la tabla `signosvitales`
--
ALTER TABLE `signosvitales`
  ADD CONSTRAINT `fk_sv_atencion` FOREIGN KEY (`lk_atencion`) REFERENCES `atencion` (`id_atencion`),
  ADD CONSTRAINT `fk_sv_tipo` FOREIGN KEY (`lk_signo_vital`) REFERENCES `lista_signosvitales` (`id_signo_vital`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
