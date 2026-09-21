"""Configuração da extração de dados do TSE."""
from pathlib import Path

# Ano da eleição alvo deste pipeline
ANO_ELEICAO = 2026

# Diretório raiz do projeto
BASE_DIR = Path(__file__).resolve().parents[2]

# Diretórios de dados
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
WAREHOUSE_DIR = BASE_DIR / "data" / "warehouse"

# Portal de dados abertos do TSE
TSE_BASE_URL = "https://cdn.tse.jus.br/estatistica/sead/odsele"

# Nome do arquivo zip de candidaturas (padrão do portal: consulta_cand_<ano>.zip)
CANDIDATOS_ZIP_NAME = f"consulta_cand_{ANO_ELEICAO}.zip"
CANDIDATOS_ZIP_URL = f"{TSE_BASE_URL}/consulta_cand/{CANDIDATOS_ZIP_NAME}"

# Nome do arquivo CSV consolidado (Brasil) dentro do zip
CANDIDATOS_CSV_NAME = f"consulta_cand_{ANO_ELEICAO}_BRASIL.csv"

# Encoding e separador usados pelo TSE nos arquivos de dados abertos
TSE_ENCODING = "latin-1"
TSE_SEPARATOR = ";"


def garantir_diretorios() -> None:
    """Garante que os diretórios de dados existam."""
    for diretorio in (RAW_DATA_DIR, PROCESSED_DATA_DIR, WAREHOUSE_DIR):
        diretorio.mkdir(parents=True, exist_ok=True)
