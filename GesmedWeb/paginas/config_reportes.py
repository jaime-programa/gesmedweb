import reflex as rx
from ..state import State, ConfigReportesState

# ── Helpers de estilo ──────────────────────────────────────────────────────────
_TH  = {"font_size": "11px", "font_weight": "600", "color": "var(--gray-11)",
         "padding": "4px 6px", "white_space": "nowrap"}
_TD  = {"font_size": "11px", "padding": "3px 6px", "vertical_align": "middle"}
_HDR = {"background": "var(--gray-2)", "border_bottom": "1px solid var(--gray-5)"}

def _seccion_header(titulo: str, boton: rx.Component | None = None) -> rx.Component:
    return rx.hstack(
        rx.text(titulo, font_size="12px", font_weight="600", color="var(--gray-12)"),
        rx.spacer(),
        boton or rx.fragment(),
        width="100%", margin_bottom="4px",
    )

def _chip(texto: str, on_delete=None) -> rx.Component:
    return rx.hstack(
        rx.text(texto, font_size="10px"),
        rx.cond(
            on_delete is not None,
            rx.icon("x", size=10, cursor="pointer", on_click=on_delete),
            rx.fragment(),
        ),
        bg="var(--blue-3)", border_radius="10px",
        padding="1px 6px", spacing="1", align="center",
    )


# ── Navbar ─────────────────────────────────────────────────────────────────────
def _navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.link(
                rx.button("← Volver", variant="ghost", size="1", type="button"),
                href="/pacientes",
            ),
            rx.text("Formato de Reporte Impreso",
                    font_size="15px", font_weight="700", color="var(--gray-12)"),
            rx.spacer(),
            rx.text(State.nombre_medico, font_size="11px", color="var(--gray-10)"),
            align="center", spacing="4", padding="0 16px", height="100%",
        ),
        position="fixed", top="0", left="0", right="0",
        height="50px", bg="white",
        border_bottom="1px solid var(--gray-5)", z_index="999",
    )


# ── BLOQUE 1: Tabla Reportes ───────────────────────────────────────────────────
def _fila_reporte(row: dict) -> rx.Component:
    es_sel = ConfigReportesState.cr_reporte_id == row.id
    return rx.table.row(
        rx.table.cell(rx.text(row.nombre, **_TD), **_TD),
        rx.table.cell(rx.text(row.explica, **_TD), **_TD),
        rx.table.cell(rx.text(row.fuente,  font_size="11px"), **_TD),
        rx.table.cell(
            rx.hstack(
                rx.icon("pencil", size=13, cursor="pointer", color="var(--blue-9)",
                        on_click=ConfigReportesState.cr_iniciar_edicion_r(row.id)),
                rx.icon("trash_2", size=13, cursor="pointer", color="var(--red-9)",
                        on_click=ConfigReportesState.cr_confirmar_borrar(
                            "reporte", row.id, row.nombre)),
                spacing="2",
            ), **_TD,
        ),
        on_click=ConfigReportesState.cr_seleccionar_reporte(row.id),
        style={"background": rx.cond(es_sel, "var(--blue-2)", "white"),
               "cursor": "pointer"},
    )


def _dlg_editar_reporte() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Editar Reporte Impreso", font_size="14px"),
            rx.vstack(
                rx.vstack(
                    rx.text("Nombre *", font_size="11px", font_weight="500"),
                    rx.input(value=ConfigReportesState.cr_edit_r_nombre,
                             on_change=ConfigReportesState.set_cr_edit_r_nombre,
                             size="2", width="100%"),
                    spacing="1", width="100%",
                ),
                rx.vstack(
                    rx.text("Explicación", font_size="11px", font_weight="500"),
                    rx.input(value=ConfigReportesState.cr_edit_r_explica,
                             on_change=ConfigReportesState.set_cr_edit_r_explica,
                             size="2", width="100%"),
                    spacing="1", width="100%",
                ),
                rx.vstack(
                    rx.text("Fuente", font_size="11px", font_weight="500"),
                    rx.select(
                        ConfigReportesState.cr_fuentes,
                        value=ConfigReportesState.cr_edit_r_fuente,
                        on_change=ConfigReportesState.set_cr_edit_r_fuente,
                        size="2", width="100%",
                    ),
                    spacing="1", width="100%",
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray",
                                  size="2", type="button",
                                  on_click=ConfigReportesState.cr_cancelar_edicion_r),
                    ),
                    rx.button("Guardar", size="2", type="button",
                              on_click=ConfigReportesState.cr_guardar_r),
                    justify="end", width="100%",
                ),
                spacing="3", width="100%", padding_top="8px",
            ),
            max_width="420px", width="90vw",
        ),
        open=ConfigReportesState.cr_dlg_edit_r,
        on_open_change=ConfigReportesState.set_cr_dlg_edit_r,
    )


def _dlg_nuevo_reporte() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Nuevo Reporte Impreso", font_size="14px"),
            rx.vstack(
                rx.vstack(
                    rx.text("Nombre *", font_size="11px", font_weight="500"),
                    rx.input(value=ConfigReportesState.cr_nr_nombre,
                             on_change=ConfigReportesState.set_cr_nr_nombre,
                             placeholder="ej. pedido_laboratorio", size="2", width="100%"),
                    spacing="1", width="100%",
                ),
                rx.vstack(
                    rx.text("Explicación", font_size="11px", font_weight="500"),
                    rx.input(value=ConfigReportesState.cr_nr_explica,
                             on_change=ConfigReportesState.set_cr_nr_explica,
                             size="2", width="100%"),
                    spacing="1", width="100%",
                ),
                rx.vstack(
                    rx.text("Fuente", font_size="11px", font_weight="500"),
                    rx.select(
                        ConfigReportesState.cr_fuentes,
                        value=ConfigReportesState.cr_nr_fuente,
                        on_change=ConfigReportesState.set_cr_nr_fuente,
                        size="2", width="100%",
                    ),
                    spacing="1", width="100%",
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray",
                                  size="2", type="button"),
                    ),
                    rx.button("Guardar", size="2", type="button",
                              on_click=ConfigReportesState.cr_crear_r),
                    justify="end", width="100%",
                ),
                spacing="3", width="100%", padding_top="8px",
            ),
            max_width="420px", width="90vw",
        ),
        open=ConfigReportesState.cr_dlg_nuevo_r,
        on_open_change=ConfigReportesState.set_cr_dlg_nuevo_r,
    )


