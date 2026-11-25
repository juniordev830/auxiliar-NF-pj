from pathlib import Path
import subprocess
import sys
import pandas as pd
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
    assert "R$ 70,00" in html
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_csv_pj_rejects_missing_columns(tmp_path):
    csv = tmp_path / "invalido.csv"
    csv.write_text("Data;Tipo\n2026-11-01;RECEITA\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Colunas obrigatórias ausentes"):
        carregar_dados(str(csv), 0)


def test_csv_pj_keeps_valid_dates_with_and_without_time(tmp_path):
    csv = tmp_path / "datas.csv"
    csv.write_text(
        "Data;Categoria;Valor\n"
        "2026-11-03;Serviços;100.00\n"
        "2026-12-04 12:30:00;Serviços;200.00\n"
        "sem data;Serviços;300.00\n",
        encoding="utf-8",
    )

    dates = carregar_dados(str(csv), 0)["Data"]
    assert dates.iloc[0] == pd.Timestamp("2026-11-03")
    assert dates.iloc[1] == pd.Timestamp("2026-12-04 12:30:00")
    assert pd.isna(dates.iloc[2])


@pytest.mark.parametrize("alias", [False, True])
def test_cli_preserva_entrada_quando_saida_e_o_mesmo_arquivo(tmp_path, alias):
    csv = tmp_path / "pj.csv"
    original = b"Data;Categoria;Valor\n2026-11-01;Servicos;100.00\n"
    csv.write_bytes(original)
    output = csv
    if alias:
        output = tmp_path / "alias.html"
        output.hardlink_to(csv)

    script = Path(__file__).resolve().parents[1] / "gerar_relatorio.py"
    result = subprocess.run(
        [sys.executable, str(script), str(csv), "--saida", str(output)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 2
    assert "deve ser diferente" in result.stderr
    assert csv.read_bytes() == original
