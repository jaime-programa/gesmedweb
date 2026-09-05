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