def bloque1() -> rx.Component:
    return rx.box(
        _seccion_header(
            "Reporte Impreso",
            rx.button("+ Nuevo Reporte", size="1", type="button",
                      on_click=ConfigReportesState.cr_abrir_dlg_nuevo_r),
        ),
        rx.box(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Nombre",      **_TH),
                        rx.table.column_header_cell("Explicación", **_TH),
                        rx.table.column_header_cell("Fuente",      **_TH),
                        rx.table.column_header_cell("CRUD",        **_TH),
                        style=_HDR,
                    ),
                ),
                rx.table.body(
                    rx.foreach(ConfigReportesState.cr_reportes, _fila_reporte),
                ),
                width="100%", size="1",
            ),
            overflow_y="auto", max_height="200px",
            border="1px solid var(--gray-4)", border_radius="4px",
        ),
        _dlg_nuevo_reporte(),
        _dlg_editar_reporte(),
        width="100%",
    )


# ── BLOQUE 2: Tabla Secciones ──────────────────────────────────────────────────
def _chips_params_display(params: list) -> rx.Component:
    return rx.hstack(
        rx.foreach(params, lambda p: _chip(p)),
        flex_wrap="wrap", spacing="1",
    )


def _fila_seccion(row: dict) -> rx.Component:
    es_sel = ConfigReportesState.cr_seccion_id == row.id
    return rx.table.row(
        rx.table.cell(rx.text(row.orden.to(str), **_TD), **_TD),
        rx.table.cell(rx.text(row.explica, **_TD), **_TD),
        rx.table.cell(_chips_params_display(row.params), **_TD),
        rx.table.cell(
            rx.hstack(
                rx.icon("pencil", size=13, cursor="pointer", color="var(--blue-9)",
                        on_click=ConfigReportesState.cr_iniciar_edicion_s(row.id)),
                rx.icon("trash_2", size=13, cursor="pointer", color="var(--red-9)",
                        on_click=ConfigReportesState.cr_confirmar_borrar(
                            "seccion", row.id, row.explica)),
                spacing="2",
            ), **_TD,
        ),
        on_click=ConfigReportesState.cr_seleccionar_seccion(row.id),
        style={"background": rx.cond(es_sel, "var(--blue-2)", "white"),
               "cursor": "pointer"},
    )


def _dlg_clonar_seccion() -> rx.Component:
    sin_dest = ConfigReportesState.cr_clonar_dest_id == 0
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Clonar Sección", font_size="14px"),
            rx.vstack(
                rx.text("Selecciona la sección destino donde se copiarán las celdas:",
                        font_size="12px", color="var(--gray-11)"),
                rx.select.root(
                    rx.select.trigger(placeholder="— elegir sección destino —",
                                      width="100%"),
                    rx.select.content(
                        rx.foreach(
                            ConfigReportesState.cr_clonar_opciones,
                            lambda s: rx.select.item(s.explica, value=s.id.to(str)),
                        ),
                    ),
                    value=ConfigReportesState.cr_clonar_dest_id.to(str),
                    on_change=ConfigReportesState.set_cr_clonar_dest_id,
                    size="2", width="100%",
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray",
                                  size="2", type="button"),
                    ),
                    rx.button("Clonar", size="2", type="button",
                              color_scheme="blue",
                              disabled=sin_dest,
                              on_click=ConfigReportesState.cr_ejecutar_clonar_s),
                    justify="end", width="100%",
                ),
                spacing="3", width="100%", padding_top="8px",
            ),
            max_width="420px", width="90vw",
        ),
        open=ConfigReportesState.cr_dlg_clonar_s,
        on_open_change=ConfigReportesState.set_cr_dlg_clonar_s,
    )


def _panel_avanzados_s(
    modo_val, set_modo,
    paso_val, set_paso,
    max_val,  set_max,
    ancla_val, set_ancla,
    gap_val,   set_gap,
    cond_val,  set_cond,
    campo_val, set_campo,
    ncols_val, set_ncols,
    pcol_val,  set_pcol,
    slot_val,  set_slot,
    titulo_val, set_titulo,
) -> rx.Component:
    """Panel colapsable de opciones avanzadas compartido por editar/nueva sección."""
    es_bucle   = modo_val != "N"
    es_agrupado = modo_val == "G"
    return rx.accordion.root(
        rx.accordion.item(
            header=rx.text("Opciones avanzadas", font_size="11px",
                           color="var(--gray-10)", font_weight="500"),
            content=rx.vstack(
                # Modo bucle
                rx.hstack(
                    rx.vstack(
                        rx.text("Modo", font_size="10px", font_weight="500"),
                        rx.select.root(
                            rx.select.trigger(width="130px"),
                            rx.select.content(
                                rx.select.item("N — Normal",          value="N"),
                                rx.select.item("F — Bucle plano",     value="F"),
                                rx.select.item("G — Bucle agrupado",  value="G"),
                            ),
                            value=modo_val, on_change=set_modo, size="1",
                        ),
                        spacing="1",
                    ),
                    rx.cond(es_bucle, rx.hstack(
                        rx.vstack(
                            rx.text("Paso fila", font_size="10px", font_weight="500"),
                            rx.input(value=paso_val.to(str), on_change=set_paso,
                                     type="number", size="1", width="70px"),
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text("Máx ítems", font_size="10px", font_weight="500"),
                            rx.input(value=max_val.to(str), on_change=set_max,
                                     type="number", size="1", width="70px"),
                            spacing="1",
                        ),
                        spacing="3",
                    ), rx.fragment()),
                    spacing="3", align="end", flex_wrap="wrap",
                ),
                # Agrupado
                rx.cond(es_agrupado, rx.vstack(
                    rx.hstack(
                        rx.vstack(
                            rx.text("Campo grupo", font_size="10px", font_weight="500"),
                            rx.input(value=campo_val, on_change=set_campo,
                                     placeholder="nombre_col_sql",
                                     size="1", width="130px"),
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text("Nº columnas", font_size="10px", font_weight="500"),
                            rx.input(value=ncols_val.to(str), on_change=set_ncols,
                                     type="number", size="1", width="70px"),
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text("Paso col", font_size="10px", font_weight="500"),
                            rx.input(value=pcol_val.to(str), on_change=set_pcol,
                                     type="number", size="1", width="70px"),
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text("Slot height", font_size="10px", font_weight="500"),
                            rx.input(value=slot_val.to(str), on_change=set_slot,
                                     type="number", size="1", width="70px"),
                            spacing="1",
                        ),
                        spacing="3", align="end", flex_wrap="wrap",
                    ),
                    spacing="2", width="100%",
                ), rx.fragment()),
                # Ancla
                rx.vstack(
                    rx.text("Anclar debajo de sección",
                            font_size="10px", font_weight="500"),
                    rx.hstack(
                        rx.select.root(
                            rx.select.trigger(placeholder="— sin ancla —", width="200px"),
                            rx.select.content(
                                rx.select.item("— sin ancla —", value="0"),
                                rx.foreach(
                                    ConfigReportesState.cr_ancla_opciones,
                                    lambda s: rx.select.item(s.explica, value=s.id.to(str)),
                                ),
                            ),
                            value=ancla_val.to(str), on_change=set_ancla, size="1",
                        ),
                        rx.vstack(
                            rx.text("Gap (filas de separación con sección anclada)", font_size="10px", font_weight="500"),
                            rx.input(value=gap_val.to(str), on_change=set_gap,
                                    type="number", size="1", width="70px"),
                            spacing="1",
                        ),
                        spacing="3", align="end",
                    ),
                    spacing="1", width="100%",
                ),
                # Título de sección
                rx.vstack(
                    rx.text("Título de sección",
                            font_size="10px", font_weight="500"),
                    rx.input(value=titulo_val, on_change=set_titulo,
                             placeholder="mín. 3 caracteres para activarlo",
                             size="1", width="100%"),
                    spacing="1", width="100%",
                ),
                # Condición de activación
                rx.vstack(
                    rx.text("SQL condición de activación",
                            font_size="10px", font_weight="500",
                            color="var(--gray-10)"),
                    rx.text_area(value=cond_val, on_change=set_cond,
                                 placeholder="SELECT 1 FROM ... WHERE ...",
                                 rows="2", width="100%",
                                 font_size="10px", font_family="monospace"),
                    spacing="1", width="100%",
                ),
                spacing="3", width="100%",
            ),
        ),
        collapsible=True, width="100%", variant="ghost",
    )


