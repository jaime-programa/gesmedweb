"""
test_crypto.py — Pruebas de GesmedCrypto
Ejecutar desde la raíz del proyecto:
    .virtual/bin/python test_crypto.py
"""

import gc
import os
import sys
import traceback

# ── Configurar PYTHONPATH para importar el paquete GesmedWeb ──────────────────
sys.path.insert(0, os.path.dirname(__file__))

# ── Clave de prueba (solo para este test, no es producción) ───────────────────
TEST_KEY = os.urandom(32).hex()

# ── Utilidades de reporte ─────────────────────────────────────────────────────
_resultados: list[tuple[str, bool, str]] = []

def prueba(nombre: str, ok: bool, detalle: str = "") -> None:
    estado = "PASSED" if ok else "FAILED"
    _resultados.append((nombre, ok, detalle))
    marca = "✓" if ok else "✗"
    print(f"  [{estado}] {marca}  {nombre}")
    if detalle:
        for linea in detalle.splitlines():
            print(f"             {linea}")

def seccion(titulo: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {titulo}")
    print(f"{'─' * 60}")

# ═════════════════════════════════════════════════════════════════════════════
# PRUEBA 5 — sin GESMED_MASTER_KEY (debe ejecutarse ANTES de definirla)
# ═════════════════════════════════════════════════════════════════════════════
seccion("5. Clave faltante → EnvironmentError explícito")

# Asegurarse de que NO esté definida y que el caché interno esté limpio
os.environ.pop("GESMED_MASTER_KEY", None)

# Recargar módulo para que el caché _key_cache sea None
if "GesmedWeb.crypto.gesmed_crypto" in sys.modules:
    del sys.modules["GesmedWeb.crypto.gesmed_crypto"]
if "GesmedWeb.crypto" in sys.modules:
    del sys.modules["GesmedWeb.crypto"]

from GesmedWeb.crypto.gesmed_crypto import GesmedCrypto   # importar sin clave

try:
    GesmedCrypto.para_medico(1)
    prueba("Lanza EnvironmentError si GESMED_MASTER_KEY no está definida",
           False, "No lanzó ninguna excepción")
except EnvironmentError as e:
    prueba("Lanza EnvironmentError si GESMED_MASTER_KEY no está definida",
           True, f"EnvironmentError: {e}")
except Exception as e:
    prueba("Lanza EnvironmentError si GESMED_MASTER_KEY no está definida",
           False, f"Excepción inesperada {type(e).__name__}: {e}")

# ── Ahora definir la clave y recargar el módulo ───────────────────────────────
os.environ["GESMED_MASTER_KEY"] = TEST_KEY

# Recargar para limpiar caché interno
for mod in list(sys.modules):
    if "gesmed_crypto" in mod or ("GesmedWeb.crypto" in mod):
        del sys.modules[mod]

from GesmedWeb.crypto.gesmed_crypto import GesmedCrypto
import GesmedWeb.crypto.gesmed_crypto as _crypto_mod

# ═════════════════════════════════════════════════════════════════════════════
# PRUEBA 1 — encriptar/desencriptar devuelve el dato original
# ═════════════════════════════════════════════════════════════════════════════
seccion("1. Encriptar → desencriptar devuelve el dato original")

crypto = GesmedCrypto.para_medico(1)

casos = [
    "Juan Pérez",
    "María Ángela López-Sánchez",
    "0912345678",
    "Observaciones con caracteres: ñ, ü, é, 中文, 🩺",
    "",   # cadena vacía
    "x",  # cadena de 1 char
]
for dato in casos:
    try:
        blob = crypto.encriptar(dato) if dato else None
        resultado = crypto.desencriptar(blob)
        ok = resultado == dato
        prueba(f'desencriptar(encriptar("{dato[:30]}")) == original', ok,
               "" if ok else f"Esperado: '{dato}' | Obtenido: '{resultado}'")
    except Exception as e:
        prueba(f'desencriptar(encriptar("{dato[:30]}"))', False,
               traceback.format_exc(limit=2))

# Prueba con None directamente
try:
    resultado = crypto.desencriptar(None)
    prueba('desencriptar(None) == ""', resultado == "",
           "" if resultado == "" else f"Obtenido: '{resultado}'")
except Exception as e:
    prueba('desencriptar(None) == ""', False, str(e))

# ═════════════════════════════════════════════════════════════════════════════
# PRUEBA 2 — IV aleatorio: dos encriptaciones del mismo dato → bytes distintos
# ═════════════════════════════════════════════════════════════════════════════
seccion("2. IV aleatorio → dos cifrados del mismo dato producen bytes diferentes")

dato = "Juan Pérez"
N = 10
blobs = [crypto.encriptar(dato) for _ in range(N)]
todos_distintos = len(set(blobs)) == N
prueba(f"Todas las {N} encriptaciones de '{dato}' son únicas", todos_distintos,
       "" if todos_distintos else "¡Colisión detectada — IV no es aleatorio!")

# Verificar que todos desencriptan al original
todos_ok = all(crypto.desencriptar(b) == dato for b in blobs)
prueba(f"Todos los {N} blobs se desencriptan al original", todos_ok)

# ═════════════════════════════════════════════════════════════════════════════
# PRUEBA 3 — GCM detecta manipulación del dato cifrado
# ═════════════════════════════════════════════════════════════════════════════
seccion("3. GCM detecta manipulación → lanza InvalidTag")

from cryptography.exceptions import InvalidTag

dato = "Información confidencial"
blob_original = crypto.encriptar(dato)

# Caso a: modificar 1 byte del ciphertext (después del nonce de 12 bytes)
blob_alterado = bytearray(blob_original)
blob_alterado[15] ^= 0xFF          # flip del byte 15 (dentro del ciphertext)
try:
    crypto.desencriptar(bytes(blob_alterado))
    prueba("Byte alterado en ciphertext → lanza InvalidTag", False,
           "No detectó la manipulación")
except InvalidTag:
    prueba("Byte alterado en ciphertext → lanza InvalidTag", True)
except Exception as e:
    prueba("Byte alterado en ciphertext → lanza InvalidTag", False, str(e))

# Caso b: modificar el tag (últimos 16 bytes)
blob_tag_alterado = bytearray(blob_original)
blob_tag_alterado[-1] ^= 0x01
try:
    crypto.desencriptar(bytes(blob_tag_alterado))
    prueba("Byte alterado en GCM-tag → lanza InvalidTag", False,
           "No detectó la manipulación")
except InvalidTag:
    prueba("Byte alterado en GCM-tag → lanza InvalidTag", True)
except Exception as e:
    prueba("Byte alterado en GCM-tag → lanza InvalidTag", False, str(e))

# Caso c: blob demasiado corto
try:
    crypto.desencriptar(b"\x00" * 10)
    prueba("Blob de 10 bytes → lanza ValueError", False, "No detectó longitud inválida")
except ValueError as e:
    prueba("Blob de 10 bytes → lanza ValueError", True, str(e))
except Exception as e:
    prueba("Blob de 10 bytes → lanza ValueError", False,
           f"Excepción inesperada: {type(e).__name__}: {e}")

# ═════════════════════════════════════════════════════════════════════════════
# PRUEBA 4 — None y vacíos se manejan sin errores
# ═════════════════════════════════════════════════════════════════════════════
seccion("4. None y vacíos se manejan sin errores")

# desencriptar(None)
try:
    r = crypto.desencriptar(None)
    prueba('desencriptar(None) no lanza excepción y devuelve ""', r == "")
except Exception as e:
    prueba('desencriptar(None) no lanza excepción', False, str(e))

# desencriptar(b"")
try:
    r = crypto.desencriptar(b"")
    prueba('desencriptar(b"") devuelve ""', r == "")
except Exception as e:
    prueba('desencriptar(b"") devuelve ""', False, str(e))

# desencriptar_campos con campo None
try:
    reg = {"nombre_completo": None, "cedula_id": b""}
    resultado = crypto.desencriptar_campos(reg, ["nombre_completo", "cedula_id"])
    prueba("desencriptar_campos con None/b'' no lanza excepción",
           resultado["nombre_completo"] is None and resultado["cedula_id"] == "")
except Exception as e:
    prueba("desencriptar_campos con None/b'' no lanza excepción", False, str(e))

# buscar_en_bloque con texto < 3 chars
try:
    r = crypto.buscar_en_bloque([], "nombre_completo", "ab")
    prueba("buscar_en_bloque con texto < 3 chars devuelve []", r == [])
except Exception as e:
    prueba("buscar_en_bloque con texto < 3 chars devuelve []", False, str(e))

# buscar_en_bloque con lista vacía
try:
    r = crypto.buscar_en_bloque([], "nombre_completo", "Juan")
    prueba("buscar_en_bloque con lista vacía devuelve []", r == [])
except Exception as e:
    prueba("buscar_en_bloque con lista vacía devuelve []", False, str(e))

# ═════════════════════════════════════════════════════════════════════════════
# PRUEBA 6 — buscar_en_bloque: coincidencias parciales y no retiene datos
# ═════════════════════════════════════════════════════════════════════════════
seccion("6. buscar_en_bloque — coincidencias parciales y limpieza de memoria")

nombres = [
    "JUAN CARLOS PÉREZ RODRÍGUEZ",
    "MARÍA ELENA SUÁREZ VARGAS",
    "CARLOS ANDRÉS MENDOZA",
    "JUANITA ALEXANDRA TORRES",
    "ROBERTO JUAN RÍOS",
    "ANA LUCÍA MORALES",
]

# Construir registros cifrados (simulando filas de BD)
registros_cifrados = [
    {
        "nro_hclinica": i + 1,
        "nombre_completo": crypto.encriptar(nombre),
        "cedula_id": crypto.encriptar(f"09{i:08d}"),
    }
    for i, nombre in enumerate(nombres)
]

# Búsqueda parcial: "JUAN" debe encontrar 3 registros
resultados = crypto.buscar_en_bloque(
    registros_cifrados,
    campo_busqueda="nombre_completo",
    texto="JUAN",
    campos_adicionales=["cedula_id"],
)
esperados = [n for n in nombres if "JUAN" in n.upper()]
encontrados = [r["nombre_completo"] for r in resultados]
ok_count = len(resultados) == len(esperados)
ok_names = sorted(encontrados) == sorted(esperados)
prueba(f"Búsqueda 'JUAN' → {len(esperados)} resultado(s) esperados",
       ok_count and ok_names,
       f"Esperados: {sorted(esperados)}\nEncontrados: {sorted(encontrados)}")

# Los resultados tienen campos en claro (para visualización)
campos_en_claro = all(
    isinstance(r["nombre_completo"], str) and isinstance(r["cedula_id"], str)
    for r in resultados
)
prueba("Resultados de buscar_en_bloque tienen campos en claro (str)", campos_en_claro)

# Los registros originales siguen cifrados (bytes intactos)
originales_cifrados = all(
    isinstance(r["nombre_completo"], bytes)
    for r in registros_cifrados
)
prueba("Registros originales siguen siendo bytes (no se modificaron)", originales_cifrados)

# Búsqueda case-insensitive: "juan" minúscula debe encontrar los mismos
resultados_lower = crypto.buscar_en_bloque(
    registros_cifrados, "nombre_completo", "juan"
)
prueba("Búsqueda 'juan' (minúscula) encuentra los mismos resultados que 'JUAN'",
       len(resultados_lower) == len(esperados))

# No retiene datos: forzar GC y verificar que resultados no quedan en el módulo
del resultados, resultados_lower
gc.collect()
# Verificar que el módulo crypto no tiene ningún atributo con datos en claro
datos_en_modulo = [
    attr for attr in dir(_crypto_mod)
    if not attr.startswith("_") and isinstance(getattr(_crypto_mod, attr, None), str)
    and any(n in getattr(_crypto_mod, attr, "") for n in nombres)
]
prueba("Módulo crypto no retiene datos en claro tras GC",
       len(datos_en_modulo) == 0,
       f"Variables con datos: {datos_en_modulo}" if datos_en_modulo else "")

# ═════════════════════════════════════════════════════════════════════════════
# RESUMEN FINAL
# ═════════════════════════════════════════════════════════════════════════════
print(f"\n{'═' * 60}")
total   = len(_resultados)
passed  = sum(1 for _, ok, _ in _resultados if ok)
failed  = total - passed
print(f"  RESULTADO: {passed}/{total} pruebas pasaron  "
      f"({'✓ TODAS OK' if failed == 0 else f'✗ {failed} FALLARON'})")
print(f"{'═' * 60}\n")

sys.exit(0 if failed == 0 else 1)
