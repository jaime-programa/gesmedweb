import reflex as rx
from typing import Tuple,List
from ..state import State,PacienteState,EditPacienteState
from ..componentes.componentes import tabla_pacientes_con_encabezado
from ..componentes.dialogos import (
    dialogo_nuevo_paciente, dialogo_datos_paciente,
    dialogo_paciente_guardado, offcanvas_config,
)
from ..componentes.agenda_ui import offcanvas_agenda
from ..state import AgendaState


def _navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            # ── Botón ☰ izquierda ──────────────────────────────────────────
            rx.button(
                rx.icon("menu", size=18),
                on_click=State.toggle_offcanvas_config,
                type="button",
                variant="ghost",
                color_scheme="gray",
                size="2",
            ),
            rx.spacer(),
            # ── Logotipo centrado ──────────────────────────────────────────
            rx.image(
                src="/logotipo_original.png",
                height="44px",
                object_fit="contain",
            ),
            rx.spacer(),
            # ── Cerrar Sesión derecha ──────────────────────────────────────
            rx.button(
                "Cerrar Sesión",
                on_click=State.hacer_logout,
                type="button",
                color_scheme="red",
                variant="soft",
                size="2",
            ),
            width="100%",
            padding_x="12px",
            align="center",
            height="60px",
        ),
        position="fixed",
        top="0",
        left="0",
        right="0",
        height="60px",
        bg="white",
        border_bottom="1px solid var(--gray-4)",
        box_shadow="0 1px 4px rgba(0,0,0,0.06)",
        z_index="1000",
    )


def muestra_pacientes():
    return rx.cond(
        State.is_authenticated,
        rx.box(
            # ── Navbar fijo ────────────────────────────────────────────────
            _navbar(),
            # ── Offcanvas de configuración ─────────────────────────────────
            offcanvas_config(),
            # ── Offcanvas agenda (ancho completo) ──────────────────────────
            offcanvas_agenda(),
            # ── Contenido principal centrado ───────────────────────────────
            rx.center(
                rx.vstack(
                    # Controles
                    rx.hstack(
                        rx.input(
                            placeholder="Buscar paciente",
                            on_change=State.set_que_paciente_busco,
                            on_mouse_down=State.quita_seleccion_pacientes,
                            value=State.que_paciente_busco,
                            color_scheme='gray',
                        ),
                        rx.cond(
                            ~State.es_medico_lee,
                            rx.cond(
                                State.hay_paciente_seleccionado,
                                rx.button('Datos del Paciente', color_scheme='lime',
                                          on_click=EditPacienteState.abrir_datos_paciente),
                                rx.button('Datos del Paciente', disabled=True),
                            ),
                            rx.fragment(),
                        ),
                        rx.cond(
                            ~State.es_medico_lee,
                            rx.button(
                                "Nuevo Paciente",
                                color_scheme='indigo',
                                on_click=PacienteState.open_dialog,
                            ),
                            rx.fragment(),
                        ),
                        rx.cond(
                            State.hay_paciente_seleccionado,
                            rx.button('Historia Clínica', on_click=State.carga_atenciones),
                            rx.button('Historia Clínica', disabled=True),
                        ),
                        rx.button(
                            rx.icon("calendar-days", size=15),
                            "Agenda",
                            on_click=AgendaState.ag_abrir,
                            type="button",
                            color_scheme="blue",
                            variant="soft",
                        ),
                        spacing='4',
                        justify='start',
                    ),
                    # Tabla de pacientes
                    rx.box(
                        tabla_pacientes_con_encabezado(),
                        border="1px solid black",
                        padding="2px",
                        width="fit-content",
                        height="fit-content",
                    ),
                    dialogo_nuevo_paciente(),
                    dialogo_datos_paciente(),
                    dialogo_paciente_guardado(),
                    align="center",
                    spacing="4",
                ),
                padding_top="72px",
                padding_bottom="40px",
                min_height="100vh",
            ),
            # ── Barra de estado inferior ────────────────────────────────────
            rx.box(
                rx.text(
                    State.nombre_medico,
                    font_size="12px",
                    color="gray",
                ),
                position="fixed",
                bottom="0",
                left="0",
                right="0",
                padding_x="12px",
                padding_y="6px",
                border_top="1px solid #e2e8f0",
                bg="#f8fafc",
                z_index="100",
            ),
        ),
        # ── Vista no autenticada ───────────────────────────────────────────
        rx.center(
            rx.box(
                rx.vstack(
                    rx.text("Su sesión ha caducado!", font_size="20px", font_weight="bold"),
                    rx.link("Vuelva a Ingresar", href="/", color="blue", is_external=False),
                    spacing="4",
                    align="center",
                ),
                width="400px", height="200px", bg="#FAECA2",
                padding="20px", border_radius="10px", box_shadow="lg",
            ),
            height="100vh",
        ),
    )
