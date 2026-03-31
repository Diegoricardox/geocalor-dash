from dash import Input, Output, html

def register_callbacks(app):
    """
    Registra todos os callbacks da aplicação.
    """
    @app.callback(
        Output("page-content", "children"),
        [Input("url", "pathname")]
    )
    def render_page_content(pathname):
        if pathname == "/":
            return html.Div([
                html.H1("Início"),
                html.P("Bem-vindo ao Dashboard GeoCalor em Python (Dash).")
            ])
        elif pathname == "/sobre":
            return html.Div([
                html.H1("Sobre o Projeto"),
                html.P("Informações sobre o projeto GeoCalor.")
            ])
        elif pathname == "/temperaturas":
            return html.Div([
                html.H1("Temperaturas Diárias"),
                html.P("Análise de temperaturas diárias.")
            ])
        elif pathname == "/ondas":
            return html.Div([
                html.H1("Ondas de Calor"),
                html.P("Monitoramento de ondas de calor.")
            ])
        
        # Se o usuário tentar acessar uma URL diferente, retorna um 404
        return html.Div(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(f"A rota {pathname} não foi reconhecida..."),
            ],
            className="p-3 bg-light rounded-3",
        )
