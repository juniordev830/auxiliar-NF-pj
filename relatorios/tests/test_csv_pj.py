from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gerar_relatorio import carregar_dados, montar_html


def test_csv_pj_generates_summary_and_escapes_category(tmp_path):
    csv = tmp_path / "pj.csv"
    csv.write_text(
        "Data;Categoria;Valor;Tipo;Descricao;Status;Contraparte;Vencimento;Pagamento\n"
        '2026-11-01;"RECEITA / Serviços";100.00;RECEITA;Trabalho;PAGO;Cliente;;\n'
        '2026-11-02;"DESPESA / <script>alert(1)</script>";30.00;DESPESA;Software;PAGO;Fornecedor;;\n',
        encoding="utf-8"
    )
    df = carregar_dados(str(csv), 0)
    assert len(df) == 2
    html = montar_html(df, {}, origem=str(csv))
    assert "Receitas previstas" in html
    assert "Despesas previstas" in html
    assert "Saldo previsto" in html
    assert "70.00" in html
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_csv_pj_rejects_missing_columns(tmp_path):
    csv = tmp_path / "invalido.csv"
    csv.write_text("Data;Tipo\n2026-11-01;RECEITA\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Colunas obrigatórias ausentes"):
        carregar_dados(str(csv), 0)
