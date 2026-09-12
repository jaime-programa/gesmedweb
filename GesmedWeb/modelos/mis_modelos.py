import reflex as rx
import datetime
from sqlmodel import Field, SQLModel, create_engine, Relationship
from sqlalchemy import DECIMAL, Column, Text, JSON, SmallInteger
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from decimal import Decimal
from typing import Optional

class Registro(SQLModel, table=True):
    id: Optional[int] | None= Field(default=None,primary_key=True)
    nombre:str
    puerto: str
    cod_error:str

class Paciente(SQLModel, table=True):
    __tablename__='paciente'
    nro_hclinica: Optional[int] | None = Field(default=None, primary_key=True)
    nombre_completo: bytes
    cedula_id: Optional[bytes] = Field(default=None)
    sexo: str = Field(default="Femenino")
    grupo_sanguineo: str
    fecha_nacimiento: datetime.date
    pais_nacimiento: str
    estado_civil: str
    ciudad_reside: str
    direccion_reside: bytes
    tf_celular: bytes
    email: Optional[bytes] = Field(default=None)
    seguro: Optional[str] = Field(default=None)
    observacion: Optional[bytes] = Field(default=None)
    fecha_creacion: datetime.datetime
    es_activo: int = Field(default=1)


class Points(SQLModel,table=True):
    __tablename__='points'
    id_medico:Optional[int]| None=Field(default=None,primary_key=True)
    nombre_medico:str
    especialidad:str
    cod_especialidad:str
    celular:str
    email:str
    usuario:str
    clave:str
    permisos:str
    estado:int
    # ── Roles (añadido en 016_rol_usuario.sql) ───────────────────────────────
    rol: str = Field(default="MEDICO_ATENCION", max_length=20)
    # ── Agenda (añadidos en 015_agenda_medica.sql) ────────────────────────────
    modo_agenda:   str           = Field(default="LIBRE", max_length=5)
    color_agenda:  str           = Field(default="#3B82F6", max_length=7)
    google_cal_id: Optional[str] = Field(default=None, max_length=200)
    
class Cie10(SQLModel,table=True):
    __tablename__='cie10'
    cod_cie10:Optional[str] | None=Field(default=None,primary_key=True)
    grupo:str
    categoria:str
    nomdiagnostico:str

class Atencion(SQLModel,table=True):
    __tablename__='atencion'
    id_atencion: Optional[int] |None =Field(default=None, primary_key=True)
    lk_paciente:Optional[int] |None =Field(default=None,foreign_key='paciente.nro_hclinica')
    lk_medico:Optional[int] | None = Field(default=None,foreign_key='points.id_medico')
    fecha_atencion:datetime.datetime
    motivo_consulta:str
    revision_sistemas: str = Field(sa_column=Column(MEDIUMTEXT, nullable=False))
    subjetivo:         str = Field(sa_column=Column(MEDIUMTEXT, nullable=False))
    objetivo:          str = Field(sa_column=Column(MEDIUMTEXT, nullable=False))
    analisis:          str = Field(sa_column=Column(MEDIUMTEXT, nullable=False))
    plan:              str = Field(sa_column=Column(MEDIUMTEXT, nullable=False))
    #cie10: Optional[Cie10] = Relationship(back_populates="atencion")

class Diagnostico(SQLModel,table=True):
    __tablename__='diagnostico'
    id_diagnostico: Optional[int]|None=Field(default=None,primary_key=True)
    lk_paciente:Optional[int]=Field(default=None,foreign_key="paciente.nro_hclinica")
    lk_cie10:Optional[str] = Field(default=None,foreign_key='cie10.cod_cie10')
    tipo:str
    fecha_diagnostico:datetime.date
    fecha_inicio_aparente:datetime.date
    lk_medico:Optional[int] | None = Field(default=None,foreign_key='points.id_medico')
    observaciones: Optional[bytes] = Field(default=None)
    noduplicados:str
     # Relación con CIE10
    #cie10: Optional[Cie10] = Relationship(back_populates="diagnosticos")

