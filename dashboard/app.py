import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="BR Eleições Brasil Analytics",
    page_icon="🇧🇷",
    layout="wide"
)


# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

@st.cache_data
def carregar_dados():
    arquivo = "data/processed/candidatos_2026.parquet"
    df = pd.read_parquet(arquivo)
    return df


df = carregar_dados()


# ============================================================
# TÍTULO
# ============================================================

st.title("🇧🇷 Eleições Brasil Analytics")

st.subheader(
    "Análise das candidaturas das Eleições Gerais de 2026"
)

st.write(
    "Dashboard interativo para exploração do perfil das candidaturas, "
    "considerando características demográficas, eleitorais e estatísticas."
)

st.divider()


# ============================================================
# FILTROS
# ============================================================

st.sidebar.header("Filtros")

generos = [
    "Todos"
] + sorted(
    df["genero"].dropna().unique().tolist()
)

cargos = [
    "Todos"
] + sorted(
    df["cargo"].dropna().unique().tolist()
)

cores_raca = [
    "Todos"
] + sorted(
    df["cor_raca"].dropna().unique().tolist()
)

escolaridades = [
    "Todos"
] + sorted(
    df["escolaridade"].dropna().unique().tolist()
)


filtro_genero = st.sidebar.selectbox(
    "Gênero",
    generos
)

filtro_cargo = st.sidebar.selectbox(
    "Cargo",
    cargos
)

filtro_cor_raca = st.sidebar.selectbox(
    "Cor/Raça",
    cores_raca
)

filtro_escolaridade = st.sidebar.selectbox(
    "Escolaridade",
    escolaridades
)


# ============================================================
# APLICAÇÃO DOS FILTROS
# ============================================================

df_filtrado = df.copy()


if filtro_genero != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["genero"] == filtro_genero
    ]


if filtro_cargo != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["cargo"] == filtro_cargo
    ]


if filtro_cor_raca != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["cor_raca"] == filtro_cor_raca
    ]


if filtro_escolaridade != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["escolaridade"] == filtro_escolaridade
    ]


# ============================================================
# VERIFICAÇÃO DOS FILTROS
# ============================================================

if df_filtrado.empty:

    st.warning(
        "Nenhuma candidatura foi encontrada para a combinação "
        "de filtros selecionada."
    )

    st.stop()


# ============================================================
# INDICADORES PRINCIPAIS
# ============================================================

total_candidaturas = len(df_filtrado)

total_mulheres = (
    df_filtrado["genero"]
    .eq("FEMININO")
    .sum()
)

total_homens = (
    df_filtrado["genero"]
    .eq("MASCULINO")
    .sum()
)

total_cargos = df_filtrado["cargo"].nunique()


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Candidaturas",
        f"{total_candidaturas:,}".replace(",", ".")
    )


with col2:

    st.metric(
        "Mulheres",
        f"{total_mulheres:,}".replace(",", ".")
    )


with col3:

    st.metric(
        "Homens",
        f"{total_homens:,}".replace(",", ".")
    )


with col4:

    st.metric(
        "Cargos",
        total_cargos
    )


st.divider()


# ============================================================
# VISÃO GERAL
# ============================================================

st.header("Visão geral das candidaturas")


# ============================================================
# DISTRIBUIÇÃO POR GÊNERO
# ============================================================

col1, col2 = st.columns(2)


with col1:

    st.subheader("Distribuição por gênero")

    genero = (
        df_filtrado["genero"]
        .value_counts()
        .rename_axis("Gênero")
        .reset_index(name="Candidaturas")
    )

    genero["Gênero"] = genero["Gênero"].replace({
        "FEMININO": "Feminino",
        "MASCULINO": "Masculino"
    })

    fig_genero = px.bar(
        genero,
        x="Gênero",
        y="Candidaturas",
        text="Candidaturas"
    )

    fig_genero.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig_genero.update_layout(
        xaxis_title="Gênero",
        yaxis_title="Número de candidaturas",
        showlegend=False
    )

    st.plotly_chart(
        fig_genero,
        use_container_width=True
    )


