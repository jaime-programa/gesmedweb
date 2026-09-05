"""
Utilidades para manejo de archivos de imagen del módulo de resultados.

Convención de nombre de archivo:
    {nro_hclinica}-{lk_atencion}-{id_imagen}.jpg
    almacenado en la ruta configurada en configuracion.txt → IMAGENES_OK
"""
import io
import pathlib
from .config import ruta_imagenes


# ── Nombres y rutas ───────────────────────────────────────────────────────────

def nombre_archivo(nro_hclinica: int, lk_atencion: int, id_imagen: int) -> str:
    return f"{nro_hclinica}-{lk_atencion}-{id_imagen}.jpg"


def ruta_completa(nro_hclinica: int, lk_atencion: int, id_imagen: int) -> pathlib.Path:
    return ruta_imagenes() / nombre_archivo(nro_hclinica, lk_atencion, id_imagen)


# ── Conversión PDF → JPG ──────────────────────────────────────────────────────

def pdf_a_jpg(pdf_bytes: bytes, dpi: int = 150) -> list[bytes]:
    """
    Convierte cada página de un PDF a JPG.
    Devuelve lista de bytes (uno por página), en orden.
    Requiere PyMuPDF (pip install pymupdf).
    """
    import pymupdf as fitz
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    paginas: list[bytes] = []
    escala = dpi / 72
    mat = fitz.Matrix(escala, escala)
    for pagina in doc:
        pix = pagina.get_pixmap(matrix=mat, alpha=False)
        paginas.append(pix.tobytes("jpeg"))
    doc.close()
    return paginas


def normalizar_a_jpg(imagen_bytes: bytes, mime_type: str) -> bytes:
    """
    Acepta JPG o PNG y devuelve bytes en formato JPG.
    Para PDF usa pdf_a_jpg y devuelve solo la primera página.
    """
    from PIL import Image
    if mime_type == "application/pdf":
        paginas = pdf_a_jpg(imagen_bytes)
        return paginas[0] if paginas else b""
    img = Image.open(io.BytesIO(imagen_bytes)).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


# ── Persistencia en disco ─────────────────────────────────────────────────────

def guardar_imagen(datos: bytes, nro_hclinica: int, lk_atencion: int, id_imagen: int) -> pathlib.Path:
    ruta = ruta_completa(nro_hclinica, lk_atencion, id_imagen)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_bytes(datos)
    return ruta


def eliminar_imagen(nro_hclinica: int, lk_atencion: int, id_imagen: int) -> None:
    ruta = ruta_completa(nro_hclinica, lk_atencion, id_imagen)
    if ruta.exists():
        ruta.unlink()


def leer_imagen(nro_hclinica: int, lk_atencion: int, id_imagen: int) -> bytes | None:
    ruta = ruta_completa(nro_hclinica, lk_atencion, id_imagen)
    return ruta.read_bytes() if ruta.exists() else None


# ── Manipulación de imagen ────────────────────────────────────────────────────

def rotar_imagen_bytes(imagen_bytes: bytes, grados: int) -> bytes:
    """Rota en memoria sin tocar el archivo en disco. Usado para preview."""
    from PIL import Image
    img = Image.open(io.BytesIO(imagen_bytes)).convert("RGB")
    # PIL rota en sentido antihorario; los grados del modelo son sentido horario
    rotada = img.rotate(-grados, expand=True)
    buf = io.BytesIO()
    rotada.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def recortar_imagen(nro_hclinica: int, lk_atencion: int, id_imagen: int,
                    x1: int, y1: int, x2: int, y2: int) -> bytes:
    """Recorta la región indicada del archivo en disco. Devuelve bytes JPG."""
    from PIL import Image
    datos = leer_imagen(nro_hclinica, lk_atencion, id_imagen)
    if not datos:
        return b""
    img = Image.open(io.BytesIO(datos)).convert("RGB")
    recorte = img.crop((x1, y1, x2, y2))
    buf = io.BytesIO()
    recorte.save(buf, format="JPEG", quality=85)
    return buf.getvalue()
