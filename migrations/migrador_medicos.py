"""
migrador_medicos.py — Migra amaymed.medico → gesmed.points (cuentas de médicos).

amaymed.medico NO tiene id numérico: su PK es nombre_medico (texto). Por
eso cada médico migrado recibe un id_medico NUEVO por AUTO_INCREMENT en
gesmed.points — no existe un id original que "conservar".

La contraseña de amaymed (columna `clave`, varchar(15)) es texto plano, no
un hash — nunca se migra tal cual. En su lugar se genera una contraseña
temporal aleatoria por médico, se guarda hasheada con bcrypt (igual que
crear_admin_inicial.py), y se imprime UNA SOLA VEZ en pantalla para que el
administrador se la entregue a cada médico por un canal seguro y le pida
cambiarla en su primer ingreso.

Debe correrse ANTES de migrations.orquestador — el orquestador resuelve la
atención/diagnóstico de cada médico buscando su nombre en gesmed.points, así
que si un médico no está aquí todavía, sus registros clínicos caen al
--medico-id de respaldo (fallback) que se le pase al orquestador.

Es idempotente: si ya existe un usuario con ese `usuario` en gesmed.points,
se omite (no se sobrescribe ni se reporta como error).

Uso:
    .virtual/bin/python -m migrations.migrador_medicos
"""

from __future__ import annotations

import os
import secrets
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv
load_dotenv(_ROOT / ".env")

import bcrypt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

# amaymed.medico.permisos → gesmed.points.rol
# Roles válidos en gesmed: SECRETARIA | MEDICO_CONSULTA | MEDICO_ATENCION | ADMIN
_MAPA_ROL = {
    "M": "MEDICO_ATENCION",
}
_ROL_DEFAULT = "MEDICO_ATENCION"


def _engine_amaymed():
    url = os.environ.get(
        "AMAYMED_DB_URL",
        "mysql+pymysql://med_admin:gesmed01@localhost:3306/amaymed",
    )
    return create_engine(url, echo=False, pool_pre_ping=True)


def _engine_gesmed():
    url = os.environ.get(
        "GESMED_DB_URL",
        "mysql+pymysql://med_admin:gesmed01@localhost:3306/gesmed",
    )
    return create_engine(url, echo=False, pool_pre_ping=True)


def migrar_medicos() -> list[dict]:
    """
    Migra todos los médicos de amaymed.medico a gesmed.points.

    Devuelve una lista de dicts {usuario, nombre_medico, id_medico,
    password_temporal} SOLO para los médicos recién creados en esta
    corrida — los que ya existían se omiten y no aparecen en el resultado.
    """
    engine_origen = _engine_amaymed()
    engine_destino = _engine_gesmed()

    creados: list[dict] = []

    with Session(engine_origen) as s_origen, Session(engine_destino) as s_destino:
        medicos = s_origen.execute(text(
            "SELECT nombre_medico, especialidad, cod_especialidad, celular, "
            "email, activo, usuario, permisos FROM medico"
        )).mappings().all()

        for m in medicos:
            existe = s_destino.execute(
                text("SELECT id_medico FROM points WHERE usuario = :u"),
                {"u": m["usuario"]},
            ).scalar_one_or_none()
            if existe is not None:
                print(f"  … '{m['usuario']}' ya existe en gesmed.points (id_medico={existe}), se omite.")
                continue

            permisos_origen = (m["permisos"] or "").strip().upper()
            rol = _MAPA_ROL.get(permisos_origen)
            if rol is None:
                rol = _ROL_DEFAULT
                print(
                    f"  ⚠ permisos='{m['permisos']}' desconocido para '{m['usuario']}', "
                    f"asignando rol por defecto '{_ROL_DEFAULT}' — revisar manualmente si corresponde otro rol."
                )

            password_temp = secrets.token_urlsafe(10)
            clave_hash = bcrypt.hashpw(password_temp.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            resultado = s_destino.execute(
                text(
                    "INSERT INTO points "
                    "(nombre_medico, especialidad, cod_especialidad, celular, email, "
                    " usuario, clave, permisos, estado, rol) "
                    "VALUES (:nombre, :especialidad, :cod_especialidad, :celular, :email, "
                    " :usuario, :clave, '', :estado, :rol)"
                ),
                {
                    "nombre": m["nombre_medico"],
                    "especialidad": m["especialidad"],
                    "cod_especialidad": m["cod_especialidad"],
                    "celular": m["celular"],
                    "email": m["email"],
                    "usuario": m["usuario"],
                    "clave": clave_hash,
                    "estado": int(bool(m["activo"])),
                    "rol": rol,
                },
            )
            nuevo_id = resultado.lastrowid

            creados.append({
                "usuario": m["usuario"],
                "nombre_medico": m["nombre_medico"],
                "id_medico": nuevo_id,
                "password_temporal": password_temp,
            })

        s_destino.commit()

    return creados


def _imprimir_resumen(creados: list[dict]) -> None:
    if not creados:
        print("\n  No se creó ningún médico nuevo (todos ya existían en gesmed.points).")
        return

    print(f"\n{'═'*78}")
    print("  MÉDICOS MIGRADOS — contraseñas temporales (se muestran UNA SOLA VEZ)")
    print(f"{'═'*78}")
    for c in creados:
        print(
            f"  id_medico={c['id_medico']:<4}  usuario={c['usuario']:<15}  "
            f"{c['nombre_medico']:<30}  password_temporal={c['password_temporal']}"
        )
    print(f"{'─'*78}")
    print("  Entregar estas contraseñas a cada médico por un canal seguro (no por")
    print("  email/chat en texto plano) y pedirles que la cambien en su primer")
    print("  ingreso. Este listado NO queda guardado en ningún archivo ni log.")
    print(f"{'═'*78}\n")
    print("  IDs asignados (usar como --medico-id de respaldo en migrations.orquestador")
    print("  si corresponde, o para verificar la atribución de datos migrados):")
    for c in creados:
        print(f"    {c['nombre_medico']} → id_medico={c['id_medico']}")
    print()


if __name__ == "__main__":
    resultado = migrar_medicos()
    _imprimir_resumen(resultado)
