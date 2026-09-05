"""
migrar_impresos.py — Migra todos los reportes de amaymed al motor paramétrico de gesmed.

Reportes migrados:
  receta            – Prescripción de medicamentos
  certificado       – Certificado médico
  form001           – Caratula Historia Clínica (antecedentes)
  form002           – Historia Clínica (ya existente, se omite si existe)
  pedido_laboratorio – Pedido de exámenes de laboratorio (ya existente)
  pedido_imagen     – Pedido de exámenes de imagen

Uso:
  python migrations/migrar_impresos.py [--limpiar]
"""

import json
import os
import sys
from pathlib import Path

import pymysql

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

_DB = dict(host="localhost", user="med_admin", password="gesmed01",
           database="gesmed", charset="utf8mb4")

# ── Formato: amaymed → gesmed ─────────────────────────────────────────────────

def fmt(old: str) -> str:
    """Convierte el código de formato antiguo (NN09.01.01.LUXX) al nuevo (09.01.01.00.NLU.0000)."""
    old = (old or "NN09").strip()
    if len(old) < 4:
        return "09.01.01.00.NLU.0000"

    estilo_map = {"N": "N", "B": "B", "S": "S", "Q": "Q"}
    estilo = estilo_map.get(old[1], "N")
    size   = old[2:4]

    if len(old) < 11:
        return f"{size}.01.01.00.{estilo}LU.0000"

    merge_v  = old[5:7]
    merge_h  = old[8:10]
    align_h  = old[11] if len(old) > 11 and old[11] in "LCR" else "L"
    align_v  = old[12] if len(old) > 12 and old[12] in "UCD" else "U"
    shadow   = "13" if len(old) > 13 and old[13] == "F" else "00"
    bchr     = old[14] if len(old) > 14 else "X"
    borders  = {"Q": "1111", "U": "1000", "D": "0010",
                "L": "0001", "R": "0100", "X": "0000"}.get(bchr, "0000")

    return f"{size}.{merge_h}.{merge_v}.{shadow}.{estilo}{align_h}{align_v}.{borders}"


# ── Helpers de inserción ──────────────────────────────────────────────────────

def add_impreso(cur, nombre, fuente="Arial Narrow", explica=""):
    cur.execute("SELECT id_impreso FROM impreso WHERE nombre_reporte=%s", (nombre,))
    row = cur.fetchone()
    if row:
        print(f"  ⚠  {nombre} ya existe (id={row[0]}) — omitido")
        return None
    cur.execute(
        "INSERT INTO impreso (nombre_reporte, nombre_fuente, explica) VALUES (%s,%s,%s)",
        (nombre, fuente, explica)
    )
    return cur.lastrowid


def add_sec(cur, iid, orden, sql, params, explica):
    cur.execute(
        "INSERT INTO seccion (lk_impreso,orden,instruccion_sql,parametros_in,explica) "
        "VALUES (%s,%s,%s,%s,%s)",
        (iid, orden, sql, json.dumps(params) if params else None, explica)
    )
    return cur.lastrowid


def cel(cur, sid, var, fila, col, pre, post, formato, explica=""):
    cur.execute(
        "INSERT INTO celda (lk_seccion,variable,fila,columna,pre_fijo,post_fijo,formato,explica) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
        (sid, var, fila, col, pre, post, formato, explica)
    )


# ── RECETA ────────────────────────────────────────────────────────────────────

