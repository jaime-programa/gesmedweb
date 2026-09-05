#Estos scripts van a convertir la base de datos GESMED original,
#hacia la nueva base de datos de la aplicación web.
#Utilizarán el mismo archivo de setup para conectarse a la BD
#Irán ajustando y creando las tablas necesarias, partiendo de la 
#información existente.
#Se recomienda hacer un backup de la base de datos antes de iniciar estos procesos

import sys, mysql.connector,os
#import tkinter as tk
#from tkinter import filedialog,messagebox

configuracion={}
paciente={}

def seleccionar_directorio(instruccion:str):
    # Crear ventana raíz oculta
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal
    
    # Abrir diálogo para seleccionar una carpeta
    ruta_carpeta = filedialog.askdirectory(title=instruccion)
    
    # Comprobar si se ha seleccionado una carpeta
    if ruta_carpeta:
        return ruta_carpeta
    else:
        return ''   

def aux(mensaje:str):
    # Crear ventana raíz oculta
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal
    
    # Mostrar un cuadro de diálogo con un mensaje de información
    messagebox.showinfo("Atención", mensaje)

def conexion():
    global bd_origen
    global curso_origen
    global inserta_origen
    global bd_destino
    global cursor_destino
    global inserta_destino
    global ruta_reportes
    global ruta_usuario
    global p1,p2,p3,p4

    #ruta_config=seleccionar_directorio("Indica la ruta del archivo configuracion.txt")
    ruta_config="/Users/jaime/Software/230817_Gesmed/Python/Setup"

    #Cargamos desde archivo de configuracion
    archivo = open(ruta_config + "/configuracion.txt", "r")

    i = 0
    for linea in archivo.readlines():
        largo=len(linea)
        fin=linea.find("]")
        clave=linea[1:fin]
        valor=linea[fin+1:]
        configuracion[clave]=valor[:-1]
        i = i + 1
    archivo.close()

    # Lee Rutas
    rbase_linux = configuracion["ruta_linux"]
    rbase_win = configuracion["ruta_windows"]
    ruta_reportes = configuracion["ruta_reportes"]
    if (os.name == 'posix'):  # Linux - MacOS
        ruta_usuario = rbase_linux
    else:
        ruta_usuario = rbase_win
        


    # Conexiones a BDatos
    try:
        n1=configuracion["usuario"].find(".")
        n2=configuracion["pass"].find(".")
        p1 = configuracion["usuario"].strip()[:n1]
        p2 = configuracion["pass"].strip()[:n2]
        p3=configuracion["host"]
        p4=configuracion["base"]
        p5="gesmed"
        #Conexion Base Datos Origen
        bd_origen = mysql.connector.connect(user=p1, password=p2, host=p3, database=p4,use_unicode=True)
        cursor_origen = bd_origen.cursor(buffered=True)
        inserta_origen = bd_origen.cursor()

        #Conexion Base Datos Destion
        bd_destino = mysql.connector.connect(user=p1, password=p2, host=p3, database=p5,use_unicode=True)
        cursor_destino = bd_destino.cursor(buffered=True)
        inserta_destino = bd_destino.cursor()

        print("Conexion Exitosa")
    except Exception as error:
        aux("Ha ocurrido un error: \n" + str(error) + "\nEn la línea:" + str(
                            sys.exc_info()[2].tb_lineno))
        return
    




#### Tablas Fijas ####
def traslada_cie10():
    #CIE10
    query="CREATE TABLE `cie10` (`cod_cie10` varchar(11) COLLATE utf8_spanish2_ci NOT NULL PRIMARY KEY,`grupo` varchar(120) COLLATE utf8_spanish2_ci NOT NULL,`categoria` varchar(120) COLLATE utf8_spanish2_ci NOT NULL,`nomdiagnostico` varchar(254) COLLATE utf8_spanish2_ci NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci;"
    inserta_destino.execute(query)
    bd_destino.commit()
    query="INSERT INTO gesmed.cie10 (cod_cie10,grupo,categoria,nomdiagnostico) SELECT cod_cie10,grupo,categoria,nomdiagnostico FROM amaymed.cie10"
    inserta_destino.execute(query)
    bd_destino.commit()
    print("Cie10 Ok")

