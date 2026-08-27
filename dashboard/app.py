import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import chi2_contingency

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
# PERFIL DEMOGRÁFICO
# ============================================================

st.divider()

st.header("Perfil demográfico")

st.write(
    "Análise das principais características demográficas das "
    "candidaturas, considerando gênero, cor/raça, escolaridade e idade."
)


# ============================================================
# GÊNERO × COR/RAÇA
# ============================================================

st.subheader("Gênero por cor/raça")

genero_cor_raca = (
    df_filtrado
    .groupby(["cor_raca", "genero"])
    .size()
    .reset_index(name="Candidaturas")
)

genero_cor_raca["genero"] = genero_cor_raca["genero"].replace({
    "FEMININO": "Feminino",
    "MASCULINO": "Masculino"
})

genero_cor_raca["cor_raca"] = genero_cor_raca["cor_raca"].replace({
    "BRANCA": "Branca",
    "PARDA": "Parda",
    "PRETA": "Preta",
    "INDÍGENA": "Indígena",
    "AMARELA": "Amarela"
})


fig_genero_cor_raca = px.bar(
    genero_cor_raca,
    x="cor_raca",
    y="Candidaturas",
    color="genero",
    barmode="group",
    text="Candidaturas"
)

fig_genero_cor_raca.update_traces(
    texttemplate="%{text:,}",
    textposition="outside"
)

fig_genero_cor_raca.update_layout(
    xaxis_title="Cor/Raça",
    yaxis_title="Número de candidaturas",
    legend_title="Gênero"
)

st.plotly_chart(
    fig_genero_cor_raca,
    use_container_width=True
)


# ============================================================
# GÊNERO × ESCOLARIDADE
# ============================================================

st.subheader("Gênero por escolaridade")

genero_escolaridade = (
    df_filtrado
    .groupby(["escolaridade", "genero"])
    .size()
    .reset_index(name="Candidaturas")
)

genero_escolaridade["genero"] = genero_escolaridade["genero"].replace({
    "FEMININO": "Feminino",
    "MASCULINO": "Masculino"
})


fig_genero_escolaridade = px.bar(
    genero_escolaridade,
    x="escolaridade",
    y="Candidaturas",
    color="genero",
    barmode="group",
    text="Candidaturas"
)

fig_genero_escolaridade.update_traces(
    texttemplate="%{text:,}",
    textposition="outside"
)

fig_genero_escolaridade.update_layout(
    xaxis_title="Escolaridade",
    yaxis_title="Número de candidaturas",
    legend_title="Gênero",
    xaxis_tickangle=-35
)

st.plotly_chart(
    fig_genero_escolaridade,
    use_container_width=True
)


# ============================================================
# DISTRIBUIÇÃO DE IDADE
# ============================================================

st.subheader("Distribuição de idade")

if "idade" in df_filtrado.columns:

    idade = (
        pd.to_numeric(
            df_filtrado["idade"],
            errors="coerce"
        )
        .dropna()
    )

    if not idade.empty:

        fig_idade = px.histogram(
            idade,
            x=idade,
            nbins=20,
            labels={
                "value": "Idade",
                "count": "Número de candidaturas"
            }
        )

        fig_idade.update_layout(
            xaxis_title="Idade",
            yaxis_title="Número de candidaturas"
        )

        st.plotly_chart(
            fig_idade,
            use_container_width=True
        )

    else:

        st.info(
            "Não há dados de idade disponíveis para os filtros selecionados."
        )

else:

    st.info(
        "A variável de idade não está disponível no dataset utilizado pelo dashboard."
    )


# ============================================================
# IDADE × GÊNERO
# ============================================================

st.subheader("Distribuição de idade por gênero")

