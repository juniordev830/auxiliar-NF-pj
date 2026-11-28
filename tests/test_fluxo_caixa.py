"""Integration coverage for cash flow by payment date."""
import json
import os
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

BASE = "http://127.0.0.1:5000/api"

def request(path, method="GET", body=None, read=False):
    token = os.environ["GASTOS_READ_TOKEN" if read else "GASTOS_ADMIN_TOKEN"]
    req = Request(BASE + path, method=method,
                  data=json.dumps(body).encode() if body is not None else None,
                  headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=5) as response:
            raw = response.read()
            return response.status, json.loads(raw) if raw else None
    except HTTPError as exc:
        return exc.code, None

class CashFlowTest(unittest.TestCase):
    def test_cash_month_differs_from_competence(self):
        ids = []
        try:
            for tipo, valor, pagamento in [
                ("RECEITA", 0.10, "2026-09-02"),
                ("RECEITA", 0.20, "2026-09-02"),
                ("DESPESA", 0.01, "2026-09-03"),
                ("RECEITA", 500, None),
                ("DESPESA", 50, "2026-10-01"),
            ]:
                status, row = request("/pj/lancamentos", "POST", dict(
                    descricao="Fluxo CI", categoria="CI", tipo=tipo, valor=valor,
                    competencia="2026-08-01", dataPagamento=pagamento))
                self.assertEqual(status, 201)
                ids.append(row["id"])
            status, result = request("/pj/fluxo-caixa?ano=2026&mes=9", read=True)
            self.assertEqual(status, 200)
            self.assertEqual(result["receitas"], 0.30)
            self.assertEqual(result["despesas"], 0.01)
            self.assertEqual(result["saldo"], 0.29)
            self.assertEqual(result["quantidade"], 3)
            self.assertEqual([day["data"] for day in result["dias"]], ["2026-09-02", "2026-09-03"])
            self.assertEqual(request("/pj/lancamentos/" + str(ids[0]), "DELETE")[0], 204)
            ids.pop(0)
            self.assertEqual(request("/pj/fluxo-caixa?ano=2026&mes=9")[1]["receitas"], 0.20)
            self.assertEqual(request("/pj/fluxo-caixa?ano=2026&mes=13")[0], 400)
            self.assertEqual(request("/pj/fluxo-caixa?ano=2026&mes=7")[1]["dias"], [])
        finally:
            for entry in ids:
                request("/pj/lancamentos/" + str(entry), "DELETE")

if __name__ == "__main__":
    unittest.main()
