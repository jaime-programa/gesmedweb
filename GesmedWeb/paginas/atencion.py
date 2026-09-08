import reflex as rx
from ..state import State, AtencionState, PrescripcionState,EditPacienteState
from ..componentes.componentes import (
    tabla_diagnosticos_con_encabezado,
    tabla_ant_personales_con_encabezado,
    tabla_ant_familiares_con_encabezado,
    tabla_alergias_con_encabezado,
    tabla_historial_atenciones,
    tabla_historial_prescripciones,
    panel_historia_atencion,
    panel_historial_prescripciones,
)
from ..componentes.colores import PACIENTE_AJENO_ATENCION_COLOR, PACIENTE_DISPONIBLE_ATENCION_COLOR
from ..componentes.dialogos import (
    offcanvas_atencion, offcanvas_prescripcion, offcanvas_nuevo_diagnostico,
    offcanvas_pedido_examenes, offcanvas_resultados_examenes,
    dialogo_nuevo_diagnostico, dialogo_vincular_diagnostico, dialogo_vinculos_exitosos,
    dialogo_editar_item_prescripcion, dialogo_nuevo_medicamento_px,
    dlg_mantenimiento_medicamentos,
    panel_prescripcion_historica, dialogo_advertencia_salir,
    dialogo_datos_paciente, offcanvas_menu,
    dialogo_nuevo_ant_familiar,
    dialogo_nueva_alergia,
    dialogo_cert_sin_soap,
    dialogo_formulario_certificado,
    dialogo_atenciones_tardias,
    offcanvas_certificados,
    offcanvas_laboratorio,
    tabla_historial_lab,
    offcanvas_resultados_laboratorio,
)
from ..state import LaboratorioState



from ..componentes.colores import BORDE_BOTONES_NAVBAR,BOTON_IMPRIMIR
from ..state import ResultadosState

nombre_paciente:str=''
grupo_sanguineo:str=''
BOTON_ABIERTO= "#0090FF"
BOTON_CERRADO="#D9ECFAFF"
_B = f"1px solid {BORDE_BOTONES_NAVBAR}"   # borde navbar

