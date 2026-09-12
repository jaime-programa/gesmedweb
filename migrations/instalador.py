"""
instalador.py — Instalador de GesmedWeb en un servidor nuevo.

Produce, en una sola corrida interactiva, uno de estos 3 resultados:
    1. Instalar solo una base "LIMPIA"  (esquema + parámetros fijos, sin datos de pacientes)
    2. Instalar solo una base "MIGRADA" (esquema + parámetros fijos + datos migrados desde
       un dump de amaymed)
    3. Instalar AMBAS, coexistiendo en el mismo servidor (LIMPIA y MIGRADA)

Para la opción MIGRADA (o AMBAS), se crea además una 3ª base de datos TEMPORAL donde se
importa el dump de amaymed indicado por el usuario; sobre esa base temporal corren
migrations.migrador_medicos y migrations.orquestador. Al terminar, se pregunta antes de
eliminarla (--drop--, es destructivo).

En ambos casos (LIMPIA y MIGRADA) se instalan también las tablas de parámetros fijos
(catálogos: cie10, medicamentos, examenes, etc. — ver migrations/parametros_fijos.py) y se
crea un usuario ADMIN nuevo e independiente (nunca se promueve un médico migrado a admin).

Al final, este script escribe/actualiza .env (GESMED_DB_URL / GESMED_DB_URL_M /
GESMED_MASTER_KEY) y configuracion.txt (clave "BASE") para que GesmedWeb arranque
apuntando a la base recién instalada — ver GesmedWeb/querys/querys.py (get_engine() /
cambiar_base()).

Requiere en el PATH: mysql, mysqldump (cliente MariaDB/MySQL).

Uso:
    .virtual/bin/python -m migrations.instalador
"""

from __future__ import annotations

import getpass
import os
import secrets
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote_plus

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv
load_dotenv(_ROOT / ".env")

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

SQL_DIR = _ROOT / "sql"
ESQUEMA_SQL = SQL_DIR / "gesmed_estructura.sql"
ENV_PATH = _ROOT / ".env"

DB_NAME = {"LIMPIA": "gesmed", "MIGRADA": "gesmed_migrada"}
ENV_KEY = {"LIMPIA": "GESMED_DB_URL", "MIGRADA": "GESMED_DB_URL_M"}


# ── Utilidades de entrada interactiva ────────────────────────────────────────

def _preguntar(prompt: str, default: str | None = None) -> str:
    etiqueta = f"{prompt} [{default}]: " if default is not None else f"{prompt}: "
    respuesta = input(etiqueta).strip()
    return respuesta or (default or "")


def _preguntar_password(prompt: str) -> str:
    return getpass.getpass(f"{prompt}: ")


def _confirmar(prompt: str, default_si: bool = False) -> bool:
    sufijo = "[S/n]" if default_si else "[s/N]"
    respuesta = input(f"{prompt} {sufijo}: ").strip().lower()
    if not respuesta:
        return default_si
    return respuesta in ("s", "si", "sí", "y", "yes")


def _construir_url(user: str, password: str, host: str, port: str, db: str) -> str:
    return f"mysql+pymysql://{user}:{quote_plus(password)}@{host}:{port}/{db}"


# ── Subprocess a mysql/mysqldump ──────────────────────────────────────────────

def _verificar_cliente_mysql() -> bool:
    if shutil.which("mysql") and shutil.which("mysqldump"):
        return True
    print("  ✗ No se encontró 'mysql'/'mysqldump' en el PATH. Instale el cliente MariaDB/MySQL.")
    return False


def _mysql_ejecutar_sql(params: dict, sql: str, timeout: int = 60) -> bool:
    """Ejecuta sentencias SQL sueltas contra el servidor (sin base específica)."""
    cmd = [
        "mysql",
        f"--host={params['host']}",
        f"--port={params['port']}",
        f"--user={params['user']}",
        f"--password={params['password']}",
        "-e", sql,
    ]
    try:
        result = subprocess.run(cmd, stderr=subprocess.PIPE, timeout=timeout)
        if result.returncode != 0:
            print(f"  ✗ mysql: {result.stderr.decode()}")
            return False
        return True
    except Exception as e:
        print(f"  ✗ Error ejecutando SQL: {e}")
        return False