def traslada_medicamentos():
    #Medicamentos
    #Tabla con error detectado, se repiten 3 elementos iguales para los codigos 451,452, 453 
    query="CREATE TABLE `medicamentos` (`cod_gen` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,`nombre_generico` varchar(80) COLLATE utf8_spanish2_ci NOT NULL,`nombre_comercial` varchar(30) COLLATE utf8_spanish2_ci NOT NULL,`tipo` int(2) NOT NULL DEFAULT 1,`es_activo` tinyint(1) NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci"
    inserta_destino.execute(query)
    bd_destino.commit()

    query1="INSERT INTO gesmed.medicamentos (nombre_generico,nombre_comercial,tipo,es_activo) \
        SELECT nombre_generico,nombre_comercial,tipo,es_activo FROM amaymed.medicamentos_ok WHERE cod_gen<451"
    inserta_destino.execute(query1)
    bd_destino.commit()
    
    #Se repiten 3 medicamentos 
    query2="ALTER TABLE medicamentos AUTO_INCREMENT = 1"
    inserta_destino.execute(query2)
    bd_destino.commit()
    
    query4="INSERT INTO gesmed.medicamentos (nombre_generico,nombre_comercial,tipo,es_activo) \
        SELECT nombre_generico,nombre_comercial,tipo,es_activo FROM amaymed.medicamentos_ok as a WHERE a.cod_gen in (454,455,456)"
    inserta_destino.execute(query4)
    bd_destino.commit()

    #Se continua con los siguientes medicamentos
    query3="INSERT INTO gesmed.medicamentos (nombre_generico,nombre_comercial,tipo,es_activo) \
        SELECT nombre_generico,nombre_comercial,tipo,es_activo FROM amaymed.medicamentos_ok as a WHERE a.cod_gen>=454"
    inserta_destino.execute(query3)
    bd_destino.commit()

    print("medicamentos ok")

def traslada_presentacion_medicamentos():
    query="CREATE TABLE `presentacion_medicamentos` (\
        id_presentacion INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,\
        `nombre_presentacion` varchar(30) COLLATE utf8_spanish2_ci NOT NULL,\
        `en_uso` tinyint(1) NOT NULL\
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci;"
    inserta_destino.execute(query)
    bd_destino.commit()

    query="INSERT INTO gesmed.presentacion_medicamentos (nombre_presentacion,en_uso) \
        SELECT nombre_presentacion,en_uso FROM amaymed.presentacion_medicamentos "
    inserta_destino.execute(query)
    bd_destino.commit()
    print("presentacion medicamentos ok")

def traslada_seguro_medico():
    query="CREATE TABLE `seguro_medico` (\
        `id_seguro` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,\
        `nombre_seguro` varchar(25) COLLATE utf8_spanish2_ci NOT NULL,\
        `condiciones` mediumtext COLLATE utf8_spanish2_ci NOT NULL,\
        `esta_activo` tinyint(4) NOT NULL,\
        UNIQUE KEY `nombre_seguro` (`nombre_seguro`)\
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci;"
    inserta_destino.execute(query)
    bd_destino.commit()

    query="INSERT INTO gesmed.seguro_medico (id_seguro, nombre_seguro, condiciones, esta_activo) \
        SELECT id_seguro, UPPER(nombre_seguro), condiciones, esta_activo FROM amaymed.empresas_seguro ORDER BY id_seguro"
    inserta_destino.execute(query)
    bd_destino.commit()
    print("Seguro Médico Ok")

def laboratorio():
    #Examenes Laboratorio
    query="CREATE TABLE `examenes_laboratorio` (`id_examen` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,`nombre_examen` varchar(60) COLLATE utf8_spanish2_ci NOT NULL,`valores_referencia` varchar(40) COLLATE utf8_spanish2_ci NOT NULL,`costo_siniva` double NOT NULL,`grupo_examen` varchar(20) COLLATE utf8_spanish2_ci NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci"
    inserta_destino.execute(query)
    bd_destino.commit()
    query="INSERT INTO gesmed.examenes_laboratorio (nombre_examen,valores_referencia,costo_siniva,grupo_examen) \
        SELECT a.nombre_examen,a.valores_referencia,a.costo_siniva,a.grupo_examen FROM amaymed.examenes_laboratorio as a ORDER BY grupo_examen,nombre_examen"
    inserta_destino.execute(query)
    bd_destino.commit()
    print("EXAMENES LABORATORIO")
    
    #Pedido Examenes Laboratorio
    query="CREATE TABLE `pedido_examenes` (`id_examen` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,`nombre_grupo` varchar(20) COLLATE utf8mb4_spanish2_ci NOT NULL,`detalle` varchar(50) COLLATE utf8mb4_spanish2_ci NOT NULL,`grupo` int(4) NOT NULL,`es_activo` int(1) NOT NULL DEFAULT 1) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish2_ci"
    inserta_destino.execute(query)
    bd_destino.commit()
    query="INSERT INTO pedido_examenes (nombre_grupo,detalle,grupo,es_activo) \
        SELECT" 
    print("Pedio examenes Laboratorio OK")

