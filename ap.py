from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import requests
import json
import time
import os

app = Flask(__name__)

# Carrega os dados iniciais
df_municipios = pd.read_excel(
    "data/estimativa_dou_2019.xlsx",
    sheet_name=1,
    header=1,
    usecols=["cod. Munic 7D", "NOME DO MUNICÍPIO", "CAPITAL"]
).dropna()

# Lista de anos disponíveis
anos_disponiveis = list(range(2015, 2024))

# Lista de períodos e anexos disponíveis
periodos_disponiveis = [1, 2, 3, 4]
anexos_disponiveis = ["RGF-Anexo%2002", "RGF-Anexo%2005"]

# Rota principal para selecionar parâmetros
@app.route("/", methods=["GET", "POST"])
def rgf():
    if request.method == "POST":
        # Pega os parâmetros do formulário
        anos = request.form.getlist("anos")
        periodos = request.form.getlist("periodos")
        anexos = request.form.getlist("anexos")
        
        # Converte os anos e períodos para inteiros
        anos = list(map(int, anos))
        periodos = list(map(int, periodos))
        
        # Lista para armazenar os DataFrames dos resultados
        lista_tabs = []

        # Faz as extrações
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
                        
                        # Pausa para evitar sobrecarregar o servidor
                        time.sleep(3)
                        
                        # Faz a requisição
                        response = requests.get(url, verify=False)
                        
                        # Estrutura os dados em JSON
                        data = response.json()
                        
                        # Verifica se há dados
                        if "items" in data:
                            result = pd.DataFrame(data["items"])
                            lista_tabs.append(result)

        # Concatena todos os DataFrames
        if lista_tabs:
            dataframes = pd.concat(lista_tabs)
            # Salva como CSV
            output_file = "dados_anexos_rgf.csv"
            dataframes.to_csv(output_file, sep=";", index=False, decimal=",")
            return send_file(output_file, as_attachment=True)
        else:
            return "Nenhum dado encontrado para os parâmetros selecionados!", 400

    return render_template("rgf.html", anos=anos_disponiveis, periodos=periodos_disponiveis, anexos=anexos_disponiveis)

if __name__ == "__main__":
    app.run(debug=True)
