import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
import gerar_relatorio as report
def test_pie_handles_zero_and_negative_totals():
    for values in ([0, 0], [-5, 3], [-1, -2]):
        frame = pd.DataFrame({report.COLUNA_CATEGORIA: ["A", "B"], report.COLUNA_VALOR: values})
        assert report.grafico_pizza(frame)
def test_temporal_skips_invalid_dates():
    frame = pd.DataFrame({report.COLUNA_DATA: [pd.NaT], report.COLUNA_VALOR: [1]})
    assert report.grafico_temporal(frame) is None