class SolicitudInterconsulta(SQLModel,table=True):
    __tablename__='solicitud_interconsulta'
    id_solicitud:       Optional[int] | None = Field(default=None, primary_key=True)
    lk_paciente:        int = Field(foreign_key="paciente.nro_hclinica")
    lk_medico_principal: int = Field(foreign_key="points.id_medico")
    lk_medico_auxiliar:  int = Field(foreign_key="points.id_medico")
    fecha_solicitud:    datetime.date
    fecha_expiracion:   datetime.date
    motivo:             str = Field(sa_column=Column(Text, nullable=False))
    estatus:            str = Field(default="activa", max_length=10)

class Interconsulta(SQLModel,table=True):
    __tablename__='interconsulta'
    id_interconsulta: Optional[int] | None = Field(default=None, primary_key=True)
    lk_atencion:        int = Field(foreign_key="atencion.id_atencion")
    lk_medico_auxiliar: int = Field(foreign_key="points.id_medico")
    reporte_final:      Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

class Rel_atencion_diagnostico(SQLModel,table=True):
    __tablename__='rel_atencion_diagnostico'
    id_relacion: Optional[int] | None=Field(default=None,primary_key=True)
    lk_atencion: Optional[int] = Field(default=None,foreign_key='atencion.id_atencion')
    lk_diagnostico: Optional[int] = Field(default=None,foreign_key='diagnostico.id_diagnostico')
    noduplicarelacion:str = Field(index=True,unique=True)

class ListaSignosVitales(SQLModel, table=True):
    __tablename__ = "lista_signosvitales"
    id_signo_vital: Optional[int] | None = Field(default=None, primary_key=True)
    nombre:         str          = Field(max_length=60)
    codigo:         str          = Field(max_length=20)
    unidad:         Optional[str] = Field(default=None, max_length=20)
    decimales:      int          = Field(default=1)
    valor_min:      Optional[Decimal] = Field(default=None, sa_column=Field(DECIMAL(6, 2)))
    valor_max:      Optional[Decimal] = Field(default=None, sa_column=Field(DECIMAL(6, 2)))
    orden_display:  int          = Field(default=99)
    es_activo:      int          = Field(default=1)

class SignosVitales(SQLModel, table=True):
    __tablename__ = "signosvitales"
    id:             Optional[int] | None = Field(default=None, primary_key=True)
    lk_atencion:    int  = Field(foreign_key="atencion.id_atencion")
    lk_signo_vital: int  = Field(foreign_key="lista_signosvitales.id_signo_vital")
    valor:          Decimal = Field(sa_column=Field(DECIMAL(6, 2)))

class SeguroMedico(SQLModel, table=True):
    __tablename__ = "seguro_medico"
    id_seguro: Optional[int] | None = Field(default=None, primary_key=True)
    nombre_seguro: str = Field(max_length=25)
    condiciones: str = Field(sa_column=Column(MEDIUMTEXT, nullable=False))
    esta_activo: int

class MedicamentoTipo(SQLModel, table=True):
    __tablename__ = "medicamento_tipo"
    id_tipo:     Optional[int] | None = Field(default=None, primary_key=True)
    nombre_tipo: str = Field(max_length=20)

class Medicamento(SQLModel, table=True):
    __tablename__ = "medicamentos"
    cod_gen:          Optional[int] | None = Field(default=None, primary_key=True)
    nombre_generico:  str  = Field(max_length=80)
    nombre_comercial: str  = Field(max_length=30)
    tipo:             int  = Field(default=1, foreign_key="medicamento_tipo.id_tipo")
    es_activo:        int  = Field(default=1)

class MedicamentoPresentacion(SQLModel, table=True):
    __tablename__ = "medicamento_presentacion"
    id_presentacion:     Optional[int] | None = Field(default=None, primary_key=True)
    nombre_presentacion: str  = Field(max_length=30)
    en_uso:              int  = Field(default=1)