def _mysql_importar_archivo(params: dict, db: str, archivo: Path, timeout: int = 900) -> bool:
    """Aplica un archivo .sql contra una base ya existente (mysql db < archivo)."""
    cmd = [
        "mysql",
        f"--host={params['host']}",
        f"--port={params['port']}",
        f"--user={params['user']}",
        f"--password={params['password']}",
        db,
    ]
    try:
        with open(archivo) as f:
            result = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, timeout=timeout)
        if result.returncode != 0:
            print(f"  ✗ mysql < {archivo.name}: {result.stderr.decode()}")
            return False
        return True
    except Exception as e:
        print(f"  ✗ Error importando {archivo.name}: {e}")
        return False


# ── Pasos del instalador ──────────────────────────────────────────────────────

def paso_pedir_modo() -> str:
    print("\n¿Qué desea instalar?")
    print("  1) Base LIMPIA   (esquema vacío + parámetros fijos)")
    print("  2) Base MIGRADA  (datos migrados desde un dump de amaymed)")
    print("  3) AMBAS (conviven en el mismo servidor)")
    while True:
        opcion = _preguntar("Opción", "1")
        if opcion == "1":
            return "LIMPIA"
        if opcion == "2":
            return "MIGRADA"
        if opcion == "3":
            return "AMBAS"
        print("  Opción inválida, ingrese 1, 2 o 3.")


def paso_pedir_admin_mariadb() -> dict:
    print("\nCredenciales de administrador de MariaDB (con privilegios para CREATE "
          "DATABASE / CREATE USER / GRANT):")
    host = _preguntar("Host", "localhost")
    port = _preguntar("Puerto", "3306")
    user = _preguntar("Usuario admin", "root")
    password = _preguntar_password("Password de admin")
    return {"host": host, "port": port, "user": user, "password": password}


def paso_pedir_credenciales_app(host: str, port: str) -> dict:
    print("\nUsuario de la aplicación (el que usará GesmedWeb para conectarse a sus bases):")
    user = _preguntar("Usuario de aplicación", "med_admin")
    password = _preguntar_password("Password de aplicación (se creará si no existe)")
    return {"user": user, "password": password}


def paso_crear_base_y_usuario(admin: dict, db_name: str, app_user: str, app_password: str) -> bool:
    # CREATE USER IF NOT EXISTS no actualiza la contraseña si la cuenta ya existía
    # de una corrida anterior (p.ej. tras reintentar por otro error) — el ALTER
    # USER siguiente la sincroniza siempre con lo que el operador acaba de teclear.
    sql = (
        f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
        f"CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci; "
        f"CREATE USER IF NOT EXISTS '{app_user}'@'%' IDENTIFIED BY '{app_password}'; "
        f"ALTER USER '{app_user}'@'%' IDENTIFIED BY '{app_password}'; "
        f"GRANT ALL PRIVILEGES ON `{db_name}`.* TO '{app_user}'@'%'; "
        f"FLUSH PRIVILEGES;"
    )
    if not _mysql_ejecutar_sql(admin, sql):
        return False
    print(f"  ✓ Base `{db_name}` y usuario '{app_user}' listos.")
    return True


def paso_aplicar_schema(admin: dict, db_name: str) -> bool:
    """Aplica el esquema con las credenciales de administrador (no las de la app):
    gesmed_estructura.sql define vistas con cláusula DEFINER explícita, y crear/
    recrear ese tipo de objeto requiere el privilegio SUPER/SET USER — algo que la
    cuenta de aplicación no debe tener, pero el admin de MariaDB sí."""
    if not ESQUEMA_SQL.exists():
        print(f"  ✗ No existe {ESQUEMA_SQL.relative_to(_ROOT)}.")
        return False
    if not _mysql_importar_archivo(admin, db_name, ESQUEMA_SQL):
        return False
    print(f"  ✓ Esquema aplicado en `{db_name}`.")
    return True


def paso_instalar_parametros_fijos() -> bool:
    from migrations import parametros_fijos
    return parametros_fijos.instalar()


def paso_instalar_base_logica(nombre_logico: str, admin: dict, app: dict) -> str | None:
    """Crea la BD física, aplica esquema + parámetros fijos. Devuelve la URL SQLAlchemy
    resultante, o None si algún paso falló."""
    db_name = DB_NAME[nombre_logico]
    host, port = admin["host"], admin["port"]

    print(f"\n── Instalando base {nombre_logico} (`{db_name}`) ──")
    if not paso_crear_base_y_usuario(admin, db_name, app["user"], app["password"]):
        return None
    if not paso_aplicar_schema(admin, db_name):
        return None

    url = _construir_url(app["user"], app["password"], host, port, db_name)
    os.environ["GESMED_DB_URL"] = url
    if not paso_instalar_parametros_fijos():
        return None
    print(f"  ✓ Parámetros fijos instalados en {nombre_logico}.")
    return url