def migrar_receta(cur):
    iid = add_impreso(cur, "receta", "Arial Narrow", "Receta de prescripción médica")
    if not iid:
        return

    # Sección 1: datos del médico
    s1 = add_sec(cur, iid, 1,
        "SELECT p.nombre_medico, p.especialidad, p.cod_especialidad, p.celular, p.email "
        "FROM points p WHERE p.id_medico = :lk_medico",
        ["lk_medico"], "Datos del médico")
    cel(cur, s1, "nombre_medico",    1,  2, "", "", fmt("NB14"),           "Nombre médico col izq")
    cel(cur, s1, "nombre_medico",    1,  7, "", "", fmt("NB14"),           "Nombre médico col der")
    cel(cur, s1, "especialidad",     2,  2, "", "", fmt("NN08.01.01.LUXX"), "Especialidad izq")
    cel(cur, s1, "especialidad",     2,  7, "", "", fmt("NN08.01.01.LUXX"), "Especialidad der")
    cel(cur, s1, "celular",          5,  3, "", "", fmt("NN09.01.01.LUXX"), "Celular izq")
    cel(cur, s1, "celular",          5,  9, "", "", fmt("NN09.01.01.LUXX"), "Celular der")
    cel(cur, s1, "email",            6,  2, "", "", fmt("NN09"),            "Email izq")
    cel(cur, s1, "email",            6,  7, "", "", fmt("NN09"),            "Email der")
    cel(cur, s1, "nombre_medico",   42,  3, "", "", fmt("NB08.01.01.LUXX"), "Firma izq")
    cel(cur, s1, "nombre_medico",   42,  8, "", "", fmt("NB08.01.01.LUXX"), "Firma der")
    cel(cur, s1, "cod_especialidad", 43,  3, "", "", fmt("CN08.01.01.LUXX"), "Código especialidad izq")
    cel(cur, s1, "cod_especialidad", 43,  8, "", "", fmt("CN08.01.01.LUXX"), "Código especialidad der")
    cel(cur, s1, "especialidad",     44,  3, "", "", fmt("NN09.01.01.CUXX"), "Esp. pie izq")

    # Sección 2: datos paciente (encriptados → decryption automática en motor)
    s2 = add_sec(cur, iid, 2,
        "SELECT p.nombre_completo, p.cedula_id FROM paciente p WHERE p.nro_hclinica = :lk_paciente",
        ["lk_paciente"], "Datos del paciente (encriptados)")
    cel(cur, s2, "nombre_completo",  8,  3, "", "", fmt("NB09"),  "Nombre paciente izq")
    cel(cur, s2, "nombre_completo",  8,  8, "", "", fmt("NB09"),  "Nombre paciente der")

    # Sección 3: diagnóstico vinculado
    s3 = add_sec(cur, iid, 3,
        "SELECT GROUP_CONCAT(CONCAT('[', d.lk_cie10, ']: ', c.nomdiagnostico) "
        "ORDER BY d.id_diagnostico SEPARATOR '\n') AS diagnostico "
        "FROM diagnostico d JOIN cie10 c ON c.cod_cie10=d.lk_cie10 "
        "JOIN rel_atencion_diagnostico r ON r.lk_diagnostico=d.id_diagnostico "
        "WHERE r.lk_atencion = :lk_atencion AND d.tipo != 'Ant.Personal'",
        ["lk_atencion"], "Diagnóstico vinculado")
    cel(cur, s3, "diagnostico", 10,  2, "", "", fmt("CN07.01.01.LUXX"), "Diagnóstico izq")

    # Sección 4: alergias
    s4 = add_sec(cur, iid, 4,
        "SELECT GROUP_CONCAT(a.sustancia_alergia ORDER BY a.id_alergia SEPARATOR ' // ') AS alergias "
        "FROM alergia a WHERE a.lk_paciente = :lk_paciente",
        ["lk_paciente"], "Alergias del paciente")
    cel(cur, s4, "alergias", 12,  2, "", "", fmt("NN07.01.01.LUXX"), "Alergias")

    # Sección 5: cuidados generales
    s5 = add_sec(cur, iid, 5,
        "SELECT pc.cuidados_generales AS cuidados FROM prescripcion_cuidados pc "
        "WHERE pc.lk_atencion = :lk_atencion",
        ["lk_atencion"], "Cuidados generales de la prescripción")
    cel(cur, s5, "cuidados", 42,  7, "", "", fmt("NN09.04.04.LUXX"), "Cuidados")

    # Sección 6: items de prescripción (lista con GROUP_CONCAT)
    s6 = add_sec(cur, iid, 6,
        "SELECT GROUP_CONCAT("
        "CONCAT(m.nombre_generico, ' ', p.concentracion, '\n', "
        "'# ', p.cantidad, ' - ', IFNULL(mp.nombre_presentacion,''), '\n', "
        "p.indicaciones) "
        "ORDER BY p.id_prescripcion SEPARATOR '\n\n') AS lista_prescripcion "
        "FROM prescripcion p "
        "JOIN medicamentos m ON m.cod_gen=p.lk_generico "
        "LEFT JOIN medicamento_presentacion mp ON mp.id_presentacion=p.lk_presentacion "
        "WHERE p.lk_atencion = :lk_atencion",
        ["lk_atencion"], "Items de prescripción (lista)")
    cel(cur, s6, "lista_prescripcion", 14,  2, "", "", fmt("NN09.01.24.LUXX"), "Prescripción col izq")

    # Sección 7: fecha de impresión
    s7 = add_sec(cur, iid, 7,
        "SELECT DATE(NOW()) AS fecha_impresion",
        [], "Fecha de impresión")
    cel(cur, s7, "fecha_impresion",  7,  3, "", "", fmt("NN09"), "Fecha izq")
    cel(cur, s7, "fecha_impresion",  7,  8, "", "", fmt("NN09"), "Fecha der")

    # Sección 8: títulos estáticos
    s8 = add_sec(cur, iid, 8, None, None, "Títulos estáticos receta")
    # Amaymed usaba imagenes para logos → en nueva versión van en la plantilla xlsx
    print(f"  ✓  receta (id={iid})")


