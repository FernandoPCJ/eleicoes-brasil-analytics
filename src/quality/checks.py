"""Testes de qualidade de dados sobre o star schema.

Roda um conjunto de verificações (contagem, nulos em colunas-chave,
integridade referencial fato<->dimensões, domínio de valores) e reporta
falhas de forma clara. Pensado para rodar a cada execução do pipeline
(e depois, em CI).

Uso:
    python -m src.quality.checks
"""
import logging
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path

from src.extract.config_tse import WAREHOUSE_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class ResultadoCheck:
    nome: str
    ok: bool
    detalhe: str


def _checar_contagem_minima(conexao: sqlite3.Connection) -> ResultadoCheck:
    total = conexao.execute("SELECT COUNT(*) FROM fato_candidatura").fetchone()[0]
    ok = total > 0
    return ResultadoCheck(
        "contagem_minima_fato",
        ok,
        f"{total} linhas em fato_candidatura" if ok else "fato_candidatura está vazia",
    )


def _checar_nulos_colunas_chave(conexao: sqlite3.Connection) -> ResultadoCheck:
    colunas = ["sk_candidato", "sk_cargo", "sk_estado", "sk_partido"]
    problemas = []
    for coluna in colunas:
        total_nulos = conexao.execute(
            f"SELECT COUNT(*) FROM fato_candidatura WHERE {coluna} IS NULL"
        ).fetchone()[0]
        if total_nulos > 0:
            problemas.append(f"{coluna}: {total_nulos} nulos")
    ok = not problemas
    return ResultadoCheck(
        "nulos_colunas_chave",
        ok,
        "nenhum nulo em chaves estrangeiras" if ok else "; ".join(problemas),
    )


def _checar_integridade_referencial(conexao: sqlite3.Connection) -> ResultadoCheck:
    verificacoes = {
        "sk_candidato": "dim_candidato",
        "sk_cargo": "dim_cargo",
        "sk_estado": "dim_estado",
        "sk_partido": "dim_partido",
    }
    orfaos = []
    for coluna_fk, tabela_dim in verificacoes.items():
        coluna_pk = coluna_fk
        total_orfaos = conexao.execute(
            f"""
            SELECT COUNT(*) FROM fato_candidatura f
            LEFT JOIN {tabela_dim} d ON f.{coluna_fk} = d.{coluna_pk}
            WHERE d.{coluna_pk} IS NULL
            """
        ).fetchone()[0]
        if total_orfaos > 0:
            orfaos.append(f"{coluna_fk} -> {tabela_dim}: {total_orfaos} órfãos")
    ok = not orfaos
    return ResultadoCheck(
        "integridade_referencial",
        ok,
        "todas as chaves estrangeiras íntegras" if ok else "; ".join(orfaos),
    )


def _checar_duplicatas_candidato(conexao: sqlite3.Connection) -> ResultadoCheck:
    total_duplicatas = conexao.execute(
        """
        SELECT COUNT(*) FROM (
            SELECT sq_candidato, COUNT(*) c
            FROM dim_candidato
            GROUP BY sq_candidato
            HAVING c > 1
        )
        """
    ).fetchone()[0]
    ok = total_duplicatas == 0
    return ResultadoCheck(
        "sem_duplicatas_candidato",
        ok,
        "sem candidatos duplicados" if ok else f"{total_duplicatas} sq_candidato duplicados",
    )


def _checar_turno_valido(conexao: sqlite3.Connection) -> ResultadoCheck:
    total_invalidos = conexao.execute(
        "SELECT COUNT(*) FROM fato_candidatura WHERE turno NOT IN ('1', '2') AND turno IS NOT NULL"
    ).fetchone()[0]
    ok = total_invalidos == 0
    return ResultadoCheck(
        "turno_dominio_valido",
        ok,
        "todos os turnos são 1 ou 2" if ok else f"{total_invalidos} linhas com turno fora do domínio",
    )


CHECKS = [
    _checar_contagem_minima,
    _checar_nulos_colunas_chave,
    _checar_integridade_referencial,
    _checar_duplicatas_candidato,
    _checar_turno_valido,
]


def rodar_checks(caminho_db: Path) -> list[ResultadoCheck]:
    if not caminho_db.exists():
        raise FileNotFoundError(f"Banco não encontrado em {caminho_db}. Rode a carga primeiro.")

    conexao = sqlite3.connect(caminho_db)
    try:
        return [check(conexao) for check in CHECKS]
    finally:
        conexao.close()


def main() -> int:
    resultados = rodar_checks(WAREHOUSE_DIR / "eleicoes.db")

    falhas = 0
    for resultado in resultados:
        status = "OK" if resultado.ok else "FALHOU"
        nivel = logger.info if resultado.ok else logger.error
        nivel("[%s] %s: %s", status, resultado.nome, resultado.detalhe)
        if not resultado.ok:
            falhas += 1

    if falhas:
        logger.error("%d/%d checks de qualidade falharam", falhas, len(resultados))
        return 1

    logger.info("Todos os %d checks de qualidade passaram", len(resultados))
    return 0


if __name__ == "__main__":
    sys.exit(main())
