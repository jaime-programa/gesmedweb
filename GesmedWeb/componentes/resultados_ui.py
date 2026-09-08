"""
UI del módulo de resultados e imágenes médicas.

Estructura:
  offcanvas_resultados()
    ├── Panel izquierdo (340px): árbol + upload
    │     ├── Rama "Sin clasificar"
    │     └── Ramas por resultados_imagen
    └── Panel derecho: análisis de imagen (Fase 3 — placeholder)
"""
import reflex as rx
from ..state import ResultadosState, LaboratorioState, State

# ── Constantes visuales ───────────────────────────────────────────────────────

_THUMB_SIZE  = "60px"
_HEADER_BG   = "var(--blue-9)"
_HEADER_COLOR= "white"
_RAMA_BG     = "var(--gray-2)"
_BORDER      = "1px solid var(--gray-4)"
_BTN_GHOST   = {"variant": "ghost", "size": "1", "type": "button", "cursor": "pointer"}
_FOCO        = "#0A2CD7"  

# ── Miniaturas ────────────────────────────────────────────────────────────────

_BORDER_FOCO = f"2px solid {_FOCO}"

def _thumb(src, rotacion_css="rotate(0deg)", on_click=None, activa=False) -> rx.Component:
    """Miniatura de imagen. src y rotacion_css deben ser strings ya resueltos (no Vars de int)."""
    return rx.image(
        src=src,
        width=_THUMB_SIZE,
        height=_THUMB_SIZE,
        object_fit="cover",
        border_radius="4px",
        flex_shrink="0",
        style={"transform": rotacion_css, "transition": "transform 0.2s"},
        border=rx.cond(activa, _BORDER_FOCO, _BORDER),
        on_click=on_click,
        cursor="pointer" if on_click is not None else "default",
    )


def _tarjeta_sin_clasificar(img: dict) -> rx.Component:
    return rx.hstack(
        _thumb(img["src_imagen"], img["rotacion_css"],
               on_click=ResultadosState.ri_seleccionar_imagen(img["id_imagen"], 0)),
        rx.vstack(
            rx.text(rx.cond(img["detalle"], img["detalle"], "Sin detalle"), font_size="11px", no_of_lines=2),
            rx.hstack(
                rx.button(
                    "Asignar →",
                    on_click=ResultadosState.ri_abrir_asignar(img["id_imagen"]),
                    size="1", variant="soft", color_scheme="blue", type="button",
                    font_size="10px",
                ),
                rx.button(
                    rx.icon("trash-2", size=12),
                    on_click=ResultadosState.ri_eliminar(img["id_imagen"]),
                    **_BTN_GHOST, color="var(--red-9)",
                ),
                spacing="1",
            ),
            spacing="1", align="start",
        ),
        padding="4px 6px",
        border_bottom=_BORDER,
        width="100%",
        align="start",
        spacing="2",
    )


def _tarjeta_imagen(resultado_id: int, img: dict) -> rx.Component:
    """Miniatura dentro de una rama clasificada con controles de orden y análisis."""
    return rx.hstack(
        _thumb(
            img["src_imagen"], img["rotacion_css"],
            on_click=ResultadosState.ri_seleccionar_imagen(img["id_imagen"], resultado_id),
            activa=ResultadosState.ri_id_imagen_activa == img["id_imagen"],
        ),
        rx.vstack(
            rx.text(rx.cond(img["detalle"], img["detalle"], ""), font_size="10px", no_of_lines=1, color="var(--gray-11)"),
            rx.hstack(
                rx.button(
                    rx.icon("arrow-up", size=15),
                    on_click=ResultadosState.ri_subir_imagen(resultado_id, img["id_imagen"]),
                    **_BTN_GHOST,
                ),
                rx.button(
                    rx.icon("arrow-down", size=15),
                    on_click=ResultadosState.ri_bajar_imagen(resultado_id, img["id_imagen"]),
                    **_BTN_GHOST,
                ),
                rx.button(
                    rx.icon("scan-search", size=15),
                    on_click=ResultadosState.ri_seleccionar_imagen(img["id_imagen"], resultado_id),
                    **_BTN_GHOST, color="var(--blue-9)",
                    title="Ver imagen",
                ),
                rx.button(
                    rx.text("- - -", font_size="12px"),
                    **_BTN_GHOST, color="var(--blue-9)",
                ),
                rx.button(
                    rx.icon("trash-2", size=15),
                    on_click=ResultadosState.ri_eliminar(img["id_imagen"]),
                    **_BTN_GHOST, color="var(--red-9)",
                ),
                spacing="1",
            ),
            spacing="1", align="start",
        ),
        padding="3px 6px",
        border_bottom=_BORDER,
        width="100%",
        align="start",
        spacing="2",
    )


