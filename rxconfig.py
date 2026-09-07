import os
import pathlib
import reflex as rx

from dotenv import load_dotenv

# GesmedWeb/*.py lee GESMED_MASTER_KEY, GESMED_DB_URL, GESMED_API_URL, etc.
# vía os.environ.get(...), pero a diferencia de los scripts en migrations/
# (que llaman load_dotenv ellos mismos), la app en sí nunca cargaba .env —
# dependía de que el proceso ya tuviera esas variables exportadas en el
# shell. Se carga aquí explícitamente para que "reflex run" funcione igual
# sin importar cómo se lance el proceso.
load_dotenv(pathlib.Path(__file__).parent / ".env")


def _patch_reflex_dispatch_guard():
    """
    Aplica un guard a reflex_base para evitar 'dispatch is not a function'.

    El bug original: si un delta WebSocket llega antes de que todos los
    substates estén registrados en el frontend, dispatch[substate] es
    undefined y el handler se rompe a mitad de ejecución, dejando la UI
    desincronizada sin avisar al usuario.

    Este fix es idempotente y se auto-aplica en cualquier entorno (dev,
    servidor nuevo) cada vez que se carga rxconfig.py.
    """
    try:
        import reflex_base
        template = (
            pathlib.Path(reflex_base.__file__).parent
            / ".templates/web/utils/state.js"
        )
        if not template.exists():
            return
        src = template.read_text()
        if "unknown substate in delta" in src:
            return  # ya aplicado
        old = "        dispatch[substate](update.delta[substate]);"
        if old not in src:
            return  # estructura cambió (nueva versión de Reflex), no tocar
        guard = (
            '        if (typeof dispatch[substate] !== "function") {\n'
            '          console.warn("[Reflex] unknown substate in delta, skipping:", substate);\n'
            '          continue;\n'
            '        }\n'
            '        dispatch[substate](update.delta[substate]);'
        )
        template.write_text(src.replace(old, guard, 1))
    except Exception:
        pass  # nunca romper el arranque de la app por este parche


def _patch_reflex_color_mode():
    """
    Corrige react-theme.js para que appearance="light" (u otro modo fijo)
    no sea sobreescrito por el valor guardado en localStorage del browser.

    El bug original: el ThemeProvider siempre lee localStorage["theme"],
    así que si el browser guardó "dark" en una sesión anterior, lo aplica
    incluso cuando el app tiene appearance="light" configurado.

    Fix: cuando defaultColorMode != "system", forzar ese valor e ignorar
    lo que haya en localStorage.
    """
    try:
        import reflex_base
        template = (
            pathlib.Path(reflex_base.__file__).parent
            / ".templates/web/utils/react-theme.js"
        )
        if not template.exists():
            return
        src = template.read_text()
        if 'defaultColorMode !== "system"' in src:
            return  # ya aplicado
        old = (
            "    // Load saved theme from localStorage\n"
            "    const savedTheme = localStorage.getItem(\"theme\") || defaultTheme;\n"
            "    setTheme(savedTheme);\n"
            "    setIsInitialized(true);"
        )
        if old not in src:
            return  # estructura cambió (nueva versión de Reflex), no tocar
        fixed = (
            '    // When the app fixes a specific appearance (not "system"), always honor it\n'
            '    // and update localStorage so the choice persists correctly.\n'
            '    if (defaultColorMode !== "system") {\n'
            '      localStorage.setItem("theme", defaultColorMode);\n'
            '      setTheme(defaultColorMode);\n'
            '      setIsInitialized(true);\n'
            '      return;\n'
            '    }\n'
            '\n'
            '    // Load saved theme from localStorage\n'
            '    const savedTheme = localStorage.getItem("theme") || defaultTheme;\n'
            '    setTheme(savedTheme);\n'
            '    setIsInitialized(true);'
        )
        template.write_text(src.replace(old, fixed, 1))
    except Exception:
        pass


_patch_reflex_dispatch_guard()
_patch_reflex_color_mode()


def _instalar_componentes_custom():
    """
    Copia los componentes JSX escritos a mano hacia .web/, ya que .web/
    completo está en .gitignore (es el build de Reflex) y por eso estos
    archivos nunca llegan al servidor con git clone.

    Sin esto, "reflex export"/"reflex run" falla en el servidor con
    "Could not load calendario_medico ... No such file or directory",
    porque GesmedWeb/componentes/calendario_fc.py referencia
    library = "$/calendario_medico" (o sea .web/calendario_medico.jsx)
    y ese archivo solo existía en la máquina donde se escribió a mano.
    """
    try:
        origen_dir = pathlib.Path(__file__).parent / "GesmedWeb" / "custom_components"
        web_dir = pathlib.Path(__file__).parent / ".web"
        if not web_dir.exists() or not origen_dir.exists():
            return
        for origen in origen_dir.glob("*.jsx"):
            destino = web_dir / origen.name
            if not destino.exists() or destino.read_text() != origen.read_text():
                destino.write_text(origen.read_text())
    except Exception:
        pass


