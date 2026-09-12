"""
estructura_parametros_fijos.py — Extiende parametros_fijos.py agregando el
volcado de la ESTRUCTURA completa de gesmed (sql/gesmed_estructura.sql),
que es el archivo que aplica migrations/instalador.py al crear una base nueva
(ver paso_aplicar_schema()).

Se excluyen del volcado las tablas propias de la integración con amaymed
(vistas/tablas de conciliación que solo existen en el servidor de origen y no
tienen sentido en una instalación nueva LIMPIA o MIGRADA):
    atencion_amaymed, atencion_amaymed_gesmed,
    diagnostico_amaymed, diagnostico_amaymed_gesmed

Equivale a:
    mysqldump --no-data --routines --triggers \\
        --ignore-table=gesmed.atencion_amaymed \\
        --ignore-table=gesmed.atencion_amaymed_gesmed \\
        --ignore-table=gesmed.diagnostico_amaymed \\
        --ignore-table=gesmed.diagnostico_amaymed_gesmed \\
        -h localhost -u med_admin -p gesmed > sql/gesmed_estructura.sql

...pero leyendo host/puerto/usuario/password desde GESMED_DB_URL (misma
convención que el resto de migrations/*.py) en lugar de tenerlos hardcodeados.

Modo de trabajo:
    extraer_estructura() → genera solo sql/gesmed_estructura.sql
    extraer_todo()       → genera sql/gesmed_estructura.sql y luego
                            sql/parametros_fijos.sql (llama a
                            parametros_fijos.extraer()), en ese orden.

Uso:
    # Regenerar solo la estructura (cuando cambia el esquema: nueva tabla/columna)
    .virtual/bin/python -m migrations.estructura_parametros_fijos --estructura

    # Regenerar estructura + catálogos en un solo paso
    .virtual/bin/python -m migrations.estructura_parametros_fijos --todo

Variables de entorno:
    GESMED_DB_URL — misma convención que usa la app (ver GesmedWeb/querys/querys.py)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv
load_dotenv(_ROOT / ".env")

from migrations.migrador_base import db_params as _db_params
from migrations import parametros_fijos

ARCHIVO_ESTRUCTURA = _ROOT / "sql" / "gesmed_estructura.sql"

_DB_DEFAULT_URL = "mysql+pymysql://med_admin:gesmed01@localhost:3306/gesmed"

# Tablas de la integración con amaymed: no existen en un servidor nuevo y no
# deben quedar en el esquema base que instala migrations/instalador.py.
TABLAS_IGNORADAS = [
    "atencion_amaymed",
    "atencion_amaymed_gesmed",
    "diagnostico_amaymed",
    "diagnostico_amaymed_gesmed",
]


def extraer_estructura() -> bool:
    """Vuelca la estructura completa (sin datos) de gesmed a
    sql/gesmed_estructura.sql, excluyendo TABLAS_IGNORADAS."""
    p = _db_params("GESMED_DB_URL", _DB_DEFAULT_URL)
    ARCHIVO_ESTRUCTURA.parent.mkdir(exist_ok=True)

    cmd = [
        "mysqldump",
        f"--host={p['host']}",
        f"--port={p['port']}",
        f"--user={p['user']}",
        f"--password={p['password']}",
        "--no-data",
        "--routines",
        "--triggers",
        *[f"--ignore-table={p['name']}.{t}" for t in TABLAS_IGNORADAS],
        p["name"],
    ]
    try:
        with open(ARCHIVO_ESTRUCTURA, "w") as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, timeout=300)

        if result.returncode != 0:
            print(f"  ✗ mysqldump: {result.stderr.decode()}")
            return False

        size_kb = ARCHIVO_ESTRUCTURA.stat().st_size // 1024
        print(f"  ✓ Estructura generada: {ARCHIVO_ESTRUCTURA.relative_to(_ROOT)}  ({size_kb} KB)")
        return True
    except FileNotFoundError:
        print("  ✗ mysqldump no encontrado. Instale mysql-client o mariadb-client.")
        return False
    except Exception as e:
        print(f"  ✗ Error generando estructura: {e}")
        return False


def extraer_todo() -> bool:
    """Genera gesmed_estructura.sql y, a continuación, parametros_fijos.sql."""
    if not extraer_estructura():
        return False
    return parametros_fijos.extraer()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Genera sql/gesmed_estructura.sql (y opcionalmente sql/parametros_fijos.sql)"
    )
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--estructura", action="store_true",
                        help="Genera solo sql/gesmed_estructura.sql")
    grupo.add_argument("--todo", action="store_true",
                        help="Genera sql/gesmed_estructura.sql y luego sql/parametros_fijos.sql")
    args = parser.parse_args()

    ok = extraer_estructura() if args.estructura else extraer_todo()
    sys.exit(0 if ok else 1)