class Prescripcion(SQLModel, table=True):
    __tablename__ = "prescripcion"
    id_prescripcion:    Optional[int] | None = Field(default=None, primary_key=True)
    lk_paciente:        Optional[int]  = Field(default=None, foreign_key="paciente.nro_hclinica")
    lk_atencion:        Optional[int]  = Field(default=None, foreign_key="atencion.id_atencion")
    fecha_prescripcion: datetime.date
    concentracion:      bytes                               # AES-256-GCM BLOB
    cantidad:           int  = Field(default=1)
    lk_presentacion:    Optional[int]  = Field(default=None, foreign_key="medicamento_presentacion.id_presentacion")
    indicaciones:       bytes                               # AES-256-GCM BLOB
    lk_generico:        Optional[int]  = Field(default=None, foreign_key="medicamentos.cod_gen")

class PrescripcionCuidados(SQLModel, table=True):
    __tablename__ = "prescripcion_cuidados"
    id_cuidados:        Optional[int] | None = Field(default=None, primary_key=True)
    lk_atencion:        int            = Field(foreign_key="atencion.id_atencion")
    cuidados_generales: Optional[str]  = Field(default=None, sa_column=Column(Text))
    fecha_emision:      Optional[datetime.date] = Field(default=None)

class Alergia(SQLModel, table=True):
    __tablename__ = "alergia"
    id_alergia:       Optional[int] | None = Field(default=None, primary_key=True)
    lk_paciente:      int  = Field(foreign_key="paciente.nro_hclinica")
    sustancia_alergia: str = Field(max_length=100)
    detalles:         Optional[str]  = Field(default=None, sa_column=Column(Text))
    fecha_reportada:  Optional[datetime.date] = Field(default=None)

class ExamenesLaboratorioPedido(SQLModel, table=True):
    __tablename__ = "examenes_laboratorio_pedido"
    id_pedido:    Optional[int] | None = Field(default=None, primary_key=True)
    lk_paciente:  Optional[int]        = Field(default=None, foreign_key="paciente.nro_hclinica")
    lk_atencion:  Optional[int]        = Field(default=None, foreign_key="atencion.id_atencion")
    fecha_pedido: datetime.date
    lk_examen:    int                  = Field(foreign_key="examenes_laboratorio_catalogo.id_examen")

class ExamenesLaboratorioGrupo(SQLModel, table=True):
    __tablename__ = "examenes_laboratorio_grupo"
    id_grupo:     Optional[int] | None = Field(default=None, primary_key=True)
    nombre_grupo: str = Field(max_length=80)

class ExamenesLaboratorioCatalogo(SQLModel, table=True):
    __tablename__ = "examenes_laboratorio_catalogo"
    id_examen:     Optional[int] | None  = Field(default=None, primary_key=True)
    nombre_examen: str                   = Field(max_length=120)
    lk_grupo:      Optional[int]         = Field(default=None, foreign_key="examenes_laboratorio_grupo.id_grupo")
    activo:        int                   = Field(default=1)
    unidad:        Optional[str]         = Field(default=None, max_length=15)
    minimo:        Optional[Decimal]     = Field(default=None, sa_column=Column(DECIMAL(6, 2)))
    maximo:        Optional[Decimal]     = Field(default=None, sa_column=Column(DECIMAL(6, 2)))
    es_pedido:     Optional[bool]        = Field(default=True)
    es_resultado:  Optional[bool]        = Field(default=True)
    lk_padre:      Optional[int]         = Field(default=None, foreign_key="examenes_laboratorio_catalogo.id_examen")


# ── Motor de reportes paramétrico ────────────────────────────────────────────

