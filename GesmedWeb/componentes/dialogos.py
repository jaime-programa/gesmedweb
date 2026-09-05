import reflex as rx
from ..state import State, AtencionState, PacienteState, EditPacienteState, NuevoDiagnosticoState, PrescripcionState, PedidoExamenesState, NuevoAntFamiliarState, NuevaAlergiaState, CertificadoState, OtrosPedidoState, LaboratorioState, MantenimientoMedState
from .resultados_ui import panel_resultados_examenes, upload_resultados_titulo
from .colores import (
    BOTON_PRIMARIO, BOTON_SECUNDARIO, BOTON_ACCION, BOTON_DESHABILITADO, BOTON_DESHABILITADO_TEXTO,BOTON_IMPRIMIR,
    TABLE_HEADER_BG_BLUE,TABLE_HEADER_BG_GREEN,TABLE_HEADER_BG_PETROLEO, TABLE_HEADER_COLOR, ROW_HOVER_BG,TABLA_SECUNDARIA_ENCABEZADO,TABLA_SECUNDARIA_TEXTO_ENCABEZADO,PRESCRIPCION_ENCABEZADO
)

def _fila_sv(item: dict) -> rx.Component:
    """Columna compacta para la fila inline de signos vitales estándar."""
    return rx.vstack(
        rx.text(item["nombre"], font_size="10px", font_weight="500"),
        rx.text(item["unidad"], font_size="9px", color="gray"),
        rx.input(
            value=item["valor_actual"],
            placeholder=item["codigo"],
            height="20px",
            width="55px",
            variant="soft",
            font_size="11px",
            align="center",
            disabled=AtencionState.soap_campos_bloqueados,
            on_change=AtencionState.set_sv_valor(item["id_signo_vital"]),
        ),
        spacing="0",
        align="center",
    )


def _fila_sv_dialog(item: dict) -> rx.Component:
    """Fila horizontal para el diálogo de signos vitales adicionales."""
    return rx.hstack(
        rx.text(item["nombre"], width="160px", font_size="13px"),
        rx.input(
            value=item["valor_actual"],
            placeholder="—",
            width="90px",
            variant="soft",
            font_size="13px",
            on_change=AtencionState.set_sv_valor(item["id_signo_vital"]),
        ),
        rx.text(item["unidad"], font_size="12px", color="gray", min_width="32px"),
        align="center",
        width="100%",
    )


def dialogo_advertencia_salir():
    """Advertencia cuando el médico intenta salir con un SOAP en edición sin guardar."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Cambios sin guardar"),
            rx.text(
                "El SOAP está en modo edición y los cambios aún no han sido guardados. "
                "¿Desea salir y descartar los cambios?",
                size="2",
                margin_bottom="16px",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancelar",
                        type="button",
                        variant="soft",
                        color_scheme="gray",
                    ),
                ),
                rx.button(
                    "Salir sin guardar",
                    type="button",
                    color_scheme="red",
                    on_click=AtencionState.confirmar_salir,
                ),
                spacing="3",
                justify="end",
            ),
            max_width="400px",
        ),
        open=AtencionState.soap_dialogo_salir,
        on_open_change=AtencionState.set_soap_dialogo_salir,
    )


def dialogo_otros_sv():
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Otros Signos Vitales"),
            rx.dialog.description(
                "Registre valores adicionales si aplica.",
                size="2",
                margin_bottom="12px",
                color="gray",
            ),
            rx.vstack(
                rx.foreach(AtencionState.sv_otros, _fila_sv_dialog),
                spacing="3",
                width="100%",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Cerrar", variant="soft", color_scheme="gray"),
                ),
                justify="end",
                margin_top="16px",
            ),
            max_width="420px",
        ),
        open=AtencionState.sv_otros_dialog_open,
        on_open_change=AtencionState.set_sv_otros_dialog_open,
    )


def form_atencion_actual():
    return rx.form(
            rx.hstack(
                    rx.text("📕 SOAP", font_weight="bold", font_size="1.4em"),
                    rx.spacer(),
                    # Botón Vincular Diagnóstico — visible solo cuando el SOAP está grabado
                    rx.cond(
                        AtencionState.vincular_visible,
                        rx.button(
                            "🧬 Vincular Diagnóstico",
                            bg=BOTON_PRIMARIO,
                            color="white",
                            on_click=AtencionState.abrir_vincular_diagnostico,
                            type="button",
                            border="none",
                            font_size="0.75em",
                            cursor="pointer",
                        ),
                        rx.box(),  # oculto hasta que el SOAP se grabe
                    ),
                    # Botón imprimir form002 — visible solo cuando el SOAP está grabado
                    rx.cond(
                        AtencionState.soap_grabado,
                        rx.link(
                            rx.button(
                                "🖨️ Imprimir",
                                type="button",
                                bg=BOTON_IMPRIMIR,
                                color="white",
                                font_size="0.75em",
                                border="none",
                                cursor="pointer",
                                title="Imprimir Historia Clínica (Form002)",
                            ),
                            href=AtencionState.url_reporte_form002,
                            is_external=True,
                        ),
                        rx.box(),
                    ),
                    rx.cond(
                        AtencionState.soap_campos_bloqueados,
                        # ── Modo grabado: ofrecer edición ──────────────────────
                        rx.button(
                            "✏️ Editar SOAP",
                            type="button",
                            on_click=AtencionState.activar_edicion_soap,
                            bg=BOTON_ACCION,
                            color="white",
                            font_size="0.75em",
                            border="none",
                            cursor="pointer",
                        ),
                        rx.cond(
                            AtencionState.soap_modo_edicion,
                            # ── Modo edición: guardar cambios ──────────────────
                            rx.button(
                                "💾 Guardar Cambios",
                                disabled=AtencionState.soap_campos_incompletos,
                                type="button",
                                on_click=AtencionState.guardar_cambios_soap,
                                bg=rx.cond(AtencionState.soap_campos_incompletos, BOTON_DESHABILITADO, BOTON_SECUNDARIO),
                                color=rx.cond(AtencionState.soap_campos_incompletos, BOTON_DESHABILITADO_TEXTO, "white"),
                                font_size="0.75em",
                                border="none",
                            ),
                            # ── Modo nuevo: grabar por primera vez ─────────────
                            rx.button(
                                "💾 Grabar SOAP",
                                disabled=AtencionState.no_puede_grabar_soap,
                                type="button",
                                on_click=AtencionState.submit_soap,
                                bg=rx.cond(AtencionState.no_puede_grabar_soap, BOTON_DESHABILITADO, BOTON_SECUNDARIO),
                                color=rx.cond(AtencionState.no_puede_grabar_soap, BOTON_DESHABILITADO_TEXTO, "white"),
                                font_size="0.75em",
                                border="none",
                            ),
                        ),
                    ),
                ),
            # Aviso obligatorio cuando el médico cancela el diálogo de vincular
            rx.cond(
                AtencionState.soap_vincular_msg,
                rx.hstack(
                    rx.icon("triangle_alert", size=13, color="var(--red-9)"),
                    rx.text(
                        "Es obligatorio vincular un diagnóstico a la atención antes de grabar.",
                        font_size="11px",
                        color="var(--red-9)",
                    ),
                    padding="6px 10px",
                    background="var(--red-2)",
                    border="1px solid var(--red-6)",
                    border_radius="6px",
                    width="100%",
                    align="center",
                    spacing="2",
                ),
                rx.box(),
            ),
            rx.divider(),                                 
            rx.scroll_area(     #Antes scroll_area
                rx.text("Motivo de Consulta (*)", font_weight="500"),
                rx.text_area(value=AtencionState.soap_motivo,placeholder="Motivo de Consulta",height="80px",disabled=AtencionState.soap_campos_bloqueados,on_change=AtencionState.set_soap_motivo),
                rx.text("Revisión de Sistemas", font_weight="500"),
                rx.text_area(value=AtencionState.soap_revision,placeholder="Revisión de Sistemas",height="80px",disabled=AtencionState.soap_campos_bloqueados,on_change=AtencionState.set_soap_revision),
                rx.text("Subjetivo (*)", font_weight="500"),
                rx.text_area(value=AtencionState.soap_subjetivo,placeholder="Subjetivo",height="80px",disabled=AtencionState.soap_campos_bloqueados,on_change=AtencionState.set_soap_subjetivo),
                rx.text("Objetivo", font_weight="500"),
                rx.hstack(
                    rx.foreach(AtencionState.sv_standard, _fila_sv),
                    rx.cond(
                        AtencionState.sv_hay_otros_tipos,
                        rx.button(
                            "Otros SV",
                            size="1",
                            variant="outline",
                            color_scheme="gray",
                            on_click=AtencionState.abrir_sv_otros_dialog,
                            disabled=AtencionState.soap_campos_bloqueados,
                            font_size="10px",
                            cursor="pointer",
                        ),
                    ),
                    flex_wrap="wrap",
                    align="end",
                    spacing="2",
                    margin="4px",
                ),
                rx.cond(
                    AtencionState.sv_hay_otros_valores,
                    rx.text(
                        "Otros: " + AtencionState.sv_otros_texto,
                        font_size="11px",
                        color="gray",
                        padding_x="4px",
                        padding_bottom="2px",
                    ),
                ),
                rx.text_area(value=AtencionState.soap_objetivo,placeholder="Objetivo",height="80px",disabled=AtencionState.soap_campos_bloqueados,on_change=AtencionState.set_soap_objetivo),
                rx.text("Análisis", font_weight="500"),
                rx.text_area(value=AtencionState.soap_analisis,placeholder="Análisis",height="80px",disabled=AtencionState.soap_campos_bloqueados,on_change=AtencionState.set_soap_analisis),
                rx.text("Plan (*)", font_weight="500"),
                rx.text_area(value=AtencionState.soap_plan,placeholder="Plan",height="80px",disabled=AtencionState.soap_campos_bloqueados,on_change=AtencionState.set_soap_plan),
                #Contenedor del SOAP
                height="77vh",
                background_color="white",
                overflow_y="scroll",
                style=rx.cond(
                    AtencionState.soap_campos_bloqueados,
                    {"opacity": "0.55", "pointer_events": "none", "user_select": "none"},
                    {"opacity": "1"},
                ),
                ),
        ),

def offcanvas_atencion():
    """Simula el componente Offcanvas de Bootstrap con Reflex."""
    return rx.box(
        # Overlay oscuro (aparece cuando el panel está abierto)
        rx.cond(
            AtencionState.offcanvas_atencion_actual,
            rx.box(
                position="fixed",
                top="0",
                left="0",
                width="100%",
                height="100%",
                bg="rgba(0,0,0,0.2)",
                z_index="98",
                transition="opacity 0.3s ease-in-out",
            )
        ),

        # Panel lateral derecho (offcanvas)
        rx.box(
            rx.vstack(
                form_atencion_actual(),
            ),
            dialogo_otros_sv(),
            position="fixed",
            top="65px",
            right="10px",
            height="calc(96% - 65px)",
            #Ancho offcanvas_atencion
            width=rx.cond(State.show_panel_izq, "55vw", "96vw"),
            bg="white",
            box_shadow="-2px 0 10px rgba(0,0,0,0.3)",
            z_index=rx.cond(AtencionState.offcanvas_atencion_actual, "101", "99"),
            padding="0.5em",
            transform=rx.cond(
                AtencionState.offcanvas_atencion_actual,
                "translateX(0)",
                "translateX(100%)",
            ),
            transition="transform 0.3s ease-in-out, width 0.3s ease-in-out",
        ),
    )

# ═══════════════════════════════════════════════════════════════════════════════
# PRESCRIPCIÓN — componentes compartidos
# ═══════════════════════════════════════════════════════════════════════════════

_PX_M = {"padding": "3px 6px", "font_size": "11px",
         "background": PRESCRIPCION_ENCABEZADO, "color": "black", "white_space": "nowrap"}
_PX_H= {"padding": "3px 6px", "font_size": "11px",
         "background": TABLE_HEADER_BG_GREEN, "color": TABLE_HEADER_COLOR, "white_space": "nowrap"}
_PX_C = {"padding": "4px 6px", "font_size": "12px", "vertical_align": "top"}


def _px_alergias() -> rx.Component:
    """Banda informativa de alergias conocidas del paciente."""
    return rx.cond(
        PrescripcionState.px_lista_alergias.length() > 0,
        rx.hstack(
            rx.icon("triangle_alert", size=14, color="var(--orange-9)"),
            rx.text("Alergias:", font_size="11px", font_weight="600", color="var(--orange-10)"),
            rx.foreach(
                PrescripcionState.px_lista_alergias,
                lambda a: rx.badge(a["sustancia_alergia"], color_scheme="orange", variant="soft", size="1"),
            ),
            padding="6px 10px",
            background="var(--orange-2)",
            border_radius="6px",
            border="1px solid var(--orange-6)",
            width="100%",
            flex_wrap="wrap",
            gap="4px",
            align="center",
        ),
        rx.hstack(
            rx.icon("circle_check", size=14, color="var(--green-9)"),
            rx.text("Sin alergias registradas.", font_size="11px", color="var(--green-10)"),
            padding="6px 10px",
            background="var(--green-2)",
            border_radius="6px",
            width="100%",
            align="center",
        ),
    )


def _px_buscador() -> rx.Component:
    """Buscador de medicamentos del catálogo (solo en modo edición)."""
    return rx.vstack(
        rx.hstack(
            rx.input(
                placeholder="Filtrar medicamento...",
                value=PrescripcionState.px_filtro_med,
                on_change=PrescripcionState.set_px_filtro_med,
                size="2",
                flex="1",
            ),
            rx.select(
                ["Todos", "Catálogo Base", "Añadidos en consulta","Accesorios y Equipos"],
                value=PrescripcionState.px_filtro_tipo_nombre,
                on_change=PrescripcionState.set_px_filtro_tipo_nombre,
                size="2",
                width="170px",
            ),
            width="60%",
            spacing="2",
        ),
        rx.scroll_area(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Medicamento genérico", style=_PX_M),
                        rx.table.column_header_cell("Comercial", style=_PX_M),
                        rx.table.column_header_cell("Tipo", style=_PX_M),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        PrescripcionState.px_lista_medicamentos,
                        lambda m: rx.table.row(
                            rx.table.cell(m["nombre_generico"], style={**_PX_C, "cursor": "pointer"}),
                            rx.table.cell(m["nombre_comercial"], style={**_PX_C, "cursor": "pointer"}),
                            rx.table.cell(m["nombre_tipo"],      style={**_PX_C, "cursor": "pointer"}),
                            on_click=PrescripcionState.seleccionar_medicamento(
                                m["cod_gen"], m["nombre_generico"]
                            ),
                            _hover={"background": ROW_HOVER_BG},
                        )
                    )
                ),
                width="100%",
                style={"border_collapse": "collapse"},
            ),
            height="155px",
            scrollbars="vertical",
            border="1px solid var(--gray-5)",
            border_radius="6px",
        ),
        rx.cond(
            PrescripcionState.px_med_cod > 0,
            rx.hstack(
                rx.icon("pill", size=18, color="var(--green-9)"),
                rx.badge(PrescripcionState.px_med_nombre, color_scheme="grass", size="3", variant="solid"),
                rx.icon_button(
                    rx.icon("x", size=12),
                    size="1", variant="ghost", color_scheme="gray",
                    on_click=PrescripcionState.deseleccionar_medicamento,
                    title="Quitar selección",
                ),
                align="center", spacing="2",
            ),
        ),
        spacing="2",
        width="100%",
    )


def _px_form_nuevo_item() -> rx.Component:
    """Formulario para completar y añadir un ítem (visible solo si hay medicamento seleccionado)."""
    return rx.cond(
        PrescripcionState.px_med_cod > 0,
        rx.box(
            rx.vstack(
                rx.grid(
                    rx.vstack(
                        rx.text("Concentración *", font_size="11px", font_weight="500", color="var(--gray-11)"),
                        rx.input(
                            placeholder="Ej: 500 mg",
                            value=PrescripcionState.px_concentracion,
                            on_change=PrescripcionState.set_px_concentracion,
                            size="2", width="100%",
                        ),
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Cantidad *", font_size="11px", font_weight="500", color="var(--gray-11)"),
                        rx.input(
                            placeholder="1",
                            value=PrescripcionState.px_cantidad,
                            on_change=PrescripcionState.set_px_cantidad,
                            type="number", min="1", size="2", width="80px",
                        ),
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Presentación", font_size="11px", font_weight="500", color="var(--gray-11)"),
                        rx.select(
                            PrescripcionState.px_presentaciones_select,
                            placeholder="Opcional...",
                            value=PrescripcionState.px_nombre_presentacion_sel,
                            on_change=PrescripcionState.set_px_lk_presentacion_por_nombre,
                            size="2", width="100%",
                        ),
                        spacing="1",
                    ),
                    columns="3", gap="3", width="100%",
                ),
                rx.vstack(
                    rx.text("Indicaciones *", font_size="11px", font_weight="500", color="var(--gray-11)"),
                    rx.text_area(
                        placeholder="Posología e indicaciones...",
                        value=PrescripcionState.px_indicaciones,
                        on_change=PrescripcionState.set_px_indicaciones,
                        rows="2", size="2", width="100%", resize="none",
                    ),
                    spacing="1", width="100%",
                ),
                rx.hstack(
                    rx.cond(
                        PrescripcionState.px_form_error != "",
                        rx.text(PrescripcionState.px_form_error, font_size="11px", color="var(--red-9)"),
                        rx.text(""),
                    ),
                    rx.spacer(),
                    rx.button(
                        "+ Añadir al catálogo",
                        variant="ghost", size="1", color_scheme="gray",
                        on_click=PrescripcionState.abrir_dlg_nuevo_med,
                    ),
                    rx.button(
                        rx.icon("plus", size=13), " Agregar",
                        size="2", color_scheme="green",
                        on_click=PrescripcionState.agregar_item,
                        disabled=~PrescripcionState.px_puede_agregar,
                    ),
                    width="100%", align="center", spacing="2",
                ),
                spacing="2", width="100%",
            ),
            border="1px solid var(--blue-5)",
            border_radius="6px",
            padding="10px",
            background="var(--blue-1)",
        ),
    )


def _px_tabla_items() -> rx.Component:
    """Tabla de ítems recetados con acciones condicionales."""
    return rx.cond(
        PrescripcionState.px_tiene_items,
        rx.box(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Medicamento", style=_PX_H),
                        rx.table.column_header_cell("Concentración", style=_PX_H),
                        rx.table.column_header_cell("Cant.", style={**_PX_H, "width": "45px"}),
                        rx.table.column_header_cell("Presentación", style=_PX_H),
                        rx.table.column_header_cell("Indicaciones", style=_PX_H),
                        rx.table.column_header_cell("", style={**_PX_H, "width": "52px"}),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        PrescripcionState.px_lista_items,
                        lambda item: rx.table.row(
                            rx.table.cell(
                                rx.text(item["nombre_generico"], font_weight="500", font_size="12px"),
                                style=_PX_C,
                            ),
                            rx.table.cell(item["concentracion"], style=_PX_C),
                            rx.table.cell(item["cantidad"], style=_PX_C),
                            rx.table.cell(item["nombre_presentacion"], style=_PX_C),
                            rx.table.cell(
                                rx.text(item["indicaciones"], white_space="pre-wrap", font_size="12px"),
                                style={**_PX_C, "max_width": "220px"},
                            ),
                            rx.table.cell(
                                rx.cond(
                                    PrescripcionState.px_puede_modificar,
                                    rx.hstack(
                                        rx.icon_button(
                                            rx.icon("pencil", size=12),
                                            size="1", variant="ghost", color_scheme="blue",
                                            on_click=PrescripcionState.abrir_dlg_editar(item["id_prescripcion"]),
                                            title="Editar",
                                        ),
                                        rx.icon_button(
                                            rx.icon("trash_2", size=12),
                                            size="1", variant="ghost", color_scheme="red",
                                            on_click=PrescripcionState.eliminar_item(item["id_prescripcion"]),
                                            title="Eliminar",
                                        ),
                                        spacing="1",
                                    ),
                                    rx.text(""),
                                ),
                                style=_PX_C,
                            ),
                            _hover={"background": ROW_HOVER_BG},
                        )
                    )
                ),
                width="100%",
                style={"border_collapse": "collapse"},
            ),
            border="1px solid var(--gray-5)",
            border_radius="6px",
            overflow_x="auto",
        ),
        rx.box(
            rx.text(
                "Sin medicamentos recetados.",
                font_size="12px", color="var(--gray-10)",
                font_style="italic", text_align="center",
            ),
            padding="14px", width="100%",
        ),
    )


def _px_cuidados() -> rx.Component:
    """Sección de cuidados generales."""
    return rx.vstack(
        rx.text_area(
            placeholder="Cuidados generales para el paciente...",
            value=PrescripcionState.px_cuidados_generales,
            on_change=PrescripcionState.set_px_cuidados_generales,
            rows="3", size="2", width="100%", resize="vertical",
            disabled=PrescripcionState.px_no_puede_modificar,
        ),
        spacing="2", width="100%",
    )


def _prescripcion_cuerpo() -> rx.Component:
    """Contenido desplazable compartido entre offcanvas y panel histórico."""
    return rx.scroll_area(
        rx.vstack(
            _px_alergias(),
            rx.divider(),
            rx.cond(
                PrescripcionState.px_puede_modificar,
                rx.vstack(
                    _section_prescripcion_title("Buscar medicamento"),
                    _px_buscador(),
                    _px_form_nuevo_item(),
                    rx.divider(),
                    spacing="2", width="100%",
                ),
                rx.box(),
            ),
            _section_prescripcion_title("Medicamentos recetados"),
            _px_tabla_items(),
            rx.divider(),
            _section_prescripcion_title("Cuidados generales"),
            _px_cuidados(),
            spacing="3", width="100%", padding_right="4px",
        ),
        height="77vh",
        scrollbars="vertical",
        type="auto",
    )


def form_prescripcion_actual() -> rx.Component:
    """Encabezado + cuerpo del offcanvas de Prescripción Actual."""
    return rx.vstack(
        # ── Encabezado ─────────────────────────────────────────────────────────
        rx.hstack(
            rx.text("📗 Prescripción", font_weight="bold", font_size="1.4em"),
            rx.spacer(),
            rx.cond(
                PrescripcionState.px_guardado_ok,
                rx.hstack(
                    rx.icon("circle_check", size=13, color="var(--green-9)"),
                    rx.text("Guardado", font_size="11px", color="var(--green-9)"),
                    on_click=PrescripcionState.cerrar_guardado_ok,
                    cursor="pointer", align="center", spacing="1",
                ),
                rx.text(""),
            ),
            # Botón imprimir receta — visible solo cuando la prescripción está grabada
            rx.cond(
                PrescripcionState.px_grabada,
                rx.link(
                    rx.button(
                        "🖨️ Imprimir",
                        type="button",
                        bg=BOTON_IMPRIMIR,
                        color="white",
                        font_size="0.75em",
                        border="none",
                        cursor="pointer",
                        title="Imprimir Receta",
                    ),
                    href=AtencionState.url_reporte_receta,
                    is_external=True,
                ),
                rx.box(),
            ),
            # Botón catálogo de medicamentos
            rx.button(
                rx.icon("book-open", size=13),
                "+ Agregar Medicamento al Catálogo",
                type="button",
                on_click=MantenimientoMedState.abrir_dlg,
                bg="var(--blue-3)",
                color="var(--blue-11)",
                font_size="0.72em",
                border="1px solid var(--blue-6)",
                cursor="pointer",
                padding="0 8px",
            ),
            # Botón 3 estados: Grabar / Editar / Guardar Cambios
            rx.cond(
                PrescripcionState.px_campos_bloqueados,
                # ── Modo grabado: ofrecer edición ──────────────────────────────
                rx.button(
                    "✏️ Editar Prescripción",
                    type="button",
                    on_click=PrescripcionState.editar_prescripcion,
                    bg=BOTON_ACCION,
                    color="white",
                    font_size="0.75em",
                    border="none",
                    cursor="pointer",
                ),
                rx.cond(
                    PrescripcionState.px_editando,
                    # ── Modo edición activo: guardar cambios ───────────────────
                    rx.button(
                        "💾 Guardar Cambios",
                        type="button",
                        on_click=PrescripcionState.guardar_cambios_prescripcion,
                        bg=BOTON_SECUNDARIO,
                        color="white",
                        font_size="0.75em",
                        border="none",
                        cursor="pointer",
                    ),
                    # ── Primera vez: grabar prescripción ───────────────────────
                    rx.button(
                        "💾 Grabar Prescripción",
                        type="button",
                        on_click=PrescripcionState.grabar_prescripcion,
                        disabled=AtencionState.prescripcion_deshabilitada,
                        bg=rx.cond(AtencionState.prescripcion_deshabilitada, BOTON_DESHABILITADO, BOTON_SECUNDARIO),
                        color=rx.cond(AtencionState.prescripcion_deshabilitada, BOTON_DESHABILITADO_TEXTO, "white"),
                        font_size="0.75em",
                        border="none",
                        cursor=rx.cond(AtencionState.prescripcion_deshabilitada, "not-allowed", "pointer"),
                    ),
                ),
            ),
            rx.cond(
                PrescripcionState.px_error != "",
                rx.text(PrescripcionState.px_error, font_size="11px", color="var(--red-9)"),
                rx.text(""),
            ),
            width="100%", align="center", spacing="2",
        ),
        # ── Aviso cuando el SOAP / vincular no están completos ─────────────────
        rx.cond(
            AtencionState.prescripcion_deshabilitada,
            rx.hstack(
                rx.icon("lock", size=13, color="var(--red-9)"),
                rx.text(
                    "La prescripción se habilitará únicamente cuando exista un SOAP válido "
                    "guardado con un diagnóstico vinculado.",
                    font_size="11px",
                    color="var(--red-9)",
                ),
                padding="6px 10px",
                background="var(--red-2)",
                border="1px solid var(--red-6)",
                border_radius="6px",
                width="100%",
                align="center",
                spacing="2",
            ),
            rx.box(),
        ),
        rx.divider(),
        _prescripcion_cuerpo(),
        spacing="0", width="100%",
    )


def panel_prescripcion_historica() -> rx.Component:
    """Panel derecha para prescripción histórica (modo lectura o edición según fecha)."""
    return rx.vstack(
        rx.hstack(
            rx.text("Prescripción", font_weight="bold", font_size="1.2em"),
            rx.text(State.atencion_seleccionada[1], font_size="12px", color="var(--gray-10)"),
            rx.badge(
                rx.cond(PrescripcionState.px_es_editable, "Edición (mismo día)", "Solo lectura"),
                color_scheme=rx.cond(PrescripcionState.px_es_editable, "green", "gray"),
                variant="soft",
            ),
            rx.spacer(),
            rx.button(
                rx.icon("x", size=14), "Cerrar",
                size="1", variant="ghost", color_scheme="gray",
                on_click=State.cambia_tab("historial_atenciones"),
                cursor="pointer",
            ),
            width="100%", align="center", spacing="2", padding_y="4px",
        ),
        rx.divider(),
        _prescripcion_cuerpo(),
        spacing="0", width="100%",
    )


def dialogo_editar_item_prescripcion() -> rx.Component:
    """Diálogo emergente para editar un ítem de la prescripción."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.box(
                        rx.icon("pencil", size=16),
                        width="32px", height="32px",
                        border_radius="50%",
                        background="var(--blue-3)",
                        display="flex", align_items="center", justify_content="center",
                    ),
                    rx.vstack(
                        rx.text("Editar medicamento", font_size="15px", font_weight="500"),
                        rx.text(PrescripcionState.px_edit_med_nombre, font_size="12px", color="var(--gray-11)"),
                        spacing="0", align="start",
                    ),
                    spacing="3", align="center",
                ),
            ),
            rx.vstack(
                rx.grid(
                    rx.vstack(
                        rx.hstack(
                            rx.text("Concentración", font_size="12px", font_weight="500", color="black"),
                            rx.text("*", color="var(--red-9)", font_size="12px"),
                            spacing="1",
                        ),
                        rx.input(
                            value=PrescripcionState.px_edit_concentracion,
                            on_change=PrescripcionState.set_px_edit_concentracion,
                            placeholder="Ej: 500 mg",
                            size="2", width="100%",
                        ),
                        spacing="1", width="100%",
                    ),
                    rx.vstack(
                        rx.hstack(
                            rx.text("Cantidad", font_size="12px", font_weight="500", color="black"),
                            rx.text("*", color="var(--red-9)", font_size="12px"),
                            spacing="1",
                        ),
                        rx.input(
                            value=PrescripcionState.px_edit_cantidad,
                            on_change=PrescripcionState.set_px_edit_cantidad,
                            type="number", min="1", size="2", width="90px",
                        ),
                        spacing="1", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Presentación", font_size="12px", font_weight="500", color="black"),
                        rx.select(
                            PrescripcionState.px_presentaciones_select,
                            placeholder="Opcional...",
                            value=PrescripcionState.px_nombre_presentacion_edit,
                            on_change=PrescripcionState.set_px_edit_lk_presentacion_por_nombre,
                            size="2", width="100%",
                        ),
                        spacing="1", width="100%",
                    ),
                    columns="3", gap="3", width="100%",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.text("Indicaciones", font_size="12px", font_weight="500", color="black"),
                        rx.text("*", color="var(--red-9)", font_size="12px"),
                        spacing="1",
                    ),
                    rx.text_area(
                        value=PrescripcionState.px_edit_indicaciones,
                        on_change=PrescripcionState.set_px_edit_indicaciones,
                        rows="3", size="2", width="100%", resize="none",
                    ),
                    spacing="1", width="100%",
                ),
                rx.cond(
                    PrescripcionState.px_edit_error != "",
                    rx.callout(
                        PrescripcionState.px_edit_error,
                        icon="triangle_alert", color_scheme="red", role="alert",
                    ),
                    rx.box(),
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="outline", size="2",
                                  on_click=PrescripcionState.cerrar_dlg_editar),
                    ),
                    rx.button(
                        "Guardar cambios",
                        size="2", color_scheme="indigo",
                        on_click=PrescripcionState.guardar_edicion_item,
                    ),
                    justify="end", spacing="2",
                    margin_top="16px", padding_top="12px",
                    border_top="1px solid var(--gray-5)", width="100%",
                ),
                spacing="4", width="100%",
            ),
            max_width="560px", width="90vw", padding="24px",
        ),
        open=PrescripcionState.px_dlg_editar,
        on_open_change=PrescripcionState.set_px_dlg_editar,
    )