def modifica_paciente():
    #Tabla Paciente
    query="CREATE TABLE `paciente` (`nro_hclinica` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,\
        `nombre_completo` varchar(80) COLLATE utf8_spanish2_ci NOT NULL,\
        `sexo` varchar(10) COLLATE utf8_spanish2_ci NOT NULL DEFAULT 'Femenino',\
        `estado_civil` varchar(25) COLLATE utf8_spanish2_ci NOT NULL,\
        `fecha_nacimiento` date NOT NULL, \
        `lugar_nacimiento` varchar(60) COLLATE utf8_spanish2_ci NOT NULL,\
        `grupo_sanguineo` varchar(15) COLLATE utf8_spanish2_ci NOT NULL,\
        `cedula_id` varchar(15) COLLATE utf8_spanish2_ci DEFAULT NULL,\
        `seguro` varchar(25) COLLATE utf8_spanish2_ci DEFAULT NULL,\
        `ciudad_reside` varchar(25) COLLATE utf8_spanish2_ci NOT NULL,\
        `direccion_reside` varchar(100) COLLATE utf8_spanish2_ci NOT NULL,\
        `tf_celular` char(12) COLLATE utf8_spanish2_ci NOT NULL,\
        `email` varchar(30) COLLATE utf8_spanish2_ci DEFAULT NULL,\
        `observacion` mediumtext COLLATE utf8_spanish2_ci DEFAULT NULL,\
        `es_activo` tinyint(1) NOT NULL DEFAULT 1,\
        `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp()\
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci;"
    inserta_destino.execute(query)
    bd_destino.commit()
    query="ALTER TABLE `paciente` ADD KEY `seguro` (`seguro`) ;"
    inserta_destino.execute(query)
    bd_destino.commit()

    query="ALTER TABLE `paciente`  AUTO_INCREMENT=1;"
    inserta_destino.execute(query)
    bd_destino.commit()

    # Se debe corregir (crear) los nro_hclinica borrados (784,792,793,821,835,1151)
    query="INSERT INTO paciente (nombre_completo,sexo,estado_civil,fecha_nacimiento,lugar_nacimiento,grupo_sanguineo,cedula_id,seguro,ciudad_reside,direccion_reside,tf_celular,email,observacion,es_activo,fecha_creacion) \
        SELECT UPPER(a.nombre_completo),a.sexo,a.estado_civil,a.fecha_nacimiento,a.lugar_nacimiento,a.grupo_sanguineo,a.cedula_id,a.seguro,a.ciudad_reside,a.direccion_reside,a.tf_celular,a.email,a.observacion,a.es_activo,a.fecha_creacion \
            FROM amaymed.paciente as a WHERE a.nro_hclinica<784 ORDER BY nro_hclinica"
    inserta_destino.execute(query)
    bd_destino.commit()
    

#def corrige_pacientes_faltan():
    #creamos 784
    query="ALTER TABLE `paciente`  AUTO_INCREMENT=1;"
    inserta_destino.execute(query)
    bd_destino.commit()

    query="INSERT INTO paciente (nombre_completo,sexo,estado_civil,fecha_nacimiento,lugar_nacimiento,grupo_sanguineo,cedula_id,seguro,ciudad_reside,direccion_reside,tf_celular,email,observacion,es_activo) VALUE \
        ('NN','NN','NN','2025-01-01','NN','NN','NN','NN','NN','NN','NN','NN','NN',0)"
    inserta_destino.execute(query)
    bd_destino.commit()
    print("Ok_1")

