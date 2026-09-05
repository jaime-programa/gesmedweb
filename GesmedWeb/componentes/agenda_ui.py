import reflex as rx
from ..state import State, AgendaState
from .calendario_fc import CalendarioMedico
from .colores import BOTON_IMPRIMIR

# ── Colores de estado ─────────────────────────────────────────────────────────
_ESTADO_COLOR = {
    "AGENDADA":    ("blue",   "Agendada"),
    "CONFIRMADA":  ("green",  "Confirmada"),
    "COMPLETADA":  ("gray",   "Completada"),
    "CANCELADA":   ("red",    "Cancelada"),
    "NO_ASISTIO":  ("orange", "No asistió"),
}


def _badge_estado(estado_var) -> rx.Component:
    return rx.match(
        estado_var,
        ("AGENDADA",   rx.badge("Agendada",   color_scheme="blue",   variant="soft")),
        ("CONFIRMADA", rx.badge("Confirmada", color_scheme="green",  variant="soft")),
        ("COMPLETADA", rx.badge("Completada", color_scheme="gray",   variant="soft")),
        ("NO_ASISTIO", rx.badge("No asistió", color_scheme="orange", variant="soft")),
        rx.badge(estado_var, color_scheme="gray", variant="soft"),
    )


# ── Diálogo: ver cita ─────────────────────────────────────────────────────────
def dialogo_ver_cita() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon("calendar-check", size=16, color="var(--blue-9)"),
                    rx.text("Detalle de Cita", font_size="15px", font_weight="600"),
                    spacing="2", align="center",
                ),
            ),
            # Cabecera: paciente + estado (siempre visible)
            rx.hstack(
                rx.vstack(
                    rx.text("Paciente", font_size="11px", color="var(--gray-9)"),
                    rx.text(AgendaState.ag_ver_px, font_size="13px", font_weight="600"),
                    spacing="0",
                ),
                rx.spacer(),
                _badge_estado(AgendaState.ag_ver_estado),
                align="center", width="100%",
            ),
            rx.divider(),
            # ── Modo lectura ──────────────────────────────────────────────────
            rx.cond(
                ~AgendaState.ag_ver_editando,
                rx.vstack(
                    rx.hstack(
                        rx.vstack(
                            rx.text("Médico", font_size="11px", color="var(--gray-9)"),
                            rx.text(AgendaState.ag_ver_medico, font_size="12px"),
                            spacing="0",
                        ),
                        rx.vstack(
                            rx.text("Tipo", font_size="11px", color="var(--gray-9)"),
                            rx.text(AgendaState.ag_ver_tipo, font_size="12px"),
                            spacing="0",
                        ),
                        spacing="6",
                    ),
                    rx.hstack(
                        rx.vstack(
                            rx.text("Inicio", font_size="11px", color="var(--gray-9)"),
                            rx.text(AgendaState.ag_ver_fecha_ini,
                                    font_size="12px", font_weight="500"),
                            rx.text(AgendaState.ag_ver_hora_ini,
                                    font_size="14px", font_weight="700",
                                    color="var(--blue-9)"),
                            spacing="0",
                        ),
                        rx.vstack(
                            rx.text("Fin", font_size="11px", color="var(--gray-9)"),
                            rx.text(AgendaState.ag_ver_fecha_fin,
                                    font_size="12px", font_weight="500"),
                            rx.text(AgendaState.ag_ver_hora_fin,
                                    font_size="14px", font_weight="700",
                                    color="var(--gray-9)"),
                            spacing="0",
                        ),
                        rx.cond(
                            AgendaState.ag_ver_duracion != "",
                            rx.vstack(
                                rx.text("Duración", font_size="11px", color="var(--gray-9)"),
                                rx.text(AgendaState.ag_ver_duracion,
                                        font_size="14px", font_weight="700",
                                        color="var(--gray-11)"),
                                spacing="0",
                            ),
                        ),
                        spacing="6",
                    ),
                    rx.cond(
                        AgendaState.ag_ver_notas != "",
                        rx.vstack(
                            rx.text("Notas", font_size="11px", color="var(--gray-9)"),
                            rx.text(AgendaState.ag_ver_notas, font_size="12px"),
                            spacing="1", width="100%",
                        ),
                    ),
                    # Botones modo lectura
                    rx.hstack(
                        rx.dialog.close(
                            rx.button("Cerrar", variant="soft", color_scheme="gray",
                                      size="2", type="button"),
                        ),
                        rx.cond(
                            AgendaState.ag_ver_req_conf & (AgendaState.ag_ver_estado == "AGENDADA"),
                            rx.button("✓ Confirmar", color_scheme="green", size="2",
                                      type="button",
                                      on_click=AgendaState.ag_confirmar_cita),
                        ),
                        rx.cond(
                            AgendaState.ag_ver_estado != "CANCELADA",
                            rx.button("✎ Editar", color_scheme="blue", variant="soft",
                                      size="2", type="button",
                                      on_click=AgendaState.ag_iniciar_edicion),
                        ),
                        rx.cond(
                            AgendaState.ag_ver_estado != "CANCELADA",
                            rx.button("✕ Cancelar cita", color_scheme="red",
                                      variant="soft", size="2", type="button",
                                      on_click=AgendaState.ag_cancelar_cita),
                        ),
                        spacing="2", justify="end", width="100%",
                    ),
                    spacing="3", width="100%",
                ),
            ),
            # ── Modo edición ──────────────────────────────────────────────────
            rx.cond(
                AgendaState.ag_ver_editando,
                rx.vstack(
                    # Médico
                    rx.vstack(
                        rx.text("Médico *", font_size="12px", font_weight="500"),
                        rx.select.root(
                            rx.select.trigger(placeholder="Seleccione médico",
                                              width="100%", size="2"),
                            rx.select.content(
                                rx.foreach(
                                    AgendaState.ag_medicos,
                                    lambda m: rx.select.item(m["nombre"],
                                                             value=m["id"].to(str)),
                                ),
                            ),
                            value=AgendaState.ag_ed_lk_medico.to(str),
                            on_change=AgendaState.set_ag_ed_lk_medico,
                            width="100%",
                        ),
                        spacing="1", width="100%",
                    ),
                    # Tipo de cita
                    rx.vstack(
                        rx.text("Tipo de cita *", font_size="12px", font_weight="500"),
                        rx.select.root(
                            rx.select.trigger(placeholder="Seleccione tipo",
                                              width="100%", size="2"),
                            rx.select.content(
                                rx.foreach(
                                    AgendaState.ag_tipos_cita,
                                    lambda t: rx.select.item(t["nombre"],
                                                             value=t["id"].to(str)),
                                ),
                            ),
                            value=AgendaState.ag_ed_lk_tipo.to(str),
                            on_change=AgendaState.set_ag_ed_lk_tipo,
                            width="100%",
                        ),
                        spacing="1", width="100%",
                    ),
                    # Notas
                    rx.vstack(
                        rx.text("Notas", font_size="12px", font_weight="500"),
                        rx.text_area(value=AgendaState.ag_ed_notas,
                                     on_change=AgendaState.set_ag_ed_notas,
                                     rows="3", size="2", width="100%"),
                        spacing="1", width="100%",
                    ),
                    # Error
                    rx.cond(
                        AgendaState.ag_ed_error != "",
                        rx.text(AgendaState.ag_ed_error, font_size="12px",
                                color="var(--red-9)"),
                    ),
                    # Botones modo edición
                    rx.hstack(
                        rx.button("Cancelar", variant="soft", color_scheme="gray",
                                  size="2", type="button",
                                  on_click=AgendaState.ag_cancelar_edicion),
                        rx.button("Guardar cambios", color_scheme="blue", size="2",
                                  type="button",
                                  on_click=AgendaState.ag_guardar_edicion_cita),
                        spacing="2", justify="end", width="100%",
                    ),
                    spacing="3", width="100%",
                ),
            ),
            max_width="460px", width="95vw",
        ),
        open=AgendaState.ag_dlg_ver,
        on_open_change=AgendaState.set_ag_dlg_ver,
    )