def dialogo_nuevo_medicamento_px() -> rx.Component:
    """Diálogo para añadir un medicamento nuevo al catálogo (tipo=2, añadido en consulta)."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.box(
                        rx.icon("pill", size=16),
                        width="32px", height="32px",
                        border_radius="50%",
                        background="var(--green-3)",
                        display="flex", align_items="center", justify_content="center",
                    ),
                    rx.vstack(
                        rx.text("Añadir al catálogo", font_size="15px", font_weight="500"),
                        rx.text(
                            "Quedará disponible para futuras recetas.",
                            font_size="12px", color="var(--gray-11)",
                        ),
                        spacing="0", align="start",
                    ),
                    spacing="3", align="center",
                ),
            ),
            rx.vstack(
                rx.vstack(
                    rx.hstack(
                        rx.text("Nombre genérico", font_size="12px", font_weight="500", color="black"),
                        rx.text("*", color="var(--red-9)", font_size="12px"),
                        spacing="1",
                    ),
                    rx.input(
                        value=PrescripcionState.px_nuevo_gen_nombre,
                        on_change=PrescripcionState.set_px_nuevo_gen_nombre,
                        placeholder="NOMBRE GENÉRICO",
                        size="2", width="100%",
                    ),
                    spacing="1", width="100%",
                ),
                rx.vstack(
                    rx.text("Nombre comercial", font_size="12px", font_weight="500", color="black"),
                    rx.input(
                        value=PrescripcionState.px_nuevo_gen_comercial,
                        on_change=PrescripcionState.set_px_nuevo_gen_comercial,
                        placeholder="Marca comercial (opcional)",
                        size="2", width="100%",
                    ),
                    spacing="1", width="100%",
                ),
                rx.cond(
                    PrescripcionState.px_nuevo_gen_error != "",
                    rx.callout(
                        PrescripcionState.px_nuevo_gen_error,
                        icon="triangle_alert", color_scheme="red", role="alert",
                    ),
                    rx.box(),
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="outline", size="2",
                                  on_click=PrescripcionState.cerrar_dlg_nuevo_med),
                    ),
                    rx.button(
                        "Añadir medicamento",
                        size="2", color_scheme="green",
                        on_click=PrescripcionState.guardar_nuevo_medicamento,
                    ),
                    justify="end", spacing="2",
                    margin_top="16px", padding_top="12px",
                    border_top="1px solid var(--gray-5)", width="100%",
                ),
                spacing="4", width="100%",
            ),
            max_width="460px", width="90vw", padding="24px",
        ),
        open=PrescripcionState.px_dlg_nuevo_med,
        on_open_change=PrescripcionState.set_px_dlg_nuevo_med,
    )

def _mm_fila_similar(med: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(
            med["nombre_generico"],
            font_size="11px", font_weight="500", padding="3px 6px",
        ),
        rx.table.cell(
            med["nombre_comercial"],
            font_size="11px", color="var(--gray-11)", padding="3px 6px",
        ),
        rx.table.cell(
            med["nombre_tipo"],
            font_size="11px", color="var(--blue-11)", padding="3px 6px",
        ),
        style={"_hover": {"background": "var(--amber-2)"}},
    )


def dlg_mantenimiento_medicamentos() -> rx.Component:
    """Diálogo de mantenimiento del catálogo de medicamentos."""
    return rx.fragment(
        # ── Diálogo principal ─────────────────────────────────────────────────
        rx.dialog.root(
            rx.dialog.content(
                rx.dialog.title(
                    rx.hstack(
                        rx.box(
                            rx.icon("book-open", size=16),
                            width="32px", height="32px",
                            border_radius="50%",
                            background="var(--blue-3)",
                            display="flex", align_items="center", justify_content="center",
                        ),
                        rx.vstack(
                            rx.text("Añadir Medicamentos", font_size="15px", font_weight="600"),
                            rx.text(
                                "Añade un nuevo medicamento al catálogo.",
                                font_size="11px", color="var(--gray-11)",
                            ),
                            spacing="0", align="start",
                        ),
                        spacing="3", align="center",
                    ),
                ),
                rx.vstack(
                    # ── Tipo ──────────────────────────────────────────────────
                    rx.vstack(
                        rx.hstack(
                            rx.text("Tipo de medicamento", font_size="12px", font_weight="500"),
                            rx.text("*", color="var(--red-9)", font_size="12px"),
                            spacing="1",
                        ),
                        rx.select.root(
                            rx.select.trigger(placeholder="Seleccione tipo..."),
                            rx.select.content(
                                rx.foreach(
                                    MantenimientoMedState.mm_tipos,
                                    lambda t: rx.select.item(
                                        t["nombre_tipo"],
                                        value=t["id_tipo"].to_string(),
                                    ),
                                ),
                            ),
                            value=MantenimientoMedState.mm_tipo_id,
                            on_change=MantenimientoMedState.set_tipo,
                            width="100%",
                        ),
                        spacing="1", width="100%",
                    ),
                    # ── Nombre genérico ───────────────────────────────────────
                    rx.vstack(
                        rx.hstack(
                            rx.text("Nombre genérico", font_size="12px", font_weight="500"),
                            rx.text("*", color="var(--red-9)", font_size="12px"),
                            spacing="1",
                        ),
                        rx.input(
                            value=MantenimientoMedState.mm_generico,
                            on_change=MantenimientoMedState.set_generico,
                            placeholder="NOMBRE GENÉRICO",
                            size="2", width="100%",
                        ),
                        spacing="1", width="100%",
                    ),
                    # ── Nombre comercial ──────────────────────────────────────
                    rx.vstack(
                        rx.text("Nombre comercial", font_size="12px", font_weight="500"),
                        rx.input(
                            value=MantenimientoMedState.mm_comercial,
                            on_change=MantenimientoMedState.set_comercial,
                            placeholder="NOMBRE COMERCIAL (opcional)",
                            size="2", width="100%",
                        ),
                        spacing="1", width="100%",
                    ),
                    # ── Similares ─────────────────────────────────────────────
                    rx.cond(
                        MantenimientoMedState.mm_similares.length() > 0,
                        rx.vstack(
                            rx.hstack(
                                rx.icon("triangle-alert", size=13, color="var(--amber-9)"),
                                rx.text(
                                    "Medicamentos similares encontrados:",
                                    font_size="12px", font_weight="500",
                                    color="var(--amber-11)",
                                ),
                                spacing="1", align="center",
                            ),
                            rx.box(
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell(
                                                "Genérico",
                                                style={"fontSize": "11px", "padding": "3px 6px",
                                                       "background": "var(--amber-3)"},
                                            ),
                                            rx.table.column_header_cell(
                                                "Comercial",
                                                style={"fontSize": "11px", "padding": "3px 6px",
                                                       "background": "var(--amber-3)"},
                                            ),
                                            rx.table.column_header_cell(
                                                "Tipo",
                                                style={"fontSize": "11px", "padding": "3px 6px",
                                                       "background": "var(--amber-3)"},
                                            ),
                                        ),
                                    ),
                                    rx.table.body(
                                        rx.foreach(
                                            MantenimientoMedState.mm_similares,
                                            _mm_fila_similar,
                                        ),
                                    ),
                                    width="100%",
                                ),
                                width="100%",
                                max_height="160px",
                                overflow_y="auto",
                                border="1px solid var(--amber-6)",
                                border_radius="6px",
                            ),
                            width="100%",
                            spacing="1",
                            padding="8px",
                            background="var(--amber-2)",
                            border="1px solid var(--amber-5)",
                            border_radius="6px",
                        ),
                        rx.box(),
                    ),
                    # ── Error ─────────────────────────────────────────────────
                    rx.cond(
                        MantenimientoMedState.mm_error != "",
                        rx.callout(
                            MantenimientoMedState.mm_error,
                            icon="triangle_alert", color_scheme="red", role="alert",
                        ),
                        rx.box(),
                    ),
                    # ── Botones ───────────────────────────────────────────────
                    rx.hstack(
                        rx.dialog.close(
                            rx.button(
                                "Cancelar",
                                variant="outline", size="2", type="button",
                                on_click=MantenimientoMedState.cerrar_dlg,
                            ),
                        ),
                        rx.button(
                            "Añadir",
                            size="2", color_scheme="blue", type="button",
                            on_click=MantenimientoMedState.intentar_anadir,
                        ),
                        justify="end", spacing="2",
                        margin_top="16px", padding_top="12px",
                        border_top="1px solid var(--gray-5)", width="100%",
                    ),
                    spacing="4", width="100%",
                ),
                max_width="520px", width="92vw", padding="24px",
            ),
            open=MantenimientoMedState.mm_dlg_open,
            on_open_change=MantenimientoMedState.set_mm_dlg_open,
        ),
        # ── Diálogo de confirmación (se muestra cuando hay similares) ─────────
        rx.dialog.root(
            rx.dialog.content(
                rx.dialog.title(
                    rx.hstack(
                        rx.icon("shield-alert", size=18, color="var(--amber-9)"),
                        rx.text("Confirmar adición", font_size="15px", font_weight="600"),
                        spacing="2", align="center",
                    ),
                ),
                rx.vstack(
                    rx.text(
                        "Se encontraron medicamentos con nombres similares en el catálogo. "
                        "¿Confirma que desea añadir este medicamento de todas formas?",
                        font_size="13px", color="var(--gray-11)",
                    ),
                    rx.hstack(
                        rx.button(
                            "Cancelar",
                            variant="outline", size="2", type="button",
                            on_click=MantenimientoMedState.set_mm_confirm_open(False),
                        ),
                        rx.button(
                            "Sí, añadir de todas formas",
                            size="2", color_scheme="amber", type="button",
                            on_click=MantenimientoMedState.confirmar_anadir,
                        ),
                        justify="end", spacing="2",
                        margin_top="16px", padding_top="12px",
                        border_top="1px solid var(--gray-5)", width="100%",
                    ),
                    spacing="3", width="100%",
                ),
                max_width="420px", width="90vw", padding="24px",
            ),
            open=MantenimientoMedState.mm_confirm_open,
            on_open_change=MantenimientoMedState.set_mm_confirm_open,
        ),
    )


def offcanvas_prescripcion():
    """Simula el componente Offcanvas de Bootstrap con Reflex."""
    return rx.box(
        # Overlay oscuro (aparece cuando el panel está abierto)
        rx.cond(
            AtencionState.offcanvas_prescripcion,
            rx.box(
                on_click=AtencionState.toggle_offcanvas_prescripcion,
                position="fixed",
                top="0",
                left="0",
                width="100%",
                height="100%",
                bg="rgba(0,0,0,0.2)",
                z_index="98",
                transition="opacity 0.3s ease-in-out",
            )
        ),

        # Panel lateral derecho (offcanvas)
        rx.box(
            rx.vstack(
                form_prescripcion_actual(),
            ),
            position="fixed",
            top="65px",
            right="10px",
            height="calc(96% - 65px)",
            #Ancho offcanvas_prescripcion
            width=rx.cond(State.show_panel_izq, "55vw", "96vw"),
            bg="white",
            box_shadow="-2px 0 10px rgba(0,0,0,0.3)",
            z_index=rx.cond(AtencionState.offcanvas_prescripcion, "101", "99"),
            padding="0.5em",
            transform=rx.cond(
                AtencionState.offcanvas_prescripcion,
                "translateX(0)",
                "translateX(100%)",
            ),
            transition="transform 0.3s ease-in-out, width 0.3s ease-in-out",
        ),
    )

def form_nuevo_diagnostico():
    return rx.form(
        rx.button("PASo 1",on_click=AtencionState.toggle_offcanvas_nuevo_diagnostico)
    )

def offcanvas_nuevo_diagnostico():
    """Simula el componente Offcanvas de Bootstrap con Reflex."""
    return rx.box(
        # Overlay oscuro (aparece cuando el panel está abierto)
        rx.cond(
            AtencionState.offcanvas_nuevo_diagnostico,
            rx.box(
                on_click=AtencionState.toggle_offcanvas_nuevo_diagnostico,
                position="fixed",
                top="0",
                left="0",
                width="100%",
                height="100%",
                bg="rgba(0,0,0,0.2)",
                z_index="98",
                transition="opacity 0.3s ease-in-out",
            )
        ),

        # Panel lateral derecho (offcanvas)
        rx.box(
            rx.vstack(
                form_nuevo_diagnostico(),
            ),
            position="fixed",
            top="65px",
            right="10px",
            #height="100%",
            height="calc(96% - 65px)",
            width="49vw",
            bg="white",
            #box_shadow="500px 20 400px rgba(0,0,0,0.3)",
            box_shadow="-2px 0 10px rgba(0,0,0,0.3)",
            z_index="99",
            padding="0.5em",
            transform=rx.cond(
                AtencionState.offcanvas_nuevo_diagnostico,
                "translateX(0)",
                "translateX(100%)"  # se oculta fuera de la pantalla
            ),
            transition="transform 0.3s ease-in-out",
        ),
    )

################
def _label(text: str, required: bool = False) -> rx.Component:
    return rx.hstack(
        rx.text(text, font_size="12px", font_weight="500", color="black"),
        rx.cond(required, rx.text("*", color="var(--red-9)", font_size="12px")),
        spacing="1",
        align="center",
        margin_bottom="4px",
    )
 
 
def _section_title(text: str) -> rx.Component:
    return rx.text(
        text.upper(),
        font_size="11px",
        font_weight="500",
        color="var(--blue-9)",
        letter_spacing="0.06em",
        margin_bottom="10px",
        margin_top="4px",
    )
 
def _section_prescripcion_title(text: str) -> rx.Component:
    return rx.text(
        text.upper(),
        font_size="11px",
        font_weight="500",
        color="green",
        letter_spacing="0.06em",
        margin_bottom="10px",
        margin_top="4px",
    )
 

def _divider() -> rx.Component:
    return rx.divider(margin_y="16px")
 
 
def _input(placeholder: str, value, on_change, type: str = "text") -> rx.Component:
    return rx.input(
        placeholder=placeholder,
        value=value,
        on_change=on_change,
        type=type,
        width="100%",
        font_size="13px",
    )
 
 
def _select(opciones: list, placeholder: str, value, on_change) -> rx.Component:
    return rx.select(
        opciones,
        placeholder=placeholder,
        value=value,
        on_change=on_change,
        width="100%",
        font_size="13px",
    )
 
 
# ── Secciones del formulario ──────────────────────────────────────────────────
 
def seccion_datos_personales() -> rx.Component:
    return rx.fragment(
        _section_title("Datos personales"),
        rx.grid(
            rx.box(
                _label("Nombre completo", required=True),
                _input("Ingrese el nombre completo", PacienteState.nombre_completo, PacienteState.set_nombre_completo),
                grid_column="1 / -1",
            ),
            rx.box(
                _label("Cédula / ID", required=True),
                _input("0000000000", PacienteState.cedula_id, PacienteState.set_cedula_id),
            ),
            rx.box(
                _label("Sexo", required=True),
                _select(["Masculino", "Femenino", "Otro"], "Seleccionar...", PacienteState.sexo, PacienteState.set_sexo),
            ),
            rx.box(
                _label("Fecha de nacimiento", required=True),
                _input("", PacienteState.fecha_nacimiento, PacienteState.set_fecha_nacimiento, type="date"),
            ),
            rx.box(
                _label("País de nacimiento", required=True),
                _input("País", PacienteState.pais_nacimiento, PacienteState.set_pais_nacimiento),
            ),
            rx.box(
                _label("Estado civil", required=True),
                _select(
                    ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a", "Unión libre"],
                    "Seleccionar...", PacienteState.estado_civil, PacienteState.set_estado_civil,
                ),
            ),
            rx.box(
                _label("Grupo sanguíneo", required=True),
                _select(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], "Seleccionar...", PacienteState.grupo_sanguineo, PacienteState.set_grupo_sanguineo),
            ),
            rx.box(
                _label("Seguro médico", required=True),
                _select(PacienteState.lista_seguros, "Seleccionar...", PacienteState.seguro, PacienteState.set_seguro),
            ),
            columns="2",
            spacing="3",
            width="100%",
        ),
    )
 
 
 
def seccion_contacto() -> rx.Component:
    return rx.fragment(
        _divider(),
        _section_title("Residencia y contacto"),
        rx.grid(
            rx.box(
                _label("Ciudad de residencia", required=True),
                _input("Ciudad", PacienteState.ciudad_reside, PacienteState.set_ciudad_reside),
            ),
            rx.box(
                _label("Teléfono celular", required=True),
                _input("0999000000", PacienteState.tf_celular, PacienteState.set_tf_celular, type="tel"),
            ),
            rx.box(
                _label("Dirección de residencia", required=True),
                _input("Calle principal, número, referencia...", PacienteState.direccion_reside, PacienteState.set_direccion_reside),
                grid_column="1 / -1",
            ),
            rx.box(
                _label("Correo electrónico", required=True),
                _input("correo@ejemplo.com", PacienteState.email, PacienteState.set_email, type="email"),
            ),
            columns="2",
            spacing="3",
            width="100%",
        ),
    )
 
 
def seccion_observaciones() -> rx.Component:
    return rx.fragment(
        _divider(),
        _section_title("Observaciones no médicas sobre el paciente"),
        rx.text_area(
            placeholder="Observacions no médicas",
            value=PacienteState.observacion,
            on_change=PacienteState.set_observacion,
            rows="4",
            width="100%",
            font_size="13px",
            resize="vertical",
        ),
    )
 
 
# ── Diálogo principal ─────────────────────────────────────────────────────────
 
def dialogo_nuevo_paciente() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(                      # ← posicional, no content=

            rx.dialog.title(
                rx.hstack(
                    rx.box(
                        rx.icon("user", size=16),
                        width="32px",
                        height="32px",
                        border_radius="50%",
                        background="var(--blue-3)",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                    ),
                    rx.vstack(
                        rx.text("Nuevo paciente", font_size="15px", font_weight="500"),
                        rx.text(
                            "Complete todos los campos requeridos",
                            font_size="12px",
                            color="var(--gray-11)",
                        ),
                        spacing="0",
                        align="start",
                    ),
                    spacing="3",
                    align="center",
                ),
            ),

            rx.dialog.description(
                rx.scroll_area(
                    rx.box(
                        seccion_datos_personales(),
                        #seccion_origen(),
                        seccion_contacto(),
                        seccion_observaciones(),
                        padding_bottom="8px",
                    ),
                    max_height="62vh",
                    scrollbars="vertical",
                    type="auto",
                ),
            ),

            # Mensajes de error/éxito
            rx.cond(
                PacienteState.error_msg != "",
                rx.text(
                    PacienteState.error_msg,
                    color="var(--red-9)",
                    font_size="12px",
                    margin_top="8px",
                ),
                rx.fragment(),
            ),
            rx.cond(
                PacienteState.success_msg != "",
                rx.text(
                    PacienteState.success_msg,
                    color="var(--green-9)",
                    font_size="12px",
                    margin_top="8px",
                ),
                rx.fragment(),
            ),

            # Pie
            rx.hstack(
                rx.text(
                    rx.text.span("* ", color="var(--red-9)"),
                    "Campos obligatorios",
                    font_size="11px",
                    color="var(--gray-10)",
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button(
                            "Cancelar",
                            variant="outline",
                            size="2",
                            on_click=PacienteState.close_dialog,
                        ),
                    ),
                    rx.button(
                        "Guardar paciente",
                        size="2",
                        color_scheme="indigo",
                        on_click=PacienteState.guardar_paciente,
                    ),
                    spacing="2",
                ),
                justify="between",
                align="center",
                margin_top="16px",
                padding_top="12px",
                border_top="1px solid var(--gray-5)",
                width="100%",
            ),

            max_width="680px",
            width="95vw",
            padding="24px",
        ),                                      # ← cierra rx.dialog.content
        open=PacienteState.dialog_open,
        on_open_change=PacienteState.set_dialog_open,
    )


# ── Diálogo Datos del Paciente (edición) ──────────────────────────────────────

def _campo_ep(label: str, value, on_change, tipo: str = "text", obligatorio: bool = False) -> rx.Component:
    label_node = (
        rx.hstack(
            rx.text(label, font_size="12px", font_weight="500", color="black"),
            rx.text("*", color="var(--red-9)", font_size="12px"),
            spacing="1", align="center",
        ) if obligatorio else
        rx.text(label, font_size="12px", font_weight="500", color="black")
    )
    bg = rx.cond(value == "", "var(--red-3)", "") if obligatorio else ""
    return rx.vstack(
        label_node,
        rx.input(
            value=value, on_change=on_change, type=tipo, size="2", width="100%",
            read_only=EditPacienteState.ep_modo_lectura,
            background_color=bg,
        ),
        spacing="1",
        width="100%",
    )

def _select_ep(label: str, opciones: list, value, on_change, obligatorio: bool = False) -> rx.Component:
    label_node = (
        rx.hstack(
            rx.text(label, font_size="12px", font_weight="500", color="black"),
            rx.text("*", color="var(--red-9)", font_size="12px"),
            spacing="1", align="center",
        ) if obligatorio else
        rx.text(label, font_size="12px", font_weight="500", color="black")
    )
    bg = rx.cond(value == "", "var(--red-3)", "") if obligatorio else ""
    return rx.vstack(
        label_node,
        rx.select(
            opciones, value=value, on_change=on_change, size="2", width="100%",
            disabled=EditPacienteState.ep_modo_lectura,
            background_color=bg,
        ),
        spacing="1",
        width="100%",
    )

def dialogo_datos_paciente() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon("user", size=16),
                    rx.vstack(
                        rx.text("Datos del Paciente", font_size="15px", font_weight="500"),
                        rx.text(
                            State.nombre_paciente_seleccionado,
                            font_size="12px",
                            color="var(--gray-11)",
                        ),
                        spacing="0",
                        align="start",
                    ),
                    spacing="3",
                    align="center",
                ),
            ),
            rx.vstack(
                rx.grid(
                    _campo_ep("Nombre Completo", EditPacienteState.ep_nombre_completo, EditPacienteState.set_ep_nombre_completo, obligatorio=True),
                    _campo_ep("Cédula / ID", EditPacienteState.ep_cedula_id, EditPacienteState.set_ep_cedula_id, obligatorio=True),
                    _select_ep("Sexo", ["Masculino", "Femenino", "Otro"], EditPacienteState.ep_sexo, EditPacienteState.set_ep_sexo, obligatorio=True),
                    _campo_ep("Fecha de Nacimiento", EditPacienteState.ep_fecha_nacimiento, EditPacienteState.set_ep_fecha_nacimiento, tipo="date", obligatorio=True),
                    _campo_ep("País de Nacimiento", EditPacienteState.ep_pais_nacimiento, EditPacienteState.set_ep_pais_nacimiento, obligatorio=True),
                    _select_ep("Estado Civil", ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a", "Unión libre"], EditPacienteState.ep_estado_civil, EditPacienteState.set_ep_estado_civil, obligatorio=True),
                    _select_ep("Grupo Sanguíneo", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], EditPacienteState.ep_grupo_sanguineo, EditPacienteState.set_ep_grupo_sanguineo, obligatorio=True),
                    _select_ep("Seguro", EditPacienteState.ep_lista_seguros, EditPacienteState.ep_seguro, EditPacienteState.set_ep_seguro, obligatorio=True),
                    _campo_ep("Ciudad de Residencia", EditPacienteState.ep_ciudad_reside, EditPacienteState.set_ep_ciudad_reside, obligatorio=True),
                    _campo_ep("Teléfono Celular", EditPacienteState.ep_tf_celular, EditPacienteState.set_ep_tf_celular, tipo="tel", obligatorio=True),
                    _campo_ep("Correo Electrónico", EditPacienteState.ep_email, EditPacienteState.set_ep_email, tipo="email", obligatorio=True),
                    _campo_ep("Dirección de Residencia", EditPacienteState.ep_direccion_reside, EditPacienteState.set_ep_direccion_reside, obligatorio=True),
                    columns="2",
                    gap="3",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Observaciones no médicas", font_size="12px", font_weight="500", color="black"),
                    rx.text_area(
                        value=EditPacienteState.ep_observacion,
                        on_change=EditPacienteState.set_ep_observacion,
                        height="70px",
                        width="100%",
                        read_only=EditPacienteState.ep_modo_lectura,
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.cond(
                    EditPacienteState.ep_error != "",
                    rx.callout(EditPacienteState.ep_error, icon="triangle_alert", color_scheme="red", role="alert"),
                ),
                rx.cond(
                    EditPacienteState.ep_success != "",
                    rx.callout(EditPacienteState.ep_success, icon="circle_check", color_scheme="green", role="status"),
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Salir", variant="soft", color_scheme="gray"),
                    ),
                    rx.spacer(),
                    rx.cond(
                        EditPacienteState.ep_modo_lectura,
                        rx.button(
                            "Editar",
                            color_scheme="indigo",
                            on_click=EditPacienteState.set_ep_modo_edicion(True),
                        ),
                        rx.fragment(),
                    ),
                    rx.cond(
                        EditPacienteState.ep_modo_edicion,
                        rx.cond(
                            EditPacienteState.ep_puede_grabar,
                            rx.button(
                                "Grabar Cambios",
                                color_scheme="green",
                                on_click=EditPacienteState.guardar_cambios_paciente,
                            ),
                            rx.button("Grabar Cambios", color_scheme="green", disabled=True),
                        ),
                        rx.fragment(),
                    ),
                    spacing="3",
                    margin_top="16px",
                    padding_top="12px",
                    border_top="1px solid var(--gray-5)",
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
            max_width="700px",
            width="95vw",
            padding="24px",
        ),
        open=EditPacienteState.dialog_editar_open,
        on_open_change=EditPacienteState.set_dialog_editar_open,
    )


def dialogo_paciente_guardado() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.box(
                    rx.icon("circle_check", size=40, color="var(--green-9)"),
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    width="100%",
                    padding_y="8px",
                ),
                rx.text(
                    "Paciente Guardado",
                    font_size="18px",
                    font_weight="600",
                    text_align="center",
                    color="var(--gray-12)",
                ),
                rx.dialog.close(
                    rx.button(
                        "Aceptar",
                        color_scheme="green",
                        size="2",
                        width="120px",
                        on_click=PacienteState.set_show_confirmacion(False),
                    ),
                ),
                spacing="4",
                align="center",
                padding="8px",
            ),
            max_width="320px",
            width="90vw",
            padding="24px",
        ),
        open=PacienteState.show_confirmacion,
        on_open_change=PacienteState.set_show_confirmacion,
    )


# ── Offcanvas Menú (izquierda, 200 px) ───────────────────────────────────────

def offcanvas_menu() -> rx.Component:
    return rx.box(
        # Overlay
        rx.cond(
            AtencionState.offcanvas_menu,
            rx.box(
                position="fixed",
                top="0",
                left="0",
                width="100%",
                height="100%",
                bg="rgba(0,0,0,0.2)",
                z_index="998",
                on_click=AtencionState.toggle_offcanvas_menu,
            ),
        ),
        # Panel lateral izquierdo
        rx.box(
            rx.vstack(
                rx.text("Menú", font_size="13px", font_weight="600", color="var(--gray-11)", padding_bottom="8px"),
                rx.divider(),
                # Agregar Medicamento — Med.Lee + Med.Prop + Admin
                rx.cond(
                    State.puede_ver_clinica,
                    rx.button(
                        rx.icon("book-open", size=13),
                        "+ Agregar Medicamento al Catálogo",
                        type="button",
                        on_click=MantenimientoMedState.abrir_dlg,
                        bg="var(--blue-3)",
                        color="var(--blue-11)",
                        font_size="0.72em",
                        border="1px solid var(--blue-6)",
                        cursor="pointer",
                        padding="0 8px",
                    ),
                    rx.fragment(),
                ),
                # ── Certificados ─────────────────────────────────────────────
                rx.accordion.root(
                    rx.accordion.item(
                        header=rx.hstack(
                            rx.icon("file_badge", size=14, color="var(--gray-11)"),
                            rx.text("Certificados", font_size="12px", color="var(--gray-12)"),
                            spacing="2", align="center",
                        ),
                        content=rx.vstack(
                            # Nuevo Certificado — solo Med.Prop + Admin
                            rx.cond(
                                State.puede_escribir,
                                rx.button(
                                    rx.icon("file_plus", size=13),
                                    rx.text("Nuevo Certificado", font_size="11px"),
                                    variant="ghost", width="100%", justify="start",
                                    type="button",
                                    on_click=CertificadoState.cert_abrir_nuevo,
                                    padding_left="16px",
                                ),
                                rx.fragment(),
                            ),
                            # Certificado Tardío — Med.Lee + Med.Prop + Admin
                            rx.cond(
                                State.puede_ver_clinica,
                                rx.button(
                                    rx.icon("clock", size=13),
                                    rx.text("Certificado Tardío", font_size="11px"),
                                    variant="ghost", width="100%", justify="start",
                                    type="button",
                                    on_click=CertificadoState.cert_abrir_dlg_atenciones,
                                    padding_left="16px",
                                ),
                                rx.fragment(),
                            ),
                            # Re-Imprimir Certificados — todos los perfiles
                            rx.button(
                                rx.icon("list", size=13),
                                rx.text("Re-Imprimir Certificados", font_size="11px"),
                                variant="ghost", width="100%", justify="start",
                                type="button",
                                on_click=CertificadoState.cert_abrir_offcanvas,
                                padding_left="16px",
                            ),
                            spacing="1", width="100%", padding_y="4px",
                        ),
                    ),
                    collapsible=True, variant="ghost", width="100%",
                ),
                spacing="2",
                align="start",
                padding="12px",
                width="100%",
                
            ),
            position="fixed",
            top="60px",
            left="0",
            height="calc(100% - 60px)",
            width="200px",
            bg="white",
            box_shadow="2px 0 10px rgba(0,0,0,0.2)",
            z_index="999",
            transform=rx.cond(
                AtencionState.offcanvas_menu,
                "translateX(0)",
                "translateX(-100%)",
            ),
            transition="transform 0.3s ease-in-out",
        ),
    )


# ── Diálogo Nuevo Diagnóstico ─────────────────────────────────────────────────

def dialogo_nuevo_diagnostico() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.box(
                        rx.icon("stethoscope", size=16),
                        width="32px", height="32px",
                        border_radius="50%",
                        background="var(--green-3)",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                    ),
                    rx.vstack(
                        rx.text("Nuevo Diagnóstico - Antecedente Personal", font_size="15px", font_weight="500"),
                        rx.text(
                            State.nombre_paciente_seleccionado,
                            font_size="12px",
                            color="var(--gray-11)",
                        ),
                        spacing="0",
                        align="start",
                    ),
                    spacing="3",
                    align="center",
                ),
            ),
            rx.vstack(
                # ── Buscar CIE10 ──
                rx.vstack(
                    rx.hstack(
                        rx.text("Buscar Diagnóstico CIE10", font_size="12px", font_weight="500", color="black"),
                        rx.text("*", color="var(--red-9)", font_size="12px"),
                        spacing="1",
                    ),
                    rx.input(
                        value=NuevoDiagnosticoState.nd_busqueda_cie10,
                        on_change=NuevoDiagnosticoState.set_nd_busqueda_cie10,
                        placeholder="Ingrese al menos 3 caracteres...",
                        size="2",
                        width="100%",
                    ),
                    # Tabla de hallazgos
                    rx.cond(
                        NuevoDiagnosticoState.nd_resultados_cie10.length() > 0,
                        rx.scroll_area(
                            rx.table.root(
                                rx.table.header(
                                    rx.table.row(
                                        rx.table.column_header_cell("CIE10",  style={"padding": "3px 6px", "font_size": "11px", "font_weight": "bold", "background": TABLE_HEADER_BG_PETROLEO, "color": TABLE_HEADER_COLOR, "width": "70px"}),
                                        rx.table.column_header_cell("Categoría", style={"padding": "3px 6px", "font_size": "11px", "font_weight": "bold", "background": TABLE_HEADER_BG_PETROLEO, "color": TABLE_HEADER_COLOR, "width": "220px"}),
                                        rx.table.column_header_cell("Diagnóstico", style={"padding": "3px 6px", "font_size": "11px", "font_weight": "bold", "background": TABLE_HEADER_BG_PETROLEO, "color": TABLE_HEADER_COLOR}),
                                    )
                                ),
                                rx.table.body(
                                    rx.foreach(
                                        NuevoDiagnosticoState.nd_resultados_cie10,
                                        lambda r: rx.table.row(
                                            rx.table.cell(r["cod_cie10"], style={"padding": "2px 6px", "font_size": "11px", "border": "1px solid #e5e7eb"}),
                                            rx.table.cell(r["categoria"],  style={"padding": "2px 6px", "font_size": "11px", "border": "1px solid #e5e7eb"}),
                                            rx.table.cell(r["nomdiagnostico"], style={"padding": "2px 6px", "font_size": "11px", "border": "1px solid #e5e7eb"}),
                                            on_click=NuevoDiagnosticoState.selecciona_cie10(r["cod_cie10"]),
                                            cursor="pointer",
                                            _hover={"background": ROW_HOVER_BG},
                                        )
                                    )
                                ),
                                width="100%",
                                style={"border_collapse": "collapse"},
                            ),
                            height="180px",
                            scrollbars="vertical",
                        ),
                    ),
                    # CIE10 seleccionado
                    rx.cond(
                        NuevoDiagnosticoState.nd_cie10 != "",
                        rx.hstack(
                            rx.badge(NuevoDiagnosticoState.nd_cie10, color_scheme="green", size="2"),
                            rx.text(NuevoDiagnosticoState.nd_nombre_cie10, font_size="12px", color="var(--green-11)", font_style="italic"),
                            align="center",
                            spacing="2",
                            padding="6px",
                            border_radius="4px",
                            background="var(--green-2)",
                            width="100%",
                        ),
                    ),
                    spacing="2",
                    width="100%",
                ),
                # ── Grid tipo + fechas ──
                rx.grid(
                    rx.vstack(
                        rx.hstack(
                            rx.text("Tipo", font_size="12px", font_weight="500", color="black"),
                            rx.text("*", color="var(--red-9)", font_size="12px"),
                            spacing="1",
                        ),
                        rx.cond(
                            NuevoDiagnosticoState.nd_tipo_fijo,
                            rx.input(
                                value=NuevoDiagnosticoState.nd_tipo,
                                disabled=True,
                                size="2",
                                width="100%",
                                color="var(--gray-11)",
                            ),
                            rx.select(
                                ["Definitivo", "Presuntivo"],
                                placeholder="Seleccionar...",
                                value=NuevoDiagnosticoState.nd_tipo,
                                on_change=NuevoDiagnosticoState.set_nd_tipo,
                                size="2",
                                width="100%",
                                background_color=rx.cond(
                                    NuevoDiagnosticoState.nd_tipo == "", "var(--red-3)", ""
                                ),
                            ),
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.hstack(
                            rx.text("Fecha Diagnóstico", font_size="12px", font_weight="500", color="black"),
                            rx.text("*", color="var(--red-9)", font_size="12px"),
                            spacing="1",
                        ),
                        rx.input(
                            value=NuevoDiagnosticoState.nd_fecha_diagnostico,
                            on_change=NuevoDiagnosticoState.set_nd_fecha_diagnostico,
                            type="date",
                            size="2",
                            width="100%",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.hstack(
                            rx.text("Fecha Inicio Aparente", font_size="12px", font_weight="500", color="black"),
                            rx.text("*", color="var(--red-9)", font_size="12px"),
                            spacing="1",
                        ),
                        rx.input(
                            value=NuevoDiagnosticoState.nd_fecha_inicio_aparente,
                            on_change=NuevoDiagnosticoState.set_nd_fecha_inicio_aparente,
                            type="date",
                            size="2",
                            width="100%",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    columns="3",
                    gap="3",
                    width="100%",
                ),
                # ── Edad de Inicio Aparente ──
                rx.vstack(
                    rx.text("Edad de Inicio Aparente", font_size="12px", font_weight="500", color="black"),
                    rx.hstack(
                        rx.vstack(
                            rx.text("Años", font_size="11px", color="var(--gray-11)"),
                            rx.input(
                                value=NuevoDiagnosticoState.nd_edad_anios.to(str),
                                on_change=NuevoDiagnosticoState.set_nd_edad_anios,
                                type="number",
                                min="0",
                                max="120",
                                size="2",
                                width="90px",
                            ),
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text("Meses", font_size="11px", color="var(--gray-11)"),
                            rx.input(
                                value=NuevoDiagnosticoState.nd_edad_meses.to(str),
                                on_change=NuevoDiagnosticoState.set_nd_edad_meses,
                                type="number",
                                min="0",
                                max="11",
                                size="2",
                                width="90px",
                            ),
                            spacing="1",
                        ),
                        rx.text(
                            "→ ",
                            NuevoDiagnosticoState.nd_fecha_inicio_aparente,
                            font_size="11px",
                            color="var(--gray-10)",
                            align_self="flex-end",
                            padding_bottom="4px",
                        ),
                        spacing="3",
                        align="end",
                    ),
                    spacing="1",
                    width="100%",
                ),
                # ── Observaciones ──
                rx.vstack(
                    rx.text("Observaciones", font_size="12px", font_weight="500", color="black"),
                    rx.text_area(
                        value=NuevoDiagnosticoState.nd_observaciones,
                        on_change=NuevoDiagnosticoState.set_nd_observaciones,
                        placeholder="Observaciones adicionales...",
                        height="70px",
                        width="100%",
                    ),
                    spacing="1",
                    width="100%",
                ),
                # ── Error ──
                rx.cond(
                    NuevoDiagnosticoState.nd_error != "",
                    rx.callout(
                        NuevoDiagnosticoState.nd_error,
                        icon="triangle_alert",
                        color_scheme="red",
                        role="alert",
                    ),
                ),
                # ── Pie ──
                rx.hstack(
                    rx.text(
                        rx.text.span("* ", color="var(--red-9)"),
                        "Campos obligatorios",
                        font_size="11px",
                        color="var(--gray-10)",
                    ),
                    rx.hstack(
                        rx.dialog.close(
                            rx.button("Cancelar", variant="outline", size="2",
                                      on_click=NuevoDiagnosticoState.set_nd_dialog_open(False)),
                        ),
                        rx.button(
                            "Guardar Diagnóstico",
                            size="2",
                            color_scheme="green",
                            on_click=NuevoDiagnosticoState.guardar_diagnostico,
                        ),
                        spacing="2",
                    ),
                    justify="between",
                    align="center",
                    margin_top="16px",
                    padding_top="12px",
                    border_top="1px solid var(--gray-5)",
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
            max_width="780px",
            width="95vw",
            padding="24px",
        ),
        open=NuevoDiagnosticoState.nd_dialog_open,
        on_open_change=NuevoDiagnosticoState.set_nd_dialog_open,
    )


def dialogo_vincular_diagnostico():
    _HEADER = {"background": TABLE_HEADER_BG_PETROLEO, "color": TABLE_HEADER_COLOR, "padding": "8px 12px", "font_size": "13px", "font_weight": "bold"}
    _CELL = {"padding": "6px 12px", "font_size": "13px"}
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.dialog.title("Vincular Diagnóstico"),
                    rx.spacer(),
                    rx.button(
                        "＋ Nuevo Diagnóstico",
                        bg=BOTON_ACCION,
                        color="white",
                        border="none",
                        font_size="0.75em",
                        on_click=NuevoDiagnosticoState.abrir_nuevo_diagnostico,
                        cursor="pointer",
                    ),
                    width="100%",
                    align="center",
                ),
                rx.dialog.description(
                    "Seleccione los diagnósticos a vincular con esta atención.",
                    font_size="13px",
                    color="gray",
                ),
                rx.box(
                    #Tabla con diagnosticos registrados para el paciente
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Vincular", style=_HEADER),
                                rx.table.column_header_cell("Nombre Diagnóstico", style=_HEADER),
                                rx.table.column_header_cell("CIE10", style=_HEADER),
                                rx.table.column_header_cell("Tipo", style=_HEADER),
                                rx.table.column_header_cell("Observaciones", style=_HEADER),
                            ),
                            style={"position": "sticky", "top": "0", "z_index": "1"},
                        ),
                        rx.table.body(
                            rx.foreach(
                                AtencionState.vd_diagnosticos_con_estado,
                                lambda row: rx.table.row(
                                    rx.table.cell(
                                        rx.checkbox(
                                            checked=row["checked"],
                                            on_change=AtencionState.toggle_diagnostico(row["id_diagnostico"]),
                                        ),
                                        style=_CELL,
                                    ),
                                    rx.table.cell(row["nombre_cie10"], style=_CELL),
                                    rx.table.cell(row["cie10"], style=_CELL),
                                    rx.table.cell(row["tipo"], style=_CELL),
                                    rx.table.cell(
                                        row["observaciones"],
                                        style={**_CELL, "max_width": "260px", "white_space": "pre-wrap", "word_break": "break-word"},
                                    ),
                                ),
                            )
                        ),
                        width="100%",
                    ),
                    overflow_y="auto",
                    max_height="45vh",
                    border="1px solid var(--gray-5)",
                    border_radius="6px",
                    width="100%",
                ),
                rx.cond(
                    AtencionState.vd_error != "",
                    rx.callout(
                        AtencionState.vd_error,
                        color="red",
                        variant="soft",
                        width="100%",
                    ),
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray"),
                    ),
                    rx.button(
                        "Vincular",
                        on_click=AtencionState.confirmar_vinculos,
                        color_scheme="blue",
                    ),
                    justify="end",
                    width="100%",
                    spacing="3",
                    padding_top="12px",
                    border_top="1px solid var(--gray-5)",
                ),
                spacing="4",
                width="100%",
            ),
            max_width="1000px",
            width="92vw",
            padding="24px",
        ),
        open=AtencionState.vd_dialog_open,
        on_open_change=AtencionState.set_vd_dialog_open,
    )


def dialogo_vinculos_exitosos():
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.icon("circle_check", size=28, color="green"),
                    rx.dialog.title(
                        "Diagnósticos Vinculados Exitosamente",
                        font_size="1.1em",
                        font_weight="bold",
                    ),
                    align="center",
                    spacing="3",
                ),
                rx.hstack(
                    rx.button(
                        "Aceptar",
                        on_click=AtencionState.cerrar_vinculos_ok,
                        color_scheme="green",
                        width="120px",
                    ),
                    justify="end",
                    width="100%",
                    padding_top="12px",
                    border_top="1px solid var(--gray-5)",
                ),
                spacing="4",
                width="100%",
            ),
            max_width="420px",
            padding="24px",
        ),
        open=AtencionState.vd_vinculos_ok,
    )


def _fila_grupo(grupo: dict) -> rx.Component:
    """Fila de la tabla de grupos (col 1); click para filtrar."""
    _sel = PedidoExamenesState.pe_filtro_grupo == grupo["id_grupo"]
    return rx.table.row(
        rx.table.cell(
            grupo["nombre_grupo"],
            style={"fontSize": "11px", "padding": "3px 6px"},
        ),
        on_click=PedidoExamenesState.pe_toggle_grupo(grupo["id_grupo"]),
        cursor="pointer",
        background=rx.cond(_sel, "var(--blue-3)", "transparent"),
        font_weight=rx.cond(_sel, "600", "400"),
        color=rx.cond(_sel, "var(--blue-11)", "inherit"),
        _hover={"background": ROW_HOVER_BG},
    )


def _fila_examen_disponible(examen: dict) -> rx.Component:
    """Fila de la tabla de exámenes disponibles (col 2); botón + para agregar al pedido."""
    return rx.table.row(
        rx.table.cell(
            rx.button(
                "➕",
                type="button",
                on_click=PedidoExamenesState.pe_agregar_examen(examen["id_examen"]),
                size="3",
                variant="ghost",
                color="#025BFF",
                font_weight="bold",
                font_size="20px",
                cursor=rx.cond(PedidoExamenesState.pe_campos_bloqueados, "not-allowed", "pointer"),
                disabled=PedidoExamenesState.pe_campos_bloqueados,
                padding="2px",
                top="4px",
                height="20px",
                width="20px",
            ),
            style={"padding": "1px 2px", "width": "1px", "white_space": "nowrap", "text_align": "center"},
        ),
        rx.table.cell(
            examen["nombre_examen"],
            style={"fontSize": "11px", "padding": "2px 4px"},
        ),
        _hover={"background": ROW_HOVER_BG},
    )


def _fila_examen_seleccionado(examen: dict) -> rx.Component:
    """Fila de la tabla derecha (pedido); botón − para quitar."""
    return rx.table.row(
        rx.table.cell(
            examen["nombre_examen"],
            style={"fontSize": "11px", "padding": "2px 4px"},
        ),
        rx.table.cell(
            examen["nombre_grupo"],
            style={"fontSize": "10px", "padding": "2px 4px", "color": "var(--gray-9)"},
        ),
        rx.table.cell(
            rx.button(
                "−",
                type="button",
                on_click=PedidoExamenesState.pe_quitar_examen(examen["id_examen"]),
                size="3",
                variant="ghost",
                color="var(--red-9)",
                font_weight="bold",
                font_size="20px",
                cursor=rx.cond(PedidoExamenesState.pe_campos_bloqueados, "not-allowed", "pointer"),
                disabled=PedidoExamenesState.pe_campos_bloqueados,
                padding="4px",
                height="20px",
                width="20px",
            ),
            style={"padding": "1px 2px", "width": "26px", "text_align": "center"},
        ),
        background=examen["fila_fondo"],
        _hover={"background": "rgba(220,38,38,0.06)"},
    )


# ── TAB Otros Exámenes ────────────────────────────────────────────────────────

_OE_TH = {
    "fontSize": "11px", "padding": "3px 8px", "fontWeight": "600",
    "background": TABLE_HEADER_BG_BLUE, "color": TABLE_HEADER_COLOR,
}
_OE_TD = {"fontSize": "11px", "padding": "3px 8px", "verticalAlign": "top"}


def _fila_oe(item: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(item["tipo"],   style=_OE_TD),
        rx.table.cell(item["alias"],  style=_OE_TD),
        rx.table.cell(item["nombre"], style=_OE_TD),
        rx.table.cell(
            item["detalle"],
            style={**_OE_TD, "maxWidth": "200px", "whiteSpace": "pre-wrap", "wordBreak": "break-word"},
        ),
        rx.table.cell(
            rx.hstack(
                rx.button(
                    rx.icon("pencil", size=17),
                    type="button",
                    size="1",
                    variant="ghost",
                    on_click=OtrosPedidoState.oe_iniciar_editar(item["id"]),
                    cursor="pointer",
                ),
                rx.button(
                    rx.icon("trash-2", size=17),
                    type="button",
                    size="1",
                    variant="ghost",
                    color_scheme="red",
                    on_click=OtrosPedidoState.oe_eliminar(item["id"]),
                    cursor="pointer",
                ),
                gap="10px",
            ),
            style={**_OE_TD, "width": "52px"},
        ),
        _hover={"background": ROW_HOVER_BG},
    )


def _dlg_oe_nuevo() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon("flask-conical", size=15, color=BOTON_ACCION),
                    rx.text("Nueva solicitud de examen"),
                    spacing="2",
                    align="center",
                ),
            ),
            rx.vstack(
                # Error
                rx.cond(
                    OtrosPedidoState.oe_error != "",
                    rx.hstack(
                        rx.icon("triangle-alert", size=13, color="var(--red-9)"),
                        rx.text(OtrosPedidoState.oe_error, font_size="11px", color="var(--red-9)"),
                        padding="4px 8px",
                        bg="var(--red-2)",
                        border_radius="4px",
                        width="100%",
                        align="center",
                        spacing="2",
                    ),
                    rx.text(""),
                ),
                # Tipo de examen
                rx.vstack(
                    rx.text("Tipo de examen", font_size="12px", color="var(--gray-10)"),
                    rx.select.root(
                        rx.select.trigger(placeholder="— Tipo de examen —", width="100%"),
                        rx.select.content(
                            rx.foreach(
                                OtrosPedidoState.oe_opciones_tipos,
                                lambda t: rx.select.item(t[1], value=t[0]),
                            ),
                        ),
                        value=OtrosPedidoState.oe_val_tipo,
                        on_change=OtrosPedidoState.set_oe_sel_tipo,
                        width="100%",
                        size="2",
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                # Examen
                rx.vstack(
                    rx.text("Examen", font_size="12px", color="var(--gray-10)"),
                    rx.select.root(
                        rx.select.trigger(
                            placeholder="— Seleccione el tipo primero —",
                            width="100%",
                        ),
                        rx.select.content(
                            rx.foreach(
                                OtrosPedidoState.oe_opciones_cat,
                                lambda e: rx.select.item(e[1], value=e[0]),
                            ),
                        ),
                        value=OtrosPedidoState.oe_val_examen,
                        on_change=OtrosPedidoState.set_oe_sel_examen,
                        disabled=OtrosPedidoState.oe_sel_tipo == 0,
                        width="100%",
                        size="2",
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                # Detalle
                rx.vstack(
                    rx.text("Detalle del examen", font_size="12px", color="var(--gray-10)"),
                    rx.text_area(
                        value=OtrosPedidoState.oe_detalle,
                        on_change=OtrosPedidoState.set_oe_detalle,
                        rows="3",
                        width="100%",
                        font_size="12px",
                        placeholder="Detalles del examen solicitado...",
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                spacing="3",
                width="100%",
                align="start",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancelar",
                        type="button",
                        variant="outline",
                        size="2",
                        on_click=OtrosPedidoState.oe_cancelar_form,
                    ),
                ),
                rx.button(
                    "💾 Grabar examen",
                    type="button",
                    size="2",
                    bg=BOTON_SECUNDARIO,
                    color="white",
                    on_click=OtrosPedidoState.oe_grabar_examen,
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),
            max_width="500px",
        ),
        open=OtrosPedidoState.oe_form_visible,
        on_open_change=OtrosPedidoState.set_oe_form_visible,
    )


def _form_oe_editar() -> rx.Component:
    return rx.vstack(
        rx.text("Editar examen solicitado", font_size="12px", font_weight="600", color="var(--gray-11)"),
        rx.hstack(
            rx.vstack(
                rx.text("Tipo de examen", font_size="11px", color="var(--gray-10)"),
                rx.select.root(
                    rx.select.trigger(placeholder="— Tipo —", width="190px"),
                    rx.select.content(
                        rx.foreach(
                            OtrosPedidoState.oe_opciones_tipos,
                            lambda t: rx.select.item(t[1], value=t[0]),
                        ),
                    ),
                    value=OtrosPedidoState.oe_val_edit_tipo,
                    on_change=OtrosPedidoState.set_oe_edit_sel_tipo,
                    size="2",
                ),
                spacing="1",
                align="start",
            ),
            rx.vstack(
                rx.text("Examen", font_size="11px", color="var(--gray-10)"),
                rx.select.root(
                    rx.select.trigger(placeholder="— Examen —", width="260px"),
                    rx.select.content(
                        rx.foreach(
                            OtrosPedidoState.oe_opciones_cat_edit,
                            lambda e: rx.select.item(e[1], value=e[0]),
                        ),
                    ),
                    value=OtrosPedidoState.oe_val_edit_examen,
                    on_change=OtrosPedidoState.set_oe_edit_sel_examen,
                    disabled=OtrosPedidoState.oe_edit_sel_tipo == 0,
                    size="2",
                ),
                spacing="1",
                align="start",
            ),
            spacing="3",
            align="end",
            flex_wrap="wrap",
        ),
        rx.text_area(
            value=OtrosPedidoState.oe_edit_detalle,
            on_change=OtrosPedidoState.set_oe_edit_detalle,
            rows="3",
            width="100%",
            font_size="12px",
        ),
        rx.hstack(
            rx.button(
                "Cancelar",
                type="button",
                variant="outline",
                size="2",
                on_click=OtrosPedidoState.oe_cancelar_editar,
            ),
            rx.button(
                "💾 Guardar Cambios",
                type="button",
                size="2",
                bg=BOTON_SECUNDARIO,
                color="white",
                on_click=OtrosPedidoState.oe_guardar_edicion,
            ),
            spacing="2",
        ),
        padding="10px",
        border="1px solid var(--amber-6)",
        border_radius="6px",
        bg="var(--amber-1)",
        width="100%",
        spacing="2",
        align="start",
    )


def _tab_otros_examenes() -> rx.Component:
    return rx.box(
     _dlg_oe_nuevo(),
     rx.vstack(
        # ── Aviso SOAP inválido ───────────────────────────────────────────────
        rx.cond(
            OtrosPedidoState.oe_deshabilitado,
            rx.hstack(
                rx.icon("lock", size=13, color="var(--red-9)"),
                rx.text(
                    "El pedido se habilitará cuando exista un SOAP válido guardado.",
                    font_size="11px",
                    color="var(--red-9)",
                ),
                padding="6px 10px",
                bg="var(--red-2)",
                border_radius="6px",
                width="100%",
                align="center",
                spacing="2",
            ),
            rx.text(""),
        ),
        # ── Mensaje de error ──────────────────────────────────────────────────
        rx.cond(
            OtrosPedidoState.oe_error != "",
            rx.hstack(
                rx.icon("triangle-alert", size=13, color="var(--red-9)"),
                rx.text(OtrosPedidoState.oe_error, font_size="11px", color="var(--red-9)"),
                padding="4px 8px",
                bg="var(--red-2)",
                border_radius="4px",
                width="100%",
                align="center",
                spacing="2",
            ),
            rx.text(""),
        ),
        # ── Select diagnóstico ────────────────────────────────────────────────
        rx.hstack(
            rx.text(
                "Diagnóstico del pedido:",
                font_size="12px",
                font_weight="600",
                white_space="nowrap",
                color="var(--gray-11)",
            ),
            rx.select.root(
                rx.select.trigger(placeholder="— seleccione diagnóstico —", width="100%"),
                rx.select.content(
                    rx.foreach(
                        OtrosPedidoState.oe_opciones_diag,
                        lambda d: rx.select.item(d[1], value=d[0]),
                    ),
                ),
                value=OtrosPedidoState.oe_val_diag,
                on_change=OtrosPedidoState.set_oe_lk_diagnostico,
                disabled=OtrosPedidoState.oe_deshabilitado,
                width="100%",
                size="2",
            ),
            width="100%",
            align="center",
            spacing="2",
        ),
        rx.divider(),
        # ── Tabla + botones dinámicos por tipo ────────────────────────────────
        rx.vstack(
            rx.hstack(
                rx.text(
                    "Exámenes solicitados",
                    font_size="11px",
                    font_weight="600",
                    color=TABLE_HEADER_COLOR,
                    background=TABLE_HEADER_BG_BLUE,
                    padding_x="8px",
                    padding_y="3px",
                ),
                rx.spacer(),
                rx.cond(
                    OtrosPedidoState.oe_tiene_lista,
                    rx.link(
                        rx.button(
                            rx.icon("printer", size=12),
                            " Imprimir Pedido",
                            type="button",
                            size="1",
                            bg=BOTON_IMPRIMIR,
                            color="white",
                            font_size="0.72em",
                            border="none",
                            cursor="pointer",
                        ),
                        href=OtrosPedidoState.oe_url_reporte,
                        is_external=True,
                    ),
                    rx.fragment(),
                ),
                rx.button(
                    rx.icon("plus", size=13),
                    " Agregar",
                    type="button",
                    size="1",
                    bg=rx.cond(OtrosPedidoState.oe_bloquear_form, BOTON_DESHABILITADO, BOTON_ACCION),
                    color=rx.cond(OtrosPedidoState.oe_bloquear_form, BOTON_DESHABILITADO_TEXTO, "white"),
                    disabled=OtrosPedidoState.oe_bloquear_form,
                    on_click=OtrosPedidoState.oe_abrir_form,
                    cursor=rx.cond(OtrosPedidoState.oe_bloquear_form, "not-allowed", "pointer"),
                    border="none",
                ),
                width="100%",
                align="center",
                spacing="2",
            ),
            rx.cond(
                OtrosPedidoState.oe_tiene_lista,
                rx.scroll_area(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Tipo Examen", style=_OE_TH),
                                rx.table.column_header_cell("Alias",       style=_OE_TH),
                                rx.table.column_header_cell("Examen",      style=_OE_TH),
                                rx.table.column_header_cell("Detalle",     style=_OE_TH),
                                rx.table.column_header_cell("",            style={**_OE_TH, "width": "52px"}),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(OtrosPedidoState.oe_lista, _fila_oe),
                        ),
                        width="100%",
                        size="1",
                    ),
                    max_height="280px",
                    width="100%",
                ),
                rx.center(
                    rx.text(
                        "Sin exámenes. Seleccione un diagnóstico y use «Agregar» para añadir.",
                        font_size="11px",
                        color="var(--gray-9)",
                        text_align="center",
                    ),
                    padding_y="20px",
                    width="100%",
                ),
            ),
            border="1px solid var(--gray-4)",
            border_radius="6px",
            overflow="hidden",
            width="100%",
            spacing="0",
            align="start",
        ),
        # ── Formulario — edición ──────────────────────────────────────────────
        rx.cond(
            OtrosPedidoState.oe_editando_fila,
            _form_oe_editar(),
            rx.text(""),
        ),
        spacing="3",
        width="100%",
        align="start",
        padding_top="8px",
    ),   # end rx.vstack
    width="100%",
   )


def offcanvas_pedido_examenes():
    """Panel lateral — Pedido de Exámenes de Laboratorio."""
    _th = {"fontSize": "10px", "padding": "2px 4px", "background": TABLE_HEADER_BG_BLUE, "color": TABLE_HEADER_COLOR}

    return rx.box(
        # ── Overlay ───────────────────────────────────────────────────────────
        rx.cond(
            AtencionState.offcanvas_pedido_examenes,
            rx.box(
                on_click=AtencionState.cierra_offcanvas_pedido_examenes,
                position="fixed",
                top="0",
                left="0",
                width="100%",
                height="100%",
                bg="rgba(0,0,0,0.2)",
                z_index="98",
                transition="opacity 0.3s ease-in-out",
            ),
        ),
        # ── Panel ─────────────────────────────────────────────────────────────
        rx.box(
            rx.vstack(

                # ── Cabecera ──────────────────────────────────────────────────
                rx.hstack(
                    rx.text(
                        "🔬 Pedido de Exámenes",
                        font_weight="bold",
                        font_size="1.05em",
                    ),
                    width="100%",
                    align="center",
                    padding_bottom="8px",
                    border_bottom="1px solid var(--gray-5)",
                ),

                # ── Tabs: Laboratorio / Imagen / Otros ────────────────────────
                rx.tabs.root(
                    rx.tabs.list(
                        rx.tabs.trigger("Exámenes Laboratorio", value="lab", size="2"),
                        rx.tabs.trigger("Otros Exámenes",       value="otros",  size="2"),
                    ),

                    # ── TAB Laboratorio ───────────────────────────────────────
                    rx.tabs.content(
                        rx.vstack(
                            # ── Barra de acciones ─────────────────────────────
                            rx.hstack(
                                rx.spacer(),
                                # Indicador "Guardado"
                                rx.cond(
                                    PedidoExamenesState.pe_guardado_ok,
                                    rx.hstack(
                                        rx.icon("circle-check", size=13, color="var(--green-9)"),
                                        rx.text("Guardado", font_size="11px", color="var(--green-9)"),
                                        on_click=PedidoExamenesState.pe_cerrar_guardado_ok,
                                        cursor="pointer",
                                        align="center",
                                        spacing="1",
                                    ),
                                    rx.text(""),
                                ),
                                # Botón Imprimir — visible solo cuando está grabado
                                rx.cond(
                                    PedidoExamenesState.pe_grabado,
                                    rx.link(
                                        rx.button(
                                            "🖨️ Imprimir",
                                            type="button",
                                            bg=BOTON_IMPRIMIR,
                                            color="white",
                                            font_size="0.75em",
                                            border="none",
                                            cursor="pointer",
                                        ),
                                        href=AtencionState.url_reporte_pedido_laboratorio,
                                        is_external=True,
                                    ),
                                    rx.text(""),
                                ),
                                # Botón 3 estados: Grabar / Editar / Guardar Cambios
                                rx.cond(
                                    PedidoExamenesState.pe_campos_bloqueados,
                                    rx.button(
                                        "✏️ Editar Pedido",
                                        type="button",
                                        on_click=PedidoExamenesState.pe_editar,
                                        bg=BOTON_ACCION,
                                        color="white",
                                        font_size="0.75em",
                                        border="none",
                                        cursor="pointer",
                                    ),
                                    rx.cond(
                                        PedidoExamenesState.pe_editando,
                                        rx.button(
                                            "💾 Guardar Cambios",
                                            type="button",
                                            on_click=PedidoExamenesState.pe_guardar_cambios,
                                            bg=BOTON_SECUNDARIO,
                                            color="white",
                                            font_size="0.75em",
                                            border="none",
                                            cursor="pointer",
                                        ),
                                        rx.button(
                                            "💾 Grabar Pedido",
                                            type="button",
                                            on_click=PedidoExamenesState.pe_grabar,
                                            disabled=PedidoExamenesState.pe_deshabilitado,
                                            bg=rx.cond(
                                                PedidoExamenesState.pe_deshabilitado,
                                                BOTON_DESHABILITADO,
                                                BOTON_SECUNDARIO,
                                            ),
                                            color=rx.cond(
                                                PedidoExamenesState.pe_deshabilitado,
                                                BOTON_DESHABILITADO_TEXTO,
                                                "white",
                                            ),
                                            font_size="0.75em",
                                            border="none",
                                            cursor=rx.cond(
                                                PedidoExamenesState.pe_deshabilitado,
                                                "not-allowed",
                                                "pointer",
                                            ),
                                        ),
                                    ),
                                ),
                                width="100%",
                                align="center",
                                spacing="2",
                                padding_bottom="4px",
                            ),
                            # Aviso si no hay SOAP válido
                            rx.cond(
                                PedidoExamenesState.pe_deshabilitado,
                                rx.hstack(
                                    rx.icon("lock", size=13, color="var(--red-9)"),
                                    rx.text(
                                        "El pedido se habilitará cuando exista un SOAP válido guardado.",
                                        font_size="11px",
                                        color="var(--red-9)",
                                    ),
                                    padding="6px 10px",
                                    bg="var(--red-2)",
                                    border_radius="6px",
                                    width="100%",
                                    align="center",
                                    spacing="2",
                                ),
                                rx.text(""),
                            ),
                            # Mensaje de error
                            rx.cond(
                                PedidoExamenesState.pe_error != "",
                                rx.text(
                                    PedidoExamenesState.pe_error,
                                    font_size="11px",
                                    color="var(--red-9)",
                                ),
                                rx.text(""),
                            ),
                            # 3 columnas
                            rx.hstack(
                                # COL 1 — Grupos de exámenes
                                rx.vstack(
                                    rx.text(
                                        "Grupos",
                                        font_size="11px",
                                        font_weight="600",
                                        color=TABLE_HEADER_COLOR,
                                        background=TABLE_HEADER_BG_BLUE,
                                        width="100%",
                                        padding_x="6px",
                                        padding_y="3px",
                                    ),
                                    rx.scroll_area(
                                        rx.table.root(
                                            rx.table.body(
                                                rx.foreach(
                                                    PedidoExamenesState.pe_grupos,
                                                    _fila_grupo,
                                                )
                                            ),
                                            width="100%",
                                            size="1",
                                        ),
                                        height="calc(96vh - 295px)",
                                        width="100%",
                                    ),
                                    width="22%",
                                    spacing="0",
                                    align="start",
                                    border="1px solid var(--gray-4)",
                                    border_radius="4px",
                                    overflow="hidden",
                                    flex_shrink="0",
                                ),
                                # COL 2 — Exámenes disponibles (filtrado por grupo + nombre)
                                rx.vstack(
                                    rx.text(
                                        "Exámenes disponibles",
                                        font_size="11px",
                                        font_weight="600",
                                        color=TABLE_HEADER_COLOR,
                                        background=TABLE_HEADER_BG_BLUE,
                                        width="100%",
                                        padding_x="6px",
                                        padding_y="3px",
                                    ),
                                    rx.input(
                                        placeholder="Buscar examen...",
                                        value=PedidoExamenesState.pe_filtro_nombre,
                                        on_change=PedidoExamenesState.set_pe_filtro_nombre,
                                        font_size="12px",
                                        width="100%",
                                        size="1",
                                        disabled=PedidoExamenesState.pe_deshabilitado,
                                        border_radius="0",
                                        border_left="none",
                                        border_right="none",
                                    ),
                                    rx.scroll_area(
                                        rx.table.root(
                                            rx.table.header(
                                                rx.table.row(
                                                    rx.table.column_header_cell("Examen", style=_th),
                                                    rx.table.column_header_cell("",       style={**_th, "width": "26px"}),
                                                )
                                            ),
                                            rx.table.body(
                                                rx.foreach(
                                                    PedidoExamenesState.pe_catalogo_filtrado,
                                                    _fila_examen_disponible,
                                                )
                                            ),
                                            width="100%",
                                            size="1",
                                        ),
                                        height="calc(96vh - 325px)",
                                        width="100%",
                                    ),
                                    width="40%",
                                    spacing="0",
                                    align="start",
                                    border="1px solid var(--gray-4)",
                                    border_radius="4px",
                                    overflow="hidden",
                                    flex_shrink="0",
                                ),
                                # COL 3 — Exámenes solicitados (sin cambios)
                                rx.vstack(
                                    rx.text(
                                        "Exámenes solicitados",
                                        font_size="11px",
                                        font_weight="600",
                                        color=TABLE_HEADER_COLOR,
                                        background=TABLE_HEADER_BG_BLUE,
                                        width="100%",
                                        padding_x="6px",
                                        padding_y="3px",
                                    ),
                                    rx.scroll_area(
                                        rx.cond(
                                            PedidoExamenesState.pe_tiene_seleccionados,
                                            rx.table.root(
                                                rx.table.header(
                                                    rx.table.row(
                                                        rx.table.column_header_cell("Examen", style=_th),
                                                        rx.table.column_header_cell("Grupo",  style=_th),
                                                        rx.table.column_header_cell("",       style={**_th, "width": "26px"}),
                                                    )
                                                ),
                                                rx.table.body(
                                                    rx.foreach(
                                                        PedidoExamenesState.pe_seleccionados_con_fondo,
                                                        _fila_examen_seleccionado,
                                                    )
                                                ),
                                                width="100%",
                                                size="1",
                                            ),
                                            rx.center(
                                                rx.text(
                                                    "Haga clic en + para agregar exámenes",
                                                    font_size="11px",
                                                    color="var(--gray-9)",
                                                    text_align="center",
                                                ),
                                                width="100%",
                                                padding_top="24px",
                                            ),
                                        ),
                                        height="calc(96vh - 295px)",
                                        width="100%",
                                    ),
                                    width="38%",
                                    spacing="0",
                                    align="start",
                                    border="1px solid var(--gray-4)",
                                    border_radius="4px",
                                    overflow="hidden",
                                ),
                                width="100%",
                                spacing="2",
                                align="start",
                            ),
                            spacing="3",
                            width="100%",
                            align="start",
                            padding_top="8px",
                        ),
                        value="lab",
                        padding="0",
                    ),

                    # ── TAB Otros Exámenes ─────────────────────────────────────
                    rx.tabs.content(
                        _tab_otros_examenes(),
                        value="otros",
                        padding="0",
                    ),

                    default_value="lab",
                    width="100%",
                ),

                spacing="3",
                width="100%",
                padding="12px",
                align="start",
            ),
            position="fixed",
            top="65px",
            right="10px",
            height="calc(96% - 65px)",
            #Ancho offcanvas_pedido_examenes
            width=rx.cond(State.show_panel_izq, "55vw", "96vw"),
            bg="white",
            box_shadow="-2px 0 10px rgba(0,0,0,0.3)",
            z_index=rx.cond(AtencionState.offcanvas_pedido_examenes, "101", "99"),
            padding="0.5em",
            transform=rx.cond(
                AtencionState.offcanvas_pedido_examenes,
                "translateX(0)",
                "translateX(100%)",
            ),
            transition="transform 0.3s ease-in-out, width 0.3s ease-in-out",
        ),
    )


def offcanvas_resultados_examenes():
    """Panel lateral para los resultados de exámenes de la atención actual."""
    return rx.box(
        rx.cond(
            AtencionState.offcanvas_resultados_examenes,
            rx.box(
                on_click=AtencionState.cierra_offcanvas_resultados_examenes,
                position="fixed",
                top="0",
                left="0",
                width="100%",
                height="100%",
                bg="rgba(0,0,0,0.2)",
                z_index="98",
                transition="opacity 0.3s ease-in-out",
            ),
        ),
        rx.box(
            rx.vstack(
                # ── Cabecera ─────────────────────────────────────────────────
                rx.hstack(
                    rx.text(
                        "🔬 Imágenes",
                        font_weight="bold",
                        font_size="15px",
                    ),
                    rx.spacer(),
                    rx.cond(State.puede_escribir, upload_resultados_titulo(), rx.fragment()),
                    ##rx.button(
                    ##    "✕",
                    ##    on_click=AtencionState.cierra_offcanvas_resultados_examenes,
                    ##    variant="ghost",
                    ##    cursor="pointer",
                    ##    font_size="16px",
                    ##    type="button",
                    ##),
                    width="100%",
                    align="center",
                    spacing="2",
                    padding="8px 12px",
                    border_bottom="1px solid var(--gray-5)",
                    flex_shrink="0",
                ),
                # ── Contenido ────────────────────────────────────────────────
                panel_resultados_examenes(),
                spacing="0",
                width="100%",
                height="100%",
                overflow="hidden",
            ),
            position="fixed",
            top="65px",
            right="10px",
            height="calc(96% - 65px)",
            #Ancho offcanvas_resultados_examenes
            width=rx.cond(State.show_panel_izq, "55vw", "96vw"),
            bg="white",
            box_shadow="-2px 0 10px rgba(0,0,0,0.3)",
            z_index=rx.cond(AtencionState.offcanvas_resultados_examenes, "101", "99"),
            padding="0",
            transform=rx.cond(
                AtencionState.offcanvas_resultados_examenes,
                "translateX(0)",
                "translateX(100%)",
            ),
            transition="transform 0.3s ease-in-out, width 0.3s ease-in-out",
            overflow="hidden",
        ),
    )


# ── Offcanvas Laboratorio ─────────────────────────────────────────────────────

def _semaforo_lab(fila_id_var, rango_var) -> rx.Component:
    """Selector vertical: barra de color encima + select con calificación."""
    _color = rx.match(
        rango_var,
        ("BAJO",     "var(--gray-9)"),
        ("EN_RANGO", "var(--green-9)"),
        ("SOBRE",    "var(--orange-9)"),
        ("ALTO",     "var(--red-9)"),
        "var(--green-9)",
    )
    return rx.vstack(
        rx.box(
            width="66px", height="8px",
            border_radius="3px 3px 0 0",
            background=_color,
        ),
        rx.select.root(
            rx.select.trigger(
                width="66px",
                style={"font_size": "9px", "height": "22px", "border_radius": "0 0 3px 3px"},
            ),
            rx.select.content(
                rx.select.item("Bajo",   value="BAJO",     style={"color": "var(--gray-9)"}),
                rx.select.item("En Rango", value="EN_RANGO", style={"color": "var(--green-9)"}),
                rx.select.item("Sobre",  value="SOBRE",    style={"color": "var(--orange-9)"}),
                rx.select.item("Alto",   value="ALTO",     style={"color": "var(--red-9)"}),
            ),
            value=rango_var,
            on_change=LaboratorioState.lab_set_rango(fila_id_var),
            size="1",
        ),
        spacing="0",
        align="center",
        flex_shrink="0",
    )


def _fila_lab(fila: dict) -> rx.Component:
    return rx.hstack(
        # Eliminar fila — solo puede_escribir
        rx.cond(
            State.puede_escribir,
            rx.button(
                rx.icon("trash-2", size=11),
                on_click=LaboratorioState.lab_eliminar_fila(fila["fila_id"]),
                variant="ghost", type="button", size="1",
                color="var(--red-9)", flex_shrink="0",
                style={"padding": "0 2px"},
            ),
            rx.fragment(),
        ),
        # Col 1 — Nombre examen (combobox con datalist)
        rx.el.input(
            list="lab-examenes-datalist",
            placeholder="Buscar examen…",
            value=fila["busqueda"],
            on_change=LaboratorioState.lab_set_busqueda(fila["fila_id"]),
            style={
                "flex": "1",
                "min_width": "140px",
                "height": "24px",
                "font_size": "12px",
                "padding": "0 6px",
                "border": "1px solid var(--gray-6)",
                "border_radius": "var(--radius-2)",
                "background": "var(--color-background)",
                "color": "var(--gray-12)",
                "outline": "none",
                "width": "100%",
            },
        ),
        # Col 2 — Valor numérico
        rx.el.input(
            type="number",
            placeholder="0.00",
            value=fila["valor"],
            on_change=LaboratorioState.lab_set_valor(fila["fila_id"]),
            style={
                "width": "68px",
                "flex_shrink": "0",
                "height": "24px",
                "font_size": "12px",
                "padding": "0 4px",
                "border": "1px solid var(--gray-6)",
                "border_radius": "var(--radius-2)",
                "background": "var(--color-background)",
                "color": "var(--gray-12)",
                "outline": "none",
            },
        ),
        # Col 3 — Semáforo rango
        _semaforo_lab(fila["fila_id"], fila["en_rango"]),
        # Col 4 — Observación
        rx.el.input(
            placeholder="Obs…",
            value=fila["observacion"],
            on_change=LaboratorioState.lab_set_obs(fila["fila_id"]),
            style={
                "flex": "1",
                "min_width": "60px",
                "height": "24px",
                "font_size": "12px",
                "padding": "0 6px",
                "border": "1px solid var(--gray-6)",
                "border_radius": "var(--radius-2)",
                "background": "var(--color-background)",
                "color": "var(--gray-12)",
                "outline": "none",
                "width": "100%",
            },
        ),
        spacing="1",
        width="100%",
        align="center",
        padding_y="2px",
    )


def offcanvas_laboratorio() -> rx.Component:
    """Panel lateral (20 vw) para ingresar resultados de laboratorio."""
    _COL_HDR = {"font_size": "9px", "font_weight": "600", "color": "var(--gray-11)"}
    return rx.box(
        rx.vstack(
            # ── Encabezado ───────────────────────────────────────────────────
            rx.hstack(
                rx.icon("flask-conical", size=15, color="var(--blue-9)"),
                rx.text("Laboratorio", font_weight="700", font_size="14px"),
                rx.spacer(),
                rx.button(
                    rx.icon("panel-right-close", size=15),
                    on_click=LaboratorioState.lab_cerrar,
                    variant="ghost", type="button", size="1",
                    title="Cerrar panel",
                ),
                width="100%", align="center",
                padding="8px 10px",
                border_bottom="1px solid var(--gray-5)",
                flex_shrink="0",
            ),
            # ── Cuerpo scrollable ─────────────────────────────────────────────
            rx.vstack(
                # Fecha
                rx.vstack(
                    rx.text("Fecha del Examen", font_size="11px", font_weight="600"),
                    rx.input(
                        value=LaboratorioState.lab_fecha,
                        on_change=LaboratorioState.lab_set_fecha,
                        type="date", size="1", width="100%",
                    ),
                    spacing="1", width="100%",
                ),
                rx.separator(width="100%"),
                # Datalist compartido para todas las filas
                rx.el.datalist(
                    rx.foreach(
                        LaboratorioState.lab_catalogo,
                        lambda e: rx.el.option(value=e["display"]),
                    ),
                    id="lab-examenes-datalist",
                ),
                # Encabezados tabla
                rx.hstack(
                    rx.box(width="22px", flex_shrink="0"),
                    rx.text("Nombre Examen", **_COL_HDR, flex="1", min_width="140px"),
                    rx.text("Valor",         **_COL_HDR, width="68px", flex_shrink="0"),
                    rx.text("Rango",         **_COL_HDR, width="80px", flex_shrink="0"),
                    rx.text("Obs.",          **_COL_HDR, flex="1", min_width="60px"),
                    spacing="1", width="100%", align="center",
                    padding_y="2px",
                ),
                rx.divider(width="100%", border_color="var(--gray-4)"),
                # Filas
                rx.vstack(
                    rx.foreach(LaboratorioState.lab_filas, _fila_lab),
                    spacing="1", width="100%",
                ),
                # Agregar fila — solo puede_escribir
                rx.cond(
                    State.puede_escribir,
                    rx.button(
                        rx.icon("plus", size=12), "Agregar fila",
                        on_click=LaboratorioState.lab_agregar_fila,
                        variant="ghost", type="button", size="1",
                        color="var(--blue-9)", width="100%",
                    ),
                    rx.fragment(),
                ),
                # Error
                rx.cond(
                    LaboratorioState.lab_error != "",
                    rx.text(
                        LaboratorioState.lab_error,
                        font_size="11px", color="var(--red-9)",
                        padding_top="4px",
                    ),
                ),
                spacing="2", width="100%",
                padding="10px",
                overflow_y="auto",
                flex="1",
                min_height="0",
            ),
            # ── Pie ─────────────────────────────────────────────────────────
            rx.hstack(
                rx.button(
                    "Cancelar",
                    on_click=LaboratorioState.lab_cerrar,
                    variant="soft", color_scheme="gray",
                    type="button", size="2",
                ),
                rx.spacer(),
                rx.cond(
                    State.puede_escribir,
                    rx.button(
                        "Guardar",
                        on_click=LaboratorioState.lab_guardar,
                        color_scheme="blue", type="button", size="2",
                        loading=LaboratorioState.lab_guardando,
                    ),
                    rx.fragment(),
                ),
                width="100%", padding="8px 10px",
                border_top="1px solid var(--gray-5)",
                flex_shrink="0",
            ),
            spacing="0", width="100%", height="100%", overflow="hidden",
        ),
        position="fixed",
        top="60px",
        right="0",
        height="calc(100% - 60px)",
        width="40vw",
        min_width="380px",
        background="white",
        box_shadow="-3px 0 12px rgba(0,0,0,0.18)",
        z_index=rx.cond(LaboratorioState.lab_open, "115", "99"),
        transform=rx.cond(
            LaboratorioState.lab_open,
            "translateX(0)",
            "translateX(100%)",
        ),
        transition="transform 0.3s ease-in-out",
        overflow="hidden",
    )


# ── Offcanvas de Configuración (página pacientes) ─────────────────────────────
def offcanvas_config() -> rx.Component:
    return rx.box(
        # Overlay
        rx.cond(
            State.offcanvas_config,
            rx.box(
                position="fixed",
                top="0",
                left="0",
                width="100%",
                height="100%",
                bg="rgba(0,0,0,0.2)",
                z_index="998",
                on_click=State.toggle_offcanvas_config,
            ),
        ),
        # Panel lateral izquierdo
        rx.box(
            rx.vstack(
                rx.text(
                    "Configuración",
                    font_size="13px", font_weight="600",
                    color="var(--gray-11)", padding_bottom="8px",
                ),
                rx.divider(),
                # Sección Admin — solo visible para ADMIN
                rx.cond(
                    State.puede_admin,
                    rx.vstack(
                        rx.link(
                            rx.button(
                                rx.icon("file_spreadsheet", size=14),
                                rx.text("Formatos Impresos", font_size="12px"),
                                variant="ghost", width="100%", justify="start",
                                type="button",
                                on_click=State.toggle_offcanvas_config,
                            ),
                            href="/config/reportes",
                            width="100%",
                            text_decoration="none",
                        ),
                        rx.link(
                            rx.button(
                                rx.icon("users", size=14),
                                rx.text("Usuarios", font_size="12px"),
                                variant="ghost", width="100%", justify="start",
                                type="button",
                                on_click=State.toggle_offcanvas_config,
                            ),
                            href="/config/usuarios",
                            width="100%",
                            text_decoration="none",
                        ),
                        spacing="0", width="100%",
                    ),
                    rx.fragment(),
                ),
                spacing="2",
                align="start",
                padding="12px",
                width="100%",
            ),
            position="fixed",
            top="60px",
            left="0",
            height="calc(100% - 60px)",
            width="200px",
            bg="white",
            box_shadow="2px 0 10px rgba(0,0,0,0.2)",
            z_index="999",
            transform=rx.cond(
                State.offcanvas_config,
                "translateX(0)",
                "translateX(-100%)",
            ),
            transition="transform 0.3s ease-in-out",
        ),
    )


def dialogo_nuevo_ant_familiar() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Nuevo Antecedente Familiar"),
            rx.vstack(
                rx.vstack(
                    rx.text("Fecha de registro", font_size="12px", font_weight="500", color="black"),
                    rx.input(
                        value=NuevoAntFamiliarState.naf_fecha_registro,
                        on_change=NuevoAntFamiliarState.set_naf_fecha_registro,
                        type="date",
                        size="2",
                        width="100%",
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.text("Descripción", font_size="12px", font_weight="500", color="black"),
                        rx.text("*", color="var(--red-9)", font_size="12px"),
                        spacing="1",
                    ),
                    rx.text_area(
                        value=NuevoAntFamiliarState.naf_descripcion,
                        on_change=NuevoAntFamiliarState.set_naf_descripcion,
                        placeholder="Describa el antecedente familiar...",
                        height="120px",
                        width="100%",
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.cond(
                    NuevoAntFamiliarState.naf_error != "",
                    rx.text(NuevoAntFamiliarState.naf_error, color="var(--red-9)", font_size="12px"),
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray", type="button"),
                    ),
                    rx.button(
                        "Guardar",
                        color_scheme="blue",
                        on_click=NuevoAntFamiliarState.guardar_naf,
                        type="button",
                    ),
                    justify="end",
                    width="100%",
                    spacing="2",
                ),
                spacing="3",
                width="100%",
            ),
            max_width="480px",
        ),
        open=NuevoAntFamiliarState.naf_dialog_open,
        on_open_change=NuevoAntFamiliarState.set_naf_dialog_open,
    )


def dialogo_nueva_alergia() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Nueva Alergia"),
            rx.vstack(
                rx.vstack(
                    rx.hstack(
                        rx.text("Sustancia", font_size="12px", font_weight="500", color="black"),
                        rx.text("*", color="var(--red-9)", font_size="12px"),
                        spacing="1",
                    ),
                    rx.input(
                        value=NuevaAlergiaState.naa_sustancia,
                        on_change=NuevaAlergiaState.set_naa_sustancia,
                        placeholder="Nombre de la sustancia alérgena...",
                        size="2",
                        width="100%",
                        auto_focus=True,
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.cond(
                    NuevaAlergiaState.naa_error != "",
                    rx.text(NuevaAlergiaState.naa_error, color="var(--red-9)", font_size="12px"),
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray", type="button"),
                    ),
                    rx.button(
                        "Guardar",
                        color_scheme="red",
                        on_click=NuevaAlergiaState.guardar_naa,
                        type="button",
                    ),
                    justify="end",
                    width="100%",
                    spacing="2",
                ),
                spacing="3",
                width="100%",
            ),
            max_width="400px",
        ),
        open=NuevaAlergiaState.naa_dialog_open,
        on_open_change=NuevaAlergiaState.set_naa_dialog_open,
    )


# ── Certificados ──────────────────────────────────────────────────────────────

_TH_CERT = {"padding": "3px 8px", "font_size": "13px", "font_weight": "600",
             "background": TABLE_HEADER_BG_PETROLEO, "color": TABLE_HEADER_COLOR,
             "white_space": "nowrap"}
_TD_CERT = {"padding": "3px 8px", "font_size": "13px", "vertical_align": "middle"}


def _formulario_campos_cert() -> rx.Component:
    """Campos compartidos por el diálogo nuevo/tardío y el diálogo de edición."""
    bloqueado = CertificadoState.cert_grabado
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.text("Reposo desde *", font_size="13px", font_weight="500"),
                rx.input(value=CertificadoState.cert_reposo_desde,
                         on_change=CertificadoState.set_cert_reposo_desde,
                         type="date", size="2", width="150px", disabled=bloqueado),
                spacing="1",
            ),
            rx.vstack(
                rx.text("Días de reposo", font_size="13px", font_weight="500"),
                rx.input(value=CertificadoState.cert_dias_reposo.to(str),
                         on_change=CertificadoState.set_cert_dias_reposo,
                         type="number", min="1", size="2", width="90px",
                         disabled=bloqueado),
                spacing="1",
            ),
            rx.vstack(
                rx.text("Reposo hasta", font_size="13px", font_weight="500",
                        color="var(--gray-10)"),
                rx.input(value=CertificadoState.cert_reposo_hasta,
                         type="date", size="2", width="150px",
                         read_only=True,
                         style={"background": "var(--gray-2)", "color": "var(--gray-10)"}),
                spacing="1",
            ),
            spacing="4", flex_wrap="wrap",
        ),
        rx.vstack(
            rx.text("Contingencia", font_size="13px", font_weight="500"),
            rx.input(value=CertificadoState.cert_contingencia,
                     on_change=CertificadoState.set_cert_contingencia,
                     placeholder="Ej. Enfermedad común", size="2", width="100%",
                     disabled=bloqueado),
            spacing="1", width="100%",
        ),
        rx.hstack(
            rx.checkbox("Presenta síntomas",
                        checked=CertificadoState.cert_presenta_sintomas,
                        on_change=CertificadoState.set_cert_presenta_sintomas,
                        size="2", disabled=bloqueado),
            rx.checkbox("Aislamiento",
                        checked=CertificadoState.cert_aislamiento,
                        on_change=CertificadoState.set_cert_aislamiento,
                        size="2", disabled=bloqueado),
            spacing="4",
        ),
        rx.vstack(
            rx.text("Ocupación", font_size="13px", font_weight="500"),
            rx.input(value=CertificadoState.cert_ocupacion,
                     on_change=CertificadoState.set_cert_ocupacion,
                     size="2", width="100%", disabled=bloqueado),
            spacing="1", width="100%",
        ),
        rx.vstack(
            rx.text("Lugar de trabajo", font_size="13px", font_weight="500"),
            rx.input(value=CertificadoState.cert_lugar_trabajo,
                     on_change=CertificadoState.set_cert_lugar_trabajo,
                     size="2", width="100%", disabled=bloqueado),
            spacing="1", width="100%",
        ),
        rx.vstack(
            rx.text("Observación", font_size="13px", font_weight="500"),
            rx.text_area(value=CertificadoState.cert_observacion,
                         on_change=CertificadoState.set_cert_observacion,
                         rows="3", size="2", width="100%", disabled=bloqueado),
            spacing="1", width="100%",
        ),
        rx.cond(
            CertificadoState.cert_error != "",
            rx.text(CertificadoState.cert_error, font_size="13px",
                    color="var(--red-9)", font_weight="500"),
            rx.fragment(),
        ),
        spacing="3", width="100%",
    )


def dialogo_cert_sin_soap() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.icon("triangle_alert", size=32, color="var(--amber-9)"),
                rx.text("SOAP requerido", font_size="14px", font_weight="600"),
                rx.text(
                    "Para emitir un certificado debe registrar un SOAP en la atención actual.",
                    font_size="12px", color="var(--gray-11)", text_align="center",
                    max_width="280px",
                ),
                rx.dialog.close(
                    rx.button("Entendido", size="2", type="button"),
                ),
                align="center", spacing="3", padding="8px",
            ),
            max_width="340px",
        ),
        open=CertificadoState.cert_dlg_sin_soap,
        on_open_change=CertificadoState.set_cert_dlg_sin_soap,
    )


def dialogo_formulario_certificado() -> rx.Component:
    """Diálogo compartido para Nuevo Certificado y Certificado Tardío."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon("file_badge", size=16, color="var(--blue-9)"),
                    rx.text("Certificado Médico", font_size="14px", font_weight="600"),
                    rx.text(State.nombre_paciente_seleccionado,
                            font_size="11px", color="var(--gray-10)"),
                    spacing="2", align="center",
                ),
            ),
            rx.vstack(
                _formulario_campos_cert(),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray",
                                  size="2", type="button"),
                    ),
                    rx.button(
                        "Grabar Certificado",
                        size="2", type="button", color_scheme="blue",
                        disabled=CertificadoState.cert_grabado,
                        on_click=CertificadoState.cert_guardar,
                    ),
                    rx.link(
                        rx.button(
                            rx.icon("printer", size=14),
                            "Imprimir",
                            size="2", type="button", color_scheme="green",
                            disabled=CertificadoState.cert_grabado == False,
                        ),
                        href=CertificadoState.cert_url_reporte,
                        is_external=True,
                    ),
                    justify="end", width="100%", spacing="2", flex_wrap="wrap",
                ),
                spacing="3", width="100%", padding_top="8px",
            ),
            max_width="520px", width="95vw",
        ),
        open=CertificadoState.cert_dlg_formulario,
        on_open_change=CertificadoState.set_cert_dlg_formulario,
    )