# ── Ramas del árbol ────────────────────────────────────────────────────────────

def _encabezado_rama(resultado: dict) -> rx.Component:
    """Cabecera de una rama: área clickeable (toggle) + botón borrar + botón grabar."""
    es_abierta   = ResultadosState.ri_rama_abierta == resultado["id_resultado"]
    es_este_rama = ResultadosState.ri_grabar_rama_id == resultado["id_resultado"]
    return rx.hstack(
        # Área de toggle: chevron + alias (1ª línea) + nombre—fecha (2ª línea)
        rx.hstack(
            rx.icon(
                rx.cond(es_abierta, "chevron-down", "chevron-right"),
                size=14, color=_HEADER_COLOR, flex_shrink="0",
            ),
            rx.vstack(
                rx.text(
                    resultado["alias"],
                    font_size="11px", font_weight="700", color=_HEADER_COLOR,
                    no_of_lines=1,
                ),
                rx.text(
                    resultado["nombre_examen"], " — ", resultado["fecha_imagen"],
                    font_size="9px", font_weight="400",
                    color="rgba(255,255,255,0.70)",
                    no_of_lines=1,
                ),
                spacing="0", align="start",
            ),
            on_click=ResultadosState.ri_toggle_rama(resultado["id_resultado"]),
            cursor="pointer",
            flex="1",
            spacing="1",
            align="center",
            overflow="hidden",
        ),
        # Mensaje de estado del último grabar (solo para esta rama)
        rx.cond(
            es_este_rama & (ResultadosState.ri_grabar_msg != ""),
            rx.text(
                ResultadosState.ri_grabar_msg,
                font_size="9px", color="var(--yellow-3)",
                no_of_lines=1,
            ),
        ),
        # Botón borrar — separado del save con padding derecho extra
        rx.button(
            rx.icon("trash-2", size=12),
            on_click=ResultadosState.ri_abrir_borrar_resultado(resultado["id_resultado"]),
            variant="ghost", size="1", type="button", cursor="pointer",
            title="Eliminar este resultado y todas sus imágenes",
            color="var(--red-9)",
            padding_right="10px",
        ),
        # Botón grabar — no propaga al toggle
        rx.button(
            rx.icon("save", size=12),
            on_click=ResultadosState.ri_grabar_imagenes_rama(resultado["id_resultado"]),
            variant="ghost", size="1", type="button", cursor="pointer",
            title="Grabar imágenes de esta rama en disco",
            color="var(--yellow-3)",
        ),
        background=_HEADER_BG,
        padding="4px 8px",
        width="100%",
        align="center",
        border_radius="4px 4px 0 0",
        spacing="2",
    )


def _rama_resultado(resultado: dict) -> rx.Component:
    es_abierta = ResultadosState.ri_rama_abierta == resultado["id_resultado"]
    return rx.box(
        _encabezado_rama(resultado),
        rx.cond(
            es_abierta,
            rx.vstack(
                rx.foreach(
                    ResultadosState.ri_imagenes_rama,
                    lambda img: _tarjeta_imagen(resultado["id_resultado"], img),
                ),
                spacing="0", width="100%",
            ),
        ),
        border=_BORDER,
        border_radius="4px",
        overflow="hidden",
        width="100%",
        margin_bottom="4px",
    )


# ── Panel árbol ───────────────────────────────────────────────────────────────