# ── Diálogo: nueva cita ───────────────────────────────────────────────────────
def dialogo_nueva_cita() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon("calendar-plus", size=16, color="var(--blue-9)"),
                    rx.text("Nueva Cita", font_size="15px", font_weight="600"),
                    spacing="2", align="center",
                ),
            ),
            rx.vstack(
                # Horario (solo lectura — viene del clic en el calendario)
                rx.hstack(
                    rx.vstack(
                        rx.text("Fecha", font_size="12px", font_weight="500"),
                        rx.input(value=AgendaState.ag_nc_fecha_ini, read_only=True,
                                 size="2", width="110px",
                                 style={"background": "var(--gray-2)"}),
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Hora", font_size="12px", font_weight="500"),
                        rx.input(value=AgendaState.ag_nc_hora_ini, read_only=True,
                                 size="2", width="80px",
                                 style={"background": "var(--gray-2)"}),
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Duración", font_size="12px", font_weight="500"),
                        rx.hstack(
                            rx.select.root(
                                rx.select.trigger(size="2", width="110px"),
                                rx.select.content(
                                    rx.select.item("15 min",  value="15"),
                                    rx.select.item("30 min",  value="30"),
                                    rx.select.item("45 min",  value="45"),
                                    rx.select.item("60 min",  value="60"),
                                ),
                                value=AgendaState.ag_nc_duracion.to(str),
                                on_change=AgendaState.set_ag_nc_duracion,
                            ),
                            rx.text(
                                AgendaState.ag_nc_duracion.to(str) + " min",
                                font_size="13px", font_weight="600",
                                color="var(--blue-9)",
                            ),
                            align="center", spacing="2",
                        ),
                        spacing="1",
                    ),
                    spacing="4", flex_wrap="wrap",
                ),
                # Médico
                rx.vstack(
                    rx.text("Médico *", font_size="12px", font_weight="500"),
                    rx.select.root(
                        rx.select.trigger(placeholder="Seleccione médico",
                                          width="100%", size="2"),
                        rx.select.content(
                            rx.foreach(
                                AgendaState.ag_medicos,
                                lambda m: rx.select.item(m["nombre"],
                                                         value=m["id"].to(str)),
                            ),
                        ),
                        on_change=AgendaState.set_ag_nc_lk_medico,
                        width="100%",
                    ),
                    spacing="1", width="100%",
                ),
                # Tipo de cita
                rx.vstack(
                    rx.text("Tipo de cita *", font_size="12px", font_weight="500"),
                    rx.select.root(
                        rx.select.trigger(placeholder="Seleccione tipo",
                                          width="100%", size="2"),
                        rx.select.content(
                            rx.foreach(
                                AgendaState.ag_tipos_cita,
                                lambda t: rx.select.item(t["nombre"],
                                                         value=t["id"].to(str)),
                            ),
                        ),
                        on_change=AgendaState.set_ag_nc_lk_tipo,
                        width="100%",
                    ),
                    spacing="1", width="100%",
                ),
                # Paciente: buscar existente o registrar nuevo
                rx.vstack(
                    rx.text("Paciente* (ya registrado)", font_size="12px", font_weight="500"),
                    rx.input(
                        placeholder="Buscar por nombre (mín. 3 letras)...",
                        value=AgendaState.ag_nc_busq_px,
                        on_change=AgendaState.set_ag_nc_busq_px,
                        size="2", width="100%",
                    ),
                    # Resultados de búsqueda
                    rx.cond(
                        AgendaState.ag_nc_resultados_px.length() > 0,
                        rx.vstack(
                            rx.foreach(
                                AgendaState.ag_nc_resultados_px,
                                lambda r: rx.button(
                                    r["nombre"],
                                    on_click=AgendaState.ag_seleccionar_paciente_existente(r["id"]),
                                    variant="ghost", size="1", width="100%",
                                    justify="start", type="button",
                                    style={"text_align": "left"},
                                ),
                            ),
                            border="1px solid var(--gray-4)",
                            border_radius="6px",
                            padding="4px",
                            width="100%",
                            max_height="140px",
                            overflow_y="auto",
                            background="white",
                        ),
                    ),
                    spacing="1", width="100%",
                ),
                # Formulario paciente nuevo (si no se seleccionó uno existente)
                rx.cond(
                    AgendaState.ag_nc_lk_paciente == 0,
                    rx.vstack(
                        rx.text("Datos del paciente nuevo",
                                font_size="12px", color="var(--green-9)",
                                font_weight="600"),
                        rx.hstack(
                            rx.vstack(
                                rx.text("Nombre completo *", font_size="11px"),
                                rx.input(value=AgendaState.ag_nc_px_nombre,
                                         on_change=AgendaState.set_ag_nc_px_nombre,
                                         size="2", width="100%"),
                                spacing="1", width="200px",
                            ),
                            rx.vstack(
                                rx.text("Sexo", font_size="11px"),
                                rx.select.root(
                                    rx.select.trigger(width="110px", size="2"),
                                    rx.select.content(
                                        rx.select.item("Femenino",  value="Femenino"),
                                        rx.select.item("Masculino", value="Masculino"),
                                    ),
                                    default_value="Femenino",
                                    on_change=AgendaState.set_ag_nc_px_sexo,
                                ),
                                spacing="1",
                            ),
                            spacing="3", flex_wrap="wrap",
                        ),
                        rx.hstack(
                            rx.vstack(
                                rx.text("Celular", font_size="11px"),
                                rx.input(value=AgendaState.ag_nc_px_celular,
                                         on_change=AgendaState.set_ag_nc_px_celular,
                                         size="2", width="130px"),
                                spacing="1",
                            ),
                            rx.vstack(
                                rx.text("Ciudad", font_size="11px"),
                                rx.input(value=AgendaState.ag_nc_px_ciudad,
                                         on_change=AgendaState.set_ag_nc_px_ciudad,
                                         size="2", width="130px"),
                                spacing="1",
                            ),
                            rx.vstack(
                                rx.text("Seguro", font_size="11px"),
                                rx.select.root(
                                    rx.select.trigger(
                                        placeholder="Sin seguro",
                                        width="120px", size="2",
                                    ),
                                    rx.select.content(
                                        rx.select.item("Sin seguro", value="__ninguno__"),
                                        rx.foreach(
                                            AgendaState.ag_seguros,
                                            lambda s: rx.select.item(s, value=s),
                                        ),
                                    ),
                                    value=AgendaState.ag_nc_px_seguro,
                                    on_change=AgendaState.set_ag_nc_px_seguro,
                                ),
                                spacing="1",
                            ),
                            spacing="3", flex_wrap="wrap",
                        ),
                        spacing="2",
                        padding="8px",
                        border="1px solid var(--gray-4)",
                        border_radius="6px",
                        width="100%",
                        background="var(--green-2)",
                    ),
                ),
                # Notas
                rx.vstack(
                    rx.text("Notas", font_size="12px", font_weight="500"),
                    rx.text_area(value=AgendaState.ag_nc_notas,
                                 on_change=AgendaState.set_ag_nc_notas,
                                 rows="2", size="2", width="100%"),
                    spacing="1", width="100%",
                ),
                # Error
                rx.cond(
                    AgendaState.ag_nc_error != "",
                    rx.text(AgendaState.ag_nc_error, font_size="12px",
                            color="var(--red-9)"),
                ),
                # Acciones
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray",
                                  size="2", type="button"),
                    ),
                    rx.button("Agendar Cita", color_scheme="blue", size="2",
                              type="button",
                              on_click=AgendaState.ag_guardar_nueva_cita),
                    spacing="2", justify="end", width="100%",
                ),
                spacing="3", width="100%",
            ),
            max_width="560px", width="96vw",
        ),
        open=AgendaState.ag_dlg_nueva,
        on_open_change=AgendaState.set_ag_dlg_nueva,
    )


