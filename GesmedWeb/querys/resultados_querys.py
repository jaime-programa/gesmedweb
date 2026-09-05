"""
Queries del módulo de resultados de exámenes.
"""
from __future__ import annotations
import datetime
from sqlmodel import Session, select
from reflex.config import get_config as _rx_get_config

_BACKEND = _rx_get_config().api_url.rstrip("/")

from ..modelos.mis_modelos import (
    ResultadosImagenes,
    ResultadosLaboratorio,
    Imagenes,
    Marcas,
    OtrosExamenesCatalogo,
    Atencion,
    OtrosExamenesCatalogo,
    ExamenesLaboratorioCatalogo,
    ExamenesLaboratorioGrupo,
    Paciente,
    ListaSignosVitales,
    SignosVitales,
)


# ── resultados_imagen ───────────────────���─────────────────────────────────────

def cargar_resultados_imagen_paciente(session: Session, nro_hclinica: int) -> list[dict]:
    """
    Devuelve todos los resultados de imagen del paciente, con nombre del examen.
    Ordenados por fecha descendente.
    """
    stmt = (
        select(ResultadosImagenes, OtrosExamenesCatalogo.examen_nombre)
        .outerjoin(OtrosExamenesCatalogo,
                   OtrosExamenesCatalogo.id_examen == ResultadosImagenes.lk_examen)
        .where(ResultadosImagenes.lk_paciente == nro_hclinica)
        .order_by(ResultadosImagenes.fecha_imagen.desc())
    )
    filas = session.exec(stmt).all()
    return [
        {
            "id_resultado":    r.id_resultado,
            "fecha_imagen":    r.fecha_imagen.strftime("%d/%m/%Y"),
            "nombre_examen":   nombre or "Sin tipo",
            "lk_examen":       r.lk_examen,
            "alias":           r.alias or "",
            "hallazgos":       r.hallazgos or "",
        }
        for r, nombre in filas
    ]


def eliminar_resultado_imagen(session: Session, id_resultado: int) -> list[dict]:
    """
    Elimina el resultado y todas sus imágenes (marcas incluidas).
    Devuelve lista de dicts {id_imagen, lk_atencion, nro_hclinica} para el
    borrado posterior de los archivos físicos.
    """
    resultado = session.get(ResultadosImagenes, id_resultado)
    if not resultado:
        return []
    nro_hclinica = resultado.lk_paciente
    imagenes = session.exec(
        select(Imagenes).where(Imagenes.lk_resultado_imagen == id_resultado)
    ).all()
    datos_fisicos = []
    for img in imagenes:
        datos_fisicos.append({
            "id_imagen":    img.id_imagen,
            "lk_atencion":  img.lk_atencion,
            "nro_hclinica": nro_hclinica,
        })
        for m in session.exec(select(Marcas).where(Marcas.lk_imagen == img.id_imagen)).all():
            session.delete(m)
        session.delete(img)
    session.delete(resultado)
    session.commit()
    return datos_fisicos


def crear_resultado_imagen(session: Session, nro_hclinica: int,
                           lk_examen: int | None, fecha: datetime.date | None = None,
                           alias: str | None = None,
                           hallazgos: str | None = None) -> int:
    nuevo = ResultadosImagenes(
        fecha_imagen  = fecha or datetime.date.today(),
        lk_paciente   = nro_hclinica,
        lk_examen     = lk_examen,
        alias         = alias or None,
        hallazgos     = hallazgos or None,
    )
    session.add(nuevo)
    session.commit()
    session.refresh(nuevo)
    return nuevo.id_resultado


# ── imagen ───────────────────��────────────────────────────────────────────────

def cargar_imagenes_resultado(session: Session, id_resultado: int) -> list[dict]:
    """Imágenes de un resultado ordenadas por campo orden."""
    stmt = (
        select(Imagenes)
        .where(Imagenes.lk_resultado_imagen == id_resultado)
        .order_by(Imagenes.orden)
    )
    return [
        {
            "id_imagen":   img.id_imagen,
            "src_imagen":  f"{_BACKEND}/imagen/{img.id_imagen}",
            "rotacion_css": f"rotate({img.rotacion}deg)",
            "orden":       img.orden,
            "rotacion":    img.rotacion,
            "ubicacion":   img.ubicacion or "",
            "detalle":     img.detalle   or "",
            "lk_atencion": img.lk_atencion,
        }
        for img in session.exec(stmt).all()
    ]


