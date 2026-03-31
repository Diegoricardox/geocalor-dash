import dash
import dash_bootstrap_components as dbc
from app.layout import create_layout
from app.callbacks import register_callbacks

# Inicialização do app Dash com tema Bootstrap
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
    title="Dashboard GeoCalor | OCS"
)

# Configuração para deploy (Gunicorn)
server = app.server

# Definir layout
app.layout = create_layout(app)

# Registrar callbacks
register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
