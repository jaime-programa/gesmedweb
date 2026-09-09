from typing import List
from sqlmodel import Session, select,create_engine,or_, and_,asc,desc,func
import bcrypt as _bcrypt
#from sqlalchemy import or_, and_
from ..modelos.mis_modelos import (
    Paciente, Atencion, Diagnostico, Cie10, Rel_atencion_diagnostico,
    Points, SeguroMedico,
    Medicamento, MedicamentoTipo, MedicamentoPresentacion,
    Prescripcion, PrescripcionCuidados, Alergia,
    ListaSignosVitales, SignosVitales,
    ExamenesLaboratorioCatalogo, ExamenesLaboratorioGrupo, ExamenesLaboratorioPedido,
    AntecedenteFamiliar,
)
from decimal import Decimal
from ..crypto import GesmedCrypto
import datetime
import os

_URL_GESMED  = os.environ.get("GESMED_DB_URL",  "mysql+pymysql://med_admin:gesmed01@localhost:3306/gesmed")

engine = create_engine(_URL_GESMED, echo=False, pool_pre_ping=True)

def carga_medicos():
    with Session(engine) as session:
        statement=select(Points.id_medico,Points.nombre_medico,Points.especialidad,Points.cod_especialidad,Points.celular,Points.email,Points.permisos).where(Points.estado==1)
        resultados=session.exec(statement).all()
        medicos={r.id_medico:[r.nombre_medico,r.especialidad,r.cod_especialidad,r.celular,r.email,r.permisos] 
                 for r in resultados}
    return medicos

def carga_seguros() -> list[str]:
    with Session(engine) as session:
        statement = select(SeguroMedico.nombre_seguro).where(SeguroMedico.esta_activo == 1).order_by(SeguroMedico.nombre_seguro)
        return session.exec(statement).all()

def consultar_pacientes_por_nombre(session, filtro: str, medico_id: int = 1, solo_propios: bool = False):
    crypto = GesmedCrypto.para_medico(medico_id)
    statement = (
        select(
            Paciente.nro_hclinica,
            Paciente.nombre_completo,
            Paciente.cedula_id,
            Paciente.seguro,
            Paciente.fecha_nacimiento,
            Paciente.grupo_sanguineo,
            func.count(Atencion.id_atencion).label("numero_atenciones"),
        )
        .join(Atencion, Atencion.lk_paciente == Paciente.nro_hclinica, isouter=True)
        .group_by(Paciente.nro_hclinica)
    )
    if solo_propios:
        # "Solo mis pacientes" (permisos[1] == "P"): limita a pacientes con
        # al menos una atención propia, MÁS los que no tienen ninguna atención
        # todavía (recién creados, sin médico "dueño" — cualquiera debe poder
        # verlos para poder registrarles su primera atención). No restringe
        # el conteo de arriba (que sigue mostrando el total de cualquier médico).
        statement = statement.where(
            or_(
                Paciente.nro_hclinica.in_(
                    select(Atencion.lk_paciente).where(Atencion.lk_medico == medico_id)
                ),
                Paciente.nro_hclinica.not_in(select(Atencion.lk_paciente)),
            )
        )
    pacientes = session.exec(statement).all()

    # Pacientes "propios" del médico logueado (con al menos una atención suya),
    # para poder distinguirlos visualmente de los "ajenos" en la lista — se
    # calcula siempre, independiente de "solo_propios", porque un perfil con
    # lectura "T" también quiere ver esta distinción aunque no filtre nada.
    propios_ids = set(
        session.exec(
            select(Atencion.lk_paciente).where(Atencion.lk_medico == medico_id).distinct()
        ).all()
    )

    def _estado_propiedad(p) -> str:
        if p.numero_atenciones == 0:
            return "disponible"  # sin atenciones de nadie: cualquiera puede reclamarlo
        return "propio" if p.nro_hclinica in propios_ids else "ajeno"

    registros = [
        {
            "nro_hclinica": p.nro_hclinica,
            "nombre_completo": p.nombre_completo,   # bytes (BLOB)
            "cedula_id": p.cedula_id,               # bytes or None
            "edad": edad(p.fecha_nacimiento),
            "fecha_nacimiento": p.fecha_nacimiento,
            "seguro": p.seguro,
            "grupo_sanguineo": p.grupo_sanguineo,
            "cuantas_atenciones": p.numero_atenciones,
            "estado_propiedad": _estado_propiedad(p),
        }
        for p in pacientes
    ]

    if len(filtro.strip()) >= 3:
        return crypto.buscar_en_bloque(registros, "nombre_completo", filtro, ["cedula_id"])

    return [crypto.desencriptar_campos(r, ["nombre_completo", "cedula_id"]) for r in registros]

