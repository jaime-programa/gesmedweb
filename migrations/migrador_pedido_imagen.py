"""
migrador_pedido_imagen.py — Migra amaymed.pedido_imagen (+ pedido_imagen_cie)
→ gesmed.examen_pedido

Diferencias de esquema:
    amaymed.pedido_imagen tiene 6 columnas de texto libre (una por modalidad):
    rx, rmn, ggo, eco, tomo, esp — más cod_terapia/observacion_terapia (terapia,
    no imagenología). gesmed.examen_pedido es una tabla normalizada: una fila
    por examen solicitado, con lk_catalogo apuntando a examen_catalogo.

    examen_tipo / examen_catalogo YA EXISTEN en gesmed con datos reales
    (catálogo clínico, no se generan aquí). El catálogo actual para el tipo
    "Imagen" es:
        RX, GGO, TOMOGRAFIA, RMN, ECO
    Los campos `esp`, `cod_terapia` y `observacion_terapia` de amaymed no
    tienen alias correspondiente en examen_catalogo → se descartan (decisión
    confirmada con el usuario).

    Por cada pedido de amaymed, se genera UNA fila en examen_pedido por cada
    campo de modalidad no vacío, resolviendo:
      - lk_catalogo:   alias fijo del campo → examen_catalogo.id_examen
                       (RX→RX, RMN→RMN, GGO→GGO, ECO→ECO, TOMO→TOMOGRAFIA)
      - lk_atencion:   atención del mismo paciente con fecha_atencion más
                       cercana (misma fecha o inmediatamente anterior a
                       fecha_pedido)
      - lk_diagnostico: vía pedido_imagen_cie.cie10_pedido, buscando en
                       amaymed.diagnostico un registro del mismo paciente con
                       ese cod_cie10 (el más reciente si hay varios)
      - detalle_pedido: el texto libre del campo, truncado a 150 caracteres

    Si no se puede resolver lk_atencion o lk_diagnostico (ambas NOT NULL en
    gesmed), esa fila se descarta y se registra como error — no se inserta
    con NULL.

    Ninguna columna de gesmed.examen_pedido es BLOB → sin cifrado.

Requiere que atencion, diagnostico y el catálogo examen_tipo/examen_catalogo
ya existan en gesmed.
"""

from __future__ import annotations

import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from .migrador_base import MigradorTabla

# campo en pedido_imagen -> alias en examen_catalogo (tipo "Imagen")
ALIAS_POR_CAMPO = {
    "rx":   "RX",
    "rmn":  "RMN",
    "ggo":  "GGO",
    "eco":  "ECO",
    "tomo": "TOMOGRAFIA",
}


