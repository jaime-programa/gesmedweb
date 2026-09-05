#!/usr/bin/env bash
# Aplica el guard contra "dispatch is not a function" en el state.js generado por Reflex.
# Ejecutar después de: reflex init / actualización de Reflex / borrado de .web/
#
# El bug: cuando llega un delta WebSocket antes de que todos los substates estén
# registrados, dispatch[substate] es undefined → TypeError que rompe el handler
# y deja el frontend desincronizado con el backend.

TARGET=".web/utils/state.js"

if [ ! -f "$TARGET" ]; then
    echo "ERROR: $TARGET no existe. ¿Ejecutaste 'reflex run' al menos una vez?"
    exit 1
fi

# Verifica si el parche ya está aplicado
if grep -q "unknown substate in delta" "$TARGET"; then
    echo "Parche ya aplicado en $TARGET"
    exit 0
fi

# Aplica el parche: agrega el guard antes de dispatch[substate](...)
python3 - <<'PYEOF'
import re, pathlib

path = pathlib.Path(".web/utils/state.js")
src = path.read_text()

old = "        dispatch[substate](update.delta[substate])"
new = (
    '        if (typeof dispatch[substate] !== "function") {\n'
    '          console.warn("[Reflex] unknown substate in delta, skipping:", substate);\n'
    '          continue;\n'
    '        }\n'
    '        dispatch[substate](update.delta[substate])'
)

if old not in src:
    print("ADVERTENCIA: no se encontró el patrón esperado. ¿Cambió la versión de Reflex?")
    print("Revisa manualmente .web/utils/state.js alrededor de 'dispatch[substate]'")
    exit(1)

patched = src.replace(old, new, 1)
path.write_text(patched)
print("Parche aplicado correctamente en .web/utils/state.js")
PYEOF