def historial_atenciones_con_cie10(session,paciente:int,filtro:str) -> List[dict]: 
    if len (filtro)>0:
        stmt = (
        select(
            Atencion.id_atencion,
            Atencion.lk_paciente,
            Atencion.lk_medico,
            Atencion.fecha_atencion,
            Atencion.motivo_consulta,
            Atencion.revision_sistemas,
            Atencion.subjetivo,
            Atencion.objetivo,
            Atencion.analisis,
            Atencion.plan,
            func.group_concat(Cie10.cod_cie10, ', ').label("codigos_cie10"),) # Agrega otros campos relevantes de Atencion
            .join(Rel_atencion_diagnostico, Rel_atencion_diagnostico.lk_atencion == Atencion.id_atencion)
            .join(Diagnostico, Diagnostico.id_diagnostico == Rel_atencion_diagnostico.lk_diagnostico)
            .join(Cie10, Cie10.cod_cie10 == Diagnostico.lk_cie10)
            .group_by(Atencion.id_atencion)
        ).where(and_(Atencion.lk_paciente==paciente,
                or_(
                Atencion.revision_sistemas.like(f"%{filtro}%"),
                Atencion.objetivo.like(f"%{filtro}%"),
                Atencion.subjetivo.like(f"%{filtro}%"),
                Atencion.analisis.like(f"%{filtro}%"),
                Atencion.motivo_consulta.like(f"%{filtro}%"),
                Atencion.plan.like(f"%{filtro}%"),))
                ).order_by(desc(Atencion.fecha_atencion))
    else:
        stmt = (
        select(
            Atencion.id_atencion,
            Atencion.lk_paciente,
            Atencion.lk_medico,
            Atencion.fecha_atencion,
            Atencion.motivo_consulta,
            Atencion.revision_sistemas,
            Atencion.subjetivo,
            Atencion.objetivo,
            Atencion.analisis,
            Atencion.plan,
            func.group_concat(Cie10.cod_cie10, ', ').label("codigos_cie10"),) # Agrega otros campos relevantes de Atencion
            .join(Rel_atencion_diagnostico, Rel_atencion_diagnostico.lk_atencion == Atencion.id_atencion)
            .join(Diagnostico, Diagnostico.id_diagnostico == Rel_atencion_diagnostico.lk_diagnostico)
            .join(Cie10, Cie10.cod_cie10 == Diagnostico.lk_cie10)
            .group_by(Atencion.id_atencion)
        ).where(Atencion.lk_paciente==paciente).order_by(desc(Atencion.fecha_atencion))

    results = session.exec(stmt).all()

    # Convertir los resultados en una lista de diccionarios
    lista_atenciones = [
        {
            "id_atencion": row.id_atencion,
            "lk_paciente": row.lk_paciente,
            "lk_medico":row.lk_medico,
            "fecha_atencion":str(row.fecha_atencion.strftime("%Y-%m-%d"))+" | "+edad(row.fecha_atencion),
            "motivo_consulta":row.motivo_consulta,
            #"motivo_consulta":edad(row.fecha_atencion)+" | "+ ''.join(map(str,row.codigos_cie10))+' | '+row.motivo_consulta,
            "revision_sistemas":row.revision_sistemas,
            "subjetivo":row.subjetivo,
            "objetivo":row.objetivo,
            "analisis":row.analisis,
            "plan":row.plan,
            "codigos_cie10": row.codigos_cie10.split(','),
            
        }
        for row in results
    ]
    return lista_atenciones

def historial_diagnosticos(session, paciente: int, medico_id: int = 1):
    crypto = GesmedCrypto.para_medico(medico_id)
    statement = select(Diagnostico, Cie10).join(Cie10, Diagnostico.lk_cie10 == Cie10.cod_cie10).where(Diagnostico.lk_paciente == paciente).order_by(desc(Diagnostico.fecha_diagnostico))
    resultados = session.exec(statement).all()
    lista = [
        {
            "id_diagnostico": diagnostico.id_diagnostico,
            "lk_paciente": diagnostico.lk_paciente,
            "cie10": diagnostico.lk_cie10,
            "nombre_cie10": cie10.nomdiagnostico,
            "tipo": diagnostico.tipo,
            "fecha_diagnostico": diagnostico.fecha_diagnostico,
            "fecha_inicio_aparente": diagnostico.fecha_inicio_aparente,
            "observaciones": diagnostico.observaciones,   # bytes or None
        }
        for diagnostico, cie10 in resultados
    ]
    return [crypto.desencriptar_campos(r, ["observaciones"]) for r in lista]

