import React, { useCallback } from 'react'
import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'

// Definido a mano (copia del locale oficial "es" de @fullcalendar/core) en
// vez de "import esLocale from '@fullcalendar/core/locales/es'": el
// package.json de @fullcalendar/core (desde v6) restringe "exports" a solo
// ".", "./protected-api" y "./package.json", así que Vite/rolldown rechaza
// cualquier import de una subruta como "./locales/es" con el error
// "is not exported under the conditions [...] from package @fullcalendar/core"
// aunque el archivo exista físicamente en node_modules.
const esLocale = {
    code: 'es',
    week: { dow: 1, doy: 4 },
    buttonText: {
        prev: 'Ant', next: 'Sig', today: 'Hoy', year: 'Año',
        month: 'Mes', week: 'Semana', day: 'Día', list: 'Agenda',
    },
    buttonHints: {
        prev: '$0 antes',
        next: '$0 siguiente',
        today(buttonText) {
            return (buttonText === 'Día') ? 'Hoy' :
                ((buttonText === 'Semana') ? 'Esta' : 'Este') + ' ' + buttonText.toLocaleLowerCase()
        },
    },
    viewHint(buttonText) {
        return 'Vista ' + (buttonText === 'Semana' ? 'de la' : 'del') + ' ' + buttonText.toLocaleLowerCase()
    },
    weekText: 'Sm',
    weekTextLong: 'Semana',
    allDayText: 'Todo el día',
    moreLinkText: 'más',
    moreLinkHint(eventCnt) {
        return `Mostrar ${eventCnt} eventos más`
    },
    noEventsText: 'No hay eventos para mostrar',
    navLinkHint: 'Ir al $0',
    closeHint: 'Cerrar',
    timeHint: 'La hora',
    eventHint: 'Evento',
}

export function CalendarioMedico({
    eventos = [],
    vista = 'timeGridWeek',
    onEventClick,
    onDateSelect,
    onEventDrop,
}) {
    const handleEventClick = useCallback((info) => {
        if (!onEventClick) return
        const ext = info.event.extendedProps || {}
        onEventClick({
            id_cita:       ext.id_cita       ?? 0,
            px_nombre:     ext.px_nombre     ?? '',
            tipo:          ext.tipo          ?? '',
            categoria:     ext.categoria     ?? '',
            estado:        ext.estado        ?? '',
            medico:        ext.medico        ?? '',
            id_medico:     ext.id_medico     ?? 0,
            notas:         ext.notas        ?? '',
            requiere_conf: ext.requiere_conf ?? false,
            start:         info.event.startStr,
            end:           info.event.endStr,
        })
    }, [onEventClick])

    const handleDateSelect = useCallback((info) => {
        if (!onDateSelect) return
        onDateSelect({ start: info.startStr, end: info.endStr })
    }, [onDateSelect])

    const handleEventDrop = useCallback((info) => {
        if (!onEventDrop) return
        const ext = info.event.extendedProps || {}
        onEventDrop({
            id_cita: ext.id_cita ?? 0,
            start:   info.event.startStr,
            end:     info.event.endStr,
        })
    }, [onEventDrop])

    return (
        <div style={{ height: 'calc(100vh - 130px)', padding: '0 12px 8px 12px' }}>
            <FullCalendar
                plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
                initialView={vista}
                locale={esLocale}
                headerToolbar={{
                    left:   'prev,next today',
                    center: 'title',
                    right:  'timeGridDay,timeGridWeek,tresSemanas',
                }}
                views={{
                    tresSemanas: {
                        type:       'dayGrid',
                        duration:   { weeks: 3 },
                        buttonText: '3 sem.',
                    },
                }}
                events={eventos}
                selectable={true}
                selectMirror={true}
                editable={true}
                eventClick={handleEventClick}
                select={handleDateSelect}
                eventDrop={handleEventDrop}
                slotMinTime="07:00:00"
                slotMaxTime="20:00:00"
                slotDuration="00:15:00"
                allDaySlot={false}
                height="100%"
                nowIndicator={true}
                eventTimeFormat={{
                    hour:     '2-digit',
                    minute:   '2-digit',
                    meridiem: false,
                    hour12:   false,
                }}
                slotLabelFormat={{
                    hour:           'numeric',
                    minute:         '2-digit',
                    omitZeroMinute: false,
                    hour12:         false,
                }}
            />
        </div>
    )
}