def _dlg_editar_seccion() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Editar Sección", font_size="14px"),
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text("Orden", font_size="11px", font_weight="500"),
                        rx.input(value=ConfigReportesState.cr_edit_s_orden.to(str),
                                 on_change=ConfigReportesState.set_cr_edit_s_orden,
                                 type="number", size="2", width="80px"),
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Explicación", font_size="11px", font_weight="500"),
                        rx.input(value=ConfigReportesState.cr_edit_s_explica,
                                 on_change=ConfigReportesState.set_cr_edit_s_explica,
                                 size="2", width="100%"),
                        spacing="1", width="100%",
                    ),
                    spacing="3", width="100%", align="end",
                ),
                rx.vstack(
                    rx.text("Instrucción SQL", font_size="11px", font_weight="500"),
                    rx.text_area(value=ConfigReportesState.cr_sql_edit,
                                 on_change=ConfigReportesState.set_cr_sql_edit,
                                 rows="5", width="100%", font_size="11px",
                                 font_family="monospace"),
                    spacing="1", width="100%",
                ),
                rx.vstack(
                    rx.text("Parámetros IN", font_size="11px", font_weight="500"),
                    rx.hstack(
                        rx.foreach(
                            ConfigReportesState.cr_edit_s_params,
                            lambda p: _chip(p, on_delete=ConfigReportesState.cr_edit_s_del_param(p)),
                        ),
                        rx.input(value=ConfigReportesState.cr_edit_s_param_input,
                                 on_change=ConfigReportesState.set_cr_edit_s_param_input,
                                 placeholder="nombre_param", size="1", width="120px"),
                        rx.button("Agregar", size="1", type="button",
                                  on_click=ConfigReportesState.cr_edit_s_add_param),
                        flex_wrap="wrap", spacing="2", align="center",
                    ),
                    spacing="1", width="100%",
                ),
                _panel_avanzados_s(
                    ConfigReportesState.cr_edit_s_modo_bucle,   ConfigReportesState.set_cr_edit_s_modo_bucle,
                    ConfigReportesState.cr_edit_s_paso_fila,    ConfigReportesState.set_cr_edit_s_paso_fila,
                    ConfigReportesState.cr_edit_s_max_iter,     ConfigReportesState.set_cr_edit_s_max_iter,
                    ConfigReportesState.cr_edit_s_ancla_id,     ConfigReportesState.set_cr_edit_s_ancla_id,
                    ConfigReportesState.cr_edit_s_ancla_gap,    ConfigReportesState.set_cr_edit_s_ancla_gap,
                    ConfigReportesState.cr_edit_s_cond_activa,  ConfigReportesState.set_cr_edit_s_cond_activa,
                    ConfigReportesState.cr_edit_s_campo_grupo,  ConfigReportesState.set_cr_edit_s_campo_grupo,
                    ConfigReportesState.cr_edit_s_num_columnas, ConfigReportesState.set_cr_edit_s_num_columnas,
                    ConfigReportesState.cr_edit_s_paso_columna, ConfigReportesState.set_cr_edit_s_paso_columna,
                    ConfigReportesState.cr_edit_s_slot_height,  ConfigReportesState.set_cr_edit_s_slot_height,
                    ConfigReportesState.cr_edit_s_titulo,       ConfigReportesState.set_cr_edit_s_titulo,
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray",
                                  size="2", type="button",
                                  on_click=ConfigReportesState.cr_cancelar_edicion_s),
                    ),
                    rx.button("Guardar", size="2", type="button",
                              on_click=ConfigReportesState.cr_guardar_s),
                    justify="end", width="100%",
                ),
                spacing="3", width="100%", padding_top="8px",
            ),
            max_width="600px", width="95vw",
        ),
        open=ConfigReportesState.cr_dlg_edit_s,
        on_open_change=ConfigReportesState.set_cr_dlg_edit_s,
    )