# ── CERTIFICADO ───────────────────────────────────────────────────────────────

def migrar_certificado(cur):
    iid = add_impreso(cur, "certificado", "Arial Narrow", "Certificado Médico")
    if not iid:
        return

    # Sección 1: datos del médico
    s1 = add_sec(cur, iid, 1,
        "SELECT p.nombre_medico, p.especialidad, p.cod_especialidad, p.celular, p.email "
        "FROM points p WHERE p.id_medico = :lk_medico",
        ["lk_medico"], "Datos del médico")
    cel(cur, s1, "nombre_medico",    2, 10, "", "", fmt("NB11.01.01.LUXX"), "Nombre médico")
    cel(cur, s1, "especialidad",     3, 10, "", "", fmt("NN09.01.01.LUXX"), "Especialidad")
    cel(cur, s1, "cod_especialidad", 45, 12, "", "", fmt("NN08.01.07.CUXX"), "Código")
    cel(cur, s1, "celular",          6, 18, "", "", fmt("NN09.01.01.LUXX"), "Celular")
    cel(cur, s1, "email",            7, 10, "", "", fmt("NN09"),            "Email")
    cel(cur, s1, "especialidad",     46,  9, "", "", fmt("NN09.01.14.CUXX"), "Especialidad pie")
    cel(cur, s1, "nombre_medico",   44, 10, "", "", fmt("NB09.01.12.CUXX"), "Firma")

    # Sección 2: datos del paciente (encriptados)
    s2 = add_sec(cur, iid, 2,
        "SELECT p.nombre_completo AS nombre_paciente, p.cedula_id AS cedula, "
        "p.ciudad_reside AS ciudad_reside, p.direccion_reside AS direccion_reside, "
        "p.tf_celular AS tf_celular, p.nro_hclinica AS historia_clinica "
        "FROM paciente p WHERE p.nro_hclinica = :lk_paciente",
        ["lk_paciente"], "Datos del paciente (encriptados)")
    cel(cur, s2, "nombre_paciente",  13,  5, "", "", fmt("NB09.01.16.LUXX"), "Nombre paciente")
    cel(cur, s2, "cedula",           14,  9, "", "", fmt("NN09.01.05.LUXX"), "Cédula")
    cel(cur, s2, "ciudad_reside",    14, 22, "", "", fmt("NN09.01.08.LUXX"), "Ciudad")
    cel(cur, s2, "direccion_reside", 15,  4, "", "", fmt("NN09.01.18.LUXX"), "Dirección")
    cel(cur, s2, "tf_celular",       15, 25, "", "", fmt("NN09.01.06.LUXX"), "Celular paciente")
    cel(cur, s2, "historia_clinica", 13, 25, "", "", fmt("NB10.01.04.LUXX"), "HC #")

    # Sección 3: datos de la atención
    s3 = add_sec(cur, iid, 3,
        "SELECT DATE(a.fecha_atencion) AS fecha_atencion FROM atencion a "
        "WHERE a.id_atencion = :lk_atencion",
        ["lk_atencion"], "Fecha de la atención")
    cel(cur, s3, "fecha_atencion",  18,  9, "", "", fmt("NB09.01.09.LUXX"), "Fecha atención")

    # Sección 4: primer diagnóstico vinculado
    s4 = add_sec(cur, iid, 4,
        "SELECT d.lk_cie10 AS cie1, c.nomdiagnostico AS diagnostico1, d.tipo AS tipo1 "
        "FROM diagnostico d JOIN cie10 c ON c.cod_cie10=d.lk_cie10 "
        "JOIN rel_atencion_diagnostico r ON r.lk_diagnostico=d.id_diagnostico "
        "WHERE r.lk_atencion = :lk_atencion AND d.tipo != 'Ant.Personal' "
        "ORDER BY d.id_diagnostico LIMIT 1",
        ["lk_atencion"], "Primer diagnóstico")
    cel(cur, s4, "cie1",         21,  1, "", "", fmt("NN09.01.03.LUXQ"), "CIE1")
    cel(cur, s4, "diagnostico1", 21,  4, "", "", fmt("NN08.01.22.LUXQ"), "Diagnóstico1")
    cel(cur, s4, "tipo1",        21, 26, "", "", fmt("NN08.01.04.LUXQ"), "Tipo1")

    # Sección 5: fecha impresión y reposo (valores en blanco — se completan en UI)
    s5 = add_sec(cur, iid, 5,
        "SELECT DATE(NOW()) AS fecha",
        [], "Fecha impresión")
    cel(cur, s5, "fecha",  9, 21, "", "", fmt("NN09.01.09.RUXX"), "Fecha impresión")

    # Sección 6: títulos estáticos
    s6 = add_sec(cur, iid, 6, None, None, "Títulos fijos certificado")
    titulos_cert = [
        (11, 10, "CERTIFICADO MÉDICO",                  fmt("NB11.01.09.CUXX")),
        (13,  1, "El (la) paciente:",                   fmt("NN09.01.01.LUXX")),
        (14,  1, "con documento de identidad:",         fmt("NN09.01.08.LUXX")),
        (18,  1, "fue atendido(a) en mi consulta el:",  fmt("NN09.01.08.LUXX")),
        (19,  1, "con el siguiente diagnostico:",       fmt("NN09.01.08.LUXX")),
        (20,  1, "CIE 10:",                             fmt("NN09.01.03.LUFQ")),
        (20,  4, "Detalle diagnóstico:",                fmt("NN09.01.22.LUFQ")),
        (20, 26, "Tipo:",                               fmt("NN09.01.04.LUFQ")),
        (33,  1, "Observaciones:",                      fmt("NB09.01.05.LUXX")),
        (38,  1, "Es todo cuanto puedo certificar en honor a la verdad.", fmt("NN09.01.16.LUXX")),
    ]
    for fila, col, texto, formato in titulos_cert:
        cel(cur, s6, None, fila, col, texto, "", formato)

    print(f"  ✓  certificado (id={iid})")