class ReporteImpreso(SQLModel, table=True):
    __tablename__ = "reporte_impreso"
    id_impreso:     Optional[int] | None = Field(default=None, primary_key=True)
    nombre_reporte: str  = Field(max_length=50)
    nombre_fuente:  str  = Field(default="Arial Narrow", max_length=50)
    explica:        str  = Field(default="", max_length=200)


class ReporteImagen(SQLModel, table=True):
    __tablename__ = "reporte_imagen"
    id_imagen:    Optional[int] | None = Field(default=None, primary_key=True)
    lk_impreso:   int  = Field(foreign_key="reporte_impreso.id_impreso")
    nombre_archivo: str = Field(max_length=80)   # archivo en templates/, ej. "logotipo.png"
    celda:        str  = Field(max_length=10)    # celda de anclaje, ej. "A1"
    ancho:        int  = Field(default=100)      # px
    alto:         int  = Field(default=40)       # px
    orden:        int  = Field(default=1)        # orden de inserción


class ReporteSeccion(SQLModel, table=True):
    __tablename__ = "reporte_seccion"
    id_seccion:           Optional[int] | None = Field(default=None, primary_key=True)
    lk_impreso:           int  = Field(foreign_key="reporte_impreso.id_impreso")
    orden:                int  = Field(default=1)
    instruccion_sql:      Optional[str] = Field(default=None, sa_column=Column(Text))
    parametros_in:        Optional[list] = Field(default=None, sa_column=Column(JSON))
    explica:              str  = Field(default="", max_length=200)
    es_activa:            int  = Field(default=1)
    # ── Motor de bucle ──────────────────────────────────────────────────────────
    modo_bucle:           str  = Field(default="N", max_length=1)  # N=normal F=plano G=agrupado
    paso_fila:            int  = Field(default=1)
    max_iteraciones:      int  = Field(default=10)
    lk_seccion_ancla:     Optional[int] = Field(default=None)      # FK manual → reporte_seccion
    ancla_gap:            int  = Field(default=0)
    condicion_activa_sql: Optional[str] = Field(default=None, sa_column=Column(Text))
    campo_grupo:          Optional[str] = Field(default=None, max_length=60)
    num_columnas:         int  = Field(default=1)
    paso_columna:         int  = Field(default=0)
    slot_height:          int  = Field(default=10)
    titulo_seccion:       Optional[str] = Field(default=None, max_length=200)


class AntecedenteFamiliar(SQLModel, table=True):
    __tablename__ = "antecedente_familiar"
    id_antecedente: Optional[int] | None = Field(default=None, primary_key=True)
    lk_paciente:    int = Field(foreign_key="paciente.nro_hclinica")
    descripcion:    bytes  # AES-256-GCM BLOB, texto plano ≥ 500 chars
    fecha_registro: datetime.date


class ReporteCelda(SQLModel, table=True):
    __tablename__ = "reporte_celda"
    id_celda:   Optional[int] | None = Field(default=None, primary_key=True)
    lk_seccion: int  = Field(foreign_key="reporte_seccion.id_seccion")
    variable:   Optional[str] = Field(default=None, max_length=60)
    fila:       int
    columna:    int
    pre_fijo:   str  = Field(default="", max_length=200)
    post_fijo:  str  = Field(default="", max_length=200)
    formato:    str  = Field(default="09.01.01.00.NLU.0000.N", max_length=22)
    explica:    str  = Field(default="", max_length=200)
    es_activa:  int  = Field(default=1)
    tipo_celda: str  = Field(default="D", max_length=1)  # D=detalle G=cabecera de grupo

class Certificado(SQLModel, table=True):
    __tablename__ = "certificado"
    id_certificado:    Optional[int] | None = Field(default=None, primary_key=True)
    lk_atencion:       int  = Field(foreign_key="atencion.id_atencion")
    fecha_certificado: datetime.datetime = Field(default_factory=datetime.datetime.now)
    reposo_desde:      datetime.date
    reposo_hasta:      datetime.date
    contingencia:      str  = Field(default="", max_length=200)
    presenta_sintomas: int  = Field(default=0)
    aislamiento:       int  = Field(default=0)
    ocupacion:         str  = Field(default="", max_length=200)
    lugar_trabajo:     str  = Field(default="", max_length=200)
    observacion:       str  = Field(default="", max_length=800)
    