def atenciones_vinculadas_a_diagnostico(session,que_diagnostico:int):
    query=select(Rel_atencion_diagnostico.lk_atencion).where(Rel_atencion_diagnostico.lk_diagnostico==que_diagnostico)
    resultados=session.exec(query).all()
    return resultados

def diagnosticos_vinculados_a_atencion(session, id_atencion: int) -> list:
    query = select(Rel_atencion_diagnostico.lk_diagnostico).where(
        Rel_atencion_diagnostico.lk_atencion == id_atencion
    )
    return list(session.exec(query).all())


def actualiza_vistas():
    with Session(engine) as session:
        session.exec(
            """
            CREATE OR REPLACE VIEW cuantas_consultas AS
            SELECT COUNT(id_atencion),nombre_paciente
            FROM `atencion` GROUP BY nombre_paciente """
        )


# ── Prescripción ──────────────────────────────────────────────────────────────

def buscar_medicamentos(session, filtro: str = "", tipo_id: int | None = None) -> list[dict]:
    """Búsqueda en el catálogo de medicamentos genéricos."""
    stmt = (
        select(
            Medicamento.cod_gen,
            Medicamento.nombre_generico,
            Medicamento.nombre_comercial,
            Medicamento.tipo,
            MedicamentoTipo.nombre_tipo,
        )
        .join(MedicamentoTipo, MedicamentoTipo.id_tipo == Medicamento.tipo)
        .where(Medicamento.es_activo == 1)
        .order_by(asc(Medicamento.nombre_generico))
    )
    if len(filtro.strip()) >= 2:
        stmt = stmt.where(Medicamento.nombre_generico.like(f"%{filtro.strip()}%"))
    if tipo_id is not None:
        stmt = stmt.where(Medicamento.tipo == tipo_id)
    rows = session.exec(stmt).all()
    return [
        {
            "cod_gen":          r.cod_gen,
            "nombre_generico":  r.nombre_generico,
            "nombre_comercial": r.nombre_comercial,
            "tipo":             r.tipo,
            "nombre_tipo":      r.nombre_tipo,
        }
        for r in rows
    ]


def listar_presentaciones(session) -> list[dict]:
    """Presentaciones farmacéuticas activas para el dropdown."""
    stmt = (
        select(MedicamentoPresentacion)
        .where(MedicamentoPresentacion.en_uso == 1)
        .order_by(asc(MedicamentoPresentacion.nombre_presentacion))
    )
    rows = session.exec(stmt).all()
    return [
        {"id_presentacion": r.id_presentacion, "nombre_presentacion": r.nombre_presentacion}
        for r in rows
    ]


def listar_alergias_paciente(session, lk_paciente: int) -> list[dict]:
    """Alergias conocidas de un paciente, ordenadas alfabéticamente."""
    stmt = (
        select(Alergia)
        .where(Alergia.lk_paciente == lk_paciente)
        .order_by(asc(Alergia.sustancia_alergia))
    )
    rows = session.exec(stmt).all()
    return [
        {
            "id_alergia":       r.id_alergia,
            "sustancia_alergia": r.sustancia_alergia,
            "detalles":         r.detalles or "",
            "fecha_reportada":  str(r.fecha_reportada) if r.fecha_reportada else "",
        }
        for r in rows
    ]


def listar_prescripcion_atencion(session, lk_atencion: int, medico_id: int = 1) -> list[dict]:
    """Ítems de prescripción de una atención con desencriptación de campos sensibles."""
    crypto = GesmedCrypto.para_medico(medico_id)
    stmt = (
        select(
            Prescripcion.id_prescripcion,
            Prescripcion.lk_generico,
            Prescripcion.concentracion,
            Prescripcion.cantidad,
            Prescripcion.lk_presentacion,
            Prescripcion.indicaciones,
            Medicamento.nombre_generico,
            MedicamentoPresentacion.nombre_presentacion,
        )
        .join(Medicamento, Medicamento.cod_gen == Prescripcion.lk_generico)
        .join(MedicamentoPresentacion,
              MedicamentoPresentacion.id_presentacion == Prescripcion.lk_presentacion,
              isouter=True)
        .where(Prescripcion.lk_atencion == lk_atencion)
        .order_by(asc(Prescripcion.id_prescripcion))
    )
    rows = session.exec(stmt).all()
    return [
        {
            "id_prescripcion":    r.id_prescripcion,
            "lk_generico":        r.lk_generico,
            "nombre_generico":    r.nombre_generico,
            "concentracion":      crypto.desencriptar(r.concentracion),
            "cantidad":           r.cantidad,
            "lk_presentacion":    r.lk_presentacion,
            "nombre_presentacion": r.nombre_presentacion or "",
            "indicaciones":       crypto.desencriptar(r.indicaciones),
        }
        for r in rows
    ]