#def corrige_pacientes_faltan_2():
    #trasladamos 785 a 791
    query="INSERT INTO paciente (nombre_completo,sexo,estado_civil,fecha_nacimiento,lugar_nacimiento,grupo_sanguineo,cedula_id,seguro,ciudad_reside,direccion_reside,tf_celular,email,observacion,es_activo,fecha_creacion) \
        SELECT UPPER(a.nombre_completo),a.sexo,a.estado_civil,a.fecha_nacimiento,a.lugar_nacimiento,a.grupo_sanguineo,a.cedula_id,a.seguro,a.ciudad_reside,a.direccion_reside,a.tf_celular,a.email,a.observacion,a.es_activo,a.fecha_creacion \
            FROM amaymed.paciente as a WHERE a.nro_hclinica>=785 AND a.nro_hclinica<=791 ORDER BY nro_hclinica"
    inserta_destino.execute(query)
    bd_destino.commit()
    print("Ok_2")

#def corrige_pacientes_faltan_3():
    #creamos 792 y 793
    for i in (0,1):
        query="INSERT INTO paciente (nombre_completo,sexo,estado_civil,fecha_nacimiento,lugar_nacimiento,grupo_sanguineo,cedula_id,seguro,ciudad_reside,direccion_reside,tf_celular,email,observacion,es_activo) VALUE \
            ('NN','NN','NN','2025-01-01','NN','NN','NN','NN','NN','NN','NN','NN','NN',0)"
        inserta_destino.execute(query)
        bd_destino.commit()
    print("Ok_3")

#def corrige_pacientes_faltan_4():
    #trasladamos 794 a 820
    query="INSERT INTO paciente (nombre_completo,sexo,estado_civil,fecha_nacimiento,lugar_nacimiento,grupo_sanguineo,cedula_id,seguro,ciudad_reside,direccion_reside,tf_celular,email,observacion,es_activo,fecha_creacion) \
        SELECT UPPER(a.nombre_completo),a.sexo,a.estado_civil,a.fecha_nacimiento,a.lugar_nacimiento,a.grupo_sanguineo,a.cedula_id,a.seguro,a.ciudad_reside,a.direccion_reside,a.tf_celular,a.email,a.observacion,a.es_activo,a.fecha_creacion \
            FROM amaymed.paciente as a WHERE a.nro_hclinica>=794 AND a.nro_hclinica<=820 ORDER BY nro_hclinica"
    inserta_destino.execute(query)
    bd_destino.commit()
    print("Ok_4")

#def corrige_pacientes_faltan_5():
    query="ALTER TABLE `paciente`  AUTO_INCREMENT=1;"
    inserta_destino.execute(query)
    bd_destino.commit()

        #creamos 821
    query="INSERT INTO paciente (nombre_completo,sexo,estado_civil,fecha_nacimiento,lugar_nacimiento,grupo_sanguineo,cedula_id,seguro,ciudad_reside,direccion_reside,tf_celular,email,observacion,es_activo) VALUE \
        ('NN','NN','NN','2025-01-01','NN','NN','NN','NN','NN','NN','NN','NN','NN',0)"
    inserta_destino.execute(query)
    bd_destino.commit()
    print("Ok_5")

#def corrige_pacientes_faltan_6():
    #trasladamos 822 a 834
    query="INSERT INTO paciente (nombre_completo,sexo,estado_civil,fecha_nacimiento,lugar_nacimiento,grupo_sanguineo,cedula_id,seguro,ciudad_reside,direccion_reside,tf_celular,email,observacion,es_activo,fecha_creacion) \
        SELECT UPPER(a.nombre_completo),a.sexo,a.estado_civil,a.fecha_nacimiento,a.lugar_nacimiento,a.grupo_sanguineo,a.cedula_id,a.seguro,a.ciudad_reside,a.direccion_reside,a.tf_celular,a.email,a.observacion,a.es_activo,a.fecha_creacion \
            FROM amaymed.paciente as a WHERE a.nro_hclinica>=822 AND a.nro_hclinica<=834 ORDER BY nro_hclinica"
    inserta_destino.execute(query)
    bd_destino.commit()
    print("Ok_6")

#def corrige_pacientes_faltan_7():
    query="ALTER TABLE `paciente`  AUTO_INCREMENT=1;"
    inserta_destino.execute(query)
    bd_destino.commit()
    
        #creamos 835
    query="INSERT INTO paciente (nombre_completo,sexo,estado_civil,fecha_nacimiento,lugar_nacimiento,grupo_sanguineo,cedula_id,seguro,ciudad_reside,direccion_reside,tf_celular,email,observacion,es_activo) VALUE \
        ('NN','NN','NN','2025-01-01','NN','NN','NN','NN','NN','NN','NN','NN','NN',0)"
    inserta_destino.execute(query)
    bd_destino.commit()
    print("Ok_7")