def dialogo_atenciones_tardias() -> rx.Component:
    """Lista de atenciones pasadas para seleccionar donde crear un certificado tardío."""
    def _fila_atencion_tardia(a: dict) -> rx.Component:
        return rx.table.row(
            rx.table.cell(
                rx.text(a["fecha_atencion"], font_size="11px", white_space="nowrap"),
                **_TD_CERT,
            ),
            rx.table.cell(
                rx.text(a["motivo_consulta"], font_size="11px"),
                **_TD_CERT,
            ),
            rx.table.cell(
                rx.button(
                    rx.icon("file_plus", size=13),
                    "Crear certificado",
                    size="1", type="button", variant="soft",
                    on_click=CertificadoState.cert_abrir_formulario_tardio(a["id_atencion"]),
                ),
                **_TD_CERT,
            ),
            _hover={"background": ROW_HOVER_BG},
        )

    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.vstack(
                    rx.hstack(
                        rx.icon("clock", size=16, color="var(--amber-9)"),
                        rx.text("Certificado para una atención anterior",
                                    font_size="13px", font_weight="600"),    
                    ),
                    rx.text("Seleccione la atención que origina el certificao",font_size="10px"),
                ),
                spacing="2", align="center",
            ),
            rx.vstack(
                rx.cond(
                    CertificadoState.cert_error != "",
                    rx.text(CertificadoState.cert_error, font_size="11px",
                            color="var(--red-9)"),
                    rx.fragment(),
                ),
                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Fecha Atención", **_TH_CERT),
                                rx.table.column_header_cell("Motivo Consulta", **_TH_CERT),
                                rx.table.column_header_cell("", **_TH_CERT),
                            ),
                        ),
                        rx.table.body(
                            rx.foreach(State.lista_atenciones, _fila_atencion_tardia),
                        ),
                        width="100%", size="1",
                    ),
                    overflow_y="auto", max_height="50vh",
                    border="1px solid var(--gray-4)", border_radius="4px",
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cerrar", variant="soft", color_scheme="gray",
                                  size="2", type="button"),
                    ),
                    justify="end", width="100%",
                ),
                spacing="3", width="100%", padding_top="8px",
            ),
            max_width="640px", width="95vw",
        ),
        open=CertificadoState.cert_dlg_atenciones,
        on_open_change=CertificadoState.set_cert_dlg_atenciones,
    )


