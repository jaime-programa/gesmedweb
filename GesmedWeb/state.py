import re
import reflex as rx
import bcrypt
from pydantic import BaseModel as _PydanticBase
from reflex.config import get_config as _rx_get_config
from sqlmodel import Field, SQLModel, Session, create_engine, select
from sqlalchemy import text

# URL base del backend (http://localhost:8000 en dev; se configura en rxconfig.py para producción)
_BACKEND = _rx_get_config().api_url.rstrip("/")
from typing import Tuple
from datetime import date,datetime,timedelta
from .modelos.mis_modelos import (
    Paciente, Atencion, Points, Diagnostico, Cie10, Rel_atencion_diagnostico,
    ReporteImpreso, ReporteImagen, ReporteSeccion, ReporteCelda, AntecedenteFamiliar, Alergia,
    Certificado, OtrosExamenesTipo, OtrosExamenesCatalogo, OtrosExamenesPedido,
    Cita, TipoCita, Imagenes, ResultadosImagenes,
)
from .querys.resultados_querys import (
    cargar_resultados_imagen_paciente,
    cargar_imagenes_resultado,
    cargar_imagenes_sin_clasificar,
    insertar_imagen      as rq_insertar_imagen,
    asignar_imagen_a_resultado,
    actualizar_rotacion  as rq_actualizar_rotacion,
    reordenar_imagenes   as rq_reordenar,
    eliminar_imagen      as rq_eliminar_imagen,
    cargar_marcas,
    guardar_marca        as rq_guardar_marca,
    eliminar_marca       as rq_eliminar_marca,
    actualizar_marca     as rq_actualizar_marca,
    cargar_catalogo_lab,
    guardar_resultado_lab,
    crear_resultado_imagen,
    eliminar_resultado_imagen as rq_eliminar_resultado_imagen,
    cargar_catalogo_examenes_imagen,
    cargar_catalogo_completo_lab,
    cargar_historial_lab,
    cargar_historial_sv,
)
from .utils.imagen_utils import (
    pdf_a_jpg,
    normalizar_a_jpg,
    guardar_imagen       as img_guardar,
    eliminar_imagen      as img_eliminar,
    leer_imagen          as img_leer,
)
from .querys.querys import (
    get_engine, base_actual, cambiar_base, base_migrada_disponible, consultar_pacientes_por_nombre, estado_propiedad_paciente, historial_atenciones_con_cie10,
    historial_diagnosticos, atenciones_vinculadas_a_diagnostico,
    diagnosticos_vinculados_a_atencion, carga_medicos, carga_seguros,
    buscar_medicamentos, listar_presentaciones, listar_alergias_paciente,
    listar_prescripcion_atencion, obtener_prescripcion_cuidados,
    guardar_item_prescripcion, actualizar_prescripcion_cuidados,
    eliminar_item_prescripcion, agregar_medicamento_nuevo,
    actualizar_item_prescripcion,
    cargar_catalogo_sv, cargar_sv_atencion, guardar_sv_atencion,
    actualizar_atencion, historial_prescripciones_paciente,
    signos_vitales_atencion, diagnosticos_atencion_detalle,
    cargar_catalogo_examenes, cargar_grupos_examenes,
    cargar_pedido_atencion, guardar_pedido_examenes,
    listar_ant_familiares,
    listar_tipos_medicamento, buscar_similares_medicamento, guardar_medicamento_catalogo,
    listar_usuarios, crear_usuario, actualizar_usuario, resetear_clave,
    listar_examen_tipos, crear_examen_tipo, actualizar_examen_tipo, eliminar_examen_tipo,
    listar_examen_catalogo, crear_examen_catalogo, actualizar_examen_catalogo,
    eliminar_examen_catalogo,
    es_atencion_bajo_interconsulta, registrar_interconsulta,
    crear_solicitud_interconsulta, listar_solicitudes_interconsulta,
    finalizar_solicitud_interconsulta, cerrar_interconsulta,
    listar_medicos_para_interconsulta,
)
from .crypto import GesmedCrypto

class State(rx.State):
    is_authenticated: bool = False  #Controla si el usuario se ha autenticado
    permisos: str = ""  # Campo permisos de la tabla points
    contenido_derecha: str = "historial_atenciones"
    show_menu: bool=False
    show_submenu: bool = False
    show_sidebar: bool = False
    show_panel_izq: bool = True
    hay_signos_vitales:bool = False
    ancho_contenido: str="50%"
    color_gris: str="rgb(240,240,240)"
    color_boton_azul: str="rgb(0,113,227)"
    color_boton_celeste: str="rgba(0,113,227,.7)"
    color_nota_azul: str="rgb(232, 248, 255)"
    color_nota_verde: str="rgb(232, 248, 255)"
    color_petroleo: str="rgb(27, 39, 51)"
    color_petroleo_obscuro: str="rgb(18, 26, 38)"
    color_letras_celestes: str="rgb(64, 194, 255)"
    color_letras_azules: str="rgb(25, 102, 209)"
    error_message: str = "" #Mensaje de error en la autenticación
    login_cargando: bool = False
    #engine: any
    page: int = 1
    page_size: int = 10
    total_rows: int = 0
    px1:str=''  #nombre de usuario
    px2:str=''  #password
    que_paciente_busco: str =''
    lista_pacientes: list[dict]=[]
    pac_orden_col: str = ""
    pac_orden_asc: bool = True
    lista_medicos: dict={}
    paciente_seleccionado: list = []
    paciente_actual_es_propio: bool = True
    paciente_actual_disponible: bool = False
    paciente_actual_interconsulta: bool = False  # acceso temporal vía solicitud_interconsulta vigente
    diagnostico_seleccionado: list = []
    atencion_seleccionada: list = []
    celda_pacientes: dict = {"row": None, "column": None}
    celda_diagnosticos: dict ={"row":None, "column":None}
    celda_atenciones: dict ={"row":None, "column":None}
    nombre_medico: str = ''
    id_medico: int = 0
    rol_usuario: str = ""  # MEDICO_ATENCION | MEDICO_CONSULTA | SECRETARIA
    lista_atenciones: list[dict]=[]
    lista_diagnosticos: list[dict]=[]
    lista_ant_familiares: list[dict] = []
    lista_alergias: list[dict] = []
    lista_atenciones_vinculadas_a_diagnostico: list =[]
    lista_diagnosticos_vinculados: list[int] = []
    id_atencion_seleccionada: int = 0
    filtro_diagnostico_activo: bool = False
    tab_izq_activo: str = "diagnosticos"
    offcanvas_config: bool = False

    # ── Historia: datos cargados al seleccionar una atención ─────────────────
    ha_sv_lista:        list[dict] = []   # SV con valor registrado
    ha_diagnosticos:    list[dict] = []   # [{cie10, nomdiagnostico}]
    ha_px_items:        list[dict] = []   # prescripciones (lectura)
    ha_px_cuidados:     str        = ""   # cuidados generales (lectura)
    ha_pedido_examenes:       list[dict] = []   # exámenes laboratorio (lectura)
    ha_otros_examenes:        list[dict] = []   # otros exámenes / imagen (lectura)
    ha_hay_otros_examenes:    bool       = False
    ha_hay_certificado:       bool       = False
    ha_tab_historia:          str        = "soap"  # tab activo en panel historia
    ha_panel_expandido:       bool       = False   # panel_historia_atencion a pantalla completa
    ha_sub_tab_pedidos:       str        = "lab"   # sub-tab activo dentro de Pedido Exámenes
    #que_fecha_atencion_busco: str=''
    #que_motivo_atencion_busco: str=''
    que_historial_busco: str=''
    tab_derecha:str=''
    si_contiene_texto:bool =False
    

    def toggle_offcanvas_config(self):
        self.offcanvas_config = not self.offcanvas_config

    def set_px1(self, value: str):
        self.px1 = value

    def set_px2(self, value: str):
        self.px2 = value

    def set_tab_izq(self, tab: str):
        self.tab_izq_activo = tab

    def cambia_tab(self, tab: str):
        self.contenido_derecha = tab
        if tab == "historial_atenciones" and self.id_atencion_seleccionada == 0 and self.lista_atenciones:
            yield from self.selecciona_atencion(self.lista_atenciones[0]['id_atencion'])
        if tab == "historial_prescripciones":
            yield PrescripcionState.hp_cargar

    def toggle_submenu(self):
        self.show_submenu = not self.show_submenu

    def toggle_sidebar(self):
        self.show_sidebar = not self.show_sidebar
        if self.show_sidebar:
            self.ancho_contenido="41%"
        else:
            self.ancho_contenido="55%"

    def toggle_panel_izq(self):
        self.show_panel_izq = not self.show_panel_izq

    def logout(self):
        self.diagnostico_seleccionado=[]
        yield AtencionState.reinicia_soap
        yield AtencionState.reset_atencion_iniciada
        yield rx.redirect('/pacientes')

    def hacer_logout(self):
        # Limpia autenticación y credenciales
        self.is_authenticated = False
        self.px1 = ""
        self.px2 = ""
        self.error_message = ""
        # Limpia datos de pacientes y sesión
        self.lista_pacientes = []
        self.paciente_seleccionado = []
        self.diagnostico_seleccionado = []
        self.atencion_seleccionada = []
        self.lista_atenciones = []
        self.lista_diagnosticos = []
        self.lista_ant_familiares = []
        self.lista_alergias = []
        self.lista_diagnosticos_vinculados = []
        self.lista_atenciones_vinculadas_a_diagnostico = []
        self.id_atencion_seleccionada = 0
        self.contenido_derecha = "historial_atenciones"
        self.que_paciente_busco = ""
        self.que_historial_busco = ""
        self.nombre_medico = ""
        self.id_medico = 0
        self.rol_usuario = ""
        self.permisos = ""
        self.ha_sv_lista = []
        self.ha_diagnosticos = []
        self.ha_px_items = []
        self.ha_px_cuidados = ""
        self.ha_pedido_examenes = []
        self.ha_otros_examenes = []
        self.ha_hay_otros_examenes = False
        self.ha_hay_certificado = False
        self.ha_tab_historia = "soap"
        self.ha_sub_tab_pedidos = "lab"
        yield AtencionState.reinicia_soap
        yield PrescripcionState.reinicia_prescripcion
        # Hard reload: cierra WebSocket y reinicia frontend completamente
        yield rx.call_script("window.location.replace('/')")
    
    
    def handle_login(self):
        self.login_cargando = True
        self.error_message = ""
        yield
        with Session(get_engine()) as sesion:
            query = select(Points).where(Points.usuario == self.px1)
            resultado = sesion.exec(query)
            user = resultado.first()
            if user is not None:
                password_hash = self.px2.encode('utf-8')
                password_in=user.clave.encode('utf-8')
                if bcrypt.checkpw(password_hash, password_in):
                    self.is_authenticated=True
                    self.set_que_paciente_busco('')
                    self.nombre_medico=user.nombre_medico
                    self.id_medico=user.id_medico
                    self.rol_usuario=user.rol
                    self.permisos=user.permisos
                    self.login_cargando = False
                    yield rx.redirect("/pacientes")
                    return
                else:
                    self.is_authenticated=False
                    self.error_message = "Acceso denegado\n Revise su contraseña"
            else:
                self.is_authenticated=False
                self.error_message = "Usuario no encontrado"
        self.login_cargando = False

    def entrar_false(self):
        self.is_authenticated=True
        self.carga_lista_medicos()
        return rx.redirect('/pacientes')
    
    @rx.var
    def es_autentico(self) -> bool:
        return self.is_authenticated

    @rx.var
    def puede_config_reportes(self) -> bool:
        return len(self.permisos) > 0 and self.permisos[0] == "R"

    @rx.var
    def ve_solo_propios_pacientes(self) -> bool:
        """permisos[1]: alcance de LECTURA. 'P' = solo pacientes propios (con
        atención del médico logueado), 'T' o ausente = todos (comportamiento previo)."""
        return len(self.permisos) > 1 and self.permisos[1] == "P"

    @rx.var
    def edita_solo_propios_pacientes(self) -> bool:
        """permisos[2]: alcance de ESCRITURA. 'P' = solo puede modificar pacientes
        propios (aunque pueda leer otros si permisos[1] == 'T'), 'T' o ausente =
        modifica cualquier paciente (comportamiento previo)."""
        return len(self.permisos) > 2 and self.permisos[2] == "P"

    @rx.var
    def paciente_actual_ajeno(self) -> bool:
        """True cuando el paciente actual es ajeno (sin atención propia del
        médico logueado, y con al menos una atención de otro médico)."""
        return not self.paciente_actual_es_propio

    @rx.var
    def resultados_deshabilitado_por_ajeno(self) -> bool:
        """Para el panel Resultado_imagenes: los botones 'Subir archivos' y
        'Laboratorio' se deshabilitan solo cuando el paciente es ajeno Y el
        perfil del médico restringe la escritura a sus propios pacientes
        (permisos[2] == 'P', perfil 3 'T/P'). En perfil 1 (T/T) los botones
        quedan habilitados aunque el paciente sea ajeno, porque ese perfil
        puede modificar cualquier paciente. En perfil 2 (P/P) no aplica en
        la práctica, ya que ese perfil ni siquiera ve pacientes ajenos. Tampoco
        aplica si el acceso es por una interconsulta vigente (el auxiliar sí
        puede escribir)."""
        return self.edita_solo_propios_pacientes and self.paciente_actual_ajeno and not self.paciente_actual_interconsulta

    # ── Control de perfiles ───────────────────────────────────────────────────
    # Perfiles: SECRETARIA | MEDICO_CONSULTA | MEDICO_ATENCION | ADMIN

    @rx.var
    def es_secretaria(self) -> bool:
        return self.rol_usuario == "SECRETARIA"

    @rx.var
    def es_medico_lee(self) -> bool:
        return self.rol_usuario == "MEDICO_CONSULTA"

    @rx.var
    def es_medico_prop(self) -> bool:
        return self.rol_usuario == "MEDICO_ATENCION"

    @rx.var
    def es_admin(self) -> bool:
        return self.rol_usuario == "ADMIN"

    @rx.var
    def puede_ver_clinica(self) -> bool:
        """Med.Lee + Med.Prop + Admin pueden ver información clínica. Sec no."""
        return self.rol_usuario in ["MEDICO_CONSULTA", "MEDICO_ATENCION", "ADMIN"]

    @rx.var
    def puede_escribir(self) -> bool:
        """Solo Med.Prop y Admin pueden crear/modificar registros clínicos."""
        return self.rol_usuario in ["MEDICO_ATENCION", "ADMIN"]

    @rx.var
    def puede_escribir_paciente_actual(self) -> bool:
        """puede_escribir (rol) + respeta el alcance de escritura (permisos[2])
        sobre el paciente actualmente cargado. paciente_actual_es_propio se
        calcula una sola vez, al seleccionar el paciente (no en cada acceso),
        para no repetir la consulta a Atencion en cada render. Una interconsulta
        vigente también habilita la escritura aunque el paciente no sea propio."""
        return self.puede_escribir and (
            not self.edita_solo_propios_pacientes
            or self.paciente_actual_es_propio
            or self.paciente_actual_interconsulta
        )

    @rx.var
    def puede_admin(self) -> bool:
        """Solo Admin accede a funciones de administración del sistema."""
        return self.rol_usuario == "ADMIN"
    
    ### Lista de Pacientes ####
    @rx.var
    def nombre_paciente_seleccionado(self) -> str:
        if self.paciente_seleccionado and len(self.paciente_seleccionado) > 1:
            return str(self.paciente_seleccionado[1])
        return ""

    @rx.var
    def nro_hclinica_seleccionado(self) -> int:
        if self.paciente_seleccionado and len(self.paciente_seleccionado) > 0:
            return self.paciente_seleccionado[0]
        return -1

    @rx.var
    def hay_paciente_seleccionado(self) ->bool:
        if self.paciente_seleccionado==None:
            return False
        elif len(self.paciente_seleccionado)==0:
            return False
        else:
            return True
        
    def quita_seleccion_pacientes(self):
        self.paciente_seleccionado = []

    def hay_filtro_pacientes(self) -> bool:
        return True

    # ── URLs de impresión para la atención seleccionada en el historial ──────
    # Usan id_atencion_seleccionada (fila activa en tabla_historial_atenciones)
    @rx.var
    def _url_params_hist(self) -> str:
        return (f"lk_paciente={self.nro_hclinica_seleccionado}"
                f"&lk_atencion={self.id_atencion_seleccionada}"
                f"&lk_medico={self.id_medico}")

    @rx.var
    def url_hist_form002(self) -> str:
        return f"{_BACKEND}/reporte/form002?{self._url_params_hist}"

    @rx.var
    def url_hist_receta(self) -> str:
        return f"{_BACKEND}/reporte/receta?{self._url_params_hist}"

    @rx.var
    def url_hist_pedido_laboratorio(self) -> str:
        return f"{_BACKEND}/reporte/pedido_laboratorio?{self._url_params_hist}"

    @rx.var
    def url_hist_pedido_imagen(self) -> str:
        return f"{_BACKEND}/reporte/pedido_imagen?{self._url_params_hist}"

    @rx.var
    def url_hist_pedido_otros_examenes(self) -> str:
        return f"{_BACKEND}/reporte/pedido_examen?{self._url_params_hist}&modo=pedido_plano"

    @rx.var
    def url_hist_certificado(self) -> str:
        return f"{_BACKEND}/reporte/certificado?{self._url_params_hist}"

    @rx.var
    def url_hist_form001(self) -> str:
        return (f"{_BACKEND}/reporte/form001"
                f"?lk_paciente={self.nro_hclinica_seleccionado}"
                f"&lk_atencion=0&lk_medico={self.id_medico}")

    @rx.var
    def hay_atencion_historial(self) -> bool:
        return self.id_atencion_seleccionada > 0

    @rx.var
    def hay_soap_valido_hist(self) -> bool:
        return (
            bool(self.atencion_seleccionada)
            and len(self.atencion_seleccionada) > 4
            and bool(str(self.atencion_seleccionada[4]).strip())
        )

    @rx.var
    def hay_pedido_laboratorio_hist(self) -> bool:
        return len(self.ha_pedido_examenes) > 0

    def set_que_paciente_busco(self,filtro:str):
        self.que_paciente_busco=filtro
        if callable(self.carga_pacientes_filtrados):
            self.carga_pacientes_filtrados()
        else:
            print("Error: carga_pacientes_filtrados no es una función callable")
            self.carga_pacientes_filtrados
        
    @rx.var
    def actualiza_pacientes(self) -> list[dict]:
        return self.lista_pacientes

    @rx.var
    def lista_pacientes_ordenada(self) -> list[dict]:
        rows = self.lista_pacientes
        col = self.pac_orden_col
        if not col:
            return rows
        def _key(p):
            v = p.get(col)
            if v is None:
                return (1, "")
            if isinstance(v, str):
                return (0, v.lower())
            return (0, v)
        return sorted(rows, key=_key, reverse=not self.pac_orden_asc)

    def pac_toggle_orden(self, col: str):
        if self.pac_orden_col == col:
            self.pac_orden_asc = not self.pac_orden_asc
        else:
            self.pac_orden_col = col
            self.pac_orden_asc = True

    @rx.var
    def lista_pacientes_rows(self) -> list[list]:
        return [
            [p.get('nro_hclinica',''), p.get('nombre_completo',''), p.get('edad',''),
             p.get('grupo_sanguineo',''), p.get('seguro',''), p.get('cuantas_atenciones',0)]
            for p in self.lista_pacientes
        ]

    @rx.var
    def lista_diagnosticos_rows(self) -> list[list]:
        return [
            [d.get('cie10',''), d.get('nombre_cie10',''), d.get('tipo',''),
             str(d.get('fecha_diagnostico','')), str(d.get('fecha_inicio_aparente','')), d.get('observaciones','')]
            for d in self.lista_diagnosticos
        ]

    @rx.var
    def lista_atenciones_rows(self) -> list[list]:
        return [
            [str(a.get('fecha_atencion','')), a.get('codigos_cie10',''), a.get('motivo_consulta','')]
            for a in self.lista_atenciones
        ]
            
    def carga_lista_medicos(self):
        self.lista_medicos=carga_medicos()
        print(self.lista_medicos)

    def carga_pacientes_filtrados(self):
        with Session(get_engine()) as session:
            self.lista_pacientes=consultar_pacientes_por_nombre(session,self.que_paciente_busco,self.id_medico,self.ve_solo_propios_pacientes)

    def _autoriza_y_selecciona_paciente(self, datos: list) -> bool:
        """Fija paciente_seleccionado tras verificar el alcance de lectura
        (permisos[1]) contra el paciente puntual — no solo confiar en que la
        búsqueda ya lo haya filtrado, ya que un médico puede llegar a un
        paciente por otra vía (agenda, selección directa, etc.). También
        cachea paciente_actual_es_propio/paciente_actual_disponible para que
        puede_escribir_paciente_actual y la UI no repitan la consulta a
        Atencion en cada acceso.

        Un paciente sin ninguna atención registrada (de ningún médico) está
        "disponible": aún no tiene dueño, así que se trata como accesible
        para cualquier médico (puede verlo y registrarle su primera
        atención), sin importar su alcance de lectura/escritura."""
        nro_hclinica = datos[0]
        with Session(get_engine()) as session:
            accesible, disponible = estado_propiedad_paciente(session, nro_hclinica, self.id_medico)
            interconsulta = False
            if not accesible:
                interconsulta = es_atencion_bajo_interconsulta(session, nro_hclinica, self.id_medico)
        if self.ve_solo_propios_pacientes and not accesible and not interconsulta:
            return False
        self.paciente_seleccionado = datos
        self.paciente_actual_es_propio = accesible
        self.paciente_actual_disponible = disponible
        self.paciente_actual_interconsulta = interconsulta
        self.contenido_derecha = ""
        return True

    def click_tabla_pacientes(self, cell_data: Tuple):
        self.celda_pacientes = {
            "row": cell_data[1],
            "column": cell_data[0]
        }
        fila = self.lista_pacientes[self.celda_pacientes['row']]
        datos = [fila['nro_hclinica'], fila['nombre_completo'], fila['edad'],
                 fila['fecha_nacimiento'], fila['grupo_sanguineo'], fila['seguro']]
        if not self._autoriza_y_selecciona_paciente(datos):
            yield rx.toast.error("No tiene permiso para acceder a este paciente.")
            return
        yield AtencionState.reinicia_soap
        #self.diagnostico_seleccionado.clear

    ### Atenciones - Historia Clínica ####
    def actualizar_que_hc_busco(self,filtro:str):
        self.que_historial_busco=filtro
        self.filtro_diagnostico_activo = False
        if callable(self.actualiza_atenciones_filtradas):
            self.actualiza_atenciones_filtradas()
        else:
            print("Error: carga_historial_atenciones_filtradas no es una función callable")
            self.actualiza_atenciones_filtradas

    def carga_atenciones(self):
        with Session(get_engine()) as session:
            self.lista_atenciones=historial_atenciones_con_cie10(session,self.paciente_seleccionado[0],'',self.id_medico)
            self.lista_diagnosticos=historial_diagnosticos(session,self.paciente_seleccionado[0],self.id_medico)
            self.lista_ant_familiares=listar_ant_familiares(session,self.paciente_seleccionado[0],self.id_medico)
            self.lista_alergias=listar_alergias_paciente(session,self.paciente_seleccionado[0])
        
        self.que_historial_busco = ''
        self.contenido_derecha = ''
        self.id_atencion_seleccionada = 0
        self.lista_diagnosticos_vinculados = []
        self.ha_sv_lista = []
        self.ha_diagnosticos = []
        self.ha_px_items = []
        self.ha_px_cuidados = ""
        self.ha_pedido_examenes = []
        self.ha_otros_examenes = []
        self.ha_hay_otros_examenes = False
        self.ha_hay_certificado = False
        self.ha_tab_historia = "soap"
        self.ha_sub_tab_pedidos = "lab"
        yield AtencionState.reinicia_soap
        yield AtencionState.reset_atencion_iniciada
        yield rx.redirect('/atencion')
    
    #@rx.var
    def limpia_hc_busco(self):
        self.que_historial_busco=''
        self.filtro_diagnostico_activo = False
        if callable(self.actualiza_atenciones_filtradas):
            self.actualiza_atenciones_filtradas()
        else:
            print("Error: carga_historial_atenciones_filtradas no es una función callable")
            self.actualiza_atenciones_filtradas
    
    def escucho_hc_busco(self):
        self.que_historial_busco

    def actualiza_atenciones_filtradas(self):
        with Session(get_engine()) as session:
            self.lista_atenciones=historial_atenciones_con_cie10(session,self.paciente_seleccionado[0],self.que_historial_busco,self.id_medico)
        #self.lista_atenciones=historial_atenciones(self.paciente_seleccionado[0],self.que_historial_busco)
        
        
    ### Diagnosticos #####
    def click_tabla_diagnosticos(self, cell_data: Tuple):
        self.celda_diagnosticos = {
            "row": cell_data[1],
            "column": cell_data[0]
        }
        self.diagnostico_seleccionado=[self.lista_diagnosticos[self.celda_diagnosticos['row']]['id_diagnostico'],
                                    self.lista_diagnosticos[self.celda_diagnosticos['row']]['cie10'],
                                    self.lista_diagnosticos[self.celda_diagnosticos['row']]['nombre_cie10'],
                                    self.lista_diagnosticos[self.celda_diagnosticos['row']]['tipo'],
                                    self.lista_diagnosticos[self.celda_diagnosticos['row']]['fecha_diagnostico'],
                                    self.lista_diagnosticos[self.celda_diagnosticos['row']]['fecha_inicio_aparente'],
                                    self.lista_diagnosticos[self.celda_diagnosticos['row']]['observaciones']]
        
        if self.diagnostico_seleccionado[0] == 0:
            self.lista_atenciones_vinculadas_a_diagnostico = []
            print(f"🟦 Añadir nuevo diagnostico")
        else:
            #PONER ATENCIÓN AQUÍ  TESLA
            with Session(get_engine()) as session:
                self.lista_atenciones_vinculadas_a_diagnostico=atenciones_vinculadas_a_diagnostico(session,self.diagnostico_seleccionado[0])
            print(self.lista_atenciones_vinculadas_a_diagnostico)
        self.atenciones_con_estilo()
        
    
    #Estilo a atenciones vinculadas a diagnostico seleccionado
    @rx.var
    def atenciones_con_estilo(self) -> list[dict]:
        return [
            {
                **atencion,
                "class_name": "resaltado" if atencion["id_atencion"] in self.lista_atenciones_vinculadas_a_diagnostico else ""
            }
            for atencion in self.lista_atenciones
        ]

    @rx.var
    def atenciones_visibles(self) -> list[dict]:
        if self.filtro_diagnostico_activo and self.lista_atenciones_vinculadas_a_diagnostico:
            ids = self.lista_atenciones_vinculadas_a_diagnostico
            return [a for a in self.lista_atenciones if a.get("id_atencion") in ids]
        return self.lista_atenciones

    @rx.var
    def diagnosticos_con_estilo(self) -> list[dict]:
        sel_id = self.diagnostico_seleccionado[0] if self.diagnostico_seleccionado else 0
        return [
            {
                **d,
                "destacado": d["id_diagnostico"] in self.lista_diagnosticos_vinculados,
                "seleccionado": d["id_diagnostico"] == sel_id,
            }
            for d in self.lista_diagnosticos
        ]

    @rx.var
    def ant_personales_con_estilo(self) -> list[dict]:
        sel_id = self.diagnostico_seleccionado[0] if self.diagnostico_seleccionado else 0
        return [
            {
                **d,
                "destacado": d["id_diagnostico"] in self.lista_diagnosticos_vinculados,
                "seleccionado": d["id_diagnostico"] == sel_id,
            }
            for d in self.lista_diagnosticos
            if d.get("tipo") == "Ant.Personal"
        ]

    @rx.var
    def tab_label_diagnosticos(self) -> str:
        return f"Diagnósticos ({len(self.diagnosticos_con_estilo)})"

    @rx.var
    def tab_label_ant_personales(self) -> str:
        return f"Antecedentes \nPersonales ({len(self.ant_personales_con_estilo)})"

    @rx.var
    def tab_label_ant_familiares(self) -> str:
        return f"Antecedentes \nFamiliares ({len(self.lista_ant_familiares)})"

    @rx.var
    def tab_label_alergias(self) -> str:
        return f"Alergias ({len(self.lista_alergias)})"

    ### Historial Atenciones ######
    def click_tabla_historial_atenciones(self,cell_data:Tuple):
        self.celda_atenciones={
            "row":cell_data[1],
            "column":cell_data[0]
            
        }
        self.atencion_seleccionada=[self.lista_atenciones[self.celda_atenciones['row']]['lk_medico'],
                                    self.lista_atenciones[self.celda_atenciones['row']]['fecha_atencion'],
                                    self.lista_atenciones[self.celda_atenciones['row']]['motivo_consulta'],
                                    self.lista_atenciones[self.celda_atenciones['row']]['revision_sistemas'],
                                    self.lista_atenciones[self.celda_atenciones['row']]['subjetivo'],
                                    self.lista_atenciones[self.celda_atenciones['row']]['objetivo'],
                                    self.lista_atenciones[self.celda_atenciones['row']]['analisis'],
                                    self.lista_atenciones[self.celda_atenciones['row']]['plan'],
                                    #self.lista_atenciones[self.celda_atenciones['row']]['codigos_cie10'],
                                    ]       
        self.contenido_derecha='historial_atenciones'
        
    def invoca_signos_vitales(self):
        if self.hay_signos_vitales:
            self.hay_signos_vitales=False
        else:
            self.hay_signos_vitales=True

    @rx.var
    def contiene_motivo(self) ->bool:
        texto_motivo = str(self.atencion_seleccionada[2]) if self.atencion_seleccionada and len(self.atencion_seleccionada[2]) > 2 else "_"
        if len(str(self.que_historial_busco))>2:
            return str(self.que_historial_busco).lower() in texto_motivo.lower()
        else:
            return False
    
    @rx.var
    def contiene_revision(self)->bool:
        texto_revision = str(self.atencion_seleccionada[3]) if self.atencion_seleccionada and len(self.atencion_seleccionada[3]) > 2 else "_"
        if len(str(self.que_historial_busco))>2:
            return str(self.que_historial_busco).lower() in texto_revision.lower()
        else:
            return False
    
    @rx.var
    def contiene_subjetivo(self)->bool:    
        texto_subjetivo = str(self.atencion_seleccionada[4]) if self.atencion_seleccionada and len(self.atencion_seleccionada[4]) > 2 else "_"
        if len(str(self.que_historial_busco))>2:
            return str(self.que_historial_busco).lower() in texto_subjetivo.lower()
        else:
            return False
    
    @rx.var
    def contiene_objetivo(self)->bool:
        texto_objetivo = str(self.atencion_seleccionada[5]) if self.atencion_seleccionada and len(self.atencion_seleccionada[5]) > 2 else "_"
        if len(str(self.que_historial_busco))>2:
            return str(self.que_historial_busco).lower() in texto_objetivo.lower()
        else:
            return False
        
    @rx.var
    def contiene_analisis(self)->bool:
        texto_analisis = str(self.atencion_seleccionada[6]) if self.atencion_seleccionada and len(self.atencion_seleccionada[6]) > 2 else "_"
        if len(str(self.que_historial_busco))>2:
            return str(self.que_historial_busco).lower() in texto_analisis.lower()
        else:
            return False

    @rx.var
    def contiene_plan(self)->bool:
        texto_plan = str(self.atencion_seleccionada[7]) if self.atencion_seleccionada and len(self.atencion_seleccionada[7]) > 2 else "_"
        if len(str(self.que_historial_busco))>2:
            return str(self.que_historial_busco).lower() in texto_plan.lower()
        else:
            return False
        

    @rx.var
    def ha_fecha_display(self) -> str:
        if self.atencion_seleccionada and len(self.atencion_seleccionada) > 1:
            parts = str(self.atencion_seleccionada[1]).split("|")
            return parts[0].strip()
        return ""

    @rx.var
    def ha_edad_display(self) -> str:
        if self.atencion_seleccionada and len(self.atencion_seleccionada) > 1:
            parts = str(self.atencion_seleccionada[1]).split("|")
            return parts[1].strip() if len(parts) > 1 else ""
        return ""

    @rx.var
    def ha_motivo_display(self) -> str:
        if self.atencion_seleccionada and len(self.atencion_seleccionada) > 2:
            return str(self.atencion_seleccionada[2])
        return ""

    @rx.var
    def ha_hay_sv(self) -> bool:
        return len(self.ha_sv_lista) > 0

    @rx.var
    def ha_hay_px(self) -> bool:
        return len(self.ha_px_items) > 0

    @rx.var
    def ha_label_prescripcion(self) -> str:
        n = len(self.ha_px_items)
        return f"Prescripción ({n})" if n else "Prescripción"

    @rx.var
    def ha_label_pedidos(self) -> str:
        n = (1 if self.ha_pedido_examenes else 0) + (1 if self.ha_otros_examenes else 0)
        return f"Pedido Exámenes ({n})" if n else "Pedido Exámenes"

    @rx.var
    def ha_label_lab(self) -> str:
        n = len(self.ha_pedido_examenes)
        return f"Laboratorio ({n})" if n else "Laboratorio"

    @rx.var
    def ha_label_otros(self) -> str:
        n = len(self.ha_otros_examenes)
        return f"Otros Exámenes ({n})" if n else "Otros Exámenes"

    @rx.var
    def ha_hay_cuidados(self) -> bool:
        return bool(self.ha_px_cuidados.strip())

    @rx.var
    def ha_pedido_por_grupo(self) -> list[dict]:
        """Lista plana con filas tipo 'grupo' (cabecera) y 'examen' (ítem)."""
        groups: dict = {}
        order: list = []
        for e in self.ha_pedido_examenes:
            g = e.get("nombre_grupo") or "Sin grupo"
            if g not in groups:
                groups[g] = []
                order.append(g)
            groups[g].append(e["nombre_examen"])
        rows: list = []
        for g in sorted(order):
            rows.append({"fila_tipo": "grupo",  "texto": g})
            for ex in groups[g]:
                rows.append({"fila_tipo": "examen", "texto": ex})
        return rows

    @rx.var
    def ha_otros_examenes_por_tipo(self) -> list[dict]:
        """Lista plana de otros exámenes con cabecera de tipo y filas de ítems."""
        rows: list = []
        current = ""
        for item in self.ha_otros_examenes:
            tipo = item.get("tipo", "")
            if tipo != current:
                rows.append({"fila_tipo": "grupo", "texto": tipo})
                current = tipo
            alias   = item.get("alias", "")
            nombre  = item.get("nombre", "")
            detalle = item.get("detalle", "")
            rows.append({"fila_tipo": "examen", "texto": f"{alias} - {nombre}"})
            if detalle:
                rows.append({"fila_tipo": "detalle", "texto": detalle})
        return rows

    @rx.var
    def ha_soap_html(self) -> list[str]:
        """Campos SOAP con el término de búsqueda resaltado en HTML (<mark>).
        Índices: 0=motivo, 1=revision, 2=subjetivo, 3=objetivo, 4=analisis, 5=plan.
        Si el filtro tiene menos de 3 chars devuelve texto plano."""
        if not self.atencion_seleccionada or len(self.atencion_seleccionada) < 8:
            return ["", "", "", "", "", ""]
        campos = [str(self.atencion_seleccionada[i]) for i in range(2, 8)]
        filtro = self.que_historial_busco.strip().lower()
        if len(filtro) < 3:
            return campos
        style = "background:#F892F6;border-radius:2px;padding:0 1px"
        pattern = re.compile(re.escape(filtro), re.IGNORECASE)
        return [
            pattern.sub(
                lambda m: f'<mark style="{style}">{m.group()}</mark>', c
            )
            for c in campos
        ]

    def set_ha_tab_historia(self, v: str):
        self.ha_tab_historia = v

    def toggle_ha_panel_expandido(self):
        self.ha_panel_expandido = not self.ha_panel_expandido

    def set_ha_sub_tab_pedidos(self, v: str):
        self.ha_sub_tab_pedidos = v

    def nuevo_diagnostico(self):
        print("Nuevo diagnostico")

    def selecciona_paciente(self, nro_hclinica: int):
        for p in self.lista_pacientes:
            if p.get('nro_hclinica') == nro_hclinica:
                datos = [
                    p['nro_hclinica'],
                    p['nombre_completo'],
                    p.get('edad', ''),
                    p.get('fecha_nacimiento', ''),
                    p.get('grupo_sanguineo', ''),
                    p.get('seguro', '')
                ]
                if not self._autoriza_y_selecciona_paciente(datos):
                    yield rx.toast.error("No tiene permiso para acceder a este paciente.")
                break

    def selecciona_diagnostico(self, id_diagnostico: int):
        for d in self.lista_diagnosticos:
            if d.get('id_diagnostico') == id_diagnostico:
                self.diagnostico_seleccionado = [
                    d.get('id_diagnostico', 0),
                    d.get('cie10', ''),
                    d.get('nombre_cie10', ''),
                    d.get('tipo', ''),
                    d.get('fecha_diagnostico', ''),
                    d.get('fecha_inicio_aparente', ''),
                    d.get('observaciones', '')
                ]
                # Limpiar estado del modo "desde atención"
                self.id_atencion_seleccionada = 0
                self.lista_diagnosticos_vinculados = []
                if id_diagnostico != 0:
                    with Session(get_engine()) as session:
                        self.lista_atenciones_vinculadas_a_diagnostico = atenciones_vinculadas_a_diagnostico(session, id_diagnostico)
                    self.filtro_diagnostico_activo = True
                else:
                    self.lista_atenciones_vinculadas_a_diagnostico = []
                    self.filtro_diagnostico_activo = False
                break

    def selecciona_atencion(self, id_atencion: int):
        if self.id_atencion_seleccionada == id_atencion:
            return  # misma fila: mantiene resaltado sin cambios
        # Solo limpiar el filtro de diagnóstico si NO está activo
        if not self.filtro_diagnostico_activo:
            self.diagnostico_seleccionado = []
        # Volver al tab de diagnósticos en el panel izquierdo
        self.tab_izq_activo = "diagnosticos"
        for a in self.lista_atenciones:
            if a.get('id_atencion') == id_atencion:
                self.atencion_seleccionada = [
                    a.get('lk_medico', ''),
                    a.get('fecha_atencion', ''),
                    a.get('motivo_consulta', ''),
                    a.get('revision_sistemas', ''),
                    a.get('subjetivo', ''),
                    a.get('objetivo', ''),
                    a.get('analisis', ''),
                    a.get('plan', ''),
                ]
                self.contenido_derecha = 'historial_atenciones'
                break
        self.id_atencion_seleccionada = id_atencion
        # Cualquier selección en el historial saca del modo edición: el
        # menú "Editar Atención" solo se activa vía el ícono "lápiz".
        yield AtencionState.sale_modo_edicion_si_corresponde
        self.ha_tab_historia = "soap"
        self.ha_panel_expandido = False
        with Session(get_engine()) as session:
            self.lista_diagnosticos_vinculados = diagnosticos_vinculados_a_atencion(session, id_atencion)
            self.ha_sv_lista    = signos_vitales_atencion(session, id_atencion)
            self.ha_diagnosticos = diagnosticos_atencion_detalle(session, id_atencion)
            self.ha_px_items    = listar_prescripcion_atencion(session, id_atencion, self.id_medico)
            cuidados = obtener_prescripcion_cuidados(session, id_atencion)
            self.ha_px_cuidados = cuidados["cuidados_generales"] if cuidados else ""
            self.ha_pedido_examenes = cargar_pedido_atencion(session, id_atencion)
            otros_rows = session.execute(text("""
                SELECT t.examen_tipo, c.examen_alias, c.examen_nombre, p.detalle_pedido
                FROM examen_pedido p
                JOIN examen_catalogo c ON c.id_examen      = p.lk_catalogo
                JOIN examen_tipo     t ON t.id_examen_tipo = c.lk_examen_tipo
                WHERE p.lk_atencion = :lk
                ORDER BY t.examen_tipo, p.id_examen_pedido
            """), {"lk": id_atencion}).all()
            self.ha_otros_examenes = [
                {"tipo": str(r[0]), "alias": str(r[1]), "nombre": str(r[2]), "detalle": str(r[3]) if r[3] else ""}
                for r in otros_rows
            ]
            self.ha_hay_otros_examenes = len(self.ha_otros_examenes) > 0
            lk_pac = self.paciente_seleccionado[0] if self.paciente_seleccionado else -1
            self.ha_hay_certificado = session.exec(
                select(Certificado)
                .join(Atencion, Certificado.lk_atencion == Atencion.id_atencion)
                .where(Atencion.lk_paciente == lk_pac)
            ).first() is not None

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::
#=======================================================
#=======================================================

