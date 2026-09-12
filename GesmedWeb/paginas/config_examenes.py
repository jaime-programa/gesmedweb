import reflex as rx
from ..state import State, ExamenesState

# ── Navbar ─────────────────────────────────────────────────────────────────────
def _navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.link(
                rx.button("← Volver", variant="ghost", size="1", type="button"),
                href="/config/usuarios",
            ),
            rx.text("Mantenimiento de Exámenes",
                    font_size="15px", font_weight="700", color="var(--gray-12)"),
            rx.spacer(),
            rx.text(State.nombre_medico, font_size="11px", color="var(--gray-10)"),
            align="center", spacing="4", padding="0 16px", height="100%",
        ),
        position="fixed", top="0", left="0", right="0",
        height="50px", bg="white",
        border_bottom="1px solid var(--gray-5)", z_index="999",
    )


# ── Fila: tipo de examen ─────────────────────────────────────────────────────
def _fila_tipo(t: dict) -> rx.Component:
    es_actual = ExamenesState.ex_tipo_sel == t["id_examen_tipo"]
    return rx.box(
        rx.hstack(
            rx.text(
                t["examen_tipo"], font_size="12px", font_weight="500",
                cursor="pointer",
                on_click=ExamenesState.ex_seleccionar_tipo(t["id_examen_tipo"]),
            ),
            rx.spacer(),
            rx.icon("pencil", size=14, cursor="pointer", color="var(--blue-9)",
                    title="Editar tipo",
                    on_click=ExamenesState.ex_abrir_editar_tipo(t["id_examen_tipo"])),
            rx.icon("trash-2", size=14, cursor="pointer", color="var(--red-9)",
                    title="Eliminar tipo",
                    on_click=ExamenesState.ex_eliminar_tipo(t["id_examen_tipo"])),
            spacing="3", align="center", width="100%",
        ),
        on_click=ExamenesState.ex_seleccionar_tipo(t["id_examen_tipo"]),
        padding="8px 10px",
        bg=rx.cond(es_actual, "var(--blue-3)", "transparent"),
        border_radius="6px",
        cursor="pointer",
        width="100%",
        style={"_hover": {"bg": rx.cond(es_actual, "var(--blue-3)", "var(--gray-2)")}},
    )


# ── Fila: catálogo de exámenes ────────────────────────────────────────────────
def _fila_catalogo(c: dict) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(c["examen_alias"], font_size="11px", font_weight="700",
                        color="var(--gray-11)", font_family="monospace"),
                rx.text(c["examen_nombre"], font_size="12px", font_weight="500"),
                spacing="0", align="start",
            ),
            rx.spacer(),
            rx.icon("pencil", size=14, cursor="pointer", color="var(--blue-9)",
                    title="Editar examen",
                    on_click=ExamenesState.ex_abrir_editar_catalogo(c["id_examen"])),
            rx.icon("trash-2", size=14, cursor="pointer", color="var(--red-9)",
                    title="Eliminar examen",
                    on_click=ExamenesState.ex_eliminar_catalogo(c["id_examen"])),
            spacing="3", align="center", width="100%",
        ),
        padding="8px 10px",
        border_radius="6px",
        width="100%",
        style={"_hover": {"bg": "var(--gray-2)"}},
    )


# ── Diálogo: tipo de examen ───────────────────────────────────────────────────
def _dlg_tipo() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(ExamenesState.ex_t_id != 0, "Editar Tipo de Examen", "Nuevo Tipo de Examen"),
                font_size="14px", font_weight="700",
            ),
            rx.vstack(
                rx.vstack(
                    rx.text("Nombre del tipo *", font_size="11px", font_weight="600",
                            color="var(--gray-11)"),
                    rx.input(
                        placeholder="Ej. Laboratorio, Imagen…",
                        value=ExamenesState.ex_t_nombre,
                        on_change=ExamenesState.set_ex_t_nombre,
                        max_length=40, size="2", width="100%",
                    ),
                    spacing="1", width="100%",
                ),
                rx.cond(
                    ExamenesState.ex_error != "",
                    rx.text(ExamenesState.ex_error, font_size="11px", color="var(--red-9)"),
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray",
                                  type="button", size="2",
                                  on_click=ExamenesState.ex_cancelar_tipo),
                    ),
                    rx.spacer(),
                    rx.button("Guardar", color_scheme="blue",
                              type="button", size="2",
                              on_click=ExamenesState.ex_guardar_tipo),
                    width="100%",
                ),
                spacing="3", width="100%",
            ),
            max_width="380px",
        ),
        open=ExamenesState.ex_dlg_tipo,
        on_open_change=ExamenesState.set_ex_dlg_tipo,
    )