def dialogo_editar_certificado() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon("pencil", size=15, color="var(--blue-9)"),
                    rx.text("Editar Certificado", font_size="14px", font_weight="600"),
                    spacing="2", align="center",
                ),
            ),
            rx.vstack(
                _formulario_campos_cert(),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray",
                                  size="2", type="button"),
                    ),
                    rx.button(
                        "Guardar Cambios",
                        size="2", type="button", color_scheme="blue",
                        on_click=CertificadoState.cert_guardar_edicion,
                    ),
                    rx.link(
                        rx.button(
                            rx.icon("printer", size=14),
                            "Imprimir",
                            size="2", type="button", color_scheme="green",
                        ),
                        href=CertificadoState.cert_url_reporte,
                        is_external=True,
                    ),
                    justify="end", width="100%", spacing="2", flex_wrap="wrap",
                ),
                spacing="3", width="100%", padding_top="8px",
            ),
            max_width="520px", width="95vw",
        ),
        open=CertificadoState.cert_dlg_editar,
        on_open_change=CertificadoState.set_cert_dlg_editar,
    )


def offcanvas_certificados() -> rx.Component:
    """Panel lateral derecho con todos los certificados del paciente actual."""
    def _fila_cert(c: dict) -> rx.Component:
        puede_editar = CertificadoState.cert_hoy == c["fecha_date"]
        return rx.table.row(
            rx.table.cell(
                rx.text(c["fecha_atencion"], font_size="10px", white_space="nowrap"),
                **_TD_CERT,
            ),
            rx.table.cell(
                rx.text(c["motivo_consulta"], font_size="10px"),
                **_TD_CERT,
            ),
            rx.table.cell(
                rx.text(c["contingencia"], font_size="10px"),
                **_TD_CERT,
            ),
            rx.table.cell(
                rx.text(c["observacion"], font_size="10px",
                        max_width="180px", overflow="hidden",
                        text_overflow="ellipsis", white_space="nowrap"),
                **_TD_CERT,
            ),
            rx.table.cell(
                rx.cond(
                    puede_editar,
                    rx.icon("pencil", size=14, cursor="pointer",
                            color="var(--blue-9)",
                            on_click=CertificadoState.cert_abrir_editar(c["id_certificado"])),
                    rx.icon("pencil", size=14, color="var(--gray-4)"),
                ),
                **_TD_CERT,
            ),
            rx.table.cell(
                rx.link(
                    rx.icon("printer", size=14, cursor="pointer",
                            color="var(--green-9)"),
                    href=CertificadoState.cert_url_reporte,
                    is_external=True,
                    on_click=CertificadoState.cert_imprimir_desde_lista(c["lk_atencion"]),
                ),
                **_TD_CERT,
            ),
            _hover={"background": ROW_HOVER_BG},
        )

    return rx.box(
        rx.cond(
            CertificadoState.cert_offcanvas,
            rx.box(
                on_click=CertificadoState.cert_cerrar_offcanvas,
                position="fixed", top="0", left="0",
                width="100%", height="100%",
                bg="rgba(0,0,0,0.2)", z_index="98",
            ),
        ),
        rx.box(
            rx.vstack(
                # Cabecera
                rx.hstack(
                    rx.icon("file_badge", size=16, color="var(--blue-9)"),
                    rx.text("Historial de Certificados Médicos", font_weight="700", font_size="14px"),
                    rx.spacer(),
                    rx.button("✕", variant="ghost", type="button",
                              on_click=CertificadoState.cert_cerrar_offcanvas,
                              font_size="16px", cursor="pointer"),
                    width="100%", align="center",
                    padding_bottom="8px",
                    border_bottom="1px solid var(--gray-5)",
                ),
                rx.text(State.nombre_paciente_seleccionado,
                        font_size="12px", color="var(--gray-10)"),
                # Tabla
                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Fecha Atención",  **_TH_CERT),
                                rx.table.column_header_cell("Motivo",          **_TH_CERT),
                                rx.table.column_header_cell("Contingencia",    **_TH_CERT),
                                rx.table.column_header_cell("Observación",     **_TH_CERT),
                                rx.table.column_header_cell("Editar",          **_TH_CERT),
                                rx.table.column_header_cell("Imprimir",        **_TH_CERT),
                            ),
                        ),
                        rx.table.body(
                            rx.foreach(CertificadoState.cert_lista, _fila_cert),
                        ),
                        width="100%", size="1",
                    ),
                    overflow_x="auto", overflow_y="auto",
                    max_height="calc(100vh - 200px)",
                    border="1px solid var(--gray-4)", border_radius="4px",
                ),
                spacing="3", width="100%", padding="12px",
            ),
            position="fixed",
            top="65px", right="10px",
            height="calc(96% - 65px)",
            width="70vw",
            bg="white",
            box_shadow="-2px 0 10px rgba(0,0,0,0.3)",
            z_index=rx.cond(CertificadoState.cert_offcanvas, "101", "99"),
            transform=rx.cond(
                CertificadoState.cert_offcanvas,
                "translateX(0)", "translateX(110%)",
            ),
            transition="transform 0.3s ease-in-out",
            border_radius="8px 0 0 8px",
        ),
        dialogo_editar_certificado(),
    )