def _dlg_nueva_seccion() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Nueva Sección", font_size="14px"),
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text("Orden", font_size="11px", font_weight="500"),
                        rx.input(value=ConfigReportesState.cr_ns_orden.to(str),
                                 on_change=ConfigReportesState.set_cr_ns_orden,
                                 type="number", size="2", width="80px"),
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Explicación", font_size="11px", font_weight="500"),
                        rx.input(value=ConfigReportesState.cr_ns_explica,
                                 on_change=ConfigReportesState.set_cr_ns_explica,
                                 size="2", width="100%"),
                        spacing="1", width="100%",
                    ),
                    spacing="3", width="100%", align="end",
                ),
                rx.vstack(
                    rx.text("Instrucción SQL", font_size="11px", font_weight="500"),
                    rx.text_area(value=ConfigReportesState.cr_ns_sql,
                                 on_change=ConfigReportesState.set_cr_ns_sql,
                                 rows="4", width="100%", font_size="11px",
                                 font_family="monospace"),
                    spacing="1", width="100%",
                ),
                rx.vstack(
                    rx.text("Parámetros IN", font_size="11px", font_weight="500"),
                    rx.hstack(
                        rx.foreach(
                            ConfigReportesState.cr_ns_params,
                            lambda p: _chip(p, on_delete=ConfigReportesState.cr_ns_del_param(p)),
                        ),
                        rx.input(value=ConfigReportesState.cr_ns_param_input,
                                 on_change=ConfigReportesState.set_cr_ns_param_input,
                                 placeholder="nombre_param", size="1", width="120px"),
                        rx.button("Agregar", size="1", type="button",
                                  on_click=ConfigReportesState.cr_ns_add_param),
                        flex_wrap="wrap", spacing="2", align="center",
                    ),
                    spacing="1", width="100%",
                ),
                _panel_avanzados_s(
                    ConfigReportesState.cr_ns_modo_bucle,   ConfigReportesState.set_cr_ns_modo_bucle,
                    ConfigReportesState.cr_ns_paso_fila,    ConfigReportesState.set_cr_ns_paso_fila,
                    ConfigReportesState.cr_ns_max_iter,     ConfigReportesState.set_cr_ns_max_iter,
                    ConfigReportesState.cr_ns_ancla_id,     ConfigReportesState.set_cr_ns_ancla_id,
                    ConfigReportesState.cr_ns_ancla_gap,    ConfigReportesState.set_cr_ns_ancla_gap,
                    ConfigReportesState.cr_ns_cond_activa,  ConfigReportesState.set_cr_ns_cond_activa,
                    ConfigReportesState.cr_ns_campo_grupo,  ConfigReportesState.set_cr_ns_campo_grupo,
                    ConfigReportesState.cr_ns_num_columnas, ConfigReportesState.set_cr_ns_num_columnas,
                    ConfigReportesState.cr_ns_paso_columna, ConfigReportesState.set_cr_ns_paso_columna,
                    ConfigReportesState.cr_ns_slot_height,  ConfigReportesState.set_cr_ns_slot_height,
                    ConfigReportesState.cr_ns_titulo,       ConfigReportesState.set_cr_ns_titulo,
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray",
                                  size="2", type="button"),
                    ),
                    rx.button("Guardar", size="2", type="button",
                              on_click=ConfigReportesState.cr_crear_s),
                    justify="end", width="100%",
                ),
                spacing="3", width="100%", padding_top="8px",
            ),
            max_width="600px", width="95vw",
        ),
        open=ConfigReportesState.cr_dlg_nueva_s,
        on_open_change=ConfigReportesState.set_cr_dlg_nueva_s,
    )


def bloque2() -> rx.Component:
    return rx.box(
        _seccion_header(
            "Secciones del reporte",
            rx.button("+ Nueva Sección", size="1", type="button",
                      on_click=ConfigReportesState.cr_abrir_dlg_nueva_s,
                      disabled=ConfigReportesState.cr_reporte_id == 0),
        ),
        rx.box(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Orden",          **_TH),
                        rx.table.column_header_cell("Explicación",    **_TH),
                        rx.table.column_header_cell("Parámetros IN",  **_TH),
                        rx.table.column_header_cell("CRUD",           **_TH),
                        style=_HDR,
                    ),
                ),
                rx.table.body(
                    rx.foreach(ConfigReportesState.cr_secciones, _fila_seccion),
                ),
                width="100%", size="1",
            ),
            overflow_y="auto", max_height="180px",
            border="1px solid var(--gray-4)", border_radius="4px",
        ),
        # Botones Sube/Baja fila
        rx.hstack(
            rx.button("↑ Sube 1", size="1", type="button", variant="soft",
                      disabled=ConfigReportesState.cr_seccion_id == 0,
                      on_click=ConfigReportesState.cr_desplazar_celdas(-1)),
            rx.button("↓ Baja 1", size="1", type="button", variant="soft",
                      disabled=ConfigReportesState.cr_seccion_id == 0,
                      on_click=ConfigReportesState.cr_desplazar_celdas(1)),
            rx.button("← Col", size="1", type="button", variant="soft",
                      disabled=ConfigReportesState.cr_seccion_id == 0,
                      on_click=ConfigReportesState.cr_desplazar_columna(-1)),
            rx.button("→ Col", size="1", type="button", variant="soft",
                      disabled=ConfigReportesState.cr_seccion_id == 0,
                      on_click=ConfigReportesState.cr_desplazar_columna(1)),
            rx.button("Clonar Sección", size="1", type="button", variant="soft",
                      color_scheme="blue",
                      disabled=ConfigReportesState.cr_seccion_id == 0,
                      on_click=ConfigReportesState.cr_abrir_dlg_clonar_s),
            spacing="2", margin_top="6px",
        ),
        # Textarea SQL (solo lectura; la edición va al diálogo)
        rx.vstack(
            rx.text("Instrucción SQL", font_size="11px", font_weight="500",
                    color="var(--gray-10)", margin_top="8px"),
            rx.text_area(
                value=ConfigReportesState.cr_sql_display,
                read_only=True, rows="5", width="100%",
                font_size="11px", font_family="monospace",
                bg="var(--gray-2)",
            ),
            spacing="1", width="100%",
        ),
        _dlg_clonar_seccion(),
        _dlg_nueva_seccion(),
        _dlg_editar_seccion(),
        width="100%",
    )


# ── BLOQUE 3: Tabla Celdas + Editor formato ────────────────────────────────────
def _fila_celda(row: dict) -> rx.Component:
    es_sel  = ConfigReportesState.cr_celda_sel_id  == row.id
    es_edit = ConfigReportesState.cr_celda_edit_id == row.id
    _cel_click = {"on_click": ConfigReportesState.cr_seleccionar_c(row.id),
                  "cursor": "pointer"}
    _bg = rx.cond(es_edit, "var(--blue-2)", rx.cond(es_sel, "var(--gray-3)", "white"))
    return rx.table.row(
        rx.table.cell(rx.text(row.variable,  **_TD), **_TD, **_cel_click),
        rx.table.cell(rx.text(row.celda_ref, font_size="11px", font_weight="600",
                              color="var(--blue-9)", font_family="monospace"),
                      **_TD, **_cel_click),
        rx.table.cell(rx.text(row.explica,   **_TD), **_TD, **_cel_click),
        rx.table.cell(
            rx.hstack(
                rx.cond(es_edit,
                    rx.icon("x", size=13, cursor="pointer", color="var(--gray-9)",
                            on_click=ConfigReportesState.cr_cancelar_edicion_c),
                    rx.icon("pencil", size=13, cursor="pointer", color="var(--blue-9)",
                            on_click=ConfigReportesState.cr_iniciar_edicion_c(row.id)),
                ),
                rx.icon("clipboard", size=13, cursor="pointer", color="var(--green-9)",
                        on_click=ConfigReportesState.cr_abrir_dlg_pegar_fmt(row.id)),
                rx.icon("trash_2", size=13, cursor="pointer", color="var(--red-9)",
                        on_click=ConfigReportesState.cr_confirmar_borrar(
                            "celda", row.id, row.variable)),
                spacing="2",
            ), **_TD,
        ),
        style={"background": _bg, "cursor": "default"},
    )


