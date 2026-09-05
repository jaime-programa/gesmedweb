"""
migrador_rel_atencion_diagnostico.py
    amaymed.rel_atencion_diagnostico → gesmed.rel_atencion_diagnostico

Diferencias de esquema:
    amaymed: id_atencion, id_diagnostico  (nombres sin prefijo lk_)
    gesmed:  lk_atencion, lk_diagnostico  (nombres con prefijo lk_)

    noduplicarelacion: amaymed VARCHAR(20), gesmed VARCHAR(18→20 tras ALTER).

Requiere que atencion y diagnostico ya estén migradas (FK).
"""

from __future__ import annotations

from .migrador_base import MigradorTabla


class MigradorRelAtencionDiagnostico(MigradorTabla):

    def tabla_origen(self) -> str:
        return "rel_atencion_diagnostico"

    def tabla_destino(self) -> str:
        return "rel_atencion_diagnostico"

    def mapeo_campos(self) -> dict[str, str]:
        return {
            "id_relacion":       "id_relacion",
            "id_atencion":       "lk_atencion",
            "id_diagnostico":    "lk_diagnostico",
            "noduplicarelacion": "noduplicarelacion",
        }

    def campos_a_encriptar(self) -> list[str]:
        return []

    def transformar_registro(self, registro: dict) -> dict:
        # Truncar noduplicarelacion a 20 chars por seguridad
        if registro.get("noduplicarelacion"):
            registro["noduplicarelacion"] = str(registro["noduplicarelacion"])[:20]
        return registro