def _panel_arbol() -> rx.Component:
    return rx.vstack(
        # ── Sin clasificar (visible solo cuando hay imágenes pendientes) ──────
        rx.cond(
            ResultadosState.ri_hay_sin_clasificar,
            rx.box(
                rx.hstack(
                    rx.icon("image", size=13, color=_HEADER_COLOR),
                    rx.text("Sin clasificar", font_size="11px", font_weight="600", color=_HEADER_COLOR),
                    rx.badge(
                        ResultadosState.ri_sin_clasificar.length(),
                        color_scheme="orange", variant="solid", size="1",
                    ),
                    spacing="1", align="center",
                    background=_HEADER_BG, padding="4px 8px", width="100%", border_radius="4px 4px 0 0",
                ),
                rx.vstack(
                    rx.foreach(ResultadosState.ri_sin_clasificar, _tarjeta_sin_clasificar),
                    spacing="0", width="100%",
                ),
                border=_BORDER,
                border_radius="4px",
                overflow="hidden",
                margin_bottom="6px",
            ),
        ),
        # ── Ramas por resultado ─────────────────────────────────────────────
        rx.foreach(ResultadosState.ri_resultados, _rama_resultado),
        width="340px",
        flex_shrink="0",
        height="100%",
        overflow_y="auto",
        padding="8px",
        background="var(--gray-1)",
        border_right=_BORDER,
        spacing="0",
        align="start",
    )


# ── Diálogo: asignar imagen a resultado ──────────────────────────────────────

def _dialogo_asignar() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Asignar imagen a resultado"),
            rx.vstack(
                rx.cond(
                    ~ResultadosState.ri_show_crear,
                    rx.vstack(
                        rx.text("Seleccione el resultado al que pertenece esta imagen:",
                                font_size="12px"),
                        rx.select.root(
                            rx.select.trigger(placeholder="Seleccionar resultado..."),
                            rx.select.content(
                                rx.foreach(
                                    ResultadosState.ri_opciones_res,
                                    lambda opt: rx.select.item(opt["label"], value=opt["id"]),
                                ),
                            ),
                            value=ResultadosState.ri_opcion_sel,
                            on_change=ResultadosState.ri_set_opcion,
                            width="100%",
                        ),
                        width="100%", spacing="2",
                    ),
                ),
                # ── Sub-form: crear nuevo resultado ─────────────────────────
                rx.cond(
                    ResultadosState.ri_show_crear,
                    rx.vstack(
                        rx.separator(width="100%"),
                        rx.text("Nuevo resultado — datos", font_size="11px", font_weight="600"),
                        rx.select.root(
                            rx.select.trigger(placeholder="Tipo de examen..."),
                            rx.select.content(
                                rx.foreach(
                                    ResultadosState.ri_catalogo_nombres,
                                    lambda n: rx.select.item(n, value=n),
                                ),
                            ),
                            value=ResultadosState.ri_crear_examen,
                            on_change=ResultadosState.set_ri_crear_examen,
                            width="100%",
                        ),
                        rx.input(
                            placeholder="Fecha de ejecución del exámen (YYYY-MM-DD)",
                            value=ResultadosState.ri_crear_fecha,
                            on_change=ResultadosState.set_ri_crear_fecha,
                            type="date",
                            font_size="12px",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.text("Cómo identificar este exámen *",
                                    font_size="11px", font_weight="600"),
                            rx.input(
                                placeholder="Ej: Rx de Torax",
                                value=ResultadosState.ri_crear_alias,
                                on_change=ResultadosState.set_ri_crear_alias,
                                max_length=80,
                                font_size="12px",
                                width="100%",
                            ),
                            spacing="1", width="100%",
                        ),
                        rx.vstack(
                            rx.text("Hallazgos de Exámen",
                                    font_size="11px", font_weight="600"),
                            rx.text_area(
                                placeholder="Descripción de hallazgos (opcional)...",
                                value=ResultadosState.ri_crear_hallazgos,
                                on_change=ResultadosState.set_ri_crear_hallazgos,
                                rows="3",
                                font_size="12px",
                                width="100%",
                            ),
                            spacing="1", width="100%",
                        ),
                        width="100%", spacing="2",
                    ),
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray",
                                  type="button", size="2"),
                    ),
                    rx.cond(
                        ResultadosState.ri_show_crear,
                        rx.button(
                            "Crear y asignar",
                            on_click=ResultadosState.ri_crear_y_asignar,
                            color_scheme="blue", type="button", size="2",
                        ),
                        rx.button(
                            "Asignar",
                            on_click=ResultadosState.ri_confirmar_asignar,
                            color_scheme="blue", type="button", size="2",
                            disabled=ResultadosState.ri_opcion_sel == "",
                        ),
                    ),
                    justify="end", spacing="2", width="100%",
                ),
                width="100%", spacing="3",
            ),
            max_width="440px",
        ),
        open=ResultadosState.ri_show_asignar,
        on_open_change=ResultadosState.set_ri_show_asignar,
    )


