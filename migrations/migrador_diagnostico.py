"""
migrador_diagnostico.py — Migra amaymed.diagnostico → gesmed.diagnostico

AJUSTAR ANTES DE USAR:
    Revisar mapeo_campos() para que coincida con el esquema real de amaymed.
    La FK lk_paciente se resuelve descifrando amaymed.paciente.nombre_completo
    y comparando contra diagnostico.nombre_paciente (igual que en
    migrador_atencion.py). Si no hay coincidencia, queda NULL.
"""

from __future__ import annotations

import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from .migrador_base import MigradorTabla


class MigradorDiagnostico(MigradorTabla):

    def tabla_origen(self) -> str:
        return "diagnostico"      # ← nombre en amaymed (ajustar si difiere)

    def tabla_destino(self) -> str:
        return "diagnostico"

    def mapeo_campos(self) -> dict[str, str]:
        """
        ⚠ AJUSTAR según el esquema real de amaymed.
        """
        return {
            "id_diagnostico":       "id_diagnostico",
            "lk_paciente":          "lk_paciente",
            "id_paciente":          "lk_paciente",    # nombre alternativo en amaymed
            "lk_cie10":             "lk_cie10",
            "cod_cie10":            "lk_cie10",       # nombre alternativo
            "tipo":                 "tipo",
            "fecha_diagnostico":    "fecha_diagnostico",
            "fecha_inicio_aparente":"fecha_inicio_aparente",
            "lk_medico":            "lk_medico",
            "id_medico":            "lk_medico",      # nombre alternativo
            "observaciones":        "observaciones",
            "noduplicados":         "noduplicados",

            # Se resuelve a lk_paciente en migrar() (nombre texto → nro_hclinica)
            "nombre_paciente":      None,
            # Columnas de amaymed que NO existen en gesmed → descartar
            "medico_diagnostica":   None,
        }

    def campos_a_encriptar(self) -> list[str]:
        return ["observaciones"]

    def transformar_registro(self, registro: dict) -> dict:
        r = dict(registro)

        # Normalizar fechas a datetime.date
        for campo_fecha in ("fecha_diagnostico", "fecha_inicio_aparente"):
            val = r.get(campo_fecha)
            if isinstance(val, str):
                try:
                    r[campo_fecha] = datetime.date.fromisoformat(val)
                except ValueError:
                    r[campo_fecha] = datetime.datetime.strptime(val, "%d/%m/%Y").date()
            elif isinstance(val, datetime.datetime):
                r[campo_fecha] = val.date()

        # lk_medico es obligatorio en gesmed; si amaymed no lo tiene, usar 0 o el medico_id
        r.setdefault("lk_medico", self.medico_id)

        # noduplicados: generar si falta
        if not r.get("noduplicados"):
            lk_p = r.get("lk_paciente") or 0
            lk_c = r.get("lk_cie10", "")
            fd   = r.get("fecha_diagnostico", datetime.date.today())
            r["noduplicados"] = f"{lk_p}_{lk_c}_{fd}"

        return r

    # ── Resolución de lk_paciente (igual patrón que MigradorAtencion) ─────────

    def migrar(self, limite=None, offset=0) -> dict:
        print(f"\n  ▶ {self.tabla_origen()} → {self.tabla_destino()}", flush=True)

        registros = self.leer_origen(limite=limite, offset=offset)
        exitosos = 0
        errores: list[dict] = []
        mapa = self.mapeo_campos()

        mapa_pacientes = self._cargar_mapa_pacientes()
        mapa_medicos = self._cargar_mapa_medicos()
        sin_medico = 0

        with Session(self._engine_destino) as session:
            for reg in registros:
                try:
                    mapeado: dict = {}
                    for col, valor in reg.items():
                        col_dest = mapa.get(col, col)
                        if col_dest is not None:
                            mapeado[col_dest] = valor

                    nombre_pac = str(reg.get("nombre_paciente") or "").strip().upper()
                    mapeado["lk_paciente"] = mapa_pacientes.get(nombre_pac)

                    # Resolver lk_medico desde medico_diagnostica; si no hay
                    # match, cae al medico_id de respaldo del constructor.
                    nombre_med = str(reg.get("medico_diagnostica") or "").strip().upper()
                    if nombre_med in mapa_medicos:
                        mapeado["lk_medico"] = mapa_medicos[nombre_med]
                    else:
                        sin_medico += 1

                    transformado = self.transformar_registro(mapeado)

                    for campo in self.campos_a_encriptar():
                        if campo in transformado and transformado[campo] is not None:
                            valor = transformado[campo]
                            if not isinstance(valor, (bytes, bytearray)):
                                transformado[campo] = self.crypto.encriptar(str(valor))

                    self._insertar(session, transformado)
                    exitosos += 1

                except Exception as exc:
                    errores.append({"id": reg.get("id_diagnostico", "?"), "error": str(exc)})

            session.commit()

        total = len(registros)
        estado = "✓" if not errores else "✗"
        no_resueltos = sum(1 for r in registros
                          if str(r.get("nombre_paciente") or "").strip().upper()
                          not in mapa_pacientes)
        if no_resueltos:
            print(f"  ⚠ {no_resueltos} diagnósticos sin lk_paciente (nombre no encontrado)", flush=True)
        if sin_medico:
            print(
                f"  ⚠ {sin_medico} diagnósticos sin medico_diagnostica reconocido, "
                f"asignados al medico_id de respaldo ({self.medico_id})",
                flush=True,
            )
        print(
            f"  {estado} {exitosos}/{total} registros migrados"
            + (f"  ({len(errores)} errores)" if errores else ""),
            flush=True,
        )
        return {"exitosos": exitosos, "errores": errores, "total": total}

    def _cargar_mapa_medicos(self) -> dict[str, int]:
        """gesmed.points ya migrado → {NOMBRE_MEDICO_UPPER: id_medico}."""
        mapa: dict[str, int] = {}
        with Session(self._engine_destino) as s:
            for row in s.execute(text("SELECT id_medico, nombre_medico FROM points")):
                mapa[str(row.nombre_medico).strip().upper()] = row.id_medico
        return mapa

    def _cargar_mapa_pacientes(self) -> dict[str, int]:
        """Descifra nombre_completo de amaymed.paciente → {NOMBRE_UPPER: nro_hclinica}."""
        mapa: dict[str, int] = {}
        with Session(self._engine_origen) as s:
            for row in s.execute(text("SELECT nro_hclinica, nombre_completo FROM paciente")):
                nombre_raw = row.nombre_completo
                try:
                    if isinstance(nombre_raw, (bytes, bytearray)):
                        nombre_texto = self.crypto.desencriptar(nombre_raw)
                    else:
                        nombre_texto = str(nombre_raw)
                    mapa[nombre_texto.strip().upper()] = row.nro_hclinica
                except Exception:
                    pass
        return mapa
