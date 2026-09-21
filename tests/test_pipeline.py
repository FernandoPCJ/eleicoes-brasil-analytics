"""Testes de ponta a ponta do pipeline: transform -> load -> quality -> query_gold.

Usa uma amostra sintética com o mesmo layout de colunas que o TSE publica
(separador ';', encoding latin-1), para não depender de rede nem de dados
reais. Compatível com pytest e com `python -m unittest`.

Uso:
    python -m unittest discover -s tests
    (ou, com pytest instalado: pytest tests/)
"""
import csv
import io
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.load import build_star_schema
from src.load.query_gold import carregar_candidatos_df
from src.quality import checks
from src.transform import clean_candidatos

CABECALHO_BRUTO = [
    "ANO_ELEICAO", "NR_TURNO", "SG_UF", "DS_CARGO", "SQ_CANDIDATO",
    "NR_CANDIDATO", "NM_CANDIDATO", "NM_URNA_CANDIDATO", "SG_PARTIDO",
    "NM_PARTIDO", "DS_GENERO", "DS_COR_RACA", "DS_GRAU_INSTRUCAO",
    "DS_ESTADO_CIVIL", "DS_SITUACAO_CANDIDATURA", "DS_SIT_TOT_TURNO",
    "DT_NASCIMENTO",
]

LINHAS_BRUTAS = [
    ["2026", "1", "CE", "DEPUTADO FEDERAL", "100001", "1234", "FULANO DA SILVA",
     "FULANO", "PT", "PARTIDO DOS TRABALHADORES", "MASCULINO", "PARDA",
     "SUPERIOR COMPLETO", "SOLTEIRO", "DEFERIDO", "#NE#", "15/03/1980"],
    ["2026", "1", "CE", "DEPUTADO FEDERAL", "100002", "5678", "CICLANA SOUZA",
     "CICLANA", "PSDB", "PARTIDO DA SOCIAL DEMOCRACIA BRASILEIRA", "FEMININO",
     "BRANCA", "SUPERIOR COMPLETO", "CASADO", "DEFERIDO", "#NE#", "20/07/1975"],
    ["2026", "1", "SP", "GOVERNADOR", "100003", "13", "BELTRANO COSTA",
     "BELTRANO", "PT", "PARTIDO DOS TRABALHADORES", "MASCULINO", "PRETA",
     "SUPERIOR COMPLETO", "SOLTEIRO", "DEFERIDO", "#NE#", "02/01/1965"],
    # linha com dados essenciais ausentes -> deve ser descartada na limpeza
    ["2026", "1", "SP", "", "", "99", "SEM CARGO", "SEM CARGO", "PSDB",
     "PARTIDO DA SOCIAL DEMOCRACIA BRASILEIRA", "MASCULINO", "PARDA",
     "MEDIO COMPLETO", "SOLTEIRO", "INDEFERIDO", "#NE#", "#NULO#"],
]


def _escrever_csv_bruto(caminho: Path) -> None:
    with open(caminho, "w", encoding="latin-1", newline="") as f:
        escritor = csv.writer(f, delimiter=";")
        escritor.writerow(CABECALHO_BRUTO)
        escritor.writerows(LINHAS_BRUTAS)


class TestPipelineCompleto(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self._tmpdir.name)

        self.caminho_bruto = self.tmp_path / "consulta_cand_2026_BRASIL.csv"
        _escrever_csv_bruto(self.caminho_bruto)

        # Isola os módulos de I/O usando os diretórios temporários do teste
        self._processed_original = clean_candidatos.PROCESSED_DATA_DIR
        clean_candidatos.PROCESSED_DATA_DIR = self.tmp_path
        clean_candidatos.garantir_diretorios = lambda: None

    def tearDown(self):
        clean_candidatos.PROCESSED_DATA_DIR = self._processed_original
        self._tmpdir.cleanup()

    def test_limpeza_descarta_linhas_sem_campos_essenciais(self):
        linhas = clean_candidatos.limpar(self.caminho_bruto)
        self.assertEqual(len(linhas), 3)  # a 4a linha (sem cargo/sq_candidato) é descartada

    def test_limpeza_mapeia_colunas_corretamente(self):
        linhas = clean_candidatos.limpar(self.caminho_bruto)
        primeira = linhas[0]
        self.assertEqual(primeira["cargo"], "DEPUTADO FEDERAL")
        self.assertEqual(primeira["uf"], "CE")
        self.assertEqual(primeira["partido"], "PT")
        self.assertEqual(primeira["genero"], "MASCULINO")
        self.assertIsNone(primeira.get("situacao_totalizacao"))  # "#NE#" -> None

    def test_pipeline_completo_ate_o_star_schema(self):
        linhas = clean_candidatos.limpar(self.caminho_bruto)
        clean_candidatos.salvar_processed(linhas, "candidatos_teste.csv")

        caminho_db = self.tmp_path / "eleicoes_teste.db"
        build_star_schema.construir(linhas, caminho_db)

        conexao = sqlite3.connect(caminho_db)
        try:
            total_fato = conexao.execute(
                "SELECT COUNT(*) FROM fato_candidatura"
            ).fetchone()[0]
            total_candidatos = conexao.execute(
                "SELECT COUNT(*) FROM dim_candidato"
            ).fetchone()[0]
            total_partidos = conexao.execute(
                "SELECT COUNT(*) FROM dim_partido"
            ).fetchone()[0]
        finally:
            conexao.close()

        self.assertEqual(total_fato, 3)
        self.assertEqual(total_candidatos, 3)
        self.assertEqual(total_partidos, 2)  # PT e PSDB

    def test_quality_checks_passam_em_dados_limpos(self):
        linhas = clean_candidatos.limpar(self.caminho_bruto)
        caminho_db = self.tmp_path / "eleicoes_teste.db"
        build_star_schema.construir(linhas, caminho_db)

        resultados = checks.rodar_checks(caminho_db)
        falhas = [r for r in resultados if not r.ok]

        self.assertEqual(falhas, [], f"Checks falharam: {falhas}")

    def test_quality_checks_detectam_orfaos(self):
        linhas = clean_candidatos.limpar(self.caminho_bruto)
        caminho_db = self.tmp_path / "eleicoes_teste.db"
        build_star_schema.construir(linhas, caminho_db)

        # Corrompe propositalmente uma referência para simular um bug de carga
        conexao = sqlite3.connect(caminho_db)
        conexao.execute("UPDATE fato_candidatura SET sk_cargo = 9999 WHERE sk_candidatura = 1")
        conexao.commit()
        conexao.close()

        resultados = checks.rodar_checks(caminho_db)
        resultado_integridade = next(
            r for r in resultados if r.nome == "integridade_referencial"
        )
        self.assertFalse(resultado_integridade.ok)

    def test_query_gold_retorna_colunas_esperadas_pelo_dashboard(self):
        linhas = clean_candidatos.limpar(self.caminho_bruto)
        caminho_db = self.tmp_path / "eleicoes_teste.db"
        build_star_schema.construir(linhas, caminho_db)

        df = carregar_candidatos_df(caminho_db)

        for coluna in ["genero", "cargo", "cor_raca", "escolaridade", "idade"]:
            self.assertIn(coluna, df.columns)

        self.assertEqual(len(df), 3)
        # candidato nascido em 15/03/1980, eleição 2026 -> idade aproximada 46
        idade_primeiro = df.loc[df["nr_candidato"] == "1234", "idade"].iloc[0]
        self.assertEqual(idade_primeiro, 46)


if __name__ == "__main__":
    unittest.main()