# ── Panel derecho — placeholder Fase 3 ───────────────────────────────────────

def _panel_analisis() -> rx.Component:
    return rx.box(
        rx.cond(
            ResultadosState.ri_id_imagen_activa > 0,
            rx.box(
                rx.image(
                    src=ResultadosState.ri_src_activa,
                    width="100%",
                    height="100%",
                    object_fit="contain",
                    display="block",
                    border_radius="4px",
                    style={
                        "transform": ResultadosState.ri_transform_activa,
                        "transition": "transform 0.3s ease",
                        "transform-origin": "center center",
                    },
                ),
                # Canvas overlay: marks_tool.js gestiona su contenido
                rx.el.canvas(
                    id="ri-marks-canvas",
                    style={
                        "position": "absolute", "top": "0", "left": "0",
                        "pointer-events": "none",
                    },
                ),
                # Bridge JS → Reflex: input oculto (fiber trick) + botón de disparo
                rx.el.input(
                    type="text",
                    default_value="",
                    on_change=ResultadosState.set_ri_nv_payload,
                    style={"display": "none"},
                    custom_attrs={"data-ri-marca-payload": "true"},
                ),
                rx.button(
                    on_click=ResultadosState.ri_recibir_marca,
                    display="none",
                    type="button",
                    custom_attrs={"data-ri-marca-submit": "true"},
                ),
                id="ri-img-inner",
                custom_attrs={
                    "data-image-id":  ResultadosState.ri_id_imagen_activa,
                    "data-ri-marcas": ResultadosState.ri_marcas_json,
                    "data-rotation":  ResultadosState.ri_rotacion_grados,
                },
                position="absolute",
                top="0",
                left="0",
                width="100%",
                height="100%",
            ),
            rx.vstack(
                rx.icon("image", size=40, color="var(--gray-6)"),
                rx.text("Seleccione una imagen del panel izquierdo",
                        font_size="12px", color="var(--gray-9)", text_align="center"),
                align="center", spacing="2",
            ),
        ),
        # ── Botón toggle panel árbol ─────────────────────────────────────────
        rx.button(
            rx.cond(
                ResultadosState.ri_show_arbol,
                rx.icon("panel-left-close", size=14),
                rx.icon("panel-left-open",  size=14),
            ),
            on_click=ResultadosState.toggle_ri_show_arbol,
            position="absolute",
            top="8px",
            left="8px",
            z_index="20",
            variant="ghost",
            size="1",
            type="button",
            cursor="pointer",
            title=rx.cond(ResultadosState.ri_show_arbol, "Ocultar panel", "Mostrar panel"),
            style={
                "background": "rgba(0,0,0,0.35)",
                "color": "white",
                "border-radius": "4px",
            },
            custom_attrs={"data-panel-controles": "true"},
        ),
        id="ri-img-viewport",
        position="relative",
        overflow="hidden",
        style={"flex": "3 1 0%"},
        min_width="0",
        height="100%",
        custom_attrs={
            "data-zoom-nivel": ResultadosState.ri_zoom_nivel,
            "data-ri-tool":    ResultadosState.ri_herramienta,
        },
    )


# ── Etiqueta de sección compacta ─────────────────────────────────────────────

def _sec_label(text: str) -> rx.Component:
    return rx.text(text, font_size="9px", font_weight="700",
                   color="var(--gray-9)", text_transform="uppercase",
                   letter_spacing="0.06em")


# ── Panel de controles y marcas ───────────────────────────────────────────────

