from pathlib import Path
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gerar_relatorio import carregar_dados, montar_html, centavos, moeda

def test_exact_centavos_and_brazilian_format(tmp_path):
    source = tmp_path / "exato.csv"
    source.write_text("Data;Categoria;Valor;Tipo\n2026-11-01;A;0.10;RECEITA\n2026-11-01;A;0.20;RECEITA\n2026-11-01;B;0.01;DESPESA\n", encoding="utf-8")
    df = carregar_dados(str(source), 0)
    html = montar_html(df, {})
    assert "R$ 0,30" in html and "R$ 0,29" in html
    assert moeda(123456789) == "R$ 1.234.567,89"
    assert centavos("1.001") is None

def test_report_discloses_rejected_records_and_dates(tmp_path):
    source = tmp_path / "rejeitados.csv"
    source.write_text("Data;Categoria;Valor;Tipo\n2026-11-01;A;1.001;RECEITA\nsem data;B;0.20;RECEITA\n2026-11-01;C;0.20;OUTRO\n", encoding="utf-8")
    with pytest.warns(UserWarning):
        df = carregar_dados(str(source), 0)
    assert len(df) == 1
    html = montar_html(df, {})
    assert "2 registro(s) rejeitado(s)" in html
    assert "Registro 1:" in html and "Registro 3:" in html
    assert "1 data(s)" in html