def navbar():
    return rx.box(
        rx.hstack(
            rx.hstack(
                # Box con información del paciente
                rx.box(
                    rx.hstack(
                        rx.button("☰", cursor="pointer", variant="surface", font_size="14px",
                                  on_click=AtencionState.toggle_offcanvas_menu, type="button", height="33px"),
                        ##Boton mostrar/ocultar panel de historial
                        #rx.button(
                        #    rx.icon(
                        #        rx.cond(State.show_panel_izq, "panel-left-close", "panel-left-open"),
                        #        size=16,
                        #    ),
                        #    on_click=State.toggle_panel_izq,
                        #    variant="surface",
                        #    type="button",
                        #    height="33px",
                        #    title="Mostrar/Ocultar Panel de Historial",
                        #    cursor="pointer",
                        #),
                        rx.button("✏️", cursor="pointer", variant="surface", font_size="12px",
                                  on_click=EditPacienteState.abrir_datos_paciente, type="button", height="33px"),
                        spacing="1",
                    ),
                    position="absolute",
                    top="11px",
                    border_radius="4px",
                ),
                rx.box(
                    rx.flex(
                        # Historia Clinica
                        rx.text('# ', State.paciente_seleccionado[0], font_weight="bold", font_size="12px"),
                        # Nombre Paciente
                        rx.text(
                            State.paciente_seleccionado[1], font_weight="bold", font_size="12px",
                            color=rx.cond(
                                State.paciente_actual_disponible,
                                PACIENTE_DISPONIBLE_ATENCION_COLOR,
                                rx.cond(
                                    State.paciente_actual_es_propio, "inherit", PACIENTE_AJENO_ATENCION_COLOR
                                ),
                            ),
                        ),
                        # Edad
                        rx.badge(State.paciente_seleccionado[2], variant="surface", font_size="12px"),
                        # Fecha Nacimiento
                        rx.badge(State.paciente_seleccionado[3], variant="surface", font_size="12px"),
                        # Grupo sanguineo
                        rx.badge(State.paciente_seleccionado[4], variant="solid", color_scheme="crimson", font_size="12px"),
                        spacing="2",
                        padding="2px",
                    ),
                    position="absolute",
                    top="10px",
                    left="80px",
                    margin="2px",
                    border="1px solid black",
                    padding="4px",
                    height="33px",
                    border_radius="3px",
                ),
                #Boton mostrar/ocultar panel de historial
                rx.button(
                    rx.icon(
                        rx.cond(State.show_panel_izq, "panel-left-close", "panel-left-open"),
                        size=16,
                    ),
                    rx.text("Historial",font_size="8px"),
                    on_click=State.toggle_panel_izq,
                    variant="surface",
                    type="button",
                    height="33px",
                    title="Mostrar/Ocultar Panel de Historial",
                    cursor="pointer",
                    position="absolute",
                    top="10px",
                    left="590px",
                ),
                # Grupo central — contenedor posicionado al 50% del navbar
                rx.box(
                    rx.cond(
                        State.puede_escribir_paciente_actual,
                        rx.cond(
                            AtencionState.atencion_iniciada,
                            # ── Botones SOAP / Prescripción / Exámenes ────────────
                            rx.hstack(
                                rx.cond(
                                    AtencionState.offcanvas_atencion_actual,
                                    rx.button("📖 SOAP", color="white", font_size="12px",
                                              on_click=AtencionState.cierra_offcanvas_actual, cursor="pointer",
                                              bg=BOTON_ABIERTO, border=_B),
                                    rx.button("📕 SOAP", font_size="12px",
                                              variant='surface', border=_B,
                                              on_click=AtencionState.abre_offcanvas_actual, cursor="pointer"),
                                ),
                                rx.cond(
                                    AtencionState.offcanvas_prescripcion,
                                    rx.button("📖 Prescripción", bg=BOTON_ABIERTO, color="white", font_size="12px",
                                              border=_B, on_click=AtencionState.cierra_offcanvas_prescripcion, cursor="pointer"),
                                    rx.button("📗 Prescripción", variant='surface', font_size="12px",
                                              border=_B, on_click=AtencionState.abre_offcanvas_prescripcion, cursor="pointer"),
                                ),
                                rx.cond(
                                    AtencionState.offcanvas_pedido_examenes,
                                    rx.button("📖 Pedido Exámenes", bg=BOTON_ABIERTO, color="white", font_size="12px",
                                              border=_B, on_click=AtencionState.cierra_offcanvas_pedido_examenes, cursor="pointer"),
                                    rx.button("📘 Pedido Exámenes", variant='surface', font_size="12px",
                                              border=_B, on_click=AtencionState.abre_offcanvas_pedido_examenes, cursor="pointer"),
                                ),
                                spacing="2",
                                align="center",
                                position="absolute",
                                left="50%",
                            ),
                            # ── Botones "Nueva Atención" / "Editar Atención" ──────
                            rx.hstack(
                                rx.button(
                                    "Nueva Atención",
                                    on_click=AtencionState.iniciar_nueva_atencion,
                                    type="button",
                                    bg=BOTON_IMPRIMIR,
                                    color="white",
                                    font_size="13px",
                                    font_weight="600",
                                    cursor="pointer",
                                ),
                                rx.cond(
                                    State.hay_atencion_hoy_historial,
                                    rx.button(
                                        "Editar Atención",
                                        on_click=AtencionState.editar_atencion_historica,
                                        type="button",
                                        variant="surface",
                                        color_scheme="plum",
                                        font_size="13px",
                                        font_weight="600",
                                        cursor="pointer",
                                    ),
                                    rx.fragment(),
                                ),
                                spacing="2",
                                align="center",
                            ),
                        ),
                        rx.fragment(),
                    ),
                    position="absolute",
                    left="58%",
                    transform="translateX(-50%)",
                    top="11px",
                ),

                rx.spacer(),
                rx.vstack(
                    # Resultados Imagen — Med.Lee + Med.Prop + Admin
                    rx.cond(
                        State.puede_ver_clinica,
                        rx.cond(
                            AtencionState.offcanvas_resultados_examenes,
                            rx.button("📖 Imágenes", color_scheme="tomato", variant="solid",
                                      font_size="9px", height="22px", padding="0 8px",
                                      on_click=AtencionState.cierra_offcanvas_resultados_examenes, cursor="pointer"),
                            rx.button("📙 Imágenes", color_scheme="tomato", variant="surface",
                                      font_size="9px", height="22px", padding="0 8px", cursor="pointer",
                                      on_click=[AtencionState.abre_offcanvas_resultados_examenes, ResultadosState.ri_recargar]),
                        ),
                        rx.fragment(),
                    ),
                    # Resultados Laboratorio — Med.Lee + Med.Prop + Admin
                    rx.cond(
                        State.puede_ver_clinica,
                        rx.cond(
                            AtencionState.offcanvas_lab_orl,
                            rx.button("📖 Análisis Valores", color_scheme="tomato", variant="solid",
                                      font_size="9px", height="22px", padding="0 8px",
                                      on_click=AtencionState.cerrar_lab_orl, cursor="pointer"),
                            rx.button("🧪 Análisis Valores", color_scheme="tomato", variant="surface",
                                      font_size="9px", height="22px", padding="0 8px", cursor="pointer",
                                      on_click=LaboratorioState.abrir_lab_orl),
                        ),
                        rx.fragment(),
                    ),
                    spacing="1",
                    align="end",
                ),
                rx.button("Salir", on_click=AtencionState.logout_con_advertencia),
                spacing="4",
                top="11px",
                align_items="center",
                width="100%",
            ),
        position="fixed",
        top="0",
        left="0",
        right="0",
        height="60px",
        bg="white",
        border_bottom="1px solid lightgray",
        z_index="999",
    )
    )
    
