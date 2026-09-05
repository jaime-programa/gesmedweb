"""
migrador_prescripcion_cuidados.py — Migra amaymed.cuidados_paciente → gesmed.prescripcion_cuidados

Diferencias de esquema:
    amaymed.cuidados_paciente:
        para_atencion  int PK  (FK implícita a atencion.id_atencion, sin
                                 restricción declarada en el dump)
        cuidado        mediumtext

    gesmed.prescripcion_cuidados:
        id_cuidados         int AUTO_INCREMENT PK  (no existe en amaymed,
                                                     se deja que MySQL lo genere)
        lk_atencion          int NOT NULL, UNIQUE   (FK real a atencion.id_atencion)
        cuidados_generales   text
        fecha_emision        date

    lk_atencion se copia directo desde para_atencion porque migrador_atencion.py
    preserva los id_atencion originales de amaymed.

    fecha_emision no existe en amaymed.cuidados_paciente → se resuelve
    consultando amaymed.atencion.fecha_atencion para la misma atención
    (igual espíritu que la resolución de lk_paciente en otros migradores:
    un mapa precargado id_atencion → fecha).

    Ninguna columna de gesmed.prescripcion_cuidados es BLOB → sin cifrado.

Requiere que atencion ya esté migrada (FK lk_atencion).
"""

from __future__ import annotations

import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from .migrador_base import MigradorTabla


class MigradorPrescripcionCuidados(MigradorTabla):

    def tabla_origen(self) -> str:
        return "cuidados_paciente"

    def tabla_destino(self) -> str:
        return "prescripcion_cuidados"

    def mapeo_campos(self) -> dict[str, str]:
        return {
            "para_atencion": "lk_atencion",
            "cuidado":       "cuidados_generales",
        }

    def campos_a_encriptar(self) -> list[str]:
        return []   # gesmed.prescripcion_cuidados no tiene columnas BLOB

    def transformar_registro(self, registro: dict) -> dict:
        r = dict(registro)
        r.setdefault("cuidados_generales", "")
        if r.get("cuidados_generales") is None:
            r["cuidados_generales"] = ""
        return r

    # ── Resolución de fecha_emision vía amaymed.atencion ───────────────────────

    def migrar(self, limite=None, offset=0) -> dict:
        print(f"\n  ▶ {self.tabla_origen()} → {self.tabla_destino()}", flush=True)

        registros = self.leer_origen(limite=limite, offset=offset)
        exitosos = 0
        errores: list[dict] = []
        mapa = self.mapeo_campos()

        mapa_fechas = self._cargar_mapa_fechas_atencion()

        with Session(self._engine_destino) as session:
            for reg in registros:
                try:
                    mapeado: dict = {}
                    for col, valor in reg.items():
                        col_dest = mapa.get(col, col)
                        if col_dest is not None:
                            mapeado[col_dest] = valor

                    transformado = self.transformar_registro(mapeado)
                    transformado["fecha_emision"] = mapa_fechas.get(transformado.get("lk_atencion"))

                    self._insertar(session, transformado)
                    exitosos += 1

                except Exception as exc:
                    errores.append({"id": reg.get("para_atencion", "?"), "error": str(exc)})

            session.commit()

        total = len(registros)
        estado = "✓" if not errores else "✗"
        print(
            f"  {estado} {exitosos}/{total} registros migrados"
            + (f"  ({len(errores)} errores)" if errores else ""),
            flush=True,
        )
        return {"exitosos": exitosos, "errores": errores, "total": total}

    def _cargar_mapa_fechas_atencion(self) -> dict[int, datetime.date]:
        """Precarga {id_atencion: fecha_atencion.date()} desde amaymed.atencion."""
        mapa: dict[int, datetime.date] = {}
        with Session(self._engine_origen) as s:
            for row in s.execute(text("SELECT id_atencion, fecha_atencion FROM atencion")):
                fecha = row.fecha_atencion
                if isinstance(fecha, datetime.datetime):
                    fecha = fecha.date()
                mapa[row.id_atencion] = fecha
        return mapa
