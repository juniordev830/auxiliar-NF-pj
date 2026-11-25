"""Integration test: run against CI's temporary databases and local server."""
import json
import os
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BASE = "http://127.0.0.1:5000/api"

def call(path, method="GET", data=None, reader=False):
    token = os.environ["GASTOS_READ_TOKEN" if reader else "GASTOS_ADMIN_TOKEN"]
    req = Request(BASE + path, method=method,
                  data=json.dumps(data).encode() if data is not None else None,
                  headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=5) as response:
            raw = response.read()
            return response.status, json.loads(raw) if raw else None
    except HTTPError as err:
        return err.code, None

class PjAudit(unittest.TestCase):
    def test_lifecycle(self):
        data = dict(descricao="Teste CI", tipo="RECEITA", categoria="CI",
                    valor=12.34, competencia="2026-11-01", vencimento="2026-11-01")
        status, item = call("/pj/lancamentos", "POST", data)
        self.assertEqual(status, 201)
        path = "/pj/lancamentos/" + str(item["id"])
        self.assertEqual(call(path, "PUT", data, reader=True)[0], 403)
        data["valor"] = 15.67
        self.assertEqual(call(path, "PUT", data)[0], 200)
        self.assertEqual(call(path + "/pagamento", "PUT", {"dataPagamento":"2026-11-02"})[0], 200)
        status, page = call("/pj/lancamentos?ano=2026&mes=11&status=PAGO&limit=1")
        self.assertEqual(status, 200)
        self.assertEqual(page["items"][0]["valor"], 15.67)
        self.assertEqual(call(path, "DELETE")[0], 204)
        self.assertEqual(call(path, "PUT", data)[0], 404)
        status, page = call("/pj/lancamentos?ano=2026&mes=11")
        self.assertEqual(page["total"], 0)
        status, history = call(path + "/historico", reader=True)
        self.assertEqual(status, 200)
        self.assertEqual([x["acao"] for x in history["items"]],
                         ["EXCLUSAO", "PAGAMENTO", "EDICAO", "CRIACAO"])
        self.assertEqual(call("/transacoes?ate=9999-12-31")[0], 400)

if __name__ == "__main__":
    unittest.main()
