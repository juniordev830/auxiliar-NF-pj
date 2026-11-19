"""Exercise the ASP.NET API over fixtures from the pre-migration SQLite schema."""
from contextlib import closing
import csv
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import time
import unittest
from urllib.error import URLError
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1] / "ControladorGastos"
APP = ROOT / "bin" / "Release" / "net8.0" / "ControladorGastos.dll"
BASE_URL = "http://127.0.0.1:5000"


def seed_legacy(residential, pj):
    with closing(sqlite3.connect(residential)) as connection, connection:
        connection.executescript("""
            CREATE TABLE Pessoas (
                Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, Nome TEXT NOT NULL,
                Idade INTEGER NOT NULL, DataCriacao TEXT NOT NULL);
            CREATE TABLE Transacoes (
                Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, Descricao TEXT NOT NULL,
                Valor TEXT NOT NULL, Tipo TEXT NOT NULL, PessoaId INTEGER NOT NULL,
                DataCriacao TEXT NOT NULL,
                FOREIGN KEY (PessoaId) REFERENCES Pessoas (Id) ON DELETE CASCADE);
            CREATE INDEX IX_Transacoes_PessoaId ON Transacoes (PessoaId);
            INSERT INTO Pessoas VALUES (1, 'Ana', 31, '2026-11-01 00:00:00');
            INSERT INTO Transacoes VALUES (1, 'Transporte', '62.50', 'DESPESA', 1, '2026-11-02 00:00:00');
        """)
    with closing(sqlite3.connect(pj)) as connection, connection:
        connection.executescript("""
            CREATE TABLE Lancamentos (
                Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, Descricao TEXT NOT NULL,
                Tipo TEXT NOT NULL, Categoria TEXT NOT NULL, Contraparte TEXT NULL,
                Valor TEXT NOT NULL, Competencia TEXT NOT NULL, Vencimento TEXT NULL,
                DataPagamento TEXT NULL, CriadoEm TEXT NOT NULL);
            CREATE INDEX IX_Lancamentos_Competencia ON Lancamentos (Competencia);
            INSERT INTO Lancamentos VALUES (
                7, 'Consultoria', 'RECEITA', 'Serviços', 'Cliente teste', '1500.75',
                '2026-11-02 00:00:00', '2026-11-15 00:00:00', '2026-11-10 00:00:00',
                '2026-11-02 00:00:00');
        """)


def request(path):
    with urlopen(BASE_URL + path, timeout=2) as response:
        return response.read()


class LegacyUpgradeTest(unittest.TestCase):
    def test_legacy_data_survives_two_app_starts_and_exports(self):
        with tempfile.TemporaryDirectory() as scratch:
            directory = Path(scratch)
            residential, pj = directory / "residential.db", directory / "pj.db"
            seed_legacy(residential, pj)
            env = {
                **os.environ,
                "ConnectionStrings__DefaultConnection": f"Data Source={residential}",
                "ConnectionStrings__AuxiliarPj": f"Data Source={pj}",
                "GASTOS_READ_TOKEN": "",
                "GASTOS_ADMIN_TOKEN": "",
            }

            for startup in range(2):
                log = directory / f"startup-{startup}.log"
                with log.open("w+b") as output:
                    process = subprocess.Popen(["dotnet", str(APP)], cwd=ROOT, env=env, stdout=output, stderr=output)
                    try:
                        for _ in range(80):
                            if process.poll() is not None:
                                self.fail(log.read_text())
                            if "Now listening on:" in log.read_text():
                                try:
                                    request("/api/health")
                                except URLError:
                                    pass
                                else:
                                    break
                            time.sleep(0.125)
                        else:
                            self.fail(log.read_text())

                        people = json.loads(request("/api/pessoas"))
                        self.assertEqual([(row["id"], row["nome"]) for row in people], [(1, "Ana")])
                        entries = json.loads(request("/api/transacoes"))
                        self.assertEqual([(row["id"], row["valor"]) for row in entries], [(1, 62.5)])
                        summary = json.loads(request("/api/pj/resumo?ano=2026&mes=11"))
                        self.assertEqual(summary["saldoRealizado"], 1500.75)
                        exported = request("/api/pj/exportar.csv?ano=2026&mes=11").decode("utf-8-sig")
                        rows = list(csv.DictReader(exported.splitlines(), delimiter=";"))
                        self.assertEqual(len(rows), 1)
                        self.assertEqual((rows[0]["Valor"], rows[0]["Pagamento"]), ("1500.75", "2026-11-10"))
                    finally:
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait()

            for database, migration in [(residential, "BaselineResidencial"), (pj, "BaselineAuxiliarPj")]:
                with closing(sqlite3.connect(database)) as connection:
                    history = connection.execute('SELECT MigrationId FROM "__EFMigrationsHistory"').fetchall()
                self.assertEqual(len(history), 1)
                self.assertTrue(history[0][0].endswith(migration))


if __name__ == "__main__":
    unittest.main()