def _panel_controles() -> rx.Component:
    _dis = ~ResultadosState.ri_imagen_activa_clasificada

    def _tool_btn(icon_name: str, tipo: str, title: str) -> rx.Component:
        _active = ResultadosState.ri_herramienta == tipo
        return rx.button(
            rx.icon(icon_name, size=13),
            title=title,
            on_click=ResultadosState.ri_activar_herramienta(tipo),
            variant=rx.cond(_active, "solid", "surface"),
            color_scheme=rx.cond(_active, "blue", "gray"),
            type="button", size="1", flex="1",
            disabled=_dis,
            custom_attrs={"data-panel-controles": "true"},
        )

    def _fila_marca(m: dict) -> rx.Component:
        return rx.hstack(
            rx.icon(
                rx.cond(m["tipo_marca"] == "c", "circle",
                rx.cond(m["tipo_marca"] == "f", "move-up-right", "type")),
                size=11,
                color=m["color"],
            ),
            rx.text(
                rx.cond(m["observacion"] != "", m["observacion"], "—"),
                font_size="10px", flex="1", no_of_lines=1,
                color="var(--gray-12)",
            ),
            rx.cond(
                m["tipo_marca"] == "t",
                rx.cond(
                    State.puede_escribir,
                    rx.button(
                        rx.icon("pencil", size=11),
                        on_click=ResultadosState.ri_abrir_editar_marca(m["id_marca"]),
                        **_BTN_GHOST, color="var(--blue-9)",
                        custom_attrs={"data-panel-controles": "true"},
                    ),
                    rx.fragment(),
                ),
            ),
            rx.cond(
                State.puede_escribir,
                rx.button(
                    rx.icon("trash-2", size=11),
                    on_click=ResultadosState.ri_eliminar_marca_item(m["id_marca"]),
                    **_BTN_GHOST, color="var(--red-9)",
                    custom_attrs={"data-panel-controles": "true"},
                ),
                rx.fragment(),
            ),
            spacing="1", width="100%", align="center",
            padding="1px 0",
        )

    # Parte superior fija: herramientas
    _top = rx.vstack(
        # ── Zoom ─────────────────────────────────────────────────────────────
        _sec_label("Zoom"),
        rx.hstack(
            rx.button(
                rx.icon("zoom-out", size=13),
                on_click=ResultadosState.ri_zoom_out,
                disabled=ResultadosState.ri_zoom_nivel == 0,
                variant="soft", type="button", size="1", flex="1",
                custom_attrs={"data-zoom-dir": "out"},
            ),
            rx.text(ResultadosState.ri_zoom_label,
                    font_size="11px", font_weight="500",
                    color="var(--gray-12)", text_align="center", min_width="32px"),
            rx.button(
                rx.icon("zoom-in", size=13),
                on_click=ResultadosState.ri_zoom_in,
                disabled=ResultadosState.ri_zoom_nivel == 8,
                variant="soft", type="button", size="1", flex="1",
                custom_attrs={"data-zoom-dir": "in"},
            ),
            spacing="1", width="100%", align="center",
        ),
        rx.text("⎵ + arrastrar", font_size="8px", color="var(--gray-7)", width="100%"),
        rx.separator(width="100%"),
        # ── Rotación ─────────────────────────────────────────────────────────
        _sec_label("Rotación"),
        rx.button(
            rx.icon("rotate-cw", size=13), "Girar 90°",
            on_click=ResultadosState.ri_rotar,
            variant="soft", type="button", size="1", width="100%",
            disabled=_dis,
        ),
        rx.separator(width="100%"),
        # ── Marcas — solo puede_escribir ────────────────────────────────────
        rx.cond(
            State.puede_escribir,
            rx.vstack(
                _sec_label("Marcas"),
                rx.hstack(
                    _tool_btn("circle",       "c", "Círculo: click 1=centro, click 2=radio"),
                    _tool_btn("move-up-right","f", "Flecha: click 1=punta, click 2=inicio"),
                    _tool_btn("type",         "t", "Texto: click para posicionar"),
                    spacing="1", width="100%",
                ),
                rx.cond(
                    ResultadosState.ri_herramienta != "",
                    rx.text(
                        rx.cond(ResultadosState.ri_herramienta == "c",
                                "Click en imagen → centro, luego radio",
                        rx.cond(ResultadosState.ri_herramienta == "f",
                                "Click en imagen → punta, luego inicio",
                                "Click en imagen para posicionar texto")),
                        font_size="8px", color="var(--blue-9)",
                        text_align="center", width="100%",
                    ),
                ),
                spacing="1", width="100%",
            ),
            rx.fragment(),
        ),
        rx.separator(width="100%"),
        # ── Laboratorio ──────────────────────────────────────────────────────
        _sec_label("Laboratorio"),
        rx.button(
            rx.icon("flask-conical", size=13), "Laboratorio",
            on_click=LaboratorioState.lab_abrir(ResultadosState.ri_id_imagen_activa),
            variant="soft", type="button", size="1", width="100%",
            disabled=State.resultados_deshabilitado_por_ajeno,
        ),
        rx.separator(width="100%"),
        # ── Cabecera lista marcas ─────────────────────────────────────────────
        _sec_label("Lista de marcas"),
        spacing="1", width="100%", flex_shrink="0",
        padding="8px 8px 4px 8px",
    )

    # Parte inferior scrollable: lista de marcas
    _lista = rx.box(
        rx.cond(
            ResultadosState.ri_marcas.length() == 0,
            rx.text("Sin marcas", font_size="10px", color="var(--gray-8)",
                    text_align="center", width="100%", padding_y="6px"),
            rx.vstack(
                rx.foreach(ResultadosState.ri_marcas, _fila_marca),
                spacing="0", width="100%",
            ),
        ),
        flex="1",
        overflow_y="auto",
        padding="4px 8px 8px 8px",
        width="100%",
    )

    return rx.box(
        _top,
        _lista,
        display="flex",
        flex_direction="column",
        style={"flex": "0 0 140px"},
        min_width="0",
        height="100%",
        background="var(--gray-1)",
        border_left=_BORDER,
        overflow="hidden",
    )


