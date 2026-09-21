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
