from pathlib import Path


# Ano da eleição
ANO_ELEICAO = 2026


# Diretório raiz do projeto
BASE_DIR = Path(__file__).resolve().parents[2]


# Diretório onde serão armazenados os dados brutos
RAW_DATA_DIR = BASE_DIR / "data" / "raw"


# Diretório dos dados tratados
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"


# URL base do portal de dados do TSE
TSE_BASE_URL = (
    "https://dadosabertos.tse.jus.br"
)


print("Configuração TSE carregada!")
print("Projeto:", BASE_DIR)
print("Dados brutos:", RAW_DATA_DIR)