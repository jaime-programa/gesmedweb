-- MariaDB dump 10.18  Distrib 10.4.17-MariaDB, for osx10.10 (x86_64)
--
-- Host: localhost    Database: gesmed
-- ------------------------------------------------------
-- Server version	10.4.17-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alergia`
--

DROP TABLE IF EXISTS `alergia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alergia` (
  `id_alergia` int(11) NOT NULL AUTO_INCREMENT,
  `lk_paciente` int(11) NOT NULL,
  `sustancia_alergia` varchar(100) NOT NULL,
  `detalles` text DEFAULT NULL,
  `fecha_reportada` date DEFAULT NULL,
  PRIMARY KEY (`id_alergia`),
  KEY `fk_alergia_paciente` (`lk_paciente`),
  CONSTRAINT `fk_alergia_paciente` FOREIGN KEY (`lk_paciente`) REFERENCES `paciente` (`nro_hclinica`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `antecedente_familiar`
--

DROP TABLE IF EXISTS `antecedente_familiar`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `antecedente_familiar` (
  `id_antecedente` int(11) NOT NULL AUTO_INCREMENT,
  `lk_paciente` int(11) NOT NULL,
  `descripcion` blob NOT NULL,
  `fecha_registro` date NOT NULL,
  PRIMARY KEY (`id_antecedente`),
  KEY `fk_af_paciente` (`lk_paciente`),
  CONSTRAINT `fk_af_paciente` FOREIGN KEY (`lk_paciente`) REFERENCES `paciente` (`nro_hclinica`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `atencion`
--

DROP TABLE IF EXISTS `atencion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `atencion` (
  `id_atencion` int(11) NOT NULL AUTO_INCREMENT,
  `lk_paciente` int(11) DEFAULT NULL,
  `lk_medico` int(11) NOT NULL,
  `fecha_atencion` timestamp NOT NULL DEFAULT current_timestamp(),
  `motivo_consulta` varchar(250) COLLATE utf8_spanish2_ci NOT NULL,
  `revision_sistemas` mediumtext COLLATE utf8_spanish2_ci NOT NULL,
  `subjetivo` mediumtext COLLATE utf8_spanish2_ci NOT NULL,
  `objetivo` mediumtext COLLATE utf8_spanish2_ci NOT NULL,
  `analisis` mediumtext COLLATE utf8_spanish2_ci NOT NULL,
  `plan` mediumtext COLLATE utf8_spanish2_ci NOT NULL,
  PRIMARY KEY (`id_atencion`),
  KEY `lk_paciente` (`lk_paciente`),
  KEY `lk_medico` (`lk_medico`),
  CONSTRAINT `atencion_ibfk_1` FOREIGN KEY (`lk_paciente`) REFERENCES `paciente` (`nro_hclinica`) ON UPDATE CASCADE,
  CONSTRAINT `atencion_ibfk_2` FOREIGN KEY (`lk_medico`) REFERENCES `points` (`id_medico`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1180 DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `atencion_gesmed`
--

DROP TABLE IF EXISTS `atencion_gesmed`;
/*!50001 DROP VIEW IF EXISTS `atencion_gesmed`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `atencion_gesmed` (
  `id_atencion` tinyint NOT NULL,
  `clave` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `bloqueo_horario`
--

DROP TABLE IF EXISTS `bloqueo_horario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bloqueo_horario` (
  `id_bloqueo` int(11) NOT NULL AUTO_INCREMENT,
  `lk_medico` int(11) NOT NULL,
  `fecha_inicio` datetime NOT NULL,
  `fecha_fin` datetime NOT NULL,
  `motivo` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id_bloqueo`),
  KEY `lk_medico` (`lk_medico`),
  CONSTRAINT `bloqueo_horario_ibfk_1` FOREIGN KEY (`lk_medico`) REFERENCES `points` (`id_medico`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `certificado`
--

DROP TABLE IF EXISTS `certificado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `certificado` (
  `id_certificado` int(11) NOT NULL AUTO_INCREMENT,
  `lk_atencion` int(11) NOT NULL,
  `fecha_certificado` datetime NOT NULL DEFAULT current_timestamp(),
  `reposo_desde` date NOT NULL,
  `reposo_hasta` date NOT NULL,
  `contingencia` varchar(200) NOT NULL DEFAULT '',
  `presenta_sintomas` tinyint(4) NOT NULL DEFAULT 0,
  `aislamiento` tinyint(4) NOT NULL DEFAULT 0,
  `ocupacion` varchar(200) NOT NULL DEFAULT '',
  `lugar_trabajo` varchar(200) NOT NULL DEFAULT '',
  `observacion` varchar(800) NOT NULL DEFAULT '',
  PRIMARY KEY (`id_certificado`),
  KEY `fk_cert_atencion` (`lk_atencion`),
  CONSTRAINT `fk_cert_atencion` FOREIGN KEY (`lk_atencion`) REFERENCES `atencion` (`id_atencion`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cie10`
--

DROP TABLE IF EXISTS `cie10`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cie10` (
  `cod_cie10` varchar(11) COLLATE utf8_spanish2_ci NOT NULL,
  `grupo` varchar(120) COLLATE utf8_spanish2_ci NOT NULL,
  `categoria` varchar(120) COLLATE utf8_spanish2_ci NOT NULL,
  `nomdiagnostico` varchar(254) COLLATE utf8_spanish2_ci NOT NULL,
  PRIMARY KEY (`cod_cie10`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cita`
--

DROP TABLE IF EXISTS `cita`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cita` (
  `id_cita` int(11) NOT NULL AUTO_INCREMENT,
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
  `px_seguro` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id_cita`),
  KEY `lk_paciente` (`lk_paciente`),
  KEY `lk_medico` (`lk_medico`),
  KEY `lk_tipo_cita` (`lk_tipo_cita`),
  CONSTRAINT `cita_ibfk_1` FOREIGN KEY (`lk_paciente`) REFERENCES `paciente` (`nro_hclinica`) ON DELETE SET NULL,
  CONSTRAINT `cita_ibfk_2` FOREIGN KEY (`lk_medico`) REFERENCES `points` (`id_medico`),
  CONSTRAINT `cita_ibfk_3` FOREIGN KEY (`lk_tipo_cita`) REFERENCES `tipo_cita` (`id_tipo_cita`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `diagnostico`
--

DROP TABLE IF EXISTS `diagnostico`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `diagnostico` (
  `id_diagnostico` int(11) NOT NULL AUTO_INCREMENT,
  `lk_paciente` int(11) DEFAULT NULL,
  `lk_cie10` varchar(11) COLLATE utf8_spanish2_ci NOT NULL,
  `tipo` varchar(14) COLLATE utf8_spanish2_ci NOT NULL,
  `fecha_diagnostico` date NOT NULL,
  `fecha_inicio_aparente` date NOT NULL,
  `lk_medico` int(11) NOT NULL,
  `observaciones` blob DEFAULT NULL,
  `noduplicados` varchar(300) COLLATE utf8_spanish2_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`id_diagnostico`),
  UNIQUE KEY `noduplicados` (`noduplicados`),
  KEY `lk_paciente` (`lk_paciente`),
  KEY `lk_cie10` (`lk_cie10`),
  KEY `lk_medico` (`lk_medico`),
  CONSTRAINT `diagnostico_ibfk_1` FOREIGN KEY (`lk_paciente`) REFERENCES `paciente` (`nro_hclinica`) ON UPDATE CASCADE,
  CONSTRAINT `diagnostico_ibfk_2` FOREIGN KEY (`lk_cie10`) REFERENCES `cie10` (`cod_cie10`) ON UPDATE CASCADE,
  CONSTRAINT `diagnostico_ibfk_3` FOREIGN KEY (`lk_medico`) REFERENCES `points` (`id_medico`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2116 DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `examen_catalogo`
--

DROP TABLE IF EXISTS `examen_catalogo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `examen_catalogo` (
  `id_examen` int(11) NOT NULL AUTO_INCREMENT,
  `lk_examen_tipo` int(11) NOT NULL DEFAULT 0,
  `examen_alias` varchar(15) NOT NULL DEFAULT '',
  `examen_nombre` varchar(40) NOT NULL DEFAULT '',
  PRIMARY KEY (`id_examen`),
  KEY `fk_ec_tipo` (`lk_examen_tipo`),
  CONSTRAINT `fk_ec_tipo` FOREIGN KEY (`lk_examen_tipo`) REFERENCES `examen_tipo` (`id_examen_tipo`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `examen_pedido`
--

DROP TABLE IF EXISTS `examen_pedido`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `examen_pedido` (
  `id_examen_pedido` int(11) NOT NULL AUTO_INCREMENT,
  `lk_atencion` int(11) NOT NULL,
  `lk_catalogo` int(11) NOT NULL,
  `lk_diagnostico` int(11) NOT NULL,
  `detalle_pedido` varchar(150) NOT NULL DEFAULT 'Favor realizar un',
  PRIMARY KEY (`id_examen_pedido`),
  KEY `fk_ep_atencion` (`lk_atencion`),
  KEY `fk_ep_catalogo` (`lk_catalogo`),
  KEY `fk_ep_diagnostico` (`lk_diagnostico`),
  CONSTRAINT `fk_ep_atencion` FOREIGN KEY (`lk_atencion`) REFERENCES `atencion` (`id_atencion`),
  CONSTRAINT `fk_ep_catalogo` FOREIGN KEY (`lk_catalogo`) REFERENCES `examen_catalogo` (`id_examen`),
  CONSTRAINT `fk_ep_diagnostico` FOREIGN KEY (`lk_diagnostico`) REFERENCES `diagnostico` (`id_diagnostico`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `examen_tipo`
--

DROP TABLE IF EXISTS `examen_tipo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `examen_tipo` (
  `id_examen_tipo` int(11) NOT NULL AUTO_INCREMENT,
  `examen_tipo` varchar(40) NOT NULL DEFAULT '',
  PRIMARY KEY (`id_examen_tipo`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `examenes_laboratorio_catalogo`
--

DROP TABLE IF EXISTS `examenes_laboratorio_catalogo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `examenes_laboratorio_catalogo` (
  `id_examen` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_examen` varchar(120) COLLATE utf8mb4_spanish2_ci NOT NULL,
  `lk_grupo` int(11) DEFAULT NULL,
  `activo` int(11) NOT NULL,
  `unidad` varchar(15) COLLATE utf8mb4_spanish2_ci DEFAULT NULL,
  `minimo` decimal(6,2) DEFAULT NULL,
  `maximo` decimal(6,2) DEFAULT NULL,
  `es_pedido` tinyint(1) DEFAULT 1,
  `es_resultado` tinyint(1) DEFAULT 1,
  `lk_padre` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_examen`),
  KEY `lk_grupo` (`lk_grupo`),
  KEY `fk_lab_catalogo_padre` (`lk_padre`),
  CONSTRAINT `examenes_laboratorio_catalogo_ibfk_1` FOREIGN KEY (`lk_grupo`) REFERENCES `examenes_laboratorio_grupo` (`id_grupo`),
  CONSTRAINT `fk_lab_catalogo_padre` FOREIGN KEY (`lk_padre`) REFERENCES `examenes_laboratorio_catalogo` (`id_examen`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=300 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `examenes_laboratorio_grupo`
--

DROP TABLE IF EXISTS `examenes_laboratorio_grupo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `examenes_laboratorio_grupo` (
  `id_grupo` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_grupo` varchar(80) COLLATE utf8mb4_spanish2_ci NOT NULL,
  PRIMARY KEY (`id_grupo`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `examenes_laboratorio_pedido`
--

DROP TABLE IF EXISTS `examenes_laboratorio_pedido`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `examenes_laboratorio_pedido` (
  `id_pedido` int(11) NOT NULL AUTO_INCREMENT,
  `lk_paciente` int(11) DEFAULT NULL,
  `lk_atencion` int(11) DEFAULT NULL,
  `fecha_pedido` date NOT NULL,
  `lk_examen` int(11) NOT NULL,
  PRIMARY KEY (`id_pedido`),
  KEY `lk_paciente` (`lk_paciente`),
  KEY `lk_examen` (`lk_examen`),
  KEY `fk_examenes_laboratorio_pedido_atencion` (`lk_atencion`),
  CONSTRAINT `examenes_laboratorio_pedido_ibfk_1` FOREIGN KEY (`lk_paciente`) REFERENCES `paciente` (`nro_hclinica`),
  CONSTRAINT `examenes_laboratorio_pedido_ibfk_2` FOREIGN KEY (`lk_examen`) REFERENCES `examenes_laboratorio_catalogo` (`id_examen`),
  CONSTRAINT `fk_examenes_laboratorio_pedido_atencion` FOREIGN KEY (`lk_atencion`) REFERENCES `atencion` (`id_atencion`)
) ENGINE=InnoDB AUTO_INCREMENT=2199 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `horario_medico`
--

DROP TABLE IF EXISTS `horario_medico`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `horario_medico` (
  `id_horario` int(11) NOT NULL AUTO_INCREMENT,
  `lk_medico` int(11) NOT NULL,
  `dia_semana` tinyint(4) NOT NULL COMMENT '0=Lun 1=Mar 2=Mié 3=Jue 4=Vie 5=Sáb 6=Dom',
  `hora_inicio` time NOT NULL,
  `hora_fin` time NOT NULL,
  PRIMARY KEY (`id_horario`),
  UNIQUE KEY `uq_medico_dia_inicio` (`lk_medico`,`dia_semana`,`hora_inicio`),
  CONSTRAINT `horario_medico_ibfk_1` FOREIGN KEY (`lk_medico`) REFERENCES `points` (`id_medico`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `imagen`
--

DROP TABLE IF EXISTS `imagen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `imagen` (
  `id_imagen` int(11) NOT NULL AUTO_INCREMENT,
  `lk_resultado_imagen` int(11) DEFAULT NULL,
  `lk_atencion` int(11) DEFAULT NULL COMMENT 'Atención activa al momento de la subida; parte del nombre de archivo',
  `ubicacion` varchar(80) COLLATE utf8mb4_spanish2_ci DEFAULT NULL COMMENT 'Ubicación anatómica (ej: cuadrante superior izquierdo)',
  `detalle` varchar(100) COLLATE utf8mb4_spanish2_ci DEFAULT NULL,
  `orden` int(11) NOT NULL DEFAULT 0 COMMENT 'Posición de la imagen dentro del mismo resultados_imagen (0 = primera)',
  `rotacion` smallint(6) NOT NULL DEFAULT 0 COMMENT '0|90|180|270 — nunca modifica el JPG físico',
  PRIMARY KEY (`id_imagen`),
  KEY `fk_imagen_resultado` (`lk_resultado_imagen`),
  KEY `fk_imagen_atencion` (`lk_atencion`),
  CONSTRAINT `fk_imagen_atencion` FOREIGN KEY (`lk_atencion`) REFERENCES `atencion` (`id_atencion`),
  CONSTRAINT `fk_imagen_resultado` FOREIGN KEY (`lk_resultado_imagen`) REFERENCES `resultados_imagen` (`id_resultado`)
) ENGINE=InnoDB AUTO_INCREMENT=79 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `lista_signosvitales`
--

DROP TABLE IF EXISTS `lista_signosvitales`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lista_signosvitales` (
  `id_signo_vital` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(60) NOT NULL,
  `codigo` varchar(20) NOT NULL,
  `unidad` varchar(20) DEFAULT NULL,
  `decimales` tinyint(4) NOT NULL DEFAULT 1,
  `valor_min` decimal(6,2) DEFAULT NULL,
  `valor_max` decimal(6,2) DEFAULT NULL,
  `orden_display` tinyint(4) NOT NULL DEFAULT 99,
  `es_activo` tinyint(4) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_signo_vital`),
  UNIQUE KEY `uq_codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `marca`
--

DROP TABLE IF EXISTS `marca`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `marca` (
  `id_marca` int(11) NOT NULL AUTO_INCREMENT,
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
  `grosor` tinyint(4) NOT NULL DEFAULT 2 COMMENT 'Grosor de línea en píxeles',
  PRIMARY KEY (`id_marca`),
  KEY `fk_marca_imagen` (`lk_imagen`),
  CONSTRAINT `fk_marca_imagen` FOREIGN KEY (`lk_imagen`) REFERENCES `imagen` (`id_imagen`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `medicamento_presentacion`
--

DROP TABLE IF EXISTS `medicamento_presentacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `medicamento_presentacion` (
  `id_presentacion` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_presentacion` varchar(30) NOT NULL,
  `en_uso` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_presentacion`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `medicamento_tipo`
--

DROP TABLE IF EXISTS `medicamento_tipo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `medicamento_tipo` (
  `id_tipo` int(2) NOT NULL AUTO_INCREMENT,
  `nombre_tipo` varchar(20) NOT NULL,
  PRIMARY KEY (`id_tipo`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `medicamentos`
--

DROP TABLE IF EXISTS `medicamentos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `medicamentos` (
  `cod_gen` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_generico` varchar(80) COLLATE utf8_spanish2_ci NOT NULL,
  `nombre_comercial` varchar(30) COLLATE utf8_spanish2_ci NOT NULL,
  `tipo` int(2) NOT NULL DEFAULT 1,
  `es_activo` tinyint(1) NOT NULL,
  PRIMARY KEY (`cod_gen`),
  KEY `fk_medicamentos_tipo` (`tipo`),
  CONSTRAINT `fk_medicamentos_tipo` FOREIGN KEY (`tipo`) REFERENCES `medicamento_tipo` (`id_tipo`)
) ENGINE=InnoDB AUTO_INCREMENT=474 DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `paciente`
--

DROP TABLE IF EXISTS `paciente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `paciente` (
  `nro_hclinica` int(11) NOT NULL AUTO_INCREMENT,
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
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`nro_hclinica`),
  KEY `seguro` (`seguro`)
) ENGINE=InnoDB AUTO_INCREMENT=1173 DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `paciente_pk`
--

DROP TABLE IF EXISTS `paciente_pk`;
/*!50001 DROP VIEW IF EXISTS `paciente_pk`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `paciente_pk` (
  `nro_hclinica` tinyint NOT NULL,
  `nombre_completo` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `points`
--

DROP TABLE IF EXISTS `points`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `points` (
  `id_medico` int(11) NOT NULL AUTO_INCREMENT,
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
  `rol` varchar(20) COLLATE utf8mb4_spanish2_ci NOT NULL DEFAULT 'MEDICO_ATENCION',
  PRIMARY KEY (`id_medico`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `prescripcion`
--

DROP TABLE IF EXISTS `prescripcion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `prescripcion` (
  `id_prescripcion` int(11) NOT NULL AUTO_INCREMENT,
  `lk_paciente` int(11) DEFAULT NULL,
  `lk_atencion` int(11) NOT NULL,
  `fecha_prescripcion` date NOT NULL,
  `concentracion` blob NOT NULL,
  `cantidad` int(2) NOT NULL,
  `lk_presentacion` int(11) DEFAULT NULL,
  `indicaciones` blob NOT NULL,
  `lk_generico` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_prescripcion`),
  KEY `lk_paciente` (`lk_paciente`),
  KEY `lk_atencion` (`lk_atencion`),
  KEY `lk_presentacion` (`lk_presentacion`),
  KEY `lk_generico` (`lk_generico`),
  CONSTRAINT `prescripcion_ok_ibfk_1` FOREIGN KEY (`lk_generico`) REFERENCES `medicamentos` (`cod_gen`) ON UPDATE CASCADE,
  CONSTRAINT `prescripcion_ok_ibfk_2` FOREIGN KEY (`lk_paciente`) REFERENCES `paciente` (`nro_hclinica`) ON UPDATE CASCADE,
  CONSTRAINT `prescripcion_ok_ibfk_3` FOREIGN KEY (`lk_atencion`) REFERENCES `atencion` (`id_atencion`),
  CONSTRAINT `prescripcion_ok_ibfk_4` FOREIGN KEY (`lk_presentacion`) REFERENCES `medicamento_presentacion` (`id_presentacion`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1239 DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `prescripcion_cuidados`
--

DROP TABLE IF EXISTS `prescripcion_cuidados`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `prescripcion_cuidados` (
  `id_cuidados` int(11) NOT NULL AUTO_INCREMENT,
  `lk_atencion` int(11) NOT NULL,
  `cuidados_generales` text DEFAULT NULL,
  `fecha_emision` date DEFAULT NULL,
  PRIMARY KEY (`id_cuidados`),
  UNIQUE KEY `uk_cuidados_atencion` (`lk_atencion`),
  CONSTRAINT `fk_cuidados_atencion` FOREIGN KEY (`lk_atencion`) REFERENCES `atencion` (`id_atencion`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `registro`
--

DROP TABLE IF EXISTS `registro`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `registro` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) COLLATE utf8mb4_spanish2_ci NOT NULL,
  `puerto` varchar(255) COLLATE utf8mb4_spanish2_ci NOT NULL,
  `cod_error` varchar(255) COLLATE utf8mb4_spanish2_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rel_atencion_diagnostico`
--

DROP TABLE IF EXISTS `rel_atencion_diagnostico`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rel_atencion_diagnostico` (
  `id_relacion` int(11) NOT NULL AUTO_INCREMENT,
  `lk_atencion` int(11) NOT NULL,
  `lk_diagnostico` int(11) NOT NULL,
  `noduplicarelacion` varchar(20) COLLATE utf8_spanish2_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`id_relacion`),
  UNIQUE KEY `noduplicarelacion` (`noduplicarelacion`),
  KEY `lk_atencion` (`lk_atencion`),
  KEY `lk_diagnostico` (`lk_diagnostico`),
  CONSTRAINT `rel_atencion_diagnostico_ibfk_1` FOREIGN KEY (`lk_atencion`) REFERENCES `atencion` (`id_atencion`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `rel_atencion_diagnostico_ibfk_3` FOREIGN KEY (`lk_diagnostico`) REFERENCES `diagnostico` (`id_diagnostico`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2802 DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `reporte_celda`
--

DROP TABLE IF EXISTS `reporte_celda`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `reporte_celda` (
  `id_celda` int(11) NOT NULL AUTO_INCREMENT,
  `lk_seccion` int(11) NOT NULL,
  `variable` varchar(60) COLLATE utf8mb4_spanish2_ci DEFAULT NULL,
  `fila` int(11) NOT NULL,
  `columna` int(11) NOT NULL,
  `pre_fijo` varchar(200) COLLATE utf8mb4_spanish2_ci NOT NULL DEFAULT '',
  `post_fijo` varchar(200) COLLATE utf8mb4_spanish2_ci NOT NULL DEFAULT '',
  `formato` varchar(22) COLLATE utf8mb4_spanish2_ci NOT NULL DEFAULT '09.01.01.00.NLU.0000.N',
  `explica` varchar(200) COLLATE utf8mb4_spanish2_ci NOT NULL DEFAULT '',
  `es_activa` tinyint(1) NOT NULL DEFAULT 1,
  `tipo_celda` char(1) COLLATE utf8mb4_spanish2_ci NOT NULL DEFAULT 'D',
  PRIMARY KEY (`id_celda`),
  KEY `fk_celda_seccion` (`lk_seccion`),
  CONSTRAINT `fk_celda_seccion` FOREIGN KEY (`lk_seccion`) REFERENCES `reporte_seccion` (`id_seccion`)
) ENGINE=InnoDB AUTO_INCREMENT=312 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `reporte_imagen`
--

DROP TABLE IF EXISTS `reporte_imagen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `reporte_imagen` (
  `id_imagen` int(11) NOT NULL AUTO_INCREMENT,
  `lk_impreso` int(11) NOT NULL,
  `nombre_archivo` varchar(80) NOT NULL,
  `celda` varchar(10) NOT NULL,
  `ancho` int(11) NOT NULL DEFAULT 100,
  `alto` int(11) NOT NULL DEFAULT 40,
  `orden` int(11) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_imagen`),
  KEY `fk_ri_impreso` (`lk_impreso`),
  CONSTRAINT `fk_ri_impreso` FOREIGN KEY (`lk_impreso`) REFERENCES `reporte_impreso` (`id_impreso`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `reporte_impreso`
--

DROP TABLE IF EXISTS `reporte_impreso`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `reporte_impreso` (
  `id_impreso` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_reporte` varchar(50) COLLATE utf8mb4_spanish2_ci NOT NULL,
  `nombre_fuente` varchar(50) COLLATE utf8mb4_spanish2_ci NOT NULL DEFAULT 'Arial Narrow',
  `explica` varchar(200) COLLATE utf8mb4_spanish2_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`id_impreso`),
  UNIQUE KEY `uq_nombre_reporte` (`nombre_reporte`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `reporte_seccion`
--

DROP TABLE IF EXISTS `reporte_seccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `reporte_seccion` (
  `id_seccion` int(11) NOT NULL AUTO_INCREMENT,
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
  `titulo_seccion` varchar(200) COLLATE utf8mb4_spanish2_ci DEFAULT NULL,
  PRIMARY KEY (`id_seccion`),
  KEY `fk_seccion_impreso` (`lk_impreso`),
  CONSTRAINT `fk_seccion_impreso` FOREIGN KEY (`lk_impreso`) REFERENCES `reporte_impreso` (`id_impreso`)
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `resultados_imagen`
--

DROP TABLE IF EXISTS `resultados_imagen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `resultados_imagen` (
  `id_resultado` int(11) NOT NULL AUTO_INCREMENT,
  `fecha_imagen` date NOT NULL,
  `lk_paciente` int(11) DEFAULT NULL,
  `lk_diagnostico` int(11) DEFAULT NULL,
  `lk_examen` int(11) DEFAULT NULL,
  `hallazgos` text COLLATE utf8mb4_spanish2_ci DEFAULT NULL,
  `lk_pedido` int(11) DEFAULT NULL COMMENT 'Pedido de imagen de origen (opcional)',
  `alias` varchar(80) COLLATE utf8mb4_spanish2_ci DEFAULT NULL,
  PRIMARY KEY (`id_resultado`),
  KEY `fk_resimg_paciente` (`lk_paciente`),
  KEY `fk_resimg_diagnostico` (`lk_diagnostico`),
  KEY `fk_resimg_examen` (`lk_examen`),
  KEY `fk_resimg_pedido` (`lk_pedido`),
  CONSTRAINT `fk_resimg_diagnostico` FOREIGN KEY (`lk_diagnostico`) REFERENCES `diagnostico` (`id_diagnostico`),
  CONSTRAINT `fk_resimg_examen` FOREIGN KEY (`lk_examen`) REFERENCES `examen_catalogo` (`id_examen`),
  CONSTRAINT `fk_resimg_paciente` FOREIGN KEY (`lk_paciente`) REFERENCES `paciente` (`nro_hclinica`),
  CONSTRAINT `fk_resimg_pedido` FOREIGN KEY (`lk_pedido`) REFERENCES `examen_pedido` (`id_examen_pedido`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `resultados_laboratorio`
--

DROP TABLE IF EXISTS `resultados_laboratorio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `resultados_laboratorio` (
  `id_resultado` int(11) NOT NULL AUTO_INCREMENT,
  `fecha_examen` date NOT NULL,
  `lk_paciente` int(11) DEFAULT NULL,
  `lk_examen` int(11) DEFAULT NULL,
  `valor_numerico` decimal(8,2) DEFAULT NULL,
  `valor_texto` varchar(30) COLLATE utf8mb4_spanish2_ci DEFAULT NULL,
  `en_rango` varchar(10) COLLATE utf8mb4_spanish2_ci DEFAULT NULL COMMENT 'BAJO | EN_RANGO | SOBRE | ALTO | NULL cuando valor_texto',
  `observacion` text COLLATE utf8mb4_spanish2_ci DEFAULT NULL,
  `lk_pedido` int(11) DEFAULT NULL COMMENT 'Pedido de laboratorio de origen (opcional)',
  `lk_imagen_fuente` int(11) DEFAULT NULL COMMENT 'Imagen escaneada de la que se extrajo este valor (trazabilidad OCR)',
  PRIMARY KEY (`id_resultado`),
  KEY `fk_reslab_paciente` (`lk_paciente`),
  KEY `fk_reslab_examen` (`lk_examen`),
  KEY `fk_reslab_pedido` (`lk_pedido`),
  KEY `fk_reslab_imagen` (`lk_imagen_fuente`),
  CONSTRAINT `fk_reslab_examen` FOREIGN KEY (`lk_examen`) REFERENCES `examenes_laboratorio_catalogo` (`id_examen`),
  CONSTRAINT `fk_reslab_imagen` FOREIGN KEY (`lk_imagen_fuente`) REFERENCES `imagen` (`id_imagen`),
  CONSTRAINT `fk_reslab_paciente` FOREIGN KEY (`lk_paciente`) REFERENCES `paciente` (`nro_hclinica`),
  CONSTRAINT `fk_reslab_pedido` FOREIGN KEY (`lk_pedido`) REFERENCES `examenes_laboratorio_pedido` (`id_pedido`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `seguro_medico`
--

DROP TABLE IF EXISTS `seguro_medico`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `seguro_medico` (
  `id_seguro` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_seguro` varchar(25) COLLATE utf8_spanish2_ci NOT NULL,
  `condiciones` mediumtext COLLATE utf8_spanish2_ci NOT NULL,
  `esta_activo` tinyint(4) NOT NULL,
  PRIMARY KEY (`id_seguro`),
  UNIQUE KEY `nombre_seguro` (`nombre_seguro`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `signosvitales`
--

DROP TABLE IF EXISTS `signosvitales`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `signosvitales` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `lk_atencion` int(11) NOT NULL,
  `lk_signo_vital` int(11) NOT NULL,
  `valor` decimal(6,2) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_atencion_signo` (`lk_atencion`,`lk_signo_vital`),
  KEY `fk_sv_atencion` (`lk_atencion`),
  KEY `fk_sv_tipo` (`lk_signo_vital`),
  CONSTRAINT `fk_sv_atencion` FOREIGN KEY (`lk_atencion`) REFERENCES `atencion` (`id_atencion`),
  CONSTRAINT `fk_sv_tipo` FOREIGN KEY (`lk_signo_vital`) REFERENCES `lista_signosvitales` (`id_signo_vital`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tipo_cita`
--

DROP TABLE IF EXISTS `tipo_cita`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tipo_cita` (
  `id_tipo_cita` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(60) NOT NULL,
  `categoria` varchar(15) NOT NULL DEFAULT 'CONSULTA' COMMENT 'CONSULTA | PROCEDIMIENTO | CIRUGIA',
  `duracion_min` int(11) DEFAULT 30 COMMENT 'Minutos fijos. NULL para CIRUGIA (duración libre al agendar)',
  `color_hex` varchar(7) NOT NULL DEFAULT '#3B82F6',
  `requiere_conf` tinyint(1) NOT NULL DEFAULT 0 COMMENT '1 = requiere confirmación explícita antes de la cita',
  `es_activo` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_tipo_cita`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'gesmed'
--

--
-- Final view structure for view `atencion_gesmed`
--

/*!50001 DROP TABLE IF EXISTS `atencion_gesmed`*/;
/*!50001 DROP VIEW IF EXISTS `atencion_gesmed`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`med_admin`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `atencion_gesmed` AS select `a`.`id_atencion` AS `id_atencion`,concat(substr(`a`.`motivo_consulta`,1,9),substr(`a`.`subjetivo`,1,9),substr(`a`.`objetivo`,1,9),substr(`a`.`analisis`,1,9),substr(`a`.`plan`,1,9)) AS `clave` from `atencion` `a` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `paciente_pk`
--

/*!50001 DROP TABLE IF EXISTS `paciente_pk`*/;
/*!50001 DROP VIEW IF EXISTS `paciente_pk`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`med_admin`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `paciente_pk` AS select `p`.`nro_hclinica` AS `nro_hclinica`,`p`.`nombre_completo` AS `nombre_completo` from `paciente` `p` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-06 18:06:49