# ── FORM001 ───────────────────────────────────────────────────────────────────

def migrar_form001(cur):
    iid = add_impreso(cur, "form001", "Arial Narrow",
                      "Carátula Historia Clínica (Antecedentes)")
    if not iid:
        return

    # Sección 1: datos del paciente
    s1 = add_sec(cur, iid, 1,
        "SELECT p.nro_hclinica, p.nombre_completo AS nombre2, "
        "p.fecha_nacimiento AS f_nacimiento, p.cedula_id AS cedula_p, "
        "p.seguro, p.grupo_sanguineo AS grupo_sang, p.estado_civil AS e_civil, "
        "p.pais_nacimiento AS nacionalidad, p.nro_hclinica AS nro_hclinica2 "
        "FROM paciente p WHERE p.nro_hclinica = :lk_paciente",
        ["lk_paciente"], "Datos del paciente")
    cel(cur, s1, "nombre2",       1,  8, "", "", fmt("NB14.02.14.CCFQ"),  "Nombre paciente")
    cel(cur, s1, "f_nacimiento",  8,  8, "", "", fmt("NN09.01.05.CUXQ"),  "Fecha nacimiento")
    cel(cur, s1, "cedula_p",      5,  8, "", "", fmt("NN09.01.05.CUXQ"),  "Cédula")
    cel(cur, s1, "seguro",        5, 17, "", "", fmt("NN09.01.05.CUXQ"),  "Seguro")
    cel(cur, s1, "grupo_sang",    1, 22, "", "", fmt("NB14.02.03.CCXQ"),  "Grupo sanguíneo")
    cel(cur, s1, "e_civil",       8, 13, "", "", fmt("NN09.01.04.CUXQ"),  "Estado civil")
    cel(cur, s1, "nacionalidad",  8, 17, "", "", fmt("NN09.01.05.CUXQ"),  "Nacionalidad")
    cel(cur, s1, "nro_hclinica2", 5, 13, "", "", fmt("NN09.01.04.CUXQ"),  "Nro HC2")

    # Sección 2: antecedentes personales (lista)
    s2 = add_sec(cur, iid, 2,
        "SELECT GROUP_CONCAT("
        "CONCAT('[', IFNULL(d.fecha_inicio_aparente,''), ']: ', "
        "c.nomdiagnostico, ' (', d.lk_cie10, ')') "
        "ORDER BY d.fecha_inicio_aparente DESC SEPARATOR '\n') AS ant_personal "
        "FROM diagnostico d JOIN cie10 c ON c.cod_cie10=d.lk_cie10 "
        "WHERE d.lk_paciente = :lk_paciente AND d.tipo = 'Ant.Personal'",
        ["lk_paciente"], "Antecedentes personales")
    cel(cur, s2, "ant_personal", 11,  1, "", "", fmt("NN08.13.24.LUXQ"), "Antecedentes personales")

    # Sección 3: antecedentes familiares — NOTE: no existe tabla en gesmed
    # Se deja como sección estática vacía (se completará manualmente)

    # Sección 4: alergias
    s4 = add_sec(cur, iid, 4,
        "SELECT a.sustancia_alergia AS alergia_sust, "
        "IFNULL(a.detalles,'') AS alergia_coment "
        "FROM alergia a WHERE a.lk_paciente = :lk_paciente LIMIT 1",
        ["lk_paciente"], "Primera alergia (posición fija)")
    cel(cur, s4, "alergia_sust",   42,  1, "", "", fmt("NN08.02.09.LUXQ"), "Sustancia alergia")
    cel(cur, s4, "alergia_coment", 42, 10, "", "", fmt("NN07.02.15.LUXQ"), "Comentario alergia")

    # Sección 5: títulos estáticos
    s5 = add_sec(cur, iid, 5, None, None, "Títulos fijos form001")
    titulos_f1 = [
        ( 7,  8, "Fecha Nacimiento",  fmt("NN08.01.05.CUFQ")),
        ( 4,  8, "Doc.Identidad",     fmt("NN08.01.05.CUFQ")),
        ( 4, 13, "No. H.Clínica",     fmt("NN07.01.04.CUFQ")),
        ( 4, 17, "Seguro",            fmt("NN08.01.05.CUFQ")),
        ( 7, 13, "Estado Civil",      fmt("NN08.01.04.CUFQ")),
        ( 7, 17, "Nacionalidad",      fmt("NN08.01.05.CUFQ")),
        (10,  1, "2. ANTECEDENTES PERSONALES", fmt("NB09.01.24.LUFQ")),
        (25,  1, "3. ANTECEDENTES FAMILIARES", fmt("NB09.01.24.LUFQ")),
        (40,  1, "4. ALERGIAS",               fmt("NB09.01.24.LUFQ")),
        (41,  1, "SUSTANCIA",                 fmt("NB09.01.09.CUFQ")),
        (41, 10, "OBSERVACIONES",             fmt("NB09.01.15.CUFQ")),
    ]
    for fila, col, texto, formato in titulos_f1:
        cel(cur, s5, None, fila, col, texto, "", formato)

    print(f"  ✓  form001 (id={iid})")


