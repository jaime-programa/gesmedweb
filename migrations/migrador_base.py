"""
migrador_base.py — Clase base para migradores amaymed → gesmed.

Variables de entorno requeridas:
    GESMED_MASTER_KEY   — clave AES-256 (64 hex chars)
    GESMED_DB_URL       — opcional, default: mysql+pymysql://med_admin:gesmed01@localhost:3306/gesmed
    AMAYMED_DB_URL      — opcional, default: mysql+pymysql://med_admin:gesmed01@localhost:3306/amaymed

Extender a una nueva tabla:
    1. Crear migrations/migrador_nuevatabla.py
    2. Subclasear MigradorTabla
    3. Implementar los 5 métodos abstractos
    4. Añadir la clase al OrquestadorMigracion en el orden correcto de FK
"""

from __future__ import annotations

import os
import sys
from abc import ABC, abstractmethod
from typing import Optional

# ── Asegurar que el paquete GesmedWeb sea importable ─────────────────────────
_ROOT = os.path.dirname(os.path.dirname(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from GesmedWeb.crypto import GesmedCrypto


def _engine(env_var: str, default_url: str):
    url = os.environ.get(env_var, default_url)
    return create_engine(url, echo=False, pool_pre_ping=True)


def db_params(env_var: str, default_url: str) -> dict:
    """Descompone la URL de SQLAlchemy de env_var (GESMED_DB_URL/AMAYMED_DB_URL)
    en host/port/user/password/name — lo que necesitan los subprocess a
    mysqldump/mysql. Única fuente de verdad para la conexión: no hay
    variables *_DB_HOST/PORT/USER/PASSWORD/NAME independientes."""
    url = make_url(os.environ.get(env_var, default_url))
    return {
        "host": url.host or "localhost",
        "port": str(url.port or 3306),
        "user": url.username or "",
        "password": url.password or "",
        "name": url.database or "",
    }


class MigradorTabla(ABC):
    """
    Template-method para migrar una tabla de amaymed a gesmed con encriptación.

    Flujo de migrar():
        leer_origen() → mapeo_campos() → transformar_registro()
                      → encriptar_campos() → _insertar()
    """

    def __init__(self, medico_id: int) -> None:
        self.medico_id = medico_id
        self.crypto = GesmedCrypto.para_medico(medico_id)
        self._engine_origen = _engine(
            "AMAYMED_DB_URL",
            "mysql+pymysql://med_admin:gesmed01@localhost:3306/amaymed",
        )
        self._engine_destino = _engine(
            "GESMED_DB_URL",
            "mysql+pymysql://med_admin:gesmed01@localhost:3306/gesmed",
        )

    # ── Métodos abstractos (implementar en cada subclase) ─────────────────────

    @abstractmethod
    def tabla_origen(self) -> str:
        """Nombre de la tabla en amaymed."""

    @abstractmethod
    def tabla_destino(self) -> str:
        """Nombre de la tabla en gesmed."""

    @abstractmethod
    def mapeo_campos(self) -> dict[str, str]:
        """
        Renombrado de columnas: {"nombre_en_amaymed": "nombre_en_gesmed"}.
        Columnas sin entrada en este dict conservan su nombre original.
        Columnas mapeadas a None se descartan (no se insertan en gesmed).
        """

    @abstractmethod
    def campos_a_encriptar(self) -> list[str]:
        """Nombres de los campos en gesmed que deben cifrarse (después del mapeo)."""

    @abstractmethod
    def transformar_registro(self, registro: dict) -> dict:
        """
        Hook de transformación custom por tabla.
        Recibe el registro ya con los campos renombrados según mapeo_campos().
        Debe devolver el dict listo para encriptar e insertar.
        Aquí se añaden campos nuevos, conversiones de tipo, valores por defecto, etc.
        """

    # ── Lógica base (no se necesita sobreescribir normalmente) ────────────────

    def leer_origen(
        self, limite: Optional[int] = None, offset: int = 0
    ) -> list[dict]:
        """Lee registros de amaymed; admite paginación opcional."""
        sql = f"SELECT * FROM {self.tabla_origen()}"
        if limite is not None:
            sql += f" LIMIT {limite} OFFSET {offset}"
        with Session(self._engine_origen) as session:
            result = session.execute(text(sql))
            return [dict(row._mapping) for row in result]

    def contar_origen(self) -> int:
        with Session(self._engine_origen) as s:
            return s.execute(
                text(f"SELECT COUNT(*) FROM {self.tabla_origen()}")
            ).scalar_one()

    def contar_destino(self) -> int:
        with Session(self._engine_destino) as s:
            return s.execute(
                text(f"SELECT COUNT(*) FROM {self.tabla_destino()}")
            ).scalar_one()

    def migrar(
        self, limite: Optional[int] = None, offset: int = 0
    ) -> dict:
        """
        Ejecuta la migración completa (o parcial con limite/offset).
        Devuelve {"exitosos": int, "errores": list, "total": int}.
        """
        print(f"\n  ▶ {self.tabla_origen()} → {self.tabla_destino()}", flush=True)

        registros = self.leer_origen(limite=limite, offset=offset)
        exitosos = 0
        errores: list[dict] = []
        mapa = self.mapeo_campos()

        with Session(self._engine_destino) as session:
            for reg in registros:
                try:
                    # 1. Renombrar y filtrar columnas
                    mapeado: dict = {}
                    for col_origen, valor in reg.items():
                        col_destino = mapa.get(col_origen, col_origen)
                        if col_destino is not None:      # None = descartar campo
                            mapeado[col_destino] = valor

                    # 2. Transformación custom (fechas, defaults, campos nuevos…)
                    transformado = self.transformar_registro(mapeado)

                    # 3. Encriptar campos sensibles (skip si ya es bytes: ya encriptado)
                    for campo in self.campos_a_encriptar():
                        if campo in transformado and transformado[campo] is not None:
                            valor = transformado[campo]
                            if not isinstance(valor, (bytes, bytearray)):
                                transformado[campo] = self.crypto.encriptar(str(valor))

                    # 4. Insertar en gesmed
                    self._insertar(session, transformado)
                    exitosos += 1

                except Exception as exc:
                    errores.append({"id": list(reg.values())[0], "error": str(exc)})

            session.commit()

        total = len(registros)
        estado = "✓" if not errores else "✗"
        print(
            f"  {estado} {exitosos}/{total} registros migrados"
            + (f"  ({len(errores)} errores)" if errores else ""),
            flush=True,
        )
        return {"exitosos": exitosos, "errores": errores, "total": total}

    def verificar_migracion(self) -> dict:
        """Compara conteos entre origen y destino."""
        n_origen = self.contar_origen()
        n_destino = self.contar_destino()
        ok = n_origen == n_destino
        return {
            "tabla": self.tabla_destino(),
            "origen": n_origen,
            "destino": n_destino,
            "ok": ok,
        }

    def truncar_destino(self) -> None:
        """Vacía la tabla destino y reinicia el AUTO_INCREMENT a 1."""
        tabla = self.tabla_destino()
        with Session(self._engine_destino) as session:
            session.execute(text("SET FOREIGN_KEY_CHECKS=0"))
            session.execute(text(f"DELETE FROM {tabla}"))
            session.execute(text(f"ALTER TABLE {tabla} AUTO_INCREMENT = 1"))
            session.execute(text("SET FOREIGN_KEY_CHECKS=1"))
            session.commit()

    # ── Privados ──────────────────────────────────────────────────────────────

    def _insertar(self, session: Session, registro: dict) -> None:
        """INSERT parametrizado en gesmed. Maneja bytes (BLOB) nativamente."""
        cols = list(registro.keys())
        placeholders = ", ".join(f":{c}" for c in cols)
        nombres = ", ".join(cols)
        sql = text(
            f"INSERT INTO {self.tabla_destino()} ({nombres}) VALUES ({placeholders})"
        )
        session.execute(sql, registro)
