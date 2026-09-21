"""Extração (unzip) do CSV de candidaturas do TSE.

Uso:
    python -m src.extract.extract_tse
"""
import logging
import zipfile
from pathlib import Path

from src.extract.config_tse import (
    CANDIDATOS_CSV_NAME,
    CANDIDATOS_ZIP_NAME,
    RAW_DATA_DIR,
    garantir_diretorios,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


class ExtracaoError(Exception):
    """Erro ao extrair arquivo do zip do TSE."""


def extrair_zip(nome_zip: str, arquivo_saida: str, forcar: bool = False) -> Path:
    """Extrai um arquivo específico de dentro de um zip do TSE.

    Args:
        nome_zip: Nome do arquivo zip (dentro de RAW_DATA_DIR).
        arquivo_saida: Nome (ou substring) do arquivo a extrair do zip.
        forcar: Se True, extrai mesmo que o destino já exista.

    Returns:
        Caminho do arquivo extraído.
    """
    origem = RAW_DATA_DIR / nome_zip
    destino = RAW_DATA_DIR / arquivo_saida

    if not origem.exists():
        raise ExtracaoError(
            f"Zip não encontrado em {origem}. Rode o download primeiro."
        )

    if destino.exists() and not forcar:
        logger.info("Arquivo já extraído, pulando: %s", destino)
        return destino

    logger.info("Extraindo %s de %s", arquivo_saida, origem)

    with zipfile.ZipFile(origem, "r") as zip_ref:
        candidatos = [x for x in zip_ref.namelist() if arquivo_saida in x]

        if not candidatos:
            raise ExtracaoError(
                f"Nenhum arquivo contendo '{arquivo_saida}' encontrado em {origem}. "
                f"Conteúdo do zip: {zip_ref.namelist()}"
            )

        nome_interno = candidatos[0]
        zip_ref.extract(nome_interno, RAW_DATA_DIR)

        extraido = RAW_DATA_DIR / nome_interno
        if extraido != destino:
            extraido.rename(destino)

    logger.info("Extraído com sucesso: %s", destino)
    return destino


def main() -> Path:
    garantir_diretorios()
    return extrair_zip(CANDIDATOS_ZIP_NAME, CANDIDATOS_CSV_NAME)


if __name__ == "__main__":
    main()