# ── Upload compacto para la barra de título ───────────────────────────────────

# ── Diálogo confirmación nueva marca ─────────────────────────────────────────

def _dlg_nueva_marca() -> rx.Component:
    _titulo = rx.cond(
        ResultadosState.ri_nv_tipo == "c", "Nueva Marca — Círculo",
        rx.cond(ResultadosState.ri_nv_tipo == "f", "Nueva Marca — Flecha",
                "Nueva Marca — Texto"),
    )
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(_titulo, font_size="14px", font_weight="700"),
            rx.vstack(
                # ── Observación / texto de la marca ──────────────────────────
                rx.cond(
                    ResultadosState.ri_nv_tipo == "t",
                    rx.vstack(
                        rx.text("Texto a mostrar *", font_size="11px", font_weight="600"),
                        rx.text_area(
                            value=ResultadosState.ri_nv_obs,
                            on_change=ResultadosState.set_ri_nv_obs,
                            placeholder="Escribe el texto de la marca...",
                            rows="3",
                            width="100%",
                        ),
                        spacing="1", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Observación (etiqueta)", font_size="11px", font_weight="600"),
                        rx.input(
                            value=ResultadosState.ri_nv_obs,
                            on_change=ResultadosState.set_ri_nv_obs,
                            placeholder="Descripción corta (opcional)...",
                            max_length=30,
                            width="100%",
                        ),
                        spacing="1", width="100%",
                    ),
                ),
                # ── Color ────────────────────────────────────────────────────
                rx.hstack(
                    rx.text("Color", font_size="11px", font_weight="600",
                            min_width="80px"),
                    rx.el.input(
                        type="color",
                        value=ResultadosState.ri_nv_color,
                        on_change=ResultadosState.set_ri_nv_color,
                        style={
                            "width": "52px", "height": "28px",
                            "padding": "2px", "cursor": "pointer",
                            "border": "1px solid var(--gray-5)",
                            "border-radius": "4px",
                        },
                    ),
                    align="center", spacing="2",
                ),
                # ── Grosor (círculo y flecha) ─────────────────────────────────
                rx.cond(
                    ResultadosState.ri_nv_tipo != "t",
                    rx.hstack(
                        rx.text("Grosor (px)", font_size="11px", font_weight="600",
                                min_width="80px"),
                        rx.el.input(
                            value=ResultadosState.ri_nv_grosor,
                            on_change=ResultadosState.set_ri_nv_grosor,
                            type="number",
                            min=1,
                            max=10,
                            style={"width": "64px"},
                        ),
                        align="center", spacing="2",
                    ),
                ),
                # ── Tamaño fuente (texto) ─────────────────────────────────────
                rx.cond(
                    ResultadosState.ri_nv_tipo == "t",
                    rx.hstack(
                        rx.text("Fuente (px)", font_size="11px", font_weight="600",
                                min_width="80px"),
                        rx.el.input(
                            value=ResultadosState.ri_nv_font,
                            on_change=ResultadosState.set_ri_nv_font,
                            type="number",
                            min=8,
                            max=72,
                            style={"width": "64px"},
                        ),
                        align="center", spacing="2",
                    ),
                ),
                spacing="3", width="100%",
            ),
            rx.hstack(
                rx.button(
                    "Rechazar",
                    on_click=ResultadosState.ri_cancelar_nueva_marca,
                    variant="soft", color_scheme="red", type="button", size="2",
                ),
                rx.spacer(),
                rx.button(
                    "Guardar marca",
                    on_click=ResultadosState.ri_guardar_nueva_marca,
                    type="button", size="2",
                ),
                width="100%",
                margin_top="16px",
            ),
            max_width="360px",
        ),
        open=ResultadosState.ri_nv_open,
    )


