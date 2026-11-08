import Foundation
import XCTest
@testable import GastosClient

final class GastosClientTests: XCTestCase {
    func testAcceptsOnlyLocalAPIURLs() throws {
        XCTAssertNoThrow(try GastosClient())
        XCTAssertNoThrow(try GastosClient(baseURL: URL(string: "http://localhost:5000")!))
        for invalid in ["https://example.com:5000", "http://127.0.0.1:8080", "http://user:pass@localhost:5000", "http://localhost:5000/api"] {
            XCTAssertThrowsError(try GastosClient(baseURL: URL(string: invalid)!))
        }
    }

    func testDecodesActualAPIResponseShapes() throws {
        let health = try JSONDecoder().decode(Health.self, from: Data(#"{"status":"ok"}"#.utf8))
        XCTAssertEqual(health.status, "ok")
        let people = try JSONDecoder().decode([Pessoa].self, from: Data(#"[{"id":1,"nome":"Ana","idade":30}]"#.utf8))
        XCTAssertEqual(people.first?.nome, "Ana")
        let summary = try JSONDecoder().decode(Resumo.self, from: Data(#"{"totalReceitas":250.50,"totalDespesas":100.25,"saldoGeral":150.25}"#.utf8))
        XCTAssertEqual(summary.saldoGeral, Decimal(string: "150.25"))
    }

    func testTransactionQueryRespectsBackendValidation() throws {
        let query = try GastosClient.transactionQuery(page: 2, limit: 10, tipo: " despesa ")
        XCTAssertEqual(query.map { $0.name }, ["page", "limit", "tipo"])
        XCTAssertEqual(query.map { $0.value ?? "" }, ["2", "10", "DESPESA"])
        XCTAssertThrowsError(try GastosClient.transactionQuery(page: 0, limit: 10))
        XCTAssertThrowsError(try GastosClient.transactionQuery(page: 1, limit: 101))
        XCTAssertThrowsError(try GastosClient.transactionQuery(page: 100_001, limit: 1))
        XCTAssertThrowsError(try GastosClient.transactionQuery(page: 1, limit: 10, tipo: "TRANSFERENCIA"))
        let noFilter = try GastosClient.transactionQuery(page: 1, limit: 20)
        XCTAssertEqual(noFilter.count, 2)
    }

    func testDecodesTransactionResponse() throws {
        let json = #"[{"id":7,"descricao":"Mercado","valor":125.90,"tipo":"DESPESA","pessoaId":1,"pessoaNome":"Ana","dataCriacao":"2026-11-07T14:35:00"}]"#
        let transactions = try JSONDecoder().decode([Transacao].self, from: Data(json.utf8))
        XCTAssertEqual(transactions.count, 1)
        XCTAssertEqual(transactions.first?.id, 7)
        XCTAssertEqual(transactions.first?.pessoaNome, "Ana")
        XCTAssertEqual(transactions.first?.tipo, "DESPESA")
        XCTAssertEqual(transactions.first?.valor, Decimal(string: "125.90"))
    }

}
