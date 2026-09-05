import reflex as rx
from ..state import State, AdminUsuariosState

# ── Estilos ────────────────────────────────────────────────────────────────────
_TH = {"font_size": "11px", "font_weight": "600", "color": "var(--gray-11)",
       "padding": "6px 10px", "white_space": "nowrap"}
_TD = {"font_size": "12px", "padding": "6px 10px", "vertical_align": "middle"}

_ROL_COLOR = {
    "SECRETARIA":      "gray",
    "MEDICO_CONSULTA": "blue",
    "MEDICO_ATENCION": "green",
    "ADMIN":           "red",
}

_ROL_LABEL = {
    "SECRETARIA":      "Secretaria",
    "MEDICO_CONSULTA": "Médico (Lectura)",
    "MEDICO_ATENCION": "Médico (Completo)",
    "ADMIN":           "Administrador",
}

# ── Navbar ─────────────────────────────────────────────────────────────────────
def _navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.link(
                rx.button("← Volver", variant="ghost", size="1", type="button"),
                href="/pacientes",
            ),
            rx.text("Gestión de Usuarios",
                    font_size="15px", font_weight="700", color="var(--gray-12)"),
            rx.spacer(),
            rx.text(State.nombre_medico, font_size="11px", color="var(--gray-10)"),
            align="center", spacing="4", padding="0 16px", height="100%",
        ),
        position="fixed", top="0", left="0", right="0",
        height="50px", bg="white",
        border_bottom="1px solid var(--gray-5)", z_index="999",
    )


# ── Badge de rol ───────────────────────────────────────────────────────────────
def _rol_badge(rol: str) -> rx.Component:
    color = rx.match(
        rol,
        ("SECRETARIA",      "var(--gray-9)"),
        ("MEDICO_CONSULTA", "var(--blue-9)"),
        ("MEDICO_ATENCION", "var(--green-9)"),
        ("ADMIN",           "var(--red-9)"),
        "var(--gray-9)",
    )
    bg = rx.match(
        rol,
        ("SECRETARIA",      "var(--gray-3)"),
        ("MEDICO_CONSULTA", "var(--blue-3)"),
        ("MEDICO_ATENCION", "var(--green-3)"),
        ("ADMIN",           "var(--red-3)"),
        "var(--gray-3)",
    )
    label = rx.match(
        rol,
        ("SECRETARIA",      "Secretaria"),
        ("MEDICO_CONSULTA", "Médico (Lectura)"),
        ("MEDICO_ATENCION", "Médico (Completo)"),
        ("ADMIN",           "Administrador"),
        rol,
    )
    return rx.box(
        rx.text(label, font_size="10px", font_weight="600", color=color),
        bg=bg, border_radius="10px", padding="2px 8px",
        display="inline-block",
    )


# ── Fila de la tabla ───────────────────────────────────────────────────────────
def _fila_usuario(u: dict) -> rx.Component:
    _C = {"padding": "6px 10px"}  # estilo de celda (sin font_size para evitar conflictos)
    return rx.table.row(
        rx.table.cell(
            rx.text(u["nombre_medico"], font_size="12px", font_weight="500"),
            **_C,
        ),
        rx.table.cell(
            rx.text(u["usuario"], font_size="11px", color="var(--gray-10)",
                    font_family="monospace"),
            **_C,
        ),
        rx.table.cell(
            rx.text(u["especialidad"], font_size="11px", color="var(--gray-10)"),
            **_C,
        ),
        rx.table.cell(
            _rol_badge(u["rol"]),
            **_C,
        ),
        # Estado: botón toggle activo/inactivo
        rx.table.cell(
            rx.cond(
                u["estado"] == 1,
                rx.button(
                    rx.icon("circle-check", size=13),
                    "Activo",
                    on_click=AdminUsuariosState.au_toggle_estado(u["id_medico"]),
                    variant="soft", color_scheme="green", size="1", type="button",
                    cursor="pointer",
                ),
                rx.button(
                    rx.icon("circle-x", size=13),
                    "Inactivo",
                    on_click=AdminUsuariosState.au_toggle_estado(u["id_medico"]),
                    variant="soft", color_scheme="gray", size="1", type="button",
                    cursor="pointer",
                ),
            ),
            **_C,
        ),
        # Acciones
        rx.table.cell(
            rx.hstack(
                rx.icon("pencil", size=14, cursor="pointer", color="var(--blue-9)",
                        title="Editar usuario",
                        on_click=AdminUsuariosState.au_abrir_editar(u["id_medico"])),
                rx.icon("key-round", size=14, cursor="pointer", color="var(--amber-9)",
                        title="Resetear contraseña",
                        on_click=AdminUsuariosState.au_abrir_password(u["id_medico"])),
                spacing="3", align="center",
            ),
            **_C,
        ),
        style={"border_bottom": "1px solid var(--gray-4)", "_hover": {"bg": "var(--gray-1)"}},
    )