_ACCEPT = {
    "image/jpeg": [".jpg", ".jpeg"],
    "image/png":  [".png"],
    "application/pdf": [".pdf"],
}

def upload_resultados_titulo() -> rx.Component:
    """Botón de upload + indicador de error para la barra de título del offcanvas."""
    return rx.hstack(
        rx.cond(
            ResultadosState.ri_upload_error != "",
            rx.text(
                ResultadosState.ri_upload_error,
                font_size="10px", color="var(--red-9)",
                max_width="180px", no_of_lines=1,
            ),
        ),
        rx.upload(
            rx.button(
                rx.cond(
                    ResultadosState.ri_subiendo,
                    rx.spinner(size="1"),
                    rx.icon("upload", size=13),
                ),
                rx.cond(
                    ResultadosState.ri_subiendo,
                    rx.text("Subiendo…", font_size="11px"),
                    rx.text("Subir archivos", font_size="11px"),
                ),
                variant="soft", color_scheme="blue",
                type="button", size="1",
                disabled=ResultadosState.ri_subiendo | State.resultados_deshabilitado_por_ajeno,
                gap="1",
            ),
            id="up_resultados",
            multiple=True,
            accept=_ACCEPT,
            on_drop=ResultadosState.ri_procesar_upload(
                rx.upload_files(upload_id="up_resultados")
            ),
            disabled=ResultadosState.ri_subiendo | State.resultados_deshabilitado_por_ajeno,
            border="none",
            outline="none",
            display="inline-flex",
            padding="0",
            background="transparent",
        ),
        align="center",
        spacing="2",
    )


# ── Overlay de carga ──────────────────────────────────────────────────────────

def _overlay_carga() -> rx.Component:
    """Overlay full-screen con cursor wait y mensaje mientras se procesan archivos."""
    return rx.cond(
        ResultadosState.ri_subiendo,
        rx.fragment(
            # Inyecta cursor:wait en TODOS los elementos del documento
            rx.el.style("*, *::before, *::after { cursor: wait !important; }"),
            rx.box(
                rx.vstack(
                    rx.spinner(size="3", color="white"),
                    rx.text(
                        "Cargando archivos…",
                        font_size="14px", font_weight="600", color="white",
                    ),
                    rx.text(
                        "Por favor espere",
                        font_size="12px", color="var(--gray-4)",
                    ),
                    align="center",
                    spacing="2",
                    background="rgba(0,0,0,0.72)",
                    padding="28px 36px",
                    border_radius="12px",
                ),
                position="fixed",
                top="0", left="0", right="0", bottom="0",
                background="rgba(0,0,0,0.18)",
                z_index="9998",
                display="flex",
                align_items="center",
                justify_content="center",
                cursor="wait",
            ),
        ),
    )


# ── Diálogo editar marca de texto ────────────────────────────────────────────

def _dlg_editar_marca() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Editar marca — Texto",
                            font_size="14px", font_weight="700"),
            rx.vstack(
                # ── Texto ────────────────────────────────────────────────────
                rx.vstack(
                    rx.text("Texto a mostrar *",
                            font_size="11px", font_weight="600"),
                    rx.text_area(
                        value=ResultadosState.ri_nv_obs,
                        on_change=ResultadosState.set_ri_nv_obs,
                        placeholder="Escribe el texto de la marca...",
                        rows="3",
                        width="100%",
                    ),
                    spacing="1", width="100%",
                ),
                # ── Color ────────────────────────────────────────────────────
                rx.hstack(
                    rx.text("Color", font_size="11px", font_weight="600",
                            min_width="80px"),
                    rx.el.input(
                        type="color",
                        value=ResultadosState.ri_nv_color,
                        on_change=ResultadosState.set_ri_nv_color,
                        style={
                            "width": "52px", "height": "28px",
                            "padding": "2px", "cursor": "pointer",
                            "border": "1px solid var(--gray-5)",
                            "border-radius": "4px",
                        },
                    ),
                    align="center", spacing="2",
                ),
                # ── Fuente ───────────────────────────────────────────────────
                rx.hstack(
                    rx.text("Fuente (px)", font_size="11px", font_weight="600",
                            min_width="80px"),
                    rx.el.input(
                        value=ResultadosState.ri_nv_font,
                        on_change=ResultadosState.set_ri_nv_font,
                        type="number",
                        min=8,
                        max=72,
                        style={"width": "64px"},
                    ),
                    align="center", spacing="2",
                ),
                spacing="3", width="100%",
            ),
            rx.hstack(
                rx.button(
                    "Cancelar",
                    on_click=ResultadosState.ri_cancelar_edicion_marca,
                    variant="soft", color_scheme="gray", type="button", size="2",
                ),
                rx.spacer(),
                rx.button(
                    "Guardar cambios",
                    on_click=ResultadosState.ri_guardar_edicion_marca,
                    type="button", size="2",
                ),
                width="100%",
                margin_top="16px",
            ),
            max_width="360px",
        ),
        open=ResultadosState.ri_edit_open,
    )


