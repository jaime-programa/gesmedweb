"""
Wrapper de PaddleOCR para extracción de texto en imágenes médicas.

El objeto _ocr es un singleton — se inicializa una vez al arranque
(opción B: precarga) y se reutiliza en todas las llamadas.

Uso en rxconfig.py:
    from GesmedWeb.utils.ocr_utils import inicializar_ocr
    inicializar_ocr()
"""
from __future__ import annotations
import io
from difflib import SequenceMatcher

_ocr = None


def inicializar_ocr() -> None:
    """Precarga los modelos de PaddleOCR en memoria. Llamar al arranque."""
    global _ocr
    if _ocr is not None:
        return
    try:
        from paddleocr import PaddleOCR
        _ocr = PaddleOCR(use_angle_cls=True, lang="es", show_log=False)
        print("[OCR] PaddleOCR listo.")
    except Exception as e:
        print(f"[OCR] No se pudo inicializar PaddleOCR: {e}")


def _asegurar_ocr() -> bool:
    """Inicializa OCR si aún no está listo. Devuelve True si está disponible."""
    if _ocr is None:
        inicializar_ocr()
    return _ocr is not None


# ── Extracción de texto ───────────────────────────────────────────────────────

def extraer_region(imagen_bytes: bytes, x1: int, y1: int, x2: int, y2: int) -> list[list[str]]:
    """
    Recorta la región (x1,y1)→(x2,y2) de la imagen y corre OCR.

    Devuelve lista de filas. Cada fila es una lista de strings (columnas
    detectadas por posición horizontal). Si la región parece una tabla simple
    (varias columnas), las palabras se agrupan por fila y columna.

    Formato de retorno:
        [["Glucosa", "95", "mg/dL", "70-110"],
         ["Hemoglobina", "14.2", "g/dL", "12-16"], ...]
    """
    if not _asegurar_ocr():
        return []

    from PIL import Image
    import numpy as np

    img = Image.open(io.BytesIO(imagen_bytes)).convert("RGB")
    recorte = img.crop((x1, y1, x2, y2))
    arr = np.array(recorte)

    resultado = _ocr.ocr(arr, cls=True)
    if not resultado or not resultado[0]:
        return []

    bloques = []
    for bloque in resultado[0]:
        coords  = bloque[0]            # [[x0,y0],[x1,y0],[x1,y1],[x0,y1]]
        texto   = bloque[1][0]
        x_cent  = (coords[0][0] + coords[1][0]) / 2
        y_cent  = (coords[0][1] + coords[2][1]) / 2
        bloques.append({"texto": texto, "x": x_cent, "y": y_cent})

    if not bloques:
        return []

    # Agrupa en filas por proximidad vertical (tolerancia = altura promedio * 0.5)
    alturas = [(b["y"]) for b in bloques]
    tolerancia = (max(alturas) - min(alturas)) / max(len(alturas), 1) * 0.6

    bloques.sort(key=lambda b: b["y"])
    filas: list[list[dict]] = []
    fila_actual: list[dict] = [bloques[0]]

    for b in bloques[1:]:
        if abs(b["y"] - fila_actual[-1]["y"]) <= tolerancia:
            fila_actual.append(b)
        else:
            filas.append(fila_actual)
            fila_actual = [b]
    filas.append(fila_actual)

    # Dentro de cada fila, ordena por x y devuelve los textos
    return [[c["texto"] for c in sorted(fila, key=lambda b: b["x"])] for fila in filas]


# ── Matching con catálogo ─────────────────────────────────────────────────────

def match_catalogo(nombre_ocr: str, catalogo: list[dict]) -> dict | None:
    """
    Busca el examen del catálogo más similar al nombre extraído por OCR.

    catalogo: lista de dicts con claves 'id_examen' y 'nombre_examen'.

    Devuelve el dict del examen con 'score' añadido, o None si el mejor
    score no supera 0.55 (umbral conservador para nombres médicos cortos).
    """
    mejor      = None
    mejor_score = 0.0
    nombre_low  = nombre_ocr.strip().lower()

    for examen in catalogo:
        score = SequenceMatcher(None, nombre_low, examen["nombre_examen"].lower()).ratio()
        if score > mejor_score:
            mejor_score = score
            mejor       = examen

    if mejor and mejor_score >= 0.55:
        return {**mejor, "score": round(mejor_score, 2)}
    return None