def historial_prescripciones_paciente(session, nro_paciente: int, medico_id: int) -> list[dict]:
    """Todas las prescripciones del paciente a través de todas sus atenciones."""
    crypto = GesmedCrypto.para_medico(medico_id)
    stmt = (
        select(
            Atencion.id_atencion,
            Atencion.fecha_atencion,
            Prescripcion.id_prescripcion,
            Prescripcion.cantidad,
            Prescripcion.concentracion,
            Medicamento.nombre_generico,
            MedicamentoPresentacion.nombre_presentacion,
        )
        .join(Prescripcion, Prescripcion.lk_atencion == Atencion.id_atencion)
        .join(Medicamento, Medicamento.cod_gen == Prescripcion.lk_generico)
        .join(
            MedicamentoPresentacion,
            MedicamentoPresentacion.id_presentacion == Prescripcion.lk_presentacion,
            isouter=True,
        )
        .where(Prescripcion.lk_paciente == nro_paciente)
        .order_by(desc(Atencion.fecha_atencion), asc(Medicamento.nombre_generico))
    )
    rows = session.exec(stmt).all()
    return [
        {
            "id_atencion":         r.id_atencion,
            "fecha_atencion":      r.fecha_atencion.strftime("%Y-%m-%d %H:%M"),
            "cantidad":            r.cantidad,
            "concentracion":       crypto.desencriptar(r.concentracion),
            "nombre_generico":     r.nombre_generico,
            "nombre_presentacion": r.nombre_presentacion or "",
        }
        for r in rows
    ]


def obtener_prescripcion_cuidados(session, lk_atencion: int) -> dict | None:
    """Cuidados generales de la prescripción de una atención. None si no existen aún."""
    stmt = select(PrescripcionCuidados).where(PrescripcionCuidados.lk_atencion == lk_atencion)
    row = session.exec(stmt).first()
    if row is None:
        return None
    return {
        "id_cuidados":      row.id_cuidados,
        "cuidados_generales": row.cuidados_generales or "",
        "fecha_emision":    str(row.fecha_emision) if row.fecha_emision else "",
    }


def guardar_item_prescripcion(
    session,
    lk_paciente:    int,
    lk_atencion:    int,
    lk_generico:    int,
    concentracion:  str,
    cantidad:       int,
    lk_presentacion: int | None,
    indicaciones:   str,
    medico_id:      int = 1,
) -> int:
    """Inserta un ítem de prescripción con encriptación. Devuelve el id generado."""
    crypto = GesmedCrypto.para_medico(medico_id)
    nuevo = Prescripcion(
        lk_paciente=lk_paciente,
        lk_atencion=lk_atencion,
        fecha_prescripcion=datetime.date.today(),
        lk_generico=lk_generico,
        concentracion=crypto.encriptar(concentracion.strip()),
        cantidad=cantidad,
        lk_presentacion=lk_presentacion,
        indicaciones=crypto.encriptar(indicaciones.strip()),
    )
    session.add(nuevo)
    session.commit()
    session.refresh(nuevo)
    return nuevo.id_prescripcion


def actualizar_prescripcion_cuidados(session, lk_atencion: int, cuidados_generales: str) -> None:
    """Inserta o actualiza los cuidados generales de la prescripción de una atención."""
    stmt = select(PrescripcionCuidados).where(PrescripcionCuidados.lk_atencion == lk_atencion)
    registro = session.exec(stmt).first()
    if registro:
        registro.cuidados_generales = cuidados_generales
        registro.fecha_emision = datetime.date.today()
    else:
        registro = PrescripcionCuidados(
            lk_atencion=lk_atencion,
            cuidados_generales=cuidados_generales,
            fecha_emision=datetime.date.today(),
        )
        session.add(registro)
    session.commit()