# ── Diálogo: Nuevo usuario ─────────────────────────────────────────────────────
def _campo(label: str, comp: rx.Component) -> rx.Component:
    return rx.vstack(
        rx.text(label, font_size="11px", font_weight="600", color="var(--gray-11)"),
        comp,
        spacing="1", width="100%",
    )


def _dlg_nuevo() -> rx.Component:
    _inp = lambda placeholder, value, on_change, **kw: rx.input(
        placeholder=placeholder, value=value, on_change=on_change,
        size="2", width="100%", **kw,
    )
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Nuevo Usuario", font_size="14px", font_weight="700"),
            rx.vstack(
                # Fila 1: Nombre + Especialidad
                rx.hstack(
                    _campo("Nombre completo *",
                           _inp("Nombre y apellido",
                                AdminUsuariosState.au_n_nombre,
                                AdminUsuariosState.set_au_n_nombre)),
                    _campo("Especialidad",
                           _inp("Especialidad",
                                AdminUsuariosState.au_n_especialidad,
                                AdminUsuariosState.set_au_n_especialidad)),
                    spacing="3", width="100%",
                ),
                # Fila 2: Cod. especialidad + Celular
                rx.hstack(
                    _campo("Cód. especialidad",
                           _inp("Ej. MED, OFT…",
                                AdminUsuariosState.au_n_cod_esp,
                                AdminUsuariosState.set_au_n_cod_esp)),
                    _campo("Celular",
                           _inp("0999…",
                                AdminUsuariosState.au_n_celular,
                                AdminUsuariosState.set_au_n_celular)),
                    spacing="3", width="100%",
                ),
                # Email
                _campo("Email",
                       _inp("correo@ejemplo.com",
                            AdminUsuariosState.au_n_email,
                            AdminUsuariosState.set_au_n_email, type="email")),
                rx.separator(width="100%"),
                # Fila 3: Usuario + Rol
                rx.hstack(
                    _campo("Nombre de usuario *",
                           _inp("login",
                                AdminUsuariosState.au_n_usuario,
                                AdminUsuariosState.set_au_n_usuario)),
                    _campo("Perfil *",
                           rx.select.root(
                               rx.select.trigger(width="100%"),
                               rx.select.content(
                                   rx.select.item("Secretaria",       value="SECRETARIA"),
                                   rx.select.item("Médico (Lectura)", value="MEDICO_CONSULTA"),
                                   rx.select.item("Médico (Completo)",value="MEDICO_ATENCION"),
                                   rx.select.item("Administrador",    value="ADMIN"),
                               ),
                               value=AdminUsuariosState.au_n_rol,
                               on_change=AdminUsuariosState.set_au_n_rol,
                               size="2",
                           )),
                    spacing="3", width="100%",
                ),
                # Fila 4: Contraseñas
                rx.hstack(
                    _campo("Contraseña *",
                           _inp("", AdminUsuariosState.au_n_clave,
                                AdminUsuariosState.set_au_n_clave, type="password")),
                    _campo("Confirmar contraseña *",
                           _inp("", AdminUsuariosState.au_n_clave2,
                                AdminUsuariosState.set_au_n_clave2, type="password")),
                    spacing="3", width="100%",
                ),
                # Error
                rx.cond(
                    AdminUsuariosState.au_error != "",
                    rx.text(AdminUsuariosState.au_error,
                            font_size="11px", color="var(--red-9)"),
                ),
                # Botones
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray",
                                  type="button", size="2",
                                  on_click=AdminUsuariosState.au_cancelar_nuevo),
                    ),
                    rx.spacer(),
                    rx.button("Crear Usuario", color_scheme="blue",
                              type="button", size="2",
                              on_click=AdminUsuariosState.au_crear),
                    width="100%",
                ),
                spacing="3", width="100%",
            ),
            max_width="600px",
        ),
        open=AdminUsuariosState.au_dlg_nuevo,
        on_open_change=AdminUsuariosState.set_au_dlg_nuevo,
    )


