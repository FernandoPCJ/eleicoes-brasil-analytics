"""Exporta o modelo estrela em CSVs prontos para o Power BI (powerbi/dados/).

Lê data/processed/candidatos_<ano>.csv e gera:
    fato_candidatura.csv  (grão: uma candidatura)
    dim_candidato.csv     (+ idade na data do 1º turno, faixa etária e colunas de ordenação)
    dim_cargo.csv         (+ ordem lógica dos cargos e poder: Executivo/Legislativo)
    dim_estado.csv        (+ nome do estado e região)
    dim_partido.csv

O projeto Power BI (powerbi/EleicoesBrasil.pbip) lê esses arquivos pelo parâmetro PastaDados.

Uso:
    python -m src.load.export_powerbi
"""
import logging

import pandas as pd

from src.extract.config_tse import ANO_ELEICAO, BASE_DIR, PROCESSED_DATA_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

POWERBI_DATA_DIR = BASE_DIR / "powerbi" / "dados"
DATA_PRIMEIRO_TURNO = pd.Timestamp("2026-10-04")

FAIXAS = [(0, 29, "18-29"), (30, 39, "30-39"), (40, 49, "40-49"), (50, 59, "50-59"), (60, 69, "60-69"), (70, 200, "70+")]

REGIOES = {
    "Norte": "AC AP AM PA RO RR TO",
    "Nordeste": "AL BA CE MA PB PE PI RN SE",
    "Centro-Oeste": "DF GO MT MS",
    "Sudeste": "ES MG RJ SP",
    "Sul": "PR RS SC",
}
UF_REGIAO = {uf: regiao for regiao, ufs in REGIOES.items() for uf in ufs.split()}

NOMES_UF = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia", "CE": "Ceará",
    "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul", "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
    "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina", "SP": "São Paulo",
    "SE": "Sergipe", "TO": "Tocantins", "BR": "Brasil (candidaturas nacionais)",
}

ORDEM_ESCOLARIDADE = {
    "LÊ E ESCREVE": 1, "ENSINO FUNDAMENTAL INCOMPLETO": 2, "ENSINO FUNDAMENTAL COMPLETO": 3,
    "ENSINO MÉDIO INCOMPLETO": 4, "ENSINO MÉDIO COMPLETO": 5, "SUPERIOR INCOMPLETO": 6, "SUPERIOR COMPLETO": 7,
}
ORDEM_CARGO = {
    "PRESIDENTE": 1, "VICE-PRESIDENTE": 2, "GOVERNADOR": 3, "VICE-GOVERNADOR": 4, "SENADOR": 5,
    "1º SUPLENTE": 6, "2º SUPLENTE": 7, "DEPUTADO FEDERAL": 8, "DEPUTADO ESTADUAL": 9, "DEPUTADO DISTRITAL": 10,
}
EXECUTIVO = {"PRESIDENTE", "VICE-PRESIDENTE", "GOVERNADOR", "VICE-GOVERNADOR"}


def faixa_etaria(idade) -> str:
    if pd.isna(idade):
        return "NÃO INFORMADA"
    for ini, fim, rotulo in FAIXAS:
        if ini <= idade <= fim:
            return rotulo
    return "NÃO INFORMADA"


def exportar() -> None:
    origem = PROCESSED_DATA_DIR / f"candidatos_{ANO_ELEICAO}.csv"
    df = pd.read_csv(origem, dtype={"sq_candidato": str, "nr_candidato": str})
    logger.info("Lidas %d candidaturas de %s", len(df), origem)

    nasc = pd.to_datetime(df["dt_nascimento"], format="%d/%m/%Y", errors="coerce")
    df["idade"] = ((DATA_PRIMEIRO_TURNO - nasc).dt.days // 365.2425).astype("Int64")
    df["faixa_etaria"] = df["idade"].map(faixa_etaria)

    # --- dimensões ---
    dim_candidato = (
        df[["sq_candidato", "nr_candidato", "nm_candidato", "nm_urna_candidato", "genero", "cor_raca",
            "escolaridade", "estado_civil", "dt_nascimento", "idade", "faixa_etaria"]]
        .drop_duplicates("sq_candidato").reset_index(drop=True)
    )
    dim_candidato.insert(0, "sk_candidato", dim_candidato.index + 1)
    dim_candidato["ordem_escolaridade"] = dim_candidato["escolaridade"].map(ORDEM_ESCOLARIDADE).fillna(99).astype(int)
    ordem_faixa = {rotulo: i + 1 for i, (_, _, rotulo) in enumerate(FAIXAS)}
    dim_candidato["ordem_faixa_etaria"] = dim_candidato["faixa_etaria"].map(ordem_faixa).fillna(99).astype(int)
    dim_candidato["dt_nascimento"] = pd.to_datetime(
        dim_candidato["dt_nascimento"], format="%d/%m/%Y", errors="coerce").dt.strftime("%Y-%m-%d")

    dim_cargo = pd.DataFrame({"cargo": sorted(df["cargo"].unique(), key=lambda c: ORDEM_CARGO.get(c, 50))})
    dim_cargo.insert(0, "sk_cargo", dim_cargo.index + 1)
    dim_cargo["ordem_cargo"] = dim_cargo["cargo"].map(ORDEM_CARGO).fillna(50).astype(int)
    dim_cargo["poder"] = dim_cargo["cargo"].map(lambda c: "Executivo" if c in EXECUTIVO else "Legislativo")

    dim_estado = pd.DataFrame({"uf": sorted(df["uf"].unique())})
    dim_estado.insert(0, "sk_estado", dim_estado.index + 1)
    dim_estado["nome_estado"] = dim_estado["uf"].map(NOMES_UF)
    dim_estado["regiao"] = dim_estado["uf"].map(UF_REGIAO).fillna("Nacional")

    dim_partido = (
        df[["partido", "nm_partido"]].drop_duplicates("partido").sort_values("partido").reset_index(drop=True)
        .rename(columns={"partido": "sigla_partido", "nm_partido": "nome_partido"})
    )
    dim_partido.insert(0, "sk_partido", dim_partido.index + 1)

    # --- fato ---
    fato = (
        df.merge(dim_candidato[["sk_candidato", "sq_candidato"]], on="sq_candidato")
        .merge(dim_cargo[["sk_cargo", "cargo"]], on="cargo")
        .merge(dim_estado[["sk_estado", "uf"]], on="uf")
        .merge(dim_partido[["sk_partido", "sigla_partido"]], left_on="partido", right_on="sigla_partido")
    )[["sk_candidato", "sk_cargo", "sk_estado", "sk_partido", "ano_eleicao", "turno", "situacao_candidatura"]]
    fato.insert(0, "sk_candidatura", range(1, len(fato) + 1))

    if len(fato) != len(df):
        raise ValueError(f"Fato com {len(fato)} linhas, esperado {len(df)} — verifique as chaves das dimensões.")

    POWERBI_DATA_DIR.mkdir(parents=True, exist_ok=True)
    for nome, tabela in [("fato_candidatura", fato), ("dim_candidato", dim_candidato), ("dim_cargo", dim_cargo),
                         ("dim_estado", dim_estado), ("dim_partido", dim_partido)]:
        destino = POWERBI_DATA_DIR / f"{nome}.csv"
        tabela.to_csv(destino, index=False, encoding="utf-8")
        logger.info("%-18s %6d linhas -> %s", nome, len(tabela), destino.relative_to(BASE_DIR))


if __name__ == "__main__":
    exportar()
