from flask import Flask, render_template, request, send_file
import pandas as pd
import requests
import urllib3
import os
from concurrent.futures import ThreadPoolExecutor

# Desabilita avisos de HTTPS não verificado
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# Carrega o DataFrame dos municípios
try:
    df_municipios = pd.read_excel(
        "data/estimativa_dou_2019.xlsx", 
        sheet_name=1, 
        header=1, 
        usecols=["cod. Munic 7D", "NOME DO MUNICÍPIO", "CAPITAL"]
    ).dropna()
except FileNotFoundError:
    raise FileNotFoundError("O arquivo 'data/estimativa_dou_2019.xlsx' não foi encontrado.")

# Listas de anexos e entes
anexos_rreo = [
    "RREO-Anexo%2001", "RREO-Anexo%2002", "RREO-Anexo%2003",
    "RREO-Anexo%2004", "RREO-Anexo%2004%20-%20RGPS", "RREO-Anexo%2004%20-%20RPPS",
    "RREO-Anexo%2004.0%20-%20RGPS", "RREO-Anexo%2004.1", "RREO-Anexo%2004.2",
    "RREO-Anexo%2004.3%20-%20RGPS", "RREO-Anexo%2005", "RREO-Anexo%2006",
    "RREO-Anexo%2007", "RREO-Anexo%2009", "RREO-Anexo%2010%20-%20RGPS",
    "RREO-Anexo%2010%20-%20RPPS", "RREO-Anexo%2011", "RREO-Anexo%2013", "RREO-Anexo%2014"
]

anexos_dca = [
    "Anexo%20I-AB", "Anexo%20I-C", "Anexo%20I-D", "Anexo%20I-E", "Anexo%20I-F",
    "Anexo%20I-G", "Anexo%20I-HI", "DCA-Anexo%20I-AB", "DCA-Anexo%20I-C",
    "DCA-Anexo%20I-D", "DCA-Anexo%20I-E", "DCA-Anexo%20I-F", "DCA-Anexo%20I-G",
    "DCA-Anexo%20I-HI"
]

anexos_rgf = [
    "RGF-Anexo%2001", "RGF-Anexo%2002", "RGF-Anexo%2003", 
    "RGF-Anexo%2004", "RGF-Anexo%2005", "RGF-Anexo%2006"
]

entes = df_municipios["cod. Munic 7D"].astype('int').to_list()

# Função para realizar a requisição

def fetch_data(url):
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        return response.json().get("items", [])
    except Exception as e:
        print(f"Erro ao consultar {url}: {e}")
        return []

@app.route("/")
def index():
    return render_template("base.html")

@app.route("/dca", methods=["GET", "POST"])
def dca():
    if request.method == "POST":
        anos = request.form.getlist("anos")
        entes_a_extrair = request.form.getlist("entes")
        anexos_a_extrair = request.form.getlist("anexos")

        if not anos or not entes_a_extrair or not anexos_a_extrair:
            return "Por favor, selecione pelo menos um ano, ente e anexo.", 400

        anos = list(map(int, anos))
        entes_a_extrair = list(map(int, entes_a_extrair))
        urls = []

        for ano in anos:
            for ente in entes_a_extrair:
                for anexo in anexos_a_extrair:
                    urls.append(
                        f"https://apidatalake.tesouro.gov.br/ords/siconfi/tt/dca?"
                        f"an_exercicio={ano}&no_anexo={anexo}&id_ente={ente}"
                    )

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fetch_data, url) for url in urls]
            results = [future.result() for future in futures]

        if results:
            dataframes = pd.concat([pd.DataFrame(result) for result in results if result])
            output_file = "dados_anexos_DCA.csv"
            dataframes.to_csv(output_file, sep=";", index=False, decimal=",")
            return send_file(output_file, as_attachment=True)
        else:
            return "Nenhum dado encontrado para os parâmetros selecionados.", 400

    return render_template("dca.html", anos=list(range(2015, 2024)), entes=entes, anexos=anexos_dca)

@app.route("/rreo", methods=["GET", "POST"])
def rreo():
    if request.method == "POST":
        anos = request.form.getlist("anos")
        periodos = request.form.getlist("periodos")
        anexos_a_extrair = request.form.getlist("anexos")
        municipios_selecionados = request.form.getlist("municipios")

        if not anos or not periodos or not anexos_a_extrair or not municipios_selecionados:
            return "Por favor, selecione pelo menos um ano, período, anexo e município.", 400

        anos = list(map(int, anos))
        periodos = list(map(int, periodos))
        municipios_selecionados = list(map(int, municipios_selecionados))
        urls = []

        for ano in anos:
            for periodo in periodos:
                for municipio in municipios_selecionados:
                    for anexo in anexos_a_extrair:
                        urls.append(
                            f"https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo?"
                            f"an_exercicio={ano}&nr_periodo={periodo}&co_tipo_demonstrativo=RREO"
                            f"&no_anexo={anexo}&co_esfera=M&id_ente={municipio}"
                        )

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fetch_data, url) for url in urls]
            results = [future.result() for future in futures]

        if results:
            dataframes = pd.concat([pd.DataFrame(result) for result in results if result])
            output_file = "dados_anexos_RREO.csv"
            dataframes.to_csv(output_file, sep=";", index=False, decimal=",")
            return send_file(output_file, as_attachment=True)
        else:
            return "Nenhum dado encontrado para os parâmetros selecionados.", 400

    return render_template("rreo.html", anos=list(range(2015, 2025)), periodos=list(range(1, 7)), anexos=anexos_rreo, municipios=df_municipios[["cod. Munic 7D", "NOME DO MUNICÍPIO"]].to_dict(orient="records"))

@app.route("/rgf", methods=["GET", "POST"])
def rgf():
    if request.method == "POST":
        anos = request.form.getlist("anos")
        periodos = request.form.getlist("periodos")
        anexos = request.form.getlist("anexos")
        municipios = request.form.getlist("municipios")

        if not anos or not periodos or not anexos or not municipios:
            return "Por favor, selecione pelo menos um ano, período, anexo e município.", 400

        anos = list(map(int, anos))
        periodos = list(map(int, periodos))
        municipios = list(map(int, municipios))
        urls = []

        for ano in anos:
            for municipio in municipios:
                for periodo in periodos:
                    for anexo in anexos:
                        for poder in ["E", "L"]:
                            urls.append(
                                f"https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rgf?"
                                f"an_exercicio={ano}&in_periodicidade=Q&nr_periodo={periodo}"
                                f"&co_tipo_demonstrativo=RGF&no_anexo={anexo}"
                                f"&co_esfera=M&co_poder={poder}&id_ente={municipio}"
                            )

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fetch_data, url) for url in urls]
            results = [future.result() for future in futures]

        if results:
            dataframes = pd.concat([pd.DataFrame(result) for result in results if result])
            output_file = "dados_anexos_RGF.csv"
            dataframes.to_csv(output_file, sep=";", index=False, decimal=",")
            return send_file(output_file, as_attachment=True)
        else:
            return "Nenhum dado encontrado para os parâmetros selecionados.", 400

    return render_template("rgf.html", anos=list(range(2015, 2026)), periodos=[1, 2, 3, 4], anexos=anexos_rgf, municipios=df_municipios[["cod. Munic 7D", "NOME DO MUNICÍPIO"]].to_dict(orient="records"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
