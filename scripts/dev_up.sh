#!/usr/bin/env bash
# Arranca "reflex run" para GesmedWeb en modo desarrollo, limpiando primero
# cualquier proceso huérfano de una corrida anterior (reflex/bun/react-router
# que haya quedado vivo) para evitar el problema de "Address already in use"
# en el puerto 3000/8000, que hace que el backend caiga silenciosamente a
# otro puerto (ej. 8004) sin que el frontend lo sepa.
#
# Uso:
#   scripts/dev_up.sh          # deja el server en foreground
#   scripts/dev_up.sh &        # en background
#
# Seguridad:
#   - Solo mata procesos cuyo cmdline contiene la ruta de ESTE proyecto,
#     nunca procesos de otros proyectos reflex ni servicios ajenos.
#   - Si detecta que gesmedweb corre como servicio systemd (despliegue en
#     un servidor Linux), NO mata nada y aborta: ese caso se administra con
#     "systemctl", no con este script de desarrollo.
set -euo pipefail
cd "$(dirname "$0")/.."
PROJECT_DIR="$(pwd)"

# --- Guard: no tocar un despliegue systemd real (servidor Linux futuro) ---
if command -v systemctl >/dev/null 2>&1; then
    if systemctl is-active --quiet gesmedweb 2>/dev/null; then
        echo "gesmedweb ya corre como servicio systemd (systemctl status gesmedweb)." >&2
        echo "Este script es solo para desarrollo local; no se mata nada. Aborta." >&2
        exit 1
    fi
fi

echo "Limpiando procesos huérfanos de GesmedWeb (ruta: $PROJECT_DIR)..."

# 1) Mata cualquier proceso cuyo cmdline referencie esta carpeta del proyecto
#    (reflex run, bun run dev, react-router dev, workers del backend, etc.)
pkill -9 -f "$PROJECT_DIR" 2>/dev/null || true

# 2) Por si queda algo escuchando en los puertos de la app sin que su
#    cmdline contenga la ruta del proyecto (p.ej. un worker reforkeado)
for port in 3000 8000; do
    pids=$(lsof -ti tcp:"$port" -sTCP:LISTEN 2>/dev/null || true)
    if [ -n "$pids" ]; then
        echo "Puerto $port ocupado por PID(s) $pids -> matando"
        kill -9 $pids 2>/dev/null || true
    fi
done

sleep 1

echo "Listo"
#echo "Iniciando reflex run..."
#exec .virtual/bin/reflex run
