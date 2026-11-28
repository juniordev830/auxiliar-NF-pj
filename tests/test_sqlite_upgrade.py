"""Exercise the ASP.NET API over fixtures from the pre-migration SQLite schema."""
from contextlib import closing, contextmanager
import csv
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import time
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1] / "ControladorGastos"
APP = ROOT / "bin" / "Release" / "net8.0" / "ControladorGastos.dll"
BASE_URL = "http://127.0.0.1:5000"
READ_TOKEN = "ci-read-token-for-tests-only-0123456789abcdef"
ADMIN_TOKEN = "ci-admin-token-for-tests-only-0123456789abcdef"


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
                7, '=HYPERLINK("https://example.invalid","abrir")', 'RECEITA', 'Serviços',
                '+SUM(1,1)', '1500.75', '2026-11-02 00:00:00', '2026-11-15 00:00:00',
                '2026-11-10 00:00:00', '2026-11-02 00:00:00');
        """)


def api(path, token, *, method="GET", body=None):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = json.dumps(body).encode() if body is not None else None
    req = Request(BASE_URL + path, data=payload, headers=headers, method=method)
    try:
        response = urlopen(req, timeout=2)
    except HTTPError as error:
        response = error
    with response:
        return response.status, response.read()


def request(path):
    status, data = api(path, READ_TOKEN)
    if status != 200:
        raise AssertionError(f"HTTP {status} for {path}")
    return data


@contextmanager
def running_api(log, env):
    with log.open("w+b") as output:
        process = subprocess.Popen(["dotnet", str(APP)], cwd=ROOT, env=env, stdout=output, stderr=output)
        try:
            for _ in range(80):
                if process.poll() is not None:
                    raise AssertionError(log.read_text())
                if "Now listening on:" in log.read_text():
                    try:
                        request("/api/health")
                    except URLError:
                        pass
                    else:
                        break
                time.sleep(0.125)
            else:
                raise AssertionError(log.read_text())
            yield
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


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
                "GASTOS_READ_TOKEN": READ_TOKEN,
                "GASTOS_ADMIN_TOKEN": ADMIN_TOKEN,
            }

            for startup in range(2):
                log = directory / f"startup-{startup}.log"
                with running_api(log, env):
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
                    # Text fields that begin with spreadsheet formulas must be neutralized.
                    self.assertEqual(rows[0]["Descricao"], "'=HYPERLINK(\"https://example.invalid\",\"abrir\")")
                    self.assertEqual(rows[0]["Contraparte"], "'+SUM(1,1)")

            for database, migration in [(residential, "BaselineResidencial"), (pj, "BaselineAuxiliarPj")]:
                with closing(sqlite3.connect(database)) as connection:
                    history = connection.execute('SELECT MigrationId FROM "__EFMigrationsHistory"').fetchall()
                expected = 3 if database == pj else 1
                self.assertEqual(len(history), expected)
                self.assertTrue(any(row[0].endswith(migration) for row in history))
                if database == pj:
                    self.assertTrue(any(row[0].endswith("AuditoriaPj") for row in history))
                    self.assertTrue(any(row[0].endswith("CredenciaisPj") for row in history))

    def test_individual_credentials_attribute_and_revoke_writes(self):
        with tempfile.TemporaryDirectory() as scratch:
            directory = Path(scratch)
            env = {
                **os.environ,
                "ConnectionStrings__DefaultConnection": f"Data Source={directory / 'res.db'}",
                "ConnectionStrings__AuxiliarPj": f"Data Source={directory / 'pj.db'}",
                "GASTOS_READ_TOKEN": READ_TOKEN,
                "GASTOS_ADMIN_TOKEN": ADMIN_TOKEN,
            }
            tokens = {}
            for actor, role, expires in (("operador-01", "admin", "2099-01-01T00:00:00Z"),
                                         ("leitor-02", "read", "2099-01-01T00:00:00Z"),
                                         ("expirado-03", "admin", "2000-01-01T00:00:00Z")):
                token = f"{actor}.{'x' * 40}"
                tokens[actor] = token
                prefix = f"GASTOS_CREDENCIAIS__{actor}__"
                env[prefix + "TokenHash"] = hashlib.sha256(token.encode()).hexdigest()
                env[prefix + "Role"] = role
                env[prefix + "ExpiresAt"] = expires
            admin, reader, expired = tokens.values()
            entries = "/api/pj/lancamentos"
            input_data = {"descricao": "Teste individual", "tipo": "RECEITA", "categoria": "CI",
                          "valor": 12.34, "competencia": "2026-11-01"}
            with running_api(directory / "first.log", env):
                self.assertEqual(api(entries, ADMIN_TOKEN)[0], 401)
                self.assertEqual(api(entries, expired)[0], 401)
                self.assertEqual(api(entries, reader)[0], 200)
                self.assertEqual(api(entries, reader, method="POST", body=input_data)[0], 403)
                status, response = api(entries, admin, method="POST", body=input_data)
                self.assertEqual(status, 201, response)
                entry = json.loads(response)["id"]
                status, history = api(f"{entries}/{entry}/historico", reader)
                self.assertEqual(status, 200)
                self.assertEqual(json.loads(history)["items"][0]["responsavel"], "operador-01")
                self.assertEqual(api("/api/session/logout", admin, method="POST")[0], 204)
                self.assertEqual(api(entries, admin)[0], 401)

            with running_api(directory / "second.log", env):
                self.assertEqual(api(entries, admin)[0], 401)
                self.assertEqual(api(entries, reader)[0], 200)



if __name__ == "__main__":
    unittest.main()
