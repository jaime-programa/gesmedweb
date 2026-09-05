import reflex as rx


class CalendarioMedico(rx.Component):
    """Wrapper Reflex para FullCalendar.
    El archivo JSX vive en .web/calendario_medico.jsx.
    Instalar paquetes (una vez): cd .web && bun add @fullcalendar/react
        @fullcalendar/daygrid @fullcalendar/timegrid @fullcalendar/interaction
    """
    library = "$/calendario_medico"
    tag = "CalendarioMedico"

    # Props reactivos
    eventos: rx.Var[list]
    vista:   rx.Var[str]

    # Callbacks → Python state handlers
    on_event_click: rx.EventHandler[lambda data: [data]]
    on_date_select: rx.EventHandler[lambda data: [data]]
    on_event_drop:  rx.EventHandler[lambda data: [data]]
