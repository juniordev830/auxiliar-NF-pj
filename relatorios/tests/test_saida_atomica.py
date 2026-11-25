from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gerar_relatorio as report


def test_atomic_publish(tmp_path):
    output = tmp_path / "report.html"
    output.write_text("anterior", encoding="utf-8")
    report.salvar_html(output, "novo relatório")
    assert output.read_text(encoding="utf-8") == "novo relatório"
    assert list(tmp_path.iterdir()) == [output]


def test_failed_publish_preserves_previous_report(tmp_path, monkeypatch):
    output = tmp_path / "report.html"
    output.write_text("anterior", encoding="utf-8")

    def fail(*args):
        raise OSError("falha simulada")

    monkeypatch.setattr(report.os, "replace", fail)
    with pytest.raises(OSError, match="falha simulada"):
        report.salvar_html(output, "incompleto")
    assert output.read_text(encoding="utf-8") == "anterior"
    assert list(tmp_path.iterdir()) == [output]