#def corrige_pacientes_faltan_8():
    #trasladamos 836 a 1150
    query="INSERT INTO paciente (nombre_completo,sexo,estado_civil,fecha_nacimiento,lugar_nacimiento,grupo_sanguineo,cedula_id,seguro,ciudad_reside,direccion_reside,tf_celular,email,observacion,es_activo,fecha_creacion) \
        SELECT UPPER(a.nombre_completo),a.sexo,a.estado_civil,a.fecha_nacimiento,a.lugar_nacimiento,a.grupo_sanguineo,a.cedula_id,a.seguro,a.ciudad_reside,a.direccion_reside,a.tf_celular,a.email,a.observacion,a.es_activo,a.fecha_creacion \
            FROM amaymed.paciente as a WHERE a.nro_hclinica>=836 AND a.nro_hclinica<=1150 ORDER BY nro_hclinica"
    inserta_destino.execute(query)
    bd_destino.commit()
    print("Ok_8")

#def corrige_pacientes_faltan_9():
    query="ALTER TABLE `paciente`  AUTO_INCREMENT=1;"
    inserta_destino.execute(query)
    bd_destino.commit()

        #creamos 1151
    query="INSERT INTO paciente (nombre_completo,sexo,estado_civil,fecha_nacimiento,lugar_nacimiento,grupo_sanguineo,cedula_id,seguro,ciudad_reside,direccion_reside,tf_celular,email,observacion,es_activo) VALUE \
        ('NN','NN','NN','2025-01-01','NN','NN','NN','NN','NN','NN','NN','NN','NN',0)"
    inserta_destino.execute(query)
    bd_destino.commit()
    print("Ok_9")

#def corrige_pacientes_faltan_10():
    #trasladamos 1152 en adelante
    query="INSERT INTO paciente (nombre_completo,sexo,estado_civil,fecha_nacimiento,lugar_nacimiento,grupo_sanguineo,cedula_id,seguro,ciudad_reside,direccion_reside,tf_celular,email,observacion,es_activo,fecha_creacion) \
        SELECT UPPER(a.nombre_completo),a.sexo,a.estado_civil,a.fecha_nacimiento,a.lugar_nacimiento,a.grupo_sanguineo,a.cedula_id,a.seguro,a.ciudad_reside,a.direccion_reside,a.tf_celular,a.email,a.observacion,a.es_activo,a.fecha_creacion \
            FROM amaymed.paciente as a WHERE a.nro_hclinica>=1152 ORDER BY nro_hclinica"
    inserta_destino.execute(query)
    bd_destino.commit()
    print("Ok_10")

    #Creamos vista con las claves primarias de gesmed:
    query="CREATE OR REPLACE VIEW paciente_pk AS SELECT p.nro_hclinica,p.nombre_completo FROM gesmed.paciente as p"
    inserta_destino.execute(query)
    bd_destino.commit()
    print("Pacientes Ok")

def modifica_atencion():
    #Tabla Atencion
    query="CREATE TABLE `atencion` (`id_atencion` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,\
        `lk_paciente` int(11)NOT NULL,\
        `lk_medico` int(11) NOT NULL,\
        `fecha_atencion` timestamp NOT NULL DEFAULT current_timestamp(),\
        `motivo_consulta` varchar(250) COLLATE utf8_spanish2_ci NOT NULL,\
        `revision_sistemas` mediumtext COLLATE utf8_spanish2_ci NOT NULL,\
        `subjetivo` mediumtext COLLATE utf8_spanish2_ci NOT NULL,\
        `objetivo` mediumtext COLLATE utf8_spanish2_ci NOT NULL,\
        `analisis` mediumtext COLLATE utf8_spanish2_ci NOT NULL,\
        `plan` mediumtext COLLATE utf8_spanish2_ci NOT NULL\
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci;"
    inserta_destino.execute(query)
    bd_destino.commit()
        #Genera claves foraneas
    query="ALTER TABLE `atencion` ADD  FOREIGN KEY (`lk_paciente`) REFERENCES `paciente`(`nro_hclinica`) ON DELETE RESTRICT ON UPDATE CASCADE;"
    inserta_destino.execute(query)
    query2="ALTER TABLE `atencion` ADD  FOREIGN KEY (`lk_medico`) REFERENCES `geodata`.`points`(`id_medico`) ON DELETE RESTRICT ON UPDATE CASCADE;"
    inserta_destino.execute(query2)
    bd_destino.commit()
        #Transformo datos
    query="INSERT INTO atencion (lk_paciente,lk_medico,fecha_atencion,motivo_consulta,revision_sistemas,subjetivo,objetivo,analisis,plan) \
        SELECT pk.nro_hclinica,mm.id_medico,aa.fecha_atencion,aa.motivo_consulta,aa.revision_sistemas,aa.subjetivo,aa.objetivo,aa.analisis,aa.plan \
            FROM amaymed.atencion as aa, amaymed.paciente as pp,geodata.points as mm,amaymed.medico as am,gesmed.paciente_pk as pk \
            WHERE pp.nombre_completo=pk.nombre_completo AND aa.medico_atiende=am.nombre_medico AND pk.nombre_completo=aa.nombre_paciente \
                AND (length(aa.motivo_consulta)>2 AND length(aa.subjetivo)>2 AND length(aa.objetivo)>2 AND length(aa.analisis)>2 AND length(aa.plan)>2)\
                    ORDER BY aa.id_atencion"
    inserta_destino.execute(query)
    bd_destino.commit()
    
    print("Atencion Ok")