def eliminar_item_prescripcion(session, id_prescripcion: int) -> None:
    """Elimina un ítem de la prescripción."""
    item = session.get(Prescripcion, id_prescripcion)
    if item:
        session.delete(item)
        session.commit()


def actualizar_item_prescripcion(
    session,
    id_prescripcion: int,
    concentracion:   str,
    cantidad:        int,
    lk_presentacion: int | None,
    indicaciones:    str,
    medico_id:       int = 1,
) -> None:
    """Actualiza concentración, cantidad, presentación e indicaciones de un ítem existente."""
    crypto = GesmedCrypto.para_medico(medico_id)
    item = session.get(Prescripcion, id_prescripcion)
    if item:
        item.concentracion   = crypto.encriptar(concentracion.strip())
        item.cantidad        = cantidad
        item.lk_presentacion = lk_presentacion
        item.indicaciones    = crypto.encriptar(indicaciones.strip())
        session.commit()


def agregar_medicamento_nuevo(
    session, nombre_generico: str, nombre_comercial: str
) -> dict:
    """Añade un medicamento al catálogo con tipo=2 (añadido en consulta)."""
    nuevo = Medicamento(
        nombre_generico=nombre_generico.strip().upper(),
        nombre_comercial=nombre_comercial.strip(),
        tipo=2,
        es_activo=1,
    )
    session.add(nuevo)
    session.commit()
    session.refresh(nuevo)
    return {
        "cod_gen":         nuevo.cod_gen,
        "nombre_generico": nuevo.nombre_generico,
        "nombre_comercial": nuevo.nombre_comercial,
    }



# ── Mantenimiento catálogo de medicamentos ───────────────────────────────────

def listar_tipos_medicamento(session) -> list[dict]:
    stmt = select(MedicamentoTipo).order_by(asc(MedicamentoTipo.id_tipo))
    rows = session.exec(stmt).all()
    return [{"id_tipo": r.id_tipo, "nombre_tipo": r.nombre_tipo} for r in rows]


def buscar_similares_medicamento(session, texto: str) -> list[dict]:
    """Busca medicamentos similares al texto en todos los tipos (para detectar duplicados)."""
    texto_up = texto.strip().upper()
    if len(texto_up) < 3:
        return []
    palabras = [p for p in texto_up.split() if len(p) >= 3]
    conds = [Medicamento.nombre_generico.like(f"%{texto_up}%")]
    for p in palabras:
        conds.append(Medicamento.nombre_generico.like(f"%{p}%"))
    stmt = (
        select(
            Medicamento.cod_gen,
            Medicamento.nombre_generico,
            Medicamento.nombre_comercial,
            Medicamento.tipo,
            MedicamentoTipo.nombre_tipo,
        )
        .join(MedicamentoTipo, MedicamentoTipo.id_tipo == Medicamento.tipo)
        .where(or_(*conds))
        .order_by(asc(Medicamento.nombre_generico))
        .limit(10)
    )
    rows = session.exec(stmt).all()
    return [
        {
            "cod_gen":          r.cod_gen,
            "nombre_generico":  r.nombre_generico,
            "nombre_comercial": r.nombre_comercial,
            "tipo":             r.tipo,
            "nombre_tipo":      r.nombre_tipo,
        }
        for r in rows
    ]


def guardar_medicamento_catalogo(
    session, nombre_generico: str, nombre_comercial: str, tipo_id: int
) -> dict:
    """Inserta un nuevo medicamento desde el módulo de mantenimiento."""
    nuevo = Medicamento(
        nombre_generico=nombre_generico.strip().upper(),
        nombre_comercial=nombre_comercial.strip().upper(),
        tipo=tipo_id,
        es_activo=1,
    )
    session.add(nuevo)
    session.commit()
    session.refresh(nuevo)
    return {"cod_gen": nuevo.cod_gen, "nombre_generico": nuevo.nombre_generico}


# ── Atencion — actualización ─────────────────────────────────────────────────

def actualizar_atencion(
    session,
    id_atencion: int,
    motivo: str,
    revision: str,
    subjetivo: str,
    objetivo: str,
    analisis: str,
    plan: str,
) -> None:
    atencion = session.get(Atencion, id_atencion)
    if not atencion:
        return
    atencion.motivo_consulta   = motivo
    atencion.revision_sistemas = revision
    atencion.subjetivo         = subjetivo
    atencion.objetivo          = objetivo
    atencion.analisis          = analisis
    atencion.plan              = plan
    session.commit()


