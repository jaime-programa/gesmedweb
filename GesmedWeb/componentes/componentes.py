import reflex as rx
from ..state import State, NuevoDiagnosticoState, PrescripcionState, NuevoAntFamiliarState, NuevaAlergiaState,CertificadoState
from ..querys.querys import edad
from ..modelos.mis_modelos import Paciente,Atencion
from .colores import (
    ROW_SELECTED_BG, ROW_HOVER_BG, ROW_DESTACADO_COLOR, ROW_DESTACADO_COLOR2,
    TABLE_HEADER_BG_BLUE,TABLE_HEADER_BG_GREEN,TABLE_HEADER_BG_PETROLEO, TABLE_HEADER_COLOR, TABLE_BORDER,
    COLOR_RESALTA_TEXTO,
    ZEBRA_OBSCURO, ZEBRA_CLARO,BOTON_IMPRIMIR,
    SOAP_FIELD_BORDER,SOAP_FONDO,PRESCRIPCION_FONDO,PEDIDO_FONDO,RESULTADO_FONDO
)



def tabla_pacientes():
    return rx.box(
                     rx.table.root(
                            rx.table.header(
                                   rx.table.row(
                                          rx.table.column_header_cell("# HClinica"),
                                          rx.table.column_header_cell("Nombre Completo"),
                                          rx.table.column_header_cell("Edad"),
                                          rx.table.column_header_cell("Seguro"),
                                          )
                                   ),
                            rx.table.body(
                                rx.foreach(
                                    State.lista_pacientes,una_fila)
                            )  
                        )
                     ),

def una_fila(paciente:Paciente):
    return rx.table.row(
        rx.table.cell(paciente.nro_hclinica),
        rx.table.cell(paciente.nombre_completo),
        #rx.table.cell(edad(paciente.fecha_nacimiento)),
        rx.table.cell(paciente.seguro),
        #rx.table.cell(rx.button('Nueva Atención')),
    )

def un_acordeon(atencion:Atencion):
        #print ("Veamos si hay id_atencion")
        #print (str(atencion.id_atencion))
    return rx.accordion.item(
                header=rx.text(atencion.motivo_consulta,color="black",font_weight="bold",align="left"),
                content=rx.text(atencion.objetivo,color="grey",size="2"),
                id=str(atencion.id_atencion),
                ),

def tabla_pacientes_interactiva():
    return tabla_pacientes_con_encabezado()

def _fila_paciente(p: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(p['nro_hclinica']),
        rx.table.cell(p['nombre_completo']),
        rx.table.cell(p['edad']),
        rx.table.cell(p['grupo_sanguineo']),
        rx.table.cell(p['seguro']),
        rx.table.cell(p['cuantas_atenciones']),
        on_click=State.selecciona_paciente(p['nro_hclinica']),
        cursor="pointer",
        background=rx.cond(
            State.nro_hclinica_seleccionado == p['nro_hclinica'],
            ROW_SELECTED_BG,
            "transparent",
        ),
        _hover={"background": ROW_HOVER_BG},
    )

def tabla_pacientes_con_encabezado():
    return rx.scroll_area(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("# HClínica"),
                    rx.table.column_header_cell("Nombre"),
                    rx.table.column_header_cell("Edad"),
                    rx.table.column_header_cell("Gr. Sanguíneo"),
                    rx.table.column_header_cell("Seguro"),
                    rx.table.column_header_cell("Atenciones"),
                )
            ),
            rx.table.body(rx.foreach(State.lista_pacientes, _fila_paciente)),
            width="100%",
        ),
        height="75vh",
    )


_CELL_DIAG = {"padding_y": "2px", "padding_x": "4px", "font_size": "11px", "line_height": "1.2", "border": f"1px solid {TABLE_BORDER}", "vertical_align": "middle"}

def _fila_diagnostico(d: dict) -> rx.Component:
    _color = rx.cond(d['destacado'], ROW_DESTACADO_COLOR, "inherit")
    _weight = rx.cond(d['destacado'], "700", "400")
    return rx.table.row(
        rx.table.cell(d['cie10'], **_CELL_DIAG, color=_color, font_weight=_weight),
        rx.table.cell(d['nombre_cie10'], **{**_CELL_DIAG, "font_size": "10px"}, color=_color, font_weight=_weight),
        rx.table.cell(d['tipo'], **_CELL_DIAG, color=_color, font_weight=_weight),
        rx.table.cell(d['fecha_diagnostico'], **_CELL_DIAG, color=_color, font_weight=_weight),
        rx.table.cell(d['fecha_inicio_aparente'], **_CELL_DIAG, color=_color, font_weight=_weight),
        rx.table.cell(d['observaciones'], **_CELL_DIAG, color=_color, font_weight=_weight),
        on_click=State.selecciona_diagnostico(d['id_diagnostico']),
        cursor="pointer",
        background=rx.cond(d['seleccionado'], ROW_SELECTED_BG, "transparent"),
        _hover={"background": ROW_HOVER_BG},
    )