class AtencionState(State):
    offcanvas_atencion_actual:bool=False
    offcanvas_prescripcion:bool=False
    offcanvas_nuevo_diagnostico:bool=False
    offcanvas_pedido_examenes: bool = False
    offcanvas_resultados_examenes: bool = False
    offcanvas_lab_orl: bool = False
    offcanvas_menu: bool = False
    atencion_iniciada: bool = False

    def toggle_offcanvas_menu(self):
        self.offcanvas_menu = not self.offcanvas_menu

    # ── Solicitar Interconsulta ──────────────────────────────────────────────
    ic_dialog_open: bool = False
    ic_motivo: str = ""
    ic_fecha_expiracion: str = ""
    ic_auxiliar_opciones: list[str] = []
    ic_auxiliar_sel: str = ""
    ic_error: str = ""
    ic_ok: bool = False

    def ic_abrir(self):
        if not self.puede_escribir_paciente_actual:
            return
        if not self.paciente_seleccionado:
            return
        self.ic_motivo = ""
        self.ic_auxiliar_sel = ""
        self.ic_error = ""
        self.ic_ok = False
        self.ic_fecha_expiracion = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        with Session(get_engine()) as session:
            medicos = listar_medicos_para_interconsulta(session, self.id_medico)
        self.ic_auxiliar_opciones = [f"{m['id_medico']} - {m['nombre_medico']}" for m in medicos]
        self.ic_dialog_open = True
        self.offcanvas_menu = False

    def ic_cerrar(self):
        self.ic_dialog_open = False

    def set_ic_dialog_open(self, v: bool):
        self.ic_dialog_open = v

    def set_ic_motivo(self, v: str):
        self.ic_motivo = v

    def set_ic_fecha_expiracion(self, v: str):
        self.ic_fecha_expiracion = v

    def set_ic_auxiliar_sel(self, v: str):
        self.ic_auxiliar_sel = v

    def ic_solicitar(self):
        if not self.puede_escribir_paciente_actual:
            return
        if not self.paciente_seleccionado:
            return
        if not self.ic_motivo.strip():
            self.ic_error = "El motivo es obligatorio."
            return
        if not self.ic_auxiliar_sel:
            self.ic_error = "Seleccione el médico auxiliar."
            return
        try:
            fecha_exp = datetime.strptime(self.ic_fecha_expiracion, "%Y-%m-%d").date()
        except ValueError:
            self.ic_error = "Fecha de finalización inválida."
            return
        id_auxiliar = int(self.ic_auxiliar_sel.split(" - ")[0])
        nro = self.paciente_seleccionado[0]
        with Session(get_engine()) as session:
            crear_solicitud_interconsulta(
                session, nro, self.id_medico, id_auxiliar,
                self.ic_motivo.strip(), fecha_exp,
            )
        self.ic_error = ""
        self.ic_ok = True
        self.ic_dialog_open = False

    def iniciar_nueva_atencion(self):
        if not self.puede_escribir_paciente_actual:
            return
        self.atencion_iniciada = True
        self.show_panel_izq = False

    def reset_atencion_iniciada(self):
        self.atencion_iniciada = False

    def sale_modo_edicion_si_corresponde(self):
        """Si veníamos editando una atención (soap_id_atencion>0), vuelve a
        modo 'Nueva Atención' descartando lo cargado en modo edición."""
        if self.soap_id_atencion:
            self.reinicia_soap()

    def nueva_atencion_desde_historial(self):
        """Botón 'Nueva Atención' sobre tabla_historial_atenciones: fuerza
        la salida del modo edición, quita el resaltado de fila, oculta el
        historial y abre el offcanvas SOAP en modo 'nueva atención'."""
        if not self.puede_escribir_paciente_actual:
            return
        self.sale_modo_edicion_si_corresponde()
        self.id_atencion_seleccionada = 0
        self.atencion_iniciada = True
        self.show_panel_izq = False
        self.offcanvas_atencion_actual = True
        self.offcanvas_prescripcion = False
        self.offcanvas_pedido_examenes = False
        self.offcanvas_resultados_examenes = False

    def editar_atencion_historica(self):
        if not self.puede_escribir_paciente_actual:
            return
        if not self.atencion_seleccionada or len(self.atencion_seleccionada) < 8:
            return
        if self.atencion_seleccionada[0] != self.id_medico:
            return  # solo el autor de la atención puede editarla
        fecha_str = str(self.atencion_seleccionada[1]).split("|")[0].strip()
        if fecha_str != date.today().isoformat():
            return  # solo se puede editar una atención el mismo día
        self.soap_id_atencion = self.id_atencion_seleccionada
        self.soap_motivo    = str(self.atencion_seleccionada[2])
        self.soap_revision  = str(self.atencion_seleccionada[3])
        self.soap_subjetivo = str(self.atencion_seleccionada[4])
        self.soap_objetivo  = str(self.atencion_seleccionada[5])
        self.soap_analisis  = str(self.atencion_seleccionada[6])
        self.soap_plan      = str(self.atencion_seleccionada[7])
        self.soap_snap_motivo    = self.soap_motivo
        self.soap_snap_revision  = self.soap_revision
        self.soap_snap_subjetivo = self.soap_subjetivo
        self.soap_snap_objetivo  = self.soap_objetivo
        self.soap_snap_analisis  = self.soap_analisis
        self.soap_snap_plan      = self.soap_plan
        self.soap_grabado      = True
        self.vd_vinculado      = True
        self.soap_modo_edicion = False
        with Session(get_engine()) as session:
            catalogo = cargar_catalogo_sv(session)
            sv_vals  = cargar_sv_atencion(session, self.soap_id_atencion)
        self.sv_catalogo = [
            {**item, "valor_actual": sv_vals.get(item["id_signo_vital"], "")}
            for item in catalogo
        ]
        self.atencion_iniciada             = True
        self.offcanvas_atencion_actual     = True
        self.offcanvas_prescripcion        = False
        self.offcanvas_pedido_examenes     = False
        self.offcanvas_resultados_examenes = False

    # Pedido de exámenes
    pedido_grabado: bool = False
    pedido_campo_provisional: str = ""

    # Resultados de exámenes
    resultados_grabado: bool = False
    resultados_campo_provisional: str = ""

    # Modo edición SOAP
    soap_modo_edicion:  bool = False
    soap_dialogo_salir: bool = False
    # Snapshot de los valores grabados (para descartar cambios al salir)
    soap_snap_motivo:    str = ""
    soap_snap_revision:  str = ""
    soap_snap_subjetivo: str = ""
    soap_snap_objetivo:  str = ""
    soap_snap_analisis:  str = ""
    soap_snap_plan:      str = ""

    # Signos vitales
    sv_catalogo:        list[dict] = []
    sv_grabado:         bool = False
    sv_otros_dialog_open: bool = False

    @rx.var
    def sv_standard(self) -> list[dict]:
        return [item for item in self.sv_catalogo if item.get("orden_display", 99) <= 9]

    @rx.var
    def sv_otros(self) -> list[dict]:
        return [item for item in self.sv_catalogo if item.get("orden_display", 99) > 9]

    @rx.var
    def sv_hay_otros_tipos(self) -> bool:
        return any(item.get("orden_display", 99) > 9 for item in self.sv_catalogo)

    @rx.var
    def sv_otros_texto(self) -> str:
        partes = [
            f"{item['nombre']}: {item['valor_actual']}"
            for item in self.sv_catalogo
            if item.get("orden_display", 99) > 9 and item.get("valor_actual", "").strip()
        ]
        return "; ".join(partes)

    @rx.var
    def sv_hay_otros_valores(self) -> bool:
        return any(
            item.get("valor_actual", "").strip()
            for item in self.sv_catalogo
            if item.get("orden_display", 99) > 9
        )

    def abrir_sv_otros_dialog(self):
        self.sv_otros_dialog_open = True

    def set_sv_otros_dialog_open(self, v: bool):
        self.sv_otros_dialog_open = v

    @rx.var
    def pedido_deshabilitado(self) -> bool:
        return not self.soap_grabado or self.pedido_grabado

    @rx.var
    def resultados_deshabilitado(self) -> bool:
        return self.resultados_grabado

    # ── URLs para impresión de reportes ──────────────────────────────────────
    @rx.var
    def _url_params_reporte(self) -> str:
        return (f"lk_paciente={self.nro_hclinica_seleccionado}"
                f"&lk_atencion={self.soap_id_atencion}"
                f"&lk_medico={self.id_medico}")

    @rx.var
    def url_reporte_form002(self) -> str:
        return f"{_BACKEND}/reporte/form002?{self._url_params_reporte}"

    @rx.var
    def url_reporte_receta(self) -> str:
        return f"{_BACKEND}/reporte/receta?{self._url_params_reporte}"

    @rx.var
    def url_reporte_pedido_laboratorio(self) -> str:
        return f"{_BACKEND}/reporte/pedido_laboratorio?{self._url_params_reporte}"

    @rx.var
    def url_reporte_pedido_imagen(self) -> str:
        return f"{_BACKEND}/reporte/pedido_imagen?{self._url_params_reporte}"

    @rx.var
    def url_reporte_certificado(self) -> str:
        return f"{_BACKEND}/reporte/certificado?{self._url_params_reporte}"

    @rx.var
    def url_reporte_form001(self) -> str:
        return (f"{_BACKEND}/reporte/form001"
                f"?lk_paciente={self.nro_hclinica_seleccionado}"
                f"&lk_atencion=0&lk_medico={self.id_medico}")
    soap_grabado:bool=False
    soap_actual: dict={}

    # Campos SOAP — todos controlados por estado
    soap_motivo:    str = ""
    soap_revision:  str = ""
    soap_subjetivo: str = ""
    soap_objetivo:  str = ""
    soap_analisis:  str = ""
    soap_plan:      str = ""

    def set_soap_motivo(self, v: str):
        if not self.soap_grabado or self.soap_modo_edicion:
            self.soap_motivo = v

    def set_soap_revision(self, v: str):
        if not self.soap_grabado or self.soap_modo_edicion:
            self.soap_revision = v

    def set_soap_subjetivo(self, v: str):
        if not self.soap_grabado or self.soap_modo_edicion:
            self.soap_subjetivo = v

    def set_soap_objetivo(self, v: str):
        if not self.soap_grabado or self.soap_modo_edicion:
            self.soap_objetivo = v

    def set_soap_analisis(self, v: str):
        if not self.soap_grabado or self.soap_modo_edicion:
            self.soap_analisis = v

    def set_soap_plan(self, v: str):
        if not self.soap_grabado or self.soap_modo_edicion:
            self.soap_plan = v

    @rx.var
    def soap_campos_incompletos(self) -> bool:
        return (
            not self.soap_motivo.strip()
            or not self.soap_subjetivo.strip()
            or not self.soap_plan.strip()
        )

    # id de la atención recién grabada (disponible tras submit_soap)
    soap_id_atencion: int = 0
    soap_error: str = ""  # mensaje cuando actualizar_atencion rechaza la edición (autor/fecha)

    # Vincular Diagnóstico
    vd_dialog_open: bool = False
    vd_lista_diagnosticos: list[dict] = []
    vd_seleccionados: list[int] = []
    vd_error: str = ""
    vd_vinculos_ok: bool = False
    vd_vinculado: bool = False       # True tras grabar rel_atencion_diagnostico
    vd_modo_nuevo_soap: bool = False  # True cuando el dialog abre desde "Grabar SOAP" (primera vez)
    soap_vincular_msg: bool = False   # True cuando el médico cierra vincular sin completar

    @rx.var
    def vd_diagnosticos_con_estado(self) -> list[dict]:
        return [
            {**d, "checked": d["id_diagnostico"] in self.vd_seleccionados}
            for d in self.vd_lista_diagnosticos
        ]

    @rx.var
    def no_puede_grabar_soap(self) -> bool:
        return self.soap_grabado or self.soap_campos_incompletos

    @rx.var
    def soap_no_grabado(self) -> bool:
        return not self.soap_grabado

    @rx.var
    def soap_campos_bloqueados(self) -> bool:
        """Campos del SOAP deshabilitados: grabado pero no en modo edición."""
        return self.soap_grabado and not self.soap_modo_edicion

    @rx.var
    def vincular_visible(self) -> bool:
        """El botón 'Vincular Diagnóstico' solo es visible después de grabar el SOAP."""
        return self.soap_grabado

    @rx.var
    def vincular_deshabilitado(self) -> bool:
        """Cuando visible, el botón siempre está habilitado."""
        return not self.soap_grabado

    @rx.var
    def prescripcion_habilitada(self) -> bool:
        """La prescripción se habilita cuando el SOAP está guardado y hay diagnóstico vinculado."""
        return self.soap_grabado and self.vd_vinculado

    @rx.var
    def prescripcion_deshabilitada(self) -> bool:
        return not self.soap_grabado or not self.vd_vinculado

    def refrescar_lista_vincular(self):
        """Re-consulta los diagnósticos del paciente y actualiza lista_diagnosticos
        y vd_lista_diagnosticos sin tocar el estado del diálogo (abierto/cerrado)."""
        if not self.paciente_seleccionado:
            return
        nro = self.paciente_seleccionado[0]
        with Session(get_engine()) as session:
            rows = historial_diagnosticos(session, nro, self.id_medico)
        self.lista_diagnosticos = rows
        self.vd_lista_diagnosticos = [
            r for r in rows if r.get("tipo") in ("Presuntivo", "Definitivo")
        ]

    def abrir_vincular_diagnostico(self):
        if not self.paciente_seleccionado:
            self.vd_error = "No hay paciente seleccionado."
            self.vd_dialog_open = True
            return
        nro = self.paciente_seleccionado[0]
        with Session(get_engine()) as session:
            rows = historial_diagnosticos(session, nro, self.id_medico)
            # Pre-marca los vínculos existentes cuando el SOAP ya está grabado
            if self.soap_grabado and self.soap_id_atencion:
                self.vd_seleccionados = diagnosticos_vinculados_a_atencion(
                    session, self.soap_id_atencion
                )
            else:
                self.vd_seleccionados = []
        self.lista_diagnosticos = rows
        self.vd_lista_diagnosticos = [
            r for r in rows if r.get("tipo") in ("Presuntivo", "Definitivo")
        ]
        # Solo resetea vd_vinculado si es primera vez (SOAP sin grabar todavía)
        if not self.soap_grabado:
            self.vd_vinculado = False
        self.vd_error = ""
        self.vd_dialog_open = True

    def set_vd_dialog_open(self, v: bool):
        self.vd_dialog_open = v
        if not v and self.vd_modo_nuevo_soap and not self.vd_vinculado:
            # Médico cerró el diálogo sin vincular en el flujo "Grabar SOAP"
            self.soap_vincular_msg = True
            self.vd_modo_nuevo_soap = False

    def toggle_diagnostico(self, id_diagnostico: int, checked: bool):
        if checked:
            if id_diagnostico not in self.vd_seleccionados:
                self.vd_seleccionados = self.vd_seleccionados + [id_diagnostico]
        else:
            self.vd_seleccionados = [i for i in self.vd_seleccionados if i != id_diagnostico]
        self.vd_error = ""

    def confirmar_vinculos(self):
        if not self.puede_escribir_paciente_actual:
            return
        if not self.vd_seleccionados:
            self.vd_error = "Seleccione al menos un diagnóstico."
            return

        if self.vd_modo_nuevo_soap:
            # ── Primera vez: graba SOAP + vincular de forma atómica ────────────
            if not self.paciente_seleccionado:
                self.vd_error = "No hay paciente seleccionado."
                return
            nro = self.paciente_seleccionado[0]
            with Session(get_engine()) as session:
                nueva_atencion = Atencion(
                    lk_paciente=nro,
                    lk_medico=self.id_medico,
                    fecha_atencion=datetime.now(),
                    motivo_consulta=self.soap_motivo,
                    revision_sistemas=self.soap_revision,
                    subjetivo=self.soap_subjetivo,
                    objetivo=self.soap_objetivo,
                    analisis=self.soap_analisis,
                    plan=self.soap_plan,
                )
                session.add(nueva_atencion)
                session.flush()
                self.soap_id_atencion = nueva_atencion.id_atencion
                if es_atencion_bajo_interconsulta(session, nro, self.id_medico):
                    registrar_interconsulta(session, self.soap_id_atencion, self.id_medico)
                guardar_sv_atencion(session, self.soap_id_atencion, self.sv_catalogo)
                for id_diag in self.vd_seleccionados:
                    nodup = f"{str(self.soap_id_atencion).zfill(8)}.{str(id_diag).zfill(8)}"
                    session.add(Rel_atencion_diagnostico(
                        lk_atencion=self.soap_id_atencion,
                        lk_diagnostico=id_diag,
                        noduplicarelacion=nodup,
                    ))
                session.commit()
            self.soap_grabado = True
            self.soap_snap_motivo    = self.soap_motivo
            self.soap_snap_revision  = self.soap_revision
            self.soap_snap_subjetivo = self.soap_subjetivo
            self.soap_snap_objetivo  = self.soap_objetivo
            self.soap_snap_analisis  = self.soap_analisis
            self.soap_snap_plan      = self.soap_plan
            self.vd_vinculado       = True
            self.vd_vinculos_ok     = True
            self.vd_dialog_open     = False
            self.vd_modo_nuevo_soap = False
            self.soap_vincular_msg  = False
            self.lista_diagnosticos_vinculados = list(self.vd_seleccionados)
            with Session(get_engine()) as session:
                self.lista_atenciones = historial_atenciones_con_cie10(session, nro, "", self.id_medico)
            self.que_historial_busco = ""
        else:
            # ── SOAP ya existe: DELETE + INSERT (re-vincular) ─────────────────
            if not self.soap_id_atencion:
                self.vd_error = "Primero grabe el SOAP."
                return
            with Session(get_engine()) as session:
                existentes = session.exec(
                    select(Rel_atencion_diagnostico).where(
                        Rel_atencion_diagnostico.lk_atencion == self.soap_id_atencion
                    )
                ).all()
                for rel in existentes:
                    session.delete(rel)
                session.flush()
                for id_diag in self.vd_seleccionados:
                    nodup = f"{str(self.soap_id_atencion).zfill(8)}.{str(id_diag).zfill(8)}"
                    session.add(Rel_atencion_diagnostico(
                        lk_atencion=self.soap_id_atencion,
                        lk_diagnostico=id_diag,
                        noduplicarelacion=nodup,
                    ))
                session.commit()
            self.vd_dialog_open = False
            self.vd_vinculos_ok  = True
            self.vd_vinculado    = True
            self.lista_diagnosticos_vinculados = list(self.vd_seleccionados)

    def cerrar_vinculos_ok(self):
        self.vd_vinculos_ok = False
        if self.paciente_seleccionado:
            with Session(get_engine()) as session:
                self.lista_atenciones = historial_atenciones_con_cie10(
                    session, self.paciente_seleccionado[0], "", self.id_medico
                )
            self.que_historial_busco = ""
        # No cerrar el offcanvas: el médico continúa con la atención

    def abre_offcanvas_prescripcion(self):
        self.offcanvas_prescripcion = True
        self.offcanvas_atencion_actual = False
        self.offcanvas_nuevo_diagnostico = False
        self.offcanvas_pedido_examenes = False
        self.offcanvas_resultados_examenes = False
        yield PrescripcionState.abrir_prescripcion(self.soap_id_atencion)

    def cierra_offcanvas_prescripcion(self):
        self.offcanvas_prescripcion=False

    def set_sv_valor(self, id_signo: int, valor: str):
        self.sv_catalogo = [
            {**item, "valor_actual": valor} if item["id_signo_vital"] == id_signo else item
            for item in self.sv_catalogo
        ]

    def abre_offcanvas_actual(self):
        if not self.soap_grabado:
            self.reinicia_soap()
        self.offcanvas_atencion_actual = True
        self.offcanvas_prescripcion = False
        self.offcanvas_pedido_examenes = False
        self.offcanvas_resultados_examenes = False
        if not self.sv_catalogo:
            with Session(get_engine()) as session:
                self.sv_catalogo = cargar_catalogo_sv(session)

    def cierra_offcanvas_actual(self):
        self.offcanvas_atencion_actual=False

    def toggle_offcanvas_prescripcion(self):
        self.offcanvas_prescripcion=not self.offcanvas_prescripcion

    def toggle_offcanvas_nuevo_diagnostico(self):
        self.offcanvas_nuevo_diagnostico=not self.offcanvas_nuevo_diagnostico

    def abre_offcanvas_pedido_examenes(self):
        self.offcanvas_pedido_examenes = True
        self.offcanvas_resultados_examenes = False
        self.offcanvas_atencion_actual = False
        self.offcanvas_prescripcion = False
        yield PedidoExamenesState.pe_abrir(self.soap_id_atencion)
        yield OtrosPedidoState.oe_cargar()

    def cierra_offcanvas_pedido_examenes(self):
        self.offcanvas_pedido_examenes = False

    def abre_offcanvas_resultados_examenes(self):
        self.offcanvas_resultados_examenes = True
        self.offcanvas_pedido_examenes = False
        self.offcanvas_atencion_actual = False
        self.offcanvas_prescripcion = False
        self.offcanvas_lab_orl = False
        self.show_panel_izq = False

    def cierra_offcanvas_resultados_examenes(self):
        self.offcanvas_resultados_examenes = False

    def cerrar_lab_orl(self):
        self.offcanvas_lab_orl = False

    def set_pedido_campo_provisional(self, v: str):
        self.pedido_campo_provisional = v

    def grabar_pedido(self):
        self.pedido_grabado = True

    def editar_pedido(self):
        self.pedido_grabado = False

    def set_resultados_campo_provisional(self, v: str):
        self.resultados_campo_provisional = v

    def grabar_resultados(self):
        self.resultados_grabado = True

    def editar_resultados(self):
        self.resultados_grabado = False

    ###### GRABAMOS SOAP ###########
    def reinicia_soap(self):
        self.soap_grabado = False
        self.soap_modo_edicion = False
        self.soap_dialogo_salir = False
        self.soap_id_atencion = 0
        self.soap_motivo = ""
        self.soap_revision = ""
        self.soap_subjetivo = ""
        self.soap_objetivo = ""
        self.soap_analisis = ""
        self.soap_plan = ""
        self.soap_snap_motivo = ""
        self.soap_snap_revision = ""
        self.soap_snap_subjetivo = ""
        self.soap_snap_objetivo = ""
        self.soap_snap_analisis = ""
        self.soap_snap_plan = ""
        self.vd_seleccionados = []
        self.vd_lista_diagnosticos = []
        self.vd_dialog_open = False
        self.vd_vinculos_ok = False
        self.vd_vinculado = False
        self.vd_modo_nuevo_soap = False
        self.soap_vincular_msg = False
        self.pedido_grabado = False
        self.pedido_campo_provisional = ""
        self.resultados_grabado = False
        self.resultados_campo_provisional = ""
        self.offcanvas_atencion_actual = False
        self.offcanvas_prescripcion = False
        self.offcanvas_pedido_examenes = False
        self.offcanvas_resultados_examenes = False
        self.sv_catalogo = []
        self.sv_grabado = False
        self.sv_otros_dialog_open = False

    def submit_soap(self):
        """Vinculación obligatoria: abre el diálogo de vincular diagnóstico.
        El SOAP se graba de forma atómica en confirmar_vinculos cuando vd_modo_nuevo_soap=True."""
        if self.soap_id_atencion:  # guardia contra doble ejecución
            return
        self.vd_modo_nuevo_soap = True
        self.soap_vincular_msg  = False
        self.abrir_vincular_diagnostico()

    def activar_edicion_soap(self):
        self.soap_modo_edicion = True
        self.soap_error = ""

    def guardar_cambios_soap(self):
        if not self.puede_escribir_paciente_actual:
            return
        if not self.soap_id_atencion:
            return
        self.soap_error = ""
        with Session(get_engine()) as session:
            try:
                actualizar_atencion(
                    session,
                    self.soap_id_atencion,
                    self.soap_motivo,
                    self.soap_revision,
                    self.soap_subjetivo,
                    self.soap_objetivo,
                    self.soap_analisis,
                    self.soap_plan,
                    self.id_medico,
                )
            except ValueError as e:
                self.soap_error = str(e)
                return
            guardar_sv_atencion(session, self.soap_id_atencion, self.sv_catalogo)
        self.soap_modo_edicion = False
        # Actualiza snapshot con los nuevos valores guardados
        self.soap_snap_motivo    = self.soap_motivo
        self.soap_snap_revision  = self.soap_revision
        self.soap_snap_subjetivo = self.soap_subjetivo
        self.soap_snap_objetivo  = self.soap_objetivo
        self.soap_snap_analisis  = self.soap_analisis
        self.soap_snap_plan      = self.soap_plan
        if self.paciente_seleccionado:
            nro = self.paciente_seleccionado[0]
            with Session(get_engine()) as session:
                self.lista_atenciones = historial_atenciones_con_cie10(session, nro, "", self.id_medico)
            self.que_historial_busco = ""

    def set_soap_dialogo_salir(self, v: bool):
        self.soap_dialogo_salir = v

    def logout_con_advertencia(self):
        """Intercepta el 'Salir' para advertir si hay cambios sin guardar."""
        if self.soap_modo_edicion:
            self.soap_dialogo_salir = True
        else:
            self.diagnostico_seleccionado = []
            self.reinicia_soap()
            self.atencion_iniciada = False
            yield rx.redirect("/pacientes")

    def confirmar_salir(self):
        """El médico confirma salir descartando los cambios de edición."""
        # Restaura desde snapshot
        self.soap_motivo    = self.soap_snap_motivo
        self.soap_revision  = self.soap_snap_revision
        self.soap_subjetivo = self.soap_snap_subjetivo
        self.soap_objetivo  = self.soap_snap_objetivo
        self.soap_analisis  = self.soap_snap_analisis
        self.soap_plan      = self.soap_snap_plan
        self.soap_modo_edicion  = False
        self.soap_dialogo_salir = False
        self.diagnostico_seleccionado = []
        self.reinicia_soap()
        yield rx.redirect("/pacientes")