def _dlg_nueva_celda() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Nueva Celda", font_size="14px"),
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text("Variable", font_size="11px", font_weight="500"),
                        rx.input(value=ConfigReportesState.cr_nc_variable,
                                 on_change=ConfigReportesState.set_cr_nc_variable,
                                 placeholder="nombre_columna_sql", size="2"),
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Celda", font_size="11px", font_weight="500"),
                        rx.input(
                            value=ConfigReportesState.cr_nc_celda_ref,
                            on_change=ConfigReportesState.set_cr_nc_celda_ref,
                            placeholder="ej: A8",
                            size="2", width="80px",
                            style={"text_transform": "uppercase",
                                   "font_weight": "600",
                                   "color": "var(--blue-9)"},
                        ),
                        spacing="1",
                    ),
                    spacing="3", align="end",
                ),
                rx.vstack(
                    rx.text("Explicación", font_size="11px", font_weight="500"),
                    rx.input(value=ConfigReportesState.cr_nc_explica,
                             on_change=ConfigReportesState.set_cr_nc_explica,
                             size="2", width="100%"),
                    spacing="1", width="100%",
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray",
                                  size="2", type="button"),
                    ),
                    rx.button("Guardar", size="2", type="button",
                              on_click=ConfigReportesState.cr_crear_c),
                    justify="end", width="100%",
                ),
                spacing="3", width="100%", padding_top="8px",
            ),
            max_width="420px", width="90vw",
        ),
        open=ConfigReportesState.cr_dlg_nueva_c,
        on_open_change=ConfigReportesState.set_cr_dlg_nueva_c,
    )


def _dlg_aviso_celda() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.icon("info", size=32, color="var(--blue-9)"),
                rx.text("Celda creada con formato por defecto.",
                        font_size="13px", text_align="center"),
                rx.text("Para personalizar el formato, selecciona la celda en la tabla "
                        "y presiona el ícono ✏️ de edición.",
                        font_size="12px", color="var(--gray-10)", text_align="center"),
                rx.dialog.close(
                    rx.button("Entendido", size="2", type="button",
                              on_click=ConfigReportesState.cr_cerrar_aviso_c),
                ),
                align="center", spacing="3", padding="8px",
            ),
            max_width="340px", width="90vw",
        ),
        open=ConfigReportesState.cr_dlg_aviso_c,
        on_open_change=ConfigReportesState.set_cr_dlg_aviso_c,
    )


def _dlg_pegar_formato() -> rx.Component:
    valido = ConfigReportesState.cr_pegar_fmt_valido
    n      = ConfigReportesState.cr_pegar_fmt_len
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Pegar Formato", font_size="14px"),
            rx.vstack(
                rx.text(ConfigReportesState.cr_pegar_fmt_explica,
                        font_size="12px", color="var(--gray-11)", font_style="italic"),
                rx.vstack(
                    rx.hstack(
                        rx.text("Formato", font_size="11px", font_weight="500"),
                        rx.cond(
                            valido,
                            rx.text("✓ 22 chars", font_size="10px",
                                    color="var(--green-9)", font_weight="600"),
                            rx.text(n.to(str), " / 22 chars", font_size="10px",
                                    color="var(--red-9)"),
                        ),
                        justify="between", width="100%",
                    ),
                    rx.input(
                        value=ConfigReportesState.cr_pegar_fmt_string,
                        on_change=ConfigReportesState.set_cr_pegar_fmt_string,
                        placeholder="ej: 09.12.02.00.NLU.0000.N",
                        size="2", width="100%",
                        style={"font_family": "monospace", "font_size": "13px",
                               "letter_spacing": "0.04em"},
                    ),
                    spacing="1", width="100%",
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray",
                                  size="2", type="button"),
                    ),
                    rx.button("Aplicar", size="2", type="button",
                              disabled=~valido,
                              on_click=ConfigReportesState.cr_aplicar_pegar_fmt),
                    justify="end", width="100%",
                ),
                spacing="3", width="100%", padding_top="8px",
            ),
            max_width="380px", width="90vw",
        ),
        open=ConfigReportesState.cr_dlg_pegar_fmt,
        on_open_change=ConfigReportesState.set_cr_dlg_pegar_fmt,
    )