class OtrosExamenesTipo(SQLModel,table=True):
    __tablename__="examen_tipo"
    id_examen_tipo:    Optional[int] | None = Field(default=None, primary_key=True)
    examen_tipo:       str = Field(default="",max_length=40)
    

class OtrosExamenesCatalogo(SQLModel,table=True):
    __tablename__="examen_catalogo"
    id_examen:    Optional[int] | None = Field(default=None, primary_key=True)
    lk_examen_tipo:     int = Field(foreign_key="examen_tipo.id_examen_tipo")
    examen_alias:       str = Field(default="",max_length=6)
    examen_nombre:      str = Field(default="",max_length=40)
    

class OtrosExamenesPedido(SQLModel,table=True):
    __tablename__="examen_pedido"
    id_examen_pedido:      Optional[int] | None = Field(default=None, primary_key=True)
    lk_atencion:    int = Field(foreign_key="atencion.id_atencion")
    lk_catalogo:    int = Field(foreign_key="examen_catalogo.id_examen")
    lk_diagnostico: int = Field(foreign_key="diagnostico.id_diagnostico")
    detalle_pedido: str = Field(default = "Favor realizar un",max_length=150)


# ── Módulo de agenda médica (015_agenda_medica.sql) ───────────────────────────

class TipoCita(SQLModel, table=True):
    __tablename__ = "tipo_cita"
    id_tipo_cita:  Optional[int] | None = Field(default=None, primary_key=True)
    nombre:        str           = Field(max_length=60)
    categoria:     str           = Field(default="CONSULTA", max_length=15)
    duracion_min:  Optional[int] = Field(default=30)
    color_hex:     str           = Field(default="#3B82F6", max_length=7)
    requiere_conf: int           = Field(default=0)
    es_activo:     int           = Field(default=1)


class HorarioMedico(SQLModel, table=True):
    __tablename__ = "horario_medico"
    id_horario:  Optional[int] | None = Field(default=None, primary_key=True)
    lk_medico:   int                  = Field(foreign_key="points.id_medico")
    dia_semana:  int                  = Field(default=0)
    hora_inicio: datetime.time
    hora_fin:    datetime.time


class BloqueoHorario(SQLModel, table=True):
    __tablename__ = "bloqueo_horario"
    id_bloqueo:   Optional[int] | None = Field(default=None, primary_key=True)
    lk_medico:    int                  = Field(foreign_key="points.id_medico")
    fecha_inicio: datetime.datetime
    fecha_fin:    datetime.datetime
    motivo:       Optional[str]        = Field(default=None, max_length=200)


class Cita(SQLModel, table=True):
    __tablename__ = "cita"
    id_cita:         Optional[int] | None = Field(default=None, primary_key=True)
    lk_paciente:     Optional[int]        = Field(default=None, foreign_key="paciente.nro_hclinica")
    lk_medico:       int                  = Field(foreign_key="points.id_medico")
    lk_tipo_cita:    int                  = Field(foreign_key="tipo_cita.id_tipo_cita")
    inicio:          datetime.datetime
    fin:             datetime.datetime
    estado:          str                  = Field(default="AGENDADA", max_length=15)
    notas:           Optional[str]        = Field(default=None, sa_column=Column(Text))
    google_event_id: Optional[str]        = Field(default=None, max_length=200)
    # Paciente nuevo (datos temporales hasta completar registro)
    px_nombre:       Optional[str]        = Field(default=None, max_length=150)
    px_sexo:         Optional[str]        = Field(default=None, max_length=10)
    px_celular:      Optional[str]        = Field(default=None, max_length=20)
    px_ciudad:       Optional[str]        = Field(default=None, max_length=60)
    px_seguro:       Optional[str]        = Field(default=None, max_length=30)

