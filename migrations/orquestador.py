"""
orquestador.py — Migración masiva amaymed → gesmed con encriptación AES-256-GCM.

Uso:
    cd /ruta/al/proyecto
    GESMED_MASTER_KEY=<hex64> .virtual/bin/python -m migrations.orquestador

Variables de entorno opcionales (tienen defaults):
    GESMED_DB_URL   mysql+pymysql://med_admin:gesmed01@localhost:3306/gesmed
    AMAYMED_DB_URL  mysql+pymysql://med_admin:gesmed01@localhost:3306/amaymed
    GESMED_DB_HOST, GESMED_DB_PORT, GESMED_DB_USER, GESMED_DB_PASSWORD, GESMED_DB_NAME
    (usadas solo para mysqldump, independientes de la URL de SQLAlchemy)
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ── Asegurar que el paquete GesmedWeb sea importable ─────────────────────────
_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv
load_dotenv(_ROOT / ".env")

from migrations.migrador_paciente                  import MigradorPaciente
from migrations.migrador_diagnostico               import MigradorDiagnostico
from migrations.migrador_atencion                  import MigradorAtencion
from migrations.migrador_rel_atencion_diagnostico  import MigradorRelAtencionDiagnostico
from migrations.migrador_prescripcion              import MigradorPrescripcion
from migrations.migrador_prescripcion_cuidados     import MigradorPrescripcionCuidados
from migrations.migrador_certificado               import MigradorCertificado
from migrations.migrador_examenes                  import MigradorExamenesGrupo, MigradorExamenesCatalogo
from migrations.migrador_examenes_pedido           import MigradorExamenesPedido
from migrations.migrador_pedido_imagen             import MigradorPedidoImagen


# ── Parámetros de conexión para mysqldump ─────────────────────────────────────
def _db_params() -> dict:
    return {
        "host":     os.environ.get("GESMED_DB_HOST",     "localhost"),
        "port":     os.environ.get("GESMED_DB_PORT",     "3306"),
        "user":     os.environ.get("GESMED_DB_USER",     "med_admin"),
        "password": os.environ.get("GESMED_DB_PASSWORD", "gesmed01"),
        "name":     os.environ.get("GESMED_DB_NAME",     "gesmed"),
    }

def _amaymed_params() -> dict:
    return {
        "host":     os.environ.get("AMAYMED_DB_HOST",     "localhost"),
        "port":     os.environ.get("AMAYMED_DB_PORT",     "3306"),
        "user":     os.environ.get("AMAYMED_DB_USER",     "med_admin"),
        "password": os.environ.get("AMAYMED_DB_PASSWORD", "gesmed01"),
        "name":     os.environ.get("AMAYMED_DB_NAME",     "amaymed"),
    }


class OrquestadorMigracion:
    """
    Ejecuta la migración completa de un médico de amaymed a gesmed.

    Orden de migración (respeta dependencias FK):
        paciente → diagnostico → prescripcion → (tablas futuras)
    """

    # Orden FK correcto: tablas independientes primero
    ORDEN_TABLAS = ["paciente", "diagnostico", "atencion", "rel_atencion_diagnostico",
                    "prescripcion", "prescripcion_cuidados", "certificado",
                    "examenes_grupo", "examenes_catalogo", "examenes_pedido",
                    "pedido_imagen"]

    def __init__(self, medico_id: int) -> None:
        self.medico_id   = medico_id
        self.backup_dir  = _ROOT / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        self._reporte: list[dict] = []

    # ── Punto de entrada público ──────────────────────────────────────────────

    def ejecutar_migracion_completa(self) -> bool:
        """
        1. Backup automático (amaymed + gesmed)
        2. ALTER TABLE: columnas a BLOB
        3. Truncar tablas destino (orden inverso FK)
        4. Migrar (orden FK)
        5. Verificar conteos
        6. Rollback automático si cualquier tabla falla
        7. Reporte final

        Retorna True si todo fue exitoso, False si hubo fallos.
        """
        inicio = time.time()
        print(f"\n{'═'*60}")
        print(f"  MIGRACIÓN AMAYMED → GESMED   médico_id={self.medico_id}")
        print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'═'*60}")

        # ── Paso 1: Backups ───────────────────────────────────────────────────
        print("\n[1/5] Backups automáticos...")
        ok_bg = self._backup_gesmed() and self._backup_amaymed()
        if not ok_bg:
            print("  ✗ Backup fallido. Migración cancelada por seguridad.")
            return False

        # ── Paso 2: ALTER TABLE ───────────────────────────────────────────────
        print("\n[2/5] Aplicando scripts SQL (columnas a BLOB)...")
        ok_sql = self._ejecutar_scripts_sql()
        if not ok_sql:
            print("  ✗ Error en scripts SQL. Migración cancelada.")
            return False

        # ── Paso 3: Truncar destino (inverso FK) ──────────────────────────────
        print("\n[3/5] Vaciando tablas destino...")
        self._truncar_tablas()

        # ── Paso 4: Migrar ────────────────────────────────────────────────────
        print("\n[4/5] Migrando datos...")
        migradores = self._construir_migradores()
        exito_total = True

        for nombre, migrador in migradores.items():
            try:
                resultado = migrador.migrar()
            except Exception as exc:
                print(f"  ✗ {nombre}: excepción no capturada — {exc}")
                resultado = {"exitosos": 0, "errores": [{"id": "?", "error": str(exc)}], "total": 0}
                exito_total = False
            self._reporte.append({"tabla": nombre, **resultado})
            if resultado["errores"]:
                exito_total = False
                for err in resultado["errores"][:3]:
                    print(f"      ✗ id={err['id']}  {err['error']}")

        # ── Paso 5: Verificar ─────────────────────────────────────────────────
        print("\n[5/5] Verificando conteos...")
        verificaciones = []
        for _, migrador in migradores.items():
            try:
                v = migrador.verificar_migracion()
            except Exception as exc:
                v = {"tabla": migrador.tabla_destino(), "origen": "?", "destino": "?", "ok": False}
                print(f"  ✗ verificación fallida: {exc}")
            verificaciones.append(v)
            estado = "✓" if v["ok"] else "✗"
            print(f"  {estado} {v['tabla']:20s}  origen={v['origen']}  destino={v['destino']}")
            if not v["ok"]:
                exito_total = False

        # ── Rollback si hubo fallos ───────────────────────────────────────────
        if not exito_total:
            print("\n  ⚠ Se detectaron errores. Ejecutando rollback...")
            self._rollback()

        # ── Reporte final ─────────────────────────────────────────────────────
        self._imprimir_reporte(tiempo=time.time() - inicio, exito=exito_total)
        return exito_total

    # ── Backups ───────────────────────────────────────────────────────────────

    def _backup_gesmed(self) -> bool:
        return self._mysqldump(_db_params(), "gesmed")

    def _backup_amaymed(self) -> bool:
        return self._mysqldump(_amaymed_params(), "amaymed")

    def _mysqldump(self, params: dict, etiqueta: str) -> bool:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo = self.backup_dir / f"backup_{etiqueta}_{ts}.sql"
        cmd = [
            "mysqldump",
            f"--host={params['host']}",
            f"--port={params['port']}",
            f"--user={params['user']}",
            f"--password={params['password']}",
            "--add-drop-table",    # permite restaurar con: mysql < backup.sql
            "--single-transaction",
            params["name"],
        ]
        try:
            with open(archivo, "w") as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, timeout=120)
            if result.returncode != 0:
                print(f"  ✗ mysqldump {etiqueta}: {result.stderr.decode()}")
                return False
            size_kb = archivo.stat().st_size // 1024
            print(f"  ✓ Backup {etiqueta}: {archivo.name}  ({size_kb} KB)")
            return True
        except FileNotFoundError:
            print("  ✗ mysqldump no encontrado. Instale mysql-client o mariadb-client.")
            return False
        except Exception as e:
            print(f"  ✗ Error en mysqldump {etiqueta}: {e}")
            return False

    # ── Scripts SQL ───────────────────────────────────────────────────────────

    def _ejecutar_scripts_sql(self) -> bool:
        sql_dir = _ROOT / "sql"
        scripts = sorted([
            sql_dir / "001_paciente_encrypt.sql",
            sql_dir / "002_diagnostico_encrypt.sql",
            sql_dir / "003_prescripcion_encrypt.sql",
            sql_dir / "012_lkpaciente_nullable.sql",
        ])
        p = _db_params()
        ok = True
        for script in scripts:
            if not script.exists():
                print(f"  ✗ Script no encontrado: {script}")
                ok = False
                continue
            cmd = [
                "mysql",
                f"--host={p['host']}",
                f"--port={p['port']}",
                f"--user={p['user']}",
                f"--password={p['password']}",
                p["name"],
            ]
            try:
                with open(script) as f:
                    result = subprocess.run(
                        cmd, stdin=f, stderr=subprocess.PIPE, timeout=30
                    )
                if result.returncode != 0:
                    print(f"  ✗ {script.name}: {result.stderr.decode()}")
                    ok = False
                else:
                    print(f"  ✓ {script.name}")
            except Exception as e:
                print(f"  ✗ {script.name}: {e}")
                ok = False
        return ok

    # ── Truncar tablas ────────────────────────────────────────────────────────

    def _truncar_tablas(self) -> None:
        migradores = self._construir_migradores()
        # Orden inverso a FK para no violar restricciones
        for nombre in reversed(list(migradores.keys())):
            migradores[nombre].truncar_destino()
            print(f"  ✓ {nombre} vaciada")

    # ── Construcción de migradores ────────────────────────────────────────────

    def _construir_migradores(self) -> dict:
        """Retorna los migradores en el orden correcto de FK."""
        return {
            "paciente":                  MigradorPaciente(self.medico_id),
            "diagnostico":               MigradorDiagnostico(self.medico_id),
            "atencion":                  MigradorAtencion(self.medico_id),
            "rel_atencion_diagnostico":  MigradorRelAtencionDiagnostico(self.medico_id),
            "prescripcion":              MigradorPrescripcion(self.medico_id),
            "prescripcion_cuidados":     MigradorPrescripcionCuidados(self.medico_id),
            "certificado":               MigradorCertificado(self.medico_id),
            "examenes_grupo":            MigradorExamenesGrupo(self.medico_id),
            "examenes_catalogo":         MigradorExamenesCatalogo(self.medico_id),
            "examenes_pedido":           MigradorExamenesPedido(self.medico_id),
            "pedido_imagen":             MigradorPedidoImagen(self.medico_id),
        }

    # ── Rollback ──────────────────────────────────────────────────────────────

    def _rollback(self) -> None:
        """
        Restaura el backup más reciente de gesmed.
        El archivo debe haber sido generado con --add-drop-table.
        """
        backups = sorted(self.backup_dir.glob("backup_gesmed_*.sql"), reverse=True)
        if not backups:
            print("  ✗ No se encontró backup para rollback. Restaure manualmente.")
            return
        backup = backups[0]
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
            with open(backup) as f:
                result = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, timeout=300)
            if result.returncode == 0:
                print(f"  ✓ Rollback exitoso desde {backup.name}")
            else:
                print(f"  ✗ Rollback fallido: {result.stderr.decode()}")
                print(f"    Restaure manualmente: mysql {p['name']} < {backup}")
        except Exception as e:
            print(f"  ✗ Rollback error: {e}")
            print(f"    Restaure manualmente: mysql {p['name']} < {backup}")

    # ── Reporte ───────────────────────────────────────────────────────────────

    def _imprimir_reporte(self, tiempo: float, exito: bool) -> None:
        print(f"\n{'═'*60}")
        print(f"  REPORTE FINAL")
        print(f"{'─'*60}")
        total_reg = sum(r["total"] for r in self._reporte)
        total_ok  = sum(r["exitosos"] for r in self._reporte)
        total_err = sum(len(r["errores"]) for r in self._reporte)

        for r in self._reporte:
            estado = "✓" if not r["errores"] else "✗"
            print(f"  {estado} {r['tabla']:20s}  {r['exitosos']}/{r['total']} migrados")
            for err in r["errores"][:5]:        # mostrar máximo 5 errores por tabla
                print(f"      ✗ id={err['id']}  {err['error']}")

        print(f"{'─'*60}")
        print(f"  Total: {total_ok}/{total_reg} registros  |  Errores: {total_err}")
        print(f"  Tiempo: {tiempo:.1f}s")
        estado_final = "✓ EXITOSA" if exito else "✗ CON ERRORES"
        print(f"  Migración: {estado_final}")
        print(f"{'═'*60}\n")


# ── Punto de entrada CLI ──────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Migración amaymed → gesmed")
    parser.add_argument(
        "--medico-id", type=int, default=1,
        help="ID del médico (default: 1)"
    )
    args = parser.parse_args()

    orq = OrquestadorMigracion(medico_id=args.medico_id)
    exito = orq.ejecutar_migracion_completa()
    sys.exit(0 if exito else 1)