def _editor_formato() -> rx.Component:
    """Panel de controles de formato.

    seleccionado: muestra valores; controles deshabilitados.
    editando:     habilita todos los controles.
    """
    seleccionado = ConfigReportesState.cr_celda_sel_id  != 0
    editando     = ConfigReportesState.cr_celda_edit_id != 0
    no_edit      = ConfigReportesState.cr_celda_edit_id == 0
    # Panel completo se atenúa cuando no hay nada seleccionado
    panel_style  = rx.cond(seleccionado, {}, {"opacity": "0.4", "pointer_events": "none"})

    # Celda de preview
    preview = rx.box(
        rx.text("PREVIO", font_size=f"{ConfigReportesState.cr_fmt_size}px",
                font_weight=ConfigReportesState.cr_preview_fw,
                font_style=ConfigReportesState.cr_preview_fs,
                text_decoration=ConfigReportesState.cr_preview_td,
                text_align=ConfigReportesState.cr_preview_ah,
                width="100%"),
        width="80px", height="40px",
        bg=ConfigReportesState.cr_preview_bg,
        border_top=rx.cond(ConfigReportesState.cr_fmt_borde_t, "1px solid black", "none"),
        border_right=rx.cond(ConfigReportesState.cr_fmt_borde_r, "1px solid black", "none"),
        border_bottom=rx.cond(ConfigReportesState.cr_fmt_borde_b, "1px solid black", "none"),
        border_left=rx.cond(ConfigReportesState.cr_fmt_borde_l, "1px solid black", "none"),
        display="flex", align_items="center", padding="2px",
        overflow="hidden",
    )

    # Merge grid
    def _celda_merge(cell: dict) -> rx.Component:
        return rx.box(
            width="14px", height="12px",
            bg=rx.cond(cell["sel"], "var(--blue-8)", "var(--gray-2)"),
            border="1px solid var(--gray-5)",
            cursor="pointer",
            on_click=ConfigReportesState.cr_set_merge(cell["r"], cell["c"]),
            border_radius="1px",
        )

    merge_grid = rx.vstack(
        rx.text("Merge", font_size="10px", font_weight="600", color="var(--gray-10)"),
        rx.hstack(
            rx.text(
                ConfigReportesState.cr_fmt_merge_h.to(str),
                font_size="10px", color="var(--blue-9)", font_weight="600",
            ),
            rx.text("×", font_size="10px"),
            rx.text(
                ConfigReportesState.cr_fmt_merge_v.to(str),
                font_size="10px", color="var(--blue-9)", font_weight="600",
            ),
            spacing="1",
        ),
        rx.box(
            rx.foreach(
                ConfigReportesState.cr_merge_grid,
                lambda fila_celdas: rx.hstack(
                    rx.foreach(fila_celdas, _celda_merge),
                    spacing="0",
                ),
            ),
            overflow="auto", max_height="130px", max_width="300px",
        ),
        spacing="1", align="start",
    )

    merge_bloqueado = rx.cond(no_edit, {"pointer_events": "none", "opacity": "0.5"}, {})

    return rx.box(
        rx.vstack(
            # Fila: preview + posición + merge
            rx.hstack(
                rx.vstack(
                    rx.text("Vista previa", font_size="10px", color="var(--gray-10)"),
                    preview,
                    spacing="1", align="center",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.vstack(
                            rx.text("Columna", font_size="10px", font_weight="500"),
                            rx.input(
                                value=ConfigReportesState.cr_col_letra,
                                on_change=ConfigReportesState.set_cr_fmt_columna,
                                placeholder="A",
                                size="1", width="60px",
                                disabled=no_edit,
                                style={"text_transform": "uppercase", "font_weight": "600",
                                       "color": "var(--blue-9)","text_align":"center"},
                            ),
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text("Fila", font_size="10px", font_weight="500"),
                            rx.input(
                                value=ConfigReportesState.cr_fmt_fila.to(str),
                                on_change=ConfigReportesState.set_cr_fmt_fila,
                                type="number", size="1", width="60px",
                                disabled=no_edit,
                                style={ "font_weight": "600",
                                       "color": "var(--blue-9)","text_align":"center"},
                            ),
                            spacing="1",
                        ),
                        spacing="3", align="end",
                    ),
                    rx.hstack(
                        rx.vstack(
                            rx.text("Variable", font_size="10px", font_weight="500"),
                            rx.input(value=ConfigReportesState.cr_fmt_variable,
                                     on_change=ConfigReportesState.set_cr_fmt_variable,
                                     size="1", width="120px",
                                     disabled=no_edit),
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text("Explicación", font_size="10px", font_weight="500"),
                            rx.input(value=ConfigReportesState.cr_fmt_explica,
                                     on_change=ConfigReportesState.set_cr_fmt_explica,
                                     size="1", width="150px",
                                     disabled=no_edit),
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text("Nº → letras", font_size="10px", font_weight="500"),
                            rx.checkbox(
                                checked=ConfigReportesState.cr_fmt_en_letras,
                                on_change=ConfigReportesState.set_cr_fmt_en_letras,
                                size="2",
                                disabled=no_edit,
                            ),
                            spacing="1", align="center",
                        ),
                        rx.vstack(
                            rx.text("Tipo celda", font_size="10px", font_weight="500"),
                            rx.select.root(
                                rx.select.trigger(width="90px"),
                                rx.select.content(
                                    rx.select.item("Detalle", value="D"),
                                    rx.select.item("Cab. grupo", value="G"),
                                ),
                                value=ConfigReportesState.cr_fmt_tipo_celda,
                                on_change=ConfigReportesState.set_cr_fmt_tipo_celda,
                                size="1", disabled=no_edit,
                            ),
                            spacing="1",
                        ),
                        spacing="2", align="end",
                    ),
                    spacing="2",
                ),
                rx.box(merge_grid, style=merge_bloqueado),
                rx.vstack(
                    rx.vstack(
                        rx.text("Pre-fijo", font_size="10px", font_weight="500"),
                        rx.input(
                            value=ConfigReportesState.cr_fmt_pre_fijo,
                            on_change=ConfigReportesState.set_cr_fmt_pre_fijo,
                            placeholder="ej: $ ",
                            size="1", width="120px",
                            disabled=no_edit,
                        ),
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Post-fijo", font_size="10px", font_weight="500"),
                        rx.input(
                            value=ConfigReportesState.cr_fmt_post_fijo,
                            on_change=ConfigReportesState.set_cr_fmt_post_fijo,
                            placeholder="ej:  kg",
                            size="1", width="120px",
                            disabled=no_edit,
                        ),
                        spacing="1",
                    ),
                    spacing="3", align="start",
                ),
                spacing="4", align="start", flex_wrap="wrap",
            ),

            rx.divider(),

            # Fila: tamaño fuente + relleno
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        rx.text("8px", font_size="10px"),
                        rx.slider(
                            value=ConfigReportesState.cr_fmt_size_list,
                            on_change=ConfigReportesState.set_cr_fmt_size,
                            min=8, max=18, step=1, width="120px",
                            disabled=no_edit,
                        ),
                        rx.text("18 px", font_size="10px"),
                        spacing="2", align="center",
                    ),
                    rx.text(
                        "Tamaño de fuente: ",
                        rx.text.span(ConfigReportesState.cr_fmt_size.to(str),
                                     font_weight="600", color="var(--blue-9)"),
                        rx.text.span(" px"),
                        font_size="10px", color="var(--gray-10)", text_align="center",
                    ),
                    spacing="1", align="center",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.text("0%", font_size="10px"),
                        rx.slider(
                            value=ConfigReportesState.cr_fmt_sombra_list,
                            on_change=ConfigReportesState.set_cr_fmt_sombra,
                            min=0, max=99, step=1, width="120px",
                            disabled=no_edit,
                        ),
                        rx.text("99%", font_size="10px"),
                        spacing="2", align="center",
                    ),
                    rx.text(
                        "Relleno Gris: ",
                        rx.text.span(ConfigReportesState.cr_fmt_sombra.to(str),
                                     font_weight="600", color="var(--blue-9)"),
                        rx.text.span(" %"),
                        font_size="10px", color="var(--gray-10)", text_align="center",
                    ),
                    spacing="1", align="center",
                ),
                spacing="6", flex_wrap="wrap",
            ),

            rx.divider(),

            # Fila: efectos + alineación + bordes
            rx.hstack(
                # Efectos de fuente
                rx.vstack(
                    rx.text("Efectos de fuente", font_size="10px", font_weight="600"),
                    rx.hstack(
                        rx.radio_group(
                            ["N", "B", "S", "Q"],
                            value=ConfigReportesState.cr_fmt_efecto,
                            on_change=ConfigReportesState.set_cr_fmt_efecto,
                            direction="column",
                            disabled=no_edit,
                        ),
                        rx.vstack(
                            rx.text("N = Normal", font_size="9px"),
                            rx.text("B = Bold", font_size="9px"),
                            rx.text("S = Subrayado", font_size="9px"),
                            rx.text("Q = Cursiva", font_size="9px"),
                            spacing="0",
                        ),
                        spacing="2", align="center",
                    ),
                    spacing="1",
                ),
                # Alineaciones
                rx.vstack(
                    rx.vstack(
                        rx.text("Alineación Horizontal", font_size="10px", font_weight="500"),
                        rx.select.root(
                            rx.select.trigger(width="110px"),
                            rx.select.content(
                                rx.select.item("Izquierda", value="L"),
                                rx.select.item("Centro",    value="C"),
                                rx.select.item("Derecha",   value="R"),
                            ),
                            value=ConfigReportesState.cr_fmt_alin_h,
                            on_change=ConfigReportesState.set_cr_fmt_alin_h,
                            size="1", disabled=no_edit,
                        ),
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Alineación Vertical", font_size="10px", font_weight="500"),
                        rx.select.root(
                            rx.select.trigger(width="110px"),
                            rx.select.content(
                                rx.select.item("Arriba", value="U"),
                                rx.select.item("Centro", value="C"),
                                rx.select.item("Abajo",  value="D"),
                            ),
                            value=ConfigReportesState.cr_fmt_alin_v,
                            on_change=ConfigReportesState.set_cr_fmt_alin_v,
                            size="1", disabled=no_edit,
                        ),
                        spacing="1",
                    ),
                    spacing="2",
                ),
                # Bordes
                rx.vstack(
                    rx.text("Bordes", font_size="10px", font_weight="600"),
                    rx.grid(
                        rx.fragment(),
                        rx.checkbox("Superior",  checked=ConfigReportesState.cr_fmt_borde_t,
                                    on_change=ConfigReportesState.set_cr_fmt_borde_t,
                                    size="1", disabled=no_edit),
                        rx.fragment(),
                        rx.checkbox("Izquierda", checked=ConfigReportesState.cr_fmt_borde_l,
                                    on_change=ConfigReportesState.set_cr_fmt_borde_l,
                                    size="1", disabled=no_edit),
                        rx.box(
                            rx.text("BORDES", font_size="9px", color="var(--gray-8)"),
                            border="1px dashed var(--gray-6)",
                            width="50px", height="30px",
                            display="flex", align_items="center",
                            justify_content="center",
                        ),
                        rx.checkbox("Derecha",   checked=ConfigReportesState.cr_fmt_borde_r,
                                    on_change=ConfigReportesState.set_cr_fmt_borde_r,
                                    size="1", disabled=no_edit),
                        rx.fragment(),
                        rx.checkbox("Inferior",  checked=ConfigReportesState.cr_fmt_borde_b,
                                    on_change=ConfigReportesState.set_cr_fmt_borde_b,
                                    size="1", disabled=no_edit),
                        rx.fragment(),
                        columns="3", rows="3", gap="4px",
                        align_items="center", justify_items="center",
                    ),
                    spacing="1",
                ),
                spacing="6", align="start", flex_wrap="wrap",
            ),

            spacing="3", width="100%",
        ),
        # Formato resultante + Guardar — esquina superior derecha
        rx.vstack(
            rx.text("Formato:", font_size="9px", color="var(--gray-9)"),
            rx.text(ConfigReportesState.cr_fmt_string,
                    font_size="11px", font_family="monospace",
                    font_weight="600", color="var(--gray-12)"),
            rx.cond(
                editando,
                rx.button("💾 Guardar Formato", size="1", type="button",
                          color_scheme="blue",
                          on_click=ConfigReportesState.cr_guardar_c),
                rx.fragment(),
            ),
            position="absolute", top="6px", right="8px",
            align="end", spacing="1",
        ),
        position="relative",
        padding="10px",
        border="1px solid var(--gray-4)", border_radius="4px",
        bg=rx.cond(seleccionado, "white", "var(--gray-1)"),
        style=panel_style,
    )