def paso_asegurar_master_key() -> None:
    if os.environ.get("GESMED_MASTER_KEY", "").strip():
        return
    nueva = secrets.token_hex(32)
    os.environ["GESMED_MASTER_KEY"] = nueva
    _escribir_env({"GESMED_MASTER_KEY": nueva})
    print("  ✓ GESMED_MASTER_KEY generada y guardada en .env (necesaria para cifrar datos sensibles).")


def paso_crear_admin(url_db: str, nombre_logico: str) -> int | None:
    print(f"\n── Crear usuario ADMIN para la base {nombre_logico} ──")
    from migrations.crear_admin_inicial import crear_admin_inicial

    usuario = _preguntar("Usuario del admin", "admin")
    nombre = _preguntar("Nombre completo", "Administrador")
    email = _preguntar("Email", "")
    especialidad = _preguntar("Especialidad", "")
    cod_especialidad = _preguntar("Cód. especialidad", "")
    celular = _preguntar("Celular", "")

    while True:
        clave = _preguntar_password("Contraseña (mínimo 8 caracteres)")
        clave2 = _preguntar_password("Repetir contraseña")
        if clave != clave2:
            print("  ✗ Las contraseñas no coinciden, intente de nuevo.")
            continue
        if len(clave) < 8:
            print("  ✗ La contraseña debe tener al menos 8 caracteres.")
            continue
        break

    os.environ["GESMED_DB_URL"] = url_db
    ok = crear_admin_inicial(
        usuario=usuario, nombre=nombre, email=email, clave_plain=clave,
        especialidad=especialidad, cod_especialidad=cod_especialidad, celular=celular,
    )
    if not ok:
        return None

    engine = create_engine(url_db, echo=False, pool_pre_ping=True)
    with Session(engine) as s:
        id_medico = s.execute(
            text("SELECT id_medico FROM points WHERE usuario = :u"), {"u": usuario},
        ).scalar_one()
    return id_medico


def paso_pedir_dump_amaymed() -> Path:
    while True:
        ruta = _preguntar("Ruta al archivo .sql (dump de amaymed)")
        archivo = Path(ruta).expanduser()
        if archivo.exists():
            return archivo
        print(f"  ✗ No existe el archivo: {archivo}")


def paso_migrar_amaymed(admin: dict, url_gesmed_migrada: str, fallback_medico_id: int) -> bool:
    print("\n── Migración de datos desde amaymed ──")
    dump = paso_pedir_dump_amaymed()
    staging_db = "amaymed_staging"
    host, port = admin["host"], admin["port"]

    print(f"  Creando base temporal `{staging_db}`...")
    if not _mysql_ejecutar_sql(
        admin,
        f"CREATE DATABASE IF NOT EXISTS `{staging_db}` CHARACTER SET utf8mb4;",
    ):
        return False

    print(f"  Importando {dump.name} en `{staging_db}` (puede tardar varios minutos)...")
    if not _mysql_importar_archivo(admin, staging_db, dump):
        return False
    print("  ✓ Dump importado.")

    url_staging = _construir_url(admin["user"], admin["password"], host, port, staging_db)
    os.environ["AMAYMED_DB_URL"] = url_staging
    os.environ["GESMED_DB_URL"] = url_gesmed_migrada

    print("\n  Migrando médicos (amaymed.medico → gesmed.points)...")
    from migrations.migrador_medicos import migrar_medicos, _imprimir_resumen
    creados = migrar_medicos()
    _imprimir_resumen(creados)

    print("\n  Migrando datos clínicos (pacientes, atenciones, diagnósticos, etc.)...")
    from migrations.orquestador import OrquestadorMigracion
    orq = OrquestadorMigracion(medico_id=fallback_medico_id)
    exito = orq.ejecutar_migracion_completa()

    if _confirmar(f"\n¿Eliminar la base temporal `{staging_db}`?", default_si=True):
        if _mysql_ejecutar_sql(admin, f"DROP DATABASE `{staging_db}`;"):
            print(f"  ✓ Base temporal `{staging_db}` eliminada.")
    else:
        print(f"  … Base temporal `{staging_db}` conservada (elimínela manualmente cuando termine).")

    return exito


