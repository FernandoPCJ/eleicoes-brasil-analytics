"""Download robusto do arquivo de candidaturas do TSE.

Uso:
    python -m src.extract.download_tse
"""
import logging
import time
from pathlib import Path

import requests

from src.extract.config_tse import (
    CANDIDATOS_ZIP_NAME,
    CANDIDATOS_ZIP_URL,
    RAW_DATA_DIR,
    garantir_diretorios,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

MAX_TENTATIVAS = 3
TIMEOUT_SEGUNDOS = 60
BACKOFF_BASE_SEGUNDOS = 2

# O CDN do TSE (por trás de um WAF) devolve 403 para clientes sem cara de
# navegador (ex.: o User-Agent padrão do requests, "python-requests/x.y").
# Um User-Agent e Referer de navegador comum resolvem na maioria dos casos.
HEADERS_NAVEGADOR = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://dadosabertos.tse.jus.br/",
}


class DownloadError(Exception):
    """Erro ao baixar arquivo do TSE após esgotar as tentativas."""


def download_arquivo(url: str, destino: Path, forcar: bool = False) -> Path:
    """Baixa um arquivo com retry e backoff exponencial.

    Args:
        url: URL de origem.
        destino: Caminho local de destino.
        forcar: Se True, baixa mesmo que o arquivo já exista.

    Returns:
        Caminho do arquivo baixado.

    Raises:
        DownloadError: se todas as tentativas falharem.
    """
    if destino.exists() and not forcar:
        logger.info("Arquivo já existe, pulando download: %s", destino)
        return destino

    ultimo_erro: Exception | None = None

    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            logger.info(
                "Baixando (tentativa %d/%d): %s", tentativa, MAX_TENTATIVAS, url
            )
            resposta = requests.get(
                url, timeout=TIMEOUT_SEGUNDOS, stream=True, headers=HEADERS_NAVEGADOR
            )
            resposta.raise_for_status()

            destino.parent.mkdir(parents=True, exist_ok=True)
            tmp_destino = destino.with_suffix(destino.suffix + ".part")

            total_bytes = 0
            with open(tmp_destino, "wb") as f:
                for chunk in resposta.iter_content(chunk_size=1024 * 256):
                    if chunk:
                        f.write(chunk)
                        total_bytes += len(chunk)

            if total_bytes == 0:
                raise DownloadError("Download retornou 0 bytes")

            tmp_destino.rename(destino)
            logger.info("Download concluído: %s (%d bytes)", destino, total_bytes)
            return destino

        except (requests.RequestException, DownloadError) as erro:
            ultimo_erro = erro
            logger.warning("Falha na tentativa %d: %s", tentativa, erro)
            if tentativa < MAX_TENTATIVAS:
                espera = BACKOFF_BASE_SEGUNDOS**tentativa
                logger.info("Aguardando %ds antes de tentar novamente...", espera)
                time.sleep(espera)

    raise DownloadError(
        f"Falha ao baixar {url} após {MAX_TENTATIVAS} tentativas: {ultimo_erro}"
    )


def main() -> Path:
    garantir_diretorios()
    destino = RAW_DATA_DIR / CANDIDATOS_ZIP_NAME
    return download_arquivo(CANDIDATOS_ZIP_URL, destino)


if __name__ == "__main__":
    main()
