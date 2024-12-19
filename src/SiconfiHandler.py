import requests
import pandas as pd
import json

class SiconfiHandler:
    def __init__(self):
        self.base_url = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/"
        self.mounted_url = None  # Adicione essa linha para inicializar self.mounted_url

    def mount_url(
        self,
        ano: int,
        periodo: int,
        documento: str,
        cd_anexo: str,
        cd_municipio: str,
        nm_municipio: str,
        cd_esfera: str = "M",
        debug=False,
    ):
        print(
            f"Extraindo {documento} - {nm_municipio} - {periodo} - {ano} ANEXO {cd_anexo}"
        )

        if documento == "rreo":
            self.mounted_url = (
                self.base_url + f"rreo?an_exercicio={ano}"
                f"&nr_periodo={periodo}&co_tipo_demonstrativo=RREO&no_anexo=RREO"
                f"-Anexo%200{cd_anexo}&co_esfera={cd_esfera}&id_ente={cd_municipio}"
            )

        elif documento == "rgf":
            self.mounted_url = (
                self.base_url + f"rgf?an_exercicio={ano}"
                f"&in_periodicidade=Q&nr_periodo={periodo}&co_tipo_demonstrativo=RGF&no_anexo=RGF"
                f"-Anexo%200{cd_anexo}&co_esfera={cd_esfera}&co_poder=E&id_ente={cd_municipio}"
            )

        elif documento == "dca":
            self.mounted_url = (
                self.base_url + f"dca?an_exercicio={ano}"
                f"&no_anexo=DCA-Anexo%20I-{cd_anexo}&id_ente={cd_municipio}"
            )

        elif documento == "capag":
            self.mounted_url = "http://www.tesourotransparente.gov.br/ckan/api/3/action/package_show?id=capag-municipios"

        if debug:
            print(self.mounted_url)

    def receive_data(self):
        try:
            r = requests.get(
                self.mounted_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
                },
            )
            if r.status_code == 200:
                base = json.loads(r.text)
                info = base["items"]
                df = pd.DataFrame(info)
                print("Data received successfully")
                return df
            else:
                print(f"Request failed with status code: {r.status_code}")
                return None

        except Exception as e:
            print(f"Error during data retrieval: {str(e)}")
            return None