class MigradorPedidoImagen(MigradorTabla):

    def tabla_origen(self) -> str:
        return "pedido_imagen"

    def tabla_destino(self) -> str:
        return "examen_pedido"

    def mapeo_campos(self) -> dict[str, str]:
        return {}   # no aplica: la reestructuración se hace en migrar()

    def campos_a_encriptar(self) -> list[str]:
        return []

    def transformar_registro(self, registro: dict) -> dict:
        return registro

    # ── Migración custom: 1 pedido → N filas de examen_pedido ──────────────────

    def migrar(self, limite=None, offset=0) -> dict:
        print(f"\n  ▶ {self.tabla_origen()} → {self.tabla_destino()}", flush=True)

        pedidos = self._leer_pedidos(limite=limite, offset=offset)
        mapa_catalogo = self._cargar_mapa_catalogo()
        mapa_atenciones = self._cargar_mapa_atenciones()
        mapa_cies_pedido = self._cargar_mapa_cies_pedido()
        mapa_diagnosticos = self._cargar_mapa_diagnosticos()

        exitosos = 0
        errores: list[dict] = []
        total_candidatos = 0

        with Session(self._engine_destino) as session:
            for pedido in pedidos:
                nombre_pac = str(pedido["paciente"] or "").strip().upper()
                fecha_pedido = pedido["fecha_pedido"]
                if isinstance(fecha_pedido, datetime.datetime):
                    fecha_pedido = fecha_pedido.date()

                id_atencion = self._resolver_atencion(mapa_atenciones, nombre_pac, fecha_pedido)

                cies = mapa_cies_pedido.get(pedido["id_pedido"], [])
                id_diagnostico = self._resolver_diagnostico(mapa_diagnosticos, nombre_pac, cies)

                for campo, alias in ALIAS_POR_CAMPO.items():
                    texto = str(pedido.get(campo) or "").strip()
                    if not texto:
                        continue
                    total_candidatos += 1

                    id_examen = mapa_catalogo.get(alias)
                    if id_examen is None or id_atencion is None or id_diagnostico is None:
                        errores.append({
                            "id": f"{pedido['id_pedido']}/{campo}",
                            "error": (
                                f"sin resolver "
                                f"(catalogo={id_examen}, atencion={id_atencion}, diagnostico={id_diagnostico})"
                            ),
                        })
                        continue

                    try:
                        fila = {
                            "lk_atencion":    id_atencion,
                            "lk_catalogo":    id_examen,
                            "lk_diagnostico": id_diagnostico,
                            "detalle_pedido": texto[:150],
                        }
                        self._insertar(session, fila)
                        exitosos += 1
                    except Exception as exc:
                        errores.append({"id": f"{pedido['id_pedido']}/{campo}", "error": str(exc)})

            session.commit()

        estado = "✓" if not errores else "✗"
        print(
            f"  {estado} {exitosos}/{total_candidatos} registros migrados"
            + (f"  ({len(errores)} errores)" if errores else ""),
            flush=True,
        )
        return {"exitosos": exitosos, "errores": errores, "total": total_candidatos}

    # ── Carga de datos de origen ────────────────────────────────────────────────

    def _leer_pedidos(self, limite=None, offset=0) -> list[dict]:
        sql = "SELECT * FROM pedido_imagen ORDER BY id_pedido"
        if limite is not None:
            sql += f" LIMIT {int(limite)} OFFSET {int(offset)}"
        with Session(self._engine_origen) as s:
            filas = s.execute(text(sql)).mappings().all()
            return [dict(f) for f in filas]

    def contar_origen(self) -> int:
        """Cuenta candidatos reales (campos de modalidad no vacíos), no filas de pedido_imagen."""
        campos = " + ".join(f"(TRIM({c}) != '')" for c in ALIAS_POR_CAMPO)
        with Session(self._engine_origen) as s:
            return s.execute(text(f"SELECT SUM({campos}) FROM pedido_imagen")).scalar_one() or 0

    def _cargar_mapa_catalogo(self) -> dict[str, int]:
        """{examen_alias: id_examen} para el tipo 'Imagen' en gesmed.examen_catalogo."""
        mapa: dict[str, int] = {}
        with Session(self._engine_destino) as s:
            filas = s.execute(text(
                "SELECT ec.id_examen, ec.examen_alias "
                "FROM examen_catalogo ec JOIN examen_tipo et ON et.id_examen_tipo = ec.lk_examen_tipo "
                "WHERE et.examen_tipo = 'Imagen'"
            ))
            for row in filas:
                mapa[row.examen_alias] = row.id_examen
        return mapa

    def _cargar_mapa_atenciones(self) -> dict[str, list[tuple[datetime.date, int]]]:
        """{NOMBRE_PACIENTE_UPPER: [(fecha_atencion, id_atencion), ...]} ordenado por fecha."""
        mapa: dict[str, list[tuple[datetime.date, int]]] = {}
        with Session(self._engine_origen) as s:
            filas = s.execute(text("SELECT nombre_paciente, id_atencion, fecha_atencion FROM atencion"))
            for row in filas:
                nombre = str(row.nombre_paciente or "").strip().upper()
                fecha = row.fecha_atencion
                if isinstance(fecha, datetime.datetime):
                    fecha = fecha.date()
                mapa.setdefault(nombre, []).append((fecha, row.id_atencion))
        for nombre in mapa:
            mapa[nombre].sort(key=lambda t: t[0])
        return mapa

    def _cargar_mapa_cies_pedido(self) -> dict[int, list[str]]:
        """{lk_pedido: [cie10_pedido, ...]} desde amaymed.pedido_imagen_cie."""
        mapa: dict[int, list[str]] = {}
        with Session(self._engine_origen) as s:
            filas = s.execute(text("SELECT lk_pedido, cie10_pedido FROM pedido_imagen_cie"))
            for row in filas:
                mapa.setdefault(row.lk_pedido, []).append(row.cie10_pedido)
        return mapa

    def _cargar_mapa_diagnosticos(self) -> dict[tuple[str, str], list[tuple[datetime.date, int]]]:
        """{(NOMBRE_PACIENTE_UPPER, cod_cie10): [(fecha_diagnostico, id_diagnostico), ...]}."""
        mapa: dict[tuple[str, str], list[tuple[datetime.date, int]]] = {}
        with Session(self._engine_origen) as s:
            filas = s.execute(text(
                "SELECT nombre_paciente, cod_cie10, id_diagnostico, fecha_diagnostico FROM diagnostico"
            ))
            for row in filas:
                clave = (str(row.nombre_paciente or "").strip().upper(), row.cod_cie10)
                mapa.setdefault(clave, []).append((row.fecha_diagnostico, row.id_diagnostico))
        for clave in mapa:
            mapa[clave].sort(key=lambda t: t[0])
        return mapa

    # ── Resolución de FKs ────────────────────────────────────────────────────────

    def _resolver_atencion(self, mapa_atenciones, nombre_pac: str, fecha_pedido) -> int | None:
        """Atención del paciente con fecha_atencion más cercana (misma fecha o anterior)."""
        candidatas = mapa_atenciones.get(nombre_pac, [])
        mejor: int | None = None
        for fecha, id_atencion in candidatas:
            if fecha <= fecha_pedido:
                mejor = id_atencion   # la lista está ordenada asc: nos quedamos con la última <=
            else:
                break
        return mejor

    def _resolver_diagnostico(self, mapa_diagnosticos, nombre_pac: str, cies: list[str]) -> int | None:
        """Primer cie10 del pedido con match de diagnóstico del paciente (el más reciente)."""
        for cie in cies:
            candidatos = mapa_diagnosticos.get((nombre_pac, cie))
            if candidatos:
                return candidatos[-1][1]   # el más reciente (lista ordenada asc por fecha)
        return None
