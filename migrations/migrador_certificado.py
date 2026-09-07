"""
migrador_certificado.py — Migra amaymed.certificados → gesmed.certificado

Diferencias de esquema:
    amaymed: vincula_atencion (FK numérica a atencion.id_atencion, se conserva
             tal cual porque migrador_atencion.py preserva los id_atencion
             originales), actividad, que_cie10, tipo_cie.
    gesmed:  lk_atencion, ocupacion, fecha_certificado (no existe en amaymed).

    que_cie10 / tipo_cie no tienen columna equivalente en gesmed.certificado
    (el vínculo con el diagnóstico ya se maneja vía rel_atencion_diagnostico)
    → se descartan.

    Ninguna columna de gesmed.certificado es BLOB, por lo tanto no se cifra
    nada en esta tabla (a diferencia de paciente/diagnostico/prescripcion).

Requiere que atencion ya esté migrada (FK lk_atencion).
"""

from __future__ import annotations

import datetime

from .migrador_base import MigradorTabla


class MigradorCertificado(MigradorTabla):

    def tabla_origen(self) -> str:
        return "certificados"

    def tabla_destino(self) -> str:
        return "certificado"

    def mapeo_campos(self) -> dict[str, str]:
        return {
            "id_certificado":    "id_certificado",
            "vincula_atencion":  "lk_atencion",
            "reposo_desde":      "reposo_desde",
            "reposo_hasta":      "reposo_hasta",
            "contingencia":      "contingencia",
            "presenta_sintomas": "presenta_sintomas",
            "aislamiento":       "aislamiento",
            "actividad":         "ocupacion",
            "lugar_trabajo":     "lugar_trabajo",
            "observacion":       "observacion",

            # Columnas de amaymed que NO existen en gesmed.certificado → descartar
            "que_cie10":         None,
            "tipo_cie":          None,
        }

    def campos_a_encriptar(self) -> list[str]:
        return []   # gesmed.certificado no tiene columnas BLOB

    def transformar_registro(self, registro: dict) -> dict:
        r = dict(registro)

        # fecha_certificado no existe en amaymed.certificados → usar fecha de migración
        r.setdefault("fecha_certificado", datetime.datetime.now())
        fecha_respaldo = r["fecha_certificado"]
        if isinstance(fecha_respaldo, datetime.datetime):
            fecha_respaldo = fecha_respaldo.date()

        # Normalizar fechas a datetime.date
        for campo_fecha in ("reposo_desde", "reposo_hasta"):
            val = r.get(campo_fecha)
            if isinstance(val, str):
                val = val.strip()
                # MySQL "zero date" legado ('0000-00-00', también con hora
                # '0000-00-00 00:00:00'): significa "sin fecha", no un dato a
                # parsear — ni fromisoformat ni strptime("%d/%m/%Y") lo aceptan
                # y explotaban con ValueError, tirando la fila entera a error.
                # gesmed.certificado.reposo_desde/hasta son NOT NULL, así que
                # no se puede dejar en NULL: se usa fecha_certificado como
                # respaldo (equivale a "0 días de reposo" en vez de perder la fila).
                if not val or val.startswith("0000-00-00"):
                    r[campo_fecha] = fecha_respaldo
                else:
                    try:
                        r[campo_fecha] = datetime.date.fromisoformat(val)
                    except ValueError:
                        r[campo_fecha] = datetime.datetime.strptime(val, "%d/%m/%Y").date()
            elif isinstance(val, datetime.datetime):
                r[campo_fecha] = val.date()
            elif val is None:
                r[campo_fecha] = fecha_respaldo

        # Defaults NOT NULL de gesmed (por si amaymed trae NULL/vacío)
        r.setdefault("contingencia", "")
        r.setdefault("ocupacion", "")
        r.setdefault("lugar_trabajo", "")
        r.setdefault("observacion", "")
        r.setdefault("presenta_sintomas", 0)
        r.setdefault("aislamiento", 0)
        for campo_txt in ("contingencia", "ocupacion", "lugar_trabajo", "observacion"):
            if r.get(campo_txt) is None:
                r[campo_txt] = ""

        return r