def paso_verificar_estructura(url_db: str, nombre_logico: str) -> None:
    print(f"\n── Verificando estructura de {nombre_logico} ──")
    os.environ["GESMED_DB_URL"] = url_db
    from migrations.verificar_estructura import verificar
    verificar()


# ── .env / configuracion.txt ──────────────────────────────────────────────────

def _escribir_env(pares: dict[str, str]) -> None:
    """Actualiza (o agrega) variables en .env, preservando comentarios y demás líneas."""
    lineas_previas = ENV_PATH.read_text(encoding="utf-8").splitlines() if ENV_PATH.exists() else []
    claves_pendientes = dict(pares)
    nuevas_lineas = []
    for linea in lineas_previas:
        despojada = linea.strip()
        if despojada and not despojada.startswith("#") and "=" in despojada:
            clave = despojada.split("=", 1)[0].strip()
            if clave in claves_pendientes:
                nuevas_lineas.append(f"{clave}={claves_pendientes.pop(clave)}")
                continue
        nuevas_lineas.append(linea)
    for clave, valor in claves_pendientes.items():
        nuevas_lineas.append(f"{clave}={valor}")
    ENV_PATH.write_text("\n".join(nuevas_lineas) + "\n", encoding="utf-8")


def paso_escribir_configuracion_base(base_activa: str) -> None:
    from GesmedWeb.utils.config import escribir_config
    escribir_config("BASE", base_activa)
    print(f"  ✓ configuracion.txt: BASE={base_activa}")


# ── Punto de entrada ───────────────────────────────────────────────────────────

def main() -> int:
    print("═" * 60)
    print("  INSTALADOR GESMEDWEB")
    print("═" * 60)

    if not _verificar_cliente_mysql():
        return 1

    modo = paso_pedir_modo()
    admin = paso_pedir_admin_mariadb()
    app = paso_pedir_credenciales_app(admin["host"], admin["port"])
    paso_asegurar_master_key()

    urls: dict[str, str] = {}
    admin_ids: dict[str, int] = {}

    if modo in ("LIMPIA", "AMBAS"):
        url = paso_instalar_base_logica("LIMPIA", admin, app)
        if url is None:
            print("\n✗ Falló la instalación de la base LIMPIA. Abortando.")
            return 1
        urls["LIMPIA"] = url
        id_admin = paso_crear_admin(url, "LIMPIA")
        if id_admin is None:
            print("\n✗ No se pudo crear el usuario admin de LIMPIA. Abortando.")
            return 1
        admin_ids["LIMPIA"] = id_admin

    if modo in ("MIGRADA", "AMBAS"):
        url_m = paso_instalar_base_logica("MIGRADA", admin, app)
        if url_m is None:
            print("\n✗ Falló la instalación de la base MIGRADA. Abortando.")
            return 1
        urls["MIGRADA"] = url_m
        # Admin SIEMPRE nuevo e independiente — no se promueve ningún médico migrado.
        id_admin_m = paso_crear_admin(url_m, "MIGRADA")
        if id_admin_m is None:
            print("\n✗ No se pudo crear el usuario admin de MIGRADA. Abortando.")
            return 1
        admin_ids["MIGRADA"] = id_admin_m

        exito_migracion = paso_migrar_amaymed(admin, url_m, fallback_medico_id=id_admin_m)
        if not exito_migracion:
            print(
                "\n⚠ La migración tuvo errores (ver reporte arriba). La base MIGRADA "
                "quedó instalada igualmente; revise y corrija los registros listados."
            )

    # ── .env ──────────────────────────────────────────────────────────────────
    pares_env = {ENV_KEY[b]: urls[b] for b in urls}
    _escribir_env(pares_env)
    print(f"\n✓ .env actualizado: {', '.join(pares_env.keys())}")

    # ── configuracion.txt ─────────────────────────────────────────────────────
    if modo == "AMBAS":
        base_activa = _preguntar("¿Cuál base debe quedar activa al iniciar? (LIMPIA/MIGRADA)", "LIMPIA").upper()
        if base_activa not in ("LIMPIA", "MIGRADA"):
            base_activa = "LIMPIA"
    else:
        base_activa = modo
    paso_escribir_configuracion_base(base_activa)

    # ── Verificación final ───────────────────────────────────────────────────
    for nombre_logico, url in urls.items():
        paso_verificar_estructura(url, nombre_logico)

    print("\n" + "═" * 60)
    print("  INSTALACIÓN COMPLETA")
    print(":"*20)
    print("  Revise que la IP del servidor esté registrada en el entorno")
    print("═" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
