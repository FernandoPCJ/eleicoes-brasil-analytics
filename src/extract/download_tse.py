import requests
from pathlib import Path

from src.extract.config_tse import RAW_DATA_DIR


URL_CANDIDATOS = (
    "https://dadosabertos.tse.jus.br/"
)


def download_arquivo(url, destino):

    print("Iniciando download...")
    print("Origem:", url)

    resposta = requests.get(url)

    print("Status:", resposta.status_code)

    if resposta.status_code == 200:
        destino.write_bytes(resposta.content)
        print("Arquivo salvo em:")
        print(destino)

    else:
        print("Erro no download")


if __name__ == "__main__":

    arquivo = RAW_DATA_DIR / "teste_tse.txt"

    download_arquivo(
        URL_CANDIDATOS,
        arquivo
    )