class PacienteState(State):
    """Estado del formulario de nuevo paciente."""
 
    dialog_open: bool = False
 
    # Campos del formulario
    nombre_completo: str = ""
    sexo: str = ""
    fecha_nacimiento: str = ""
    cedula_id: str = ""
    pais_nacimiento: str = ""
    ciudad_reside: str = ""
    direccion_reside: str = ""
    tf_celular: str = ""
    email: str = ""
    observacion: str = ""
    seguro: str = ""
    grupo_sanguineo: str = ""
    estado_civil: str = ""
 
    lista_seguros: list[str] = []

    error_msg: str = ""
    success_msg: str = ""
    show_confirmacion: bool = False

    def set_show_confirmacion(self, v: bool): self.show_confirmacion = v

    def set_nombre_completo(self, value: str):
        self.nombre_completo = value.upper()

    def set_cedula_id(self, value: str): self.cedula_id = value
    def set_sexo(self, value: str): self.sexo = value
    def set_fecha_nacimiento(self, value: str): self.fecha_nacimiento = value
    def set_pais_nacimiento(self, value: str): self.pais_nacimiento = value
    def set_estado_civil(self, value: str): self.estado_civil = value
    def set_grupo_sanguineo(self, value: str): self.grupo_sanguineo = value
    def set_seguro(self, value: str): self.seguro = value
    def set_ciudad_reside(self, value: str): self.ciudad_reside = value
    def set_tf_celular(self, value: str): self.tf_celular = value
    def set_direccion_reside(self, value: str): self.direccion_reside = value
    def set_email(self, value: str): self.email = value
    def set_observacion(self, value: str): self.observacion = value
    def set_dialog_open(self, value: bool): self.dialog_open = value

    def open_dialog(self):
        self.dialog_open = True
        self.error_msg = ""
        self.success_msg = ""
        self.lista_seguros = carga_seguros()
 
    def close_dialog(self):
        self.dialog_open = False
        self._reset_form()
 
    def _reset_form(self):
        self.nombre_completo = ""
        self.sexo = ""
        self.fecha_nacimiento = ""
        self.cedula_id = ""
        self.pais_nacimiento = ""
        self.ciudad_reside = ""
        self.direccion_reside = ""
        self.tf_celular = ""
        self.email = ""
        self.observacion = ""
        self.seguro = ""
        self.grupo_sanguineo = ""
        self.estado_civil = ""
        self.error_msg = ""
        self.success_msg = ""
 
    def guardar_paciente(self):
        print(">>> guardar_paciente invocado")  # confirma que se llama
        
        campos_req = {
            "Nombre completo": self.nombre_completo,
            "Cédula / ID": self.cedula_id,
            "Sexo": self.sexo,
            "Fecha de nacimiento": self.fecha_nacimiento,
            "País de nacimiento": self.pais_nacimiento,
            "Estado civil": self.estado_civil,
            "Grupo sanguíneo": self.grupo_sanguineo,
            "Seguro": self.seguro,
            "Ciudad de residencia": self.ciudad_reside,
            "Dirección de residencia": self.direccion_reside,
            "Teléfono celular": self.tf_celular,
            "Correo electrónico": self.email,
        }
        vacios = [k for k, v in campos_req.items() if not v.strip()]
        if vacios:
            self.error_msg = f"Complete: {', '.join(vacios)}."
            return

        try:
            # ✅ "date" ya está importado directamente, no "datetime.date"
            fecha = date.fromisoformat(self.fecha_nacimiento)
        except ValueError:
            self.error_msg = "Formato de fecha inválido."
            return

        try:
            # ✅ Usa el mismo engine que el resto de tu app
            _crypto = GesmedCrypto.para_medico(self.id_medico)
            with Session(get_engine()) as session:
                nuevo = Paciente(
                    nombre_completo=_crypto.encriptar(self.nombre_completo.strip()),
                    sexo=self.sexo,
                    fecha_nacimiento=fecha,
                    cedula_id=_crypto.encriptar(self.cedula_id.strip()) if self.cedula_id.strip() else None,
                    pais_nacimiento=self.pais_nacimiento.strip() or None,
                    ciudad_reside=self.ciudad_reside.strip(),
                    direccion_reside=_crypto.encriptar(self.direccion_reside.strip()),
                    tf_celular=_crypto.encriptar(self.tf_celular.strip()),
                    email=_crypto.encriptar(self.email.strip()) if self.email.strip() else None,
                    observacion=_crypto.encriptar(self.observacion.strip()) if self.observacion.strip() else None,
                    seguro=self.seguro.strip(),
                    grupo_sanguineo=self.grupo_sanguineo,
                    estado_civil=self.estado_civil,
                    fecha_creacion=datetime.now(),  # ✅ datetime ya importado directo
                    es_activo=1,
                )
                session.add(nuevo)
                session.commit()
                print(">>> Paciente guardado OK")

            self.error_msg = ""
            self._reset_form()
            self.dialog_open = False
            self.show_confirmacion = True

        except Exception as e:
            # ✅ Muestra el error real en pantalla y consola
            self.error_msg = f"Error al guardar: {str(e)}"
            print(f">>> ERROR guardar_paciente: {e}")


class EditPacienteState(State):
    dialog_editar_open: bool = False
    ep_modo_edicion: bool = False
    campos_editados: bool = False
    ep_nombre_completo: str = ""
    ep_cedula_id: str = ""
    ep_sexo: str = ""
    ep_grupo_sanguineo: str = ""
    ep_fecha_nacimiento: str = ""
    ep_pais_nacimiento: str = ""
    ep_estado_civil: str = ""
    ep_ciudad_reside: str = ""
    ep_direccion_reside: str = ""
    ep_tf_celular: str = ""
    ep_email: str = ""
    ep_seguro: str = ""
    ep_observacion: str = ""
    ep_lista_seguros: list[str] = []
    ep_error: str = ""
    ep_success: str = ""

    def abrir_datos_paciente(self):
        if not self.paciente_seleccionado or not self.hay_paciente_seleccionado:
            return
        nro = self.paciente_seleccionado[0]
        _crypto = GesmedCrypto.para_medico(self.id_medico)
        with Session(get_engine()) as session:
            paciente = session.get(Paciente, nro)
            print(f"🟦 paciente: {paciente}")
            if paciente:
                self.ep_nombre_completo = _crypto.desencriptar(paciente.nombre_completo) if paciente.nombre_completo else ""
                self.ep_cedula_id = _crypto.desencriptar(paciente.cedula_id) if paciente.cedula_id else ""
                self.ep_sexo = paciente.sexo or ""
                self.ep_grupo_sanguineo = paciente.grupo_sanguineo or ""
                self.ep_fecha_nacimiento = str(paciente.fecha_nacimiento) if paciente.fecha_nacimiento else ""
                self.ep_pais_nacimiento = paciente.pais_nacimiento or ""
                self.ep_estado_civil = paciente.estado_civil or ""
                self.ep_ciudad_reside = paciente.ciudad_reside or ""
                self.ep_direccion_reside = _crypto.desencriptar(paciente.direccion_reside)
                self.ep_tf_celular = _crypto.desencriptar(paciente.tf_celular)
                self.ep_email = _crypto.desencriptar(paciente.email)
                self.ep_seguro = paciente.seguro or ""
                self.ep_observacion = _crypto.desencriptar(paciente.observacion)
        self.ep_lista_seguros = carga_seguros()
        self.campos_editados = False
        self.ep_modo_edicion = False
        self.ep_error = ""
        self.ep_success = ""
        self.dialog_editar_open = True

    def set_dialog_editar_open(self, v: bool):
        self.dialog_editar_open = v
        if not v:
            self.ep_modo_edicion = False

    def set_ep_modo_edicion(self, v: bool):
        self.ep_modo_edicion = v
        if v:
            self.ep_success = ""

    @rx.var
    def ep_modo_lectura(self) -> bool:
        return not self.ep_modo_edicion

    @rx.var
    def ep_puede_grabar(self) -> bool:
        return (
            self.campos_editados
            and bool(self.ep_nombre_completo.strip())
            and bool(self.ep_cedula_id.strip())
            and bool(self.ep_sexo)
            and bool(self.ep_fecha_nacimiento)
            and bool(self.ep_pais_nacimiento.strip())
            and bool(self.ep_estado_civil)
            and bool(self.ep_grupo_sanguineo)
            and bool(self.ep_seguro)
            and bool(self.ep_ciudad_reside.strip())
            and bool(self.ep_direccion_reside.strip())
            and bool(self.ep_tf_celular.strip())
            and bool(self.ep_email.strip())
        )

    def set_ep_nombre_completo(self, v: str): self.ep_nombre_completo = v.upper(); self.campos_editados = True
    def set_ep_cedula_id(self, v: str): self.ep_cedula_id = v; self.campos_editados = True
    def set_ep_sexo(self, v: str): self.ep_sexo = v; self.campos_editados = True
    def set_ep_grupo_sanguineo(self, v: str): self.ep_grupo_sanguineo = v; self.campos_editados = True
    def set_ep_fecha_nacimiento(self, v: str): self.ep_fecha_nacimiento = v; self.campos_editados = True
    def set_ep_pais_nacimiento(self, v: str): self.ep_pais_nacimiento = v; self.campos_editados = True
    def set_ep_estado_civil(self, v: str): self.ep_estado_civil = v; self.campos_editados = True
    def set_ep_ciudad_reside(self, v: str): self.ep_ciudad_reside = v; self.campos_editados = True
    def set_ep_direccion_reside(self, v: str): self.ep_direccion_reside = v; self.campos_editados = True
    def set_ep_tf_celular(self, v: str): self.ep_tf_celular = v; self.campos_editados = True
    def set_ep_email(self, v: str): self.ep_email = v; self.campos_editados = True
    def set_ep_seguro(self, v: str): self.ep_seguro = v; self.campos_editados = True
    def set_ep_observacion(self, v: str): self.ep_observacion = v; self.campos_editados = True

    def guardar_cambios_paciente(self):
        try:
            fecha = date.fromisoformat(self.ep_fecha_nacimiento)
        except ValueError:
            self.ep_error = "Formato de fecha inválido (YYYY-MM-DD)."
            return
        nro = self.paciente_seleccionado[0]
        _crypto = GesmedCrypto.para_medico(self.id_medico)
        try:
            with Session(get_engine()) as session:
                paciente = session.get(Paciente, nro)
                if paciente:
                    paciente.nombre_completo = _crypto.encriptar(self.ep_nombre_completo.strip())
                    paciente.cedula_id = _crypto.encriptar(self.ep_cedula_id.strip()) if self.ep_cedula_id.strip() else None
                    paciente.sexo = self.ep_sexo
                    paciente.grupo_sanguineo = self.ep_grupo_sanguineo
                    paciente.fecha_nacimiento = fecha
                    paciente.pais_nacimiento = self.ep_pais_nacimiento.strip() or None
                    paciente.estado_civil = self.ep_estado_civil
                    paciente.ciudad_reside = self.ep_ciudad_reside.strip()
                    paciente.direccion_reside = _crypto.encriptar(self.ep_direccion_reside.strip())
                    paciente.tf_celular = _crypto.encriptar(self.ep_tf_celular.strip())
                    paciente.email = _crypto.encriptar(self.ep_email.strip()) if self.ep_email.strip() else None
                    paciente.seguro = self.ep_seguro.strip()
                    paciente.observacion = _crypto.encriptar(self.ep_observacion.strip()) if self.ep_observacion.strip() else None
                    session.commit()
            self.campos_editados = False
            self.ep_modo_edicion = False
            self.ep_error = ""
            self.ep_success = "Datos del paciente actualizados."
            self.carga_pacientes_filtrados()
        except Exception as e:
            self.ep_error = f"Error al guardar: {str(e)}"


class NuevoDiagnosticoState(State):
    nd_dialog_open: bool = False
    nd_cie10: str = ""
    nd_nombre_cie10: str = ""
    nd_busqueda_cie10: str = ""
    nd_resultados_cie10: list[dict] = []
    nd_tipo: str = ""
    nd_tipo_fijo: bool = False
    nd_fecha_diagnostico: str = ""
    nd_fecha_inicio_aparente: str = ""
    nd_edad_anios: int = 0
    nd_edad_meses: int = 0
    nd_observaciones: str = ""
    nd_error: str = ""

    def _nd_cargar_iniciales(self) -> list[dict]:
        """Primeros 100 registros CIE10 ordenados por código (carga inicial y tras selección)."""
        with Session(get_engine()) as session:
            rows = session.exec(
                select(Cie10).order_by(Cie10.cod_cie10).limit(100)
            ).all()
        return [
            {"cod_cie10": r.cod_cie10, "categoria": r.categoria, "nomdiagnostico": r.nomdiagnostico}
            for r in rows
        ]

    def abrir_nuevo_diagnostico(self):
        self.nd_cie10 = ""
        self.nd_nombre_cie10 = ""
        self.nd_busqueda_cie10 = ""
        self.nd_tipo = ""
        self.nd_tipo_fijo = False
        self.nd_fecha_diagnostico = str(date.today())
        self.nd_fecha_inicio_aparente = str(date.today())
        self.nd_edad_anios = 0
        self.nd_edad_meses = 0
        self.nd_observaciones = ""
        self.nd_error = ""
        self.nd_resultados_cie10 = self._nd_cargar_iniciales()
        self.nd_dialog_open = True

    def abrir_nuevo_ant_personal(self):
        self.abrir_nuevo_diagnostico()
        self.nd_tipo = "Ant.Personal"
        self.nd_tipo_fijo = True

    def set_nd_dialog_open(self, v: bool): self.nd_dialog_open = v
    def set_nd_tipo(self, v: str): self.nd_tipo = v
    def set_nd_fecha_diagnostico(self, v: str): self.nd_fecha_diagnostico = v
    def set_nd_fecha_inicio_aparente(self, v: str): self.nd_fecha_inicio_aparente = v
    def set_nd_observaciones(self, v: str): self.nd_observaciones = v

    def set_nd_edad_anios(self, v: str):
        import calendar as _cal
        try:
            self.nd_edad_anios = max(0, int(v) if v else 0)
        except ValueError:
            return
        self._nd_recalcular_fecha_inicio(_cal)

    def set_nd_edad_meses(self, v: str):
        import calendar as _cal
        try:
            self.nd_edad_meses = max(0, min(11, int(v) if v else 0))
        except ValueError:
            return
        self._nd_recalcular_fecha_inicio(_cal)

    def _nd_recalcular_fecha_inicio(self, _cal=None):
        if not self.paciente_seleccionado or len(self.paciente_seleccionado) < 4:
            return
        if _cal is None:
            import calendar as _cal
        fn = self.paciente_seleccionado[3]
        try:
            fn_str = str(fn)[:10]
            fecha_nac = date.fromisoformat(fn_str)
            total_meses = fecha_nac.month + self.nd_edad_meses + self.nd_edad_anios * 12
            year = fecha_nac.year + (total_meses - 1) // 12
            month = ((total_meses - 1) % 12) + 1
            max_day = _cal.monthrange(year, month)[1]
            day = min(fecha_nac.day, max_day)
            self.nd_fecha_inicio_aparente = str(date(year, month, day))
        except Exception:
            pass

    def set_nd_busqueda_cie10(self, v: str):
        self.nd_busqueda_cie10 = v
        self.nd_cie10 = ""
        self.nd_nombre_cie10 = ""
        if len(v.strip()) >= 3:
            with Session(get_engine()) as session:
                filtro = f"%{v.strip()}%"
                stmt = (
                    select(Cie10)
                    .where(
                        Cie10.nomdiagnostico.like(filtro) |
                        Cie10.cod_cie10.like(filtro)
                    )
                    .limit(30)
                )
                rows = session.exec(stmt).all()
                self.nd_resultados_cie10 = [
                    {"cod_cie10": r.cod_cie10, "categoria": r.categoria, "nomdiagnostico": r.nomdiagnostico}
                    for r in rows
                ]
        else:
            self.nd_resultados_cie10 = self._nd_cargar_iniciales()

    def selecciona_cie10(self, codigo: str):
        for r in self.nd_resultados_cie10:
            if r.get("cod_cie10") == codigo:
                self.nd_nombre_cie10 = r.get("nomdiagnostico", "")
                break
        self.nd_cie10 = codigo
        self.nd_resultados_cie10 = self._nd_cargar_iniciales()
        self.nd_busqueda_cie10 = ""
        self.nd_error = ""

    def guardar_diagnostico(self):
        if not self.puede_escribir_paciente_actual:
            return
        if not self.nd_cie10.strip():
            self.nd_error = "Seleccione un diagnóstico CIE10 de la tabla de búsqueda."
            return
        if not self.nd_tipo:
            self.nd_error = "Seleccione el tipo de diagnóstico."
            return
        if not self.nd_fecha_diagnostico:
            self.nd_error = "Ingrese la fecha de diagnóstico."
            return
        if not self.nd_fecha_inicio_aparente:
            self.nd_error = "Ingrese la fecha de inicio aparente."
            return
        if not self.paciente_seleccionado:
            self.nd_error = "No hay paciente seleccionado."
            return
        try:
            fecha_diag = date.fromisoformat(self.nd_fecha_diagnostico)
            fecha_inicio = date.fromisoformat(self.nd_fecha_inicio_aparente)
        except ValueError:
            self.nd_error = "Formato de fecha inválido (YYYY-MM-DD)."
            return
        nro = self.paciente_seleccionado[0]
        nodup = f"{nro}_{self.nd_cie10.strip()}_{self.nd_fecha_diagnostico}"
        _crypto = GesmedCrypto.para_medico(self.id_medico)
        try:
            with Session(get_engine()) as session:
                nuevo = Diagnostico(
                    lk_paciente=nro,
                    lk_cie10=self.nd_cie10.strip(),
                    tipo=self.nd_tipo,
                    fecha_diagnostico=fecha_diag,
                    fecha_inicio_aparente=fecha_inicio,
                    lk_medico=self.id_medico or None,
                    observaciones=_crypto.encriptar(self.nd_observaciones.strip()) if self.nd_observaciones.strip() else None,
                    noduplicados=nodup,
                )
                session.add(nuevo)
                session.commit()
            self.nd_dialog_open = False
            self.nd_error = ""
        except Exception as e:
            self.nd_error = f"Error al guardar: {str(e)}"
            return
        # Delegar el refresco a AtencionState (substate hermano — no se puede
        # escribir en sus vars via self; hay que usar yield)
        yield AtencionState.refrescar_lista_vincular


# ══════════════════════════════════════════════════════════════════════════════
class PrescripcionState(State):
    """
    Gestiona la pantalla de prescripción de medicamentos.

    Activación:
        abrir_prescripcion(id_atencion) — llamar con soap_id_atencion (atención
        actual) o id_atencion_seleccionada (atención histórica).
        Solo opera si id_atencion > 0.

    Flujo de agregar un ítem:
        1. Buscar en catálogo → seleccionar_medicamento()
        2. Completar formulario (concentración, cantidad, presentación, indicaciones)
        3. agregar_item() → INSERT encriptado → recarga lista
    """

    # ── Visibilidad ───────────────────────────────────────────────────────────
    px_activo: bool = False

    # ── Modo de la pantalla: "edicion" (misma fecha) | "lectura" (histórico) ──
    px_modo: str = "edicion"

    # ── Atención en curso ─────────────────────────────────────────────────────
    px_id_atencion: int = 0

    # ── Datos cargados ────────────────────────────────────────────────────────
    px_lista_items:         list[dict] = []
    px_lista_alergias:      list[dict] = []
    px_lista_medicamentos:  list[dict] = []
    px_lista_presentaciones: list[dict] = []
    px_cuidados_generales:  str = ""

    # ── Búsqueda en catálogo ──────────────────────────────────────────────────
    px_filtro_med:  str = ""
    px_filtro_tipo: int = 0          # 0=todos  1=catálogo  2=añadido

    # ── Medicamento seleccionado del catálogo ─────────────────────────────────
    px_med_cod:    int = 0
    px_med_nombre: str = ""

    # ── Formulario nuevo ítem ─────────────────────────────────────────────────
    px_concentracion:    str = ""
    px_cantidad:         int = 1
    px_lk_presentacion:  int = 0
    px_indicaciones:     str = ""
    px_form_error:       str = ""

    # ── Diálogo editar ítem existente ────────────────────────────────────────
    px_dlg_editar:           bool = False
    px_edit_id:              int  = 0
    px_edit_med_nombre:      str  = ""
    px_edit_concentracion:   str  = ""
    px_edit_cantidad:        int  = 1
    px_edit_lk_presentacion: int  = 0
    px_edit_indicaciones:    str  = ""
    px_edit_error:           str  = ""

    # ── Diálogo "nuevo medicamento al catálogo" ───────────────────────────────
    px_dlg_nuevo_med:       bool = False
    px_nuevo_gen_nombre:    str = ""
    px_nuevo_gen_comercial: str = ""
    px_nuevo_gen_error:     str = ""

    # ── Mensajes de estado ────────────────────────────────────────────────────
    px_guardado_ok: bool = False
    px_error:       str = ""

    # ── Estado de grabado del formulario de prescripción ─────────────────────
    px_grabada:   bool = False   # True tras "Grabar Prescripción"
    px_editando:  bool = False   # True mientras se edita una prescripción ya grabada

    # ── Historial de prescripciones (tab_historial_prescripciones) ────────────
    hp_lista:      list[dict] = []
    hp_filtro:     str = ""
    hp_orden_col:  str = "fecha_atencion"
    hp_orden_asc:  bool = False   # desc por defecto (más reciente primero)

    # ── Fila seleccionada en tabla_historial_prescripciones → panel_derecha ──
    hp_id_atencion_sel:  int        = 0
    hp_sel_fecha:        str        = ""
    hp_sel_edad:         str        = ""
    hp_sel_motivo:       str        = ""
    hp_sel_diagnosticos: list[dict] = []
    hp_sel_items:        list[dict] = []
    hp_sel_cuidados:     str        = ""

    # ── Computed vars ─────────────────────────────────────────────────────────

    @rx.var
    def px_campos_bloqueados(self) -> bool:
        """Formulario bloqueado: grabado pero no en modo edición activo."""
        return self.px_grabada and not self.px_editando

    @rx.var
    def px_puede_modificar(self) -> bool:
        """True cuando el formulario está en modo edición (histórico o no bloqueado)."""
        return self.px_es_editable and not self.px_campos_bloqueados

    @rx.var
    def px_no_puede_modificar(self) -> bool:
        return not self.px_puede_modificar

    @rx.var
    def tab_label_prescripciones(self) -> str:
        return f"Prescripciones ({len(self.hp_lista)})"

    @rx.var
    def hp_lista_filtrada(self) -> list[dict]:
        rows = self.hp_lista
        filtro = self.hp_filtro.strip().lower()
        if filtro:
            rows = [r for r in rows if filtro in r.get("nombre_generico", "").lower()]
        asc_order = self.hp_orden_asc
        if self.hp_orden_col == "nombre_generico":
            rows = sorted(rows, key=lambda r: r.get("nombre_generico", "").lower(), reverse=not asc_order)
        else:
            rows = sorted(rows, key=lambda r: r.get("fecha_atencion", ""), reverse=not asc_order)

        # Zebra por día cuando se ordena por fecha_atencion (0=oscuro, 1=claro, -1=sin zebra)
        if self.hp_orden_col == "fecha_atencion":
            last_date = ""
            zebra = 0
            result = []
            for r in rows:
                day = r.get("fecha_atencion", "")[:10]  # YYYY-MM-DD
                if day != last_date:
                    if last_date:
                        zebra = 1 - zebra
                    last_date = day
                result.append({**r, "zebra": zebra})
            return result
        else:
            return [{**r, "zebra": -1} for r in rows]

    @rx.var
    def hp_hay_sel(self) -> bool:
        return self.hp_id_atencion_sel > 0

    @rx.var
    def hp_hay_sel_cuidados(self) -> bool:
        return bool(self.hp_sel_cuidados.strip())

    @rx.var
    def px_puede_agregar(self) -> bool:
        """True cuando el formulario de nuevo ítem está completo."""
        return (
            self.px_med_cod > 0
            and bool(self.px_concentracion.strip())
            and self.px_cantidad > 0
            and bool(self.px_indicaciones.strip())
        )

    @rx.var
    def px_tiene_items(self) -> bool:
        return len(self.px_lista_items) > 0

    @rx.var
    def px_nombre_presentacion_sel(self) -> str:
        """Nombre de la presentación seleccionada en el dropdown."""
        for p in self.px_lista_presentaciones:
            if p["id_presentacion"] == self.px_lk_presentacion:
                return p["nombre_presentacion"]
        return ""

    @rx.var
    def px_es_editable(self) -> bool:
        return self.px_modo == "edicion"

    @rx.var
    def px_presentaciones_select(self) -> list[str]:
        return [p["nombre_presentacion"] for p in self.px_lista_presentaciones]

    @rx.var
    def px_filtro_tipo_nombre(self) -> str:
        m = {0: "Todos", 1: "Catálogo Base", 2: "Añadidos en consulta",3:"Accesorios y Equipos"}
        return m.get(self.px_filtro_tipo, "Todos")

    @rx.var
    def px_nombre_presentacion_edit(self) -> str:
        """Nombre de la presentación en el diálogo de edición."""
        for p in self.px_lista_presentaciones:
            if p["id_presentacion"] == self.px_edit_lk_presentacion:
                return p["nombre_presentacion"]
        return ""

    # ── Apertura / cierre ─────────────────────────────────────────────────────

    def abrir_prescripcion(self, id_atencion: int):
        if not id_atencion:
            return
        if id_atencion != self.px_id_atencion:
            # Nueva prescripción: resetea el estado de grabado
            self.px_grabada  = False
            self.px_editando = False
        self.px_id_atencion = id_atencion
        self._reset_form()
        with Session(get_engine()) as session:
            self.px_lista_items         = listar_prescripcion_atencion(session, id_atencion, self.id_medico)
            self.px_lista_presentaciones = listar_presentaciones(session)
            self.px_lista_medicamentos  = buscar_medicamentos(session)
            if self.paciente_seleccionado:
                self.px_lista_alergias = listar_alergias_paciente(session, self.paciente_seleccionado[0])
            cuidados = obtener_prescripcion_cuidados(session, id_atencion)
            self.px_cuidados_generales = cuidados["cuidados_generales"] if cuidados else ""
        self.px_activo  = True
        self.px_error   = ""

    def cerrar_prescripcion(self):
        self.px_activo      = False
        self.px_id_atencion = 0
        self._reset_form()

    def reinicia_prescripcion(self):
        self.px_activo              = False
        self.px_modo                = "edicion"
        self.px_id_atencion         = 0
        self.px_lista_items         = []
        self.px_lista_alergias      = []
        self.px_lista_medicamentos  = []
        self.px_lista_presentaciones = []
        self.px_cuidados_generales  = ""
        self.px_guardado_ok         = False
        self.px_error               = ""
        self.hp_lista               = []
        self.hp_filtro              = ""
        self.hp_orden_col           = "fecha_atencion"
        self.hp_orden_asc           = False
        self.hp_id_atencion_sel      = 0
        self.hp_sel_fecha            = ""
        self.hp_sel_edad             = ""
        self.hp_sel_motivo           = ""
        self.hp_sel_diagnosticos     = []
        self.hp_sel_items            = []
        self.hp_sel_cuidados         = ""
        self._reset_form()

    def abrir_prescripcion_historica(self):
        """Carga la prescripción de la atención histórica seleccionada en modo lectura.

        Determina el modo según si la fecha de la atención coincide con hoy:
        - Mismo día → "edicion"  (el médico aún puede modificar)
        - Día anterior → "lectura" (solo consulta)
        También expande panel_derecha al 60% y muestra la sección.
        """
        id_atencion = self.id_atencion_seleccionada
        if not id_atencion:
            return
        # atencion_seleccionada[1] tiene formato "YYYY-MM-DD HH:MM | Xm Yd"
        es_hoy = False
        if self.atencion_seleccionada:
            try:
                fecha_str = str(self.atencion_seleccionada[1]).split("|")[0].strip()
                # soporta "YYYY-MM-DD HH:MM:SS" y "YYYY-MM-DD HH:MM"
                fecha_at = datetime.strptime(fecha_str[:10], "%Y-%m-%d").date()
                es_hoy = (fecha_at == date.today())
            except Exception:
                es_hoy = False
        self.px_modo       = "edicion" if es_hoy else "lectura"
        self.px_id_atencion = id_atencion
        self._reset_form()
        with Session(get_engine()) as session:
            self.px_lista_items          = listar_prescripcion_atencion(session, id_atencion, self.id_medico)
            self.px_lista_presentaciones = listar_presentaciones(session)
            self.px_lista_medicamentos   = buscar_medicamentos(session)
            if self.paciente_seleccionado:
                self.px_lista_alergias = listar_alergias_paciente(session, self.paciente_seleccionado[0])
            cuidados = obtener_prescripcion_cuidados(session, id_atencion)
            self.px_cuidados_generales = cuidados["cuidados_generales"] if cuidados else ""
        self.px_activo          = True
        self.px_error           = ""
        self.contenido_derecha  = "prescripcion_historica"

    # ── Búsqueda en catálogo ──────────────────────────────────────────────────

    def set_px_filtro_med(self, v: str):
        self.px_filtro_med = v
        self.px_med_cod    = 0
        self.px_med_nombre = ""
        tipo = self.px_filtro_tipo if self.px_filtro_tipo > 0 else None
        with Session(get_engine()) as session:
            self.px_lista_medicamentos = buscar_medicamentos(session, v, tipo)

    def set_px_filtro_tipo(self, v: str):
        self.px_filtro_tipo = int(v)
        tipo = int(v) if int(v) > 0 else None
        with Session(get_engine()) as session:
            self.px_lista_medicamentos = buscar_medicamentos(session, self.px_filtro_med, tipo)

    def set_px_filtro_tipo_nombre(self, v: str):
        m = {"Todos": 0, "Catálogo Base": 1, "Añadidos en consulta": 2,"Accesorios y Equipos":3}
        self.px_filtro_tipo = m.get(v, 0)
        tipo = self.px_filtro_tipo if self.px_filtro_tipo > 0 else None
        with Session(get_engine()) as session:
            self.px_lista_medicamentos = buscar_medicamentos(session, self.px_filtro_med, tipo)

    def seleccionar_medicamento(self, cod_gen: int, nombre: str):
        self.px_med_cod    = cod_gen
        self.px_med_nombre = nombre
        self.px_filtro_med = ""
        self.px_form_error = ""

    def deseleccionar_medicamento(self):
        self.px_med_cod    = 0
        self.px_med_nombre = ""
        self.px_filtro_med = ""
        self.px_form_error = ""

    def set_px_lk_presentacion_por_nombre(self, nombre: str):
        for p in self.px_lista_presentaciones:
            if p["nombre_presentacion"] == nombre:
                self.px_lk_presentacion = p["id_presentacion"]
                return
        self.px_lk_presentacion = 0

    def set_px_edit_lk_presentacion_por_nombre(self, nombre: str):
        for p in self.px_lista_presentaciones:
            if p["nombre_presentacion"] == nombre:
                self.px_edit_lk_presentacion = p["id_presentacion"]
                return
        self.px_edit_lk_presentacion = 0

    # ── Formulario nuevo ítem ─────────────────────────────────────────────────

    def set_px_concentracion(self, v: str):   self.px_concentracion   = v; self.px_form_error = ""
    def set_px_cantidad(self, v: str):        self.px_cantidad        = max(1, int(v or 1))
    def set_px_lk_presentacion(self, v: str): self.px_lk_presentacion = int(v or 0)
    def set_px_indicaciones(self, v: str):    self.px_indicaciones    = v; self.px_form_error = ""

    def agregar_item(self):
        """Valida, encripta y guarda un ítem de prescripción."""
        if not self.puede_escribir_paciente_actual:
            return
        if not self.px_puede_agregar:
            self.px_form_error = "Complete medicamento, concentración, cantidad e indicaciones."
            return
        if not self.px_id_atencion or not self.paciente_seleccionado:
            self.px_form_error = "No hay atención activa."
            return
        try:
            with Session(get_engine()) as session:
                guardar_item_prescripcion(
                    session=session,
                    lk_paciente=self.paciente_seleccionado[0],
                    lk_atencion=self.px_id_atencion,
                    lk_generico=self.px_med_cod,
                    concentracion=self.px_concentracion,
                    cantidad=self.px_cantidad,
                    lk_presentacion=self.px_lk_presentacion if self.px_lk_presentacion > 0 else None,
                    indicaciones=self.px_indicaciones,
                    medico_id=self.id_medico,
                )
                self.px_lista_items = listar_prescripcion_atencion(
                    session, self.px_id_atencion, self.id_medico
                )
            self._reset_form()
        except Exception as e:
            self.px_form_error = f"Error al guardar: {str(e)}"

    def eliminar_item(self, id_prescripcion: int):
        if not self.puede_escribir_paciente_actual:
            return
        with Session(get_engine()) as session:
            eliminar_item_prescripcion(session, id_prescripcion)
            self.px_lista_items = listar_prescripcion_atencion(
                session, self.px_id_atencion, self.id_medico
            )

    # ── Cuidados generales ────────────────────────────────────────────────────

    def set_px_cuidados_generales(self, v: str):
        self.px_cuidados_generales = v

    def guardar_cuidados(self):
        if not self.puede_escribir_paciente_actual:
            return
        if not self.px_id_atencion:
            return
        try:
            with Session(get_engine()) as session:
                actualizar_prescripcion_cuidados(
                    session, self.px_id_atencion, self.px_cuidados_generales
                )
            self.px_guardado_ok = True
        except Exception as e:
            self.px_error = f"Error al guardar cuidados: {str(e)}"

    def cerrar_guardado_ok(self):
        self.px_guardado_ok = False

    # ── Historial de prescripciones ───────────────────────────────────────────

    def hp_cargar(self):
        if not self.paciente_seleccionado:
            return
        nro = self.paciente_seleccionado[0]
        with Session(get_engine()) as session:
            self.hp_lista = historial_prescripciones_paciente(session, nro, self.id_medico)

    def set_hp_filtro(self, v: str):
        self.hp_filtro = v

    def hp_limpiar_filtro(self):
        self.hp_filtro = ""

    def hp_toggle_orden(self, col: str):
        if self.hp_orden_col == col:
            self.hp_orden_asc = not self.hp_orden_asc
        else:
            self.hp_orden_col = col
            self.hp_orden_asc = col == "nombre_generico"  # asc para texto, desc para fecha

    def hp_selecciona_fila(self, id_atencion: int):
        if id_atencion == self.hp_id_atencion_sel:
            return
        self.hp_id_atencion_sel = id_atencion
        for row in self.hp_lista:
            if row.get("id_atencion") == id_atencion:
                fecha_str = row.get("fecha_atencion", "")
                self.hp_sel_fecha  = fecha_str
                self.hp_sel_motivo = row.get("motivo_consulta", "")
                # Calcular años y meses transcurridos desde la fecha de la atención
                try:
                    from datetime import date as _date
                    fecha_at = _date.fromisoformat(fecha_str[:10])
                    hoy = _date.today()
                    anios = hoy.year - fecha_at.year
                    meses = hoy.month - fecha_at.month
                    if meses < 0:
                        anios -= 1
                        meses += 12
                    self.hp_sel_edad = f"{anios}a {meses}m" if anios > 0 else f"{meses}m"
                except Exception:
                    self.hp_sel_edad = ""
                break
        with Session(get_engine()) as session:
            self.hp_sel_items        = listar_prescripcion_atencion(session, id_atencion, self.id_medico)
            self.hp_sel_diagnosticos = diagnosticos_atencion_detalle(session, id_atencion)
            cuidados = obtener_prescripcion_cuidados(session, id_atencion)
            self.hp_sel_cuidados = cuidados["cuidados_generales"] if cuidados else ""

    # ── Grabar / Editar / Guardar Cambios prescripción ────────────────────────

    def grabar_prescripcion(self):
        """Guarda cuidados y bloquea el formulario."""
        if not self.puede_escribir_paciente_actual:
            return
        if self.px_id_atencion:
            try:
                with Session(get_engine()) as session:
                    actualizar_prescripcion_cuidados(
                        session, self.px_id_atencion, self.px_cuidados_generales
                    )
            except Exception as e:
                self.px_error = f"Error al guardar: {str(e)}"
                return
        self.px_grabada     = True
        self.px_editando    = False
        self.px_guardado_ok = True
        self.px_error       = ""

    def editar_prescripcion(self):
        """Desbloquea el formulario para edición."""
        self.px_editando    = True
        self.px_guardado_ok = False
        self.px_error       = ""

    def guardar_cambios_prescripcion(self):
        """Guarda cuidados y vuelve a bloquear."""
        if not self.puede_escribir_paciente_actual:
            return
        if self.px_id_atencion:
            try:
                with Session(get_engine()) as session:
                    actualizar_prescripcion_cuidados(
                        session, self.px_id_atencion, self.px_cuidados_generales
                    )
            except Exception as e:
                self.px_error = f"Error al guardar: {str(e)}"
                return
        self.px_editando    = False
        self.px_guardado_ok = True
        self.px_error       = ""

    # ── Diálogo editar ítem existente ─────────────────────────────────────────

    def abrir_dlg_editar(self, id_prescripcion: int):
        """Precarga el diálogo con los datos del ítem a editar."""
        item = next((i for i in self.px_lista_items if i["id_prescripcion"] == id_prescripcion), None)
        if not item:
            return
        self.px_edit_id              = id_prescripcion
        self.px_edit_med_nombre      = item.get("nombre_generico", "")
        self.px_edit_concentracion   = item.get("concentracion", "")
        self.px_edit_cantidad        = int(item.get("cantidad", 1))
        self.px_edit_lk_presentacion = int(item.get("lk_presentacion", 0) or 0)
        self.px_edit_indicaciones    = item.get("indicaciones", "")
        self.px_edit_error           = ""
        self.px_dlg_editar           = True

    def set_px_dlg_editar(self, v: bool):
        self.px_dlg_editar = v

    def cerrar_dlg_editar(self):
        self.px_dlg_editar = False
        self.px_edit_error = ""

    def set_px_edit_concentracion(self, v: str):
        self.px_edit_concentracion = v
        self.px_edit_error = ""

    def set_px_edit_cantidad(self, v: str):
        self.px_edit_cantidad = max(1, int(v or 1))

    def set_px_edit_lk_presentacion(self, v: str):
        self.px_edit_lk_presentacion = int(v or 0)

    def set_px_edit_indicaciones(self, v: str):
        self.px_edit_indicaciones = v
        self.px_edit_error = ""

    def guardar_edicion_item(self):
        """Valida y persiste los cambios del ítem en edición."""
        if not self.puede_escribir_paciente_actual:
            return
        if not self.px_edit_concentracion.strip() or not self.px_edit_indicaciones.strip():
            self.px_edit_error = "Concentración e indicaciones son obligatorias."
            return
        if self.px_edit_cantidad < 1:
            self.px_edit_error = "La cantidad debe ser al menos 1."
            return
        try:
            with Session(get_engine()) as session:
                actualizar_item_prescripcion(
                    session=session,
                    id_prescripcion=self.px_edit_id,
                    concentracion=self.px_edit_concentracion,
                    cantidad=self.px_edit_cantidad,
                    lk_presentacion=self.px_edit_lk_presentacion if self.px_edit_lk_presentacion > 0 else None,
                    indicaciones=self.px_edit_indicaciones,
                    medico_id=self.id_medico,
                )
                self.px_lista_items = listar_prescripcion_atencion(
                    session, self.px_id_atencion, self.id_medico
                )
            self.px_dlg_editar = False
            self.px_edit_error = ""
        except Exception as e:
            self.px_edit_error = f"Error al guardar: {str(e)}"

    # ── Diálogo nuevo medicamento ─────────────────────────────────────────────

    def abrir_dlg_nuevo_med(self):
        self.px_nuevo_gen_nombre    = self.px_filtro_med.strip().upper()
        self.px_nuevo_gen_comercial = ""
        self.px_nuevo_gen_error     = ""
        self.px_dlg_nuevo_med       = True

    def set_px_dlg_nuevo_med(self, v: bool):
        self.px_dlg_nuevo_med = v

    def cerrar_dlg_nuevo_med(self):
        self.px_dlg_nuevo_med = False

    def set_px_nuevo_gen_nombre(self, v: str):    self.px_nuevo_gen_nombre    = v.upper()
    def set_px_nuevo_gen_comercial(self, v: str): self.px_nuevo_gen_comercial = v

    def guardar_nuevo_medicamento(self):
        if not self.puede_escribir:
            return
        if not self.px_nuevo_gen_nombre.strip():
            self.px_nuevo_gen_error = "El nombre genérico es obligatorio."
            return
        try:
            with Session(get_engine()) as session:
                nuevo = agregar_medicamento_nuevo(
                    session,
                    self.px_nuevo_gen_nombre,
                    self.px_nuevo_gen_comercial,
                )
                # Seleccionarlo automáticamente en el formulario
                self.px_med_cod    = nuevo["cod_gen"]
                self.px_med_nombre = nuevo["nombre_generico"]
                # Refrescar catálogo
                self.px_lista_medicamentos = buscar_medicamentos(session)
            self.px_dlg_nuevo_med = False
            self.px_filtro_med    = ""
        except Exception as e:
            self.px_nuevo_gen_error = f"Error: {str(e)}"

    # ── Privados ──────────────────────────────────────────────────────────────

    def _reset_form(self):
        self.px_med_cod          = 0
        self.px_med_nombre       = ""
        self.px_filtro_med       = ""
        self.px_concentracion    = ""
        self.px_cantidad         = 1
        self.px_lk_presentacion  = 0
        self.px_indicaciones     = ""
        self.px_form_error       = ""
        # edit dialog
        self.px_dlg_editar           = False
        self.px_edit_id              = 0
        self.px_edit_med_nombre      = ""
        self.px_edit_concentracion   = ""
        self.px_edit_cantidad        = 1
        self.px_edit_lk_presentacion = 0
        self.px_edit_indicaciones    = ""
        self.px_edit_error           = ""


