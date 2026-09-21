"""Constrói o star schema (modelo dimensional) a partir dos dados processados.

Grão da fato: uma candidatura (um candidato, em um cargo, em um estado,
por um partido, numa eleição/turno específicos).

Tabelas:
    dim_candidato(sk_candidato, sq_candidato, nr_candidato, nm_candidato,
                  nm_urna_candidato, genero, cor_raca, escolaridade, estado_civil)
    dim_cargo(sk_cargo, cargo)
    dim_estado(sk_estado, uf)
    dim_partido(sk_partido, sigla_partido, nome_partido)
    fato_candidatura(sk_candidato, sk_cargo, sk_estado, sk_partido,
                      ano_eleicao, turno, situacao_candidatura, situacao_totalizacao)

Usa SQLite (biblioteca padrão do Python) como warehouse local — sem
dependências externas. O mesmo DDL/DML funciona em Postgres com ajustes
mínimos de tipos (ver README, seção "Evoluindo para Postgres").

Uso:
    python -m src.load.build_star_schema
"""
import csv
import logging
import sqlite3
from pathlib import Path

from src.extract.config_tse import PROCESSED_DATA_DIR, WAREHOUSE_DIR, garantir_diretorios

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

DDL = """
DROP TABLE IF EXISTS fato_candidatura;
DROP TABLE IF EXISTS dim_candidato;
DROP TABLE IF EXISTS dim_cargo;
DROP TABLE IF EXISTS dim_estado;
DROP TABLE IF EXISTS dim_partido;

CREATE TABLE dim_candidato (
    sk_candidato        INTEGER PRIMARY KEY AUTOINCREMENT,
    sq_candidato         TEXT UNIQUE NOT NULL,
    nr_candidato          TEXT,
    nm_candidato          TEXT,
    nm_urna_candidato     TEXT,
    genero                TEXT,
    cor_raca              TEXT,
    escolaridade          TEXT,
    estado_civil          TEXT,
    dt_nascimento         TEXT
);

CREATE TABLE dim_cargo (
    sk_cargo    INTEGER PRIMARY KEY AUTOINCREMENT,
    cargo        TEXT UNIQUE NOT NULL
);

CREATE TABLE dim_estado (
    sk_estado   INTEGER PRIMARY KEY AUTOINCREMENT,
    uf           TEXT UNIQUE NOT NULL
);

CREATE TABLE dim_partido (
    sk_partido      INTEGER PRIMARY KEY AUTOINCREMENT,
    sigla_partido    TEXT UNIQUE NOT NULL,
    nome_partido     TEXT
);

CREATE TABLE fato_candidatura (
    sk_candidatura          INTEGER PRIMARY KEY AUTOINCREMENT,
    sk_candidato            INTEGER NOT NULL REFERENCES dim_candidato(sk_candidato),
    sk_cargo                INTEGER NOT NULL REFERENCES dim_cargo(sk_cargo),
    sk_estado               INTEGER NOT NULL REFERENCES dim_estado(sk_estado),
    sk_partido              INTEGER NOT NULL REFERENCES dim_partido(sk_partido),
    ano_eleicao              INTEGER,
    turno                    INTEGER,
    situacao_candidatura     TEXT,
    situacao_totalizacao     TEXT
);

CREATE INDEX idx_fato_candidato ON fato_candidatura(sk_candidato);
CREATE INDEX idx_fato_cargo ON fato_candidatura(sk_cargo);
CREATE INDEX idx_fato_estado ON fato_candidatura(sk_estado);
CREATE INDEX idx_fato_partido ON fato_candidatura(sk_partido);
"""


class StarSchemaError(Exception):
    """Erro ao construir o star schema."""


def ler_processed(caminho_csv: Path) -> list[dict]:
    if not caminho_csv.exists():
        raise StarSchemaError(
            f"CSV processado não encontrado em {caminho_csv}. Rode a transformação primeiro."
        )
    with open(caminho_csv, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _get_or_create_sk(cursor: sqlite3.Cursor, tabela: str, coluna_chave: str,
                       valor: str, colunas_extra: dict | None = None) -> int:
    """Busca a surrogate key de uma dimensão; cria a linha se não existir (upsert simples)."""
    cursor.execute(f"SELECT sk_{tabela.replace('dim_', '')} FROM {tabela} WHERE {coluna_chave} = ?", (valor,))
    linha = cursor.fetchone()
    if linha:
        return linha[0]

    colunas_extra = colunas_extra or {}
    colunas = [coluna_chave] + list(colunas_extra.keys())
    valores = [valor] + list(colunas_extra.values())
    placeholders = ", ".join("?" for _ in colunas)
    cursor.execute(
        f"INSERT INTO {tabela} ({', '.join(colunas)}) VALUES ({placeholders})",
        valores,
    )
    return cursor.lastrowid


def construir(linhas: list[dict], caminho_db: Path) -> Path:
    if not linhas:
        raise StarSchemaError("Nenhuma linha para carregar no star schema")

    garantir_diretorios()
    caminho_db.parent.mkdir(parents=True, exist_ok=True)

    conexao = sqlite3.connect(caminho_db)
    conexao.executescript(DDL)
    cursor = conexao.cursor()

    total_fatos = 0
    for linha in linhas:
        sk_candidato = _get_or_create_sk(
            cursor, "dim_candidato", "sq_candidato", linha["sq_candidato"],
            {
                "nr_candidato": linha.get("nr_candidato"),
                "nm_candidato": linha.get("nm_candidato"),
                "nm_urna_candidato": linha.get("nm_urna_candidato"),
                "genero": linha.get("genero"),
                "cor_raca": linha.get("cor_raca"),
                "escolaridade": linha.get("escolaridade"),
                "estado_civil": linha.get("estado_civil"),
                "dt_nascimento": linha.get("dt_nascimento"),
            },
        )
        sk_cargo = _get_or_create_sk(cursor, "dim_cargo", "cargo", linha["cargo"])
        sk_estado = _get_or_create_sk(cursor, "dim_estado", "uf", linha["uf"])
        sk_partido = _get_or_create_sk(
            cursor, "dim_partido", "sigla_partido", linha["partido"],
            {"nome_partido": linha.get("nm_partido")},
        )

        cursor.execute(
            """
            INSERT INTO fato_candidatura
                (sk_candidato, sk_cargo, sk_estado, sk_partido,
                 ano_eleicao, turno, situacao_candidatura, situacao_totalizacao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sk_candidato,
                sk_cargo,
                sk_estado,
                sk_partido,
                linha.get("ano_eleicao"),
                linha.get("turno"),
                linha.get("situacao_candidatura"),
                linha.get("situacao_totalizacao"),
            ),
        )
        total_fatos += 1

    conexao.commit()
    conexao.close()

    logger.info("Star schema construído em %s (%d candidaturas)", caminho_db, total_fatos)
    return caminho_db


def main() -> Path:
    linhas = ler_processed(PROCESSED_DATA_DIR / "candidatos_2026.csv")
    return construir(linhas, WAREHOUSE_DIR / "eleicoes.db")


if __name__ == "__main__":
    main()