# ── PEDIDO_IMAGEN ─────────────────────────────────────────────────────────────

def migrar_pedido_imagen(cur):
    iid = add_impreso(cur, "pedido_imagen", "Arial Narrow",
                      "Pedido de Exámenes de Imagen")
    if not iid:
        return

    # Sección 1: datos del médico (se repiten en dos posiciones: cols ~13 y ~44)
    s1 = add_sec(cur, iid, 1,
        "SELECT p.nombre_medico, p.especialidad, p.cod_especialidad, p.celular, p.email "
        "FROM points p WHERE p.id_medico = :lk_medico",
        ["lk_medico"], "Datos del médico")
    # Copia 1 (mitad izquierda)
    cel(cur, s1, "nombre_medico",    3, 13, "", "", fmt("NB10.01.01.LUXX"), "Médico izq")
    cel(cur, s1, "especialidad",     4, 13, "", "", fmt("NN09.01.01.LUXX"), "Especialidad izq")
    cel(cur, s1, "celular",          7, 24, "", "", fmt("NN09.01.01.LUXX"), "Celular izq")
    cel(cur, s1, "email",            8, 13, "", "", fmt("NN09.01.01.LUXX"), "Email izq")
    # Copia 2 (mitad derecha)
    cel(cur, s1, "nombre_medico",    3, 44, "", "", fmt("NB10.01.01.LUXX"), "Médico der")
    cel(cur, s1, "especialidad",     4, 44, "", "", fmt("NN09.01.01.LUXX"), "Especialidad der")
    cel(cur, s1, "celular",          7, 55, "", "", fmt("NN09.01.01.LUXX"), "Celular der")
    cel(cur, s1, "email",            8, 44, "", "", fmt("NN09.01.01.LUXX"), "Email der")

    # Sección 2: datos del paciente
    s2 = add_sec(cur, iid, 2,
        "SELECT p.nombre_completo AS nombre_paciente, p.cedula_id AS doc_id "
        "FROM paciente p WHERE p.nro_hclinica = :lk_paciente",
        ["lk_paciente"], "Datos del paciente")
    cel(cur, s2, "nombre_paciente", 12,  7, "", "", fmt("NB09.01.18.LUXX"), "Nombre izq")
    cel(cur, s2, "doc_id",          13,  7, "", "", fmt("NN08.01.08.LUXX"), "Doc.ID izq")
    cel(cur, s2, "nombre_paciente", 12, 38, "", "", fmt("NB09.01.18.LUXX"), "Nombre der")
    cel(cur, s2, "doc_id",          13, 38, "", "", fmt("NN08.01.08.LUXX"), "Doc.ID der")

    # Sección 3: fecha
    s3 = add_sec(cur, iid, 3,
        "SELECT DATE(NOW()) AS fecha",
        [], "Fecha impresión")
    cel(cur, s3, "fecha", 11,  7, "", "", fmt("NN08.01.01.LUXX"), "Fecha izq")
    cel(cur, s3, "fecha", 11, 38, "", "", fmt("NN08.01.01.LUXX"), "Fecha der")

    # Sección 4: hasta 3 diagnósticos vinculados
    s4 = add_sec(cur, iid, 4,
        "SELECT "
        "MAX(CASE WHEN n=1 THEN CONCAT('[',lk_cie10,']: ',nomdiagnostico) END) AS diagnostico1, "
        "MAX(CASE WHEN n=2 THEN CONCAT('[',lk_cie10,']: ',nomdiagnostico) END) AS diagnostico2, "
        "MAX(CASE WHEN n=3 THEN CONCAT('[',lk_cie10,']: ',nomdiagnostico) END) AS diagnostico3 "
        "FROM (SELECT d.lk_cie10, c.nomdiagnostico, "
        "ROW_NUMBER() OVER (ORDER BY d.id_diagnostico) AS n "
        "FROM diagnostico d JOIN cie10 c ON c.cod_cie10=d.lk_cie10 "
        "JOIN rel_atencion_diagnostico r ON r.lk_diagnostico=d.id_diagnostico "
        "WHERE r.lk_atencion=:lk_atencion AND d.tipo!='Ant.Personal') sub",
        ["lk_atencion"], "Diagnósticos (3 máximo)")
    for i in range(1, 4):
        fila = 13 + i   # 14, 15, 16
        cel(cur, s4, f"diagnostico{i}", fila,  7, "", "", fmt("NN08.01.22.LUXX"), f"Diag {i} izq")
        cel(cur, s4, f"diagnostico{i}", fila, 38, "", "", fmt("NN08.01.22.LUXX"), f"Diag {i} der")

    # Sección 5: pedido de imagen — campo libre (a completar en UI futura)
    s5 = add_sec(cur, iid, 5, None, None, "Pedido texto libre")
    cel(cur, s5, None, 20,  4, "", "", fmt("NN12.13.25.LUXX"), "Pedido izq (libre)")
    cel(cur, s5, None, 20, 37, "", "", fmt("NN12.13.25.LUXX"), "Pedido der (libre)")

    # Sección 6: títulos
    s6 = add_sec(cur, iid, 6, None, None, "Títulos fijos pedido imagen")
    titulos_pi = [
        ( 1, 13, "PEDIDO DE EXÁMENES IMAGEN",    fmt("NB12.01.01.LUXX")),
        ( 1, 44, "PEDIDO DE EXÁMENES IMAGEN",    fmt("NB12.01.01.LUXX")),
        (11,  3, "Fecha:",                        fmt("NN08.01.04.RUXX")),
        (12,  3, "Paciente:",                     fmt("NN08.01.04.RUXX")),
        (13,  1, "Doc. Identidad:",               fmt("NN08.01.06.RUXX")),
        (14,  2, "Diagnóstico:",                  fmt("NN08.01.05.RUXX")),
        (19,  1, "Pedido:",                       fmt("NN09.01.01.LUXX")),
        (11, 34, "Fecha:",                        fmt("NN08.01.04.RUXX")),
        (12, 34, "Paciente:",                     fmt("NN08.01.04.RUXX")),
        (13, 32, "Doc. Identidad:",               fmt("NN08.01.06.RUXX")),
        (14, 33, "Diagnóstico:",                  fmt("NN08.01.05.RUXX")),
        (19, 34, "Pedido:",                       fmt("NN09.01.01.LUXX")),
    ]
    for fila, col, texto, formato in titulos_pi:
        cel(cur, s6, None, fila, col, texto, "", formato)

    print(f"  ✓  pedido_imagen (id={iid})")