# ── Tabla historial laboratorio ───────────────────────────────────────────────

def _lab_h_rango_dot(en_rango) -> rx.Component:
    _color = rx.cond(en_rango == "BAJO", "var(--gray-9)",
             rx.cond(en_rango == "EN_RANGO", "var(--green-9)",
             rx.cond(en_rango == "SOBRE", "var(--orange-9)", "var(--red-9)")))
    _label = rx.cond(en_rango == "BAJO", "Bajo",
             rx.cond(en_rango == "EN_RANGO", "Normal",
             rx.cond(en_rango == "SOBRE", "Sobre", "Alto")))
    return rx.hstack(
        rx.box(width="10px", height="10px", border_radius="50%", background=_color, flex_shrink="0"),
        rx.text(_label, font_size="11px"),
        spacing="1", align="center",
    )


def _lab_h_row_g(fila: dict) -> rx.Component:
    _bg = {"background": "var(--orange-3)", "padding": "3px 8px"}
    return rx.table.row(
        rx.table.cell(
            rx.hstack(
                rx.icon(rx.cond(fila["expandido"], "chevron-down", "chevron-right"),
                        size=12, color="var(--orange-11)"),
                rx.text(fila["nombre"], font_weight="bold", font_size="12px", color="var(--orange-11)"),
                spacing="1", align="center",
            ),
            style=_bg, cursor="pointer",
            on_click=LaboratorioState.lab_h_toggle_grupo(fila["gkey"]),
        ),
        rx.table.cell(style=_bg),
        rx.table.cell(style=_bg),
        rx.table.cell(style=_bg),
        rx.table.cell(style=_bg),
        rx.table.cell(style=_bg),
    )


