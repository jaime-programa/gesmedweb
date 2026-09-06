"""
parametros_fijos.py — Congela e instala en un solo proceso las tablas de
parámetros/catálogo de gesmed, para poder "instalar" gesmed en un servidor
nuevo sin depender de amaymed.

Tablas cubiertas (catálogos fijos, no datos de pacientes):
    cie10, medicamentos, medicamento_presentacion, medicamento_tipo,
    examenes_laboratorio_catalogo, examenes_laboratorio_grupo,
    examen_catalogo, examen_tipo, lista_signosvitales, points...

    ⚠ points (usuarios/médicos) queda EXCLUIDA a propósito: contiene hashes
    bcrypt de cuentas reales y no debe distribuirse en un script de
    instalación genérico. Cada servidor nuevo crea su propio usuario admin
    por separado (ver GesmedWeb/querys/querys.py).

Modo de trabajo (igual patrón que orquestador.py: subprocess a mysqldump/mysql):

    congelar()  → vuelca estructura + datos actuales de gesmed local a
                  sql/parametros_fijos.sql (un solo archivo, con
                  --add-drop-table para que sea idempotente).
    instalar()  → aplica ese archivo contra la base de datos destino
                  (por defecto gesmed local; en un servidor nuevo, apunta
                  las variables de entorno GESMED_DB_* a esa base).

Uso:
    # Regenerar el snapshot a partir del gesmed local actual (cuando cambian catálogos)
    .virtual/bin/python -m migrations.parametros_fijos --congelar

    # Instalar/reinstalar las tablas de parámetros en la base destino
    .virtual/bin/python -m migrations.parametros_fijos --instalar

Variables de entorno (mismas que orquestador.py, para mysqldump/mysql):
    GESMED_DB_HOST, GESMED_DB_PORT, GESMED_DB_USER, GESMED_DB_PASSWORD, GESMED_DB_NAME
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv
load_dotenv(_ROOT / ".env")

TABLAS = [
    "cie10",
    "medicamentos",
    "medicamento_presentacion",
    "medicamento_tipo",
    "examenes_laboratorio_catalogo",
    "examenes_laboratorio_grupo",
    "examen_catalogo",
    "examen_tipo",
    "lista_signosvitales",
    "reporte_celda",
    "reporte_imagen",
    "reporte_impreso",
    "reporte_seccion",
    "seguro_medico",
    "tipo_cita",
]

ARCHIVO_SNAPSHOT = _ROOT / "sql" / "parametros_fijos.sql"


def _db_params() -> dict:
    return {
        "host":     os.environ.get("GESMED_DB_HOST",     "localhost"),
        "port":     os.environ.get("GESMED_DB_PORT",     "3306"),
        "user":     os.environ.get("GESMED_DB_USER",     "med_admin"),
        "password": os.environ.get("GESMED_DB_PASSWORD", "gesmed01"),
        "name":     os.environ.get("GESMED_DB_NAME",     "gesmed"),
    }


def congelar() -> bool:
    """Vuelca estructura + datos actuales de TABLAS a un único archivo .sql."""
    p = _db_params()
    ARCHIVO_SNAPSHOT.parent.mkdir(exist_ok=True)

    cmd = [
        "mysqldump",
        f"--host={p['host']}",
        f"--port={p['port']}",
        f"--user={p['user']}",
        f"--password={p['password']}",
        "--add-drop-table",
        "--complete-insert",
        "--extended-insert=FALSE",   # 1 INSERT por fila: legible y diffable en git
        "--single-transaction",
        "--no-tablespaces",
        p["name"],
        *TABLAS,
    ]
    try:
        with open(ARCHIVO_SNAPSHOT, "w") as f:
            f.write(
                "-- parametros_fijos.sql — generado por migrations/parametros_fijos.py --congelar\n"
                "-- Contiene estructura + datos de los catálogos fijos de gesmed (sin `points`).\n"
                "SET FOREIGN_KEY_CHECKS=0;\n\n"
            )
            f.flush()
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, timeout=300)
            f.write("\nSET FOREIGN_KEY_CHECKS=1;\n")

        if result.returncode != 0:
            print(f"  ✗ mysqldump: {result.stderr.decode()}")
            return False

        size_kb = ARCHIVO_SNAPSHOT.stat().st_size // 1024
        print(f"  ✓ Snapshot generado: {ARCHIVO_SNAPSHOT.relative_to(_ROOT)}  ({size_kb} KB, {len(TABLAS)} tablas)")
        return True
    except FileNotFoundError:
        print("  ✗ mysqldump no encontrado. Instale mysql-client o mariadb-client.")
        return False
    except Exception as e:
        print(f"  ✗ Error generando snapshot: {e}")
        return False


def instalar() -> bool:
    """Aplica sql/parametros_fijos.sql contra la base de datos destino."""
    if not ARCHIVO_SNAPSHOT.exists():
        print(f"  ✗ No existe {ARCHIVO_SNAPSHOT.relative_to(_ROOT)}. Ejecute primero --congelar.")
        return False

    p = _db_params()
    cmd = [
        "mysql",
        f"--host={p['host']}",
        f"--port={p['port']}",
        f"--user={p['user']}",
        f"--password={p['password']}",
        p["name"],
    ]
    try:
        with open(ARCHIVO_SNAPSHOT) as f:
            result = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, timeout=300)
        if result.returncode != 0:
            print(f"  ✗ Error instalando parámetros: {result.stderr.decode()}")
            return False
        print(f"  ✓ Parámetros instalados en {p['name']}@{p['host']} ({len(TABLAS)} tablas)")
        return True
    except FileNotFoundError:
        print("  ✗ cliente mysql no encontrado.")
        return False
    except Exception as e:
        print(f"  ✗ Error instalando parámetros: {e}")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Congela/instala las tablas de parámetros fijos de gesmed")
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--congelar", action="store_true", help="Vuelca el estado actual de gesmed local a sql/parametros_fijos.sql")
    grupo.add_argument("--instalar", action="store_true", help="Aplica sql/parametros_fijos.sql contra la base destino")
    args = parser.parse_args()

    ok = congelar() if args.congelar else instalar()
    sys.exit(0 if ok else 1)