if "idade" in df_filtrado.columns:

    idade_genero = df_filtrado[
        ["idade", "genero"]
    ].copy()

    idade_genero["idade"] = pd.to_numeric(
        idade_genero["idade"],
        errors="coerce"
    )

    idade_genero = idade_genero.dropna(
        subset=["idade"]
    )

    idade_genero["genero"] = idade_genero["genero"].replace({
        "FEMININO": "Feminino",
        "MASCULINO": "Masculino"
    })

    if not idade_genero.empty:

        fig_idade_genero = px.box(
            idade_genero,
            x="genero",
            y="idade",
            color="genero",
            points="outliers"
        )

        fig_idade_genero.update_layout(
            xaxis_title="Gênero",
            yaxis_title="Idade",
            showlegend=False
        )

        st.plotly_chart(
            fig_idade_genero,
            use_container_width=True
        )

    else:

        st.info(
            "Não há dados de idade disponíveis para os filtros selecionados."
        )

else:

    st.info(
        "A variável de idade não está disponível no dataset utilizado pelo dashboard."
    )
    
    # ============================================================
# PARTE 4 - PERFIL ELEITORAL POR CARGO
# ============================================================

st.divider()

st.header("Perfil eleitoral por cargo")

st.write(
    "Análise da composição das candidaturas segundo os cargos disputados, "
    "considerando gênero e idade."
)


# ============================================================
# GÊNERO POR CARGO
# ============================================================

st.subheader("Gênero por cargo")

genero_cargo = (
    df_filtrado
    .groupby(["cargo", "genero"])
    .size()
    .reset_index(name="Candidaturas")
)

genero_cargo["genero"] = genero_cargo["genero"].replace({
    "FEMININO": "Feminino",
    "MASCULINO": "Masculino"
})

fig_genero_cargo = px.bar(
    genero_cargo,
    x="cargo",
    y="Candidaturas",
    color="genero",
    barmode="group",
    text="Candidaturas",
    labels={
        "cargo": "Cargo",
        "Candidaturas": "Número de candidaturas",
        "genero": "Gênero"
    }
)

fig_genero_cargo.update_traces(
    texttemplate="%{text:,}",
    textposition="outside"
)

fig_genero_cargo.update_layout(
    xaxis_title="Cargo",
    yaxis_title="Número de candidaturas",
    legend_title="Gênero"
)

st.plotly_chart(
    fig_genero_cargo,
    use_container_width=True
)


# ============================================================
# PARTICIPAÇÃO FEMININA POR CARGO
# ============================================================

st.subheader("Participação feminina por cargo")

participacao_feminina = (
    df_filtrado
    .groupby("cargo")
    .agg(
        total=("genero", "size"),
        mulheres=("genero", lambda x: (x == "FEMININO").sum())
    )
    .reset_index()
)

participacao_feminina["participacao_feminina"] = (
    participacao_feminina["mulheres"]
    / participacao_feminina["total"]
    * 100
)

participacao_feminina = (
    participacao_feminina
    .sort_values("participacao_feminina", ascending=True)
)

fig_participacao_feminina = px.bar(
    participacao_feminina,
    x="participacao_feminina",
    y="cargo",
    orientation="h",
    text="participacao_feminina",
    labels={
        "cargo": "Cargo",
        "participacao_feminina": "Participação feminina (%)"
    }
)

fig_participacao_feminina.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

fig_participacao_feminina.update_layout(
    xaxis_title="Participação feminina (%)",
    yaxis_title="Cargo",
    showlegend=False
)

st.plotly_chart(
    fig_participacao_feminina,
    use_container_width=True
)


# ============================================================
# IDADE MÉDIA POR CARGO E GÊNERO
# ============================================================

st.subheader("Idade média por cargo e gênero")

idade_cargo_genero = (
    df_filtrado
    .dropna(subset=["idade"])
    .groupby(["cargo", "genero"])["idade"]
    .mean()
    .reset_index()
)

idade_cargo_genero["genero"] = idade_cargo_genero["genero"].replace({
    "FEMININO": "Feminino",
    "MASCULINO": "Masculino"
})

fig_idade_cargo_genero = px.bar(
    idade_cargo_genero,
    x="cargo",
    y="idade",
    color="genero",
    barmode="group",
    text="idade",
    labels={
        "cargo": "Cargo",
        "idade": "Idade média (anos)",
        "genero": "Gênero"
    }
)

fig_idade_cargo_genero.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside"
)