_instalar_componentes_custom()


# Paquetes npm que necesita GesmedWeb/componentes/calendario_fc.py (JSX
# escrito a mano, no una librería real de npm). El campo lib_dependencies
# de rx.Component no los instala en esta versión de reflex, así que se
# instalan aquí a mano — mismo patrón self-healing que _instalar_componentes_custom.
#
# Versión fijada a 6.1.21 en TODOS los paquetes a propósito: @fullcalendar
# publicó un v7 de @fullcalendar/react y @fullcalendar/core que rompe el
# import "@fullcalendar/core/locales/es" que usa calendario_medico.jsx (el
# paquete ya no expone esa ruta bajo ESM), mientras que daygrid/timegrid/
# interaction siguen solo en v6. Sin fijar versión, "bun add" instala la
# combinación incompatible (core/react en 7.x, el resto en 6.x) y el build
# de producción falla con:
#   Error: Errored while resolving "@fullcalendar/core/locales/es" ...
#   "./locales/es" is not exported under the conditions [...] from package
#   .web/node_modules/@fullcalendar/core
_PAQUETES_NPM_CUSTOM = [
    "@fullcalendar/react@6.1.21",
    "@fullcalendar/daygrid@6.1.21",
    "@fullcalendar/timegrid@6.1.21",
    "@fullcalendar/interaction@6.1.21",
    "@fullcalendar/core@6.1.21",
]


def _instalar_paquetes_npm_custom():
    """
    Corre "bun add" para los paquetes de FullCalendar si no están ya
    instalados en .web/node_modules.

    Sin esto, el build/dev server falla con:
        [plugin:vite:import-analysis] Failed to resolve import
        "@fullcalendar/react" from "calendario_medico.jsx"
    cada vez que .web/ se genera desde cero (clon nuevo del repo, o
    "reflex init" tras borrar .web/) — el "bun add" manual que menciona
    el docstring de calendario_fc.py se pierde en cada regeneración
    porque nadie se acuerda de correrlo otra vez.
    """
    try:
        web_dir = pathlib.Path(__file__).parent / ".web"
        if not web_dir.exists():
            return
        primero = _PAQUETES_NPM_CUSTOM[0].rsplit("@", 1)[0]  # "@fullcalendar/react"
        if (web_dir / "node_modules" / primero).exists():
            return

        import subprocess
        from reflex_base.constants.installer import Bun

        bun_path = Bun.DEFAULT_PATH
        if not pathlib.Path(bun_path).exists():
            return  # bun no instalado todavía (primer "reflex init" en curso)

        subprocess.run(
            [str(bun_path), "add", *_PAQUETES_NPM_CUSTOM],
            cwd=str(web_dir),
            timeout=180,
            capture_output=True,
        )
    except Exception:
        pass


_instalar_paquetes_npm_custom()


def _precargar_ocr():
    """Precarga PaddleOCR al arranque para que el primer médico no espere."""
    try:
        import threading
        from GesmedWeb.utils.ocr_utils import inicializar_ocr
        threading.Thread(target=inicializar_ocr, daemon=True).start()
    except Exception:
        pass


_precargar_ocr()


# api_url: host que el BACKEND usa para construir URLs absolutas propias
# (p.ej. GesmedWeb/state.py y querys/resultados_querys.py arman
# f"{api_url}/imagen/{id_imagen}" para el <img src=...> de resultados).
# Si se deja el default de Reflex ("http://localhost:8000"), ese host queda
# fijo en cada URL sin importar qué cliente la reciba: funciona al navegar
# desde la misma Mac que corre el servidor, pero un cliente remoto (otra
# máquina en la LAN, ej. un Linux) recibe una URL que apunta a "localhost"
# — su PROPIO localhost, no el de la Mac — y la imagen nunca carga aunque
# sí se subió correctamente. Se soluciona fijando GESMED_API_URL en .env
# con la IP/hostname real de la Mac servidor, ej.:
#   GESMED_API_URL=http://192.168.100.14:8000
GESMED_API_URL = os.environ.get("GESMED_API_URL", "http://localhost:8000")

config = rx.Config(
    app_name="GesmedWeb",
    api_url=GESMED_API_URL,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(),
    ]
)