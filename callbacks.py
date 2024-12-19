#callbacks
# Importando as bibliotecas e módulos necessários
from dash import Dash, State, Input, Output, html, dcc
from layout import extract, carrega_municipios, generate_output_table, convert_df
import pandas as pd
import base64


# Carregando a lista de municípios
df_municipio = carrega_municipios()

# Criando a instância do aplicativo Dash
app = Dash(__name__)
server = app.server

# Definindo a função de callbacks
def callbacks(app):
    @app.callback(
        Output("output-div", "children"),
        [Input("extract-button", "n_clicks")],
        [
            State("documento-dropdown", "value"),
            State("anos-dropdown", "value"),
            State("periodos-dropdown", "value"),
            State("entes-dropdown", "value"),
            State("anexo-dropdown", "value"),
        ]
    )
    def extract_and_download_data(n_clicks, documento, anos, periodos, entes, anexo):
        # Retorna uma lista vazia na carga inicial da página ou atualização
        if n_clicks is None:
            return []

        # Verifica se todos os campos obrigatórios foram preenchidos
        if not (documento and anos and periodos and entes and anexo):
            return [html.H3("Por favor, preencha todos os campos.", style={"color": "black"})]

        # Filtra o DataFrame de municípios com base nos entes selecionados
        df_municipios_filtered = df_municipio[df_municipio["cod_completo"].isin(entes)]
        cod_entes = df_municipios_filtered["cod_completo"].tolist()
        nome_entes = df_municipios_filtered["nome_municipio"].tolist()

        # Extrai os dados usando a função 'extract'
        data = extract(anos, periodos, documento, anexo, cod_entes, nome_entes)

        # Converta o DataFrame para CSV
        csv_data = data.to_csv(index=False).encode("utf-8")

        # Cria o componente de download (âncora) com o link para download
        download_link = html.A(
            "Clique aqui para fazer o download dos dados",
            href=f"data:text/csv;base64,{base64.b64encode(csv_data).decode()}",
            download="dados_extraidos.csv",
            target="_blank",  # Abrir o link em uma nova guia
        )

        # Prepara a saída para exibição no aplicativo
        output_children = [
            html.H3("", style={"color": "black"}),
            download_link,
            html.Table(
                # Cabeçalho da tabela
                [html.Tr([html.Th(col) for col in data.columns])] +
                # Linhas da tabela
                [html.Tr([html.Td(val) for val in row]) for row in data.values],
                style={"border": "1px solid black", "border-collapse": "collapse"}
            )
        ]

        return output_children

# Registra os callbacks e executa o servidor
if __name__ == "__main__":
    callbacks(app)
    app.run_server()