def _lab_h_row_e(fila: dict) -> rx.Component:
    _sel = fila["ekey"] == LaboratorioState.orl_grafico_ekey
    _bg_val = rx.cond(_sel, "var(--orange-4)", "var(--orange-2)")
    _outline = rx.cond(_sel, "2px solid var(--orange-9)", "none")
    _bg = {"padding": "2px 8px"}
    return rx.table.row(
        rx.table.cell(style={"padding": "0"}),
        rx.table.cell(
            rx.hstack(
                rx.icon(rx.cond(fila["expandido"], "chevron-down", "chevron-right"), size=11),
                rx.text(fila["nombre"], font_weight="bold", font_size="11px"),
                rx.cond(_sel, rx.icon("chart-line", size=10, color="var(--orange-9)"), rx.fragment()),
                spacing="1", align="center",
            ),
            style={**_bg, "background": _bg_val, "outline": _outline},
            cursor="pointer",
            on_click=LaboratorioState.orl_lab_click(fila["ekey"], fila["nombre"]),
        ),
        rx.table.cell(style={**_bg, "background": _bg_val}),
        rx.table.cell(style={**_bg, "background": _bg_val}),
        rx.table.cell(style={**_bg, "background": _bg_val}),
        rx.table.cell(style={**_bg, "background": _bg_val}),
    )


