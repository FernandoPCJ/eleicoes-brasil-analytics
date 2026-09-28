# Power BI — Quem quer governar o Brasil?

Relatório-apresentação sobre o perfil das **20.985 candidaturas às Eleições Gerais de 2026**, construído sobre o modelo estrela deste repositório (dados abertos do TSE).

O projeto está no formato **Power BI Project (.pbip)**: modelo semântico em TMDL e relatório em PBIR, tudo em texto — dá para versionar, revisar em pull request e ver o diff de cada medida DAX no GitHub.

## Como abrir

1. Tenha o **Power BI Desktop** atualizado (a partir da versão de novembro/2025).
2. Coloque esta pasta `powerbi/` na raiz do repositório clonado. O caminho padrão esperado é
   `C:\Users\Fernando\eleicoes-brasil-analytics\powerbi\dados\`.
3. Abra `EleicoesBrasil.pbip`.
4. Se o repositório estiver em outro lugar: **Página Inicial → Transformar dados → Editar parâmetros → PastaDados** e informe a pasta `dados` (terminando em `\`).
   Também funciona com URL: `https://raw.githubusercontent.com/FernandoPCJ/eleicoes-brasil-analytics/main/powerbi/dados/`
5. Clique em **Atualizar**. Salve com Ctrl+S — o Desktop grava as alterações de volta nos arquivos de texto.

Para apresentar: **Exibir → Modo de exibição de leitura** (ou publique no serviço e use o modo apresentação/tela cheia). Cada página é um slide 16:9.

## Regerar os dados

```bash
python -m src.load.export_powerbi
```

Lê `data/processed/candidatos_2026.csv` e grava os CSVs do modelo estrela em `powerbi/dados/`.

## Estrutura

```
powerbi/
├── EleicoesBrasil.pbip                 ← abra este
├── dados/                              ← CSVs do modelo estrela (gerados pelo pipeline)
├── EleicoesBrasil.SemanticModel/
│   └── definition/
│       ├── expressions.tmdl            ← parâmetro PastaDados + função CarregarCSV
│       ├── relationships.tmdl          ← 4 relacionamentos 1:N (dimensão → fato)
│       └── tables/*.tmdl               ← tabelas, colunas e medidas DAX
└── EleicoesBrasil.Report/
    ├── definition/pages/               ← 10 páginas (slides), um JSON por visual
    └── StaticResources/                ← tema e fundos dos slides
```

## Modelo

| Tabela | Grão / conteúdo |
|---|---|
| `fato_candidatura` | uma candidatura (candidato × cargo × UF × partido) + medidas |
| `dim_candidato` | gênero, raça/cor, escolaridade, estado civil, idade na data do 1º turno, faixa etária |
| `dim_cargo` | cargo, ordem lógica, poder (Executivo/Legislativo) |
| `dim_estado` | UF, nome, região |
| `dim_partido` | sigla e nome |

### Medidas principais

| Medida | DAX |
|---|---|
| Candidaturas | `COUNTROWS(fato_candidatura)` |
| % Mulheres | `DIVIDE([Candidaturas Femininas], [Candidaturas])` |
| % Pessoas Negras | pretas + pardas ÷ total |
| % Mulheres Negras | mulheres pretas e pardas ÷ total |
| Sub-representação Negra (p.p.) | 55,5% da população (Censo 2022) − % de candidaturas negras |
| Idade Média | `AVERAGEX(fato_candidatura, RELATED(dim_candidato[idade]))` |
| Status Cota 30% | texto que indica se a seleção está acima da cota mínima de gênero |

`Idade Média` usa `AVERAGEX` + `RELATED` porque o filtro vai da dimensão para a fato: fazer a média direto em `dim_candidato` ignoraria os filtros de cargo, UF e partido.

## Roteiro da apresentação

1. **Capa** — números-chave
2. **Da fonte ao painel** — pipeline e decisões de modelagem
3. **Panorama** — 98% das candidaturas estão no Legislativo
4. **Gênero** — 35,1% de mulheres no total, 14,3% entre presidenciáveis; mais presentes nas vices
5. **Raça/cor** — 48,4% de pessoas negras, contra 55,5% da população
6. **Escolaridade e idade** — 58,7% com superior completo; idade média de 49 anos
7. **Partidos** — diversidade por partido (dispersão % mulheres × % pessoas negras)
8. **Estados** — indicadores por UF
9. **Conclusões** e próximos passos
10. **Explore os dados** — painel com filtros por UF, cargo, partido, gênero e raça/cor

> Observação: os dados refletem os registros de candidatura publicados pelo TSE no momento da extração. A situação de deferimento ainda não constava na base (`#NE`), então os números representam candidaturas registradas, não aptas.