# ══════════════════════════════════════════════════════════════════════════════
class MantenimientoMedState(State):
    """Diálogo de mantenimiento del catálogo de medicamentos."""
    mm_dlg_open:     bool       = False
    mm_confirm_open: bool       = False
    mm_tipos:        list[dict] = []
    mm_tipo_id:      str        = ""
    mm_generico:     str        = ""
    mm_comercial:    str        = ""
    mm_similares:    list[dict] = []
    mm_error:        str        = ""

    def abrir_dlg(self):
        with Session(get_engine()) as session:
            self.mm_tipos = listar_tipos_medicamento(session)
        self.mm_tipo_id      = str(self.mm_tipos[0]["id_tipo"]) if self.mm_tipos else ""
        self.mm_generico     = ""
        self.mm_comercial    = ""
        self.mm_similares    = []
        self.mm_error        = ""
        self.mm_confirm_open = False
        self.mm_dlg_open     = True

    def set_mm_dlg_open(self, v: bool):
        self.mm_dlg_open = v

    def cerrar_dlg(self):
        self.mm_dlg_open     = False
        self.mm_confirm_open = False

    def set_tipo(self, v: str):
        self.mm_tipo_id = v

    def set_generico(self, v: str):
        self.mm_generico = v.upper()
        texto = self.mm_generico.strip()
        if len(texto) >= 3:
            with Session(get_engine()) as session:
                self.mm_similares = buscar_similares_medicamento(session, texto)
        else:
            self.mm_similares = []

    def set_comercial(self, v: str):
        self.mm_comercial = v.upper()

    def set_mm_confirm_open(self, v: bool):
        self.mm_confirm_open = v

    def intentar_anadir(self):
        self.mm_error = ""
        if not self.mm_generico.strip():
            self.mm_error = "El nombre genérico es obligatorio."
            return
        if not self.mm_tipo_id:
            self.mm_error = "Debe seleccionar el tipo de medicamento."
            return
        if self.mm_similares:
            self.mm_confirm_open = True
        else:
            self._guardar()

    def confirmar_anadir(self):
        self.mm_confirm_open = False
        self._guardar()

    def _guardar(self):
        try:
            with Session(get_engine()) as session:
                guardar_medicamento_catalogo(
                    session,
                    nombre_generico=self.mm_generico.strip(),
                    nombre_comercial=self.mm_comercial.strip(),
                    tipo_id=int(self.mm_tipo_id),
                )
            self.mm_dlg_open = False
        except Exception as e:
            self.mm_error = f"Error al guardar: {str(e)}"


# ══════════════════════════════════════════════════════════════════════════════
class NuevoAntFamiliarState(State):
    naf_dialog_open:    bool = False
    naf_fecha_registro: str  = ""
    naf_descripcion:    str  = ""
    naf_error:          str  = ""

    def abrir_naf_dialog(self):
        self.naf_fecha_registro = str(date.today())
        self.naf_descripcion    = ""
        self.naf_error          = ""
        self.naf_dialog_open    = True

    def set_naf_dialog_open(self, v: bool):  self.naf_dialog_open    = v
    def set_naf_fecha_registro(self, v: str): self.naf_fecha_registro = v
    def set_naf_descripcion(self, v: str):    self.naf_descripcion    = v

    def guardar_naf(self):
        if not self.puede_escribir_paciente_actual:
            return
        if not self.naf_descripcion.strip():
            self.naf_error = "La descripción es obligatoria."
            return
        if not self.naf_fecha_registro:
            self.naf_error = "La fecha de registro es obligatoria."
            return
        if not self.paciente_seleccionado:
            self.naf_error = "No hay paciente seleccionado."
            return
        _crypto = GesmedCrypto.para_medico(self.id_medico)
        try:
            with Session(get_engine()) as s:
                s.add(AntecedenteFamiliar(
                    lk_paciente    = self.paciente_seleccionado[0],
                    descripcion    = _crypto.encriptar(self.naf_descripcion.strip()),
                    fecha_registro = date.fromisoformat(self.naf_fecha_registro),
                ))
                s.commit()
            with Session(get_engine()) as s:
                self.lista_ant_familiares = listar_ant_familiares(
                    s, self.paciente_seleccionado[0], self.id_medico
                )
            self.naf_dialog_open = False
        except Exception as e:
            self.naf_error = f"Error al guardar: {e}"


# ══════════════════════════════════════════════════════════════════════════════
class PedidoExamenesState(AtencionState):
    """
    Gestiona el pedido de exámenes de laboratorio para la atención actual.

    Flujo:
        1. Abrir offcanvas → pe_abrir(soap_id_atencion) carga catálogo + pedido existente
        2. Médico agrega exámenes con pe_agregar_examen / quita con pe_quitar_examen
        3. pe_grabar() persiste en DB → estado "grabado"
        4. pe_editar() desbloquea → pe_guardar_cambios() persiste cambios
    """

    # ── Catálogo y filtros ────────────────────────────────────────────────────
    pe_catalogo:      list[dict] = []   # todos los exámenes activos con nombre de grupo
    pe_grupos:        list[dict] = []   # para el selector de filtro por grupo
    pe_filtro_nombre: str        = ""
    pe_filtro_grupo:  int        = 0    # 0 = todos

    # ── Exámenes seleccionados (el pedido en construcción) ────────────────────
    pe_seleccionados: list[dict] = []

    # ── Máquina de estados ────────────────────────────────────────────────────
    pe_grabado:     bool = False
    pe_editando:    bool = False
    pe_guardado_ok: bool = False
    pe_error:       str  = ""

    # ── Computed vars ─────────────────────────────────────────────────────────

    @rx.var
    def pe_catalogo_filtrado(self) -> list[dict]:
        items = self.pe_catalogo
        filtro = self.pe_filtro_nombre.strip().lower()
        if filtro:
            return [e for e in items if filtro in e["nombre_examen"].lower()]
        if self.pe_filtro_grupo:
            return [e for e in items if e["id_grupo"] == self.pe_filtro_grupo]
        return items

    @rx.var
    def pe_campos_bloqueados(self) -> bool:
        return self.pe_grabado and not self.pe_editando

    @rx.var
    def pe_deshabilitado(self) -> bool:
        return not self.soap_grabado

    @rx.var
    def pe_tiene_seleccionados(self) -> bool:
        return len(self.pe_seleccionados) > 0

    @rx.var
    def pe_grupos_select(self) -> list[str]:
        """Lista para el rx.select: 'Todos' + nombre de cada grupo."""
        return ["Todos"] + [g["nombre_grupo"] for g in self.pe_grupos]

    @rx.var
    def pe_grupo_sel_nombre(self) -> str:
        for g in self.pe_grupos:
            if g["id_grupo"] == self.pe_filtro_grupo:
                return g["nombre_grupo"]
        return "Todos"

    @rx.var
    def pe_seleccionados_con_fondo(self) -> list[dict]:
        ordenados = sorted(self.pe_seleccionados, key=lambda e: e["nombre_grupo"])
        resultado = []
        grupo_actual = None
        indice_grupo = -1
        colores = ["white", "var(--gray-3)"]
        for e in ordenados:
            if e["nombre_grupo"] != grupo_actual:
                grupo_actual = e["nombre_grupo"]
                indice_grupo += 1
            resultado.append({**e, "fila_fondo": colores[indice_grupo % 2]})
        return resultado

    # ── Apertura ──────────────────────────────────────────────────────────────

    def pe_abrir(self, id_atencion: int):
        with Session(get_engine()) as session:
            self.pe_catalogo = cargar_catalogo_examenes(session)
            self.pe_grupos   = cargar_grupos_examenes(session)
            pedido           = cargar_pedido_atencion(session, id_atencion)
        self.pe_seleccionados = pedido
        self.pe_grabado       = len(pedido) > 0
        self.pe_editando      = False
        self.pe_filtro_nombre = ""
        self.pe_filtro_grupo  = 0
        self.pe_error         = ""
        self.pe_guardado_ok   = False

    def pe_reinicia(self):
        self.pe_catalogo      = []
        self.pe_grupos        = []
        self.pe_filtro_nombre = ""
        self.pe_filtro_grupo  = 0
        self.pe_seleccionados = []
        self.pe_grabado       = False
        self.pe_editando      = False
        self.pe_error         = ""
        self.pe_guardado_ok   = False

    # ── Filtros ───────────────────────────────────────────────────────────────

    def set_pe_filtro_nombre(self, v: str):
        self.pe_filtro_nombre = v

    def set_pe_filtro_grupo_nombre(self, nombre: str):
        if nombre == "Todos":
            self.pe_filtro_grupo = 0
            return
        for g in self.pe_grupos:
            if g["nombre_grupo"] == nombre:
                self.pe_filtro_grupo = g["id_grupo"]
                return
        self.pe_filtro_grupo = 0

    def pe_toggle_grupo(self, id_grupo: int):
        self.pe_filtro_grupo = 0 if self.pe_filtro_grupo == id_grupo else id_grupo
        self.pe_filtro_nombre = ""

    # ── Edición de la lista ───────────────────────────────────────────────────

    def pe_agregar_examen(self, id_examen: int):
        if self.pe_campos_bloqueados:
            return
        if any(e["id_examen"] == id_examen for e in self.pe_seleccionados):
            return
        examen = next((e for e in self.pe_catalogo if e["id_examen"] == id_examen), None)
        if examen:
            self.pe_seleccionados = self.pe_seleccionados + [{
                "id_pedido":     0,
                "id_examen":     examen["id_examen"],
                "nombre_examen": examen["nombre_examen"],
                "nombre_grupo":  examen["nombre_grupo"],
            }]

    def pe_quitar_examen(self, id_examen: int):
        if self.pe_campos_bloqueados:
            return
        self.pe_seleccionados = [
            e for e in self.pe_seleccionados if e["id_examen"] != id_examen
        ]

    # ── Persistencia ─────────────────────────────────────────────────────────

    def pe_grabar(self):
        if not self.soap_id_atencion or not self.paciente_seleccionado:
            self.pe_error = "No hay atención activa."
            return
        if not self.pe_seleccionados:
            self.pe_error = "Agregue al menos un examen al pedido."
            return
        try:
            with Session(get_engine()) as session:
                guardar_pedido_examenes(
                    session,
                    lk_paciente=self.paciente_seleccionado[0],
                    lk_atencion=self.soap_id_atencion,
                    examen_ids=[e["id_examen"] for e in self.pe_seleccionados],
                )
                self.pe_seleccionados = cargar_pedido_atencion(session, self.soap_id_atencion)
            self.pe_grabado     = True
            self.pe_editando    = False
            self.pe_guardado_ok = True
            self.pe_error       = ""
        except Exception as exc:
            self.pe_error = f"Error al guardar: {str(exc)}"

    def pe_editar(self):
        self.pe_editando    = True
        self.pe_guardado_ok = False
        self.pe_error       = ""

    def pe_guardar_cambios(self):
        if not self.soap_id_atencion or not self.paciente_seleccionado:
            self.pe_error = "No hay atención activa."
            return
        try:
            with Session(get_engine()) as session:
                guardar_pedido_examenes(
                    session,
                    lk_paciente=self.paciente_seleccionado[0],
                    lk_atencion=self.soap_id_atencion,
                    examen_ids=[e["id_examen"] for e in self.pe_seleccionados],
                )
                self.pe_seleccionados = cargar_pedido_atencion(session, self.soap_id_atencion)
            self.pe_editando    = False
            self.pe_grabado     = True
            self.pe_guardado_ok = True
            self.pe_error       = ""
        except Exception as exc:
            self.pe_error = f"Error al guardar: {str(exc)}"

    def pe_cerrar_guardado_ok(self):
        self.pe_guardado_ok = False


# ── Pedido de Otros Exámenes (examen_tipo → examen_catalogo → examen_pedido) ──

class OtrosPedidoState(AtencionState):

    oe_soap_valido:      bool       = False
    oe_diagnosticos:     list[dict] = []
    oe_lk_diagnostico:  int        = 0

    oe_tipos:            list[dict] = []
    oe_sel_tipo:         int        = 0
    oe_catalogo:         list[dict] = []
    oe_sel_examen:       int        = 0
    oe_detalle:          str        = "Favor realizar un"

    oe_lista:            list[dict] = []

    oe_form_visible:     bool       = False

    oe_edit_id:          int        = 0
    oe_edit_sel_tipo:    int        = 0
    oe_edit_catalogo:    list[dict] = []
    oe_edit_sel_examen:  int        = 0
    oe_edit_detalle:     str        = ""
    oe_editando_fila:    bool       = False

    oe_error:            str        = ""

    # Contexto local para el URL del reporte (evita acceder vars de estados abuelos en computed vars)
    oe_ctx_atencion:     int        = 0
    oe_ctx_medico:       int        = 0
    oe_ctx_paciente:     int        = 0

    # ── Computed vars ─────────────────────────────────────────────────────────

    @rx.var
    def oe_deshabilitado(self) -> bool:
        return not self.oe_soap_valido

    @rx.var
    def oe_bloquear_form(self) -> bool:
        return self.oe_lk_diagnostico == 0 or not self.oe_soap_valido

    @rx.var
    def oe_tiene_lista(self) -> bool:
        return len(self.oe_lista) > 0

    @rx.var
    def oe_url_reporte(self) -> str:
        return (
            f"{_BACKEND}/reporte/pedido_examen"
            f"?lk_atencion={self.oe_ctx_atencion}"
            f"&lk_medico={self.oe_ctx_medico}"
            f"&lk_paciente={self.oe_ctx_paciente}"
        )

    @rx.var
    def oe_opciones_diag(self) -> list[list[str]]:
        return [[str(d["id"]), f"{d['cod']} - {d['nombre']}"] for d in self.oe_diagnosticos]

    @rx.var
    def oe_opciones_tipos(self) -> list[list[str]]:
        return [[str(t["id"]), t["nombre"]] for t in self.oe_tipos]

    @rx.var
    def oe_opciones_cat(self) -> list[list[str]]:
        return [[str(e["id"]), f"{e['alias']} - {e['nombre']}"] for e in self.oe_catalogo]

    @rx.var
    def oe_opciones_cat_edit(self) -> list[list[str]]:
        return [[str(e["id"]), f"{e['alias']} - {e['nombre']}"] for e in self.oe_edit_catalogo]

    @rx.var
    def oe_val_diag(self) -> str:
        return str(self.oe_lk_diagnostico) if self.oe_lk_diagnostico else ""

    @rx.var
    def oe_val_tipo(self) -> str:
        return str(self.oe_sel_tipo) if self.oe_sel_tipo else ""

    @rx.var
    def oe_val_examen(self) -> str:
        return str(self.oe_sel_examen) if self.oe_sel_examen else ""

    @rx.var
    def oe_val_edit_tipo(self) -> str:
        return str(self.oe_edit_sel_tipo) if self.oe_edit_sel_tipo else ""

    @rx.var
    def oe_val_edit_examen(self) -> str:
        return str(self.oe_edit_sel_examen) if self.oe_edit_sel_examen else ""

    # ── Setters con lógica adicional ──────────────────────────────────────────

    def set_oe_lk_diagnostico(self, v: str):
        try:
            self.oe_lk_diagnostico = int(v) if v else 0
        except ValueError:
            self.oe_lk_diagnostico = 0
        self._oe_cargar_lista()

    def set_oe_sel_tipo(self, v: str):
        try:
            self.oe_sel_tipo = int(v) if v else 0
        except ValueError:
            self.oe_sel_tipo = 0
        self.oe_sel_examen = 0
        self._oe_filtrar_catalogo()

    def set_oe_sel_examen(self, v: str):
        try:
            self.oe_sel_examen = int(v) if v else 0
        except ValueError:
            self.oe_sel_examen = 0

    def set_oe_detalle(self, v: str):
        self.oe_detalle = v

    def set_oe_form_visible(self, v: bool):
        self.oe_form_visible = v
        if not v:
            self.oe_error = ""

    def set_oe_edit_sel_tipo(self, v: str):
        try:
            self.oe_edit_sel_tipo = int(v) if v else 0
        except ValueError:
            self.oe_edit_sel_tipo = 0
        self.oe_edit_sel_examen = 0
        self._oe_filtrar_catalogo_edit()

    def set_oe_edit_sel_examen(self, v: str):
        try:
            self.oe_edit_sel_examen = int(v) if v else 0
        except ValueError:
            self.oe_edit_sel_examen = 0

    def set_oe_edit_detalle(self, v: str):
        self.oe_edit_detalle = v

    # ── Helpers privados ──────────────────────────────────────────────────────

    def _oe_filtrar_catalogo(self):
        if not self.oe_sel_tipo:
            self.oe_catalogo = []
            return
        with Session(get_engine()) as session:
            rows = session.exec(
                select(OtrosExamenesCatalogo)
                .where(OtrosExamenesCatalogo.lk_examen_tipo == self.oe_sel_tipo)
            ).all()
            self.oe_catalogo = [
                {"id": r.id_examen, "alias": r.examen_alias, "nombre": r.examen_nombre}
                for r in rows
            ]

    def _oe_filtrar_catalogo_edit(self):
        if not self.oe_edit_sel_tipo:
            self.oe_edit_catalogo = []
            return
        with Session(get_engine()) as session:
            rows = session.exec(
                select(OtrosExamenesCatalogo)
                .where(OtrosExamenesCatalogo.lk_examen_tipo == self.oe_edit_sel_tipo)
            ).all()
            self.oe_edit_catalogo = [
                {"id": r.id_examen, "alias": r.examen_alias, "nombre": r.examen_nombre}
                for r in rows
            ]

    def _oe_cargar_lista(self):
        if not self.soap_id_atencion:
            self.oe_lista = []
            return
        with Session(get_engine()) as session:
            rows = session.execute(text("""
                SELECT p.id_examen_pedido, t.examen_tipo, c.examen_alias, c.examen_nombre,
                       p.detalle_pedido, p.lk_catalogo, p.lk_diagnostico, t.id_examen_tipo
                FROM examen_pedido p
                JOIN examen_catalogo c ON c.id_examen = p.lk_catalogo
                JOIN examen_tipo t ON t.id_examen_tipo = c.lk_examen_tipo
                WHERE p.lk_atencion = :lk
                ORDER BY t.examen_tipo, p.id_examen_pedido
            """), {"lk": self.soap_id_atencion}).all()
            self.oe_lista = [
                {
                    "id":      int(r[0]),
                    "tipo":    str(r[1]),
                    "alias":   str(r[2]),
                    "nombre":  str(r[3]),
                    "detalle": str(r[4]),
                    "lk_cat":  int(r[5]),
                    "lk_diag": int(r[6]),
                    "lk_tipo": int(r[7]),
                }
                for r in rows
            ]

    # ── Carga inicial ─────────────────────────────────────────────────────────

    def oe_cargar(self):
        self.oe_error = ""
        self.oe_form_visible = False
        self.oe_editando_fila = False
        self.oe_lk_diagnostico = 0
        self.oe_sel_tipo = 0
        self.oe_catalogo = []
        self.oe_sel_examen = 0
        self.oe_detalle = "Favor realizar un"
        self.oe_lista = []
        self.oe_diagnosticos = []
        self.oe_tipos = []
        # Guardar contexto localmente (evita acceso a vars de estados abuelos en computed vars)
        self.oe_ctx_atencion = self.soap_id_atencion
        self.oe_ctx_medico   = self.id_medico
        self.oe_ctx_paciente = self.paciente_seleccionado[0] if self.paciente_seleccionado else 0
        if not self.soap_id_atencion:
            self.oe_soap_valido = False
            return
        with Session(get_engine()) as session:
            at = session.exec(
                select(Atencion).where(Atencion.id_atencion == self.soap_id_atencion)
            ).first()
            self.oe_soap_valido = bool(at and at.subjetivo and at.subjetivo.strip())
            if not self.oe_soap_valido:
                return
            diag_rows = session.execute(text("""
                SELECT d.id_diagnostico, d.lk_cie10, c.nomdiagnostico
                FROM rel_atencion_diagnostico r
                JOIN diagnostico d ON d.id_diagnostico = r.lk_diagnostico
                JOIN cie10 c ON c.cod_cie10 = d.lk_cie10
                WHERE r.lk_atencion = :lk
            """), {"lk": self.soap_id_atencion}).all()
            self.oe_diagnosticos = [
                {"id": int(r[0]), "cod": str(r[1]), "nombre": str(r[2])} for r in diag_rows
            ]
            tipos = session.exec(select(OtrosExamenesTipo)).all()
            self.oe_tipos = [
                {"id": int(t.id_examen_tipo), "nombre": t.examen_tipo} for t in tipos
            ]
        self._oe_cargar_lista()

    # ── Acciones del formulario ────────────────────────────────────────────────

    def oe_abrir_form(self):
        if self.oe_bloquear_form:
            return
        self.oe_sel_tipo = 0
        self.oe_catalogo = []
        self.oe_sel_examen = 0
        self.oe_detalle = "Favor realizar un"
        self.oe_form_visible = True
        self.oe_editando_fila = False
        self.oe_error = ""

    def oe_cancelar_form(self):
        self.oe_form_visible = False
        self.oe_error = ""

    def oe_grabar_examen(self):
        if not self.soap_id_atencion or not self.oe_lk_diagnostico:
            self.oe_error = "Seleccione un diagnóstico primero."
            return
        if not self.oe_sel_examen:
            self.oe_error = "Seleccione el tipo y el examen."
            return
        try:
            with Session(get_engine()) as session:
                nuevo = OtrosExamenesPedido(
                    lk_atencion=self.soap_id_atencion,
                    lk_catalogo=self.oe_sel_examen,
                    lk_diagnostico=self.oe_lk_diagnostico,
                    detalle_pedido=self.oe_detalle or "Favor realizar un",
                )
                session.add(nuevo)
                session.commit()
            self._oe_cargar_lista()
            self.oe_form_visible = False
            self.oe_error = ""
        except Exception as exc:
            self.oe_error = f"Error al guardar: {str(exc)}"

    # ── Edición de fila ───────────────────────────────────────────────────────

    def oe_iniciar_editar(self, id_pedido: int):
        fila = next((r for r in self.oe_lista if r["id"] == id_pedido), None)
        if not fila:
            return
        self.oe_edit_id = id_pedido
        self.oe_edit_detalle = fila["detalle"]
        self.oe_edit_sel_examen = fila["lk_cat"]
        self.oe_editando_fila = True
        self.oe_form_visible = False
        with Session(get_engine()) as session:
            cat = session.exec(
                select(OtrosExamenesCatalogo)
                .where(OtrosExamenesCatalogo.id_examen == fila["lk_cat"])
            ).first()
            if cat:
                self.oe_edit_sel_tipo = cat.lk_examen_tipo or 0
                self._oe_filtrar_catalogo_edit()
        self.oe_error = ""

    def oe_cancelar_editar(self):
        self.oe_editando_fila = False
        self.oe_error = ""

    def oe_guardar_edicion(self):
        if not self.oe_edit_id or not self.oe_edit_sel_examen:
            self.oe_error = "Seleccione un examen."
            return
        try:
            with Session(get_engine()) as session:
                pedido = session.exec(
                    select(OtrosExamenesPedido)
                    .where(OtrosExamenesPedido.id_examen_pedido == self.oe_edit_id)
                ).first()
                if pedido:
                    pedido.lk_catalogo = self.oe_edit_sel_examen
                    pedido.detalle_pedido = self.oe_edit_detalle or "Favor realizar un"
                    session.add(pedido)
                    session.commit()
            self.oe_editando_fila = False
            self._oe_cargar_lista()
            self.oe_error = ""
        except Exception as exc:
            self.oe_error = f"Error al actualizar: {str(exc)}"

    def oe_eliminar(self, id_pedido: int):
        try:
            with Session(get_engine()) as session:
                pedido = session.exec(
                    select(OtrosExamenesPedido)
                    .where(OtrosExamenesPedido.id_examen_pedido == id_pedido)
                ).first()
                if pedido:
                    session.delete(pedido)
                    session.commit()
            self._oe_cargar_lista()
        except Exception as exc:
            self.oe_error = f"Error al eliminar: {str(exc)}"


# ── Modelos tipados para ConfigReportesState ──────────────────────────────────
class CrReporteItem(_PydanticBase):
    id:      int = 0
    nombre:  str = ""
    explica: str = ""
    fuente:  str = ""

class CrSeccionItem(_PydanticBase):
    id:                   int       = 0
    orden:                int       = 1
    explica:              str       = ""
    sql:                  str       = ""
    params:               list[str] = []
    activa:               int       = 1
    modo_bucle:           str       = "N"
    paso_fila:            int       = 1
    max_iteraciones:      int       = 10
    lk_seccion_ancla:     int       = 0
    ancla_gap:            int       = 0
    condicion_activa_sql: str       = ""
    campo_grupo:          str       = ""
    num_columnas:         int       = 1
    paso_columna:         int       = 0
    slot_height:          int       = 10
    titulo_seccion:       str       = ""

def _int_a_letra(n: int) -> str:
    """Convierte columna numérica (base-26 biyectiva) a letras Excel: 1→A, 27→AA."""
    result = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        result = chr(65 + r) + result
    return result or "A"

class CrCeldaItem(_PydanticBase):
    id:         int = 0
    variable:   str = ""
    fila:       int = 1
    columna:    int = 1
    celda_ref:  str = ""
    explica:    str = ""
    formato:    str = "09.01.01.00.NLU.0000"
    activa:     int = 1
    pre_fijo:   str = ""
    post_fijo:  str = ""
    en_letras:  int = 0
    tipo_celda: str = "D"

