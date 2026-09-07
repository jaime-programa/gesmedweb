import pathlib
import reflex as rx


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


def _precargar_ocr():
    """Precarga PaddleOCR al arranque para que el primer médico no espere."""
    try:
        import threading
        from GesmedWeb.utils.ocr_utils import inicializar_ocr
        threading.Thread(target=inicializar_ocr, daemon=True).start()
    except Exception:
        pass


_precargar_ocr()


config = rx.Config(
    app_name="GesmedWeb",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(),
    ]
)