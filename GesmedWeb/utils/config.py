"""
Lector del archivo configuracion.txt ubicado en la raíz del proyecto.

Formato del archivo (una entrada por línea):
    "CLAVE":valor_json

El valor puede ser cualquier tipo JSON válido:
    "IMAGENES_OK":"/data/gesmed/imagenes/"
    "ESCANEADOS_BRUTO":"/data/gesmed/escaneados/"
    "OPCIONES":{"reintentos": 3, "timeout": 30}
    "LISTA_IPS":["192.168.1.1", "10.0.0.1"]
    "MAX_UPLOAD":50
    "DEBUG":false
"""
import json
import pathlib
import re

_CONFIG_PATH = pathlib.Path(__file__).parent.parent.parent / "configuracion.txt"

_cache: dict[str, object] = {}
_loaded = False


def _cargar() -> None:
    global _loaded
    if _loaded:
        return
    _loaded = True
    try:
        for linea in _CONFIG_PATH.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if not linea:
                continue
            # Extraer la clave: empieza con "CLAVE": seguido del valor JSON
            m = re.match(r'"([^"]+)":\s*(.*)', linea)
            if not m:
                continue
            clave, valor_raw = m.group(1), m.group(2).strip()
            try:
                _cache[clave] = json.loads(valor_raw)
            except json.JSONDecodeError:
                # Guardar como cadena si no es JSON válido
                _cache[clave] = valor_raw
    except FileNotFoundError:
        pass


def leer_config(clave: str) -> str:
    """Devuelve el valor como cadena. Para claves con valores simples."""
    _cargar()
    return str(_cache.get(clave, ""))


def leer_config_json(clave: str) -> object:
    """Devuelve el valor con su tipo JSON real (dict, list, int, bool, str…)."""
    _cargar()
    return _cache.get(clave)


def ruta_imagenes() -> pathlib.Path:
    return pathlib.Path(leer_config("IMAGENES_OK"))


def ruta_escaneados() -> pathlib.Path:
    return pathlib.Path(leer_config("ESCANEADOS_BRUTO"))


def escribir_config(clave: str, valor: object) -> None:
    """Actualiza (o agrega) una clave en configuracion.txt, preservando las
    demás líneas tal cual están. Solo se usa para cambios administrativos
    poco frecuentes (ej. cambiar_base() en querys.py) — no se pretende que
    sea un almacén de escritura frecuente."""
    _cargar()
    _cache[clave] = valor

    lineas_previas = []
    if _CONFIG_PATH.exists():
        lineas_previas = _CONFIG_PATH.read_text(encoding="utf-8").splitlines()

    encontrada = False
    nuevas_lineas = []
    for linea in lineas_previas:
        m = re.match(r'"([^"]+)":\s*(.*)', linea.strip())
        if m and m.group(1) == clave:
            nuevas_lineas.append(f'"{clave}":{json.dumps(valor)}')
            encontrada = True
        else:
            nuevas_lineas.append(linea)
    if not encontrada:
        nuevas_lineas.append(f'"{clave}":{json.dumps(valor)}')

    _CONFIG_PATH.write_text("\n".join(nuevas_lineas) + "\n", encoding="utf-8")