# ── Offcanvas agenda (ancho completo) ─────────────────────────────────────────
def offcanvas_agenda() -> rx.Component:
    return rx.box(
        # ── Panel principal ────────────────────────────────────────────────────
        rx.box(
            # Cabecera
            rx.hstack(
                rx.hstack(
                    rx.icon("calendar-days", size=18, color="var(--blue-9)"),
                    rx.text("Agenda Médica", font_size="15px", font_weight="700"),
                    spacing="2", align="center",
                ),
                rx.spacer(),
                # Filtro por médico — checkboxes inline
                rx.flex(
                    rx.foreach(
                        AgendaState.ag_medicos,
                        lambda m: rx.hstack(
                            rx.checkbox(
                                checked=m["visible"],
                                on_change=AgendaState.ag_toggle_medico(m["id"]),
                                color_scheme="blue",
                            ),
                            rx.box(
                                width="9px", height="9px",
                                border_radius="50%",
                                background=m["color"],
                                flex_shrink="0",
                            ),
                            rx.text(m["nombre"], font_size="13px"),
                            spacing="1", align="center",
                        ),
                    ),
                    gap="3",
                    wrap="wrap",
                    align="center",
                ),
                rx.spacer(),
                # Botón cerrar
                rx.button(
                    rx.icon("x", size=18),
                    on_click=AgendaState.ag_cerrar,
                    variant="ghost", color_scheme="gray",
                    size="2", type="button", cursor="pointer",
                ),
                padding="8px 12px",
                width="100%",
                align="center",
                border_bottom="1px solid var(--gray-4)",
                background="white",
            ),
            # Calendario
            CalendarioMedico.create(
                eventos=AgendaState.ag_citas,
                vista="timeGridWeek",
                on_event_click=AgendaState.ag_handle_event_click,
                on_date_select=AgendaState.ag_handle_date_select,
                on_event_drop=AgendaState.ag_handle_event_drop,
            ),
            # Diálogos
            dialogo_ver_cita(),
            dialogo_nueva_cita(),
            position="fixed",
            top="60px",
            left="0",
            width="100vw",
            height="calc(100vh - 60px)",
            background="white",
            z_index="950",
            overflow="hidden",
            transform=rx.cond(
                AgendaState.ag_abierto,
                "translateX(0)",
                "translateX(100%)",
            ),
            transition="transform 0.3s ease",
        ),
    )