def sidebar():
    color2="rgba(0,113,227,.7)",
    return rx.box(
        rx.vstack(
            rx.foreach(
                State.sidebar_options,
                lambda option: rx.cond(
                    option == "Reportes",
                    rx.vstack(
                        rx.button(option, on_click=State.toggle_submenu,height="60px", padding="10px 10px",margin="10px",background_color=State.color_boton_celeste,_hover={"bg": State.color_boton_azul}),
                        rx.cond(
                            State.show_submenu,
                            rx.vstack(
                                rx.button("Submenu 1",background_color=State.color_boton_celeste,_hover={"bg": State.color_boton_azul}),
                                rx.button("Submenu 2",background_color=State.color_boton_celeste,_hover={"bg": State.color_boton_azul}),
                                rx.button("Submenu 3",background_color=State.color_boton_celeste,_hover={"bg": State.color_boton_azul}),
                                padding_left="30px",
                            ),
                        ),
                    ),
                    rx.button(option,height="50px", padding="10px 10px",margin="10px",background_color=State.color_boton_celeste,_hover={"bg": State.color_boton_azul})
                )
            ),
            align_items="stretch",
            spacing="4",
            width="100%",
        ),
        #Tabla de Signos Vitales
        #rx.vstack(
        #    rx.data_editor(
        #        columns=columns,
        #        data=data,
        #        height="40vh",
        #        row_height=28,
        #        smooth_scroll_y=True,
        #        smooth_scroll_x=False,
        #    ),
        #),'''
        width="200px",
        height="90vh",
        position="fixed",
        top="60px",
        left="0",
        bg="rgb(240,240,240)",
        padding="20px",
        transform=rx.cond(State.show_sidebar, "translateX(0)", "translateX(-100%)"),
        transition="transform 0.3s ease-in-out",
    )

