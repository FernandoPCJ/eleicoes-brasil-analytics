import zipfile
from pathlib import Path

BASE_DIR = Path.cwd()

RAW_DATA = BASE_DIR / "data" / "raw"


def extrair_zip(nome_zip, arquivo_saida):

    origem = RAW_DATA / nome_zip

    destino = RAW_DATA / arquivo_saida

    print("Extraindo:", origem)

    with zipfile.ZipFile(origem, "r") as zip_ref:

        arquivo = [
            x for x in zip_ref.namelist()
            if arquivo_saida in x
        ][0]

        zip_ref.extract(
            arquivo,
            RAW_DATA
        )

        print("Extraído:", arquivo)


if __name__ == "__main__":

    extrair_zip(
        "consulta_cand_2026.zip",
        "consulta_cand_2026_BRASIL.csv"
    )