def bloque3() -> rx.Component:
    return rx.box(
        _seccion_header(
            "Formato de Celda",
            rx.button("+ Nueva Celda", size="1", type="button",
                      on_click=ConfigReportesState.cr_abrir_dlg_nueva_c,
                      disabled=ConfigReportesState.cr_seccion_id == 0),
        ),
        rx.box(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Variable",    **_TH),
                        rx.table.column_header_cell("Celda",       **_TH),
                        rx.table.column_header_cell("Explicación", **_TH),
                        rx.table.column_header_cell("CRUD",        **_TH),
                        style=_HDR,
                    ),
                ),
                rx.table.body(
                    rx.foreach(ConfigReportesState.cr_celdas, _fila_celda),
                ),
                width="100%", size="1",
            ),
            overflow_y="auto", max_height="180px",
            border="1px solid var(--gray-4)", border_radius="4px",
            margin_bottom="10px",
        ),
        _editor_formato(),
        _dlg_nueva_celda(),
        _dlg_aviso_celda(),
        _dlg_pegar_formato(),
        width="100%",
    )


# ── BLOQUE 4: Imágenes del reporte ────────────────────────────────────────────
def _fila_imagen(row: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.text(row.orden.to(str), **_TD), **_TD),
        rx.table.cell(rx.text(row.nombre_archivo, **_TD, font_family="monospace"), **_TD),
        rx.table.cell(
            rx.text(row.celda, **_TD,
                    font_weight="600", color="var(--blue-9)", font_family="monospace"),
            **_TD,
        ),
        rx.table.cell(rx.text(row.ancho.to(str), **_TD), **_TD),
        rx.table.cell(rx.text(row.alto.to(str),  **_TD), **_TD),
        rx.table.cell(
            rx.hstack(
                rx.icon("pencil", size=13, cursor="pointer", color="var(--blue-9)",
                        on_click=ConfigReportesState.cr_iniciar_edicion_img(row.id)),
                rx.icon("trash_2", size=13, cursor="pointer", color="var(--red-9)",
                        on_click=ConfigReportesState.cr_confirmar_borrar(
                            "imagen", row.id, row.nombre_archivo)),
                spacing="2",
            ), **_TD,
        ),
        _hover={"background": "var(--gray-2)"},
    )


def _campos_imagen(
    archivo_val, set_archivo,
    celda_val,   set_celda,
    ancho_val,   set_ancho,
    alto_val,    set_alto,
    orden_val,   set_orden,
) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.text("Archivo *", font_size="11px", font_weight="500"),
                rx.select.root(
                    rx.select.trigger(width="200px"),
                    rx.select.content(
                        rx.foreach(
                            ConfigReportesState.cr_archivos_img,
                            lambda f: rx.select.item(f, value=f),
                        ),
                    ),
                    value=archivo_val, on_change=set_archivo, size="2",
                ),
                spacing="1",
            ),
            rx.vstack(
                rx.text("Celda anclaje *", font_size="11px", font_weight="500"),
                rx.input(value=celda_val, on_change=set_celda,
                         placeholder="ej. A1", size="2", width="80px",
                         style={"text_transform": "uppercase", "font_weight": "600",
                                "color": "var(--blue-9)"}),
                spacing="1",
            ),
            rx.vstack(
                rx.text("Orden", font_size="11px", font_weight="500"),
                rx.input(value=orden_val.to(str), on_change=set_orden,
                         type="number", size="2", width="70px"),
                spacing="1",
            ),
            spacing="3", align="end", flex_wrap="wrap",
        ),
        rx.hstack(
            rx.vstack(
                rx.text("Ancho (px)", font_size="11px", font_weight="500"),
                rx.input(value=ancho_val.to(str), on_change=set_ancho,
                         type="number", size="2", width="90px"),
                spacing="1",
            ),
            rx.vstack(
                rx.text("Alto (px)", font_size="11px", font_weight="500"),
                rx.input(value=alto_val.to(str), on_change=set_alto,
                         type="number", size="2", width="90px"),
                spacing="1",
            ),
            spacing="3", align="end",
        ),
        spacing="3", width="100%",
    )