def modifica_diagnostico():
    query="CREATE TABLE `diagnostico` (`id_diagnostico` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,\
        `lk_paciente` int(11) COLLATE utf8_spanish2_ci NOT NULL,\
        `lk_cie10` varchar(11) COLLATE utf8_spanish2_ci NOT NULL,\
        `tipo` varchar(14) COLLATE utf8_spanish2_ci NOT NULL,\
        `fecha_diagnostico` date NOT NULL,\
        `fecha_inicio_aparente` date NOT NULL,\
        `lk_medico` int(11) COLLATE utf8_spanish2_ci NOT NULL,\
        `observaciones` mediumtext COLLATE utf8_spanish2_ci DEFAULT NULL,\
        `noduplicados` varchar(22) COLLATE utf8_spanish2_ci DEFAULT NULL\
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci;"
    inserta_destino.execute(query)
    bd_destino.commit()
    #Añade claves foraneas
    query="ALTER TABLE `diagnostico` ADD UNIQUE KEY `noduplicados` (`noduplicados`),\
        ADD KEY `lk_paciente` (`lk_paciente`),\
        ADD KEY `lk_cie10` (`lk_cie10`),\
        ADD KEY `lk_medico` (`lk_medico`);"
    inserta_destino.execute(query)
    bd_destino.commit()
    query2="ALTER TABLE `diagnostico` ADD FOREIGN KEY (`lk_paciente`) REFERENCES `paciente` (`nro_hclinica`) ON UPDATE CASCADE"
    inserta_destino.execute(query2)
    bd_destino.commit()
    query3="ALTER TABLE `diagnostico` ADD FOREIGN KEY (`lk_cie10`) REFERENCES `cie10` (`cod_cie10`) ON UPDATE CASCADE"
    inserta_destino.execute(query3)
    bd_destino.commit()
    query4="ALTER TABLE `diagnostico` ADD FOREIGN KEY (`lk_medico`) REFERENCES `geodata`.`points` (`id_medico`) ON UPDATE CASCADE"
    inserta_destino.execute(query4)
    bd_destino.commit()
        #Inserta Valores
    query="INSERT INTO diagnostico (lk_paciente,lk_cie10,tipo,fecha_diagnostico,fecha_inicio_aparente,lk_medico,observaciones,noduplicados) \
            SELECT pg.nro_hclinica,ad.cod_cie10,ad.tipo,ad.fecha_diagnostico,ad.fecha_inicio_aparente,mg.id_medico,ad.observaciones,CONCAT(ad.cod_cie10,'.',ad.cod_cie10,'.',LPAD(pg.nro_hclinica, 8, '0')) as noduplicados\
            FROM amaymed.diagnostico as ad, gesmed.paciente_pk as pg, geodata.points as mg \
            WHERE ad.nombre_paciente=pg.nombre_completo AND mg.nombre_medico=ad.medico_diagnostica"
    inserta_destino.execute(query)
    bd_destino.commit()
    print("Diagnosticos Ok")