class CrImagenItem(_PydanticBase):
    id:             int = 0
    nombre_archivo: str = ""
    celda:          str = ""
    ancho:          int = 100
    alto:           int = 40
    orden:          int = 1
    pre_fijo:  str = ""
    post_fijo: str = ""
    en_letras:  int = 0
    tipo_celda: str = "D"

# ── Fuentes disponibles para reportes ─────────────────────────────────────────
_FUENTES_REPORTES: list[str] = [
    "Arial Narrow", "Arial", "Calibri",
    "Times New Roman", "Courier New", "Helvetica",
]

def _parsear_formato(fmt: str) -> dict:
    parts = fmt.split(".")
    if len(parts) not in (6, 7):
        return {"size": 9, "mh": 1, "mv": 1, "sombra": 0,
                "efecto": "N", "ah": "L", "av": "U",
                "bt": False, "br": False, "bb": False, "bl": False,
                "en_letras": False}
    eff = parts[4] if len(parts[4]) >= 3 else "NLU"
    brd = parts[5] if len(parts[5]) == 4 else "0000"
    return {
        "size": int(parts[0]), "mh": int(parts[1]), "mv": int(parts[2]),
        "sombra": int(parts[3]), "efecto": eff[0], "ah": eff[1], "av": eff[2],
        "bt": brd[0] == "1", "br": brd[1] == "1",
        "bb": brd[2] == "1", "bl": brd[3] == "1",
        "en_letras": len(parts) == 7 and parts[6] == "T",
    }


# ══════════════════════════════════════════════════════════════════════════════
class NuevaAlergiaState(State):
    naa_dialog_open: bool = False
    naa_sustancia:   str  = ""
    naa_error:       str  = ""

    def abrir_naa_dialog(self):
        self.naa_sustancia   = ""
        self.naa_error       = ""
        self.naa_dialog_open = True

    def set_naa_dialog_open(self, v: bool): self.naa_dialog_open = v
    def set_naa_sustancia(self, v: str):    self.naa_sustancia   = v

    def guardar_naa(self):
        if not self.puede_escribir_paciente_actual:
            return
        if not self.naa_sustancia.strip():
            self.naa_error = "La sustancia es obligatoria."
            return
        if not self.paciente_seleccionado:
            self.naa_error = "No hay paciente seleccionado."
            return
        try:
            with Session(get_engine()) as s:
                s.add(Alergia(
                    lk_paciente       = self.paciente_seleccionado[0],
                    sustancia_alergia = self.naa_sustancia.strip(),
                    fecha_reportada   = date.today(),
                ))
                s.commit()
            with Session(get_engine()) as s:
                self.lista_alergias = listar_alergias_paciente(s, self.paciente_seleccionado[0])
            self.naa_dialog_open = False
        except Exception as e:
            self.naa_error = f"Error al guardar: {e}"


class CertificadoState(State):
    # ── Dialog "sin SOAP" ────────────────────────────────────────────────────
    cert_dlg_sin_soap:   bool = False

    # ── Formulario certificado (nuevo y tardío) ───────────────────────────────
    cert_dlg_formulario:      bool = False
    cert_id_atencion:         int  = 0
    cert_grabado:             bool = False
    cert_id_grabado:          int  = 0
    cert_reposo_desde:        str  = ""
    cert_dias_reposo:         int  = 1
    cert_reposo_hasta:        str  = ""
    cert_contingencia:        str  = ""
    cert_presenta_sintomas:   bool = False
    cert_aislamiento:         bool = False
    cert_ocupacion:           str  = ""
    cert_lugar_trabajo:       str  = ""
    cert_observacion:         str  = ""
    cert_error:               str  = ""

    # ── Dialog lista atenciones tardías ──────────────────────────────────────
    cert_dlg_atenciones:     bool = False

    # ── Offcanvas todos los certificados ─────────────────────────────────────
    cert_offcanvas:          bool       = False
    cert_lista:              list[dict] = []
    cert_hoy:                str        = ""   # "YYYY-MM-DD" del día actual

    # ── Dialog editar certificado ─────────────────────────────────────────────
    cert_dlg_editar:         bool = False
    cert_edit_id:            int  = 0

    # ── Setters ──────────────────────────────────────────────────────────────
    def set_cert_dlg_sin_soap(self, v: bool):          self.cert_dlg_sin_soap         = v
    def set_cert_dlg_formulario(self, v: bool):        self.cert_dlg_formulario       = v
    def set_cert_dlg_atenciones(self, v: bool):        self.cert_dlg_atenciones       = v
    def set_cert_dlg_editar(self, v: bool):            self.cert_dlg_editar           = v
    def set_cert_reposo_desde(self, v: str):
        from datetime import date as _date, timedelta as _td
        self.cert_reposo_desde = v
        try:
            desde = _date.fromisoformat(v)
            self.cert_reposo_hasta = str(desde + _td(days=max(0, self.cert_dias_reposo - 1)))
        except ValueError:
            pass

    def set_cert_dias_reposo(self, v: str):
        from datetime import date as _date, timedelta as _td
        try:
            dias = max(1, int(v) if v else 1)
        except ValueError:
            return
        self.cert_dias_reposo = dias
        try:
            desde = _date.fromisoformat(self.cert_reposo_desde)
            self.cert_reposo_hasta = str(desde + _td(days=dias - 1))
        except ValueError:
            pass
    def set_cert_contingencia(self, v: str):           self.cert_contingencia         = v
    def set_cert_presenta_sintomas(self, v: bool):     self.cert_presenta_sintomas    = v
    def set_cert_aislamiento(self, v: bool):           self.cert_aislamiento          = v
    def set_cert_ocupacion(self, v: str):              self.cert_ocupacion            = v
    def set_cert_lugar_trabajo(self, v: str):          self.cert_lugar_trabajo        = v
    def set_cert_observacion(self, v: str):            self.cert_observacion          = v

    # ── Computed vars ─────────────────────────────────────────────────────────
    @rx.var
    def cert_url_reporte(self) -> str:
        return (f"{_BACKEND}/reporte/certificado"
                f"?lk_paciente={self.nro_hclinica_seleccionado}"
                f"&lk_atencion={self.cert_id_atencion}"
                f"&lk_medico={self.id_medico}")

    # ── Handlers ─────────────────────────────────────────────────────────────
    def _cert_reset_form(self):
        from datetime import date as _date
        hoy = str(_date.today())
        self.cert_reposo_desde      = hoy
        self.cert_dias_reposo       = 1
        self.cert_reposo_hasta      = hoy
        self.cert_contingencia      = ""
        self.cert_presenta_sintomas = False
        self.cert_aislamiento       = False
        self.cert_ocupacion         = ""
        self.cert_lugar_trabajo     = ""
        self.cert_observacion       = ""
        self.cert_error             = ""
        self.cert_grabado           = False
        self.cert_id_grabado        = 0

    def cert_abrir_nuevo(self):
        """Abre formulario para atención actual; verifica SOAP en DB."""
        if not self.id_atencion_seleccionada:
            self.cert_dlg_sin_soap = True
            return
        with Session(get_engine()) as s:
            a = s.get(Atencion, self.id_atencion_seleccionada)
            if not a or not (a.subjetivo or "").strip():
                self.cert_dlg_sin_soap = True
                return
        self._cert_reset_form()
        self.cert_id_atencion    = self.id_atencion_seleccionada
        self.cert_dlg_formulario = True

    def cert_abrir_formulario_tardio(self, id_atencion: int):
        """Verifica SOAP y abre formulario para atención pasada."""
        with Session(get_engine()) as s:
            a = s.get(Atencion, id_atencion)
            if not a or not (a.subjetivo or "").strip():
                self.cert_error        = "La atención seleccionada no tiene SOAP registrado."
                self.cert_dlg_atenciones = True   # mantiene el diálogo abierto con el error
                return
        self._cert_reset_form()
        self.cert_id_atencion    = id_atencion
        self.cert_dlg_atenciones = False
        self.cert_dlg_formulario = True

    def cert_guardar(self):
        from datetime import date as _date
        if not self.cert_id_atencion:
            return
        if not self.cert_reposo_desde or not self.cert_reposo_hasta:
            self.cert_error = "Las fechas de reposo son obligatorias."
            return
        try:
            with Session(get_engine()) as s:
                c = Certificado(
                    lk_atencion       = self.cert_id_atencion,
                    reposo_desde      = _date.fromisoformat(self.cert_reposo_desde),
                    reposo_hasta      = _date.fromisoformat(self.cert_reposo_hasta),
                    contingencia      = self.cert_contingencia.strip(),
                    presenta_sintomas = 1 if self.cert_presenta_sintomas else 0,
                    aislamiento       = 1 if self.cert_aislamiento else 0,
                    ocupacion         = self.cert_ocupacion.strip(),
                    lugar_trabajo     = self.cert_lugar_trabajo.strip(),
                    observacion       = self.cert_observacion.strip(),
                )
                s.add(c); s.commit(); s.refresh(c)
                self.cert_id_grabado = c.id_certificado
            self.cert_grabado = True
            self.cert_error   = ""
        except Exception as e:
            self.cert_error = f"Error al guardar: {e}"

    def cert_guardar_edicion(self):
        from datetime import date as _date
        if not self.cert_edit_id:
            return
        if not self.cert_reposo_desde or not self.cert_reposo_hasta:
            self.cert_error = "Las fechas de reposo son obligatorias."
            return
        try:
            with Session(get_engine()) as s:
                c = s.get(Certificado, self.cert_edit_id)
                if c:
                    c.reposo_desde      = _date.fromisoformat(self.cert_reposo_desde)
                    c.reposo_hasta      = _date.fromisoformat(self.cert_reposo_hasta)
                    c.contingencia      = self.cert_contingencia.strip()
                    c.presenta_sintomas = 1 if self.cert_presenta_sintomas else 0
                    c.aislamiento       = 1 if self.cert_aislamiento else 0
                    c.ocupacion         = self.cert_ocupacion.strip()
                    c.lugar_trabajo     = self.cert_lugar_trabajo.strip()
                    c.observacion       = self.cert_observacion.strip()
                    s.add(c); s.commit()
            self.cert_dlg_editar = False
            self.cert_edit_id    = 0
            self.cert_error      = ""
            self._cert_cargar_lista()
        except Exception as e:
            self.cert_error = f"Error al actualizar: {e}"

    def cert_abrir_dlg_atenciones(self):
        self.cert_error          = ""
        self.cert_dlg_atenciones = True

    def cert_abrir_offcanvas(self):
        from datetime import date as _date
        self.cert_hoy      = str(_date.today())
        self.cert_offcanvas = True
        self._cert_cargar_lista()

    def cert_cerrar_offcanvas(self):
        self.cert_offcanvas = False

    def _cert_cargar_lista(self):
        if not self.paciente_seleccionado:
            self.cert_lista = []
            return
        lk_pac = self.paciente_seleccionado[0]
        with Session(get_engine()) as s:
            rows = s.execute(text(
                "SELECT c.id_certificado, "
                "       DATE_FORMAT(a.fecha_atencion,'%d/%m/%Y %H:%i') AS fecha_atencion_fmt, "
                "       DATE(a.fecha_atencion) AS fecha_atencion_date, "
                "       a.motivo_consulta, c.contingencia, c.observacion, "
                "       c.lk_atencion "
                "FROM certificado c "
                "JOIN atencion a ON a.id_atencion = c.lk_atencion "
                "WHERE a.lk_paciente = :lk "
                "ORDER BY a.fecha_atencion DESC"
            ), {"lk": lk_pac}).mappings().all()
            self.cert_lista = [
                {
                    "id_certificado":   r["id_certificado"],
                    "fecha_atencion":   str(r["fecha_atencion_fmt"]),
                    "fecha_date":       str(r["fecha_atencion_date"]),
                    "motivo_consulta":  str(r["motivo_consulta"] or ""),
                    "contingencia":     str(r["contingencia"] or ""),
                    "observacion":      str(r["observacion"] or ""),
                    "lk_atencion":      r["lk_atencion"],
                }
                for r in rows
            ]

    def cert_abrir_editar(self, id_cert: int):
        from datetime import date as _date
        hoy = str(_date.today())
        for c in self.cert_lista:
            if c["id_certificado"] == id_cert:
                if c["fecha_date"] != hoy:
                    return   # No se puede editar fuera del día de atención
                self.cert_edit_id          = id_cert
                self.cert_id_atencion      = c["lk_atencion"]
                self._cert_reset_form()
                # Recargar valores actuales desde DB
                with Session(get_engine()) as s:
                    r = s.get(Certificado, id_cert)
                    if r:
                        self.cert_reposo_desde      = str(r.reposo_desde)
                        self.cert_reposo_hasta      = str(r.reposo_hasta)
                        self.cert_dias_reposo       = (r.reposo_hasta - r.reposo_desde).days + 1
                        self.cert_contingencia      = r.contingencia or ""
                        self.cert_presenta_sintomas = bool(r.presenta_sintomas)
                        self.cert_aislamiento       = bool(r.aislamiento)
                        self.cert_ocupacion         = r.ocupacion or ""
                        self.cert_lugar_trabajo     = r.lugar_trabajo or ""
                        self.cert_observacion       = r.observacion or ""
                self.cert_dlg_editar = True
                break

    def cert_imprimir_desde_lista(self, lk_atencion: int):
        self.cert_id_atencion = lk_atencion


