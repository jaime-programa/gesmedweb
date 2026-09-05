import reflex as rx
from ..state import State

def login_falso() ->rx.Component:
    
    return rx.center(
            rx.center(
                rx.button("Entrar",on_click=State.entrar_false),
            
            width="100%",
                    align="center",
                ),
                height="100vh",
            ),  

def el_login() -> rx.Component:
    return  rx.center(
                rx.card(
                    rx.vstack(
                        rx.center(
                            rx.image(
                                src="/logotipo_original.jpg",
                                width="4.5em",
                                height="auto",
                                border_radius="25%",
                            ),
                            rx.heading(
                                "Bienvenido",
                                size="6",
                                as_="h2",
                                text_align="center",
                                width="100%",
                            ),
                            direction="column",
                            spacing="5",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.text(
                                "Usuario",
                                size="3",
                                weight="medium",
                                text_align="left",
                                width="100%",
                            ),
                            rx.input(
                                placeholder="Ingrese su usuario",
                                on_change=State.set_px1,
                                #type="email",
                                size="3",
                                width="100%"
                                
                            ),
                            justify="start",
                            spacing="2",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.text(
                                    "Password",
                                    size="3",
                                    weight="medium",
                                ),
                                justify="between",
                                width="100%",
                            ),
                            rx.input(
                                placeholder="Ingrese su password",
                                on_change=State.set_px2,
                                type="password",
                                size="3",
                                width="100%",
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        rx.button(
                            "Ingresar",
                            id='submit-button',
                            on_click=State.handle_login,
                            size="3",
                            width="40%",
                            autofocus=True,
                            cursor=rx.cond(State.login_cargando, "not-allowed", "pointer"),
                            background_color=rx.cond(State.login_cargando, "#D1D5DB", None),
                            disabled=State.login_cargando,
                        ),
                        rx.cond(
                            State.error_message != "",
                            rx.callout(
                                State.error_message,
                                icon="triangle_alert",
                                color_scheme="red",
                                role="alert",
                                ),
                        ),
                        spacing="6",
                        width="100%",

                    ),
                    size="4",
                    max_width="28em",
                    width="100%",
                    align="center",
                ),
                height="100vh",
            ),
        