def _lab_h_row_r(fila: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(style={"padding": "0"}),
        rx.table.cell(style={"padding": "0"}),
        rx.table.cell(rx.text(fila["fecha"],  font_size="11px"), padding="2px 8px"),
        rx.table.cell(rx.text(fila["valor"],  font_size="11px", font_family="monospace"), padding="2px 8px"),
        rx.table.cell(rx.text(fila["unidad"], font_size="11px", color="var(--gray-10)"), padding="2px 8px"),
        rx.table.cell(_lab_h_rango_dot(fila["en_rango"]), padding="2px 4px"),
    )


def _lab_h_row(fila: dict) -> rx.Component:
    return rx.cond(
        fila["visible"],
        rx.cond(
            fila["tipo"] == "G",
            _lab_h_row_g(fila),
            rx.cond(
                fila["tipo"] == "E",
                _lab_h_row_e(fila),
                _lab_h_row_r(fila),
            ),
        ),
        rx.table.row(style={"display": "none"}),
    )


def tabla_historial_lab() -> rx.Component:
    _TH = {
        "background": "var(--orange-9)", "color": "white",
        "font_size": "11px", "padding": "5px 8px", "white_space": "nowrap",
    }
    return rx.box(
        rx.cond(
            LaboratorioState.lab_h_filas,
            rx.scroll_area(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Grupo",          style=_TH),
                            rx.table.column_header_cell("Nombre Examen",  style=_TH),
                            rx.table.column_header_cell("Fecha",          style=_TH),
                            rx.table.column_header_cell("Valor",          style=_TH),
                            rx.table.column_header_cell("Unidad",         style=_TH),
                            rx.table.column_header_cell("Rango",          style=_TH),
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(LaboratorioState.lab_h_filas, _lab_h_row),
                    ),
                    width="100%",
                    size="1",
                ),
                type="auto",
                height="100%",
                width="100%",
            ),
            rx.center(
                rx.vstack(
                    rx.icon("flask-conical", size=24, color="var(--gray-7)"),
                    rx.text("Sin registros de laboratorio", font_size="12px", color="var(--gray-9)"),
                    align="center", spacing="2",
                ),
                height="100%",
            ),
        ),
        height="100%",
        overflow="hidden",
        width="100%",
    )