# ── Signos Vitales ────────────────────────────────────────────────────────────

def cargar_catalogo_sv(session) -> list[dict]:
    """Devuelve los signos vitales activos ordenados por orden_display."""
    rows = session.exec(
        select(ListaSignosVitales)
        .where(ListaSignosVitales.es_activo == 1)
        .order_by(asc(ListaSignosVitales.orden_display))
    ).all()
    return [
        {
            "id_signo_vital": r.id_signo_vital,
            "nombre":         r.nombre,
            "codigo":         r.codigo,
            "unidad":         r.unidad or "",
            "decimales":      r.decimales,
            "valor_min":      float(r.valor_min) if r.valor_min is not None else None,
            "valor_max":      float(r.valor_max) if r.valor_max is not None else None,
            "orden_display":  r.orden_display,
            "valor_actual":   "",   # campo editable; se rellena al cargar una atención
        }
        for r in rows
    ]


def cargar_sv_atencion(session, id_atencion: int) -> dict[int, str]:
    """Devuelve {id_signo_vital: valor_str} para una atención."""
    rows = session.exec(
        select(SignosVitales).where(SignosVitales.lk_atencion == id_atencion)
    ).all()
    return {r.lk_signo_vital: str(r.valor) for r in rows}


def guardar_sv_atencion(session, id_atencion: int, valores: list[dict]) -> None:
    """INSERT OR REPLACE de los signos vitales con valor no vacío."""
    for item in valores:
        raw = item.get("valor_actual", "").strip()
        if not raw:
            continue
        try:
            valor = Decimal(raw.replace(",", "."))
        except Exception:
            continue
        existente = session.exec(
            select(SignosVitales)
            .where(SignosVitales.lk_atencion    == id_atencion)
            .where(SignosVitales.lk_signo_vital == item["id_signo_vital"])
        ).first()
        if existente:
            existente.valor = valor
        else:
            session.add(SignosVitales(
                lk_atencion=id_atencion,
                lk_signo_vital=item["id_signo_vital"],
                valor=valor,
            ))
    session.commit()


def signos_vitales_atencion(session, id_atencion: int) -> list[dict]:
    """SV con valores registrados para una atención (solo los grabados)."""
    stmt = (
        select(
            ListaSignosVitales.nombre,
            ListaSignosVitales.codigo,
            ListaSignosVitales.unidad,
            SignosVitales.valor,
        )
        .join(SignosVitales, SignosVitales.lk_signo_vital == ListaSignosVitales.id_signo_vital)
        .where(SignosVitales.lk_atencion == id_atencion)
        .order_by(asc(ListaSignosVitales.orden_display))
    )
    return [
        {
            "nombre": r.nombre,
            "codigo": r.codigo,
            "valor":  str(r.valor),
            "unidad": r.unidad or "",
        }
        for r in session.exec(stmt).all()
    ]


def diagnosticos_atencion_detalle(session, id_atencion: int) -> list[dict]:
    """Código CIE10 y nombre de los diagnósticos vinculados a una atención."""
    stmt = (
        select(Cie10.cod_cie10, Cie10.nomdiagnostico)
        .join(Diagnostico, Diagnostico.lk_cie10 == Cie10.cod_cie10)
        .join(
            Rel_atencion_diagnostico,
            Rel_atencion_diagnostico.lk_diagnostico == Diagnostico.id_diagnostico,
        )
        .where(Rel_atencion_diagnostico.lk_atencion == id_atencion)
        .order_by(asc(Cie10.cod_cie10))
    )
    return [
        {"cie10": r.cod_cie10, "nomdiagnostico": r.nomdiagnostico}
        for r in session.exec(stmt).all()
    ]


def edad(fecha_:datetime.datetime):
    #Calcula la distancia entre la fecha recibida y hoy, presentando solamente años y meses de diferencia
    # salvo que la diferencia sea solo de dias
    hoy=datetime.date.today()
    edad_a=hoy.year - fecha_.year
    edad_m=hoy.month - fecha_.month
    edad_d=hoy.day-fecha_.day
    if edad_m<0:
        edad_a=edad_a-1
        edad_m=12+edad_m
    elif edad_m==0 and edad_a==0:
        return (str(edad_d)+'d')
    return (str(edad_a)+'a '+str(edad_m)+'m')


# ── Exámenes de laboratorio ───────────────────────────────────────────────────