class ConfigReportesState(State):
    # ── Listas ─────────────────────────────────────────────────────────────────
    cr_reportes:      list[CrReporteItem]  = []
    cr_secciones:     list[CrSeccionItem]  = []
    cr_celdas:        list[CrCeldaItem]    = []
    cr_imagenes:      list[CrImagenItem]   = []
    cr_archivos_img:  list[str]            = []
    cr_fuentes:       list[str]            = _FUENTES_REPORTES

    # ── Selección activa ────────────────────────────────────────────────────────
    cr_reporte_id: int = 0
    cr_seccion_id: int = 0

    # ── Edición Bloque 1 (diálogo) ──────────────────────────────────────────────
    cr_edit_r_id:     int  = 0
    cr_edit_r_nombre: str  = ""
    cr_edit_r_explica: str = ""
    cr_edit_r_fuente:  str = "Arial Narrow"
    cr_dlg_edit_r:    bool = False

    # ── Edición Bloque 2 (diálogo) ─────────────────────────────────────────────
    cr_edit_s_id:          int  = 0
    cr_edit_s_orden:       int  = 1
    cr_edit_s_explica:     str  = ""
    cr_edit_s_params:      list[str] = []
    cr_edit_s_param_input: str  = ""
    cr_dlg_edit_s:         bool = False
    # Opciones avanzadas — editar sección
    cr_edit_s_modo_bucle:    str = "N"
    cr_edit_s_paso_fila:     int = 1
    cr_edit_s_max_iter:      int = 10
    cr_edit_s_ancla_id:      int = 0
    cr_edit_s_ancla_gap:     int = 0
    cr_edit_s_cond_activa:   str = ""
    cr_edit_s_campo_grupo:   str = ""
    cr_edit_s_num_columnas:  int = 1
    cr_edit_s_paso_columna:  int = 0
    cr_edit_s_slot_height:   int = 10
    cr_edit_s_titulo:        str = ""

    # SQL mostrado/editado bajo la tabla de secciones
    cr_sql_display: str = ""
    cr_sql_edit:    str = ""

    # ── Diálogo Nuevo Reporte ───────────────────────────────────────────────────
    cr_dlg_nuevo_r:  bool = False
    cr_nr_nombre:    str  = ""
    cr_nr_explica:   str  = ""
    cr_nr_fuente:    str  = "Arial Narrow"

    # ── Diálogo Nueva Sección ───────────────────────────────────────────────────
    cr_dlg_nueva_s:      bool      = False
    cr_ns_orden:         int       = 1
    cr_ns_explica:       str       = ""
    cr_ns_sql:           str       = ""
    cr_ns_params:        list[str] = []
    cr_ns_param_input:   str       = ""
    # Opciones avanzadas — nueva sección
    cr_ns_modo_bucle:    str       = "N"
    cr_ns_paso_fila:     int       = 1
    cr_ns_max_iter:      int       = 10
    cr_ns_ancla_id:      int       = 0
    cr_ns_ancla_gap:     int       = 0
    cr_ns_cond_activa:   str       = ""
    cr_ns_campo_grupo:   str       = ""
    cr_ns_num_columnas:  int       = 1
    cr_ns_paso_columna:  int       = 0
    cr_ns_slot_height:   int       = 10
    cr_ns_titulo:        str       = ""

    # ── Diálogo Nueva Imagen (Bloque 4) ────────────────────────────────────────
    cr_dlg_nueva_img: bool = False
    cr_ni_archivo:    str  = ""
    cr_ni_celda:      str  = ""
    cr_ni_ancho:      int  = 100
    cr_ni_alto:       int  = 40
    cr_ni_orden:      int  = 1

    # ── Diálogo Editar Imagen (Bloque 4) ────────────────────────────────────────
    cr_dlg_edit_img:  bool = False
    cr_ei_id:         int  = 0
    cr_ei_archivo:    str  = ""
    cr_ei_celda:      str  = ""
    cr_ei_ancho:      int  = 100
    cr_ei_alto:       int  = 40
    cr_ei_orden:      int  = 1

    # ── Diálogo Nueva Celda ─────────────────────────────────────────────────────
    cr_dlg_nueva_c:   bool = False
    cr_nc_variable:   str  = ""
    cr_nc_celda_ref:  str  = ""
    cr_nc_fila:       int  = 1
    cr_nc_columna:    int  = 1
    cr_nc_explica:    str  = ""
    cr_dlg_aviso_c:   bool = False

    # ── Confirmación borrar ─────────────────────────────────────────────────────
    cr_dlg_borrar:    bool = False
    cr_borrar_tipo:   str  = ""
    cr_borrar_id:     int  = 0
    cr_borrar_nombre: str  = ""

    # ── Editor formato celda (Bloque 3) ─────────────────────────────────────────
    cr_celda_sel_id:   int  = 0   # fila seleccionada (lectura)
    cr_celda_edit_id:  int  = 0   # fila en modo edición
    cr_fmt_size:       int  = 9
    cr_fmt_merge_h:    int  = 1
    cr_fmt_merge_v:    int  = 1
    cr_fmt_sombra:     int  = 0
    cr_fmt_efecto:     str  = "N"   # N B S Q
    cr_fmt_alin_h:     str  = "L"   # L C R
    cr_fmt_alin_v:     str  = "U"   # U C D
    cr_fmt_borde_t:    bool = False
    cr_fmt_borde_r:    bool = False
    cr_fmt_borde_b:    bool = False
    cr_fmt_borde_l:    bool = False
    cr_fmt_fila:       int  = 1
    cr_fmt_columna:    int  = 1
    cr_fmt_variable:   str  = ""
    cr_fmt_explica:    str  = ""
    cr_fmt_pre_fijo:   str  = ""
    cr_fmt_post_fijo:  str  = ""
    cr_fmt_en_letras:  bool = False
    cr_fmt_tipo_celda: str  = "D"

    # ── Clonar sección (Bloque 2) ───────────────────────────────────────────────
    cr_dlg_clonar_s:   bool = False
    cr_clonar_dest_id: int  = 0

    # ── Pegar formato (Bloque 3) ────────────────────────────────────────────────
    cr_dlg_pegar_fmt:     bool = False
    cr_pegar_fmt_id:      int  = 0
    cr_pegar_fmt_explica: str  = ""
    cr_pegar_fmt_string:  str  = ""

    # ── Setters explícitos ──────────────────────────────────────────────────────
    # Bloque 1
    def set_cr_edit_r_nombre(self, v: str):  self.cr_edit_r_nombre  = v
    def set_cr_edit_r_explica(self, v: str): self.cr_edit_r_explica = v
    def set_cr_edit_r_fuente(self, v: str):  self.cr_edit_r_fuente  = v
    def set_cr_dlg_edit_r(self, v: bool):    self.cr_dlg_edit_r     = v
    def set_cr_nr_nombre(self, v: str):      self.cr_nr_nombre      = v
    def set_cr_nr_explica(self, v: str):     self.cr_nr_explica     = v
    def set_cr_nr_fuente(self, v: str):      self.cr_nr_fuente      = v
    def set_cr_dlg_nuevo_r(self, v: bool):   self.cr_dlg_nuevo_r    = v
    # Bloque 2
    def set_cr_edit_s_explica(self, v: str):     self.cr_edit_s_explica     = v
    def set_cr_edit_s_param_input(self, v: str): self.cr_edit_s_param_input = v
    def set_cr_edit_s_orden(self, v: str):
        try: self.cr_edit_s_orden = int(v)
        except ValueError: pass
    def set_cr_sql_edit(self, v: str):       self.cr_sql_edit       = v
    def set_cr_dlg_edit_s(self, v: bool):    self.cr_dlg_edit_s     = v
    def set_cr_ns_explica(self, v: str):     self.cr_ns_explica     = v
    def set_cr_ns_sql(self, v: str):         self.cr_ns_sql         = v
    def set_cr_ns_param_input(self, v: str): self.cr_ns_param_input = v
    def set_cr_ns_orden(self, v: str):
        try: self.cr_ns_orden = int(v)
        except ValueError: pass
    def set_cr_dlg_nueva_s(self, v: bool):   self.cr_dlg_nueva_s    = v
    # Avanzados editar sección
    def set_cr_edit_s_modo_bucle(self, v: str):   self.cr_edit_s_modo_bucle   = v
    def set_cr_edit_s_campo_grupo(self, v: str):  self.cr_edit_s_campo_grupo  = v
    def set_cr_edit_s_cond_activa(self, v: str):  self.cr_edit_s_cond_activa  = v
    def set_cr_edit_s_paso_fila(self, v: str):
        try: self.cr_edit_s_paso_fila = int(v)
        except ValueError: pass
    def set_cr_edit_s_max_iter(self, v: str):
        try: self.cr_edit_s_max_iter = int(v)
        except ValueError: pass
    def set_cr_edit_s_ancla_id(self, v: str):
        try: self.cr_edit_s_ancla_id = int(v)
        except (ValueError, TypeError): self.cr_edit_s_ancla_id = 0
    def set_cr_edit_s_ancla_gap(self, v: str):
        try: self.cr_edit_s_ancla_gap = int(v)
        except ValueError: pass
    def set_cr_edit_s_num_columnas(self, v: str):
        try: self.cr_edit_s_num_columnas = int(v)
        except ValueError: pass
    def set_cr_edit_s_paso_columna(self, v: str):
        try: self.cr_edit_s_paso_columna = int(v)
        except ValueError: pass
    def set_cr_edit_s_slot_height(self, v: str):
        try: self.cr_edit_s_slot_height = int(v)
        except ValueError: pass
    def set_cr_edit_s_titulo(self, v: str):   self.cr_edit_s_titulo   = v
    # Avanzados nueva sección
    def set_cr_ns_modo_bucle(self, v: str):   self.cr_ns_modo_bucle   = v
    def set_cr_ns_campo_grupo(self, v: str):  self.cr_ns_campo_grupo  = v
    def set_cr_ns_cond_activa(self, v: str):  self.cr_ns_cond_activa  = v
    def set_cr_ns_paso_fila(self, v: str):
        try: self.cr_ns_paso_fila = int(v)
        except ValueError: pass
    def set_cr_ns_max_iter(self, v: str):
        try: self.cr_ns_max_iter = int(v)
        except ValueError: pass
    def set_cr_ns_ancla_id(self, v: str):
        try: self.cr_ns_ancla_id = int(v)
        except (ValueError, TypeError): self.cr_ns_ancla_id = 0
    def set_cr_ns_ancla_gap(self, v: str):
        try: self.cr_ns_ancla_gap = int(v)
        except ValueError: pass
    def set_cr_ns_num_columnas(self, v: str):
        try: self.cr_ns_num_columnas = int(v)
        except ValueError: pass
    def set_cr_ns_paso_columna(self, v: str):
        try: self.cr_ns_paso_columna = int(v)
        except ValueError: pass
    def set_cr_ns_slot_height(self, v: str):
        try: self.cr_ns_slot_height = int(v)
        except ValueError: pass
    def set_cr_ns_titulo(self, v: str):       self.cr_ns_titulo       = v
    # Bloque 4 — imagen
    def set_cr_dlg_nueva_img(self, v: bool): self.cr_dlg_nueva_img = v
    def set_cr_ni_archivo(self, v: str):     self.cr_ni_archivo    = v
    def set_cr_ni_celda(self, v: str):       self.cr_ni_celda      = v.upper()
    def set_cr_ni_ancho(self, v: str):
        try: self.cr_ni_ancho = max(10, int(v))
        except ValueError: pass
    def set_cr_ni_alto(self, v: str):
        try: self.cr_ni_alto = max(10, int(v))
        except ValueError: pass
    def set_cr_ni_orden(self, v: str):
        try: self.cr_ni_orden = max(1, int(v))
        except ValueError: pass
    def set_cr_dlg_edit_img(self, v: bool): self.cr_dlg_edit_img = v
    def set_cr_ei_archivo(self, v: str):    self.cr_ei_archivo   = v
    def set_cr_ei_celda(self, v: str):      self.cr_ei_celda     = v.upper()
    def set_cr_ei_ancho(self, v: str):
        try: self.cr_ei_ancho = max(10, int(v))
        except ValueError: pass
    def set_cr_ei_alto(self, v: str):
        try: self.cr_ei_alto = max(10, int(v))
        except ValueError: pass
    def set_cr_ei_orden(self, v: str):
        try: self.cr_ei_orden = max(1, int(v))
        except ValueError: pass
    # Bloque 3
    def set_cr_nc_variable(self, v: str):  self.cr_nc_variable = v
    def set_cr_nc_explica(self, v: str):   self.cr_nc_explica  = v
    def set_cr_nc_celda_ref(self, v: str):
        self.cr_nc_celda_ref = v.upper()
        letters = ""
        digits  = ""
        for ch in v.upper():
            if ch.isalpha() and not digits:
                letters += ch
            elif ch.isdigit():
                digits += ch
        if letters:
            n = 0
            for ch in letters:
                n = n * 26 + (ord(ch) - ord("A") + 1)
            if n > 0:
                self.cr_nc_columna = n
        if digits:
            try:
                f = int(digits)
                if f > 0:
                    self.cr_nc_fila = f
            except ValueError:
                pass
    def set_cr_dlg_nueva_c(self, v: bool):  self.cr_dlg_nueva_c = v
    def set_cr_dlg_aviso_c(self, v: bool):  self.cr_dlg_aviso_c = v
    # Formato celda
    def set_cr_fmt_variable(self, v: str):   self.cr_fmt_variable  = v
    def set_cr_fmt_explica(self, v: str):    self.cr_fmt_explica   = v
    def set_cr_fmt_en_letras(self, v: bool): self.cr_fmt_en_letras  = v
    def set_cr_fmt_tipo_celda(self, v: str): self.cr_fmt_tipo_celda = v
    def set_cr_fmt_pre_fijo(self, v: str):   self.cr_fmt_pre_fijo  = v
    def set_cr_fmt_post_fijo(self, v: str):  self.cr_fmt_post_fijo = v
    def set_cr_fmt_efecto(self, v: str):    self.cr_fmt_efecto   = v
    def set_cr_fmt_alin_h(self, v: str):    self.cr_fmt_alin_h   = v
    def set_cr_fmt_alin_v(self, v: str):    self.cr_fmt_alin_v   = v
    def set_cr_fmt_borde_t(self, v: bool):  self.cr_fmt_borde_t  = v
    def set_cr_fmt_borde_r(self, v: bool):  self.cr_fmt_borde_r  = v
    def set_cr_fmt_borde_b(self, v: bool):  self.cr_fmt_borde_b  = v
    def set_cr_fmt_borde_l(self, v: bool):  self.cr_fmt_borde_l  = v
    def set_cr_fmt_size(self, v):
        self.cr_fmt_size = int(v[0]) if isinstance(v, (list, tuple)) else int(v)
    def set_cr_fmt_sombra(self, v):
        self.cr_fmt_sombra = int(v[0]) if isinstance(v, (list, tuple)) else int(v)
    def set_cr_fmt_fila(self, v: str):
        try: self.cr_fmt_fila = int(v)
        except ValueError: pass
    def set_cr_fmt_columna(self, v: str):
        # Convierte letras de columna (A, B, Z, AA, AB…) al entero equivalente
        v = v.strip().upper()
        if not v:
            return
        n = 0
        for ch in v:
            if "A" <= ch <= "Z":
                n = n * 26 + (ord(ch) - ord("A") + 1)
            else:
                return   # carácter inválido, ignorar
        if n > 0:
            self.cr_fmt_columna = n
    # Diálogo borrar
    def set_cr_dlg_borrar(self, v: bool):   self.cr_dlg_borrar   = v
    # Clonar sección
    def set_cr_dlg_clonar_s(self, v: bool): self.cr_dlg_clonar_s = v
    def set_cr_clonar_dest_id(self, v: str):
        try:    self.cr_clonar_dest_id = int(v)
        except (ValueError, TypeError): self.cr_clonar_dest_id = 0
    # Pegar formato
    def set_cr_dlg_pegar_fmt(self, v: bool):    self.cr_dlg_pegar_fmt    = v
    def set_cr_pegar_fmt_string(self, v: str):  self.cr_pegar_fmt_string = v

    # ── Computed vars ───────────────────────────────────────────────────────────
    @rx.var
    def cr_col_letra(self) -> str:
        n = self.cr_fmt_columna
        result = ""
        while n > 0:
            n, r = divmod(n - 1, 26)
            result = chr(65 + r) + result
        return result or "A"

    @rx.var
    def cr_merge_grid(self) -> list[list[dict]]:
        rows = []
        for r in range(1, 16):
            row_data = []
            for c in range(1, 26):
                row_data.append({
                    "r": r, "c": c,
                    "sel": (r <= self.cr_fmt_merge_v) and (c <= self.cr_fmt_merge_h),
                })
            rows.append(row_data)
        return rows

    @rx.var
    def cr_preview_bg(self) -> str:
        if self.cr_fmt_sombra == 0:
            return "white"
        g = int((1 - self.cr_fmt_sombra / 100) * 255)
        return f"#{g:02X}{g:02X}{g:02X}"

    @rx.var
    def cr_preview_fw(self) -> str:
        return "bold" if self.cr_fmt_efecto == "B" else "normal"

    @rx.var
    def cr_preview_fs(self) -> str:
        return "italic" if self.cr_fmt_efecto == "Q" else "normal"

    @rx.var
    def cr_preview_td(self) -> str:
        return "underline" if self.cr_fmt_efecto == "S" else "none"

    @rx.var
    def cr_preview_ah(self) -> str:
        return {"L": "left", "C": "center", "R": "right"}.get(self.cr_fmt_alin_h, "left")

    @rx.var
    def cr_fmt_size_list(self) -> list[int]:
        return [self.cr_fmt_size]

    @rx.var
    def cr_fmt_sombra_list(self) -> list[int]:
        return [self.cr_fmt_sombra]

    @rx.var
    def cr_fmt_string(self) -> str:
        brd = (
            ("1" if self.cr_fmt_borde_t else "0") +
            ("1" if self.cr_fmt_borde_r else "0") +
            ("1" if self.cr_fmt_borde_b else "0") +
            ("1" if self.cr_fmt_borde_l else "0")
        )
        nl = "T" if self.cr_fmt_en_letras else "N"
        return (
            f"{self.cr_fmt_size:02d}.{self.cr_fmt_merge_h:02d}.{self.cr_fmt_merge_v:02d}"
            f".{self.cr_fmt_sombra:02d}.{self.cr_fmt_efecto}{self.cr_fmt_alin_h}{self.cr_fmt_alin_v}.{brd}.{nl}"
        )

    @rx.var
    def cr_ancla_opciones(self) -> list[CrSeccionItem]:
        """Secciones disponibles como ancla (excluye la que se está editando)."""
        excluir = self.cr_edit_s_id or 0
        return [s for s in self.cr_secciones if s.id != excluir]

    @rx.var
    def cr_clonar_opciones(self) -> list[CrSeccionItem]:
        return [s for s in self.cr_secciones if s.id != self.cr_seccion_id]

    @rx.var
    def cr_pegar_fmt_len(self) -> int:
        return len(self.cr_pegar_fmt_string)

    @rx.var
    def cr_pegar_fmt_valido(self) -> bool:
        return len(self.cr_pegar_fmt_string) == 22

    # ── Carga inicial ───────────────────────────────────────────────────────────
    def cr_cargar_reportes(self):
        from pathlib import Path as _Path
        _tpl = _Path(__file__).parent / "templates"
        self.cr_archivos_img = sorted(
            p.name for p in _tpl.glob("*.png")
        ) + sorted(
            p.name for p in _tpl.glob("*.jpg")
        ) + sorted(
            p.name for p in _tpl.glob("*.jpeg")
        )
        with Session(get_engine()) as s:
            rows = s.exec(
                select(ReporteImpreso).order_by(ReporteImpreso.nombre_reporte)
            ).all()
            self.cr_reportes = [
                CrReporteItem(id=r.id_impreso, nombre=r.nombre_reporte,
                              explica=r.explica, fuente=r.nombre_fuente)
                for r in rows
            ]

    def cr_seleccionar_reporte(self, id_impreso: int):
        self.cr_reporte_id  = id_impreso
        self.cr_seccion_id    = 0
        self.cr_celdas        = []
        self.cr_sql_display   = ""
        self.cr_edit_s_id     = 0
        self.cr_celda_sel_id  = 0
        self.cr_celda_edit_id = 0
        self._cr_cargar_secciones()
        self.cr_cargar_imagenes()

    def _cr_cargar_secciones(self):
        with Session(get_engine()) as s:
            rows = s.exec(
                select(ReporteSeccion)
                .where(ReporteSeccion.lk_impreso == self.cr_reporte_id)
                .order_by(ReporteSeccion.orden)
            ).all()
            self.cr_secciones = [
                CrSeccionItem(
                    id=r.id_seccion, orden=r.orden, explica=r.explica,
                    sql=r.instruccion_sql or "",
                    params=r.parametros_in or [], activa=r.es_activa,
                    modo_bucle=r.modo_bucle or "N",
                    paso_fila=r.paso_fila, max_iteraciones=r.max_iteraciones,
                    lk_seccion_ancla=r.lk_seccion_ancla or 0,
                    ancla_gap=r.ancla_gap,
                    condicion_activa_sql=r.condicion_activa_sql or "",
                    campo_grupo=r.campo_grupo or "",
                    num_columnas=r.num_columnas, paso_columna=r.paso_columna,
                    slot_height=r.slot_height,
                    titulo_seccion=r.titulo_seccion or "",
                )
                for r in rows
            ]

    def cr_seleccionar_seccion(self, id_seccion: int):
        self.cr_seccion_id    = id_seccion
        self.cr_celda_sel_id  = 0
        self.cr_celda_edit_id = 0
        for sec in self.cr_secciones:
            if sec.id == id_seccion:
                self.cr_sql_display = sec.sql
                break
        self._cr_cargar_celdas()

    def _cr_cargar_celdas(self):
        with Session(get_engine()) as s:
            rows = s.exec(
                select(ReporteCelda)
                .where(ReporteCelda.lk_seccion == self.cr_seccion_id)
                .order_by(ReporteCelda.fila, ReporteCelda.columna)
            ).all()
            self.cr_celdas = [
                CrCeldaItem(id=r.id_celda, variable=r.variable or "",
                            fila=r.fila, columna=r.columna,
                            celda_ref=f"{_int_a_letra(r.columna)}{r.fila}",
                            explica=r.explica, formato=r.formato, activa=r.es_activa,
                            pre_fijo=r.pre_fijo or "", post_fijo=r.post_fijo or "",
                            en_letras=1 if r.formato.endswith(".T") else 0,
                            tipo_celda=r.tipo_celda or "D")
                for r in rows
            ]

    # ── CRUD Bloque 1: Reportes ─────────────────────────────────────────────────
    def cr_iniciar_edicion_r(self, id_impreso: int):
        for row in self.cr_reportes:
            if row.id == id_impreso:
                self.cr_edit_r_id      = id_impreso
                self.cr_edit_r_nombre  = row.nombre
                self.cr_edit_r_explica = row.explica
                self.cr_edit_r_fuente  = row.fuente
                self.cr_dlg_edit_r     = True
                break

    def cr_cancelar_edicion_r(self):
        self.cr_dlg_edit_r = False
        self.cr_edit_r_id  = 0

    def cr_guardar_r(self):
        if not self.cr_edit_r_id:
            return
        with Session(get_engine()) as s:
            r = s.get(ReporteImpreso, self.cr_edit_r_id)
            if r:
                r.nombre_reporte = self.cr_edit_r_nombre.strip()
                r.explica        = self.cr_edit_r_explica.strip()
                r.nombre_fuente  = self.cr_edit_r_fuente
                s.add(r); s.commit()
        self.cr_dlg_edit_r = False
        self.cr_edit_r_id  = 0
        self.cr_cargar_reportes()

    def cr_abrir_dlg_nuevo_r(self):
        self.cr_nr_nombre  = ""
        self.cr_nr_explica = ""
        self.cr_nr_fuente  = "Arial Narrow"
        self.cr_dlg_nuevo_r = True

    def cr_crear_r(self):
        if not self.cr_nr_nombre.strip():
            return
        with Session(get_engine()) as s:
            s.add(ReporteImpreso(
                nombre_reporte=self.cr_nr_nombre.strip(),
                explica=self.cr_nr_explica.strip(),
                nombre_fuente=self.cr_nr_fuente,
            )); s.commit()
        self.cr_dlg_nuevo_r = False
        self.cr_cargar_reportes()

    # ── CRUD Bloque 2: Secciones ────────────────────────────────────────────────
    def cr_iniciar_edicion_s(self, id_seccion: int):
        for row in self.cr_secciones:
            if row.id == id_seccion:
                self.cr_edit_s_id            = id_seccion
                self.cr_edit_s_orden         = row.orden
                self.cr_edit_s_explica       = row.explica
                self.cr_edit_s_params        = list(row.params)
                self.cr_edit_s_param_input   = ""
                self.cr_sql_edit             = row.sql
                self.cr_seccion_id           = id_seccion
                self.cr_sql_display          = row.sql
                self.cr_edit_s_modo_bucle    = row.modo_bucle
                self.cr_edit_s_paso_fila     = row.paso_fila
                self.cr_edit_s_max_iter      = row.max_iteraciones
                self.cr_edit_s_ancla_id      = row.lk_seccion_ancla
                self.cr_edit_s_ancla_gap     = row.ancla_gap
                self.cr_edit_s_cond_activa   = row.condicion_activa_sql
                self.cr_edit_s_campo_grupo   = row.campo_grupo
                self.cr_edit_s_num_columnas  = row.num_columnas
                self.cr_edit_s_paso_columna  = row.paso_columna
                self.cr_edit_s_slot_height   = row.slot_height
                self.cr_edit_s_titulo        = row.titulo_seccion
                self.cr_dlg_edit_s           = True
                break

    def cr_cancelar_edicion_s(self):
        self.cr_dlg_edit_s = False
        self.cr_edit_s_id  = 0

    def cr_guardar_s(self):
        if not self.cr_edit_s_id:
            return
        with Session(get_engine()) as s:
            sec = s.get(ReporteSeccion, self.cr_edit_s_id)
            if sec:
                sec.orden                = self.cr_edit_s_orden
                sec.explica              = self.cr_edit_s_explica.strip()
                sec.instruccion_sql      = self.cr_sql_edit.strip() or None
                sec.parametros_in        = self.cr_edit_s_params or None
                sec.modo_bucle           = self.cr_edit_s_modo_bucle
                sec.paso_fila            = self.cr_edit_s_paso_fila
                sec.max_iteraciones      = self.cr_edit_s_max_iter
                sec.lk_seccion_ancla     = self.cr_edit_s_ancla_id or None
                sec.ancla_gap            = self.cr_edit_s_ancla_gap
                sec.condicion_activa_sql = self.cr_edit_s_cond_activa.strip() or None
                sec.campo_grupo          = self.cr_edit_s_campo_grupo.strip() or None
                sec.num_columnas         = self.cr_edit_s_num_columnas
                sec.paso_columna         = self.cr_edit_s_paso_columna
                sec.slot_height          = self.cr_edit_s_slot_height
                sec.titulo_seccion       = self.cr_edit_s_titulo.strip() or None
                s.add(sec); s.commit()
        self.cr_sql_display = self.cr_sql_edit
        self.cr_dlg_edit_s  = False
        self.cr_edit_s_id   = 0
        self._cr_cargar_secciones()

    def cr_edit_s_add_param(self):
        p = self.cr_edit_s_param_input.strip()
        if p and p not in self.cr_edit_s_params:
            self.cr_edit_s_params = self.cr_edit_s_params + [p]
        self.cr_edit_s_param_input = ""

    def cr_edit_s_del_param(self, p: str):
        self.cr_edit_s_params = [x for x in self.cr_edit_s_params if x != p]

    def cr_abrir_dlg_nueva_s(self):
        if not self.cr_reporte_id:
            return
        self.cr_ns_orden         = len(self.cr_secciones) + 1
        self.cr_ns_explica       = ""
        self.cr_ns_sql           = ""
        self.cr_ns_params        = []
        self.cr_ns_param_input   = ""
        self.cr_ns_modo_bucle    = "N"
        self.cr_ns_paso_fila     = 1
        self.cr_ns_max_iter      = 10
        self.cr_ns_ancla_id      = 0
        self.cr_ns_ancla_gap     = 0
        self.cr_ns_cond_activa   = ""
        self.cr_ns_campo_grupo   = ""
        self.cr_ns_num_columnas  = 1
        self.cr_ns_paso_columna  = 0
        self.cr_ns_slot_height   = 10
        self.cr_ns_titulo        = ""
        self.cr_dlg_nueva_s      = True

    def cr_crear_s(self):
        with Session(get_engine()) as s:
            s.add(ReporteSeccion(
                lk_impreso           = self.cr_reporte_id,
                orden                = self.cr_ns_orden,
                explica              = self.cr_ns_explica.strip(),
                instruccion_sql      = self.cr_ns_sql.strip() or None,
                parametros_in        = self.cr_ns_params or None,
                modo_bucle           = self.cr_ns_modo_bucle,
                paso_fila            = self.cr_ns_paso_fila,
                max_iteraciones      = self.cr_ns_max_iter,
                lk_seccion_ancla     = self.cr_ns_ancla_id or None,
                ancla_gap            = self.cr_ns_ancla_gap,
                condicion_activa_sql = self.cr_ns_cond_activa.strip() or None,
                campo_grupo          = self.cr_ns_campo_grupo.strip() or None,
                num_columnas         = self.cr_ns_num_columnas,
                paso_columna         = self.cr_ns_paso_columna,
                slot_height          = self.cr_ns_slot_height,
                titulo_seccion       = self.cr_ns_titulo.strip() or None,
            )); s.commit()
        self.cr_dlg_nueva_s = False
        self._cr_cargar_secciones()

    def cr_ns_add_param(self):
        p = self.cr_ns_param_input.strip()
        if p and p not in self.cr_ns_params:
            self.cr_ns_params = self.cr_ns_params + [p]
        self.cr_ns_param_input = ""

    def cr_ns_del_param(self, p: str):
        self.cr_ns_params = [x for x in self.cr_ns_params if x != p]

    # ── CRUD Bloque 3: Celdas ───────────────────────────────────────────────────
    def cr_abrir_dlg_nueva_c(self):
        if not self.cr_seccion_id:
            return
        self.cr_nc_variable  = ""
        self.cr_nc_celda_ref = ""
        self.cr_nc_fila      = 1
        self.cr_nc_columna   = 1
        self.cr_nc_explica   = ""
        self.cr_dlg_nueva_c = True

    def cr_crear_c(self):
        with Session(get_engine()) as s:
            s.add(ReporteCelda(
                lk_seccion = self.cr_seccion_id,
                variable   = self.cr_nc_variable.strip() or None,
                fila       = self.cr_nc_fila,
                columna    = self.cr_nc_columna,
                explica    = self.cr_nc_explica.strip(),
            )); s.commit()
        self.cr_dlg_nueva_c  = False
        self.cr_dlg_aviso_c  = True
        self._cr_cargar_celdas()

    def cr_cerrar_aviso_c(self):
        self.cr_dlg_aviso_c = False

    def _cr_cargar_fmt(self, row) -> None:
        """Carga los campos de formato desde un CrCeldaItem a los cr_fmt_* vars."""
        self.cr_fmt_variable  = row.variable
        self.cr_fmt_explica   = row.explica
        self.cr_fmt_fila      = row.fila
        self.cr_fmt_columna   = row.columna
        self.cr_fmt_pre_fijo  = row.pre_fijo
        self.cr_fmt_post_fijo = row.post_fijo
        f = _parsear_formato(row.formato)
        self.cr_fmt_size    = f["size"]
        self.cr_fmt_merge_h = f["mh"]
        self.cr_fmt_merge_v = f["mv"]
        self.cr_fmt_sombra  = f["sombra"]
        self.cr_fmt_efecto  = f["efecto"]
        self.cr_fmt_alin_h  = f["ah"]
        self.cr_fmt_alin_v  = f["av"]
        self.cr_fmt_borde_t   = f["bt"]
        self.cr_fmt_borde_r   = f["br"]
        self.cr_fmt_borde_b   = f["bb"]
        self.cr_fmt_borde_l   = f["bl"]
        self.cr_fmt_en_letras  = f["en_letras"]
        self.cr_fmt_tipo_celda = row.tipo_celda

    def cr_seleccionar_c(self, id_celda: int):
        """Selecciona una celda para ver su formato en modo solo lectura."""
        self.cr_celda_edit_id = 0
        for row in self.cr_celdas:
            if row.id == id_celda:
                self.cr_celda_sel_id = id_celda
                self._cr_cargar_fmt(row)
                break

    def cr_iniciar_edicion_c(self, id_celda: int):
        for row in self.cr_celdas:
            if row.id == id_celda:
                self.cr_celda_sel_id  = id_celda
                self.cr_celda_edit_id = id_celda
                self._cr_cargar_fmt(row)
                break

    def cr_cancelar_edicion_c(self):
        self.cr_celda_edit_id = 0

    def cr_guardar_c(self):
        if not self.cr_celda_edit_id:
            return
        brd = (
            ("1" if self.cr_fmt_borde_t else "0") +
            ("1" if self.cr_fmt_borde_r else "0") +
            ("1" if self.cr_fmt_borde_b else "0") +
            ("1" if self.cr_fmt_borde_l else "0")
        )
        nl  = "T" if self.cr_fmt_en_letras else "N"
        fmt = (
            f"{self.cr_fmt_size:02d}.{self.cr_fmt_merge_h:02d}.{self.cr_fmt_merge_v:02d}"
            f".{self.cr_fmt_sombra:02d}.{self.cr_fmt_efecto}{self.cr_fmt_alin_h}{self.cr_fmt_alin_v}.{brd}.{nl}"
        )
        with Session(get_engine()) as s:
            c = s.get(ReporteCelda, self.cr_celda_edit_id)
            if c:
                c.formato    = fmt
                c.variable   = self.cr_fmt_variable.strip() or None
                c.fila       = self.cr_fmt_fila
                c.columna    = self.cr_fmt_columna
                c.explica    = self.cr_fmt_explica.strip()
                c.pre_fijo   = self.cr_fmt_pre_fijo
                c.post_fijo  = self.cr_fmt_post_fijo
                c.tipo_celda = self.cr_fmt_tipo_celda
                s.add(c); s.commit()
        self.cr_celda_edit_id = 0
        self._cr_cargar_celdas()

    def cr_set_merge(self, r: int, c: int):
        self.cr_fmt_merge_v = r
        self.cr_fmt_merge_h = c

    # ── Bloque 4: Imágenes ──────────────────────────────────────────────────────
    def cr_cargar_imagenes(self):
        if not self.cr_reporte_id:
            self.cr_imagenes = []
            return
        with Session(get_engine()) as s:
            rows = s.exec(
                select(ReporteImagen)
                .where(ReporteImagen.lk_impreso == self.cr_reporte_id)
                .order_by(ReporteImagen.orden)
            ).all()
            self.cr_imagenes = [
                CrImagenItem(
                    id=r.id_imagen, nombre_archivo=r.nombre_archivo,
                    celda=r.celda, ancho=r.ancho, alto=r.alto, orden=r.orden,
                )
                for r in rows
            ]

    def cr_abrir_dlg_nueva_img(self):
        self.cr_ni_archivo = self.cr_archivos_img[0] if self.cr_archivos_img else ""
        self.cr_ni_celda   = ""
        self.cr_ni_ancho   = 100
        self.cr_ni_alto    = 40
        self.cr_ni_orden   = len(self.cr_imagenes) + 1
        self.cr_dlg_nueva_img = True

    def cr_crear_img(self):
        if not self.cr_reporte_id or not self.cr_ni_celda.strip() or not self.cr_ni_archivo:
            return
        with Session(get_engine()) as s:
            s.add(ReporteImagen(
                lk_impreso=self.cr_reporte_id,
                nombre_archivo=self.cr_ni_archivo,
                celda=self.cr_ni_celda.strip().upper(),
                ancho=self.cr_ni_ancho,
                alto=self.cr_ni_alto,
                orden=self.cr_ni_orden,
            ))
            s.commit()
        self.cr_dlg_nueva_img = False
        self.cr_cargar_imagenes()

    def cr_iniciar_edicion_img(self, id_imagen: int):
        for img in self.cr_imagenes:
            if img.id == id_imagen:
                self.cr_ei_id      = img.id
                self.cr_ei_archivo = img.nombre_archivo
                self.cr_ei_celda   = img.celda
                self.cr_ei_ancho   = img.ancho
                self.cr_ei_alto    = img.alto
                self.cr_ei_orden   = img.orden
                break
        self.cr_dlg_edit_img = True

    def cr_guardar_edicion_img(self):
        if not self.cr_ei_celda.strip() or not self.cr_ei_archivo:
            return
        with Session(get_engine()) as s:
            r = s.get(ReporteImagen, self.cr_ei_id)
            if r:
                r.nombre_archivo = self.cr_ei_archivo
                r.celda          = self.cr_ei_celda.strip().upper()
                r.ancho          = self.cr_ei_ancho
                r.alto           = self.cr_ei_alto
                r.orden          = self.cr_ei_orden
                s.add(r); s.commit()
        self.cr_dlg_edit_img = False
        self.cr_cargar_imagenes()

    # ── Confirmación borrar (compartida) ────────────────────────────────────────
    def cr_confirmar_borrar(self, tipo: str, id_: int, nombre: str):
        self.cr_borrar_tipo   = tipo
        self.cr_borrar_id     = id_
        self.cr_borrar_nombre = nombre
        self.cr_dlg_borrar    = True

    def cr_ejecutar_borrar(self):
        self.cr_dlg_borrar = False
        tipo = self.cr_borrar_tipo
        bid  = self.cr_borrar_id
        if tipo == "reporte":
            with Session(get_engine()) as s:
                r = s.get(ReporteImpreso, bid)
                if r: s.delete(r); s.commit()
            if self.cr_reporte_id == bid:
                self.cr_reporte_id  = 0
                self.cr_secciones   = []
                self.cr_celdas      = []
                self.cr_sql_display = ""
            self.cr_cargar_reportes()
        elif tipo == "seccion":
            with Session(get_engine()) as s:
                celdas = s.exec(select(ReporteCelda).where(ReporteCelda.lk_seccion == bid)).all()
                for c in celdas:
                    s.delete(c)
                r = s.get(ReporteSeccion, bid)
                if r: s.delete(r)
                s.commit()
            if self.cr_seccion_id == bid:
                self.cr_seccion_id  = 0
                self.cr_celdas      = []
                self.cr_sql_display = ""
            self._cr_cargar_secciones()
        elif tipo == "celda":
            with Session(get_engine()) as s:
                r = s.get(ReporteCelda, bid)
                if r: s.delete(r); s.commit()
            if self.cr_celda_edit_id == bid:
                self.cr_celda_edit_id = 0
            if self.cr_celda_sel_id == bid:
                self.cr_celda_sel_id = 0
            self._cr_cargar_celdas()
        elif tipo == "imagen":
            with Session(get_engine()) as s:
                r = s.get(ReporteImagen, bid)
                if r: s.delete(r); s.commit()
            self.cr_cargar_imagenes()

    # ── Pegar formato ───────────────────────────────────────────────────────────
    def cr_abrir_dlg_pegar_fmt(self, id_celda: int):
        for c in self.cr_celdas:
            if c.id == id_celda:
                self.cr_pegar_fmt_explica = c.explica
                break
        self.cr_pegar_fmt_id     = id_celda
        self.cr_pegar_fmt_string = ""
        self.cr_dlg_pegar_fmt    = True

    def cr_aplicar_pegar_fmt(self):
        if len(self.cr_pegar_fmt_string) != 22:
            return
        with Session(get_engine()) as s:
            c = s.get(ReporteCelda, self.cr_pegar_fmt_id)
            if c:
                c.formato = self.cr_pegar_fmt_string
                s.add(c); s.commit()
        self.cr_dlg_pegar_fmt = False
        self.cr_pegar_fmt_id  = 0
        self._cr_cargar_celdas()

    # ── Clonar sección ──────────────────────────────────────────────────────────
    def cr_abrir_dlg_clonar_s(self):
        self.cr_clonar_dest_id = 0
        self.cr_dlg_clonar_s   = True

    def cr_ejecutar_clonar_s(self):
        if not self.cr_seccion_id or not self.cr_clonar_dest_id:
            return
        if self.cr_clonar_dest_id == self.cr_seccion_id:
            return
        origen_name  = ""
        destino_name = ""
        for s in self.cr_secciones:
            if s.id == self.cr_seccion_id:
                origen_name  = s.explica
            if s.id == self.cr_clonar_dest_id:
                destino_name = s.explica
        with Session(get_engine()) as s:
            celdas = s.exec(
                select(ReporteCelda).where(ReporteCelda.lk_seccion == self.cr_seccion_id)
            ).all()
            for c in celdas:
                nueva = ReporteCelda(
                    lk_seccion = self.cr_clonar_dest_id,
                    variable   = c.variable,
                    fila       = c.fila,
                    columna    = c.columna,
                    pre_fijo   = c.pre_fijo,
                    post_fijo  = c.post_fijo,
                    formato    = c.formato,
                    explica    = (c.explica or "") + "_Copia",
                    es_activa  = c.es_activa,
                )
                s.add(nueva)
            s.commit()
        self.cr_dlg_clonar_s   = False
        self.cr_clonar_dest_id = 0
        self._cr_cargar_celdas()
        yield rx.toast.error(
            f'Sección "{origen_name}" clonada hacia "{destino_name}"'
        )

    # ── Desplazar filas de celdas (Sube 1 / Baja 1) ────────────────────────────
    def cr_desplazar_celdas(self, delta: int):
        if not self.cr_seccion_id:
            return
        explica = ""
        for sec in self.cr_secciones:
            if sec.id == self.cr_seccion_id:
                explica = sec.explica
                break
        with Session(get_engine()) as s:
            celdas = s.exec(
                select(ReporteCelda).where(ReporteCelda.lk_seccion == self.cr_seccion_id)
            ).all()
            for c in celdas:
                c.fila = max(1, c.fila + delta)
                s.add(c)
            s.commit()
        self._cr_cargar_celdas()
        accion = "bajó" if delta > 0 else "subió"
        yield rx.toast.error(f'Se {accion} la sección "{explica}"')

    def cr_desplazar_columna(self, delta: int):
        if not self.cr_seccion_id:
            return
        explica = ""
        for sec in self.cr_secciones:
            if sec.id == self.cr_seccion_id:
                explica = sec.explica
                break
        with Session(get_engine()) as s:
            celdas = s.exec(
                select(ReporteCelda).where(ReporteCelda.lk_seccion == self.cr_seccion_id)
            ).all()
            for c in celdas:
                c.columna = max(1, c.columna + delta)
                s.add(c)
            s.commit()
        self._cr_cargar_celdas()
        accion = "derecha" if delta > 0 else "izquierda"
        yield rx.toast.error(f'Se desplazó a la {accion} la sección "{explica}"')


_AG_DURACIONES = [15, 30, 45, 60]

def _snap_duracion(mins: int) -> int:
    """Redondea al valor predefinido más cercano de la lista de duraciones."""
    return min(_AG_DURACIONES, key=lambda d: abs(d - mins))

_AG_COLOR_DEFAULT = "#3B82F6"
_AG_PALETA = [
    "#3B82F6",  # azul
    "#10B981",  # verde esmeralda
    "#F59E0B",  # ámbar
    "#EF4444",  # rojo
    "#8B5CF6",  # violeta
    "#EC4899",  # rosa
    "#06B6D4",  # cian
    "#F97316",  # naranja
]