_CELL_HEADER_DIAG_P = {"padding_y": "2px", "padding_x": "4px", "font_size": "11px", "border": f"1px solid {TABLE_BORDER}", "background": TABLE_HEADER_BG_PETROLEO, "color": TABLE_HEADER_COLOR}
_CELL_HEADER_DIAG_G = {"padding_y": "2px", "padding_x": "4px", "font_size": "11px", "border": f"1px solid {TABLE_BORDER}", "background": TABLE_HEADER_BG_GREEN, "color": TABLE_HEADER_COLOR}
_CELL_HEADER_DIAG_B = {"padding_y": "2px", "padding_x": "4px", "font_size": "11px", "border": f"1px solid {TABLE_BORDER}", "background": TABLE_HEADER_BG_BLUE, "color": TABLE_HEADER_COLOR}

def tabla_diagnosticos_con_encabezado():
    return rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell(
                        rx.hstack(
                            rx.text("CIE10"),
                            rx.button(
                                "Nuevo",
                                size="1",
                                color_scheme="cyan",
                                on_click=NuevoDiagnosticoState.abrir_nuevo_diagnostico,
                                cursor="pointer",
                            ),
                            align="center",
                            spacing="2",
                            justify="between",
                        ),
                        **_CELL_HEADER_DIAG_P,
                    ),
                    rx.table.column_header_cell("Diagnóstico", **_CELL_HEADER_DIAG_P),
                    rx.table.column_header_cell("Tipo", **_CELL_HEADER_DIAG_P),
                    rx.table.column_header_cell("F.Diagnóstico", **_CELL_HEADER_DIAG_P),
                    rx.table.column_header_cell("F.Inicio Aparente", **_CELL_HEADER_DIAG_P),
                    rx.table.column_header_cell("Observaciones", **_CELL_HEADER_DIAG_P),
                ),
                style={"position": "sticky", "top": "0", "z_index": "1"},
            ),
            rx.table.body(rx.foreach(State.diagnosticos_con_estilo, _fila_diagnostico)),
            width="100%",
            style={"border_collapse": "collapse"},
        ),
        overflow_y="auto",
        height="35vh",
    )

def _fila_ant_personal(d: dict) -> rx.Component:
    _color = rx.cond(d['destacado'], ROW_DESTACADO_COLOR, "inherit")
    _weight = rx.cond(d['destacado'], "700", "400")
    return rx.table.row(
        rx.table.cell(d['cie10'], **_CELL_DIAG, color=_color, font_weight=_weight),
        rx.table.cell(d['nombre_cie10'], **{**_CELL_DIAG, "font_size": "10px"}, color=_color, font_weight=_weight),
        rx.table.cell(d['fecha_diagnostico'], **_CELL_DIAG, color=_color, font_weight=_weight),
        rx.table.cell(d['fecha_inicio_aparente'], **_CELL_DIAG, color=_color, font_weight=_weight),
        rx.table.cell(d['observaciones'], **_CELL_DIAG, color=_color, font_weight=_weight),
        on_click=State.selecciona_diagnostico(d['id_diagnostico']),
        cursor="pointer",
        background=rx.cond(d['seleccionado'], ROW_SELECTED_BG, "transparent"),
        _hover={"background": ROW_HOVER_BG},
    )

def tabla_ant_personales_con_encabezado():
    return rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell(
                        rx.hstack(
                            rx.text("CIE10"),
                            rx.button(
                                "Nuevo",
                                size="1",
                                color_scheme="green",
                                on_click=NuevoDiagnosticoState.abrir_nuevo_ant_personal,
                                cursor="pointer",
                            ),
                            align="center",
                            spacing="2",
                            justify="between",
                        ),
                        **_CELL_HEADER_DIAG_G,
                    ),
                    rx.table.column_header_cell("Diagnóstico", **_CELL_HEADER_DIAG_G),
                    rx.table.column_header_cell("F.Diagnóstico", **_CELL_HEADER_DIAG_G),
                    rx.table.column_header_cell("F.Inicio Aparente", **_CELL_HEADER_DIAG_G),
                    rx.table.column_header_cell("Observaciones", **_CELL_HEADER_DIAG_G),
                ),
                style={"position": "sticky", "top": "0", "z_index": "1"},
            ),
            rx.table.body(rx.foreach(State.ant_personales_con_estilo, _fila_ant_personal)),
            width="100%",
            style={"border_collapse": "collapse"},
        ),
        overflow_y="auto",
        height="35vh",
    )

def _fila_ant_familiar(d: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(d["fecha_registro"], **{**_CELL_DIAG, "white_space": "nowrap", "width": "95px"}),
        rx.table.cell(d["descripcion"],    **{**_CELL_DIAG, "width": "100%", "white_space": "pre-wrap"}),
        _hover={"background": ROW_HOVER_BG},
    )

