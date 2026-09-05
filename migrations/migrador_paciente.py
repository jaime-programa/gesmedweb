"""
migrador_paciente.py — Migra amaymed.paciente → gesmed.paciente

AJUSTAR ANTES DE USAR:
    Revisar mapeo_campos() y verificar que los nombres de columna
    coincidan exactamente con los de la tabla amaymed.
    Revisar transformar_registro() para cualquier conversión de tipo necesaria.
"""

from __future__ import annotations

import datetime

from .migrador_base import MigradorTabla


class MigradorPaciente(MigradorTabla):

    def tabla_origen(self) -> str:
        return "paciente"          # ← nombre en amaymed (ajustar si difiere)

    def tabla_destino(self) -> str:
        return "paciente"

    def mapeo_campos(self) -> dict[str, str]:
        """
        Mapa: {columna_amaymed: columna_gesmed}
        None  = descartar columna (no existe en gesmed)

        ⚠ AJUSTAR según el esquema real de amaymed.
        """
        return {
            # Identidad
            "id_paciente":        "nro_hclinica",   # ajustar si la PK tiene otro nombre
            "nro_hclinica":       "nro_hclinica",   # si ya se llama igual en amaymed

            # Datos sensibles (se encriptarán)
            "nombre_completo":    "nombre_completo",
            "nombre_paciente":    "nombre_completo", # nombre alternativo en amaymed
            "cedula":             "cedula_id",       # nombre alternativo en amaymed
            "cedula_id":          "cedula_id",

            # Datos demográficos
            "sexo":               "sexo",
            "grupo_sanguineo":    "grupo_sanguineo",
            "fecha_nacimiento":   "fecha_nacimiento",
            "pais_nacimiento":    "pais_nacimiento",
            "estado_civil":       "estado_civil",

            # Contacto / residencia
            "ciudad_reside":      "ciudad_reside",
            "ciudad":             "ciudad_reside",   # nombre alternativo
            "direccion_reside":   "direccion_reside",
            "direccion":          "direccion_reside",
            "tf_celular":         "tf_celular",
            "celular":            "tf_celular",
            "email":              "email",

            # Salud / administración
            "seguro":             "seguro",
            "observacion":        "observacion",

            # Columnas de amaymed que NO existen en gesmed → descartar
            "antec_familiares":   None,
            "nacionalidad":       None,
            "provincia_reside":   None,
            "tf_domicilio":       None,
            "es_laboral":         None,
            "lugar_nacimiento":   None,
            "id_medico_tratante": None,
        }

    def campos_a_encriptar(self) -> list[str]:
        return ["nombre_completo", "cedula_id", "direccion_reside", "tf_celular", "email", "observacion"]

    def transformar_registro(self, registro: dict) -> dict:
        """
        Añade campos nuevos de gesmed que no existen en amaymed,
        y normaliza tipos de datos.
        """
        r = dict(registro)

        # fecha_nacimiento: asegurar tipo datetime.date
        fn = r.get("fecha_nacimiento")
        if isinstance(fn, str):
            try:
                r["fecha_nacimiento"] = datetime.date.fromisoformat(fn)
            except ValueError:
                # Intentar formato DD/MM/YYYY común en apps de escritorio
                r["fecha_nacimiento"] = datetime.datetime.strptime(fn, "%d/%m/%Y").date()
        elif isinstance(fn, datetime.datetime):
            r["fecha_nacimiento"] = fn.date()

        # Campos nuevos en gesmed que amaymed no tiene
        r.setdefault("fecha_creacion", datetime.datetime.now())
        r.setdefault("es_activo", 1)
        r.setdefault("pais_nacimiento", "Ecuador")
        r.setdefault("estado_civil", "")
        r.setdefault("grupo_sanguineo", "")
        r.setdefault("seguro", None)

        # Campos Optional[bytes]: si llegan como cadena vacía → None (no encriptar nulos)
        for campo_opt in ("email", "observacion"):
            val = r.get(campo_opt)
            if isinstance(val, str) and val.strip() == "":
                r[campo_opt] = None

        # Campos bytes requeridos: si llegan como cadena vacía → cadena vacía (se encriptará)
        for campo_req in ("direccion_reside", "tf_celular"):
            if campo_req not in r or r[campo_req] is None:
                r[campo_req] = ""

        # Normalizar nombre_completo a mayúsculas (igual que en la app)
        if r.get("nombre_completo") and isinstance(r["nombre_completo"], str):
            r["nombre_completo"] = r["nombre_completo"].upper().strip()

        return r
