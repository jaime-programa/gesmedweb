"""
verificar_estructura.py — Compara la estructura real de gesmed contra lo
definido en GesmedWeb/modelos/mis_modelos.py (SQLModel).

Solo lectura: no modifica la base de datos. Reporta diferencias por tabla:
    - tablas que existen en un lado y no en el otro
    - columnas que faltan/sobran
    - nullable distinto
    - tipo de dato incompatible (comparación aproximada, MySQL/MariaDB no
      siempre reporta el mismo tipo que SQLAlchemy generaría)
    - PK y FKs distintas

Uso:
    .virtual/bin/python -m migrations.verificar_estructura
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from sqlalchemy import create_engine, inspect

from GesmedWeb.modelos.mis_modelos import SQLModel


def _engine():
    url = os.environ.get(
        "GESMED_DB_URL",
        "mysql+pymysql://med_admin:gesmed01@localhost:3306/gesmed",
    )
    return create_engine(url, echo=False, pool_pre_ping=True)


_SINONIMOS_TIPO = {
    "NUMERIC": "DECIMAL",
}


def _tipo_normalizado(col_type) -> str:
    """Nombre de tipo en mayúsculas, sin longitud/precisión/collation, para comparar a grosso modo."""
    texto = str(col_type).split(" COLLATE")[0]
    base = texto.split("(")[0].upper()
    return _SINONIMOS_TIPO.get(base, base)


def verificar() -> bool:
    engine = _engine()
    insp = inspect(engine)

    tablas_bd = set(insp.get_table_names())
    tablas_modelo = set(SQLModel.metadata.tables.keys())

    solo_en_bd = sorted(tablas_bd - tablas_modelo)
    solo_en_modelo = sorted(tablas_modelo - tablas_bd)
    comunes = sorted(tablas_bd & tablas_modelo)

    hay_diferencias = False

    print(f"\n{'═'*70}")
    print("  VERIFICACIÓN DE ESTRUCTURA: gesmed (BD real) vs mis_modelos.py")
    print(f"{'═'*70}")

    if solo_en_bd:
        hay_diferencias = True
        print(f"\n⚠ Tablas en la BD pero SIN modelo en mis_modelos.py ({len(solo_en_bd)}):")
        for t in solo_en_bd:
            print(f"    - {t}")

    if solo_en_modelo:
        hay_diferencias = True
        print(f"\n⚠ Modelos en mis_modelos.py SIN tabla en la BD ({len(solo_en_modelo)}):")
        for t in solo_en_modelo:
            print(f"    - {t}")

    for nombre_tabla in comunes:
        tabla_modelo = SQLModel.metadata.tables[nombre_tabla]

        cols_bd = {c["name"]: c for c in insp.get_columns(nombre_tabla)}
        cols_modelo = {c.name: c for c in tabla_modelo.columns}

        faltan_en_bd = sorted(set(cols_modelo) - set(cols_bd))
        sobran_en_bd = sorted(set(cols_bd) - set(cols_modelo))

        pk_bd = set(insp.get_pk_constraint(nombre_tabla).get("constrained_columns") or [])
        pk_modelo = {c.name for c in tabla_modelo.primary_key.columns}

        fks_bd = {
            (fk["constrained_columns"][0], fk["referred_table"], fk["referred_columns"][0])
            for fk in insp.get_foreign_keys(nombre_tabla)
            if fk.get("constrained_columns") and fk.get("referred_columns")
        }
        fks_modelo = {
            (fk.parent.name, fk.column.table.name, fk.column.name)
            for fk in tabla_modelo.foreign_keys
        }
        fks_faltan_en_bd = sorted(fks_modelo - fks_bd)
        fks_sobran_en_bd = sorted(fks_bd - fks_modelo)

        diffs_tipo = []
        diffs_nullable = []
        for nombre_col in sorted(set(cols_bd) & set(cols_modelo)):
            col_bd = cols_bd[nombre_col]
            col_modelo = cols_modelo[nombre_col]

            tipo_bd = _tipo_normalizado(col_bd["type"])
            tipo_modelo = _tipo_normalizado(col_modelo.type)
            # BLOB (bytes) en el modelo vs BLOB/VARBINARY/TINYBLOB/MEDIUMBLOB/LONGBLOB en BD
            equivalentes_blob = {"BLOB", "TINYBLOB", "MEDIUMBLOB", "LONGBLOB", "VARBINARY"}
            if tipo_bd != tipo_modelo and not (tipo_bd in equivalentes_blob and tipo_modelo in equivalentes_blob):
                diffs_tipo.append((nombre_col, tipo_bd, tipo_modelo))

            nullable_bd = col_bd["nullable"]
            nullable_modelo = col_modelo.nullable
            if bool(nullable_bd) != bool(nullable_modelo) and nombre_col not in pk_modelo:
                diffs_nullable.append((nombre_col, nullable_bd, nullable_modelo))

        pk_diff = pk_bd != pk_modelo

        if not (faltan_en_bd or sobran_en_bd or diffs_tipo or diffs_nullable or pk_diff
                or fks_faltan_en_bd or fks_sobran_en_bd):
            continue

        hay_diferencias = True
        print(f"\n── {nombre_tabla} ──")
        if faltan_en_bd:
            print(f"    ✗ columnas en el modelo, faltan en BD: {faltan_en_bd}")
        if sobran_en_bd:
            print(f"    ✗ columnas en BD, no están en el modelo: {sobran_en_bd}")
        if pk_diff:
            print(f"    ✗ PK distinta: BD={sorted(pk_bd)}  modelo={sorted(pk_modelo)}")
        for col, bd, modelo in diffs_tipo:
            print(f"    ✗ tipo distinto en '{col}': BD={bd}  modelo={modelo}")
        for col, bd, modelo in diffs_nullable:
            print(f"    ✗ nullable distinto en '{col}': BD={bd}  modelo={modelo}")
        for col, tabla, campo in fks_faltan_en_bd:
            print(f"    ✗ FK en el modelo, falta en BD: {col} → {tabla}.{campo}")
        for col, tabla, campo in fks_sobran_en_bd:
            print(f"    ✗ FK en BD, no está en el modelo: {col} → {tabla}.{campo}")

    print(f"\n{'─'*70}")
    if hay_diferencias:
        print("  ✗ Hay diferencias entre la BD y mis_modelos.py")
    else:
        print("  ✓ La estructura de gesmed coincide con mis_modelos.py")
    print(f"{'═'*70}\n")

    return not hay_diferencias


if __name__ == "__main__":
    ok = verificar()
    sys.exit(0 if ok else 1)