def tabla_ant_familiares_con_encabezado():
    return rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell(
                        rx.hstack(
                            rx.text("Fecha de registro"),
                            rx.button(
                                "Nuevo",
                                size="1",
                                color_scheme="blue",
                                on_click=NuevoAntFamiliarState.abrir_naf_dialog,
                                cursor="pointer",
                            ),
                            align="center",
                            spacing="2",
                            justify="between",
                        ),
                        **_CELL_HEADER_DIAG_B,
                    ),
                    rx.table.column_header_cell("Antecedente (descripción)", **_CELL_HEADER_DIAG_B),
                ),
                style={"position": "sticky", "top": "0", "z_index": "1"},
            ),
            rx.table.body(rx.foreach(State.lista_ant_familiares, _fila_ant_familiar)),
            width="100%",
            style={"border_collapse": "collapse"},
        ),
        overflow_y="auto",
        height="35vh",
    )


_CELL_ALERGIA = {"padding_y": "2px", "padding_x": "4px", "font_size": "11px", "line_height": "1.2", "border": f"1px solid {TABLE_BORDER}", "vertical_align": "middle"}
_CELL_HEADER_ALERGIA = {"padding_y": "2px", "padding_x": "4px", "font_size": "11px", "border": f"1px solid {TABLE_BORDER}", "background": "#9B2226", "color": TABLE_HEADER_COLOR}

def _fila_alergia(a: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(a["sustancia_alergia"], **_CELL_ALERGIA),
        rx.table.cell(a["fecha_reportada"],   **{**_CELL_ALERGIA, "white_space": "nowrap", "width": "95px"}),
        _hover={"background": ROW_HOVER_BG},
    )

def tabla_alergias_con_encabezado():
    return rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell(
                        rx.hstack(
                            rx.text("Sustancia"),
                            rx.button(
                                "Nueva",
                                size="1",
                                color_scheme="red",
                                on_click=NuevaAlergiaState.abrir_naa_dialog,
                                cursor="pointer",
                            ),
                            align="center",
                            spacing="2",
                            justify="between",
                        ),
                        **_CELL_HEADER_ALERGIA,
                    ),
                    rx.table.column_header_cell("Fecha Reportada", **_CELL_HEADER_ALERGIA),
                ),
                style={"position": "sticky", "top": "0", "z_index": "1"},
            ),
            rx.table.body(rx.foreach(State.lista_alergias, _fila_alergia)),
            width="100%",
            style={"border_collapse": "collapse"},
        ),
        overflow_y="auto",
        height="35vh",
    )


_CELL_ATEN = {"padding_y": "1px", "padding_x": "4px", "font_size": "11px", "line_height": "1.0", "border": f"1px solid {TABLE_BORDER}", "vertical_align": "middle"}
_CELL_ATEN_CENTRADA = {"padding_y": "1px", "padding_x": "4px", "font_size": "11px", "line_height": "1.0", "border": f"1px solid {TABLE_BORDER}", "vertical_align": "middle","align":"center"}
_CELL_HEADER_ATEN = {"padding_y": "2px", "padding_x": "4px", "font_size": "11px", "border": f"1px solid {TABLE_BORDER}", "background": TABLE_HEADER_BG_PETROLEO, "color": TABLE_HEADER_COLOR}
_CELL_HEADER_PRES = {"padding_y": "2px", "padding_x": "4px", "font_size": "11px", "border": f"1px solid {TABLE_BORDER}", "background": TABLE_HEADER_BG_GREEN, "color": TABLE_HEADER_COLOR}

def _fila_atencion(a: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(a['fecha_atencion'], **{**_CELL_ATEN, "white_space": "nowrap", "width": "300px"}),
        rx.table.cell(a['codigos_cie10'], **_CELL_ATEN,
            color=rx.cond(State.filtro_diagnostico_activo, COLOR_RESALTA_TEXTO, "inherit"),
            font_weight=rx.cond(State.filtro_diagnostico_activo, "700", "400"),
        ),
        rx.table.cell(a['motivo_consulta'], **{**_CELL_ATEN, "width": "100%"}),
        on_click=State.selecciona_atencion(a['id_atencion']),
        cursor="pointer",
        background=rx.cond(
            State.id_atencion_seleccionada == a['id_atencion'],
            ROW_SELECTED_BG,
            "transparent",
        ),
        _hover={"background": ROW_HOVER_BG},
    )

def tabla_historial_atenciones():
    return rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Fecha de Atención", **{**_CELL_HEADER_ATEN, "white_space": "nowrap", "width": "300px"}),
                    rx.table.column_header_cell("CIE10", **_CELL_HEADER_ATEN),
                    rx.table.column_header_cell("Motivo de Consulta", **{**_CELL_HEADER_ATEN, "width": "100%"}),
                ),
                style={"position": "sticky", "top": "0", "z_index": "1"},
            ),
            rx.table.body(rx.foreach(State.atenciones_visibles, _fila_atencion)),
            width="100%",
            style={"border_collapse": "collapse"},
        ),
        overflow_y="auto",
        height="33vh",
    )

_CELL_HP_H = _CELL_HEADER_PRES   # mismo estilo de encabezado que historial_atenciones
_CELL_HP   = _CELL_ATEN          # mismo estilo de celdas
_CELL_HP_CENTRADA= _CELL_ATEN_CENTRADA


