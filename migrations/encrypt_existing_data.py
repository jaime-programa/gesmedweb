"""
encrypt_existing_data.py — Encripta en-sitio los datos plaintext existentes en gesmed.

Ejecutar UNA VEZ después de aplicar los scripts SQL (001_, 002_, 003_)
y ANTES de volver a usar la aplicación.

Uso:
    GESMED_MASTER_KEY=<hex64> .virtual/bin/python -m migrations.encrypt_existing_data

El script detecta automáticamente qué registros ya están encriptados
(blob ≥ 28 bytes que pasa la verificación AES-GCM) y salta los que ya lo están,
por lo que es seguro ejecutarlo más de una vez.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# Cargar .env si existe
_env_path = _ROOT / ".env"
if _env_path.exists():
    for _line in _env_path.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

from cryptography.exceptions import InvalidTag
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from GesmedWeb.crypto import GesmedCrypto

GESMED_DB_URL = os.environ.get(
    "GESMED_DB_URL",
    "mysql+pymysql://med_admin:gesmed01@localhost:3306/gesmed",
)
MEDICO_ID = int(os.environ.get("GESMED_MEDICO_ID", "1"))


def _ya_encriptado(crypto: GesmedCrypto, blob: bytes | None) -> bool:
    """Devuelve True si el blob es un ciphertext AES-GCM válido con la clave actual."""
    if blob is None or len(blob) < 28:
        return False
    try:
        crypto.desencriptar(blob)
        return True
    except (InvalidTag, ValueError):
        return False


def _a_str(valor) -> str:
    """Convierte bytes o str a str limpio."""
    if isinstance(valor, (bytes, bytearray)):
        return valor.decode("utf-8", errors="replace")
    return str(valor) if valor is not None else ""


def encrypt_pacientes(session: Session, crypto: GesmedCrypto) -> None:
    rows = session.execute(
        text(
            "SELECT nro_hclinica, nombre_completo, cedula_id, "
            "direccion_reside, tf_celular, email, observacion FROM paciente"
        )
    ).mappings().all()

    # Campos NOT NULL (siempre tienen valor)
    _obligatorios = ("nombre_completo", "direccion_reside", "tf_celular")
    # Campos nullable (pueden ser None)
    _opcionales = ("cedula_id", "email", "observacion")

    encriptados = omitidos = 0
    for row in rows:
        updates: dict = {}

        for campo in _obligatorios:
            val = row[campo]
            if not _ya_encriptado(crypto, val):
                plaintext = _a_str(val)
                if plaintext:
                    updates[campo] = crypto.encriptar(plaintext)

        for campo in _opcionales:
            val = row[campo]
            if val is not None and not _ya_encriptado(crypto, val):
                plaintext = _a_str(val)
                if plaintext:
                    updates[campo] = crypto.encriptar(plaintext)

        if updates:
            sets = ", ".join(f"{c} = :{c}" for c in updates)
            session.execute(
                text(f"UPDATE paciente SET {sets} WHERE nro_hclinica = :pk"),
                {**updates, "pk": row["nro_hclinica"]},
            )
            encriptados += 1
        else:
            omitidos += 1

    session.commit()
    print(f"  ✓ paciente      {encriptados} encriptados  |  {omitidos} ya encriptados")


def encrypt_diagnosticos(session: Session, crypto: GesmedCrypto) -> None:
    rows = session.execute(
        text("SELECT id_diagnostico, observaciones FROM diagnostico")
    ).mappings().all()

    encriptados = omitidos = 0
    for row in rows:
        obs = row["observaciones"]
        if obs is None:
            continue
        if _ya_encriptado(crypto, obs):
            omitidos += 1
            continue
        plaintext = _a_str(obs)
        if plaintext:
            session.execute(
                text("UPDATE diagnostico SET observaciones = :v WHERE id_diagnostico = :pk"),
                {"v": crypto.encriptar(plaintext), "pk": row["id_diagnostico"]},
            )
            encriptados += 1

    session.commit()
    print(f"  ✓ diagnostico   {encriptados} encriptados  |  {omitidos} ya encriptados")


def encrypt_prescripciones(session: Session, crypto: GesmedCrypto) -> None:
    try:
        rows = session.execute(
            text("SELECT id_prescripcion, concentracion, indicaciones FROM prescripcion")
        ).mappings().all()
    except Exception:
        print("  ⚠ prescripcion  tabla no encontrada o columnas BLOB ausentes — omitida")
        return

    encriptados = omitidos = 0
    for row in rows:
        updates: dict = {}

        for campo in ("concentracion", "indicaciones"):
            val = row[campo]
            if val is None:
                continue
            if _ya_encriptado(crypto, val):
                omitidos += 1
                continue
            plaintext = _a_str(val)
            if plaintext:
                updates[campo] = crypto.encriptar(plaintext)

        if updates:
            sets = ", ".join(f"{c} = :{c}" for c in updates)
            session.execute(
                text(f"UPDATE prescripcion SET {sets} WHERE id_prescripcion = :pk"),
                {**updates, "pk": row["id_prescripcion"]},
            )
            encriptados += 1

    session.commit()
    print(f"  ✓ prescripcion  {encriptados} encriptados  |  {omitidos} ya encriptados")


if __name__ == "__main__":
    print("\n══════════════════════════════════════════════")
    print("  Encriptación en-sitio de datos existentes")
    print("══════════════════════════════════════════════")

    engine = create_engine(GESMED_DB_URL, echo=False, pool_pre_ping=True)
    crypto = GesmedCrypto.para_medico(MEDICO_ID)

    with Session(engine) as session:
        encrypt_pacientes(session, crypto)
        encrypt_diagnosticos(session, crypto)
        encrypt_prescripciones(session, crypto)

    print("══════════════════════════════════════════════")
    print("  Listo. Puede reiniciar la aplicación.\n")