# ── Diálogo: Editar usuario ────────────────────────────────────────────────────
def _dlg_editar() -> rx.Component:
    _inp = lambda placeholder, value, on_change, **kw: rx.input(
        placeholder=placeholder, value=value, on_change=on_change,
        size="2", width="100%", **kw,
    )
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Editar Usuario", font_size="14px", font_weight="700"),
            rx.vstack(
                rx.hstack(
                    _campo("Nombre completo *",
                           _inp("Nombre y apellido",
                                AdminUsuariosState.au_e_nombre,
                                AdminUsuariosState.set_au_e_nombre)),
                    _campo("Especialidad",
                           _inp("Especialidad",
                                AdminUsuariosState.au_e_especialidad,
                                AdminUsuariosState.set_au_e_especialidad)),
                    spacing="3", width="100%",
                ),
                rx.hstack(
                    _campo("Cód. especialidad",
                           _inp("Ej. MED, OFT…",
                                AdminUsuariosState.au_e_cod_esp,
                                AdminUsuariosState.set_au_e_cod_esp)),
                    _campo("Celular",
                           _inp("0999…",
                                AdminUsuariosState.au_e_celular,
                                AdminUsuariosState.set_au_e_celular)),
                    spacing="3", width="100%",
                ),
                _campo("Email",
                       _inp("correo@ejemplo.com",
                            AdminUsuariosState.au_e_email,
                            AdminUsuariosState.set_au_e_email, type="email")),
                rx.separator(width="100%"),
                rx.hstack(
                    _campo("Nombre de usuario *",
                           _inp("login",
                                AdminUsuariosState.au_e_usuario,
                                AdminUsuariosState.set_au_e_usuario)),
                    _campo("Perfil *",
                           rx.select.root(
                               rx.select.trigger(width="100%"),
                               rx.select.content(
                                   rx.select.item("Secretaria",        value="SECRETARIA"),
                                   rx.select.item("Médico (Lectura)",  value="MEDICO_CONSULTA"),
                                   rx.select.item("Médico (Completo)", value="MEDICO_ATENCION"),
                                   rx.select.item("Administrador",     value="ADMIN"),
                               ),
                               value=AdminUsuariosState.au_e_rol,
                               on_change=AdminUsuariosState.set_au_e_rol,
                               size="2",
                           )),
                    spacing="3", width="100%",
                ),
                # Estado activo/inactivo en el form de edición
                rx.hstack(
                    rx.text("Estado:", font_size="12px", font_weight="600",
                            color="var(--gray-11)"),
                    rx.cond(
                        AdminUsuariosState.au_e_estado == 1,
                        rx.button(
                            rx.icon("circle-check", size=13), "Activo — clic para desactivar",
                            on_click=AdminUsuariosState.set_au_e_estado(0),
                            variant="soft", color_scheme="green", size="1", type="button",
                        ),
                        rx.button(
                            rx.icon("circle-x", size=13), "Inactivo — clic para activar",
                            on_click=AdminUsuariosState.set_au_e_estado(1),
                            variant="soft", color_scheme="gray", size="1", type="button",
                        ),
                    ),
                    spacing="2", align="center",
                ),
                rx.cond(
                    AdminUsuariosState.au_error != "",
                    rx.text(AdminUsuariosState.au_error,
                            font_size="11px", color="var(--red-9)"),
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray",
                                  type="button", size="2",
                                  on_click=AdminUsuariosState.au_cancelar_editar),
                    ),
                    rx.spacer(),
                    rx.button("Guardar Cambios", color_scheme="blue",
                              type="button", size="2",
                              on_click=AdminUsuariosState.au_guardar_edicion),
                    width="100%",
                ),
                spacing="3", width="100%",
            ),
            max_width="600px",
        ),
        open=AdminUsuariosState.au_dlg_editar,
        on_open_change=AdminUsuariosState.set_au_dlg_editar,
    )