def _dlg_nueva_imagen() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Nueva Imagen", font_size="14px"),
            rx.vstack(
                _campos_imagen(
                    ConfigReportesState.cr_ni_archivo, ConfigReportesState.set_cr_ni_archivo,
                    ConfigReportesState.cr_ni_celda,   ConfigReportesState.set_cr_ni_celda,
                    ConfigReportesState.cr_ni_ancho,   ConfigReportesState.set_cr_ni_ancho,
                    ConfigReportesState.cr_ni_alto,    ConfigReportesState.set_cr_ni_alto,
                    ConfigReportesState.cr_ni_orden,   ConfigReportesState.set_cr_ni_orden,
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray",
                                  size="2", type="button"),
                    ),
                    rx.button("Guardar", size="2", type="button",
                              on_click=ConfigReportesState.cr_crear_img),
                    justify="end", width="100%",
                ),
                spacing="3", width="100%", padding_top="8px",
            ),
            max_width="460px", width="95vw",
        ),
        open=ConfigReportesState.cr_dlg_nueva_img,
        on_open_change=ConfigReportesState.set_cr_dlg_nueva_img,
    )


def _dlg_editar_imagen() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Editar Imagen", font_size="14px"),
            rx.vstack(
                _campos_imagen(
                    ConfigReportesState.cr_ei_archivo, ConfigReportesState.set_cr_ei_archivo,
                    ConfigReportesState.cr_ei_celda,   ConfigReportesState.set_cr_ei_celda,
                    ConfigReportesState.cr_ei_ancho,   ConfigReportesState.set_cr_ei_ancho,
                    ConfigReportesState.cr_ei_alto,    ConfigReportesState.set_cr_ei_alto,
                    ConfigReportesState.cr_ei_orden,   ConfigReportesState.set_cr_ei_orden,
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray",
                                  size="2", type="button",
                                  on_click=ConfigReportesState.set_cr_dlg_edit_img(False)),
                    ),
                    rx.button("Guardar", size="2", type="button",
                              on_click=ConfigReportesState.cr_guardar_edicion_img),
                    justify="end", width="100%",
                ),
                spacing="3", width="100%", padding_top="8px",
            ),
            max_width="460px", width="95vw",
        ),
        open=ConfigReportesState.cr_dlg_edit_img,
        on_open_change=ConfigReportesState.set_cr_dlg_edit_img,
    )


def bloque4() -> rx.Component:
    return rx.box(
        _seccion_header(
            "Imágenes del Reporte",
            rx.button("+ Nueva Imagen", size="1", type="button",
                      on_click=ConfigReportesState.cr_abrir_dlg_nueva_img,
                      disabled=ConfigReportesState.cr_reporte_id == 0),
        ),
        rx.box(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Ord",      **_TH),
                        rx.table.column_header_cell("Archivo",  **_TH),
                        rx.table.column_header_cell("Celda",    **_TH),
                        rx.table.column_header_cell("Ancho",    **_TH),
                        rx.table.column_header_cell("Alto",     **_TH),
                        rx.table.column_header_cell("CRUD",     **_TH),
                        style=_HDR,
                    ),
                ),
                rx.table.body(
                    rx.foreach(ConfigReportesState.cr_imagenes, _fila_imagen),
                ),
                width="100%", size="1",
            ),
            overflow_y="auto", max_height="160px",
            border="1px solid var(--gray-4)", border_radius="4px",
        ),
        _dlg_nueva_imagen(),
        _dlg_editar_imagen(),
        width="100%",
    )


# ── Diálogo confirmación borrar (compartido) ───────────────────────────────────
def _dlg_confirmar_borrar() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.icon("triangle_alert", size=28, color="var(--red-9)"),
                rx.text("¿Eliminar registro?", font_size="14px", font_weight="600"),
                rx.text(ConfigReportesState.cr_borrar_nombre,
                        font_size="12px", color="var(--gray-10)",
                        text_align="center", max_width="260px"),
                rx.text("Esta acción no se puede deshacer.",
                        font_size="11px", color="var(--red-9)"),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray",
                                  size="2", type="button"),
                    ),
                    rx.button("Eliminar", color_scheme="red", size="2", type="button",
                              on_click=ConfigReportesState.cr_ejecutar_borrar),
                    spacing="3",
                ),
                align="center", spacing="3", padding="8px",
            ),
            max_width="320px", width="90vw",
        ),
        open=ConfigReportesState.cr_dlg_borrar,
        on_open_change=ConfigReportesState.set_cr_dlg_borrar,
    )


# ── Página principal ───────────────────────────────────────────────────────────
def _sin_permiso() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.icon("shield_x", size=40, color="var(--red-9)"),
            rx.text("Acceso denegado", font_size="16px", font_weight="600"),
            rx.text("No tienes permisos para acceder a esta sección.",
                    font_size="13px", color="var(--gray-10)"),
            rx.link(rx.button("← Volver", type="button"), href="/pacientes"),
            align="center", spacing="3",
        ),
        height="80vh",
    )


def config_reportes() -> rx.Component:
    return rx.cond(
        State.is_authenticated,
        rx.cond(
            State.puede_config_reportes,
            rx.box(
                _navbar(),
                rx.box(
                    rx.hstack(
                        # Columna izquierda — Bloques 1, 2 y 4
                        rx.vstack(
                            bloque1(),
                            rx.divider(margin_y="10px"),
                            bloque2(),
                            rx.divider(margin_y="10px"),
                            bloque4(),
                            spacing="0", width="100%",
                        ),
                        # Columna derecha — Bloque 3
                        rx.box(
                            bloque3(),
                            width="100%",
                        ),
                        spacing="6", align="start", width="100%",
                        flex_direction=rx.cond(True, "row", "column"),
                    ),
                    margin_top="58px",
                    padding="12px",
                ),
                _dlg_confirmar_borrar(),
                rx.toast.provider(),
            ),
            _sin_permiso(),
        ),
        rx.center(
            rx.vstack(
                rx.text("Sesión no iniciada", font_size="14px"),
                rx.link(rx.button("Ir al login", type="button"), href="/"),
                align="center", spacing="3",
            ),
            height="80vh",
        ),
    )