def _icono_orden_hp(col: str) -> rx.Component:
    return rx.cond(
        PrescripcionState.hp_orden_col == col,
        rx.cond(
            PrescripcionState.hp_orden_asc,
            rx.icon("chevron_up",   size=10),
            rx.icon("chevron_down", size=10),
        ),
        rx.icon("chevrons_up_down", size=10, color="var(--gray-7)"),
    )


def _fila_historial_px(r: dict) -> rx.Component:
    _sel = PrescripcionState.hp_id_atencion_sel == r["id_atencion"]
    _zebra_bg = rx.cond(r["zebra"] == 0, ZEBRA_OBSCURO, rx.cond(r["zebra"] == 1, ZEBRA_CLARO, "transparent"))
    return rx.table.row(
        rx.table.cell(
            r["fecha_atencion"],
            **{**_CELL_HP, "white_space": "nowrap"},
            background=rx.cond(_sel, ROW_DESTACADO_COLOR2, "inherit"),
        ),
        rx.table.cell(r["cantidad"],            **_CELL_HP_CENTRADA),
        rx.table.cell(r["nombre_generico"],     **_CELL_HP),
        rx.table.cell(r["concentracion"],       **_CELL_HP_CENTRADA),
        rx.table.cell(r["nombre_presentacion"], **_CELL_HP),
        on_click=PrescripcionState.hp_selecciona_fila(r["id_atencion"]),
        cursor="pointer",
        background=_zebra_bg,
        _hover={"background": rx.cond(r["zebra"] == 0, ZEBRA_OBSCURO, rx.cond(r["zebra"] == 1, ZEBRA_CLARO, ROW_HOVER_BG)), "font_weight": "bold"},
    )


def tabla_historial_prescripciones() -> rx.Component:
    return rx.vstack(
        # ── Buscador + botón borrar ────────────────────────────────────────────
        rx.hstack(
            rx.input(
                placeholder="Filtrar por medicamento...",
                value=PrescripcionState.hp_filtro,
                on_change=PrescripcionState.set_hp_filtro,
                size="2",
                flex="1",
            ),
            rx.icon_button(
                rx.icon("eraser", size=13),
                size="2",
                variant="ghost",
                color_scheme="gray",
                on_click=PrescripcionState.hp_limpiar_filtro,
                title="Limpiar filtro",
                cursor="pointer",
            ),
            align="center",
            spacing="2",
            padding_y="2px",
            width="100%",
        ),
        # ── Tabla ──────────────────────────────────────────────────────────────
        rx.box(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell(
                            rx.hstack(
                                rx.text("Fecha Atención"),
                                _icono_orden_hp("fecha_atencion"),
                                align="center", spacing="1",
                            ),
                            on_click=PrescripcionState.hp_toggle_orden("fecha_atencion"),
                            **{**_CELL_HP_H, "white_space": "nowrap", "cursor": "pointer"},
                        ),
                        rx.table.column_header_cell("Cant.", **_CELL_HP_H),
                        rx.table.column_header_cell(
                            rx.hstack(
                                rx.text("Medicamento"),
                                _icono_orden_hp("nombre_generico"),
                                align="center", spacing="1",
                            ),
                            on_click=PrescripcionState.hp_toggle_orden("nombre_generico"),
                            **{**_CELL_HP_H, "cursor": "pointer"},
                        ),
                        rx.table.column_header_cell("Concentración", **_CELL_HP_H),
                        rx.table.column_header_cell("Presentación",  **_CELL_HP_H),
                    ),
                    style={"position": "sticky", "top": "0", "z_index": "1"},
                ),
                rx.table.body(
                    rx.foreach(PrescripcionState.hp_lista_filtrada, _fila_historial_px)
                ),
                width="100%",
                style={"border_collapse": "collapse"},
            ),
            overflow_y="auto",
            height="30vh",
            width="100%",
        ),
        spacing="1",
        width="100%",
    )


