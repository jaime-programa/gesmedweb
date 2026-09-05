"""
upsert_medicamento_presentacion.py — Upsert dentro de gesmed:
    gesmed.presentacion_medicamentos → gesmed.medicamento_presentacion

No es una migración amaymed → gesmed (ambas tablas viven en gesmed), por eso
no usa MigradorTabla/orquestador.py: es un script independiente de una sola
base de datos.

El emparejamiento se hace por id_presentacion: ese id es la clave y prevalece
sobre lo que ya exista en destino.

Comportamiento:
    - id_presentacion ya existe en medicamento_presentacion
      → UPDATE nombre_presentacion y en_uso con los valores de origen
        (sobrescribe lo que hubiera en destino para ese id).
    - id_presentacion no existe → INSERT con ese mismo id_presentacion
      explícito (no autogenerado).

⚠ Al sobrescribir por id, cualquier fila de destino que ya usara ese id con
otro contenido pierde ese contenido (y cualquier FK existente hacia ese id
pasa a apuntar, semánticamente, a la nueva presentación).

Uso:
    GESMED_DB_URL=<url opcional> .virtual/bin/python -m migrations.upsert_medicamento_presentacion
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session


def _engine():
    url = os.environ.get(
        "GESMED_DB_URL",
        "mysql+pymysql://med_admin:gesmed01@localhost:3306/gesmed",
    )
    return create_engine(url, echo=False, pool_pre_ping=True)


def ejecutar_upsert() -> dict:
    engine = _engine()

    with Session(engine) as session:
        origen = session.execute(
            text("SELECT id_presentacion, nombre_presentacion, en_uso FROM presentacion_medicamentos")
        ).mappings().all()

        ids_destino = {
            row.id_presentacion
            for row in session.execute(text("SELECT id_presentacion FROM medicamento_presentacion"))
        }

        actualizados = 0
        insertados = 0
        errores: list[dict] = []

        for fila in origen:
            try:
                if fila["id_presentacion"] in ids_destino:
                    session.execute(
                        text(
                            "UPDATE medicamento_presentacion "
                            "SET nombre_presentacion = :nombre, en_uso = :en_uso "
                            "WHERE id_presentacion = :id"
                        ),
                        {
                            "nombre": fila["nombre_presentacion"],
                            "en_uso": fila["en_uso"],
                            "id": fila["id_presentacion"],
                        },
                    )
                    actualizados += 1
                else:
                    session.execute(
                        text(
                            "INSERT INTO medicamento_presentacion "
                            "(id_presentacion, nombre_presentacion, en_uso) "
                            "VALUES (:id, :nombre, :en_uso)"
                        ),
                        {
                            "id": fila["id_presentacion"],
                            "nombre": fila["nombre_presentacion"],
                            "en_uso": fila["en_uso"],
                        },
                    )
                    insertados += 1
            except Exception as exc:
                errores.append({"id": fila["id_presentacion"], "error": str(exc)})

        session.commit()

    resultado = {
        "actualizados": actualizados,
        "insertados": insertados,
        "errores": errores,
        "total": len(origen),
    }
    print(
        f"  ✓ {actualizados} actualizados por id (UPDATE), "
        f"{insertados} nuevos (INSERT)"
        + (f", {len(errores)} errores" if errores else ""),
        flush=True,
    )
    for err in errores:
        print(f"      ✗ id={err['id']}  {err['error']}", flush=True)
    return resultado


if __name__ == "__main__":
    ejecutar_upsert()