class ResultadosLaboratorio(SQLModel,table=True):
    __tablename__="resultados_laboratorio"
    id_resultado:       Optional[int] | None = Field(default=None, primary_key=True)
    fecha_examen:       datetime.date
    lk_paciente:        Optional[int]   = Field(default=None, foreign_key="paciente.nro_hclinica")
    lk_examen:          Optional[int]   = Field(default=None, foreign_key="examenes_laboratorio_catalogo.id_examen")
    lk_pedido:          Optional[int]   = Field(default=None, foreign_key="examenes_laboratorio_pedido.id_pedido")
    lk_imagen_fuente:   Optional[int]   = Field(default=None, foreign_key="imagen.id_imagen")
    valor_numerico:     Optional[Decimal] = Field(default=None, sa_column=Column(DECIMAL(8, 2)))
    valor_texto:        Optional[str]   = Field(default=None, max_length=30)
    en_rango:           Optional[str]   = Field(default=None, max_length=10) # EN_RANGO | SOBRE | BAJO | None si valor_texto
    observacion:        Optional[str]   = Field(default=None, sa_column=Column(Text))

class ResultadosImagenes(SQLModel,table=True):
    __tablename__="resultados_imagen"
    id_resultado:       Optional[int] | None = Field(default=None, primary_key=True)
    fecha_imagen:       datetime.date
    lk_paciente:        Optional[int]   = Field(default=None, foreign_key="paciente.nro_hclinica")
    lk_diagnostico:     Optional[int]   = Field(default=None, foreign_key="diagnostico.id_diagnostico")
    lk_examen:          Optional[int]   = Field(default=None, foreign_key="examen_catalogo.id_examen")
    lk_pedido:          Optional[int]   = Field(default=None, foreign_key="examen_pedido.id_examen_pedido")
    hallazgos:          Optional[str]   = Field(default=None, sa_column=Column(Text))
    alias:              Optional[str]   = Field(default=None, max_length=80)

class Imagenes(SQLModel,table=True):
    __tablename__="imagen"
    id_imagen:          Optional[int] | None = Field(default=None, primary_key=True)
    lk_resultado_imagen:Optional[int]   = Field(default=None, foreign_key="resultados_imagen.id_resultado")
    lk_atencion:        Optional[int]   = Field(default=None, foreign_key="atencion.id_atencion")  # contexto de subida; para construir nombre de archivo
    orden:              int             = Field(default=0)
    rotacion:           int             = Field(default=0, sa_column=Column(SmallInteger, default=0))  # 0|90|180|270
    ubicacion:          Optional[str]   = Field(default=None, max_length=80)  # ubicación anatómica
    detalle:            Optional[str]   = Field(default=None, max_length=100)

class Marcas(SQLModel,table=True):
    __tablename__="marca"
    id_marca:           Optional[int] | None = Field(default=None, primary_key=True)
    x_centro:           int             = Field(default=100)
    y_centro:           int             = Field(default=100)
    tipo_marca:         str             = Field(default="c")    #c:circulo  f:flecha  t:texto
    radio:              int             = Field(default=0)
    cuadrante:          int             = Field(default=1)  #1:45º 2:135º 3:225º 4:315º
    font:               Optional[int]   = Field(default=14) #Tamaño de fuente del texto de marca
    color:              Optional[str]   = Field(default="#ff0000")
    nivel:              Optional[int]   = Field(default=0)  #0 más bajo, sigue subiendo
    lk_imagen:          Optional[int]   = Field(foreign_key="imagen.id_imagen")
    observacion:        Optional[str]   = Field(default=None,max_length=30)
    x2:                 int             = Field(default=0)  # flecha: x cola
    y2:                 int             = Field(default=0)  # flecha: y cola
    grosor:             int             = Field(default=2)  # grosor de línea en píxeles
    