def cargar_catalogo_examenes(session: Session) -> list[dict]:
    """Todos los exámenes activos con su nombre de grupo."""
    stmt = (
        select(
            ExamenesLaboratorioCatalogo.id_examen,
            ExamenesLaboratorioCatalogo.nombre_examen,
            ExamenesLaboratorioGrupo.id_grupo,
            ExamenesLaboratorioGrupo.nombre_grupo,
        )
        .join(
            ExamenesLaboratorioGrupo,
            ExamenesLaboratorioCatalogo.lk_grupo == ExamenesLaboratorioGrupo.id_grupo,
            isouter=True,
        )
        .where(ExamenesLaboratorioCatalogo.activo == 1)
        .order_by(ExamenesLaboratorioGrupo.nombre_grupo, ExamenesLaboratorioCatalogo.nombre_examen)
    )
    rows = session.exec(stmt).all()
    return [
        {
            "id_examen":    r.id_examen,
            "nombre_examen": r.nombre_examen,
            "id_grupo":     r.id_grupo or 0,
            "nombre_grupo": r.nombre_grupo or "",
        }
        for r in rows
    ]


def cargar_grupos_examenes(session: Session) -> list[dict]:
    """Lista de grupos de exámenes, ordenados por nombre."""
    stmt = select(ExamenesLaboratorioGrupo).order_by(ExamenesLaboratorioGrupo.nombre_grupo)
    rows = session.exec(stmt).all()
    return [{"id_grupo": r.id_grupo, "nombre_grupo": r.nombre_grupo} for r in rows]


def cargar_pedido_atencion(session: Session, lk_atencion: int) -> list[dict]:
    """Carga los exámenes pedidos para una atención dada, con nombre de examen y grupo."""
    if not lk_atencion:
        return []
    stmt = (
        select(
            ExamenesLaboratorioPedido.id_pedido,
            ExamenesLaboratorioCatalogo.id_examen,
            ExamenesLaboratorioCatalogo.nombre_examen,
            ExamenesLaboratorioGrupo.nombre_grupo,
        )
        .join(
            ExamenesLaboratorioCatalogo,
            ExamenesLaboratorioPedido.lk_examen == ExamenesLaboratorioCatalogo.id_examen,
        )
        .join(
            ExamenesLaboratorioGrupo,
            ExamenesLaboratorioCatalogo.lk_grupo == ExamenesLaboratorioGrupo.id_grupo,
            isouter=True,
        )
        .where(ExamenesLaboratorioPedido.lk_atencion == lk_atencion)
        .order_by(ExamenesLaboratorioGrupo.nombre_grupo, ExamenesLaboratorioCatalogo.nombre_examen)
    )
    rows = session.exec(stmt).all()
    return [
        {
            "id_pedido":    r.id_pedido,
            "id_examen":    r.id_examen,
            "nombre_examen": r.nombre_examen,
            "nombre_grupo": r.nombre_grupo or "",
        }
        for r in rows
    ]


def guardar_pedido_examenes(
    session: Session,
    lk_paciente: int,
    lk_atencion: int,
    examen_ids: list[int],
) -> None:
    """Reemplaza el pedido de exámenes de una atención (DELETE + INSERT)."""
    existentes = session.exec(
        select(ExamenesLaboratorioPedido).where(
            ExamenesLaboratorioPedido.lk_atencion == lk_atencion
        )
    ).all()
    for e in existentes:
        session.delete(e)
    session.flush()
    fecha = datetime.date.today()
    for id_ex in examen_ids:
        session.add(ExamenesLaboratorioPedido(
            lk_paciente=lk_paciente,
            lk_atencion=lk_atencion,
            fecha_pedido=fecha,
            lk_examen=id_ex,
        ))
    session.commit()


# ── Gestión de usuarios ───────────────────────────────────────────────────────

def _permisos_con_alcance(permisos_actual: str, alcance_lectura: str, alcance_escritura: str) -> str:
    """
    Fija las posiciones 1 y 2 del string "permisos":
      posición 1 = alcance de LECTURA  (T=ve todos los pacientes, P=solo los propios)
      posición 2 = alcance de ESCRITURA (T=modifica todos, P=solo los propios)
    Conserva el resto de posiciones tal cual (p.ej. posición 0 = 'R'/'X' de
    acceso a configuración de reportes).
    """
    letras = list((permisos_actual or "").ljust(4, "X"))
    letras[1] = "P" if alcance_lectura == "P" else "T"
    letras[2] = "P" if alcance_escritura == "P" else "T"
    return "".join(letras)