def panel_derecha():
    return rx.box(
        rx.cond(
            State.contenido_derecha == "historial_atenciones",
            rx.box(
                panel_historia_atencion(),
                width="100%",
                height="100%",
                style={
                    "transform": rx.cond(State.show_panel_izq, "translateX(0)", "translateX(100%)"),
                    "transition": "transform 0.3s ease-in-out",
                },
            ),
            rx.cond(
                State.contenido_derecha == "historial_prescripciones",
                panel_historial_prescripciones(),
                rx.cond(
                    State.contenido_derecha == "prescripcion_historica",
                    rx.box(
                        panel_prescripcion_historica(),
                        width="100%",
                        height="100%",
                        padding="8px 12px",
                        overflow_y="auto",
                    ),
                    rx.center(
                        rx.image(
                            src="/logotipo_original.png",
                            height="192px",
                            object_fit="contain",
                        ),
                        width="100%",
                        height="100%",
                    ),
                ),
            ),
        ),
        flex="1",
        height="100%",
        background_color="white",
        border_left="1px solid var(--gray-5)",
        overflow="hidden",
    )
                
def panel_izquierda():
    return rx.box(
                
                rx.box(     #Box que contiene los tabs de atencion, historial, prescripción, etc.
                    #. #rx.tabs.root(
                    #. #    rx.tabs.list(
                    #. #        rx.tabs.trigger("Historial Atenciones",value="historial_atenciones",
                    #. #            style={
                    #. #                "white-space": "pre-wrap",
                    #. #                "height": "auto",
                    #. #                "min-height": "48px",
                    #. #                "line-height": "1.2",
                    #. #                "padding": "4px 8px",
                    #. #                "text-align": "center",
                    #. #            },on_click=lambda: State.cambia_tab("historial_atenciones"),),
                            # #rx.tabs.trigger("Prescripciones", value="prescripcion_cuidados",
                            # #    style={
                            # #    "white-space": "pre-wrap",
                            # #    "height": "auto",
                            # #    "min-height": "48px",
                            # #    "line-height": "1.2",
                            # #    "padding": "4px 8px",
                            # #    "text-align": "center",
                            # #},on_click=lambda: State.cambia_tab("historial_prescripciones"),),
                            #rx.tabs.trigger("Resultados Laboratorio",value="resultados_examenes",
                            #    style={
                            #        "white-space": "pre-wrap",
                            #        "height": "auto",
                            #        "min-height": "48px",
                            #        "line-height": "1.2",
                            #        "padding": "4px 8px",
                            #        "text-align": "center",
                            #    },
                            #    on_click=[State.cambia_tab("resultados_examenes"), LaboratorioState.lab_h_cargar],
                            #),
                #.#        ),
                        #Contenido Atencion Actual
                        # #rx.tabs.content(
                        # #    rx.box(
                        # #        rx.text('Consulta actual'),
                        # #        width='49%',
                        # #        height="25vh",
                        # #        position='fixed',
                        # #        left='1px',
                        # #        top='150px',
                        # #        margin_left="2px",
                        # #        margin_top='2px',
                        # #        padding='5px',
                        # #        background_color="transparent",
                        # #        border="solid 1px",
                        # #    ),
                        # #    value='consulta_actual',

                        # #),

                        #Contenido Historial Consultas
                #.#        rx.tabs.content(
                            #State.contenido_derecha == "Historial de Consultas",
                    rx.vstack(
                        rx.hstack(
                        rx.text("Historial de Atenciones"),
                        rx.box(
                            rx.icon(
                                "search", size=14, color="#888",
                                position="absolute",
                                left="7px",
                                top="50%",
                                transform="translateY(-50%)",
                                pointer_events="none",
                                z_index="1",
                            ),
                            rx.el.input(
                                placeholder="Buscar",
                                value=State.que_historial_busco,
                                id="busca_historial",
                                on_change=State.actualizar_que_hc_busco,
                                style={
                                    "border": "1px solid #ddd",
                                    "borderRadius": "6px",
                                    "padding": "0.4em 0.5em 0.4em 2em",
                                    "width": "140px",
                                    "fontSize": "14px",
                                    "outline": "none",
                                    "background": "white",
                                },
                            ),
                            position="relative",
                            display="inline-flex",
                            align_items="center",
                        ),
                        # Botón limpiar búsqueda
                        rx.button(
                            rx.icon("eraser", size=13),
                            on_click=State.limpia_hc_busco,
                            size="2",
                            variant="ghost",
                            color_scheme="gray",
                            cursor="pointer",
                            height="28px",
                            width="28px",
                            padding="0",
                            title="Limpiar búsqueda",
                        ),
                        padding='2px',
                        position="relative",
                        width="600px",
                        align="center",
                        ),

                    #Tabla de atenciones
                    rx.box(
                            tabla_historial_atenciones(),
                            margin_top='1px',
                            border='solid 1px',
                            border_color='gray',
                            
                        ),
                        padding='2px',
                        spacing='0',

                    ),
                            
                                   
                            #),  #ScrollArea
                        #.#    value="historial_atenciones",
                        #.#),  #Tab
                        
                        # Historial de Prescripciones
                        # #rx.tabs.content(
                        # #    tabla_historial_prescripciones(),
                        # #    value="prescripcion_cuidados",
                        # #    padding="2px",
                        # #),

                        # Tab Resultados Laboratorio
                        #rx.tabs.content(
                        #    tabla_historial_lab(),
                        #    value="resultados_examenes",
                        #    padding="2px",
                        #    height="100%",
                        #    overflow="hidden",
                        #),
                        #default_value="",
                        #.#default_value="historial_atenciones",
                        #height='10px',
                        #padding='2px',
                        
                    #),
                    flex="0 0 47%",
                    padding="5px",
                    background_color="transparent",
                    border="solid 1px gray",
                    overflow="hidden",
                ),
                rx.cond(
                    State.puede_ver_clinica,
                rx.box(     #Diagnosticos, Antecedentes Familiares, Personales, etc.
                    rx.tabs.root(
                        rx.tabs.list(
                            rx.tabs.trigger(State.tab_label_diagnosticos, value="diagnosticos",
                                style={
                                "white-space": "pre-wrap",
                                "height": "auto",
                                "min-height": "48px",
                                "line-height": "1.2",
                                "padding": "4px 8px",
                                "text-align": "center",
                            }),
                            rx.tabs.trigger(State.tab_label_ant_personales, value="a_personales",
                                style={
                                "white-space": "pre-wrap",
                                "height": "auto",
                                "min-height": "48px",
                                "line-height": "1.2",
                                "padding": "4px 8px",
                                "text-align": "center",
                                "color":"green",
                            }),
                            rx.tabs.trigger(State.tab_label_ant_familiares, value="a_familiares",
                                style={
                                "white-space": "pre-wrap",
                                "height": "auto",
                                "min-height": "48px",
                                "line-height": "1.2",
                                "padding": "4px 8px",
                                "text-align": "center",
                                "color":"blue",
                            }),
                            rx.tabs.trigger(State.tab_label_alergias, value="alergias_",
                                style={
                                "white-space": "pre-wrap",
                                "height": "auto",
                                "min-height": "48px",
                                "line-height": "1.2",
                                "padding": "4px 8px",
                                "text-align": "center",
                                "color":"red",
                            }),
                            rx.tabs.trigger(PrescripcionState.tab_label_prescripciones, value="prescripcion_cuidados",
                                style={
                                "white-space": "pre-wrap",
                                "height": "auto",
                                "min-height": "48px",
                                "line-height": "1.2",
                                "padding": "4px 8px",
                                "text-align": "center",
                                "color":"green",
                            },on_click=lambda: State.cambia_tab("historial_prescripciones"),),
                            #rx.tabs.trigger("Antecedentes \nGinecológicos",value="a_ginecologicos",
                            #    style={
                            #    "white-space": "pre-wrap",
                            #    "height": "auto",
                            #    "min-height": "48px",
                            #    "line-height": "1.2",
                            #    "padding": "4px 8px",
                            #    "text-align": "center",
                            #}),
                        ),
                        rx.tabs.content(
                            #State.tab_derecha=='diagnosticos',
                            #rx.scroll_area(
                                rx.box(
                                    tabla_diagnosticos_con_encabezado(),
                                    #Configuracion del box que contiene tabla de diagnosticos
                                    margin_top='6px',
                                    border='solid 1px',
                                    border_color='gray',
                                    
                                ),
                            #),
                            value="diagnosticos",
                            
                            
                        ),
                        rx.tabs.content(
                            rx.box(
                                tabla_ant_personales_con_encabezado(),
                                margin_top="6px",
                                border="solid 1px",
                                border_color="gray",
                            ),
                            value="a_personales",
                        ),
                        rx.tabs.content(
                            rx.box(
                                tabla_ant_familiares_con_encabezado(),
                                margin_top="6px",
                                border="solid 1px",
                                border_color="gray",
                            ),
                            value="a_familiares",
                        ),
                        rx.tabs.content(
                            rx.box(
                                tabla_alergias_con_encabezado(),
                                margin_top="6px",
                                border="solid 1px",
                                border_color="gray",
                            ),
                            value="alergias_",
                        ),
                        # Historial de Prescripciones
                        rx.tabs.content(
                            rx.box(
                                tabla_historial_prescripciones(),
                                margin_top="6px",
                                border="solid 1px",
                                border_color="gray",
                                width="100%",
                            ),
                            value="prescripcion_cuidados",
                            width="100%",
                        ),
                        value=State.tab_izq_activo,
                        on_change=State.set_tab_izq,
                        default_value="diagnosticos",
                        width="100%",
                    ),
                    flex="1",
                    padding="5px",
                    background_color="transparent",
                    border="solid 1px gray",
                    overflow="hidden",
                    margin_top="2px",
                ),  #Fin box diagnosticos
                    rx.fragment(),
                ),  #Fin cond puede_ver_clinica
            display="flex",
            flex_direction="column",
            width=rx.cond(
                State.ha_panel_expandido,
                "0px",
                rx.cond(State.show_panel_izq, "49%", "0px"),
            ),
            min_width="0",
            flex_shrink="0",
            height="100%",
            overflow="hidden",
            transition="width 0.3s ease-in-out",
            gap="2px",
            padding="2px",
        )

