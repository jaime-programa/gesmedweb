"""
migrador_examenes.py — Migra amaymed.pedido_examenes hacia dos tablas gesmed.

Columnas de amaymed.pedido_examenes utilizadas:
    grupo        → examenes_laboratorio_grupo.id_grupo
                   examenes_laboratorio_catalogo.lk_grupo
    nombre_grupo → examenes_laboratorio_grupo.nombre_grupo
    id_examen    → examenes_laboratorio_catalogo.id_examen
    detalle      → examenes_laboratorio_catalogo.nombre_examen

ORDEN DE EJECUCIÓN REQUERIDO:
    MigradorExamenesGrupo debe migrar ANTES que MigradorExamenesCatalogo
    (FK: examenes_laboratorio_catalogo.lk_grupo → examenes_laboratorio_grupo.id_grupo)
"""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from .migrador_base import MigradorTabla


class MigradorExamenesGrupo(MigradorTabla):
    """
    Extrae los grupos únicos de amaymed.pedido_examenes
    conservando el id original (grupo) como PK de destino.
    """

    def tabla_origen(self) -> str:
        return "pedido_examenes"

    def tabla_destino(self) -> str:
        return "examenes_laboratorio_grupo"

    def mapeo_campos(self) -> dict[str, str]:
        return {}   # leer_origen ya entrega los campos con los nombres correctos

    def campos_a_encriptar(self) -> list[str]:
        return []

    def transformar_registro(self, registro: dict) -> dict:
        return registro

    def leer_origen(self, limite=None, offset=0) -> list[dict]:
        sql = (
            "SELECT DISTINCT grupo AS id_grupo, nombre_grupo"
            " FROM pedido_examenes"
            " WHERE grupo IS NOT NULL"
            " ORDER BY grupo"
        )
        if limite is not None:
            sql += f" LIMIT {limite} OFFSET {offset}"
        with Session(self._engine_origen) as s:
            return [dict(r._mapping) for r in s.execute(text(sql))]

    def contar_origen(self) -> int:
        with Session(self._engine_origen) as s:
            return s.execute(
                text("SELECT COUNT(DISTINCT grupo) FROM pedido_examenes WHERE grupo IS NOT NULL")
            ).scalar_one()


class MigradorExamenesCatalogo(MigradorTabla):
    """
    Migra el catálogo de exámenes de amaymed.pedido_examenes
    hacia gesmed.examenes_laboratorio_catalogo.
    lk_grupo se toma directamente de la columna grupo (ya es el id numérico).
    Requiere que MigradorExamenesGrupo haya sido ejecutado primero.
    """

    def tabla_origen(self) -> str:
        return "pedido_examenes"

    def tabla_destino(self) -> str:
        return "examenes_laboratorio_catalogo"

    def mapeo_campos(self) -> dict[str, str]:
        return {}   # leer_origen ya entrega los campos con los nombres correctos

    def campos_a_encriptar(self) -> list[str]:
        return []

    def transformar_registro(self, registro: dict) -> dict:
        registro["activo"] = 1
        return registro

    def leer_origen(self, limite=None, offset=0) -> list[dict]:
        sql = (
            "SELECT DISTINCT id_examen, detalle AS nombre_examen, grupo AS lk_grupo"
            " FROM pedido_examenes"
            " WHERE id_examen IS NOT NULL"
            " ORDER BY grupo, id_examen"
        )
        if limite is not None:
            sql += f" LIMIT {limite} OFFSET {offset}"
        with Session(self._engine_origen) as s:
            return [dict(r._mapping) for r in s.execute(text(sql))]

    def contar_origen(self) -> int:
        with Session(self._engine_origen) as s:
            return s.execute(
                text("SELECT COUNT(DISTINCT id_examen) FROM pedido_examenes WHERE id_examen IS NOT NULL")
            ).scalar_one()
