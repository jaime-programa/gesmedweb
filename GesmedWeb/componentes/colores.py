# ── Resaltado de filas en tablas ─────────────────────────────────────────────
ROW_SELECTED_BG     = "rgba(63, 176, 217, 0.28)"   # fondo de fila seleccionada
ROW_HOVER_BG        = "rgba(0,170,220,0.12)"   # fondo de fila al pasar el cursor
ROW_DESTACADO_COLOR = "#0A2CD7"                # texto de diagnóstico vinculado (azul marino)
ROW_DESTACADO_COLOR2 = "#94C9A8FF"                # texto de prescripción vinculado (verde limón)

# ── Encabezados de tablas ─────────────────────────────────────────────────────
# azul
TABLE_HEADER_BG_PETROLEO    = "#24508d"   # fondo del encabezado
TABLE_HEADER_BG_GREEN ="#457746"
TABLE_HEADER_BG_BLUE ="#4340E7"
TABLE_HEADER_BG_YELLOW ="#E4C063"
TABLE_HEADER_COLOR = "white"     # texto del encabezado
TABLE_BORDER       = "#d1d5db"   # borde de celdas
#verde



#-- Encabezados tablas secundarias ___________
TABLA_SECUNDARIA_ENCABEZADO = "#9ab0cf"
TABLA_SECUNDARIA_TEXTO_ENCABEZADO ="black"

# ── Fondos de botones ─────────────────────────────────────────────────────────
BOTON_PRIMARIO      = "#0090FF"    # acción primaria   (azul)
BOTON_SECUNDARIO    = "#39B3CFD5"  # acción secundaria (celeste con alfa)
BOTON_TERCIARIO    = "#0074C7D1"  # acción secundaria (celeste con alfa)
BOTON_ACCION        = "#16A34A"    # crear / agregar   (verde)
BOTON_DESHABILITADO = "#C4D8FF"    # estado deshabilitado (gris claro)

BOTON_DESHABILITADO_TEXTO = "#9CA3AF"  # texto en estado deshabilitado

BOTON_IMPRIMIR="#E93D82"
# ── Resaltado de texto en tablas ─────────────────────────────────────────────
COLOR_RESALTA_TEXTO = "#0047FF"   # azul eléctrico: resalta texto en tabla al filtrar por diagnóstico

# ── Panel derecha: visualización SOAP ────────────────────────────────────────
SOAP_FIELD_BORDER = "#e5e7eb"   # borde de recuadro de campo SOAP (gris claro)

#___ ZEBRAS _____
ZEBRA_OBSCURO="#99E4F3A8"
ZEBRA_CLARO="#E6FBFF"

#__POR TAB____
SOAP_FONDO="#f9d8d8"
PRESCRIPCION_FONDO="#7DC183"
PEDIDO_FONDO="#A8BEFF"
RESULTADO_FONDO="#FFEFD4"

PRESCRIPCION_ENCABEZADO="#9FBFA9DF"

# ── Navbar de atención ────────────────────────────────────────────────────────
BORDE_BOTONES_NAVBAR = "#0BC5FE"   # borde de botones SOAP / Prescripción / Exámenes

# ── Paciente ajeno (sin atención propia del médico logueado) ────────────────
# Se usan para distinguir visualmente, en los perfiles que ven pacientes de
# otros médicos (permisos[1] == "T"), cuáles son "propios" vs "ajenos".
PACIENTE_AJENO_LISTA_COLOR    = "#3FA9C9"  # celeste (no tan claro): fuente en la tabla de lista_pacientes
PACIENTE_AJENO_ATENCION_COLOR = "#9CA3AF"  # tono tenue: nombre del paciente en el navbar de atención

# ── Paciente "disponible" (sin atenciones de NINGÚN médico todavía) ─────────
# Un paciente recién creado no tiene atenciones, así que no tiene médico
# "dueño" hasta que alguien registre la primera — mientras tanto cualquier
# médico debe poder verlo/atenderlo aunque su perfil sea "solo propios".
PACIENTE_DISPONIBLE_LISTA_COLOR    = "#E67E22"  # naranja: fuente en la tabla de lista_pacientes
PACIENTE_DISPONIBLE_ATENCION_COLOR = "#E67E22"  # naranja: nombre del paciente en el navbar de atención