# ── Diálogo: Resetear contraseña ──────────────────────────────────────────────
def _dlg_password() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Resetear Contraseña", font_size="14px", font_weight="700"),
            rx.vstack(
                rx.text(
                    "Usuario: ", rx.text.span(AdminUsuariosState.au_p_nombre,
                                              font_weight="600"),
                    font_size="12px", color="var(--gray-11)",
                ),
                _campo("Nueva contraseña (mínimo 6 caracteres) *",
                       rx.input(
                           value=AdminUsuariosState.au_p_clave,
                           on_change=AdminUsuariosState.set_au_p_clave,
                           type="password", size="2", width="100%",
                       )),
                _campo("Confirmar contraseña *",
                       rx.input(
                           value=AdminUsuariosState.au_p_clave2,
                           on_change=AdminUsuariosState.set_au_p_clave2,
                           type="password", size="2", width="100%",
                       )),
                rx.cond(
                    AdminUsuariosState.au_error != "",
                    rx.text(AdminUsuariosState.au_error,
                            font_size="11px", color="var(--red-9)"),
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray",
                                  type="button", size="2",
                                  on_click=AdminUsuariosState.au_cancelar_password),
                    ),
                    rx.spacer(),
                    rx.button("Guardar Contraseña", color_scheme="amber",
                              type="button", size="2",
                              on_click=AdminUsuariosState.au_guardar_password),
                    width="100%",
                ),
                spacing="3", width="100%",
            ),
            max_width="400px",
        ),
        open=AdminUsuariosState.au_dlg_password,
        on_open_change=AdminUsuariosState.set_au_dlg_password,
    )


# ── Página principal ───────────────────────────────────────────────────────────
def config_usuarios() -> rx.Component:
    return rx.cond(
        State.puede_admin,
        rx.box(
            _navbar(),
            # Diálogos
            _dlg_nuevo(),
            _dlg_editar(),
            _dlg_password(),
            # Toast de éxito
            rx.cond(
                AdminUsuariosState.au_ok != "",
                rx.box(
                    rx.hstack(
                        rx.icon("circle-check", size=14, color="var(--green-9)"),
                        rx.text(AdminUsuariosState.au_ok,
                                font_size="12px", color="var(--green-11)"),
                        rx.spacer(),
                        rx.icon("x", size=12, cursor="pointer",
                                on_click=AdminUsuariosState.au_cerrar_ok),
                        spacing="2", align="center", width="100%",
                    ),
                    bg="var(--green-2)", border="1px solid var(--green-6)",
                    border_radius="6px", padding="8px 12px",
                    position="fixed", bottom="20px", right="20px",
                    z_index="2000", min_width="280px",
                ),
            ),
            # Contenido
            rx.box(
                rx.vstack(
                    # Encabezado de sección + botón Nuevo
                    rx.hstack(
                        rx.text("Cuentas de Usuario", font_size="13px",
                                font_weight="600", color="var(--gray-12)"),
                        rx.spacer(),
                        rx.button(
                            rx.icon("user-plus", size=14),
                            "Nuevo Usuario",
                            on_click=AdminUsuariosState.au_abrir_nuevo,
                            color_scheme="blue", size="2", type="button",
                        ),
                        width="100%", align="center",
                    ),
                    # Tabla
                    rx.box(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Nombre", **_TH),
                                    rx.table.column_header_cell("Usuario", **_TH),
                                    rx.table.column_header_cell("Especialidad", **_TH),
                                    rx.table.column_header_cell("Perfil", **_TH),
                                    rx.table.column_header_cell("Estado", **_TH),
                                    rx.table.column_header_cell("Acciones", **_TH),
                                    style={"background": "var(--gray-2)",
                                           "border_bottom": "2px solid var(--gray-5)"},
                                ),
                            ),
                            rx.table.body(
                                rx.foreach(AdminUsuariosState.au_lista, _fila_usuario),
                            ),
                            width="100%",
                        ),
                        border="1px solid var(--gray-4)",
                        border_radius="8px",
                        overflow="hidden",
                        width="100%",
                    ),
                    spacing="4", width="100%",
                ),
                padding="70px 24px 40px 24px",
                max_width="1000px",
                margin="0 auto",
            ),
        ),
        # Guard: no es admin → redirect visual
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
