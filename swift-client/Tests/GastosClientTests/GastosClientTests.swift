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
}