# ── Tabla historial signos vitales ────────────────────────────────────────────

def _sv_h_row_e(fila: dict) -> rx.Component:
    _sel = fila["svkey"] == LaboratorioState.orl_grafico_ekey
    _bg_val = rx.cond(_sel, "var(--blue-4)", "var(--blue-2)")
    _outline = rx.cond(_sel, "2px solid var(--blue-9)", "none")
    _bg = {"padding": "2px 8px"}
    return rx.table.row(
        rx.table.cell(
            rx.hstack(
                rx.icon(rx.cond(fila["expandido"], "chevron-down", "chevron-right"), size=11,
                        color="var(--blue-11)"),
                rx.text(fila["nombre"], font_weight="bold", font_size="11px", color="var(--blue-11)"),
                rx.cond(_sel, rx.icon("chart-line", size=10, color="var(--blue-9)"), rx.fragment()),
                spacing="1", align="center",
            ),
            style={**_bg, "background": _bg_val, "outline": _outline},
            cursor="pointer",
            on_click=LaboratorioState.orl_sv_click(fila["svkey"], fila["nombre"]),
        ),
        rx.table.cell(rx.text(fila["unidad"], font_size="11px", color="var(--gray-10)"),
                      style={**_bg, "background": _bg_val}),
        rx.table.cell(rx.text("—", font_size="11px", color="var(--gray-7)"),
                      style={**_bg, "background": _bg_val}),
    )


def _sv_h_row_r(fila: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(
            rx.text(fila["fecha"], font_size="11px", color="var(--gray-10)"),
            padding="2px 8px 2px 24px",
        ),
        rx.table.cell(style={"padding": "0"}),
        rx.table.cell(rx.text(fila["valor"], font_size="11px", font_family="monospace"), padding="2px 8px"),
    )


def _sv_h_row(fila: dict) -> rx.Component:
    return rx.cond(
        fila["visible"],
        rx.cond(
            fila["tipo"] == "E",
            _sv_h_row_e(fila),
            _sv_h_row_r(fila),
        ),
        rx.table.row(style={"display": "none"}),
    )


def tabla_historial_sv() -> rx.Component:
    _TH = {
        "background": "var(--blue-9)", "color": "white",
        "font_size": "11px", "padding": "5px 8px", "white_space": "nowrap",
    }
    return rx.box(
        rx.cond(
            LaboratorioState.sv_h_filas,
            rx.scroll_area(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Nombre", style=_TH),
                            rx.table.column_header_cell("Unidad", style=_TH),
                            rx.table.column_header_cell("Valor",  style=_TH),
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(LaboratorioState.sv_h_filas, _sv_h_row),
                    ),
                    width="100%",
                    size="1",
                ),
                type="auto",
                height="100%",
                width="100%",
            ),
            rx.center(
                rx.vstack(
                    rx.icon("activity", size=24, color="var(--gray-7)"),
                    rx.text("Sin registros de signos vitales", font_size="12px", color="var(--gray-9)"),
                    align="center", spacing="2",
                ),
                height="100%",
            ),
        ),
        height="100%",
        overflow="hidden",
        width="100%",
    )


# ── Gráfico cartesiano OfRL ───────────────────────────────────────────────────

def _orl_grafico() -> rx.Component:
    """Bloque derecho del OfRL: gráfico de evolución temporal."""
    def _btn_escala(label: str, val: str) -> rx.Component:
        return rx.button(
            label,
            on_click=LaboratorioState.orl_set_escala(val),
            variant=rx.cond(LaboratorioState.orl_grafico_escala == val, "solid", "outline"),
            color_scheme="orange", size="1", type="button",
        )

    return rx.box(
        rx.cond(
            LaboratorioState.orl_grafico_ekey == "",
            # Estado vacío
            rx.center(
                rx.vstack(
                    rx.icon("mouse-pointer-click", size=28, color="var(--gray-5)"),
                    rx.text(
                        "Haga clic en una variable del panel izquierdo",
                        font_size="12px", color="var(--gray-9)", text_align="center",
                    ),
                    align="center", spacing="3",
                ),
                width="100%", height="100%",
            ),
            # Gráfico
            rx.vstack(
                # Cabecera: título + selector de escala
                rx.hstack(
                    rx.text(
                        LaboratorioState.orl_grafico_titulo,
                        font_size="12px", font_weight="bold", color="var(--orange-11)",
                        flex="1", overflow="hidden", white_space="nowrap", text_overflow="ellipsis",
                    ),
                    rx.hstack(
                        _btn_escala("Día",   "día"),
                        _btn_escala("Sem",   "semana"),
                        _btn_escala("Mes",   "mes"),
                        _btn_escala("Trim",  "trimestre"),
                        _btn_escala("Año",   "año"),
                        spacing="1",
                    ),
                    rx.hstack(
                        rx.text("#Divisiones:", font_size="10px", color="var(--gray-10)", white_space="nowrap"),
                        rx.el.input(
                            type="number",
                            min="3",
                            max="20",
                            value=LaboratorioState.orl_grafico_divisiones.to_string(),
                            on_change=LaboratorioState.orl_set_divisiones,
                            style={
                                "width": "44px",
                                "fontSize": "11px",
                                "padding": "1px 4px",
                                "border": "1px solid var(--gray-6)",
                                "borderRadius": "4px",
                                "background": "var(--gray-1)",
                                "color": "var(--gray-12)",
                                "textAlign": "center",
                            },
                        ),
                        spacing="1",
                        align="center",
                    ),
                    width="100%", align="center", spacing="2",
                    padding="6px 10px",
                    border_bottom="1px solid var(--gray-4)",
                    flex_shrink="0",
                ),
                # Área del gráfico
                rx.cond(
                    LaboratorioState.orl_grafico_datos,
                    rx.box(
                        rx.recharts.responsive_container(
                            rx.recharts.line_chart(
                                rx.recharts.cartesian_grid(
                                    stroke_dasharray="3 3",
                                    stroke="var(--gray-4)",
                                ),
                                rx.recharts.x_axis(
                                    data_key="x",
                                    tick={"fontSize": 10},
                                    interval=0,
                                    angle=-25,
                                    text_anchor="end",
                                    height=40,
                                ),
                                rx.recharts.y_axis(
                                    tick={"fontSize": 10},
                                    width=44,
                                ),
                                rx.recharts.graphing_tooltip(),
                                rx.recharts.line(
                                    data_key="y",
                                    type_="monotone",
                                    stroke="var(--orange-9)",
                                    stroke_width=2,
                                    dot={"r": 4, "fill": "var(--orange-9)", "strokeWidth": 0},
                                    label={"position": "top", "fontSize": 10,
                                           "fill": "var(--gray-11)"},
                                    is_animation_active=False,
                                ),
                                data=LaboratorioState.orl_grafico_datos,
                                margin={"top": 20, "right": 16, "bottom": 10, "left": 4},
                            ),
                            width="100%",
                            height="100%",
                        ),
                        flex="1",
                        width="100%",
                        overflow="hidden",
                        min_height="0",
                    ),
                    rx.center(
                        rx.text("Sin datos para graficar", font_size="12px", color="var(--gray-9)"),
                        flex="1", width="100%",
                    ),
                ),
                # Slider de desplazamiento temporal (solo si hay datos fuera del rango)
                rx.cond(
                    LaboratorioState.orl_grafico_offset_max > 0,
                    rx.hstack(
                        rx.icon("chevron-left", size=13, color="var(--gray-8)"),
                        rx.el.input(
                            type="range",
                            min="0",
                            max=LaboratorioState.orl_grafico_offset_max.to_string(),
                            value=(LaboratorioState.orl_grafico_offset_max
                                   - LaboratorioState.orl_grafico_offset).to_string(),
                            on_change=LaboratorioState.orl_set_offset_slider,
                            style={
                                "flex": "1",
                                "accentColor": "var(--orange-9)",
                                "cursor": "pointer",
                                "height": "4px",
                            },
                        ),
                        rx.icon("chevron-right", size=13, color="var(--gray-8)"),
                        width="100%",
                        align="center",
                        padding="3px 10px",
                        spacing="2",
                        flex_shrink="0",
                        border_top="1px solid var(--gray-4)",
                    ),
                    rx.fragment(),
                ),
                spacing="0",
                width="100%",
                height="100%",
                overflow="hidden",
            ),
        ),
        width="100%",
        height="100%",
        overflow="hidden",
    )


# ── Offcanvas Resultados Laboratorio (OfRL) ───────────────────────────────────

def offcanvas_resultados_laboratorio() -> rx.Component:
    """Panel lateral derecho con laboratorio + signos vitales del paciente."""
    return rx.box(
        # Backdrop
        rx.cond(
            AtencionState.offcanvas_lab_orl,
            rx.box(
                on_click=AtencionState.cerrar_lab_orl,
                position="fixed", top="0", left="0",
                width="100%", height="100%",
                bg="rgba(0,0,0,0.2)",
                z_index="98",
                transition="opacity 0.3s ease-in-out",
            ),
        ),
        # Panel principal
        rx.box(
            rx.vstack(
                # ── Cabecera ─────────────────────────────────────────────────
                rx.hstack(
                    rx.icon("flask-conical", size=16, color="var(--orange-10)"),
                    rx.text(
                        "Análisis de Valores",
                        font_weight="bold", font_size="15px",
                    ),
                    rx.spacer(),
                    rx.button(
                        rx.icon("plus", size=13),
                        rx.text("Nuevo Resultado", font_size="11px"),
                        on_click=LaboratorioState.lab_abrir(0),
                        size="1", variant="soft", color_scheme="orange",
                        type="button", gap="1",
                    ),
                    width="100%", align="center", spacing="2",
                    padding="8px 12px",
                    border_bottom="1px solid var(--gray-5)",
                    flex_shrink="0",
                ),
                # ── Cuerpo — 2 columnas iguales ───────────────────────────────
                rx.hstack(
                    # Bloque izquierdo: tabs Lab + SV
                    rx.box(
                        rx.tabs.root(
                            rx.tabs.list(
                                rx.tabs.trigger("Laboratorio",    value="lab"),
                                rx.tabs.trigger("Signos Vitales", value="sv"),
                                size="1",
                            ),
                            rx.tabs.content(
                                tabla_historial_lab(),
                                value="lab",
                                padding="4px",
                                height="100%",
                                overflow="hidden",
                            ),
                            rx.tabs.content(
                                tabla_historial_sv(),
                                value="sv",
                                padding="4px",
                                height="100%",
                                overflow="hidden",
                            ),
                            value=LaboratorioState.orl_tab_activo,
                            on_change=LaboratorioState.orl_set_tab,
                            height="100%",
                            width="100%",
                            display="flex",
                            flex_direction="column",
                        ),
                        width="50%",
                        height="100%",
                        border_right="1px solid var(--gray-5)",
                        overflow="hidden",
                    ),
                    # Bloque derecho: gráfico cartesiano
                    rx.box(
                        _orl_grafico(),
                        width="50%",
                        height="100%",
                        overflow="hidden",
                        padding="4px",
                    ),
                    spacing="0",
                    width="100%",
                    flex="1",
                    overflow="hidden",
                ),
                spacing="0",
                width="100%",
                height="100%",
                overflow="hidden",
            ),
            position="fixed",
            top="65px",
            right="10px",
            height="calc(96% - 65px)",
            width=rx.cond(State.show_panel_izq, "55vw", "96vw"),
            bg="white",
            box_shadow="-2px 0 10px rgba(0,0,0,0.3)",
            z_index=rx.cond(AtencionState.offcanvas_lab_orl, "101", "99"),
            padding="0",
            transform=rx.cond(
                AtencionState.offcanvas_lab_orl,
                "translateX(0)",
                "translateX(100%)",
            ),
            transition="transform 0.3s ease-in-out, width 0.3s ease-in-out",
            overflow="hidden",
        ),
    )
