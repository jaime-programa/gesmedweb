import React, { useCallback } from 'react'
import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import esLocale from '@fullcalendar/core/locales/es'

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