def cargar_imagenes_sin_clasificar(session: Session, lk_atencion: int) -> list[dict]:
    """Imágenes subidas en esta atención que aún no tienen resultado asignado."""
    stmt = (
        select(Imagenes)
        .where(
            Imagenes.lk_atencion         == lk_atencion,
            Imagenes.lk_resultado_imagen == None,
        )
        .order_by(Imagenes.id_imagen)
    )
    return [
        {
            "id_imagen":   img.id_imagen,
            "src_imagen":  f"{_BACKEND}/imagen/{img.id_imagen}",
            "rotacion_css": f"rotate({img.rotacion}deg)",
            "rotacion":    img.rotacion,
            "ubicacion":   img.ubicacion or "",
            "detalle":     img.detalle   or "",
        }
        for img in session.exec(stmt).all()
    ]


def insertar_imagen(session: Session, lk_atencion: int,
                    id_resultado: int | None = None, orden: int = 0) -> int:
    img = Imagenes(
        lk_resultado_imagen = id_resultado,
        lk_atencion         = lk_atencion,
        orden               = orden,
    )
    session.add(img)
    session.commit()
    session.refresh(img)
    return img.id_imagen


def asignar_imagen_a_resultado(session: Session, id_imagen: int,
                                id_resultado: int, orden: int) -> None:
    img = session.get(Imagenes, id_imagen)
    if img:
        img.lk_resultado_imagen = id_resultado
        img.orden               = orden
        session.add(img)
        session.commit()


def actualizar_rotacion(session: Session, id_imagen: int, rotacion: int) -> None:
    img = session.get(Imagenes, id_imagen)
    if img:
        img.rotacion = rotacion % 360
        session.add(img)
        session.commit()


def reordenar_imagenes(session: Session, id_resultado: int, ids_ordenados: list[int]) -> None:
    """Recibe la lista de id_imagen en el nuevo orden y actualiza el campo orden."""
    for nuevo_orden, id_imagen in enumerate(ids_ordenados):
        img = session.get(Imagenes, id_imagen)
        if img and img.lk_resultado_imagen == id_resultado:
            img.orden = nuevo_orden
            session.add(img)
    session.commit()


def eliminar_imagen(session: Session, id_imagen: int) -> dict | None:
    """Devuelve los datos necesarios para borrar el archivo físico."""
    img = session.get(Imagenes, id_imagen)
    if not img:
        return None
    resultado = session.get(ResultadosImagenes, img.lk_resultado_imagen) if img.lk_resultado_imagen else None
    nro_hclinica = resultado.lk_paciente if resultado else None
    datos = {
        "id_imagen":     img.id_imagen,
        "lk_atencion":   img.lk_atencion,
        "nro_hclinica":  nro_hclinica,
    }
    session.delete(img)
    session.commit()
    return datos


# ── marcas ────────────────────────────────────────────────────────────────────

def cargar_marcas(session: Session, id_imagen: int) -> list[dict]:
    stmt = select(Marcas).where(Marcas.lk_imagen == id_imagen).order_by(Marcas.nivel)
    return [
        {
            "id_marca":    m.id_marca,
            "tipo_marca":  m.tipo_marca,
            "x_centro":    m.x_centro,
            "y_centro":    m.y_centro,
            "radio":       m.radio,
            "x2":          m.x2,
            "y2":          m.y2,
            "grosor":      m.grosor,
            "font":        m.font,
            "color":       m.color or "#ff0000",
            "nivel":       m.nivel,
            "observacion": m.observacion or "",
        }
        for m in session.exec(stmt).all()
    ]


def guardar_marca(session: Session, id_imagen: int, tipo: str,
                  x: int, y: int, radio: int,
                  x2: int, y2: int, grosor: int,
                  color: str, font: int, nivel: int, observacion: str) -> int:
    marca = Marcas(
        lk_imagen   = id_imagen,
        tipo_marca  = tipo,
        x_centro    = x,
        y_centro    = y,
        radio       = radio,
        x2          = x2,
        y2          = y2,
        grosor      = grosor,
        color       = color,
        font        = font,
        nivel       = nivel,
        observacion = observacion,
    )
    session.add(marca)
    session.commit()
    session.refresh(marca)
    return marca.id_marca


def eliminar_marca(session: Session, id_marca: int) -> None:
    m = session.get(Marcas, id_marca)
    if m:
        session.delete(m)
        session.commit()


