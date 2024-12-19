import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

# Inicializar o app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout do aplicativo
app.layout = html.Div([
    # Cabeçalho
    html.Div(
        [
            html.H1("SEPE", style={"color": "white", "margin": "0", "padding": "10px"}),
            html.A("Logout", href="#", style={"color": "white", "float": "right", "padding": "10px"})
        ],
        style={"backgroundColor": "#002855", "display": "flex", "justifyContent": "space-between", "alignItems": "center"}
    ),

    # Título principal
    html.Div(
        html.H2("Extrator de dados do Siconfi", style={"textAlign": "center", "margin": "20px 0"})
    ),

    # Menu principal
    html.Div(
        [
            html.Label("Menu", style={"color": "white", "fontSize": "20px", "marginBottom": "10px"}),
            
            html.Div([
                dcc.Dropdown(id="documento-dropdown", options=[], placeholder="Selecione o documento", style={"marginBottom": "10px"}),
                dcc.Dropdown(id="exercicio-dropdown", options=[], placeholder="Selecione o exercício", style={"marginBottom": "10px"}),
                dcc.Dropdown(id="periodo-dropdown", options=[], placeholder="Selecione o período de referência (bimestre/quadrimestre)", style={"marginBottom": "10px"}),
                dcc.Dropdown(id="ente-dropdown", options=[], placeholder="Selecione o ente", style={"marginBottom": "10px"}),
                dcc.Dropdown(id="anexo-dropdown", options=[], placeholder="Selecione o anexo", style={"marginBottom": "10px"}),
                dbc.Button("Extrair dados", id="extrair-dados-btn", color="primary", style={"width": "100%"})
            ])
        ],
        style={
            "backgroundColor": "#003E70",
            "padding": "20px",
            "borderRadius": "10px",
            "width": "400px",
            "margin": "auto"
        }
    ),

    # Rodapé
    html.Div(
        [
            html.P("FINDATA", style={"textAlign": "center", "margin": "0"}),
            html.P("Sec. de Finanças do Recife", style={"textAlign": "center", "margin": "0"})
        ],
        style={"backgroundColor": "#f8f9fa", "padding": "10px", "marginTop": "20px"}
    )
])

# Rodar o aplicativo
if __name__ == "__main__":
    app.run_server(debug=True)