fig_idade_cargo_genero.update_layout(
    xaxis_title="Cargo",
    yaxis_title="Idade média (anos)",
    legend_title="Gênero"
)

st.plotly_chart(
    fig_idade_cargo_genero,
    use_container_width=True
)


# ============================================================
# DISTRIBUIÇÃO DE IDADE POR CARGO
# ============================================================

st.subheader("Distribuição de idade por cargo")

idade_cargo = df_filtrado.dropna(
    subset=["idade", "cargo"]
)

fig_idade_cargo = px.box(
    idade_cargo,
    x="cargo",
    y="idade",
    points="outliers",
    labels={
        "cargo": "Cargo",
        "idade": "Idade"
    }
)

fig_idade_cargo.update_layout(
    xaxis_title="Cargo",
    yaxis_title="Idade (anos)",
    showlegend=False
)

st.plotly_chart(
    fig_idade_cargo,
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
# PARTE 5 - ANÁLISES ESTATÍSTICAS
# ============================================================

from scipy.stats import chi2_contingency


st.divider()

st.header("Análises estatísticas")

st.write(
    "Análise estatística das candidaturas, considerando associações "
    "entre características demográficas e diferenças de idade."
)


# ============================================================
# 5.1 ASSOCIAÇÃO ENTRE GÊNERO E ESCOLARIDADE
# ============================================================

st.subheader("Associação entre gênero e escolaridade")

tabela_genero_escolaridade = pd.crosstab(
    df_filtrado["escolaridade"],
    df_filtrado["genero"]
)

if (
    tabela_genero_escolaridade.shape[0] >= 2
    and tabela_genero_escolaridade.shape[1] >= 2
):

    qui2, p_valor, graus_liberdade, frequencias_esperadas = (
        chi2_contingency(tabela_genero_escolaridade)
    )

    n = tabela_genero_escolaridade.to_numpy().sum()

    menor_dimensao = min(
        tabela_genero_escolaridade.shape[0] - 1,
        tabela_genero_escolaridade.shape[1] - 1
    )

    v_cramer = (
        (qui2 / (n * menor_dimensao)) ** 0.5
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Qui-quadrado",
            f"{qui2:.2f}"
        )

    with col2:
        st.metric(
            "p-valor",
            f"{p_valor:.4f}"
        )

    with col3:
        st.metric(
            "V de Cramér",
            f"{v_cramer:.4f}"
        )

    if p_valor < 0.05:
        st.success(
            "Foi identificada associação estatisticamente significativa "
            "entre gênero e escolaridade (p < 0,05)."
        )
    else:
        st.info(
            "Não foi identificada associação estatisticamente significativa "
            "entre gênero e escolaridade (p ≥ 0,05)."
        )

    if v_cramer < 0.10:
        interpretacao_v = "baixa"
    elif v_cramer < 0.30:
        interpretacao_v = "moderada"
    else:
        interpretacao_v = "elevada"

    st.caption(
        f"O V de Cramér indica uma magnitude {interpretacao_v} "
        "da associação entre as variáveis."
    )

    st.markdown("**Tabela de contingência**")

    tabela_exibicao = tabela_genero_escolaridade.copy()

    tabela_exibicao = tabela_exibicao.rename(
        columns={
            "FEMININO": "Feminino",
            "MASCULINO": "Masculino"
        }
    )

    st.dataframe(
        tabela_exibicao,
        use_container_width=True
    )

else:

    st.warning(
        "Não há dados suficientes nos filtros selecionados "
        "para realizar o teste de associação."
    )


# ============================================================
# 5.2 RESÍDUOS PADRONIZADOS
# ============================================================

st.subheader("Resíduos padronizados")

if (
    tabela_genero_escolaridade.shape[0] >= 2
    and tabela_genero_escolaridade.shape[1] >= 2
):

    observados = tabela_genero_escolaridade.to_numpy()

    total = observados.sum()

    totais_linhas = observados.sum(axis=1)

    totais_colunas = observados.sum(axis=0)

    esperados = np.outer(
        totais_linhas,
        totais_colunas
    ) / total

    residuos = (
        observados - esperados
    ) / np.sqrt(esperados)

    residuos_df = pd.DataFrame(
        residuos,
        index=tabela_genero_escolaridade.index,
        columns=tabela_genero_escolaridade.columns
    )

    residuos_df = residuos_df.rename(
        columns={
            "FEMININO": "Feminino",
            "MASCULINO": "Masculino"
        }
    )

    fig_residuos = px.imshow(
        residuos_df,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r",
        labels={
            "x": "Gênero",
            "y": "Escolaridade",
            "color": "Resíduo padronizado"
        }
    )

    fig_residuos.update_layout(
        xaxis_title="Gênero",
        yaxis_title="Escolaridade",
        coloraxis_colorbar_title="Resíduo"
    )

    st.plotly_chart(
        fig_residuos,
        use_container_width=True
    )

    st.caption(
        "Valores positivos indicam frequência observada acima do esperado, "
        "enquanto valores negativos indicam frequência abaixo do esperado. "
        "Valores com maior magnitude representam maiores desvios em relação "
        "ao modelo de independência."
    )

    residuos_exibicao = (
        residuos_df
        .stack()
        .reset_index()
    )

    residuos_exibicao.columns = [
        "Escolaridade",
        "Gênero",
        "Resíduo padronizado"
    ]

    residuos_exibicao["Resíduo padronizado"] = (
        residuos_exibicao["Resíduo padronizado"]
        .round(2)
    )

    residuos_exibicao = (
        residuos_exibicao
        .sort_values(
            "Resíduo padronizado",
            key=lambda x: x.abs(),
            ascending=False
        )
    )

    st.markdown(
        "**Maiores desvios em relação ao esperado**"
    )

    st.dataframe(
        residuos_exibicao.head(5),
        use_container_width=True
    )


# ============================================================
# 5.3 DIFERENÇA DE IDADE ENTRE GÊNEROS
# ============================================================

st.subheader("Diferença de idade média entre gêneros")

idade_genero = (
    df_filtrado
    .dropna(subset=["idade", "genero"])
    .groupby("genero")["idade"]
    .agg(
        média="mean",
        mediana="median",
        desvio_padrao="std",
        mínimo="min",
        máximo="max",
        quantidade="count"
    )
    .reset_index()
)

idade_genero["genero"] = idade_genero["genero"].replace({
    "FEMININO": "Feminino",
    "MASCULINO": "Masculino"
})

if len(idade_genero) >= 2:

    media_feminina = (
        idade_genero.loc[
            idade_genero["genero"] == "Feminino",
            "média"
        ].iloc[0]
    )

    media_masculina = (
        idade_genero.loc[
            idade_genero["genero"] == "Masculino",
            "média"
        ].iloc[0]
    )

    diferenca_idade = (
        media_masculina - media_feminina
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Idade média feminina",
            f"{media_feminina:.2f} anos"
        )

    with col2:
        st.metric(
            "Idade média masculina",
            f"{media_masculina:.2f} anos"
        )

    with col3:
        st.metric(
            "Diferença média",
            f"{diferenca_idade:.2f} anos"
        )

    idade_grafico = idade_genero.copy()

    fig_idade_genero = px.bar(
        idade_grafico,
        x="genero",
        y="média",
        text="média",
        labels={
            "genero": "Gênero",
            "média": "Idade média (anos)"
        }
    )

    fig_idade_genero.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_idade_genero.update_layout(
        xaxis_title="Gênero",
        yaxis_title="Idade média (anos)",
        showlegend=False
    )

    st.plotly_chart(
        fig_idade_genero,
        use_container_width=True
    )


# ============================================================
# 5.4 DIFERENÇA DE IDADE POR CARGO
# ============================================================

st.subheader(
    "Diferença de idade média entre gêneros por cargo"
)

idade_cargo_genero = (
    df_filtrado
    .dropna(subset=["idade", "genero", "cargo"])
    .groupby(
        ["cargo", "genero"]
    )["idade"]
    .mean()
    .reset_index()
)

idade_cargo_pivot = (
    idade_cargo_genero
    .pivot(
        index="cargo",
        columns="genero",
        values="idade"
    )
)

if (
    "FEMININO" in idade_cargo_pivot.columns
    and "MASCULINO" in idade_cargo_pivot.columns
):

    idade_cargo_pivot["diferença_idade"] = (
        idade_cargo_pivot["MASCULINO"]
        - idade_cargo_pivot["FEMININO"]
    )

    idade_cargo_pivot = (
        idade_cargo_pivot
        .dropna(subset=["diferença_idade"])
        .sort_values(
            "diferença_idade",
            ascending=False
        )
    )

    idade_cargo_grafico = (
        idade_cargo_pivot
        .reset_index()
    )

    fig_diferenca_cargo = px.bar(
        idade_cargo_grafico,
        x="diferença_idade",
        y="cargo",
        orientation="h",
        text="diferença_idade",
        labels={
            "cargo": "Cargo",
            "diferença_idade": (
                "Diferença de idade média (anos)"
            )
        }
    )

    fig_diferenca_cargo.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_diferenca_cargo.update_layout(
        xaxis_title="Diferença de idade média (anos)",
        yaxis_title="Cargo",
        showlegend=False
    )

    st.plotly_chart(
        fig_diferenca_cargo,
        use_container_width=True
    )

    st.caption(
        "Valores positivos indicam idade média masculina superior à "
        "feminina. Valores negativos indicam idade média feminina "
        "superior à masculina."
    )


# ============================================================
# 5.5 RESUMO ESTATÍSTICO DA IDADE
# ============================================================

st.subheader("Resumo estatístico da idade")

resumo_idade = (
    df_filtrado["idade"]
    .dropna()
    .agg([
        "count",
        "mean",
        "median",
        "std",
        "min",
        "max"
    ])
)

resumo_idade.index = [
    "Quantidade",
    "Média",
    "Mediana",
    "Desvio padrão",
    "Mínimo",
    "Máximo"
]

resumo_idade = resumo_idade.to_frame(
    name="Valor"
)

resumo_idade.loc[
    ["Média", "Mediana", "Desvio padrão",
     "Mínimo", "Máximo"],
    "Valor"
] = resumo_idade.loc[
    ["Média", "Mediana", "Desvio padrão",
     "Mínimo", "Máximo"],
    "Valor"
].round(2)

st.dataframe(
    resumo_idade,
    use_container_width=True
)

# ============================================================
# PARTE 6 - INSIGHTS ELEITORAIS
# ============================================================

st.divider()

st.header("Insights eleitorais")

st.write(
    "Síntese dos principais padrões identificados nas candidaturas "
    "a partir dos dados demográficos e eleitorais."
)


# ============================================================
# PREPARAÇÃO DOS DADOS
# ============================================================

# Dados atualmente filtrados
df_insights = df_filtrado.copy()

# Dados para análises que precisam comparar os gêneros.
# O filtro de gênero é removido para que indicadores como
# participação feminina por cargo continuem estatisticamente
# interpretáveis mesmo quando o usuário seleciona um gênero.
df_genero = df.copy()

# Aplicar somente os filtros diferentes de gênero
if filtro_cargo != "Todos":
    df_genero = df_genero[
        df_genero["cargo"] == filtro_cargo
    ]

if filtro_cor_raca != "Todos":
    df_genero = df_genero[
        df_genero["cor_raca"] == filtro_cor_raca
    ]

if filtro_escolaridade != "Todos":
    df_genero = df_genero[
        df_genero["escolaridade"] == filtro_escolaridade
    ]


# Garantir que idade seja numérica
if "idade" in df_insights.columns:
    df_insights["idade"] = pd.to_numeric(
        df_insights["idade"],
        errors="coerce"
    )

if "idade" in df_genero.columns:
    df_genero["idade"] = pd.to_numeric(
        df_genero["idade"],
        errors="coerce"
    )


# ============================================================
# INDICADORES DOS INSIGHTS
# ============================================================

# ------------------------------------------------------------
# Cargo com maior número de candidaturas
# ------------------------------------------------------------

cargo_contagem = (
    df_insights["cargo"]
    .value_counts()
)

cargo_principal = cargo_contagem.idxmax()

quantidade_cargo_principal = (
    cargo_contagem.max()
)

percentual_cargo_principal = (
    quantidade_cargo_principal /
    len(df_insights)
) * 100


# ------------------------------------------------------------
# Idade média
# ------------------------------------------------------------

idade_media = df_insights["idade"].mean()


# ------------------------------------------------------------
# Cor/raça predominante
# ------------------------------------------------------------

cor_raca_contagem = (
    df_insights["cor_raca"]
    .value_counts()
)

cor_raca_principal = (
    cor_raca_contagem.idxmax()
)

quantidade_cor_raca_principal = (
    cor_raca_contagem.max()
)

percentual_cor_raca_principal = (
    quantidade_cor_raca_principal /
    len(df_insights)
) * 100


# ------------------------------------------------------------
# Escolaridade predominante
# ------------------------------------------------------------

escolaridade_contagem = (
    df_insights["escolaridade"]
    .value_counts()
)

escolaridade_principal = (
    escolaridade_contagem.idxmax()
)

quantidade_escolaridade_principal = (
    escolaridade_contagem.max()
)

percentual_escolaridade_principal = (
    quantidade_escolaridade_principal /
    len(df_insights)
) * 100


# ============================================================
# CARDS DE INSIGHTS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


# ------------------------------------------------------------
# Card 1 - Cargo principal
# ------------------------------------------------------------

with col1:

    st.metric(
        "Cargo com maior concentração",
        cargo_principal
    )

    st.caption(
        f"{quantidade_cargo_principal:,} candidaturas "
        f"({percentual_cargo_principal:.1f}%)"
        .replace(",", ".")
    )


# ------------------------------------------------------------
# Card 2 - Idade média
# ------------------------------------------------------------

with col2:

    if pd.notna(idade_media):

        st.metric(
            "Idade média",
            f"{idade_media:.2f} anos"
        )

    else:

        st.metric(
            "Idade média",
            "N/D"
        )

    st.caption(
        "Média de idade das candidaturas analisadas."
    )


# ------------------------------------------------------------
# Card 3 - Cor/raça predominante
# ------------------------------------------------------------

with col3:

    st.metric(
        "Cor/raça predominante",
        cor_raca_principal
    )

    st.caption(
        f"{quantidade_cor_raca_principal:,} candidaturas "
        f"({percentual_cor_raca_principal:.1f}%)"
        .replace(",", ".")
    )


# ------------------------------------------------------------
# Card 4 - Escolaridade predominante
# ------------------------------------------------------------

with col4:

    st.metric(
        "Escolaridade predominante",
        escolaridade_principal
    )

    st.caption(
        f"{quantidade_escolaridade_principal:,} candidaturas "
        f"({percentual_escolaridade_principal:.1f}%)"
        .replace(",", ".")
    )


# ============================================================
# PARTICIPAÇÃO FEMININA POR CARGO
# ============================================================

st.subheader("Participação feminina por cargo")

# A análise utiliza df_genero, e não df_insights.
# Dessa forma, o filtro de gênero não altera o denominador.
tabela_genero_cargo = pd.crosstab(
    df_genero["cargo"],
    df_genero["genero"]
)


if "FEMININO" in tabela_genero_cargo.columns:

    # Total de candidaturas por cargo
    tabela_genero_cargo["Total"] = (
        tabela_genero_cargo.sum(axis=1)
    )

    # Participação feminina
    tabela_genero_cargo["Participação feminina (%)"] = (
        tabela_genero_cargo["FEMININO"]
        .div(tabela_genero_cargo["Total"])
        .mul(100)
        .round(2)
    )

    participacao_feminina = (
        tabela_genero_cargo[
            ["Participação feminina (%)"]
        ]
        .sort_values(
            "Participação feminina (%)",
            ascending=True
        )
        .reset_index()
    )

    # Renomear coluna
    participacao_feminina = (
        participacao_feminina
        .rename(
            columns={
                "cargo": "Cargo"
            }
        )
    )

    fig_feminina = px.bar(
        participacao_feminina,
        x="Participação feminina (%)",
        y="Cargo",
        orientation="h",
        text="Participação feminina (%)"
    )

    fig_feminina.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig_feminina.update_layout(
        xaxis_title="Participação feminina (%)",
        yaxis_title="Cargo",
        showlegend=False
    )

    st.plotly_chart(
        fig_feminina,
        use_container_width=True
    )

else:

    st.info(
        "Não há dados suficientes para calcular a participação feminina."
    )


# ============================================================
# IDADE MÉDIA DAS CANDIDATURAS POR CARGO
# ============================================================

st.subheader("Idade média das candidaturas por cargo")

idade_cargo = (
    df_insights
    .groupby("cargo", as_index=False)["idade"]
    .mean()
    .rename(
        columns={
            "idade": "Idade média",
            "cargo": "Cargo"
        }
    )
    .dropna(subset=["Idade média"])
    .sort_values(
        "Idade média",
        ascending=True
    )
)


if not idade_cargo.empty:

    fig_idade_cargo = px.bar(
        idade_cargo,
        x="Idade média",
        y="Cargo",
        orientation="h",
        text="Idade média"
    )

    fig_idade_cargo.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_idade_cargo.update_layout(
        xaxis_title="Idade média (anos)",
        yaxis_title="Cargo",
        showlegend=False
    )

    st.plotly_chart(
        fig_idade_cargo,
        use_container_width=True
    )

else:

    st.info(
        "Não há dados de idade suficientes para calcular "
        "a média por cargo."
    )


# ============================================================
# RESUMO TEXTUAL
# ============================================================

st.subheader("Principais observações")


# ============================================================
# PARTICIPAÇÃO FEMININA GERAL
# ============================================================

# Também utilizamos df_genero aqui para que o indicador
# continue representando a composição de gênero do recorte
# independentemente do filtro de gênero.

total_feminino_insight = (
    df_genero["genero"]
    .eq("FEMININO")
    .sum()
)

total_masculino_insight = (
    df_genero["genero"]
    .eq("MASCULINO")
    .sum()
)

total_generos = (
    total_feminino_insight +
    total_masculino_insight
)


if total_generos > 0:

    percentual_feminino_insight = (
        total_feminino_insight /
        total_generos *
        100
    )

    percentual_masculino_insight = (
        total_masculino_insight /
        total_generos *
        100
    )

else:

    percentual_feminino_insight = 0
    percentual_masculino_insight = 0


# ============================================================
# OBSERVAÇÃO 1 - GÊNERO
# ============================================================

st.info(
    f"**Perfil de gênero:** as mulheres representam "
    f"**{percentual_feminino_insight:.2f}%** das candidaturas "
    f"analisadas, enquanto os homens representam "
    f"**{percentual_masculino_insight:.2f}%**."
)


# ============================================================
# OBSERVAÇÃO 2 - CARGO
# ============================================================

st.info(
    f"**Concentração por cargo:** o cargo de "
    f"**{cargo_principal}** concentra "
    f"**{percentual_cargo_principal:.2f}%** das candidaturas "
    f"consideradas neste recorte."
)


# ============================================================
# OBSERVAÇÃO 3 - IDADE
# ============================================================

if pd.notna(idade_media):

    st.info(
        f"**Perfil etário:** a idade média das candidaturas "
        f"analisadas é de **{idade_media:.2f} anos**."
    )

else:

    st.info(
        "**Perfil etário:** não há dados de idade suficientes "
        "para calcular a média."
    )


# ============================================================
# OBSERVAÇÃO 4 - ESCOLARIDADE
# ============================================================

st.info(
    f"**Escolaridade:** o nível "
    f"**{escolaridade_principal}** é a categoria com maior "
    f"número de candidaturas no recorte analisado, "
    f"representando **{percentual_escolaridade_principal:.2f}%** "
    f"das candidaturas."
)


# ============================================================
# RODAPÉ
# ============================================================

st.divider()

st.caption(
    "🇧🇷 Eleições Brasil Analytics • "
    "Análise das candidaturas das Eleições Gerais de 2026"
)