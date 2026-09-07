"""
migrador_prescripcion.py — Migra amaymed.prescripcion_ok → gesmed.prescripcion

AJUSTAR ANTES DE USAR:
    Revisar mapeo_campos() para que coincida con el esquema real de amaymed.
    Las FK lk_atencion deben existir en gesmed antes de migrar.
    lk_paciente se resuelve descifrando amaymed.paciente.nombre_completo y
    comparando contra prescripcion_ok.el_paciente (igual que en
    migrador_atencion.py). Si no hay coincidencia, queda NULL.
"""

from __future__ import annotations

import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from .migrador_base import MigradorTabla


class MigradorPrescripcion(MigradorTabla):

    def tabla_origen(self) -> str:
        return "prescripcion_ok"

    def tabla_destino(self) -> str:
        return "prescripcion"

    def mapeo_campos(self) -> dict[str, str]:
        """
        ⚠ AJUSTAR según el esquema real de amaymed.
        """
        return {
            "id_prescripcion":    "id_prescripcion",
            "lk_atencion":        "lk_atencion",
            "atencion_relacionada": "lk_atencion",    # nombre en amaymed.prescripcion_ok
            "fecha_prescripcion": "fecha_prescripcion",
            "concentracion":      "concentracion",
            "cantidad":           "cantidad",
            "lk_presentacion":    "lk_presentacion",
            "indicaciones":       "indicaciones",
            "el_generico":        "lk_generico",      # nombre real en amaymed.prescripcion_ok
            # Se resuelve a lk_paciente en migrar() (nombre texto → nro_hclinica)
            "el_paciente":        None,
            # Columnas de amaymed que NO existen en gesmed → descartar
            "presentacion":       None,               # texto libre, gesmed usa lk_presentacion
            "lk_generico":        None,               # siempre 0 en amaymed; usar el_generico
            "lk_paciente":        None,
            "id_paciente":        None,
        }

    def campos_a_encriptar(self) -> list[str]:
        return ["concentracion", "indicaciones"]

    def transformar_registro(self, registro: dict) -> dict:
        r = dict(registro)

        # Normalizar fecha_prescripcion a datetime.date
        val = r.get("fecha_prescripcion")
        if isinstance(val, str):
            try:
                r["fecha_prescripcion"] = datetime.date.fromisoformat(val)
            except ValueError:
                r["fecha_prescripcion"] = datetime.datetime.strptime(val, "%d/%m/%Y").date()
        elif isinstance(val, datetime.datetime):
            r["fecha_prescripcion"] = val.date()

        # Defaults para campos que podrían faltar
        r.setdefault("cantidad", 1)

        # lk_presentacion: 0/None viola FK (en amaymed era texto libre), y un
        # valor real de amaymed también puede no existir en el catálogo fijo
        # de gesmed.medicamento_presentacion (catálogo congelado por separado,
        # ver parametros_fijos.py) → en ambos casos, NULL en vez de IntegrityError.
        if r.get("lk_presentacion") not in getattr(self, "_presentacion_validos", set()):
            r["lk_presentacion"] = None

        # lk_generico: mismo caso que lk_presentacion. amaymed no valida contra
        # ningún catálogo (era texto libre / IDs propios), así que puede traer
        # códigos que no existen en el catálogo fijo de gesmed.medicamentos
        # (p.ej. cod_gen=474 cuando el AUTO_INCREMENT de gesmed.medicamentos
        # solo llega hasta 473) → NULL en vez de IntegrityError.
        if r.get("lk_generico") not in getattr(self, "_generico_validos", set()):
            r["lk_generico"] = None

        return r

    # ── Resolución de lk_paciente (igual patrón que MigradorAtencion) ─────────

    def migrar(self, limite=None, offset=0) -> dict:
        print(f"\n  ▶ {self.tabla_origen()} → {self.tabla_destino()}", flush=True)

        registros = self.leer_origen(limite=limite, offset=offset)
        exitosos = 0
        errores: list[dict] = []
        mapa = self.mapeo_campos()

        mapa_pacientes = self._cargar_mapa_pacientes()
        self._generico_validos = self._cargar_generico_validos()
        self._presentacion_validos = self._cargar_presentacion_validos()

        with Session(self._engine_destino) as session:
            for reg in registros:
                try:
                    mapeado: dict = {}
                    for col, valor in reg.items():
                        col_dest = mapa.get(col, col)
                        if col_dest is not None:
                            mapeado[col_dest] = valor

                    nombre_pac = str(reg.get("el_paciente") or "").strip().upper()
                    mapeado["lk_paciente"] = mapa_pacientes.get(nombre_pac)

                    transformado = self.transformar_registro(mapeado)

                    for campo in self.campos_a_encriptar():
                        if campo in transformado and transformado[campo] is not None:
                            valor = transformado[campo]
                            if not isinstance(valor, (bytes, bytearray)):
                                transformado[campo] = self.crypto.encriptar(str(valor))

                    self._insertar(session, transformado)
                    exitosos += 1

                except Exception as exc:
                    errores.append({"id": reg.get("id_prescripcion", "?"), "error": str(exc)})

            session.commit()

        total = len(registros)
        estado = "✓" if not errores else "✗"
        no_resueltos = sum(1 for r in registros
                          if str(r.get("el_paciente") or "").strip().upper()
                          not in mapa_pacientes)
        if no_resueltos:
            print(f"  ⚠ {no_resueltos} prescripciones sin lk_paciente (nombre no encontrado)", flush=True)
        print(
            f"  {estado} {exitosos}/{total} registros migrados"
            + (f"  ({len(errores)} errores)" if errores else ""),
            flush=True,
        )
        return {"exitosos": exitosos, "errores": errores, "total": total}

    def _cargar_generico_validos(self) -> set[int]:
        """cod_gen existentes en el catálogo fijo gesmed.medicamentos."""
        with Session(self._engine_destino) as s:
            return set(s.execute(text("SELECT cod_gen FROM medicamentos")).scalars().all())

    def _cargar_presentacion_validos(self) -> set[int]:
        """id_presentacion existentes en el catálogo fijo gesmed.medicamento_presentacion."""
        with Session(self._engine_destino) as s:
            return set(s.execute(text("SELECT id_presentacion FROM medicamento_presentacion")).scalars().all())

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
