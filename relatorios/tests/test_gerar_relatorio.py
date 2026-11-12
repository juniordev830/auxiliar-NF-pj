import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gerar_relatorio import montar_html


def test_report_escapes_untrusted_category_values():
    malicious = '<script>alert("xss")</script>'
    frame = pd.DataFrame({"Categoria": [malicious], "Valor": [10.0]})

    html = montar_html(frame, {})

    assert "<script>alert" not in html
    assert "&lt;script&gt;" in html
    assert "&lt;/script&gt;" in html



def test_load_data_discards_non_finite_amounts(monkeypatch):
    import gerar_relatorio

    frame = pd.DataFrame({
        "Categoria": ["válido", "infinito", "negativo infinito", "ausente"],
        "Valor": [12.5, float("inf"), float("-inf"), None],
    })
    monkeypatch.setattr(gerar_relatorio.pd, "read_excel", lambda *args, **kwargs: frame.copy())

    result = gerar_relatorio.carregar_dados("ignored.xlsx", 0)

    assert result["Categoria"].tolist() == ["válido"]
    assert result["Valor"].tolist() == [12.5]


def test_load_data_rejects_only_non_finite_amounts(monkeypatch):
    import pytest
    import gerar_relatorio

    frame = pd.DataFrame({"Categoria": ["infinito"], "Valor": [float("inf")]})
    monkeypatch.setattr(gerar_relatorio.pd, "read_excel", lambda *args, **kwargs: frame.copy())

    with pytest.raises(ValueError, match="não possui registros válidos"):
        gerar_relatorio.carregar_dados("ignored.xlsx", 0)


def test_parse_sheet_selector():
    import gerar_relatorio

    assert gerar_relatorio.parse_aba("2") == 2
    assert gerar_relatorio.parse_aba("Vendas") == "Vendas"
