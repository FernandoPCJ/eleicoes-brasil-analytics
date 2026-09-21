"""Consultas de leitura sobre a camada gold (star schema) para consumo
pelo dashboard e por análises ad-hoc.

Mantém o mesmo "shape" de colunas que o dashboard já usava com o parquet
único (genero, cargo, cor_raca, escolaridade, idade, ...), só que agora
lendo de um modelo dimensional de verdade.
"""
import sqlite3
from pathlib import Path

import pandas as pd

QUERY_CANDIDATOS = """
SELECT
    c.sq_candidato,
    c.nr_candidato,
    c.nm_candidato,
    c.nm_urna_candidato,
    c.genero,
    c.cor_raca,
    c.escolaridade,
    c.estado_civil,
    c.dt_nascimento,
    cg.cargo,
    e.uf,
    p.sigla_partido AS partido,
    p.nome_partido,
    f.ano_eleicao,
    f.turno,
    f.situacao_candidatura,
    f.situacao_totalizacao
FROM fato_candidatura f
JOIN dim_candidato c ON f.sk_candidato = c.sk_candidato
JOIN dim_cargo cg ON f.sk_cargo = cg.sk_cargo
JOIN dim_estado e ON f.sk_estado = e.sk_estado
JOIN dim_partido p ON f.sk_partido = p.sk_partido
"""


def carregar_candidatos_df(caminho_db: Path) -> pd.DataFrame:
    """Lê a camada gold e devolve um DataFrame no formato usado pelo dashboard."""
    if not caminho_db.exists():
        raise FileNotFoundError(
            f"Banco não encontrado em {caminho_db}. Rode o pipeline (extract -> "
            "transform -> load) primeiro."
        )

    conexao = sqlite3.connect(caminho_db)
    try:
        df = pd.read_sql_query(QUERY_CANDIDATOS, conexao)
    finally:
        conexao.close()

    df["idade"] = _calcular_idade(df)
    return df


def _calcular_idade(df: pd.DataFrame) -> pd.Series:
    """Idade aproximada = ano da eleição - ano de nascimento (formato TSE dd/mm/yyyy)."""
    ano_nascimento = pd.to_datetime(
        df["dt_nascimento"], format="%d/%m/%Y", errors="coerce"
    ).dt.year
    ano_eleicao = pd.to_numeric(df["ano_eleicao"], errors="coerce")
    return ano_eleicao - ano_nascimento