# ── Diálogo borrar resultado completo ────────────────────────────────────────

def _dlg_borrar_resultado() -> rx.Component:
    """Confirmación con código aleatorio antes de eliminar un resultado y sus imágenes."""
    codigo_ok = ResultadosState.ri_borrar_codigo_input == ResultadosState.ri_borrar_codigo_esperado
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                "Eliminar resultado de imagen",
                font_size="14px", font_weight="700", color="var(--red-11)",
            ),
            rx.vstack(
                rx.callout.root(
                    rx.callout.icon(rx.icon("triangle-alert", size=16)),
                    rx.callout.text(
                        "Operación permanente. Se eliminarán el registro y "
                        "todas las imágenes asociadas.",
                        font_size="12px",
                    ),
                    color="red",
                    size="1",
                    width="100%",
                ),
                rx.text(
                    "Para confirmar, escriba exactamente el siguiente código:",
                    font_size="11px", color="var(--gray-11)",
                ),
                rx.box(
                    rx.text(
                        ResultadosState.ri_borrar_codigo_esperado,
                        font_size="22px", font_weight="700",
                        font_family="monospace", letter_spacing="0.18em",
                        color="var(--red-11)", text_align="center",
                    ),
                    width="100%",
                    padding="8px",
                    background="var(--red-3)",
                    border_radius="6px",
                    border="1px solid var(--red-6)",
                ),
                rx.input(
                    placeholder="Escribe el código aquí",
                    value=ResultadosState.ri_borrar_codigo_input,
                    on_change=ResultadosState.set_ri_borrar_codigo_input,
                    font_size="16px",
                    font_family="monospace",
                    text_align="center",
                    width="100%",
                    auto_focus=True,
                ),
                rx.hstack(
                    rx.button(
                        "Cancelar",
                        on_click=ResultadosState.ri_cancelar_borrar_resultado,
                        variant="soft", color_scheme="gray",
                        type="button", size="2",
                    ),
                    rx.spacer(),
                    rx.button(
                        "Eliminar definitivamente",
                        on_click=ResultadosState.ri_confirmar_borrar_resultado,
                        type="button", size="2",
                        color_scheme="red",
                        disabled=~codigo_ok,
                    ),
                    width="100%",
                    margin_top="8px",
                ),
                spacing="3", width="100%",
            ),
            max_width="380px",
        ),
        open=ResultadosState.ri_borrar_resultado_open,
    )


# ── Contenido del panel (para usar dentro del offcanvas existente) ────────────

def panel_resultados_examenes() -> rx.Component:
    """Contenido completo: árbol + análisis + diálogo. Se monta dentro de offcanvas_resultados_examenes."""
    return rx.fragment(
        rx.hstack(
            rx.box(
                _panel_arbol(),
                id="ri-arbol-wrapper",
                style={
                    "width":      rx.cond(ResultadosState.ri_show_arbol, "340px", "0px"),
                    "overflow":   "hidden",
                    "flex-shrink":"0",
                    "height":     "100%",
                    "transition": "width 0.25s ease-in-out",
                },
            ),
            _panel_analisis(),
            _panel_controles(),
            spacing="0",
            width="100%",
            flex="1",
            overflow="hidden",
            align="start",
        ),
        _dialogo_asignar(),
        _dlg_nueva_marca(),
        _dlg_editar_marca(),
        _dlg_borrar_resultado(),
        _overlay_carga(),
        rx.script(src="/pan_tool.js"),
        rx.script(src="/marks_tool.js"),
    )