# ── Diálogo: examen de catálogo ───────────────────────────────────────────────
def _dlg_catalogo() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(ExamenesState.ex_c_id != 0, "Editar Examen", "Nuevo Examen"),
                font_size="14px", font_weight="700",
            ),
            rx.vstack(
                rx.vstack(
                    rx.text("Alias (máx. 6 caracteres) *", font_size="11px", font_weight="600",
                            color="var(--gray-11)"),
                    rx.input(
                        placeholder="Ej. HB",
                        value=ExamenesState.ex_c_alias,
                        on_change=ExamenesState.set_ex_c_alias,
                        max_length=6, size="2", width="100%",
                        style={"text_transform": "uppercase"},
                    ),
                    spacing="1", width="100%",
                ),
                rx.vstack(
                    rx.text("Nombre del examen *", font_size="11px", font_weight="600",
                            color="var(--gray-11)"),
                    rx.input(
                        placeholder="Ej. HEMOGLOBINA",
                        value=ExamenesState.ex_c_nombre,
                        on_change=ExamenesState.set_ex_c_nombre,
                        max_length=40, size="2", width="100%",
                        style={"text_transform": "uppercase"},
                    ),
                    spacing="1", width="100%",
                ),
                rx.cond(
                    ExamenesState.ex_error != "",
                    rx.text(ExamenesState.ex_error, font_size="11px", color="var(--red-9)"),
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray",
                                  type="button", size="2",
                                  on_click=ExamenesState.ex_cancelar_catalogo),
                    ),
                    rx.spacer(),
                    rx.button("Guardar", color_scheme="blue",
                              type="button", size="2",
                              on_click=ExamenesState.ex_guardar_catalogo),
                    width="100%",
                ),
                spacing="3", width="100%",
            ),
            max_width="380px",
        ),
        open=ExamenesState.ex_dlg_catalogo,
        on_open_change=ExamenesState.set_ex_dlg_catalogo,
    )


# ── Bloque izquierdo: tipos de examen ─────────────────────────────────────────
def _bloque_tipos() -> rx.Component:
    return rx.vstack(
        rx.text("Tipos de Examen", font_size="13px", font_weight="600",
                color="var(--gray-12)"),
        rx.box(
            rx.vstack(
                rx.foreach(ExamenesState.ex_tipos, _fila_tipo),
                spacing="1", width="100%",
            ),
            border="1px solid var(--gray-4)", border_radius="8px",
            padding="8px", width="100%", min_height="300px",
        ),
        rx.button(
            rx.icon("plus", size=14), "Agregar",
            on_click=ExamenesState.ex_abrir_nuevo_tipo,
            variant="soft", color_scheme="blue", size="2", type="button",
            width="100%",
        ),
        spacing="3", width="100%",
    )


# ── Bloque derecho: catálogo de exámenes ──────────────────────────────────────
def _bloque_catalogo() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text("Catálogo de Exámenes", font_size="13px", font_weight="600",
                    color="var(--gray-12)"),
            rx.cond(
                ExamenesState.ex_tipo_sel_nombre != "",
                rx.badge(ExamenesState.ex_tipo_sel_nombre, color_scheme="blue"),
            ),
            spacing="2", align="center",
        ),
        rx.box(
            rx.cond(
                ExamenesState.ex_tipo_sel != 0,
                rx.vstack(
                    rx.foreach(ExamenesState.ex_catalogo, _fila_catalogo),
                    spacing="1", width="100%",
                ),
                rx.center(
                    rx.text("Seleccione un tipo de examen a la izquierda.",
                            font_size="12px", color="var(--gray-9)"),
                    padding="20px",
                ),
            ),
            border="1px solid var(--gray-4)", border_radius="8px",
            padding="8px", width="100%", min_height="300px",
        ),
        rx.button(
            rx.icon("plus", size=14), "Agregar",
            on_click=ExamenesState.ex_abrir_nuevo_catalogo,
            variant="soft", color_scheme="blue", size="2", type="button",
            width="100%",
            disabled=ExamenesState.ex_tipo_sel == 0,
        ),
        spacing="3", width="100%",
    )


# ── Página principal ───────────────────────────────────────────────────────────
def config_examenes() -> rx.Component:
    return rx.cond(
        State.puede_admin,
        rx.box(
            _navbar(),
            _dlg_tipo(),
            _dlg_catalogo(),
            rx.cond(
                ExamenesState.ex_ok != "",
                rx.box(
                    rx.hstack(
                        rx.icon("circle-check", size=14, color="var(--green-9)"),
                        rx.text(ExamenesState.ex_ok, font_size="12px", color="var(--green-11)"),
                        rx.spacer(),
                        rx.icon("x", size=12, cursor="pointer",
                                on_click=ExamenesState.ex_cerrar_ok),
                        spacing="2", align="center", width="100%",
                    ),
                    bg="var(--green-2)", border="1px solid var(--green-6)",
                    border_radius="6px", padding="8px 12px",
                    position="fixed", bottom="20px", right="20px",
                    z_index="2000", min_width="280px",
                ),
            ),
            rx.box(
                rx.hstack(
                    _bloque_tipos(),
                    _bloque_catalogo(),
                    spacing="5", align="start", width="100%",
                ),
                padding="70px 24px 40px 24px",
                max_width="900px",
                margin="0 auto",
            ),
        ),
        rx.center(
            rx.vstack(
                rx.icon("shield-x", size=40, color="var(--red-9)"),
                rx.text("Acceso restringido", font_size="16px", font_weight="700"),
                rx.text("Esta sección es solo para administradores.",
                        font_size="13px", color="var(--gray-10)"),
                rx.link(rx.button("← Volver", variant="soft"), href="/pacientes"),
                spacing="3", align="center",
            ),
            height="100vh",
        ),
    )
