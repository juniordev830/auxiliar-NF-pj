"""Integration regression for due-date boundaries and paid/deleted exclusion."""
import unittest
from test_fluxo_caixa import request

class DueDates(unittest.TestCase):
    def test_due_buckets(self):
        ids = []
        try:
            for date, kind, amount, paid in [
                ("2026-05-09", "RECEITA", 0.10, None),
                ("2026-05-10", "DESPESA", 0.20, None),
                ("2026-05-17", "RECEITA", 0.30, None),
                ("2026-05-18", "DESPESA", 0.40, None),
                ("2026-06-09", "RECEITA", 0.50, None),
                ("2026-06-10", "DESPESA", 0.60, None),
                (None, "RECEITA", 0.70, None),
                ("2026-05-09", "RECEITA", 999, "2026-05-09")
            ]:
                status, row = request("/pj/lancamentos", "POST", dict(
                    descricao="Vencimento CI", categoria="CI", tipo=kind,
                    valor=amount, competencia="2026-05-01",
                    vencimento=date, dataPagamento=paid))
                self.assertEqual(status, 201)
                ids.append(row["id"])
            endpoint = "/pj/contas-a-vencer?referencia=2026-05-10"
            status, data = request(endpoint, read=True)
            self.assertEqual(status, 200)
            self.assertEqual(data["aReceber"], 1.60)
            self.assertEqual(data["aPagar"], 1.20)
            self.assertEqual(data["quantidade"], 7)
            self.assertEqual([x["quantidade"] for x in data["faixas"]], [1,1,1,2,1,1])
            self.assertEqual(data["faixas"][3]["saldoPrevisto"], 0.10)
            self.assertEqual(request("/pj/lancamentos/" + str(ids[0]), "DELETE")[0], 204)
            self.assertEqual(request(endpoint)[1]["faixas"][0]["quantidade"], 0)
            self.assertEqual(request("/pj/contas-a-vencer?referencia=1999-12-31")[0], 400)
        finally:
            for entry in ids:
                request("/pj/lancamentos/" + str(entry), "DELETE")

if __name__ == "__main__":
    unittest.main()