# ── Plantillas xlsx mínimas ───────────────────────────────────────────────────

def crear_plantilla(nombre, filas=50, columnas=24, orientacion="portrait"):
    from openpyxl import Workbook
    from openpyxl.styles import Font
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.page import PageMargins

    TEMPLATES = _ROOT / "GesmedWeb" / "templates"
    TEMPLATES.mkdir(exist_ok=True)
    path = TEMPLATES / f"{nombre}.xlsx"
    if path.exists():
        print(f"  ⚠  plantilla {nombre}.xlsx ya existe — omitida")
        return

    wb = Workbook()
    ws = wb.active
    ws.title = nombre

    default_font = Font(name="Arial Narrow", size=9)
    for row in ws.iter_rows(min_row=1, max_row=filas, min_col=1, max_col=columnas):
        for cell in row:
            cell.font = default_font

    ws.page_setup.orientation = orientacion
    ws.page_setup.paperSize = 9  # A4
    ws.page_margins = PageMargins(left=0.4, right=0.4, top=0.6, bottom=0.6,
                                  header=0.2, footer=0.2)
    ws.print_area = f"A1:{get_column_letter(columnas)}{filas}"

    wb.save(path)
    print(f"  ✓  plantilla {nombre}.xlsx creada")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limpiar", action="store_true",
                        help="Elimina TODOS los impresos antes de migrar")
    args = parser.parse_args()

    conn = pymysql.connect(**_DB)
    cur = conn.cursor()

    if args.limpiar:
        print("⚠  Limpiando tablas impreso/seccion/celda…")
        cur.execute("SET FOREIGN_KEY_CHECKS=0")
        for t in ("celda", "seccion", "impreso"):
            cur.execute(f"DELETE FROM {t}")
            cur.execute(f"ALTER TABLE {t} AUTO_INCREMENT = 1")
        cur.execute("SET FOREIGN_KEY_CHECKS=1")
        conn.commit()
        print("   Tablas vaciadas.\n")

    print("Migrando reportes…")
    migrar_receta(cur)
    migrar_certificado(cur)
    migrar_form001(cur)
    migrar_pedido_imagen(cur)
    conn.commit()

    print("\nCreando plantillas xlsx…")
    crear_plantilla("receta",            filas=50, columnas=13, orientacion="portrait")
    crear_plantilla("certificado",       filas=50, columnas=30, orientacion="portrait")
    crear_plantilla("form001",           filas=50, columnas=24, orientacion="portrait")
    crear_plantilla("pedido_imagen",     filas=42, columnas=64, orientacion="landscape")

    cur.close()
    conn.close()
    print("\nMigración completada.")


if __name__ == "__main__":
    main()
