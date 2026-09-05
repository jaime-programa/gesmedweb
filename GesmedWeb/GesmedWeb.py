import os
from pathlib import Path

_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    for _line in _env_path.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

import reflex as rx
from datetime import datetime
from starlette.requests import Request
from starlette.responses import StreamingResponse, Response
from .paginas.login import login_falso, el_login
from .paginas.atencion import index
from .paginas.lista_pacientes import muestra_pacientes
from .paginas.config_reportes import config_reportes
from .paginas.config_usuarios import config_usuarios
import unicodedata
from sqlalchemy import text
from sqlmodel import Session, select
from .state import State, ConfigReportesState, AdminUsuariosState, engine
from .modelos.mis_modelos import OtrosExamenesTipo, Imagenes, Atencion, ResultadosImagenes
from .utils.imagen_utils import leer_imagen as img_leer
from .reportes.motor import generar_reporte, generar_reporte_multisheet


def _slug_tipo(lk_tipo: int) -> str:
    if not lk_tipo:
        return ""
    with Session(engine) as s:
        tipo = s.exec(
            select(OtrosExamenesTipo).where(OtrosExamenesTipo.id_examen_tipo == lk_tipo)
        ).first()
    if not tipo:
        return ""
    nombre = tipo.examen_tipo.strip().lower().replace(" ", "_")
    return unicodedata.normalize("NFD", nombre).encode("ascii", "ignore").decode()


def _tipos_en_atencion(lk_atencion: int) -> list[tuple[int, str]]:
    """Devuelve [(id_tipo, nombre_tipo), ...] para los tipos presentes en el pedido."""
    with Session(engine) as s:
        rows = s.execute(text("""
            SELECT DISTINCT et.id_examen_tipo, et.examen_tipo
            FROM examen_pedido ep
            JOIN examen_catalogo ec ON ec.id_examen  = ep.lk_catalogo
            JOIN examen_tipo     et ON et.id_examen_tipo = ec.lk_examen_tipo
            WHERE ep.lk_atencion = :lk
            ORDER BY et.examen_tipo
        """), {"lk": lk_atencion}).all()
    return [(int(r[0]), str(r[1])) for r in rows]

styles = """
.data-table .small-font-column {
    font-size: 7px;
}
"""

app = rx.App(theme=rx.theme(appearance="light"))

# ── Endpoint de descarga de reportes ─────────────────────────────────────────
# GET /reporte/{nombre_reporte}?lk_paciente=X&lk_atencion=Y&lk_medico=Z
async def _descargar_reporte(request: Request) -> StreamingResponse:
    nombre_reporte = request.path_params["nombre_reporte"]
    contexto = {
        "lk_paciente": int(request.query_params.get("lk_paciente", 0)),
        "lk_atencion": int(request.query_params.get("lk_atencion", 0)),
        "lk_medico":   int(request.query_params.get("lk_medico",   0)),
        "lk_tipo":     int(request.query_params.get("lk_tipo",     0)),
    }
    fecha  = datetime.now().strftime("%y%m%d")
    nro_hc = contexto["lk_paciente"]

    # pedido_examen sin tipo específico → multisheet (una hoja por tipo presente)
    if nombre_reporte == "pedido_examen" and contexto["lk_tipo"] == 0:
        tipos = _tipos_en_atencion(contexto["lk_atencion"])
        if len(tipos) > 1:
            output, _ = generar_reporte_multisheet(nombre_reporte, contexto, tipos, engine)
        else:
            output = generar_reporte(nombre_reporte, contexto, engine)
    else:
        output = generar_reporte(nombre_reporte, contexto, engine)

    slug     = _slug_tipo(contexto["lk_tipo"])
    sufijo   = f"_{slug}" if slug else ""
    filename = f"{fecha}_{nro_hc:04d}_{nombre_reporte}{sufijo}.xlsx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )

app._api.add_route("/reporte/{nombre_reporte}", _descargar_reporte, methods=["GET"])

# ── Endpoint de imágenes médicas ──────────────────────────────────────────────
# GET /imagen/{id_imagen}
async def _servir_imagen(request: Request) -> Response:
    id_imagen = int(request.path_params["id_imagen"])
    with Session(engine) as session:
        img = session.get(Imagenes, id_imagen)
        if not img:
            return Response(status_code=404)
        nro_hclinica = None
        if img.lk_resultado_imagen:
            res = session.get(ResultadosImagenes, img.lk_resultado_imagen)
            if res:
                nro_hclinica = res.lk_paciente
        if not nro_hclinica and img.lk_atencion:
            at = session.get(Atencion, img.lk_atencion)
            if at:
                nro_hclinica = at.lk_paciente
    if not nro_hclinica:
        return Response(status_code=404)
    datos = img_leer(nro_hclinica, img.lk_atencion, id_imagen)
    if not datos:
        return Response(status_code=404)
    return Response(content=datos, media_type="image/jpeg")

app._api.add_route("/imagen/{id_imagen}", _servir_imagen, methods=["GET"])

# ── Páginas Reflex ────────────────────────────────────────────────────────────
app.add_page(el_login, '/')
app.add_page(muestra_pacientes, '/pacientes', on_load=State.carga_pacientes_filtrados)
app.add_page(index, "/atencion")
app.add_page(config_reportes, "/config/reportes",
             on_load=ConfigReportesState.cr_cargar_reportes)
app.add_page(config_usuarios, "/config/usuarios",
             on_load=AdminUsuariosState.au_cargar)