def estado_propiedad_paciente(session, nro_hclinica: int, medico_id: int) -> tuple[bool, bool]:
    """
    Retorna (es_accesible, es_disponible) para un paciente puntual:

    - es_disponible: True si el paciente no tiene NINGUNA atención registrada
      (de ningún médico) — es un paciente recién creado, sin atenciones
      todavía, así que ningún médico es "dueño" y cualquiera puede reclamarlo
      con su primera atención.
    - es_accesible: True si es_disponible, o si el médico dado tiene al menos
      una atención propia con ese paciente. Es el flag que deben usar los
      guards de lectura/escritura por alcance de pacientes (permisos[1]/[2]).

    En cuanto un médico registra la primera atención, el paciente deja de
    estar "disponible" y pasa a ser exclusivamente suyo (esta misma consulta,
    ejecutada de nuevo, ya lo refleja sin ningún paso adicional).
    """
    tiene_alguna = session.exec(
        select(Atencion.id_atencion).where(Atencion.lk_paciente == nro_hclinica).limit(1)
    ).first()
    if tiene_alguna is None:
        return True, True
    tiene_propia = session.exec(
        select(Atencion.id_atencion)
        .where(Atencion.lk_paciente == nro_hclinica, Atencion.lk_medico == medico_id)
        .limit(1)
    ).first()
    return (tiene_propia is not None), False


def listar_usuarios(session) -> list[dict]:
    rows = session.exec(select(Points).order_by(asc(Points.nombre_medico))).all()
    return [
        {
            "id_medico":      r.id_medico,
            "nombre_medico":  r.nombre_medico,
            "especialidad":   r.especialidad,
            "cod_especialidad": r.cod_especialidad,
            "celular":        r.celular,
            "email":          r.email,
            "usuario":        r.usuario,
            "rol":            r.rol,
            "estado":         r.estado,
            "permisos":       r.permisos,
        }
        for r in rows
    ]


def crear_usuario(session, nombre: str, especialidad: str, cod_esp: str,
                  celular: str, email: str, usuario: str,
                  clave_plain: str, rol: str,
                  alcance_lectura: str = "T", alcance_escritura: str = "T") -> Points:
    clave_hash = _bcrypt.hashpw(clave_plain.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")
    nuevo = Points(
        nombre_medico=nombre,
        especialidad=especialidad,
        cod_especialidad=cod_esp,
        celular=celular,
        email=email,
        usuario=usuario,
        clave=clave_hash,
        permisos=_permisos_con_alcance("", alcance_lectura, alcance_escritura),
        estado=1,
        rol=rol,
    )
    session.add(nuevo)
    session.commit()
    session.refresh(nuevo)
    return nuevo


def actualizar_usuario(session, id_medico: int, nombre: str, especialidad: str,
                       cod_esp: str, celular: str, email: str,
                       usuario: str, rol: str, estado: int,
                       alcance_lectura: str = "T", alcance_escritura: str = "T") -> None:
    u = session.get(Points, id_medico)
    if not u:
        return
    u.nombre_medico   = nombre
    u.especialidad    = especialidad
    u.cod_especialidad = cod_esp
    u.celular         = celular
    u.email           = email
    u.usuario         = usuario
    u.rol             = rol
    u.estado          = estado
    u.permisos        = _permisos_con_alcance(u.permisos, alcance_lectura, alcance_escritura)
    session.add(u)
    session.commit()


def resetear_clave(session, id_medico: int, nueva_clave: str) -> None:
    u = session.get(Points, id_medico)
    if not u:
        return
    clave_hash = _bcrypt.hashpw(nueva_clave.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")
    u.clave = clave_hash
    session.add(u)
    session.commit()


def listar_ant_familiares(session, lk_paciente: int, medico_id: int) -> list[dict]:
    """Antecedentes familiares de un paciente ordenados por fecha ascendente."""
    crypto = GesmedCrypto.para_medico(medico_id)
    stmt = (
        select(AntecedenteFamiliar)
        .where(AntecedenteFamiliar.lk_paciente == lk_paciente)
        .order_by(asc(AntecedenteFamiliar.fecha_registro))
    )
    rows = session.exec(stmt).all()
    return [
        {
            "id_antecedente": r.id_antecedente,
            "fecha_registro":  str(r.fecha_registro),
            "descripcion":     crypto.desencriptar(r.descripcion) if r.descripcion else "",
        }
        for r in rows
    ]
