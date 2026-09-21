# Eleições Brasil Analytics 🇧🇷

Projeto de Engenharia de Dados e Business Intelligence para análise do
cenário eleitoral brasileiro, usando dados públicos do Tribunal Superior
Eleitoral (TSE).

## Arquitetura

```
TSE (dados abertos)
        │  download (requests, retry + backoff)
        ▼
   data/raw/            bronze — CSV bruto, como o TSE publica
        │  limpeza e tipagem (src/transform)
        ▼
   data/processed/      silver — CSV limpo, colunas padronizadas
        │  modelagem dimensional (src/load)
        ▼
   data/warehouse/      gold — star schema em SQLite
        │
        ├──► src/quality/checks.py   testes de qualidade de dados
        └──► dashboard/app.py         Streamlit, lê da camada gold
```

**Modelo dimensional** (grão: uma candidatura):

- `fato_candidatura` — ano, turno, situação
- `dim_candidato` — gênero, cor/raça, escolaridade, estado civil, data de nascimento
- `dim_cargo`, `dim_estado`, `dim_partido`

O warehouse usa SQLite (biblioteca padrão do Python — zero dependências
externas). O SQL é padrão e migra para Postgres com ajustes mínimos de tipo
(ver "Evoluindo para Postgres" abaixo).

Um documento detalhado de arquitetura e roadmap (fases 2–4: dbt + DuckDB,
Airflow, ingestão incremental, cruzamento com dados de doações) foi
compartilhado separadamente com o mantenedor do projeto.

## Como rodar

```bash
pip install -r requirements.txt

# 1. Extrair dados do TSE
python -m src.extract.download_tse
python -m src.extract.extract_tse

# 2. Transformar (bronze -> silver)
python -m src.transform.clean_candidatos

# 3. Carregar o star schema (silver -> gold)
python -m src.load.build_star_schema

# 4. Rodar os testes de qualidade de dados
python -m src.quality.checks

# 5. Subir o dashboard
streamlit run dashboard/app.py
```

### Se o download automático falhar (403)

O CDN do TSE fica atrás de um WAF (proteção anti-bot) que, em alguns
ambientes de rede, bloqueia clientes HTTP não-navegador mesmo com um
User-Agent de navegador — normalmente por *fingerprint* de TLS, não só
pelos headers. Se `download_tse.py` continuar retornando 403:

1. Baixe manualmente pelo navegador:
   `https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_2026.zip`
2. Extraia o zip e copie `consulta_cand_2026_BRASIL.csv` para `data/raw/`
3. Rode o pipeline a partir da etapa 2 (`clean_candidatos`) — o script de
   extração automática só é pulado, o resto do pipeline funciona igual.

O dashboard (`dashboard/app.py`) também reconstrói o star schema
automaticamente a partir do CSV processado versionado em
`data/processed/`, caso o banco `data/warehouse/eleicoes.db` não exista
ainda — por isso funciona direto em um deploy limpo (ex.: Streamlit
Community Cloud), sem precisar rodar a extração contra o TSE no ambiente
de deploy.

## Testes

```bash
python -m pytest tests/
# ou, sem pytest instalado:
python -m unittest discover -s tests
```

Os testes cobrem limpeza de dados, construção do star schema, checks de
qualidade (incluindo detecção proposital de órfãos) e a consulta que
alimenta o dashboard — tudo com uma amostra sintética que segue o layout
oficial de colunas do TSE, sem depender de rede.

## Deploy

O dashboard está publicado no Streamlit Community Cloud (gratuito):

**[LINK_DO_DEPLOY_AQUI]**

Para publicar sua própria cópia: crie uma conta em
[share.streamlit.io](https://share.streamlit.io) com seu GitHub, aponte
para este repositório (branch `main`), arquivo principal
`dashboard/app.py`. Como o dashboard reconstrói o star schema a partir do
CSV versionado em `data/processed/` (ver seção acima), nenhuma
configuração extra é necessária — o deploy funciona direto.

## Evoluindo para Postgres

A troca de SQLite por Postgres é direta: o DDL em
`src/load/build_star_schema.py` usa tipos padrão (`INTEGER`, `TEXT`), então
basta trocar `sqlite3.connect` por uma conexão `psycopg2`/`sqlalchemy` e
ajustar `AUTOINCREMENT` para `SERIAL`/`IDENTITY`. Essa migração faz parte da
Fase 2 do roadmap.

## Tecnologias

- Python (extract, transform, load, quality — biblioteca padrão: `csv`,
  `sqlite3`, `zipfile`, `requests`)
- SQLite (warehouse local / star schema)
- Streamlit + Plotly (dashboard)
- pandas, scipy (análises estatísticas)

## Etapas do projeto

- [x] Estrutura inicial do projeto
- [x] Coleta dos dados eleitorais (extração robusta, com retry)
- [x] Pipeline ETL (extract → transform → load)
- [x] Modelagem dimensional (star schema)
- [x] Testes de qualidade de dados
- [x] Dashboard consumindo a camada gold
- [ ] Orquestração (Airflow/Dagster) — Fase 3 do roadmap
- [ ] Ingestão incremental durante a apuração — Fase 3
- [ ] Deploy em nuvem com IaC (Terraform) — Fase 4

## Fonte dos dados

Dados públicos disponibilizados pelo [Tribunal Superior Eleitoral (TSE)](https://dadosabertos.tse.jus.br/).