def modifica_relacion_atencion_diagnostico():
    # Nueva Vista para encontrar relacion de id_atencion entre amaymed y gesmed
        #Creamos vistas de paso para las tablas de atencion amaymed y para gesmed
        #Combinamos 9 primeros caracteres de los campos: motivo_consulta, subjetivo, objetivo, analisis,plan para crear una clave única
        #Hacemos un join entre las 2 vistas de paso

    #vista paso amaymed
    query="CREATE OR REPLACE VIEW atencion_amaymed AS SELECT id_atencion,CONCAT(SUBSTRING(a.motivo_consulta, 1, 9),SUBSTRING(a.subjetivo, 1, 9),SUBSTRING(a.objetivo, 1, 9),SUBSTRING(a.analisis, 1, 9),SUBSTRING(a.plan, 1, 9)) as clave\
            FROM amaymed.atencion as a"
    inserta_destino.execute(query)
    bd_destino.commit()
    #Vista paso gesmed
    query="CREATE OR REPLACE VIEW atencion_gesmed AS SELECT id_atencion,CONCAT(SUBSTRING(a.motivo_consulta, 1, 9),SUBSTRING(a.subjetivo, 1, 9),SUBSTRING(a.objetivo, 1, 9),SUBSTRING(a.analisis, 1, 9),SUBSTRING(a.plan, 1, 9)) as clave\
            FROM gesmed.atencion as a"
    inserta_destino.execute(query)
    bd_destino.commit()
    #Join dos vistas de paso
    query="CREATE OR REPLACE VIEW atencion_amaymed_gesmed AS SELECT amed.id_atencion as id_atencion_amaymed,gmed.id_atencion as id_atencion_gesmed\
        FROM gesmed.atencion_amaymed AS amed,gesmed.atencion_gesmed AS gmed \
            WHERE amed.clave=gmed.clave"
    inserta_destino.execute(query)
    bd_destino.commit()

    #vista de paso para relacionar diagnosticos amaymed y gesmed
        #Vista diagnostico amaymed
    query="CREATE OR REPLACE VIEW diagnostico_amaymed AS SELECT id_diagnostico, CONCAT(ad.cod_cie10,'.',ad.cod_cie10,'.',LPAD(pg.nro_hclinica, 8, '0')) as noduplicados \
        FROM amaymed.diagnostico as ad, gesmed.paciente_pk as pg\
            WHERE ad.nombre_paciente=pg.nombre_completo"
    inserta_destino.execute(query)
    bd_destino.commit()
        #join vista amaymed y diagnostico gesmed
    query="CREATE OR REPLACE VIEW diagnostico_amaymed_gesmed AS SELECT ad.id_diagnostico as id_diagnostico_amaymed,gd.id_diagnostico as id_diagnostico_gesmed\
        FROM diagnostico_amaymed as ad, gesmed.diagnostico as gd\
            WHERE ad.noduplicados=gd.noduplicados"
    inserta_destino.execute(query)
    bd_destino.commit()
    
    #Ahora si creamos la tabla  relacion Atencion-Diagnóstico
    query="CREATE TABLE `rel_atencion_diagnostico` (\
        `id_relacion` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,\
        `lk_atencion` int(11) NOT NULL,\
        `lk_diagnostico` int(11) NOT NULL,\
        `noduplicarelacion` varchar(18) COLLATE utf8_spanish2_ci NOT NULL\
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci;"
    inserta_destino.execute(query)
    bd_destino.commit()

    query="ALTER TABLE `rel_atencion_diagnostico`\
        ADD UNIQUE KEY `noduplicarelacion` (`noduplicarelacion`),\
        ADD KEY `lk_atencion` (`lk_atencion`),\
        ADD KEY `lk_diagnostico` (`lk_diagnostico`);"
    inserta_destino.execute(query)
    bd_destino.commit()

    query="ALTER TABLE `rel_atencion_diagnostico`\
        ADD CONSTRAINT `rel_atencion_diagnostico_ibfk_1` FOREIGN KEY (`lk_atencion`) REFERENCES `atencion` (`id_atencion`) ON DELETE CASCADE ON UPDATE CASCADE,\
        ADD CONSTRAINT `rel_atencion_diagnostico_ibfk_3` FOREIGN KEY (`lk_diagnostico`) REFERENCES `diagnostico` (`id_diagnostico`) ON DELETE CASCADE ON UPDATE CASCADE;"
    inserta_destino.execute(query)
    bd_destino.commit()

    # insertamos información
    query="INSERT INTO rel_atencion_diagnostico (lk_atencion,lk_diagnostico,noduplicarelacion) \
        SELECT at.id_atencion_gesmed,dg.id_diagnostico_gesmed,CONCAT(LPAD(at.id_atencion_gesmed, 8, '0'),'.',LPAD(dg.id_diagnostico_gesmed, 8, '0'))\
        FROM amaymed.rel_atencion_diagnostico as rl, gesmed.atencion_amaymed_gesmed as at,gesmed.diagnostico_amaymed_gesmed as dg\
            WHERE rl.id_atencion=at.id_atencion_amaymed AND rl.id_diagnostico=dg.id_diagnostico_amaymed "
    inserta_destino.execute(query)
    bd_destino.commit()
    print("Relacion Ok")

