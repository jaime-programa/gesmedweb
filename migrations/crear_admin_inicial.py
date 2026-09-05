"""
crear_admin_inicial.py — Siembra el primer usuario ADMIN en gesmed.points
al instalar en un servidor nuevo.

points queda fuera de parametros_fijos.py a propósito (son cuentas reales,
con hash bcrypt de contraseña — no debe distribuirse en un script de
instalación genérico). En su lugar, este script crea UN admin nuevo,
pidiendo la contraseña de forma interactiva (nunca como argumento en texto
plano, para que no quede en el historial de la shell ni en logs).

Es idempotente: si ya existe un usuario con ese `usuario`, no hace nada.

Uso:
    .virtual/bin/python -m migrations.crear_admin_inicial \\
        --usuario admin --nombre "Administrador" --email admin@dominio.com

    (pedirá la contraseña por prompt oculto)

Variables de entorno (mismas que orquestador.py / parametros_fijos.py):
    GESMED_DB_URL   mysql+pymysql://med_admin:gesmed01@localhost:3306/gesmed
"""

from __future__ import annotations

import argparse
import getpass
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import bcrypt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session


def _engine():
    url = os.environ.get(
        "GESMED_DB_URL",
        "mysql+pymysql://med_admin:gesmed01@localhost:3306/gesmed",
    )
    return create_engine(url, echo=False, pool_pre_ping=True)


def crear_admin_inicial(
    usuario: str,
    nombre: str,
    email: str,
    clave_plain: str,
    especialidad: str = "",
    cod_especialidad: str = "",
    celular: str = "",
) -> bool:
    engine = _engine()
    with Session(engine) as session:
        existe = session.execute(
            text("SELECT id_medico FROM points WHERE usuario = :u"),
            {"u": usuario},
        ).scalar_one_or_none()
        if existe is not None:
            print(f"  ✗ Ya existe un usuario '{usuario}' (id_medico={existe}). No se crea nada.")
            return False

        clave_hash = bcrypt.hashpw(clave_plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        session.execute(
            text(
                "INSERT INTO points "
                "(nombre_medico, especialidad, cod_especialidad, celular, email, "
                " usuario, clave, permisos, estado, rol) "
                "VALUES (:nombre, :especialidad, :cod_especialidad, :celular, :email, "
                " :usuario, :clave, '', 1, 'ADMIN')"
            ),
            {
                "nombre": nombre,
                "especialidad": especialidad,
                "cod_especialidad": cod_especialidad,
                "celular": celular,
                "email": email,
                "usuario": usuario,
                "clave": clave_hash,
            },
        )
        session.commit()

    print(f"  ✓ Usuario admin '{usuario}' creado.")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crea el primer usuario ADMIN en gesmed.points")
    parser.add_argument("--usuario", required=True)
    parser.add_argument("--nombre", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--especialidad", default="")
    parser.add_argument("--cod-especialidad", default="", dest="cod_especialidad")
    parser.add_argument("--celular", default="")
    args = parser.parse_args()

    clave = getpass.getpass("Contraseña para el nuevo admin: ")
    confirmacion = getpass.getpass("Repetir contraseña: ")
    if clave != confirmacion:
        print("  ✗ Las contraseñas no coinciden.")
        sys.exit(1)
    if len(clave) < 8:
        print("  ✗ La contraseña debe tener al menos 8 caracteres.")
        sys.exit(1)

    ok = crear_admin_inicial(
        usuario=args.usuario,
        nombre=args.nombre,
        email=args.email,
        clave_plain=clave,
        especialidad=args.especialidad,
        cod_especialidad=args.cod_especialidad,
        celular=args.celular,
    )
    sys.exit(0 if ok else 1)