# ============================================================
# DISTRIBUIÇÃO POR CARGO
# ============================================================

with col2:

    st.subheader("Distribuição por cargo")

    cargo = (
        df_filtrado["cargo"]
        .value_counts()
        .sort_values(ascending=True)
        .reset_index()
    )

    cargo.columns = [
        "Cargo",
        "Candidaturas"
    ]

    fig_cargo = px.bar(
        cargo,
        x="Candidaturas",
        y="Cargo",
        orientation="h",
        text="Candidaturas"
    )

    fig_cargo.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig_cargo.update_layout(
        xaxis_title="Número de candidaturas",
        yaxis_title="Cargo",
        showlegend=False
    )

    st.plotly_chart(
        fig_cargo,
        use_container_width=True
    )


# ============================================================
# DISTRIBUIÇÃO POR COR/RAÇA
# ============================================================

col1, col2 = st.columns(2)


with col1:

    st.subheader("Distribuição por cor/raça")

    cor_raca = (
        df_filtrado["cor_raca"]
        .value_counts()
        .sort_values(ascending=True)
        .reset_index()
    )

    cor_raca.columns = [
        "Cor/Raça",
        "Candidaturas"
    ]

    fig_cor_raca = px.bar(
        cor_raca,
        x="Candidaturas",
        y="Cor/Raça",
        orientation="h",
        text="Candidaturas"
    )

    fig_cor_raca.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig_cor_raca.update_layout(
        xaxis_title="Número de candidaturas",
        yaxis_title="Cor/Raça",
        showlegend=False
    )

    st.plotly_chart(
        fig_cor_raca,
        use_container_width=True
    )


# ============================================================
# DISTRIBUIÇÃO POR ESCOLARIDADE
# ============================================================

with col2:

    st.subheader("Distribuição por escolaridade")

    escolaridade = (
        df_filtrado["escolaridade"]
        .value_counts()
        .sort_values(ascending=True)
        .reset_index()
    )

    escolaridade.columns = [
        "Escolaridade",
        "Candidaturas"
    ]

    fig_escolaridade = px.bar(
        escolaridade,
        x="Candidaturas",
        y="Escolaridade",
        orientation="h",
        text="Candidaturas"
    )

    fig_escolaridade.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig_escolaridade.update_layout(
        xaxis_title="Número de candidaturas",
        yaxis_title="Escolaridade",
        showlegend=False
    )

    st.plotly_chart(
        fig_escolaridade,
        use_container_width=True
    )


# ============================================================
# RESUMO DA DISTRIBUIÇÃO
# ============================================================

st.divider()

st.header("Resumo da distribuição")


col1, col2 = st.columns(2)


# ============================================================
# PARTICIPAÇÃO POR GÊNERO
# ============================================================

with col1:

    st.subheader("Participação percentual por gênero")

    genero_pct = (
        df_filtrado["genero"]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
    )

    genero_pct.index = genero_pct.index.map({
        "FEMININO": "Feminino",
        "MASCULINO": "Masculino"
    })

    genero_pct = genero_pct.rename(
        "Percentual (%)"
    )

    st.dataframe(
        genero_pct,
        use_container_width=True
    )


# ============================================================
# CINCO CARGOS COM MAIOR CONCENTRAÇÃO
# ============================================================

with col2:

    st.subheader(
        "Cinco cargos com maior concentração"
    )

    cargo_pct = (
        df_filtrado["cargo"]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
        .head(5)
    )

    cargo_pct = cargo_pct.rename(
        "Percentual (%)"
    )

    st.dataframe(
        cargo_pct,
        use_container_width=True
    )


# ============================================================
# RODAPÉ
# ============================================================

st.divider()

st.caption(
    "🇧🇷 Eleições Brasil Analytics • "
    "Análise das candidaturas das Eleições Gerais de 2026"
)