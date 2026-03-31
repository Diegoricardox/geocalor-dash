from dash import html, dcc
import dash_bootstrap_components as dbc

def create_layout(app):
    """
    Define o layout principal da aplicação (Sidebar + Conteúdo)
    """
    sidebar = html.Div(
        [
            html.H2("GeoCalor", className="display-6"),
            html.Hr(),
            html.P(
                "Monitoramento de ondas de calor e impactos na saúde.", className="lead"
            ),
            dbc.Nav(
                [
                    dbc.NavLink("Início", href="/", active="exact"),
                    dbc.NavLink("Sobre o Projeto", href="/sobre", active="exact"),
                    dbc.NavLink("Temperaturas Diárias", href="/temperaturas", active="exact"),
                    dbc.NavLink("Ondas de Calor", href="/ondas", active="exact"),
                ],
                vertical=True,
                pills=True,
            ),
            html.Div(
                [
                    html.Hr(),
                    html.P("Desenvolvimento: Diego Ricardo Xavier | OCS/ICICT/Fiocruz", style={"fontSize": "10px", "color": "#888"})
                ],
                style={"position": "absolute", "bottom": "10px", "width": "90%"}
            )
        ],
        style={
            "position": "fixed",
            "top": 0,
            "left": 0,
            "bottom": 0,
            "width": "16rem",
            "padding": "2rem 1rem",
            "backgroundColor": "#f8f9fa",
        },
    )

    content = html.Div(
        id="page-content",
        style={
            "marginLeft": "18rem",
            "padding": "2rem 1rem",
        }
    )

    return html.Div([dcc.Location(id="url"), sidebar, content])