def actualizar_marca(session: Session, id_marca: int,
                     color: str, font: int, observacion: str) -> None:
    m = session.get(Marcas, id_marca)
    if m:
        m.color       = color
        m.font        = font
        m.observacion = observacion
        session.add(m)
        session.commit()


# ── catálogo de tipos de examen imagen ───────────────────────────────────────

def cargar_catalogo_examenes_imagen(session: Session) -> list[dict]:
    """Tipos de examen de imagen para el select 'crear nuevo resultado'."""
    return [
        {"id_examen": e.id_examen, "nombre_examen": e.examen_nombre}
        for e in session.exec(
            select(OtrosExamenesCatalogo).order_by(OtrosExamenesCatalogo.examen_nombre)
        ).all()
    ]


def nro_hclinica_de_imagen(session: Session, id_imagen: int) -> int | None:
    """Obtiene nro_hclinica a partir del id_imagen (vía atencion o resultado)."""
    img = session.get(Imagenes, id_imagen)
    if not img:
        return None
    if img.lk_resultado_imagen:
        res = session.get(ResultadosImagenes, img.lk_resultado_imagen)
        if res and res.lk_paciente:
            return res.lk_paciente
    if img.lk_atencion:
        at = session.get(Atencion, img.lk_atencion)
        if at:
            return at.lk_paciente
    return None


# ── resultados_laboratorio ──────────────────────────���─────────────────────────

def cargar_catalogo_lab(session: Session) -> list[dict]:
    """Catálogo completo para el matching fuzzy en OCR."""
    return [
        {"id_examen": e.id_examen, "nombre_examen": e.nombre_examen}
        for e in session.exec(select(ExamenesLaboratorioCatalogo)).all()
    ]


def cargar_catalogo_completo_lab(session: Session) -> list[dict]:
    """Catálogo completo de exámenes con su grupo, para el combobox de laboratorio."""
    stmt = (
        select(ExamenesLaboratorioCatalogo, ExamenesLaboratorioGrupo.nombre_grupo)
        .outerjoin(
            ExamenesLaboratorioGrupo,
            ExamenesLaboratorioGrupo.id_grupo == ExamenesLaboratorioCatalogo.lk_grupo,
        )
        .where(ExamenesLaboratorioCatalogo.activo == 1)
        .order_by(ExamenesLaboratorioCatalogo.nombre_examen)
    )
    return [
        {
            "id_examen": str(e.id_examen),
            "display":   f"{e.nombre_examen} — {nombre_grupo or 'Sin grupo'}",
        }
        for e, nombre_grupo in session.exec(stmt).all()
    ]


def cargar_historial_lab(session: Session, nro_hclinica: int) -> list[dict]:
    """Flat tree-table rows (tipo G/E/R) para el tab de laboratorio."""
    stmt = (
        select(
            ResultadosLaboratorio,
            ExamenesLaboratorioCatalogo.nombre_examen,
            ExamenesLaboratorioCatalogo.unidad,
            ExamenesLaboratorioGrupo.id_grupo,
            ExamenesLaboratorioGrupo.nombre_grupo,
        )
        .outerjoin(ExamenesLaboratorioCatalogo,
                   ExamenesLaboratorioCatalogo.id_examen == ResultadosLaboratorio.lk_examen)
        .outerjoin(ExamenesLaboratorioGrupo,
                   ExamenesLaboratorioGrupo.id_grupo == ExamenesLaboratorioCatalogo.lk_grupo)
        .where(ResultadosLaboratorio.lk_paciente == nro_hclinica)
        .order_by(
            ExamenesLaboratorioGrupo.nombre_grupo,
            ExamenesLaboratorioCatalogo.nombre_examen,
            ResultadosLaboratorio.fecha_examen.desc(),
        )
    )
    rows = session.exec(stmt).all()

    grupos_orden: list[tuple] = []
    examenes_orden: dict[tuple, list[tuple]] = {}
    unidades: dict[tuple, str] = {}
    resultados_map: dict[tuple, list[dict]] = {}

    for rl, nombre_examen, unidad, id_grupo, nombre_grupo in rows:
        gk = (id_grupo or 0, nombre_grupo or "Sin grupo")
        ek = (gk, rl.lk_examen or 0, nombre_examen or "Sin nombre")

        if gk not in examenes_orden:
            grupos_orden.append(gk)
            examenes_orden[gk] = []
        if ek not in examenes_orden[gk]:
            examenes_orden[gk].append(ek)
            unidades[ek] = unidad or ""

        resultados_map.setdefault(ek, []).append({
            "fecha":    rl.fecha_examen.strftime("%d/%m/%Y"),
            "valor":    str(rl.valor_numerico) if rl.valor_numerico is not None else "—",
            "en_rango": rl.en_rango or "EN_RANGO",
        })

    flat: list[dict] = []
    _base = {"fecha": "", "valor": "", "unidad": "", "en_rango": "", "expandido": False}
    for gi, gk in enumerate(grupos_orden):
        gkey = f"g{gi}"
        flat.append({**_base, "tipo": "G", "gkey": gkey, "ekey": "", "nombre": gk[1], "visible": True})
        for ei, ek in enumerate(examenes_orden[gk]):
            ekey = f"e{gi}_{ei}"
            flat.append({**_base, "tipo": "E", "gkey": gkey, "ekey": ekey, "nombre": ek[2],
                         "unidad": unidades[ek], "visible": False})
            for r in resultados_map[ek]:
                flat.append({**_base, "tipo": "R", "gkey": gkey, "ekey": ekey, "nombre": "",
                             "fecha": r["fecha"], "valor": r["valor"],
                             "unidad": unidades[ek], "en_rango": r["en_rango"], "visible": False})
    return flat