# ══════════════════════════════════════════════════════════════════════════════
# AgendaState — Módulo de citas médicas
# ══════════════════════════════════════════════════════════════════════════════
class AgendaState(State):

    # ── Offcanvas principal ───────────────────────────────────────────────────
    ag_abierto:      bool       = False
    ag_citas:        list[dict] = []
    ag_medicos:      list[dict] = []   # cada item: {"id", "nombre", "color", "visible"}
    ag_tipos_cita:   list[dict] = []
    ag_seguros:      list[str]  = []

    # ── Dialog nueva cita ─────────────────────────────────────────────────────
    ag_dlg_nueva:        bool       = False
    ag_nc_inicio:        str        = ""
    ag_nc_fin:           str        = ""
    ag_nc_fecha_ini:     str        = ""
    ag_nc_hora_ini:      str        = ""
    ag_nc_lk_medico:     int        = 0
    ag_nc_lk_tipo:       int        = 0
    ag_nc_duracion:      int        = 30
    ag_nc_busq_px:       str        = ""
    ag_nc_resultados_px: list[dict] = []
    ag_nc_lk_paciente:   int        = 0     # 0 = paciente nuevo
    ag_nc_px_nombre:     str        = ""
    ag_nc_px_sexo:       str        = "Femenino"
    ag_nc_px_celular:    str        = ""
    ag_nc_px_ciudad:     str        = ""
    ag_nc_px_seguro:     str        = ""
    ag_nc_notas:         str        = ""
    ag_nc_error:         str        = ""

    # ── Dialog ver cita ───────────────────────────────────────────────────────
    ag_dlg_ver:          bool = False
    ag_ver_id:           int  = 0
    ag_ver_px:           str  = ""
    ag_ver_tipo:         str  = ""
    ag_ver_categoria:    str  = ""
    ag_ver_estado:       str  = ""
    ag_ver_medico:       str  = ""
    ag_ver_inicio:       str  = ""
    ag_ver_fin:          str  = ""
    ag_ver_fecha_ini:    str  = ""
    ag_ver_hora_ini:     str  = ""
    ag_ver_fecha_fin:    str  = ""
    ag_ver_hora_fin:     str  = ""
    ag_ver_duracion:     str  = ""
    ag_ver_notas:        str  = ""
    ag_ver_req_conf:     bool = False
    # IDs para pre-cargar selects de edición
    ag_ver_lk_medico:    int  = 0
    ag_ver_lk_tipo:      int  = 0
    # Modo edición
    ag_ver_editando:     bool = False
    ag_ed_lk_medico:     int  = 0
    ag_ed_lk_tipo:       int  = 0
    ag_ed_notas:         str  = ""
    ag_ed_error:         str  = ""

    # ── Setters simples ───────────────────────────────────────────────────────
    def set_ag_dlg_nueva(self, v: bool):        self.ag_dlg_nueva  = v
    def set_ag_dlg_ver(self, v: bool):          self.ag_dlg_ver    = v
    def set_ag_ed_lk_medico(self, v: str):     self.ag_ed_lk_medico = int(v) if v else 0
    def set_ag_ed_lk_tipo(self, v: str):       self.ag_ed_lk_tipo   = int(v) if v else 0
    def set_ag_ed_notas(self, v: str):         self.ag_ed_notas     = v
    def set_ag_nc_lk_medico(self, v: str):      self.ag_nc_lk_medico  = int(v) if v else 0
    def set_ag_nc_lk_tipo(self, v: str):
        from sqlmodel import Session
        self.ag_nc_lk_tipo = int(v) if v else 0
        if self.ag_nc_lk_tipo:
            with Session(get_engine()) as s:
                t = s.get(TipoCita, self.ag_nc_lk_tipo)
                if t and t.duracion_min:
                    self.ag_nc_duracion = _snap_duracion(t.duracion_min)
    def set_ag_nc_duracion(self, v: str):
        from datetime import datetime as _dt, timedelta
        mins = _snap_duracion(int(v)) if v and v.isdigit() else 30
        self.ag_nc_duracion = mins
        if self.ag_nc_inicio:
            ini = _dt.fromisoformat(self.ag_nc_inicio.replace("Z", ""))
            self.ag_nc_fin = (ini + timedelta(minutes=mins)).isoformat()
    def set_ag_nc_px_nombre(self, v: str):      self.ag_nc_px_nombre  = v
    def set_ag_nc_px_sexo(self, v: str):        self.ag_nc_px_sexo    = v
    def set_ag_nc_px_celular(self, v: str):     self.ag_nc_px_celular = v
    def set_ag_nc_px_ciudad(self, v: str):      self.ag_nc_px_ciudad  = v
    def set_ag_nc_px_seguro(self, v: str):      self.ag_nc_px_seguro  = "" if v == "__ninguno__" else v
    def set_ag_nc_notas(self, v: str):          self.ag_nc_notas      = v
    def set_ag_nc_busq_px(self, v: str):
        self.ag_nc_busq_px = v
        if len(v) >= 3:
            self._ag_buscar_pacientes(v)
        else:
            self.ag_nc_resultados_px = []

    # ── Apertura / cierre ─────────────────────────────────────────────────────
    def ag_abrir(self):
        self._ag_cargar_medicos()
        self._ag_cargar_tipos()
        self._ag_cargar_seguros()
        self._ag_cargar_citas()
        self.ag_abierto = True

    def ag_cerrar(self):
        self.ag_abierto = False

    def ag_toggle_medico(self, id_medico: int):
        self.ag_medicos = [
            {**m, "visible": not m.get("visible", True)} if m["id"] == id_medico else m
            for m in self.ag_medicos
        ]
        self._ag_cargar_citas()

    # ── Carga de datos ────────────────────────────────────────────────────────
    def _ag_cargar_medicos(self):
        with Session(get_engine()) as s:
            medicos = s.exec(
                select(Points).where(Points.estado == 1)
            ).all()
        self.ag_medicos = [
            {
                "id":      m.id_medico,
                "nombre":  m.nombre_medico,
                "color":   m.color_agenda if m.color_agenda != _AG_COLOR_DEFAULT
                           else _AG_PALETA[i % len(_AG_PALETA)],
                "visible": True,
            }
            for i, m in enumerate(medicos)
        ]

    def _ag_cargar_tipos(self):
        with Session(get_engine()) as s:
            tipos = s.exec(
                select(TipoCita).where(TipoCita.es_activo == 1)
                .order_by(TipoCita.categoria, TipoCita.nombre)
            ).all()
        self.ag_tipos_cita = [
            {
                "id":            t.id_tipo_cita,
                "nombre":        t.nombre,
                "categoria":     t.categoria,
                "duracion_min":  t.duracion_min or 0,
                "color":         t.color_hex,
                "requiere_conf": bool(t.requiere_conf),
            }
            for t in tipos
        ]

    def _ag_cargar_seguros(self):
        self.ag_seguros = list(carga_seguros())

    def _ag_cargar_citas(self):
        crypto = GesmedCrypto.para_medico(self.id_medico)
        visibles = [m["id"] for m in self.ag_medicos if m.get("visible", True)]
        if visibles and len(visibles) < len(self.ag_medicos):
            ids_str = ", ".join(str(v) for v in visibles)
            filtro_sql = f"AND c.lk_medico IN ({ids_str})"
        else:
            filtro_sql = ""
        params: dict = {}
        with Session(get_engine()) as s:
            rows = s.execute(text(f"""
                SELECT c.id_cita,
                       c.lk_paciente,
                       c.px_nombre,
                       t.nombre       AS tipo_nombre,
                       t.categoria,
                       m.nombre_medico,
                       m.color_agenda,
                       m.id_medico,
                       c.inicio, c.fin, c.estado,
                       c.notas,
                       p.nombre_completo AS px_enc,
                       t.requiere_conf,
                       c.lk_tipo_cita
                FROM cita c
                JOIN tipo_cita t ON t.id_tipo_cita = c.lk_tipo_cita
                JOIN points    m ON m.id_medico    = c.lk_medico
                LEFT JOIN paciente p ON p.nro_hclinica = c.lk_paciente
                WHERE c.estado NOT IN ('CANCELADA')
                {filtro_sql}
                ORDER BY c.inicio
            """), params).all()

        color_map = {m["id"]: m["color"] for m in self.ag_medicos}
        icono_estado = {
            "AGENDADA":   "◻️",
            "CONFIRMADA": "☑️",
        }
        eventos = []
        for r in rows:
            # Descifrar nombre del paciente registrado
            if r[1] and r[12]:
                try:
                    px_nombre = crypto.desencriptar(r[12])
                except Exception:
                    px_nombre = f"Paciente #{r[1]}"
            elif r[2]:
                px_nombre = r[2]
            else:
                px_nombre = "Paciente"

            icono = icono_estado.get(r[10], "")
            color = color_map.get(r[7], r[6] or _AG_COLOR_DEFAULT)
            eventos.append({
                "id":              str(r[0]),
                "title":           f"{icono} {px_nombre} · {r[3]}",
                "start":           r[8].isoformat(),
                "end":             r[9].isoformat(),
                "backgroundColor": color,
                "borderColor":     color,
                "extendedProps": {
                    "id_cita":       r[0],
                    "px_nombre":     px_nombre,
                    "tipo":          r[3],
                    "categoria":     r[4],
                    "estado":        r[10],
                    "medico":        r[5],
                    "id_medico":     r[7],
                    "lk_tipo_cita":  r[14],
                    "notas":         r[11] or "",
                    "requiere_conf": bool(r[13]),
                },
            })
        self.ag_citas = eventos

    def _ag_buscar_pacientes(self, filtro: str):
        resultados = consultar_pacientes_por_nombre(
            Session(get_engine()), filtro, self.id_medico, self.ve_solo_propios_pacientes
        )
        self.ag_nc_resultados_px = [
            {"id": r["nro_hclinica"], "nombre": r["nombre_completo"]}
            for r in resultados[:10]
        ]

    # ── Callbacks del calendario ──────────────────────────────────────────────
    def ag_handle_event_click(self, data: dict):
        from datetime import datetime as _dt

        def _fmt(iso: str):
            try:
                dt = _dt.fromisoformat(iso.replace("Z", ""))
                return dt.strftime("%d/%m/%Y"), dt.strftime("%H:%M")
            except Exception:
                return iso, ""

        self.ag_ver_id        = data.get("id_cita", 0)
        self.ag_ver_px        = data.get("px_nombre", "")
        self.ag_ver_tipo      = data.get("tipo", "")
        self.ag_ver_categoria = data.get("categoria", "")
        self.ag_ver_estado    = data.get("estado", "")
        self.ag_ver_medico    = data.get("medico", "")
        self.ag_ver_inicio    = data.get("start", "")
        self.ag_ver_fin       = data.get("end", "")
        self.ag_ver_notas     = data.get("notas", "")
        self.ag_ver_req_conf  = bool(data.get("requiere_conf", False))
        self.ag_ver_lk_medico = data.get("id_medico", 0)
        self.ag_ver_lk_tipo   = data.get("lk_tipo_cita", 0)
        self.ag_ver_editando  = False
        self.ag_ed_error      = ""
        self.ag_ver_fecha_ini, self.ag_ver_hora_ini = _fmt(self.ag_ver_inicio)
        self.ag_ver_fecha_fin, self.ag_ver_hora_fin = _fmt(self.ag_ver_fin)
        try:
            ini_dt = _dt.fromisoformat(self.ag_ver_inicio.replace("Z", ""))
            fin_dt = _dt.fromisoformat(self.ag_ver_fin.replace("Z", ""))
            if ini_dt.date() == fin_dt.date():
                mins = int((fin_dt - ini_dt).total_seconds() // 60)
                h, m = divmod(mins, 60)
                self.ag_ver_duracion = f"{h}h {m:02d}min" if h else f"{m} min"
            else:
                self.ag_ver_duracion = ""
        except Exception:
            self.ag_ver_duracion = ""
        self.ag_dlg_ver       = True

    def ag_handle_date_select(self, data: dict):
        from datetime import datetime as _dt
        self.ag_nc_inicio    = data.get("start", "")
        self.ag_nc_fin       = data.get("end", "")
        self.ag_nc_lk_medico = 0
        self.ag_nc_lk_tipo   = 0
        try:
            ini = _dt.fromisoformat(self.ag_nc_inicio.replace("Z", ""))
            fin = _dt.fromisoformat(self.ag_nc_fin.replace("Z", ""))
            self.ag_nc_fecha_ini = ini.strftime("%d/%m/%Y")
            self.ag_nc_hora_ini  = ini.strftime("%H:%M")
            self.ag_nc_duracion  = _snap_duracion(int((fin - ini).total_seconds() / 60))
        except Exception:
            self.ag_nc_fecha_ini = ""
            self.ag_nc_hora_ini  = ""
            self.ag_nc_duracion  = 30
        self.ag_nc_busq_px   = ""
        self.ag_nc_resultados_px = []
        self.ag_nc_lk_paciente   = 0
        self.ag_nc_px_nombre = ""
        self.ag_nc_px_sexo   = "Femenino"
        self.ag_nc_px_celular = ""
        self.ag_nc_px_ciudad = ""
        self.ag_nc_px_seguro = ""
        self.ag_nc_notas     = ""
        self.ag_nc_error     = ""
        self.ag_dlg_nueva    = True

    def ag_handle_event_drop(self, data: dict):
        id_cita = data.get("id_cita", 0)
        if not id_cita:
            return
        from datetime import datetime as _dt
        try:
            ini = _dt.fromisoformat(data["start"].replace("Z", ""))
            fin = _dt.fromisoformat(data["end"].replace("Z", ""))
            with Session(get_engine()) as s:
                cita = s.get(Cita, id_cita)
                if cita:
                    cita.inicio = ini
                    cita.fin    = fin
                    s.add(cita)
                    s.commit()
        except Exception:
            pass
        self._ag_cargar_citas()

    # ── Acciones sobre cita seleccionada ──────────────────────────────────────
    def ag_iniciar_edicion(self):
        self.ag_ed_lk_medico = self.ag_ver_lk_medico
        self.ag_ed_lk_tipo   = self.ag_ver_lk_tipo
        self.ag_ed_notas     = self.ag_ver_notas
        self.ag_ed_error     = ""
        self.ag_ver_editando = True

    def ag_cancelar_edicion(self):
        self.ag_ver_editando = False
        self.ag_ed_error     = ""

    def ag_guardar_edicion_cita(self):
        if not self.ag_ed_lk_medico or not self.ag_ed_lk_tipo:
            self.ag_ed_error = "Médico y tipo de cita son obligatorios."
            return
        with Session(get_engine()) as s:
            c = s.get(Cita, self.ag_ver_id)
            if not c:
                self.ag_ed_error = "No se encontró la cita."
                return
            c.lk_medico    = self.ag_ed_lk_medico
            c.lk_tipo_cita = self.ag_ed_lk_tipo
            c.notas        = self.ag_ed_notas or None
            s.add(c); s.commit()
            # Actualizar nombres en el diálogo vista
            medico = next((m for m in self.ag_medicos if m["id"] == self.ag_ed_lk_medico), None)
            tipo   = next((t for t in self.ag_tipos_cita if t["id"] == self.ag_ed_lk_tipo), None)
            if medico:
                self.ag_ver_medico    = medico["nombre"]
                self.ag_ver_lk_medico = medico["id"]
            if tipo:
                self.ag_ver_tipo      = tipo["nombre"]
                self.ag_ver_lk_tipo   = tipo["id"]
            self.ag_ver_notas    = self.ag_ed_notas
            self.ag_ver_editando = False
        self._ag_cargar_citas()

    def ag_confirmar_cita(self):
        if not self.ag_ver_id:
            return
        with Session(get_engine()) as s:
            c = s.get(Cita, self.ag_ver_id)
            if c:
                c.estado = "CONFIRMADA"
                s.add(c); s.commit()
        self.ag_ver_estado = "CONFIRMADA"
        self._ag_cargar_citas()

    def ag_cancelar_cita(self):
        if not self.ag_ver_id:
            return
        with Session(get_engine()) as s:
            c = s.get(Cita, self.ag_ver_id)
            if c:
                c.estado = "CANCELADA"
                s.add(c); s.commit()
        self.ag_dlg_ver = False
        self._ag_cargar_citas()

    def ag_seleccionar_paciente_existente(self, id_px: int):
        self.ag_nc_lk_paciente = id_px
        nombre = next(
            (r["nombre"] for r in self.ag_nc_resultados_px if r["id"] == id_px), ""
        )
        self.ag_nc_px_nombre = nombre
        self.ag_nc_resultados_px = []
        self.ag_nc_busq_px = nombre

    def ag_guardar_nueva_cita(self):
        from datetime import datetime as _dt
        self.ag_nc_error = ""
        if not self.ag_nc_inicio or not self.ag_nc_lk_medico or not self.ag_nc_lk_tipo:
            self.ag_nc_error = "Médico, tipo de cita y horario son obligatorios."
            return
        if not self.ag_nc_lk_paciente and not self.ag_nc_px_nombre.strip():
            self.ag_nc_error = "Ingrese el nombre del paciente."
            return
        try:
            from datetime import timedelta
            ini = _dt.fromisoformat(self.ag_nc_inicio.replace("Z", ""))
            fin = ini + timedelta(minutes=self.ag_nc_duracion)
            with Session(get_engine()) as s:
                nueva = Cita(
                    lk_paciente  = self.ag_nc_lk_paciente or None,
                    lk_medico    = self.ag_nc_lk_medico,
                    lk_tipo_cita = self.ag_nc_lk_tipo,
                    inicio       = ini,
                    fin          = fin,
                    estado       = "AGENDADA",
                    notas        = self.ag_nc_notas.strip() or None,
                    px_nombre    = self.ag_nc_px_nombre.strip() if not self.ag_nc_lk_paciente else None,
                    px_sexo      = self.ag_nc_px_sexo    if not self.ag_nc_lk_paciente else None,
                    px_celular   = self.ag_nc_px_celular if not self.ag_nc_lk_paciente else None,
                    px_ciudad    = self.ag_nc_px_ciudad  if not self.ag_nc_lk_paciente else None,
                    px_seguro    = self.ag_nc_px_seguro  if not self.ag_nc_lk_paciente else None,
                )
                s.add(nueva); s.commit()
            self.ag_dlg_nueva = False
            self._ag_cargar_citas()
        except Exception as e:
            self.ag_nc_error = f"Error al guardar: {e}"


# ══════════════════════════════════════════════════════════════════════════════
# ResultadosState — Módulo de resultados e imágenes médicas
# ══════════════════════════════════════════════════════════════════════════════

class ResultadosState(AtencionState):
    """
    Gestiona el módulo de resultados de exámenes (imagenológicos y de laboratorio).

    Flujo principal:
        1. ri_abrir()          → carga árbol del paciente actual
        2. Upload de archivos  → ri_procesar_upload()
        3. Asignar imágenes    → ri_abrir_asignar() → ri_confirmar_asignar()
           o crear nuevo       → ri_crear_y_asignar()
        4. Análisis            → ri_seleccionar_imagen() (panel Fase 3)

    Atención destino del upload (ri_procesar_upload/ri_recargar): soap_id_atencion
    si hay una atención en curso abierta; si no, cae a id_atencion_seleccionada
    (la fila resaltada en tabla_historial_atenciones). Esto último es lo que
    permite subir imágenes para pacientes migrados desde amaymed que solo
    tienen atenciones históricas y ninguna "en curso" creada en gesmed.
    """

    # ── Visibilidad ─────────────────────────────────────────────────────────
    ri_abierto: bool = False

    # ── Árbol ───────────────────────────────────────────────────────────────
    # ri_resultados: [{id_resultado, nombre_examen, fecha_imagen}]  — sin imagenes anidadas
    ri_sin_clasificar: list[dict] = []
    ri_resultados:     list[dict] = []
    ri_rama_abierta:   int        = 0     # id_resultado de la rama expandida (0 = ninguna)
    ri_imagenes_rama:  list[dict] = []    # imágenes de la rama abierta

    # ── Upload ──────────────────────────────────────────────────────────────
    ri_subiendo:      bool = False
    ri_upload_error:  str  = ""

    # ── Diálogo asignar ─────────────────────────────────────────────────────
    ri_show_asignar:      bool      = False
    ri_id_img_a_asignar:  int       = 0
    ri_opciones_res:      list[dict] = []   # [{id, label}] para el select
    ri_opcion_sel:        str       = ""
    # Sub-form "crear nuevo resultado"
    ri_show_crear:        bool      = False
    ri_catalogo_img:      list[dict] = []   # [{id_examen, nombre_examen}]
    ri_crear_examen:      str       = ""    # nombre seleccionado
    ri_crear_fecha:       str       = ""
    ri_crear_alias:       str       = ""
    ri_crear_hallazgos:   str       = ""

    # ── Imagen activa (análisis — Fase 3) ────────────────────────────────────
    ri_id_imagen_activa:  int       = 0
    ri_marcas:            list[dict] = []
    ri_imgs_activas:      list[dict] = []   # imágenes del resultado activo (para nav)
    ri_idx_activo:        int       = 0
    ri_zoom_nivel:        int       = 1     # 0-8: 75%·100%·150%·200%·250%·300%·350%·400%·450%

    # ── Grabar rama ──────────────────────────────────────────────────────────
    ri_grabar_rama_id:  int = 0    # id_resultado del último grabar
    ri_grabar_msg:      str = ""   # mensaje resultado de la operación

    # ── Borrar resultado (diálogo de confirmación con código) ─────────────────
    ri_borrar_resultado_open:      bool = False
    ri_borrar_resultado_id:        int  = 0
    ri_borrar_codigo_esperado:     str  = ""
    ri_borrar_codigo_input:        str  = ""

    # ── Visibilidad del panel árbol ───────────────────────────────────────────
    ri_show_arbol: bool = True

    # ── Herramienta de marcas ─────────────────────────────────────────────────
    ri_herramienta:  str  = ""     # "" | "c" | "f" | "t"
    ri_nv_payload:   str  = ""     # JSON recibido desde JS {tipo,x1,y1,x2,y2,radio}
    ri_nv_open:      bool = False  # diálogo nueva marca
    ri_edit_open:    bool = False  # diálogo editar marca de texto
    ri_edit_id:      int  = 0     # id_marca en edición
    ri_nv_tipo:      str  = ""     # tipo de la nueva marca
    ri_nv_x1:        int  = 0
    ri_nv_y1:        int  = 0
    ri_nv_x2:        int  = 0
    ri_nv_y2:        int  = 0
    ri_nv_radio:     int  = 0
    ri_nv_color:     str  = "#ff0000"
    ri_nv_grosor:    int  = 2
    ri_nv_obs:       str  = ""
    ri_nv_font:      int  = 14

    # ── Computed vars ────────────────────────────────────────────────────────

    @rx.var
    def ri_marcas_json(self) -> str:
        import json
        return json.dumps(self.ri_marcas)

    @rx.var
    def ri_hay_sin_clasificar(self) -> bool:
        return len(self.ri_sin_clasificar) > 0 or self.ri_subiendo

    @rx.var
    def ri_imagen_activa_clasificada(self) -> bool:
        """True solo si la imagen activa pertenece a un resultado (no es 'sin clasificar')."""
        if not self.ri_id_imagen_activa:
            return False
        return any(
            im.get("id_imagen") == self.ri_id_imagen_activa
            for im in self.ri_imagenes_rama
        )

    @rx.var
    def ri_catalogo_nombres(self) -> list[str]:
        return [e["nombre_examen"] for e in self.ri_catalogo_img]

    @rx.var
    def ri_total_imgs_activas(self) -> int:
        return len(self.ri_imgs_activas)

    @rx.var
    def ri_src_activa(self) -> str:
        if self.ri_id_imagen_activa:
            return f"{_BACKEND}/imagen/{self.ri_id_imagen_activa}"
        return ""

    @rx.var
    def ri_rotacion_css_activa(self) -> str:
        """Rotación CSS de la imagen activa, leída de los dicts ya actualizados por ri_recargar."""
        if not self.ri_id_imagen_activa:
            return "rotate(0deg)"
        for im in self.ri_imagenes_rama:
            if im.get("id_imagen") == self.ri_id_imagen_activa:
                return im.get("rotacion_css", "rotate(0deg)")
        for im in self.ri_sin_clasificar:
            if im.get("id_imagen") == self.ri_id_imagen_activa:
                return im.get("rotacion_css", "rotate(0deg)")
        return "rotate(0deg)"

    @rx.var
    def ri_zoom_label(self) -> str:
        return ["75%", "100%", "150%", "200%", "250%", "300%", "350%", "400%", "450%"][self.ri_zoom_nivel]

    @rx.var
    def ri_rotacion_grados(self) -> int:
        """Ángulo de rotación de la imagen activa (0/90/180/270) para pasarlo al JS via data-rotation."""
        if not self.ri_id_imagen_activa:
            return 0
        for im in self.ri_imagenes_rama:
            if im.get("id_imagen") == self.ri_id_imagen_activa:
                return im.get("rotacion", 0)
        for im in self.ri_sin_clasificar:
            if im.get("id_imagen") == self.ri_id_imagen_activa:
                return im.get("rotacion", 0)
        return 0

    @rx.var
    def ri_transform_activa(self) -> str:
        """Combina rotación y zoom en un solo valor CSS transform para la imagen activa."""
        scales = ["0.75", "1", "1.5", "2", "2.5", "3", "3.5", "4", "4.5"]
        return f"{self.ri_rotacion_css_activa} scale({scales[self.ri_zoom_nivel]})"

    # ── Helpers privados ─────────────────────────────────────────────────────

    def ri_recargar(self):
        nro   = self.nro_hclinica_seleccionado
        # soap_id_atencion (atención en curso) si hay una abierta; si no, la
        # atención histórica resaltada en tabla_historial_atenciones — necesario
        # para pacientes migrados que solo tienen atenciones antiguas, sin
        # ninguna "en curso" (ver ri_procesar_upload).
        lk_at = self.soap_id_atencion or self.id_atencion_seleccionada
        if nro <= 0:
            return
        with Session(get_engine()) as session:
            self.ri_sin_clasificar = cargar_imagenes_sin_clasificar(session, lk_at)
            self.ri_resultados     = cargar_resultados_imagen_paciente(session, nro)
            if self.ri_rama_abierta:
                self.ri_imagenes_rama = cargar_imagenes_resultado(session, self.ri_rama_abierta)

    # ── Apertura / cierre ────────────────────────────────────────────────────

    def ri_abrir(self):
        self.ri_abierto = True
        self.ri_recargar()

    def ri_cerrar(self):
        self.ri_abierto      = False
        self.ri_show_asignar = False

    # ── Toggle rama del árbol ────────────────────────────────────────────────

    def ri_toggle_rama(self, id_resultado: int):
        if self.ri_rama_abierta == id_resultado:
            self.ri_rama_abierta  = 0
            self.ri_imagenes_rama = []
        else:
            self.ri_rama_abierta = id_resultado
            with Session(get_engine()) as session:
                self.ri_imagenes_rama = cargar_imagenes_resultado(session, id_resultado)

    # ── Upload ───────────────────────────────────────────────────────────────

    async def ri_procesar_upload(self, files: list[rx.UploadFile]):
        if not self.puede_escribir_paciente_actual:
            return
        self.ri_subiendo     = True
        self.ri_upload_error = ""
        yield                           # envía ri_subiendo=True al frontend ANTES de procesar
        nro   = self.nro_hclinica_seleccionado
        # soap_id_atencion (atención en curso) si hay una abierta; si no, la
        # atención histórica resaltada en tabla_historial_atenciones — permite
        # subir imágenes de pacientes migrados que solo tienen atenciones
        # antiguas (sin ninguna "en curso" creada todavía en gesmed).
        lk_at = self.soap_id_atencion or self.id_atencion_seleccionada
        if nro <= 0 or lk_at <= 0:
            self.ri_upload_error = "No hay paciente o atención (actual o histórica seleccionada)."
            self.ri_subiendo = False
            return
        try:
            for file in files:
                datos = await file.read()
                mime  = file.content_type or ""
                if "pdf" in mime:
                    paginas = pdf_a_jpg(datos)
                elif "png" in mime:
                    paginas = [normalizar_a_jpg(datos, mime)]
                else:
                    paginas = [datos]   # ya es JPG
                with Session(get_engine()) as session:
                    for jpg in paginas:
                        id_img = rq_insertar_imagen(session, lk_at)
                        try:
                            img_guardar(jpg, nro, lk_at, id_img)
                        except Exception:
                            rq_eliminar_imagen(session, id_img)
                            raise
        except Exception as e:
            self.ri_upload_error = str(e)
        finally:
            self.ri_subiendo = False
            self.ri_recargar()

    # ── Asignación de imagen a resultado ─────────────────────────────────────

    def ri_abrir_asignar(self, id_imagen: int):
        self.ri_id_img_a_asignar = id_imagen
        self.ri_opcion_sel       = ""
        self.ri_show_crear       = False
        nro = self.nro_hclinica_seleccionado
        with Session(get_engine()) as session:
            resultados = cargar_resultados_imagen_paciente(session, nro)
            self.ri_opciones_res = [
                {"id": str(r["id_resultado"]),
                 "label": f"{r['nombre_examen']} — {r['fecha_imagen']}"}
                for r in resultados
            ] + [{"id": "__nuevo__", "label": "+ Crear nuevo resultado..."}]
            self.ri_catalogo_img = cargar_catalogo_examenes_imagen(session)
        self.ri_show_asignar = True

    def set_ri_show_asignar(self, val: bool):
        self.ri_show_asignar = val

    def set_ri_crear_examen(self, val: str):
        self.ri_crear_examen = val

    def set_ri_crear_fecha(self, val: str):
        self.ri_crear_fecha = val

    def set_ri_crear_alias(self, val: str):
        self.ri_crear_alias = val

    def set_ri_crear_hallazgos(self, val: str):
        self.ri_crear_hallazgos = val

    def ri_set_opcion(self, val: str):
        self.ri_opcion_sel = val
        self.ri_show_crear = (val == "__nuevo__")

    def ri_confirmar_asignar(self):
        val = self.ri_opcion_sel
        if not val or val == "__nuevo__":
            return
        id_resultado = int(val)
        with Session(get_engine()) as session:
            imagenes     = cargar_imagenes_resultado(session, id_resultado)
            siguiente    = len(imagenes)
            asignar_imagen_a_resultado(
                session, self.ri_id_img_a_asignar, id_resultado, siguiente
            )
        self.ri_show_asignar = False
        self.ri_recargar()

    def ri_crear_y_asignar(self):
        if not self.ri_crear_examen or not self.ri_crear_alias.strip():
            return
        nro = self.nro_hclinica_seleccionado
        lk_examen = next(
            (e["id_examen"] for e in self.ri_catalogo_img
             if e["nombre_examen"] == self.ri_crear_examen),
            None,
        )
        import datetime as _dt
        try:
            fecha = _dt.date.fromisoformat(self.ri_crear_fecha) if self.ri_crear_fecha else _dt.date.today()
        except ValueError:
            fecha = _dt.date.today()
        with Session(get_engine()) as session:
            id_resultado = crear_resultado_imagen(
                session, nro, lk_examen, fecha,
                alias     = self.ri_crear_alias.strip(),
                hallazgos = self.ri_crear_hallazgos.strip() or None,
            )
            asignar_imagen_a_resultado(session, self.ri_id_img_a_asignar, id_resultado, 0)
        self.ri_crear_alias     = ""
        self.ri_crear_hallazgos = ""
        self.ri_show_asignar    = False
        self.ri_recargar()

    # ── Reordenar imágenes dentro de un resultado ────────────────────────────

    def ri_subir_imagen(self, id_resultado: int, id_imagen: int):
        """Intercambia la imagen con su predecesora en orden."""
        with Session(get_engine()) as session:
            imgs = cargar_imagenes_resultado(session, id_resultado)
        idx = next((i for i, im in enumerate(imgs) if im["id_imagen"] == id_imagen), None)
        if idx is None or idx == 0:
            return
        ids = [im["id_imagen"] for im in imgs]
        ids[idx - 1], ids[idx] = ids[idx], ids[idx - 1]
        with Session(get_engine()) as session:
            rq_reordenar(session, id_resultado, ids)
        self.ri_recargar()

    def ri_bajar_imagen(self, id_resultado: int, id_imagen: int):
        """Intercambia la imagen con su sucesora en orden."""
        with Session(get_engine()) as session:
            imgs = cargar_imagenes_resultado(session, id_resultado)
        idx = next((i for i, im in enumerate(imgs) if im["id_imagen"] == id_imagen), None)
        if idx is None or idx >= len(imgs) - 1:
            return
        ids = [im["id_imagen"] for im in imgs]
        ids[idx], ids[idx + 1] = ids[idx + 1], ids[idx]
        with Session(get_engine()) as session:
            rq_reordenar(session, id_resultado, ids)
        self.ri_recargar()

    # ── Eliminar imagen ──────────────────────────────────────────────────────

    def ri_eliminar(self, id_imagen: int):
        with Session(get_engine()) as session:
            datos = rq_eliminar_imagen(session, id_imagen)
        if datos and datos["nro_hclinica"] and datos["lk_atencion"]:
            img_eliminar(datos["nro_hclinica"], datos["lk_atencion"], datos["id_imagen"])
        self.ri_recargar()

    # ── Herramienta de marcas — setters explícitos ───────────────────────────

    def set_ri_nv_payload(self, v: str):
        self.ri_nv_payload = v

    def set_ri_nv_obs(self, v: str):
        self.ri_nv_obs = v

    def set_ri_nv_color(self, v: str):
        self.ri_nv_color = v

    def set_ri_nv_grosor(self, v: str):
        try:
            self.ri_nv_grosor = max(1, min(10, int(v)))
        except (ValueError, TypeError):
            pass

    def set_ri_nv_font(self, v: str):
        try:
            self.ri_nv_font = max(8, min(72, int(v)))
        except (ValueError, TypeError):
            pass

    # ── Grabar imágenes de una rama al disco ─────────────────────────────────

    def ri_grabar_imagenes_rama(self, id_resultado: int):
        from .utils.imagen_utils import ruta_completa
        self.ri_grabar_rama_id = id_resultado
        self.ri_grabar_msg     = "Verificando…"
        with Session(get_engine()) as s:
            resultado = s.get(ResultadosImagenes, id_resultado)
            if not resultado:
                self.ri_grabar_msg = "Error: resultado no encontrado."
                return
            nro = resultado.lk_paciente
            imagenes = cargar_imagenes_resultado(s, id_resultado)
        ok = faltantes = 0
        for img in imagenes:
            ruta = ruta_completa(nro, img["lk_atencion"], img["id_imagen"])
            if ruta.exists():
                ok += 1
            else:
                faltantes += 1
        total = len(imagenes)
        if total == 0:
            self.ri_grabar_msg = "Sin imágenes."
        elif faltantes == 0:
            self.ri_grabar_msg = f"OK – {ok} imagen{'es' if ok != 1 else ''} en disco"
        else:
            self.ri_grabar_msg = (
                f"{ok} OK / {faltantes} faltante{'s' if faltantes != 1 else ''}"
            )

    # ── Borrar resultado completo ─────────────────────────────────────────────

    def ri_abrir_borrar_resultado(self, id_resultado: int):
        import random, string
        self.ri_borrar_resultado_id    = id_resultado
        self.ri_borrar_codigo_esperado = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
        )
        self.ri_borrar_codigo_input    = ""
        self.ri_borrar_resultado_open  = True

    def set_ri_borrar_codigo_input(self, val: str):
        self.ri_borrar_codigo_input = val

    def ri_cancelar_borrar_resultado(self):
        self.ri_borrar_resultado_open  = False
        self.ri_borrar_resultado_id    = 0
        self.ri_borrar_codigo_esperado = ""
        self.ri_borrar_codigo_input    = ""

    def ri_confirmar_borrar_resultado(self):
        if self.ri_borrar_codigo_input.strip().upper() != self.ri_borrar_codigo_esperado:
            return
        id_resultado = self.ri_borrar_resultado_id
        with Session(get_engine()) as session:
            datos_fisicos = rq_eliminar_resultado_imagen(session, id_resultado)
        for d in datos_fisicos:
            try:
                img_eliminar(d["nro_hclinica"], d["lk_atencion"], d["id_imagen"])
            except Exception:
                pass
        if self.ri_rama_abierta == id_resultado:
            self.ri_rama_abierta     = 0
            self.ri_imagenes_rama    = []
            self.ri_id_imagen_activa = 0
            self.ri_marcas           = []
        self.ri_cancelar_borrar_resultado()
        self.ri_recargar()

    # ── Visibilidad del panel árbol ───────────────────────────────────────────

    def toggle_ri_show_arbol(self):
        self.ri_show_arbol = not self.ri_show_arbol

    # ── Herramienta de marcas ─────────────────────────────────────────────────

    def ri_activar_herramienta(self, tipo: str):
        self.ri_herramienta = "" if self.ri_herramienta == tipo else tipo

    def ri_recibir_marca(self):
        import json
        try:
            d = json.loads(self.ri_nv_payload)
            self.ri_nv_tipo  = d.get("tipo", "c")
            self.ri_nv_x1    = int(d.get("x1", 0))
            self.ri_nv_y1    = int(d.get("y1", 0))
            self.ri_nv_x2    = int(d.get("x2", 0))
            self.ri_nv_y2    = int(d.get("y2", 0))
            self.ri_nv_radio = int(d.get("radio", 0))
            self.ri_nv_obs   = ""
            self.ri_herramienta = ""
            self.ri_nv_open  = True
        except Exception:
            pass

    def ri_cancelar_nueva_marca(self):
        self.ri_nv_open    = False
        self.ri_nv_payload = ""

    def ri_guardar_nueva_marca(self):
        if not self.puede_escribir_paciente_actual:
            return
        with Session(get_engine()) as s:
            rq_guardar_marca(
                s,
                id_imagen   = self.ri_id_imagen_activa,
                tipo        = self.ri_nv_tipo,
                x           = self.ri_nv_x1,
                y           = self.ri_nv_y1,
                radio       = self.ri_nv_radio,
                x2          = self.ri_nv_x2,
                y2          = self.ri_nv_y2,
                grosor      = self.ri_nv_grosor,
                color       = self.ri_nv_color,
                font        = self.ri_nv_font,
                nivel       = len(self.ri_marcas),
                observacion = self.ri_nv_obs,
            )
            self.ri_marcas = cargar_marcas(s, self.ri_id_imagen_activa)
        self.ri_nv_open    = False
        self.ri_nv_payload = ""

    def ri_eliminar_marca_item(self, id_marca: int):
        if not self.puede_escribir_paciente_actual:
            return
        with Session(get_engine()) as s:
            rq_eliminar_marca(s, id_marca)
            self.ri_marcas = cargar_marcas(s, self.ri_id_imagen_activa)

    def ri_abrir_editar_marca(self, id_marca: int):
        for m in self.ri_marcas:
            if m["id_marca"] == id_marca:
                self.ri_nv_obs   = m["observacion"]
                self.ri_nv_color = m["color"]
                self.ri_nv_font  = m["font"]
                self.ri_edit_id  = id_marca
                self.ri_edit_open = True
                break

    def ri_cancelar_edicion_marca(self):
        self.ri_edit_open = False
        self.ri_edit_id   = 0

    def ri_guardar_edicion_marca(self):
        if not self.puede_escribir_paciente_actual:
            return
        with Session(get_engine()) as s:
            rq_actualizar_marca(s, self.ri_edit_id,
                                color=self.ri_nv_color,
                                font=self.ri_nv_font,
                                observacion=self.ri_nv_obs)
            self.ri_marcas = cargar_marcas(s, self.ri_id_imagen_activa)
        self.ri_edit_open = False
        self.ri_edit_id   = 0

    # ── Seleccionar imagen para análisis (Fase 3) ────────────────────────────

    def ri_zoom_in(self):
        if self.ri_zoom_nivel < 8:
            self.ri_zoom_nivel += 1

    def ri_zoom_out(self):
        if self.ri_zoom_nivel > 0:
            self.ri_zoom_nivel -= 1

    def ri_seleccionar_imagen(self, id_imagen: int, id_resultado: int):
        self.ri_id_imagen_activa = id_imagen
        self.ri_zoom_nivel  = 1  # reset a 100% al cambiar de imagen
        self.ri_herramienta = ""
        self.ri_nv_open     = False
        with Session(get_engine()) as session:
            self.ri_marcas = cargar_marcas(session, id_imagen)
            if id_resultado:
                self.ri_imgs_activas = cargar_imagenes_resultado(session, id_resultado)
            else:
                img_rec = session.get(Imagenes, id_imagen)
                rot = img_rec.rotacion if img_rec else 0
                self.ri_imgs_activas = [{
                    "id_imagen":    id_imagen,
                    "src_imagen":   f"{_BACKEND}/imagen/{id_imagen}",
                    "rotacion_css": f"rotate({rot}deg)",
                    "rotacion":     rot,
                    "detalle":      img_rec.detalle or "" if img_rec else "",
                    "orden":        0,
                    "lk_atencion":  img_rec.lk_atencion if img_rec else None,
                }]
        self.ri_idx_activo = next(
            (i for i, im in enumerate(self.ri_imgs_activas) if im["id_imagen"] == id_imagen), 0
        )

    def ri_nav_anterior(self):
        if self.ri_idx_activo > 0 and self.ri_imgs_activas:
            nuevo_idx    = self.ri_idx_activo - 1
            nueva_id     = self.ri_imgs_activas[nuevo_idx]["id_imagen"]
            id_resultado = self.ri_imgs_activas[0].get("lk_resultado_imagen", 0)
            self.ri_seleccionar_imagen(nueva_id, id_resultado)

    def ri_nav_siguiente(self):
        if self.ri_idx_activo < len(self.ri_imgs_activas) - 1 and self.ri_imgs_activas:
            nuevo_idx    = self.ri_idx_activo + 1
            nueva_id     = self.ri_imgs_activas[nuevo_idx]["id_imagen"]
            id_resultado = self.ri_imgs_activas[0].get("lk_resultado_imagen", 0)
            self.ri_seleccionar_imagen(nueva_id, id_resultado)

    # ── Rotar imagen activa ──────────────────────────────────────────────────

    def ri_rotar(self):
        if not self.ri_id_imagen_activa:
            return
        nueva_rot = (self._ri_rotacion_activa() + 90) % 360
        with Session(get_engine()) as session:
            rq_actualizar_rotacion(session, self.ri_id_imagen_activa, nueva_rot)
        self.ri_recargar()

    def _ri_rotacion_activa(self) -> int:
        for im in self.ri_imagenes_rama:
            if im["id_imagen"] == self.ri_id_imagen_activa:
                return im.get("rotacion", 0)
        for im in self.ri_sin_clasificar:
            if im["id_imagen"] == self.ri_id_imagen_activa:
                return im.get("rotacion", 0)
        return 0


# ── Laboratorio ───────────────────────────────────────────────────────────────