def index():
    return rx.cond(State.is_authenticated,
            rx.box(
                navbar(),
                # ── Área principal: columna izquierda + columna derecha ────────
                rx.box(
                    panel_izquierda(),
                    rx.cond(State.puede_ver_clinica, panel_derecha(), rx.fragment()),
                    position="fixed",
                    top="60px",
                    bottom="24px",
                    left="0",
                    right="0",
                    display="flex",
                    overflow="hidden",
                ),
                # ── Barra inferior con nombre del médico ───────────────────────
                rx.box(
                    State.nombre_medico,
                    position="fixed",
                    bottom="0",
                    left="0",
                    width="100%",
                    height="24px",
                    padding="4px",
                    background_color="white",
                    border_top="1px solid gray",
                    color="black",
                    font_size="12px",
                    text_align="left",
                ),
                offcanvas_atencion(),
                offcanvas_prescripcion(),
                offcanvas_pedido_examenes(),
                offcanvas_resultados_examenes(),
                offcanvas_resultados_laboratorio(),
                #offcanvas_nuevo_diagnostico(),
                dialogo_nuevo_diagnostico(),
                dialogo_vincular_diagnostico(),
                dialogo_vinculos_exitosos(),
                dialogo_editar_item_prescripcion(),
                dialogo_nuevo_medicamento_px(),
                dlg_mantenimiento_medicamentos(),
                dialogo_advertencia_salir(),
                dialogo_datos_paciente(),
                dialogo_nuevo_ant_familiar(),
                dialogo_nueva_alergia(),
                dialogo_cert_sin_soap(),
                dialogo_formulario_certificado(),
                dialogo_atenciones_tardias(),
                offcanvas_certificados(),
                offcanvas_menu(),
                offcanvas_laboratorio(),
                rx.toast.provider(),
                overflow="hidden",
            
                ),
            rx.center(
                rx.box(
                        rx.vstack(
                                rx.text("Su sesión ha caducado!", font_size="20px", font_weight="bold"),
                                rx.link("Vuelva a Ingresar", href="/", color="blue", is_external=False),
                                spacing="4",
                                align="center",
                                ),
                                width="400px", height="200px", bg="lightblue", padding="20px", border_radius="10px", box_shadow="lg"
                                ),
                        height="100vh",  # Altura completa de la ventana para centrar verticalmente
                ),
            )  