def modifica_prescripcion_medicamentos():
    query="CREATE TABLE `prescripcion` (\
        `id_prescripcion` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,\
        `lk_paciente` int(11) NOT NULL,\
        `lk_atencion` int(11) NOT NULL,\
        `fecha_prescripcion` date NOT NULL,\
        `concentracion` varchar(30) COLLATE utf8_spanish2_ci NOT NULL,\
        `cantidad` int(2) NOT NULL,\
        `lk_presentacion` int(11) NOT NULL,\
        `indicaciones` text COLLATE utf8_spanish2_ci NOT NULL,\
        `lk_generico` int(11) NOT NULL\
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci;"
    inserta_destino.execute(query)
    bd_destino.commit()

    query="ALTER TABLE `prescripcion`\
        ADD KEY `lk_paciente` (`lk_paciente`),\
        ADD KEY `lk_atencion` (`lk_atencion`),\
        ADD KEY `lk_presentacion` (`lk_presentacion`),\
        ADD KEY `lk_generico` (`lk_generico`);"
    inserta_destino.execute(query)
    bd_destino.commit()

    query="ALTER TABLE `prescripcion`\
        ADD CONSTRAINT `prescripcion_ok_ibfk_1` FOREIGN KEY (`lk_generico`) REFERENCES `medicamentos` (`cod_gen`) ON UPDATE CASCADE,\
        ADD CONSTRAINT `prescripcion_ok_ibfk_2` FOREIGN KEY (`lk_paciente`) REFERENCES `paciente` (`nro_hclinica`) ON UPDATE CASCADE,\
        ADD CONSTRAINT `prescripcion_ok_ibfk_3` FOREIGN KEY (`lk_atencion`) REFERENCES `atencion` (`id_atencion`),\
        ADD CONSTRAINT `prescripcion_ok_ibfk_4` FOREIGN KEY (`lk_presentacion`) REFERENCES `presentacion_medicamentos` (`id_presentacion`) ON UPDATE CASCADE;"
    inserta_destino.execute(query)
    bd_destino.commit()

    #Hay que afinar este query porque al parecer no coinciden las prescripciones de medicamentos de amaymed y gesmed, hay menos en gesmed y 
    #falta comprobar que todas las relaciones se cumplan y den la información correcta.
    query="INSERT INTO prescripcion (lk_paciente,lk_atencion,fecha_prescripcion,concentracion,cantidad,lk_presentacion,indicaciones,lk_generico)\
        SELECT pac.nro_hclinica,a.id_atencion,p.fecha_prescripcion,p.concentracion,p.cantidad,pm.id_presentacion,p.indicaciones,p.el_generico \
            FROM gesmed.paciente as pac,amaymed.prescripcion_ok as p, gesmed.atencion as a,gesmed.presentacion_medicamentos as pm,amaymed.presentacion_medicamentos as pma\
            WHERE p.el_paciente=pac.nombre_completo AND a.id_atencion=p.atencion_relacionada AND pm.nombre_presentacion=pma.nombre_presentacion AND pac.es_activo=1\
            GROUP BY p.el_generico,p.concentracion,p.fecha_prescripcion,p.indicaciones,p.cantidad,p.presentacion"
    inserta_destino.execute(query)
    bd_destino.commit()
    print("Prescripcion Medicamentos Ok")


def principal():
    #Nos conectamos a las bases de datos
    conexion()
    ####### creamos las tablas fijas ##############
    #crear_tablas_fijas()
    #traslada_cie10()
    #traslada_presentacion_medicamentos()
    #traslada_medicamentos()
    traslada_seguro_medico()
    ####### creamos tablas modificadas ############
    ##modifica_paciente()
    ##modifica_atencion()
    ##modifica_diagnostico()
    ##modifica_relacion_atencion_diagnostico()
    ##modifica_prescripcion_medicamentos()

principal()