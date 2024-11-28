from flask import Flask, render_template, request, send_file
import pandas as pd
import requests
import json
import time
import os
app = Flask(__name__)

# Carrega o DataFrame dos municípios
df_municipios = pd.read_excel(
    "data/estimativa_dou_2019.xlsx", 
    sheet_name=1, 
    header=1, 
    usecols=["cod. Munic 7D", "NOME DO MUNICÍPIO", "CAPITAL"]
).dropna()

# Lista de anexos para o RREO
anexos_rreo = [
    "RREO-Anexo%2001", "RREO-Anexo%2002", "RREO-Anexo%2003",
    "RREO-Anexo%2004", "RREO-Anexo%2004%20-%20RGPS", "RREO-Anexo%2004%20-%20RPPS",
    "RREO-Anexo%2004.0%20-%20RGPS", "RREO-Anexo%2004.1", "RREO-Anexo%2004.2",
    "RREO-Anexo%2004.3%20-%20RGPS", "RREO-Anexo%2005", "RREO-Anexo%2006",
    "RREO-Anexo%2007", "RREO-Anexo%2009", "RREO-Anexo%2010%20-%20RGPS",
    "RREO-Anexo%2010%20-%20RPPS", "RREO-Anexo%2011", "RREO-Anexo%2013", "RREO-Anexo%2014"
]


# Rota principal - Menu
@app.route("/")
def index():
    return render_template("index.html")

# Rotas para as páginas específicas
@app.route("/dca", methods=["GET", "POST"])
def dca():
    if request.method == "POST":
        # Captura os parâmetros do formulário
        anos = request.form.getlist("anos")
        entes_a_extrair = request.form.getlist("entes")
        anexos_a_extrair = request.form.getlist("anexos")

        # Verifica se parâmetros foram selecionados
        if not anos or not entes_a_extrair or not anexos_a_extrair:
            return "Por favor, selecione pelo menos um ano, ente e anexo.", 400

        # Converte anos para inteiros
        anos = list(map(int, anos))
        entes_a_extrair = list(map(int, entes_a_extrair))
        
        # Lista para armazenar os DataFrames de resultados
        lista_tabs = []

        # Lógica de extração
        for ano in anos:
            for ente in entes_a_extrair:
                for anexo in anexos_a_extrair:
                    url = f"https://apidatalake.tesouro.gov.br/ords/siconfi/tt/dca?an_exercicio={ano}&no_anexo={anexo}&id_ente={ente}"
                    print(f"Consultando URL (dca): {url}")

                    try:
                        time.sleep(3)  # Pausa para evitar sobrecarregar o servidor
                        response = requests.get(url, verify=False)
                        response.raise_for_status()

                        # Estrutura os dados em JSON
                        base = response.json()
                        info = base.get('items', [])

                        if info:
                            result = pd.DataFrame(info)
                            lista_tabs.append(result)
                    except Exception as e:
                        print(f"Erro ao consultar {url}: {e}")
                        continue

        # Concatena todos os DataFrames
        if lista_tabs:
            dataframes = pd.concat(lista_tabs)
            # Salva como CSV
            output_file = "dados_anexos_DCA.csv"
            dataframes.to_csv(output_file, sep=";", index=False, decimal=",")
            return send_file(output_file, as_attachment=True)
        else:
            return "Nenhum dado encontrado para os parâmetros selecionados.", 400

    # Exibe a página para seleção dos parâmetros
    return render_template(
        "dca.html",
        anos=list(range(2015, 2024)),
        entes=entes,
        anexos=anexos
    )
    # Lista de entes e anexos
entes = df_municipios["cod. Munic 7D"].astype('int').to_list()
anexos = [
    "Anexo%20I-AB",
    "Anexo%20I-C",
    "Anexo%20I-D",
    "Anexo%20I-E",
    "Anexo%20I-F",
    "Anexo%20I-G",
    "Anexo%20I-HI",
    "DCA-Anexo%20I-AB",
    "DCA-Anexo%20I-C",
    "DCA-Anexo%20I-D",
    "DCA-Anexo%20I-E",
    "DCA-Anexo%20I-F",
    "DCA-Anexo%20I-G",
    "DCA-Anexo%20I-HI"
]