def cargar_historial_sv(session: Session, nro_hclinica: int) -> list[dict]:
    """Flat tree-table rows (tipo E/R) para signos vitales del paciente."""
    stmt = (
        select(
            SignosVitales.valor,
            ListaSignosVitales.id_signo_vital,
            ListaSignosVitales.nombre,
            ListaSignosVitales.unidad,
            ListaSignosVitales.orden_display,
            Atencion.fecha_atencion,
        )
        .join(ListaSignosVitales,
              ListaSignosVitales.id_signo_vital == SignosVitales.lk_signo_vital)
        .join(Atencion, Atencion.id_atencion == SignosVitales.lk_atencion)
        .where(Atencion.lk_paciente == nro_hclinica)
        .order_by(ListaSignosVitales.orden_display, Atencion.fecha_atencion.desc())
    )
    rows = session.exec(stmt).all()

    sv_orden: list[tuple] = []
    sv_meta: dict[tuple, dict] = {}
    lecturas: dict[tuple, list[dict]] = {}

    for valor, id_sv, nombre, unidad, orden, fecha_at in rows:
        sk = (orden or 99, id_sv or 0, nombre or "")
        if sk not in sv_meta:
            sv_orden.append(sk)
            sv_meta[sk] = {"nombre": nombre or "", "unidad": unidad or ""}
            lecturas[sk] = []
        lecturas[sk].append({
            "fecha": fecha_at.strftime("%d/%m/%Y") if fecha_at else "—",
            "valor": str(valor) if valor is not None else "—",
        })

    flat: list[dict] = []
    _base = {"nombre": "", "fecha": "", "valor": "", "unidad": "", "expandido": False}
    for i, sk in enumerate(sv_orden):
        svkey = f"sv{i}"
        meta = sv_meta[sk]
        flat.append({**_base, "tipo": "E", "svkey": svkey, "nombre": meta["nombre"],
                     "unidad": meta["unidad"], "visible": True})
        for lec in lecturas[sk]:
            flat.append({**_base, "tipo": "R", "svkey": svkey,
                         "fecha": lec["fecha"], "valor": lec["valor"], "visible": False})
    return flat


def guardar_resultado_lab(session: Session, nro_hclinica: int,
                          lk_examen: int | None, fecha: datetime.date,
                          valor_numerico: float | None, valor_texto: str | None,
                          en_rango: str | None, observacion: str | None,
                          lk_imagen_fuente: int | None,
                          lk_pedido: int | None = None) -> int:
    r = ResultadosLaboratorio(
        fecha_examen      = fecha,
        lk_paciente       = nro_hclinica,
        lk_examen         = lk_examen,
        lk_pedido         = lk_pedido,
        lk_imagen_fuente  = lk_imagen_fuente,
        valor_numerico    = valor_numerico,
        valor_texto       = valor_texto,
        en_rango          = en_rango,
        observacion       = observacion,
    )
    session.add(r)
    session.commit()
    session.refresh(r)
    return r.id_resultado