class LaboratorioState(AtencionState):
    lab_open:              bool       = False
    lab_fecha:             str        = ""
    lab_catalogo:          list[dict] = []   # {id_examen, display} — cargado al abrir
    lab_filas:             list[dict] = []   # {fila_id, busqueda, examen_id, valor, en_rango, observacion}
    lab_fila_counter:      int        = 0
    lab_imagen_fuente:     int        = 0
    lab_guardando:         bool       = False
    lab_error:             str        = ""

    # ── historial laboratorio (OfRL + tab) ───────────────────────────────────
    lab_h_filas: list[dict] = []   # flat rows tipo G/E/R con visible/expandido
    lab_h_exp_g: list[str]  = []   # gkeys expandidos
    lab_h_exp_e: list[str]  = []   # ekeys expandidos

    # ── historial signos vitales (OfRL) ──────────────────────────────────────
    sv_h_filas: list[dict] = []    # flat rows tipo E/R con visible/expandido
    sv_h_exp:   list[str]  = []    # svkeys expandidos

    # ── gráfico cartesiano (OfRL) ─────────────────────────────────────────────
    orl_tab_activo:     str        = "lab"
    orl_grafico_ekey:   str        = ""          # ekey (lab) o svkey (sv) seleccionado
    orl_grafico_titulo: str        = ""
    orl_grafico_escala: str        = "trimestre" # "mes" | "trimestre" | "año"
    orl_grafico_datos:      list[dict] = []        # [{x: str, y: float|None}]
    orl_grafico_divisiones: int       = 12        # 3..20 períodos visibles
    orl_grafico_offset:     int       = 0         # períodos desplazados hacia atrás
    orl_grafico_offset_max: int       = 0         # máximo offset según datos más antiguos

    def _nueva_fila(self) -> dict:
        self.lab_fila_counter += 1
        return {
            "fila_id":     self.lab_fila_counter,
            "busqueda":    "",
            "examen_id":   "",
            "valor":       "",
            "en_rango":    "EN_RANGO",
            "observacion": "",
        }

    def lab_abrir(self, imagen_id: int = 0):
        import datetime as _dt
        with Session(get_engine()) as session:
            self.lab_catalogo = cargar_catalogo_completo_lab(session)
        self.lab_fecha         = _dt.date.today().isoformat()
        self.lab_fila_counter  = 0
        self.lab_imagen_fuente = imagen_id
        self.lab_error         = ""
        self.lab_filas         = [self._nueva_fila()]
        self.lab_open          = True

    def lab_cerrar(self):
        self.lab_open     = False
        self.lab_filas    = []
        self.lab_catalogo = []
        self.lab_error    = ""

    def lab_agregar_fila(self):
        if not self.puede_escribir_paciente_actual:
            return
        self.lab_filas = self.lab_filas + [self._nueva_fila()]

    def lab_eliminar_fila(self, fila_id: int):
        if not self.puede_escribir_paciente_actual:
            return
        self.lab_filas = [f for f in self.lab_filas if f["fila_id"] != fila_id]

    def lab_set_fecha(self, val: str):
        self.lab_fecha = val

    def lab_set_busqueda(self, fila_id: int, texto: str):
        examen_id = next(
            (e["id_examen"] for e in self.lab_catalogo if e["display"] == texto),
            "",
        )
        self.lab_filas = [
            {**f, "busqueda": texto, "examen_id": examen_id}
            if f["fila_id"] == fila_id else f
            for f in self.lab_filas
        ]

    def lab_set_valor(self, fila_id: int, val: str):
        self.lab_filas = [
            {**f, "valor": val} if f["fila_id"] == fila_id else f
            for f in self.lab_filas
        ]

    def lab_set_rango(self, fila_id: int, rango: str):
        self.lab_filas = [
            {**f, "en_rango": rango} if f["fila_id"] == fila_id else f
            for f in self.lab_filas
        ]

    def lab_set_obs(self, fila_id: int, val: str):
        self.lab_filas = [
            {**f, "observacion": val} if f["fila_id"] == fila_id else f
            for f in self.lab_filas
        ]

    def lab_guardar(self):
        if not self.puede_escribir_paciente_actual:
            return
        import datetime as _dt
        nro = self.nro_hclinica_seleccionado
        if nro <= 0:
            self.lab_error = "No hay paciente activo."
            return
        try:
            fecha = _dt.date.fromisoformat(self.lab_fecha) if self.lab_fecha else _dt.date.today()
        except ValueError:
            self.lab_error = "Fecha inválida."
            return
        filas_validas = [
            f for f in self.lab_filas
            if f.get("examen_id") and f.get("valor")
        ]
        if not filas_validas:
            self.lab_error = "Ingrese al menos un examen con valor."
            return
        self.lab_guardando = True
        self.lab_error     = ""
        try:
            with Session(get_engine()) as session:
                for f in filas_validas:
                    try:
                        valor_num = float(f["valor"])
                    except (ValueError, TypeError):
                        continue
                    guardar_resultado_lab(
                        session,
                        nro_hclinica     = nro,
                        lk_examen        = int(f["examen_id"]),
                        fecha            = fecha,
                        valor_numerico   = valor_num,
                        valor_texto      = None,
                        en_rango         = f.get("en_rango") or "EN_RANGO",
                        observacion      = f.get("observacion") or None,
                        lk_imagen_fuente = self.lab_imagen_fuente or None,
                    )
        except Exception as e:
            self.lab_error = str(e)
        finally:
            self.lab_guardando = False
        if not self.lab_error:
            self.lab_cerrar()
            self.lab_h_cargar()

    # ── historial handlers ────────────────────────────────────────────────────

    def lab_h_cargar(self):
        nro = self.nro_hclinica_seleccionado
        if nro <= 0:
            return
        with Session(get_engine()) as session:
            self.lab_h_filas = cargar_historial_lab(session, nro)
        self.lab_h_exp_g = []
        self.lab_h_exp_e = []

    def _lab_h_recompute_vis(self):
        exp_g = set(self.lab_h_exp_g)
        exp_e = set(self.lab_h_exp_e)
        self.lab_h_filas = [
            {**f,
             "visible": (
                 True if f["tipo"] == "G"
                 else (f["gkey"] in exp_g) if f["tipo"] == "E"
                 else (f["gkey"] in exp_g and f["ekey"] in exp_e)
             ),
             "expandido": (
                 (f["gkey"] in exp_g) if f["tipo"] == "G"
                 else (f["ekey"] in exp_e) if f["tipo"] == "E"
                 else False
             ),
            }
            for f in self.lab_h_filas
        ]

    def lab_h_toggle_grupo(self, gkey: str):
        if gkey in self.lab_h_exp_g:
            self.lab_h_exp_g = [k for k in self.lab_h_exp_g if k != gkey]
        else:
            self.lab_h_exp_g = self.lab_h_exp_g + [gkey]
        self._lab_h_recompute_vis()

    def lab_h_toggle_examen(self, ekey: str):
        if ekey in self.lab_h_exp_e:
            self.lab_h_exp_e = [k for k in self.lab_h_exp_e if k != ekey]
        else:
            self.lab_h_exp_e = self.lab_h_exp_e + [ekey]
        self._lab_h_recompute_vis()

    # ── OfRL (offcanvas Resultados Laboratorio) ───────────────────────────────

    def abrir_lab_orl(self):
        self.offcanvas_lab_orl = True
        self.offcanvas_resultados_examenes = False
        self.show_panel_izq = False
        nro = self.nro_hclinica_seleccionado
        if nro > 0:
            with Session(get_engine()) as session:
                self.lab_h_filas = cargar_historial_lab(session, nro)
                self.sv_h_filas  = cargar_historial_sv(session, nro)
        self.lab_h_exp_g       = []
        self.lab_h_exp_e       = []
        self.sv_h_exp          = []
        self.orl_grafico_ekey       = ""
        self.orl_grafico_titulo     = ""
        self.orl_grafico_datos      = []
        self.orl_grafico_escala     = "trimestre"
        self.orl_grafico_divisiones = 12
        self.orl_grafico_offset     = 0
        self.orl_grafico_offset_max = 0
        self.orl_tab_activo         = "lab"

    # ── signos vitales handlers ───────────────────────────────────────────────

    def sv_h_cargar(self):
        nro = self.nro_hclinica_seleccionado
        if nro <= 0:
            return
        with Session(get_engine()) as session:
            self.sv_h_filas = cargar_historial_sv(session, nro)
        self.sv_h_exp = []

    def _sv_h_recompute_vis(self):
        exp = set(self.sv_h_exp)
        self.sv_h_filas = [
            {**f,
             "visible":  True if f["tipo"] == "E" else f["svkey"] in exp,
             "expandido": (f["svkey"] in exp) if f["tipo"] == "E" else False,
            }
            for f in self.sv_h_filas
        ]

    def sv_h_toggle(self, svkey: str):
        if svkey in self.sv_h_exp:
            self.sv_h_exp = [k for k in self.sv_h_exp if k != svkey]
        else:
            self.sv_h_exp = self.sv_h_exp + [svkey]
        self._sv_h_recompute_vis()

    # ── gráfico cartesiano ────────────────────────────────────────────────────

    def orl_set_tab(self, tab: str):
        self.orl_tab_activo         = tab
        self.orl_grafico_ekey       = ""
        self.orl_grafico_titulo     = ""
        self.orl_grafico_datos      = []
        self.orl_grafico_offset     = 0
        self.orl_grafico_offset_max = 0

    def orl_set_escala(self, escala: str):
        self.orl_grafico_escala = escala
        self.orl_grafico_offset = 0
        self._orl_recompute_grafico()

    def orl_set_divisiones(self, val: str):
        try:
            self.orl_grafico_divisiones = max(3, min(20, int(val)))
        except (ValueError, TypeError):
            pass
        self.orl_grafico_offset = 0
        self._orl_recompute_grafico()

    def orl_set_offset_slider(self, val: str):
        """Slider con posición invertida: derecha = hoy (offset 0), izquierda = más antiguo."""
        try:
            slider_val = int(float(val))
        except (ValueError, TypeError):
            slider_val = self.orl_grafico_offset_max
        self.orl_grafico_offset = max(0, min(self.orl_grafico_offset_max,
                                             self.orl_grafico_offset_max - slider_val))
        self._orl_recompute_grafico()

    def orl_lab_click(self, ekey: str, nombre: str):
        """Toggle árbol + selecciona para el gráfico."""
        if ekey in self.lab_h_exp_e:
            self.lab_h_exp_e = [k for k in self.lab_h_exp_e if k != ekey]
        else:
            self.lab_h_exp_e = self.lab_h_exp_e + [ekey]
        self._lab_h_recompute_vis()
        self.orl_tab_activo         = "lab"
        self.orl_grafico_ekey       = ekey
        self.orl_grafico_titulo     = nombre
        self.orl_grafico_offset     = 0
        self._orl_recompute_grafico()

    def orl_sv_click(self, svkey: str, nombre: str):
        """Toggle árbol + selecciona para el gráfico."""
        if svkey in self.sv_h_exp:
            self.sv_h_exp = [k for k in self.sv_h_exp if k != svkey]
        else:
            self.sv_h_exp = self.sv_h_exp + [svkey]
        self._sv_h_recompute_vis()
        self.orl_tab_activo         = "sv"
        self.orl_grafico_ekey       = svkey
        self.orl_grafico_titulo     = nombre
        self.orl_grafico_offset     = 0
        self._orl_recompute_grafico()

    def _orl_recompute_grafico(self):
        import datetime as _dt
        from collections import defaultdict as _dd

        if not self.orl_grafico_ekey:
            self.orl_grafico_datos = []
            return

        if self.orl_tab_activo == "lab":
            filas_r = [
                f for f in self.lab_h_filas
                if f.get("tipo") == "R" and f.get("ekey") == self.orl_grafico_ekey
            ]
        else:
            filas_r = [
                f for f in self.sv_h_filas
                if f.get("tipo") == "R" and f.get("svkey") == self.orl_grafico_ekey
            ]

        raw: list = []
        for f in filas_r:
            try:
                d = _dt.datetime.strptime(f["fecha"], "%d/%m/%Y")
                v = float(f["valor"])
                raw.append((d, v))
            except (ValueError, TypeError, KeyError):
                pass

        escala  = self.orl_grafico_escala
        N       = max(3, min(20, self.orl_grafico_divisiones))
        today   = _dt.datetime.today()

        _M = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
        _Q = ["T1","T2","T3","T4"]

        def make_key(d: _dt.datetime) -> tuple:
            if escala == "día":
                return (d.year, d.month, d.day, 4)
            elif escala == "semana":
                iso = d.isocalendar()
                return (iso[0], int(iso[1]), 0, 0)
            elif escala == "mes":
                return (d.year, d.month, 0, 1)
            elif escala == "trimestre":
                q = (d.month - 1) // 3
                return (d.year, q * 3 + 1, 0, 2)
            else:
                return (d.year, 1, 0, 3)

        def make_label(k: tuple) -> str:
            if k[3] == 4:
                y, m, d_, _ = k;  return f"{d_:02d}/{m:02d}/{y}"
            elif k[3] == 0:
                y, w, _, _ = k;   return f"S{w:02d} {y}"
            elif k[3] == 1:
                y, m, _, _ = k;   return f"{_M[m-1]} {y}"
            elif k[3] == 2:
                y, m, _, _ = k;   return f"{_Q[(m-1)//3]} {y}"
            else:
                return str(k[0])

        # Calcular offset_max a partir de la fecha más antigua con datos
        if raw:
            earliest = min(d for d, _ in raw)
            if escala == "día":
                total_periods = (today - earliest).days
            elif escala == "semana":
                total_periods = (today - earliest).days // 7
            elif escala == "mes":
                total_periods = (today.year * 12 + today.month) - (earliest.year * 12 + earliest.month)
            elif escala == "trimestre":
                total_periods = ((today.year * 12 + today.month) - (earliest.year * 12 + earliest.month)) // 3
            else:  # año
                total_periods = today.year - earliest.year
            offset_max = max(0, total_periods - N + 1)
        else:
            offset_max = 0

        self.orl_grafico_offset_max = offset_max
        offset = max(0, min(offset_max, self.orl_grafico_offset))
        self.orl_grafico_offset = offset

        # Generar los N períodos hacia atrás desde (hoy - offset períodos)
        def period_keys() -> list:
            keys: list = []
            if escala == "día":
                anchor = today - _dt.timedelta(days=offset)
                for i in range(N - 1, -1, -1):
                    keys.append(make_key(anchor - _dt.timedelta(days=i)))
            elif escala == "semana":
                anchor = today - _dt.timedelta(weeks=offset)
                for i in range(N - 1, -1, -1):
                    keys.append(make_key(anchor - _dt.timedelta(weeks=i)))
            elif escala == "mes":
                base = today.year * 12 + today.month - 1 - offset
                for i in range(N - 1, -1, -1):
                    total = base - i
                    keys.append((total // 12, total % 12 + 1, 0, 1))
            elif escala == "trimestre":
                base_q = today.year * 4 + (today.month - 1) // 3 - offset
                for i in range(N - 1, -1, -1):
                    tq = base_q - i
                    keys.append((tq // 4, (tq % 4) * 3 + 1, 0, 2))
            else:  # año
                base_y = today.year - offset
                for i in range(N - 1, -1, -1):
                    keys.append((base_y - i, 1, 0, 3))
            return keys

        # Agregar datos por período
        groups: dict = _dd(list)
        for d, v in raw:
            groups[make_key(d)].append(v)

        slots = period_keys()
        self.orl_grafico_datos = [
            {
                "x": make_label(k),
                "y": round(sum(groups[k]) / len(groups[k]), 2) if k in groups else None,
            }
            for k in slots
        ]


# ── Administración de usuarios ────────────────────────────────────────────────

class AdminUsuariosState(State):
    # Lista de usuarios
    au_lista: list[dict] = []

    # ID del usuario siendo editado
    au_edit_id: int = 0

    # Formulario: nuevo usuario
    au_n_nombre: str = ""
    au_n_especialidad: str = ""
    au_n_cod_esp: str = ""
    au_n_celular: str = ""
    au_n_email: str = ""
    au_n_usuario: str = ""
    au_n_clave: str = ""
    au_n_clave2: str = ""
    au_n_rol: str = "MEDICO_ATENCION"
    # Perfil de alcance de pacientes ("TT"=ve y modifica todos, "PP"=ve y
    # modifica solo propios, "TP"=ve todos pero modifica solo propios).
    au_n_perfil_alcance: str = "TT"

    # Formulario: editar usuario
    au_e_nombre: str = ""
    au_e_especialidad: str = ""
    au_e_cod_esp: str = ""
    au_e_celular: str = ""
    au_e_email: str = ""
    au_e_usuario: str = ""
    au_e_rol: str = "MEDICO_ATENCION"
    au_e_estado: int = 1
    au_e_perfil_alcance: str = "TT"

    # Formulario: resetear contraseña
    au_p_id: int = 0
    au_p_nombre: str = ""
    au_p_clave: str = ""
    au_p_clave2: str = ""

    # Estado de diálogos
    au_dlg_nuevo: bool = False
    au_dlg_editar: bool = False
    au_dlg_password: bool = False
    au_dlg_base: bool = False

    # Cambio de base de datos (LIMPIA / MIGRADA)
    au_base_destino: str = ""
    au_base_error: str = ""

    # Feedback
    au_error: str = ""
    au_ok: str = ""

    @rx.var
    def au_roles(self) -> list[str]:
        return ["SECRETARIA", "MEDICO_CONSULTA", "MEDICO_ATENCION", "ADMIN"]

    @rx.var
    def au_base_actual(self) -> str:
        return base_actual()

    @rx.var
    def au_base_migrada_disponible(self) -> bool:
        return base_migrada_disponible()

    # ── Setters para formulario nuevo ─────────────────────────────────────────
    def set_au_n_nombre(self, v: str):       self.au_n_nombre      = v
    def set_au_n_especialidad(self, v: str): self.au_n_especialidad = v
    def set_au_n_cod_esp(self, v: str):      self.au_n_cod_esp     = v
    def set_au_n_celular(self, v: str):      self.au_n_celular     = v
    def set_au_n_email(self, v: str):        self.au_n_email       = v
    def set_au_n_usuario(self, v: str):      self.au_n_usuario     = v
    def set_au_n_clave(self, v: str):        self.au_n_clave       = v
    def set_au_n_clave2(self, v: str):       self.au_n_clave2      = v
    def set_au_n_rol(self, v: str):          self.au_n_rol         = v
    def set_au_n_perfil_alcance(self, v: str): self.au_n_perfil_alcance = v

    # ── Setters para formulario editar ────────────────────────────────────────
    def set_au_e_nombre(self, v: str):       self.au_e_nombre      = v
    def set_au_e_especialidad(self, v: str): self.au_e_especialidad = v
    def set_au_e_cod_esp(self, v: str):      self.au_e_cod_esp     = v
    def set_au_e_celular(self, v: str):      self.au_e_celular     = v
    def set_au_e_email(self, v: str):        self.au_e_email       = v
    def set_au_e_usuario(self, v: str):      self.au_e_usuario     = v
    def set_au_e_rol(self, v: str):          self.au_e_rol         = v
    def set_au_e_perfil_alcance(self, v: str): self.au_e_perfil_alcance = v
    def set_au_e_estado(self, v: int):       self.au_e_estado      = v

    # ── Setters para formulario contraseña ────────────────────────────────────
    def set_au_p_clave(self, v: str):        self.au_p_clave       = v
    def set_au_p_clave2(self, v: str):       self.au_p_clave2      = v

    # ── Setters para diálogos ─────────────────────────────────────────────────
    def set_au_dlg_nuevo(self, v: bool):     self.au_dlg_nuevo     = v
    def set_au_dlg_editar(self, v: bool):    self.au_dlg_editar    = v
    def set_au_dlg_password(self, v: bool):  self.au_dlg_password  = v
    def set_au_dlg_base(self, v: bool):      self.au_dlg_base      = v

    def au_cargar(self):
        if not self.puede_admin:
            return
        with Session(get_engine()) as s:
            self.au_lista = listar_usuarios(s)

    # ── Nuevo usuario ─────────────────────────────────────────────────────────

    def au_abrir_nuevo(self):
        if not self.puede_admin:
            return
        self.au_n_nombre = ""
        self.au_n_especialidad = ""
        self.au_n_cod_esp = ""
        self.au_n_celular = ""
        self.au_n_email = ""
        self.au_n_usuario = ""
        self.au_n_clave = ""
        self.au_n_clave2 = ""
        self.au_n_rol = "MEDICO_ATENCION"
        self.au_n_perfil_alcance = "TT"
        self.au_error = ""
        self.au_dlg_nuevo = True

    def au_cancelar_nuevo(self):
        self.au_dlg_nuevo = False
        self.au_error = ""

    def au_crear(self):
        if not self.puede_admin:
            return
        if not self.au_n_nombre.strip():
            self.au_error = "El nombre completo es obligatorio."
            return
        if not self.au_n_usuario.strip():
            self.au_error = "El nombre de usuario es obligatorio."
            return
        if not self.au_n_clave:
            self.au_error = "La contraseña es obligatoria."
            return
        if self.au_n_clave != self.au_n_clave2:
            self.au_error = "Las contraseñas no coinciden."
            return
        try:
            with Session(get_engine()) as s:
                crear_usuario(
                    s,
                    nombre=self.au_n_nombre.strip(),
                    especialidad=self.au_n_especialidad.strip(),
                    cod_esp=self.au_n_cod_esp.strip(),
                    celular=self.au_n_celular.strip(),
                    email=self.au_n_email.strip(),
                    usuario=self.au_n_usuario.strip(),
                    clave_plain=self.au_n_clave,
                    rol=self.au_n_rol,
                    alcance_lectura=self.au_n_perfil_alcance[0],
                    alcance_escritura=self.au_n_perfil_alcance[1],
                )
                self.au_lista = listar_usuarios(s)
        except Exception as e:
            self.au_error = f"Error: {str(e)}"
            return
        self.au_dlg_nuevo = False
        self.au_error = ""
        self.au_ok = "Usuario creado exitosamente."

    # ── Editar usuario ────────────────────────────────────────────────────────

    def au_abrir_editar(self, id_medico: int):
        if not self.puede_admin:
            return
        u = next((x for x in self.au_lista if x["id_medico"] == id_medico), None)
        if not u:
            return
        self.au_edit_id       = id_medico
        self.au_e_nombre      = u["nombre_medico"]
        self.au_e_especialidad = u["especialidad"]
        self.au_e_cod_esp     = u["cod_especialidad"]
        self.au_e_celular     = u["celular"]
        self.au_e_email       = u["email"]
        self.au_e_usuario     = u["usuario"]
        self.au_e_rol         = u["rol"]
        self.au_e_estado      = u["estado"]
        permisos_u              = u.get("permisos") or ""
        lectura_u   = "P" if len(permisos_u) > 1 and permisos_u[1] == "P" else "T"
        escritura_u = "P" if len(permisos_u) > 2 and permisos_u[2] == "P" else "T"
        self.au_e_perfil_alcance = lectura_u + escritura_u
        self.au_error         = ""
        self.au_dlg_editar    = True

    def au_cancelar_editar(self):
        self.au_dlg_editar = False
        self.au_error = ""

    def au_guardar_edicion(self):
        if not self.puede_admin:
            return
        if not self.au_e_nombre.strip():
            self.au_error = "El nombre completo es obligatorio."
            return
        if not self.au_e_usuario.strip():
            self.au_error = "El nombre de usuario es obligatorio."
            return
        try:
            with Session(get_engine()) as s:
                actualizar_usuario(
                    s,
                    id_medico=self.au_edit_id,
                    nombre=self.au_e_nombre.strip(),
                    especialidad=self.au_e_especialidad.strip(),
                    cod_esp=self.au_e_cod_esp.strip(),
                    celular=self.au_e_celular.strip(),
                    email=self.au_e_email.strip(),
                    usuario=self.au_e_usuario.strip(),
                    rol=self.au_e_rol,
                    estado=self.au_e_estado,
                    alcance_lectura=self.au_e_perfil_alcance[0],
                    alcance_escritura=self.au_e_perfil_alcance[1],
                )
                self.au_lista = listar_usuarios(s)
        except Exception as e:
            self.au_error = f"Error: {str(e)}"
            return
        self.au_dlg_editar = False
        self.au_error = ""
        self.au_ok = "Usuario actualizado."

    def au_toggle_estado(self, id_medico: int):
        if not self.puede_admin:
            return
        u = next((x for x in self.au_lista if x["id_medico"] == id_medico), None)
        if not u:
            return
        nuevo_estado = 0 if u["estado"] == 1 else 1
        permisos_u = u.get("permisos") or ""
        lectura_u   = "P" if len(permisos_u) > 1 and permisos_u[1] == "P" else "T"
        escritura_u = "P" if len(permisos_u) > 2 and permisos_u[2] == "P" else "T"
        try:
            with Session(get_engine()) as s:
                actualizar_usuario(
                    s,
                    id_medico=id_medico,
                    nombre=u["nombre_medico"],
                    especialidad=u["especialidad"],
                    cod_esp=u["cod_especialidad"],
                    celular=u["celular"],
                    email=u["email"],
                    usuario=u["usuario"],
                    rol=u["rol"],
                    estado=nuevo_estado,
                    alcance_lectura=lectura_u,
                    alcance_escritura=escritura_u,
                )
                self.au_lista = listar_usuarios(s)
        except Exception as e:
            self.au_error = str(e)

    # ── Resetear contraseña ───────────────────────────────────────────────────

    def au_abrir_password(self, id_medico: int):
        if not self.puede_admin:
            return
        u = next((x for x in self.au_lista if x["id_medico"] == id_medico), None)
        self.au_p_id     = id_medico
        self.au_p_nombre = u["nombre_medico"] if u else ""
        self.au_p_clave  = ""
        self.au_p_clave2 = ""
        self.au_error    = ""
        self.au_dlg_password = True

    def au_cancelar_password(self):
        self.au_dlg_password = False
        self.au_error = ""

    def au_guardar_password(self):
        if not self.puede_admin:
            return
        if not self.au_p_clave:
            self.au_error = "Ingrese la nueva contraseña."
            return
        if len(self.au_p_clave) < 6:
            self.au_error = "La contraseña debe tener al menos 6 caracteres."
            return
        if self.au_p_clave != self.au_p_clave2:
            self.au_error = "Las contraseñas no coinciden."
            return
        try:
            with Session(get_engine()) as s:
                resetear_clave(s, self.au_p_id, self.au_p_clave)
        except Exception as e:
            self.au_error = f"Error: {str(e)}"
            return
        self.au_dlg_password = False
        self.au_error = ""
        self.au_ok = "Contraseña actualizada."

    def au_cerrar_ok(self):
        self.au_ok = ""

    # ── Cambio de base de datos (LIMPIA / MIGRADA) ───────────────────────────

    def au_abrir_cambiar_base(self, destino: str):
        if not self.puede_admin:
            return
        destino = destino.upper()
        if destino == base_actual():
            return
        if destino == "MIGRADA" and not base_migrada_disponible():
            self.au_base_error = "La base MIGRADA no está configurada (GESMED_DB_URL_M)."
            return
        self.au_base_destino = destino
        self.au_base_error = ""
        self.au_dlg_base = True

    def au_cancelar_cambiar_base(self):
        self.au_dlg_base = False
        self.au_base_error = ""

    def au_confirmar_cambiar_base(self):
        if not self.puede_admin:
            return
        try:
            cambiar_base(self.au_base_destino)
        except Exception as e:
            self.au_base_error = f"Error: {str(e)}"
            return
        self.au_dlg_base = False
        self.au_base_error = ""
        # Recarga forzada de esta sesión: evita que quede información en
        # memoria (State ya instanciado) proveniente de la base anterior.
        yield rx.call_script("window.location.replace('/')")


class ExamenesState(State):
    """Mantenimiento (CRUD) de examen_tipo y examen_catalogo — solo ADMIN."""

    # Listados
    ex_tipos: list[dict] = []
    ex_catalogo: list[dict] = []

    # Tipo seleccionado a la izquierda (0 = ninguno)
    ex_tipo_sel: int = 0
    ex_tipo_sel_nombre: str = ""

    # Formulario: tipo (nuevo/editar)
    ex_t_id: int = 0
    ex_t_nombre: str = ""
    ex_dlg_tipo: bool = False

    # Formulario: catálogo (nuevo/editar)
    ex_c_id: int = 0
    ex_c_alias: str = ""
    ex_c_nombre: str = ""
    ex_dlg_catalogo: bool = False

    # Feedback
    ex_error: str = ""
    ex_ok: str = ""

    def set_ex_t_nombre(self, v: str): self.ex_t_nombre = v
    def set_ex_c_alias(self, v: str):  self.ex_c_alias  = v
    def set_ex_c_nombre(self, v: str): self.ex_c_nombre = v
    def set_ex_dlg_tipo(self, v: bool):      self.ex_dlg_tipo = v
    def set_ex_dlg_catalogo(self, v: bool):  self.ex_dlg_catalogo = v

    def ex_cargar(self):
        if not self.puede_admin:
            return
        with Session(get_engine()) as s:
            self.ex_tipos = listar_examen_tipos(s)
        if self.ex_tipos and not any(t["id_examen_tipo"] == self.ex_tipo_sel for t in self.ex_tipos):
            self.ex_tipo_sel = 0
        if self.ex_tipo_sel:
            self._ex_cargar_catalogo()
        else:
            self.ex_catalogo = []
            self.ex_tipo_sel_nombre = ""

    def _ex_cargar_catalogo(self):
        with Session(get_engine()) as s:
            self.ex_catalogo = listar_examen_catalogo(s, self.ex_tipo_sel)

    def ex_seleccionar_tipo(self, id_examen_tipo: int):
        if not self.puede_admin:
            return
        self.ex_tipo_sel = id_examen_tipo
        t = next((x for x in self.ex_tipos if x["id_examen_tipo"] == id_examen_tipo), None)
        self.ex_tipo_sel_nombre = t["examen_tipo"] if t else ""
        self._ex_cargar_catalogo()

    # ── Tipo: nuevo / editar ──────────────────────────────────────────────────

    def ex_abrir_nuevo_tipo(self):
        if not self.puede_admin:
            return
        self.ex_t_id = 0
        self.ex_t_nombre = ""
        self.ex_error = ""
        self.ex_dlg_tipo = True

    def ex_abrir_editar_tipo(self, id_examen_tipo: int):
        if not self.puede_admin:
            return
        t = next((x for x in self.ex_tipos if x["id_examen_tipo"] == id_examen_tipo), None)
        if not t:
            return
        self.ex_t_id = id_examen_tipo
        self.ex_t_nombre = t["examen_tipo"]
        self.ex_error = ""
        self.ex_dlg_tipo = True

    def ex_cancelar_tipo(self):
        self.ex_dlg_tipo = False
        self.ex_error = ""

    def ex_guardar_tipo(self):
        if not self.puede_admin:
            return
        nombre = self.ex_t_nombre.strip()
        if not nombre:
            self.ex_error = "El nombre del tipo es obligatorio."
            return
        try:
            with Session(get_engine()) as s:
                if self.ex_t_id:
                    actualizar_examen_tipo(s, self.ex_t_id, nombre)
                else:
                    crear_examen_tipo(s, nombre)
                self.ex_tipos = listar_examen_tipos(s)
        except Exception as e:
            self.ex_error = f"Error: {str(e)}"
            return
        self.ex_dlg_tipo = False
        self.ex_error = ""
        self.ex_ok = "Tipo de examen guardado."

    def ex_eliminar_tipo(self, id_examen_tipo: int):
        if not self.puede_admin:
            return
        try:
            with Session(get_engine()) as s:
                eliminar_examen_tipo(s, id_examen_tipo)
                self.ex_tipos = listar_examen_tipos(s)
        except Exception as e:
            self.ex_error = str(e)
            return
        if self.ex_tipo_sel == id_examen_tipo:
            self.ex_tipo_sel = 0
            self.ex_tipo_sel_nombre = ""
            self.ex_catalogo = []
        self.ex_ok = "Tipo de examen eliminado."

    # ── Catálogo: nuevo / editar ──────────────────────────────────────────────

    def ex_abrir_nuevo_catalogo(self):
        if not self.puede_admin or not self.ex_tipo_sel:
            return
        self.ex_c_id = 0
        self.ex_c_alias = ""
        self.ex_c_nombre = ""
        self.ex_error = ""
        self.ex_dlg_catalogo = True

    def ex_abrir_editar_catalogo(self, id_examen: int):
        if not self.puede_admin:
            return
        c = next((x for x in self.ex_catalogo if x["id_examen"] == id_examen), None)
        if not c:
            return
        self.ex_c_id = id_examen
        self.ex_c_alias = c["examen_alias"]
        self.ex_c_nombre = c["examen_nombre"]
        self.ex_error = ""
        self.ex_dlg_catalogo = True

    def ex_cancelar_catalogo(self):
        self.ex_dlg_catalogo = False
        self.ex_error = ""

    def ex_guardar_catalogo(self):
        if not self.puede_admin or not self.ex_tipo_sel:
            return
        alias = self.ex_c_alias.strip().upper()
        nombre = self.ex_c_nombre.strip().upper()
        if not nombre:
            self.ex_error = "El nombre del examen es obligatorio."
            return
        try:
            with Session(get_engine()) as s:
                if self.ex_c_id:
                    actualizar_examen_catalogo(s, self.ex_c_id, alias, nombre)
                else:
                    crear_examen_catalogo(s, self.ex_tipo_sel, alias, nombre)
                self.ex_catalogo = listar_examen_catalogo(s, self.ex_tipo_sel)
        except Exception as e:
            self.ex_error = f"Error: {str(e)}"
            return
        self.ex_dlg_catalogo = False
        self.ex_error = ""
        self.ex_ok = "Examen de catálogo guardado."

    def ex_eliminar_catalogo(self, id_examen: int):
        if not self.puede_admin:
            return
        try:
            with Session(get_engine()) as s:
                eliminar_examen_catalogo(s, id_examen)
                self.ex_catalogo = listar_examen_catalogo(s, self.ex_tipo_sel)
        except Exception as e:
            self.ex_error = str(e)
            return
        self.ex_ok = "Examen de catálogo eliminado."

    def ex_cerrar_ok(self):
        self.ex_ok = ""