@app.route("/rreo", methods=["GET", "POST"])
def rreo():
    if request.method == "POST":
        # Captura os parâmetros do formulário
        anos = request.form.getlist("anos")
        periodos = request.form.getlist("periodos")
        anexos_a_extrair = request.form.getlist("anexos")

        # Verifica se parâmetros foram selecionados
        if not anos or not periodos or not anexos_a_extrair:
            return "Por favor, selecione pelo menos um ano, período e anexo.", 400

        # Converte anos e períodos para inteiros
        anos = list(map(int, anos))
        periodos = list(map(int, periodos))

        # Lista para armazenar os DataFrames de resultados
        lista_tabs = []

        # Lógica de extração
        for ano in anos:
            for periodo in periodos:
                for index, row in df_municipios.iterrows():
                    ente = int(row["cod. Munic 7D"])
                    nome_municipio = row["NOME DO MUNICÍPIO"]

                    for anexo in anexos_a_extrair:
                        url = (f"https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo?"
                               f"an_exercicio={ano}&nr_periodo={periodo}"
                               f"&co_tipo_demonstrativo=RREO&no_anexo={anexo}&co_esfera=M&id_ente={ente}")
                        print(f"Consultando URL (RREO) para {nome_municipio} ({ente}) - Ano {ano}, Período {periodo}: {url}")

                        try:
                            time.sleep(3)  # Pausa para evitar sobrecarregar o servidor
                            response = requests.get(url, verify=False)
                            response.raise_for_status()

                            # Estrutura os dados em JSON
                            base = response.json()
                            info = base.get('items', [])

                            if info:
                                result = pd.DataFrame(info)
                                lista_tabs.append(result)
                        except Exception as e:
                            print(f"Erro ao consultar {url}: {e}")
                            continue

        # Concatena todos os DataFrames
        if lista_tabs:
            dataframes = pd.concat(lista_tabs)
            # Salva como CSV
            output_file = "dados_anexos_rreo.csv"
            dataframes.to_csv(output_file, sep=";", index=False, decimal=",")
            return send_file(output_file, as_attachment=True)
        else:
            return "Nenhum dado encontrado para os parâmetros selecionados.", 400

    # Exibe a página para seleção dos parâmetros
    return render_template(
        "rreo.html",
        anos=list(range(2020, 2025)),
        periodos=list(range(1, 7)),
        anexos=anexos_rreo
    )

@app.route("/rgf", methods=["GET", "POST"])
def rgf():
    if request.method == "POST":
        # Captura os parâmetros do formulário
        anos = request.form.getlist("anos")
        periodos = request.form.getlist("periodos")
        anexos = request.form.getlist("anexos")

        # Verifica se parâmetros foram selecionados
        if not anos or not periodos or not anexos:
            return "Por favor, selecione pelo menos um ano, período e anexo.", 400

        # Converte anos e períodos para inteiros
        anos = list(map(int, anos))
        periodos = list(map(int, periodos))
        
        # Lista para armazenar os DataFrames de resultados
        lista_tabs = []

        # Lógica de extração
        for ano in anos:
            for index, row in df_municipios.iterrows():
                ente = int(row["cod. Munic 7D"])
                nome_municipio = row["NOME DO MUNICÍPIO"]
                
                for periodo in periodos:
                    for anexo in anexos:
                        url = (f"https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rgf?"
                               f"an_exercicio={ano}&in_periodicidade=Q&nr_periodo={periodo}"
                               f"&co_tipo_demonstrativo=RGF&no_anexo={anexo}"
                               f"&co_esfera=M&co_poder=E&id_ente={ente}")
                        
                        print(f"Consultando URL para {nome_municipio} ({ente}) - Anexo: {anexo} - {url}")
                        
                        try:
                            # Pausa para evitar sobrecarregar o servidor
                            time.sleep(3)
                            
                            # Faz a requisição
                            response = requests.get(url, verify=False)
                            response.raise_for_status()
                            
                            # Estrutura os dados em JSON
                            data = response.json()
                            
                            # Verifica se há dados
                            if "items" in data and data["items"]:
                                result = pd.DataFrame(data["items"])
                                lista_tabs.append(result)
                        except Exception as e:
                            print(f"Erro ao consultar {url}: {e}")
                            continue

        # Concatena todos os DataFrames
        if lista_tabs:
            dataframes = pd.concat(lista_tabs)
            # Salva como CSV
            output_file = "dados_anexos_rgf.csv"
            dataframes.to_csv(output_file, sep=";", index=False, decimal=",")
            return send_file(output_file, as_attachment=True)
        else:
            return "Nenhum dado encontrado para os parâmetros selecionados.", 400
    
    # Exibe a página para seleção dos parâmetros
    return render_template(
        "rgf.html", 
        anos=list(range(2015, 2024)), 
        periodos=[1, 2, 3, 4], 
        anexos=["RGF-Anexo%2002", "RGF-Anexo%2005"]
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
