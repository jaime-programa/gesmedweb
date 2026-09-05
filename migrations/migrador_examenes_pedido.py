"""
migrador_examenes_pedido.py
    amaymed.paso_pedido_examenes → gesmed.examenes_laboratorio_pedido

Mapeo de campos:
    id_pedido    → id_pedido      (PK, se conserva)
    paciente     → lk_paciente    (nombre texto → nro_hclinica, via descifrado)
    fecha_pedido → fecha_pedido
    id_examen    → lk_examen      (mismo ID, migrado con MigradorExamenesCatalogo)

lk_paciente se resuelve descifrando amaymed.paciente.nombre_completo.
Si no hay coincidencia, queda NULL.
"""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from .migrador_base import MigradorTabla


class MigradorExamenesPedido(MigradorTabla):

    def tabla_origen(self) -> str:
        return "paso_pedido_examenes"

    def tabla_destino(self) -> str:
        return "examenes_laboratorio_pedido"

    def mapeo_campos(self) -> dict[str, str]:
        return {
            "id_pedido":    "id_pedido",
            "paciente":     None,           # se resuelve a lk_paciente en migrar()
            "fecha_pedido": "fecha_pedido",
            "id_examen":    "lk_examen",
        }

    def campos_a_encriptar(self) -> list[str]:
        return []

    def transformar_registro(self, registro: dict) -> dict:
        return registro

    def migrar(self, limite=None, offset=0) -> dict:
        print(f"\n  ▶ {self.tabla_origen()} → {self.tabla_destino()}", flush=True)

        registros = self.leer_origen(limite=limite, offset=offset)
        exitosos = 0
        errores: list[dict] = []
        mapa = self.mapeo_campos()

        mapa_pacientes = self._cargar_mapa_pacientes()

        with Session(self._engine_destino) as session:
            for reg in registros:
                try:
                    mapeado: dict = {}
                    for col, valor in reg.items():
                        col_dest = mapa.get(col, col)
                        if col_dest is not None:
                            mapeado[col_dest] = valor

                    nombre_pac = str(reg.get("paciente") or "").strip().upper()
                    mapeado["lk_paciente"] = mapa_pacientes.get(nombre_pac)

                    self._insertar(session, mapeado)
                    exitosos += 1

                except Exception as exc:
                    errores.append({"id": reg.get("id_pedido", "?"), "error": str(exc)})

            session.commit()

        total = len(registros)
        estado = "✓" if not errores else "✗"
        no_resueltos = sum(1 for r in registros
                          if str(r.get("paciente") or "").strip().upper()
                          not in mapa_pacientes)
        if no_resueltos:
            print(f"  ⚠ {no_resueltos} pedidos sin lk_paciente (nombre no encontrado)", flush=True)
        print(
            f"  {estado} {exitosos}/{total} registros migrados"
            + (f"  ({len(errores)} errores)" if errores else ""),
            flush=True,
        )
        return {"exitosos": exitosos, "errores": errores, "total": total}

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