def tab_atencion_actual():
    return rx.box(     #Box Atención Actual
                    rx.hstack(
                                        rx.button("Grabar SOAP",type='submit',height='24px',width="120px",background_color=State.color_boton_celeste,_hover={"bg": State.color_boton_azul}),

                                        ),
                    rx.card(
                            rx.flex(
                                rx.form(                                    
                                    rx.scroll_area(     #Antes scroll_area
                                        rx.text("Motivo de Consulta"),
                                        rx.text_area(name='motivo_consulta',placeholder="Motivo de Consulta",height="80px"),
                                        rx.text("Revisión de Sistemas"),
                                        rx.text_area(name='revision_sistemas',placeholder="Revisión de Sistemas",height="80px"),
                                        rx.text("Subjetivo (*)"),
                                        rx.text_area(name='subjetivo',placeholder="Subjetivo",height= "80px"),
                                        rx.text("Objetivo"),
                                        rx.hstack(
                                            rx.vstack(
                                                rx.text('Peso (Kg)',font_size='10px'),
                                                rx.input(name='peso',placeholder='Peso',height='20px',width='45px',variant='soft',font_size='11px',alignment='center'),),
                                            rx.vstack(
                                                rx.text('Talla (cm)',font_size='10px'),
                                                rx.input(name='talla',placeholder='Talla',height='20px',width='45px',variant='soft',font_size='11px',align='center'),),
                                            rx.vstack(
                                                rx.text('Temp.ºC',font_size='10px',color='gray'),
                                                rx.input(name='temperatura',placeholder='Temp.',height='20px',width='45px',variant='soft',font_size='11px',align='center'),),
                                            rx.vstack(
                                                rx.text('P.Cefal (cm)',font_size='10px',color='gray'),
                                                rx.input(name='perimetro',placeholder='P.Cefalico',height='20px',width='45px',variant='soft',font_size='11px',align='center'),),
                                            rx.vstack(
                                                rx.text('TAS',font_size='10px',color='gray'),
                                                rx.input(name='tas',placeholder='TAS',height='20px',width='45px',variant='soft',font_size='11px',align='center'),),
                                            rx.vstack(
                                                rx.text('TAD',font_size='10px',color='gray'),
                                                rx.input(name='tad',placeholder='TAD',height='20px',width='45px',variant='soft',font_size='11px',align='center'),),
                                            rx.vstack(
                                                rx.text('FC',font_size='10px',color='gray'),
                                                rx.input(name='fc',placeholder='FC',height='20px',width='45px',variant='soft',font_size='11px',align='center'),),
                                            rx.vstack(
                                                rx.text('FR',font_size='10px',color='gray'),
                                                rx.input(name='fr',placeholder='FR',height='20px',width='45px',variant='soft',font_size='11px',align='center'),),
                                            rx.vstack(
                                                rx.text('%Sat.Oxig',font_size='10px',color='gray'),
                                                rx.input(name='saturacion',placeholder='%Sat',height='20px',width='45px',variant='soft',font_size='11px',align='center'),),
                                            margin='4px',
                                        ),                                 

                                        
                                        rx.text_area(name='objetivo',placeholder="Objetivo",height= "80px"),
                                        rx.text("Análisis"),
                                        rx.text_area(name='analisis',placeholder="Análisis",height= "80px"),
                                        rx.text("Plan (*)"),
                                        rx.text_area(name='plan',placeholder="Plan",height= "80px"),
                                        #Contenedor del SOAP
                                        height="79vh", 
                                        background_color="transparent",
                                        #border="solid 1px",
                                        overflow_y="scroll",
                                        ),
                                    on_submit=State.submit_soap
                                ),
                                #Configuracion del Flex
                                direction="column",
                                spacing="3",
                                ),
                                #Configuracion de la Card
                                style={"maxWidth": "100%","height":"82vh"},
                            ),
                            
                    #Configuracion del box que contiene a las pestañas
                    width="50%",
                    height="87vh",
                    position="fixed",
                    top="60px",
                    left='50%',
                    margin_left="2px",
                    margin_top='2px',
                    #bg=State.color_nota_verde,
                    padding="5px",
                    border="solid 1px",
                    ),

def tab_historia_clinica_INVALIDA():
    return rx.box(     #Diagnosticos, Antecedentes Familiares, Personales, etc.
                    rx.tabs.root(
                        rx.tabs.list(
                            rx.tabs.trigger("Diagnósticos", value="diagnosticos",
                                style={
                                "white-space": "pre-wrap",
                                "height": "auto",
                                "min-height": "48px",
                                "line-height": "1.2",
                                "padding": "4px 8px",
                                "text-align": "center",
                            }),
                            rx.tabs.trigger("Antecedentes \nPersonales", value="a_personales",
                                style={
                                "white-space": "pre-wrap",
                                "height": "auto",
                                "min-height": "48px",
                                "line-height": "1.2",
                                "padding": "4px 8px",
                                "text-align": "center",
                                "color":"blue",
                            }),
                            rx.tabs.trigger("Antecedentes \nFamiliares",value="a_familiares",
                                style={
                                "white-space": "pre-wrap",
                                "height": "auto",
                                "min-height": "48px",
                                "line-height": "1.2",
                                "padding": "4px 8px",
                                "text-align": "center",
                                "color":"green",
                            }),
                            rx.tabs.trigger("Alergias",value="a_natales",
                                style={
                                "white-space": "pre-wrap",
                                "height": "auto",
                                "min-height": "48px",
                                "line-height": "1.2",
                                "padding": "4px 8px",
                                "text-align": "center",
                                "color":"red",
                            }),
                            rx.tabs.trigger("Antecedentes \nGinecológicos",value="a_ginecologicos",
                                style={
                                "white-space": "pre-wrap",
                                "height": "auto",
                                "min-height": "48px",
                                "line-height": "1.2",
                                "padding": "4px 8px",
                                "text-align": "center",
                            }),
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
                            #State.tab_derecha=='a_personales',
                            rx.text("item on tab 2"),
                            value="a_personales",
                        ),
                        default_value="diagnosticos",
                    ),
                    #Configuracion del box que contiene a las pestañas
                    width="49%",
                    height="45vh",
                    position="fixed",
                    top="51vh",
                    left='1px',
                    margin_left="2px",
                    margin_top='2px',
                    #bg=State.color_nota_verde,
                    padding="5px",
                    border="solid 1px",
                ),  #Fin box diagnosticos


