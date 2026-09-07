import reflex as rx


class CalendarioMedico(rx.Component):
    """Wrapper Reflex para FullCalendar.
    El archivo JSX vive en .web/calendario_medico.jsx (copiado ahí
    automáticamente por rxconfig.py desde
    GesmedWeb/custom_components/calendario_medico.jsx).
    """
    library = "$/calendario_medico"
    tag = "CalendarioMedico"

    # NO declarar lib_dependencies aquí: reflex sí lo procesa (a diferencia
    # de lo que sugiere la ausencia de version pin), pero instala la última
    # versión de cada paquete sin respetar compatibilidad entre ellos —
    # eso resolvía @fullcalendar/core y @fullcalendar/react a v7.x mientras
    # daygrid/timegrid/interaction quedaban en v6.x, una combinación
    # incompatible que rompe el build de producción. Los paquetes de
    # FullCalendar se instalan en su lugar desde rxconfig.py
    # (_instalar_paquetes_npm_custom), con las 5 versiones fijadas a
    # 6.1.21 para que queden en lockstep.

    # Props reactivos
    eventos: rx.Var[list]
    vista:   rx.Var[str]

    # Callbacks → Python state handlers
    on_event_click: rx.EventHandler[lambda data: [data]]
    on_date_select: rx.EventHandler[lambda data: [data]]
    on_event_drop:  rx.EventHandler[lambda data: [data]]
