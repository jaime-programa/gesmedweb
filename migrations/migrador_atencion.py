"""
migrador_atencion.py — Migra amaymed.atencion → gesmed.atencion

Diferencias de esquema:
    amaymed usa nombre_paciente (texto) y medico_atiende (texto).
    gesmed usa lk_paciente (FK int) y lk_medico (FK int).

    lk_paciente se resuelve descifrando amaymed.paciente.nombre_completo
    y comparando con atencion.nombre_paciente. Si no hay match → NULL.
    lk_medico se fija a medico_id del constructor.

    Columnas de amaymed descartadas (no existen en gesmed):
        nombre_paciente, medico_atiende, ya_facturado,
        peso_kg, talla_cm, perimetro_cefalico, imc,
        fc, fr, tas, tad, temp, saturacion_o2
    (los signos vitales deberían migrarse a gesmed.signosvitales por separado)
"""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from .migrador_base import MigradorTabla


_COLS_DESCARTAR = {
    "nombre_paciente", "medico_atiende", "ya_facturado",
    "peso_kg", "talla_cm", "perimetro_cefalico", "imc",
    "fc", "fr", "tas", "tad", "temp", "saturacion_o2",
}


class MigradorAtencion(MigradorTabla):

    def tabla_origen(self) -> str:
        return "atencion"

    def tabla_destino(self) -> str:
        return "atencion"

    def mapeo_campos(self) -> dict[str, str]:
        return {col: None for col in _COLS_DESCARTAR}

    def campos_a_encriptar(self) -> list[str]:
        return []

    def transformar_registro(self, registro: dict) -> dict:
        registro.setdefault("lk_medico", self.medico_id)
        return registro

    def migrar(self, limite=None, offset=0) -> dict:
        print(f"\n  ▶ {self.tabla_origen()} → {self.tabla_destino()}", flush=True)

        registros = self.leer_origen(limite=limite, offset=offset)
        exitosos = 0
        errores: list[dict] = []
        mapa = self.mapeo_campos()

        # Descifrar nombres de amaymed.paciente para resolver lk_paciente
        mapa_pacientes = self._cargar_mapa_pacientes()

        with Session(self._engine_destino) as session:
            for reg in registros:
                try:
                    # Renombrar y descartar columnas
                    mapeado: dict = {}
                    for col, valor in reg.items():
                        col_dest = mapa.get(col, col)
                        if col_dest is not None:
                            mapeado[col_dest] = valor

                    # Resolver lk_paciente desde nombre_paciente
                    nombre_pac = str(reg.get("nombre_paciente") or "").strip().upper()
                    mapeado["lk_paciente"] = mapa_pacientes.get(nombre_pac)

                    transformado = self.transformar_registro(mapeado)
                    self._insertar(session, transformado)
                    exitosos += 1

                except Exception as exc:
                    errores.append({"id": reg.get("id_atencion", "?"), "error": str(exc)})

            session.commit()

        total = len(registros)
        estado = "✓" if not errores else "✗"
        no_resueltos = sum(1 for r in registros
                          if str(r.get("nombre_paciente") or "").strip().upper()
                          not in mapa_pacientes)
        if no_resueltos:
            print(f"  ⚠ {no_resueltos} atenciones sin lk_paciente (nombre no encontrado)", flush=True)
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