# ══════════════════════════════════════════════════════════════════════════════
# Panel Historia Atención — componentes de solo lectura
# ══════════════════════════════════════════════════════════════════════════════

def _sv_chip(sv: dict) -> rx.Component:
    return rx.badge(
        rx.hstack(
            rx.text(sv["nombre"], font_size="10px", font_weight="bold"),
            rx.text(sv["valor"], font_size="10px"),
            rx.text(sv["unidad"], font_size="10px", color="var(--gray-9)"),
            spacing="1",
            align="center",
        ),
        variant="soft",
        color_scheme="red",
        padding="1px 6px",
        cursor="default",
    )


def _soap_campo_ro(label: str, valor) -> rx.Component:
    """Campo SOAP de solo lectura: badge cyan + recuadro con HTML (soporta <mark> para resaltado)."""
    return rx.vstack(
        rx.badge(label, background=SOAP_FONDO, variant="solid", size="1",color="black"),
        rx.box(
            rx.html(valor),
            border=f"1px solid {SOAP_FIELD_BORDER}",
            border_radius="4px",
            padding="6px 10px",
            width="100%",
            min_height="32px",
            background="var(--gray-1)",
            font_size="13px",
        ),
        spacing="1",
        width="100%",
    )


def _tarjeta_med_historia(item: dict) -> rx.Component:
    """Tarjeta de un medicamento en modo lectura."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(item["nombre_generico"], font_weight="bold", font_size="13px"),
                rx.spacer(),
                rx.text(item["nombre_presentacion"], font_size="11px", color="var(--gray-9)"),
                align="center",
                width="100%",
            ),
            rx.hstack(
                rx.badge(item["cantidad"], color_scheme="grass", variant="soft", font_size="11px"),
                rx.text("unid.  ·", font_size="11px", color="var(--gray-9)"),
                rx.text(item["concentracion"], font_size="11px"),
                align="center",
                spacing="1",
            ),
            rx.hstack(
                rx.text("Indicaciones:", font_size="11px", font_weight="500"),
                rx.text(item["indicaciones"], font_size="11px"),
                flex_wrap="wrap",
                align="start",
                spacing="1",
            ),
            spacing="1",
            width="100%",
            align="start",
        ),
        padding="8px 10px",
        border="2px solid var(--gray-4)",
        border_radius="6px",
        border_color="#016b3bae",
        background="#FFFFFF",
        width="100%",
    )


def _fila_pedido_ro(row: dict) -> rx.Component:
    return rx.cond(
        row["fila_tipo"] == "grupo",
        rx.text(
            row["texto"],
            font_size="11px",
            font_weight="700",
            color="var(--blue-9)",
            text_transform="uppercase",
            letter_spacing="0.04em",
            padding_top="6px",
        ),
        rx.cond(
            row["fila_tipo"] == "detalle",
            rx.text(
                row["texto"],
                font_size="11px",
                color="var(--gray-10)",
                font_style="italic",
                padding_left="24px",
            ),
            rx.text(
                "• ", row["texto"],
                font_size="12px",
                color="var(--blue-11)",
                padding_left="12px",
            ),
        ),
    )

def _pedido_examenes_ro(items_var, height="calc(100vh - 230px)") -> rx.Component:
    """Lista de exámenes en modo lectura. height configurable para uso en accordion."""
    return rx.scroll_area(
        rx.cond(
            items_var.length() > 0,
            rx.vstack(
                rx.foreach(items_var, _fila_pedido_ro),
                spacing="1",
                padding="10px",
                width="100%",
                align="start",
            ),
            rx.center(
                rx.text(
                    "Sin exámenes pedidos para esta atención",
                    font_size="12px",
                    color="var(--gray-9)",
                ),
                padding="20px",
            ),
        ),
        height=height,
    )


def _prescripcion_ro(items_var, cuidados_var, hay_cuidados_var) -> rx.Component:
    """Contenido de tab 'Prescripción' en modo lectura (reutilizable)."""
    return rx.scroll_area(
        rx.vstack(
            rx.foreach(items_var, _tarjeta_med_historia),
            rx.cond(
                hay_cuidados_var,
                rx.vstack(
                    rx.badge("Cuidados Generales", background=PRESCRIPCION_FONDO, variant="solid", size="1"),
                    rx.box(
                        rx.text(cuidados_var, font_size="12px"),
                        border=f"1px solid {SOAP_FIELD_BORDER}",
                        border_radius="4px",
                        padding="8px",
                        width="100%",
                        background="var(--gray-1)",
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.box(),
            ),
            spacing="2",
            padding="8px",
            width="100%",
        ),
        height="calc(100vh - 230px)",
    )


def _tab_soap_historia() -> rx.Component:
    return rx.vstack(
        rx.cond(
            State.ha_hay_sv,
            rx.flex(
                rx.foreach(State.ha_sv_lista, _sv_chip),
                flex_wrap="wrap",
                gap="4px",
                padding="4px 8px",
                border_bottom="1px solid var(--gray-4)",
                background="var(--cyan-1)",
                width="100%",
            ),
            rx.box(),
        ),
        rx.scroll_area(
            rx.vstack(
                _soap_campo_ro("Motivo de Consulta",   State.ha_soap_html[0]),
                _soap_campo_ro("Revisión de Sistemas", State.ha_soap_html[1]),
                _soap_campo_ro("Subjetivo",            State.ha_soap_html[2]),
                _soap_campo_ro("Objetivo",             State.ha_soap_html[3]),
                _soap_campo_ro("Análisis",             State.ha_soap_html[4]),
                _soap_campo_ro("Plan",                 State.ha_soap_html[5]),
                spacing="2",
                padding="8px",
                width="100%",
            ),
            height="calc(100vh - 230px)",
        ),
        spacing="0",
        width="100%",
    )


def _historia_header(fecha_var, edad_var, motivo_var, diagnosticos_var) -> rx.Component:
    """Cabecera reutilizable: fecha, edad transcurrida, motivo de consulta y diagnósticos vinculados."""
    return rx.box(
        rx.hstack(
            # ── Botón expandir/contraer ───────────────────────────────────
            rx.button(
                rx.cond(
                    State.ha_panel_expandido,
                    rx.icon("minimize-2", size=14),
                    rx.icon("maximize-2", size=14),
                ),
                on_click=State.toggle_ha_panel_expandido,
                variant="ghost",
                size="1",
                type="button",
                cursor="pointer",
                title=rx.cond(State.ha_panel_expandido, "Contraer panel", "Expandir panel"),
                color="black",
                #color="var(--gray-10)",
            ),
            rx.text("INFORMACIÓN HISTÓRICA DE LA ATENCIÓN SELECCIONADA", font_size="13px", font_weight="700",
                    letter_spacing="0.08em", color="var(--gray-23)"),
            background="var(--gray-6)",
            padding="3px 10px",
            width="100%",
        ),
        rx.hstack(
            rx.text(fecha_var, font_weight="bold", font_size="14px"),
            rx.badge(
                rx.hstack(rx.text("hace"), rx.text(edad_var), spacing="1"),
                color_scheme="gray",
                variant="soft",
                font_size="12px",
            ),
            rx.cond(
                motivo_var != "",
                rx.hstack(
                    rx.text("  Motivo de Consulta:", font_size="14px", font_weight="bold", color="black"),
                    rx.text(motivo_var, font_size="14px", font_weight="600", color="black"),
                    spacing="1",
                    align="center",
                    padding_top="2px",
                ),
            ),
            rx.spacer(),
            # Aquí antes Botón Expandir - Contraer   
            # ── Botón Imprimir ────────────────────────────────────────────
            rx.menu.root(
                rx.menu.trigger(
                    rx.button(
                        "🖨️ Imprimir",
                        bg=rx.cond(State.hay_atencion_historial,BOTON_IMPRIMIR, "#94A3B8"),
                        color="white",
                        cursor=rx.cond(State.hay_atencion_historial, "pointer", "not-allowed"),
                        size="1",
                        font_size="0.85em",
                        title=rx.cond(
                            State.hay_atencion_historial,
                            "Imprimir atención seleccionada",
                            "Seleccione una atención en el historial para imprimir",
                        ),
                    ),
                ),
                rx.menu.content(
                    rx.menu.item(
                        rx.cond(
                            State.hay_atencion_historial,
                            rx.text("📅 Atención del ", State.ha_fecha_display,
                                    font_size="11px", color="var(--gray-9)"),
                            rx.text("No hay atención seleccionada",
                                    font_size="11px", color="var(--gray-8)", font_style="italic"),
                        ),
                        disabled=True,
                    ),
                    rx.menu.separator(),
                    rx.menu.item(
                        rx.link("🟥 Historia Clínica (form002)", href=State.url_hist_form002,
                                is_external=True, color="inherit", text_decoration="none",
                                display="block", width="100%"),
                        disabled=State.hay_soap_valido_hist == False,
                    ),
                    rx.menu.item(
                        rx.link("🟩 Prescripción / Receta", href=State.url_hist_receta,
                                is_external=True, color="inherit", text_decoration="none",
                                display="block", width="100%"),
                        disabled=State.ha_hay_px == False,
                    ),
                    rx.menu.item(
                        rx.link("🟦 Pedido Laboratorio", href=State.url_hist_pedido_laboratorio,
                                is_external=True, color="inherit", text_decoration="none",
                                display="block", width="100%"),
                        disabled=State.hay_pedido_laboratorio_hist == False,
                    ),
                    rx.menu.item(
                        rx.link("🟦 🟦 Pedido Otros Exámenes", href=State.url_hist_pedido_otros_examenes,
                                is_external=True, color="inherit", text_decoration="none",
                                display="block", width="100%"),
                        disabled=State.ha_hay_otros_examenes == False,
                    ),
                    rx.menu.item(
                        "📄 Certificado Médico",
                        on_click=CertificadoState.cert_abrir_offcanvas,
                        disabled=State.ha_hay_certificado == False,
                    ),
                    rx.menu.separator(),
                    rx.menu.item(
                        rx.link("📁 Carátula HC (Form001)", href=State.url_hist_form001,
                                is_external=True, color="inherit", text_decoration="none",
                                display="block", width="100%"),
                        disabled=State.hay_soap_valido_hist == False,
                    ),
                ),
            ),
            align="center",
            spacing="2",
            width="100%",
        ),
        rx.foreach(
            diagnosticos_var,
            lambda d: rx.hstack(
                rx.text(d["cie10"], font_size="11px", font_weight="500"),
                rx.text("—", font_size="11px", color="var(--gray-7)"),
                rx.text(d["nomdiagnostico"], font_size="11px", color="var(--gray-11)"),
                spacing="2",
                align="center",
            ),
        ),
        padding="6px 10px",
        border_bottom="1px solid var(--gray-4)",
        background="var(--gray-1)",
        width="100%",
        flex_shrink="0",
    )


def panel_historia_atencion() -> rx.Component:
    """Panel derecha cuando el tab activo es 'Historial Atenciones'."""
    return rx.cond(
        State.id_atencion_seleccionada > 0,
        rx.box(
            _historia_header(State.ha_fecha_display, State.ha_edad_display, State.ha_motivo_display, State.ha_diagnosticos),
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger(
                        "SOAP", value="soap",
                        on_click=State.set_ha_tab_historia("soap"), size="1", style={"color": "red"},
                    ),
                    rx.tabs.trigger(
                        State.ha_label_prescripcion, value="prescripcion",
                        on_click=State.set_ha_tab_historia("prescripcion"), size="1",style={"color": "green"},
                    ),
                    rx.tabs.trigger(
                        State.ha_label_pedidos, value="pedidos",
                        on_click=State.set_ha_tab_historia("pedidos"), size="1",style={"color": "blue"},
                    ),
                    #rx.tabs.trigger(
                    #    "Resultados", value="resultados",
                    #    on_click=State.set_ha_tab_historia("resultados"), size="1",style={"color": "orange"},
                    #),
                ),
                rx.tabs.content(
                    _tab_soap_historia(),
                    value="soap",
                    padding="0",
                ),
                rx.tabs.content(
                    _prescripcion_ro(
                        State.ha_px_items,
                        State.ha_px_cuidados,
                        State.ha_hay_cuidados,
                    ),
                    value="prescripcion",
                    padding="0",
                ),
                rx.tabs.content(
                    rx.accordion.root(
                        rx.accordion.item(
                            header=State.ha_label_lab,
                            content=_pedido_examenes_ro(State.ha_pedido_por_grupo, height="calc((100vh - 350px) / 2)"),
                            value="lab",
                        ),
                        rx.accordion.item(
                            header=State.ha_label_otros,
                            content=_pedido_examenes_ro(State.ha_otros_examenes_por_tipo, height="calc((100vh - 350px) / 2)"),
                            value="otros",
                        ),
                        default_value=["lab"],
                        collapsible=True,
                        type="multiple",
                        width="100%",
                        variant="ghost",
                    ),
                    value="pedidos",
                    padding="0",
                ),
                #rx.tabs.content(
                #    rx.center(
                #        rx.text("Módulo en construcción", color="var(--gray-9)", font_size="13px"),
                #        padding="20px",
                #    ),
                #    value="resultados",
                #),
                value=State.ha_tab_historia,
                flex="1",
                overflow="hidden",
                display="flex",
                flex_direction="column",
            ),
            display="flex",
            flex_direction="column",
            width="100%",
            height="100%",
            background="white",
            overflow="hidden",
        ),
        rx.box(
            rx.center(
                rx.text(
                    "Seleccione una atención del historial",
                    color="var(--gray-9)",
                    font_size="13px",
                ),
                height="100%",
            ),
            width="100%",
            height="100%",
            background="white",
        ),
    )


def panel_historial_prescripciones() -> rx.Component:
    """Panel derecha cuando el tab activo es 'Historial Prescripciones'."""
    return rx.box(
        rx.cond(
            PrescripcionState.hp_hay_sel,
            rx.vstack(
                _historia_header(
                    PrescripcionState.hp_sel_fecha,
                    PrescripcionState.hp_sel_edad,
                    PrescripcionState.hp_sel_motivo,
                    PrescripcionState.hp_sel_diagnosticos,
                ),
                _prescripcion_ro(
                    PrescripcionState.hp_sel_items,
                    PrescripcionState.hp_sel_cuidados,
                    PrescripcionState.hp_hay_sel_cuidados,
                ),
                spacing="0",
                width="100%",
                height="100%",
            ),
            rx.center(
                rx.text(
                    "Seleccione una fila en la tabla para ver la prescripción",
                    color="var(--gray-9)",
                    font_size="13px",
                ),
                height="100%",
            ),
        ),
        width="100%",
        height="100%",
        background="white",
        border_left="1px solid var(--gray-5)",
        overflow="hidden",
    )