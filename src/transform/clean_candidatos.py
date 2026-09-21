"""Limpeza e padronização dos dados brutos de candidaturas do TSE.

Lê o CSV bruto (separador ';', encoding latin-1, como o TSE publica),
renomeia colunas para nomes limpos em português, remove valores sentinela
("#NULO#", "-1", etc.) e grava um CSV processado com colunas estáveis
para as próximas etapas (star schema, dashboard).

Uso:
    python -m src.transform.clean_candidatos
"""
import csv
import logging
from pathlib import Path
from typing import Iterator

from src.extract.config_tse import (
    CANDIDATOS_CSV_NAME,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    TSE_ENCODING,
    TSE_SEPARATOR,
    garantir_diretorios,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# Mapeamento coluna bruta (TSE) -> coluna limpa (usada no restante do pipeline)
MAPA_COLUNAS = {
    "ANO_ELEICAO": "ano_eleicao",
    "NR_TURNO": "turno",
    "SG_UF": "uf",
    "DS_CARGO": "cargo",
    "SQ_CANDIDATO": "sq_candidato",
    "NR_CANDIDATO": "nr_candidato",
    "NM_CANDIDATO": "nm_candidato",
    "NM_URNA_CANDIDATO": "nm_urna_candidato",
    "SG_PARTIDO": "partido",
    "NM_PARTIDO": "nm_partido",
    "DS_GENERO": "genero",
    "DS_COR_RACA": "cor_raca",
    "DS_GRAU_INSTRUCAO": "escolaridade",
    "DS_ESTADO_CIVIL": "estado_civil",
    "DS_SITUACAO_CANDIDATURA": "situacao_candidatura",
    "DS_SIT_TOT_TURNO": "situacao_totalizacao",
    "DT_NASCIMENTO": "dt_nascimento",
}

# Valores sentinela que o TSE usa para "não informado" / "não se aplica"
VALORES_NULOS = {"#NULO#", "#NE#", "-1", "-3", ""}

COLUNAS_OBRIGATORIAS = [
    "sq_candidato",
    "nr_candidato",
    "cargo",
    "uf",
    "partido",
]


class TransformError(Exception):
    """Erro na etapa de limpeza/transformação."""


def _limpar_valor(valor: str) -> str | None:
    valor = (valor or "").strip()
    return None if valor in VALORES_NULOS else valor


def ler_bruto(caminho_csv: Path) -> Iterator[dict]:
    """Lê o CSV bruto do TSE linha a linha (evita carregar tudo em memória)."""
    if not caminho_csv.exists():
        raise TransformError(
            f"CSV bruto não encontrado em {caminho_csv}. Rode a extração primeiro."
        )

    with open(caminho_csv, encoding=TSE_ENCODING, newline="") as f:
        leitor = csv.DictReader(f, delimiter=TSE_SEPARATOR)
        for linha in leitor:
            yield linha


def limpar_linha(linha: dict) -> dict | None:
    """Aplica o mapeamento de colunas e limpeza de valores a uma linha bruta."""
    limpa = {}
    for coluna_bruta, coluna_limpa in MAPA_COLUNAS.items():
        limpa[coluna_limpa] = _limpar_valor(linha.get(coluna_bruta, ""))

    for coluna in COLUNAS_OBRIGATORIAS:
        if not limpa.get(coluna):
            return None  # descarta linhas sem dados essenciais

    return limpa


def limpar(caminho_csv: Path) -> list[dict]:
    """Lê e limpa o CSV bruto completo, retornando as linhas válidas."""
    total_lidas = 0
    total_descartadas = 0
    linhas_limpas = []

    for linha_bruta in ler_bruto(caminho_csv):
        total_lidas += 1
        linha_limpa = limpar_linha(linha_bruta)
        if linha_limpa is None:
            total_descartadas += 1
            continue
        linhas_limpas.append(linha_limpa)

    logger.info(
        "Limpeza concluída: %d linhas lidas, %d descartadas, %d válidas",
        total_lidas,
        total_descartadas,
        len(linhas_limpas),
    )
    return linhas_limpas


def salvar_processed(linhas: list[dict], nome_arquivo: str = "candidatos_2026.csv") -> Path:
    """Grava as linhas limpas como CSV na camada processed."""
    if not linhas:
        raise TransformError("Nenhuma linha para salvar")

    garantir_diretorios()
    destino = PROCESSED_DATA_DIR / nome_arquivo
    colunas = list(linhas[0].keys())

    with open(destino, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=colunas)
        escritor.writeheader()
        escritor.writerows(linhas)

    logger.info("Salvo: %s (%d linhas)", destino, len(linhas))
    return destino


def main() -> Path:
    caminho_bruto = RAW_DATA_DIR / CANDIDATOS_CSV_NAME
    linhas = limpar(caminho_bruto)
    return salvar_processed(linhas)


if __name__ == "__main__":
    main()
