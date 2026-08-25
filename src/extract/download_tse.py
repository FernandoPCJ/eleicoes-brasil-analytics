from pathlib import Path
import requests


BASE_DIR = Path(__file__).resolve().parents[2]

RAW_DATA = BASE_DIR / "data" / "raw"


def criar_pasta_raw():
    RAW_DATA.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    criar_pasta_raw()

    print("Pasta de dados brutos:")
    print(RAW_DATA)

    print("Extract configurado com sucesso!")