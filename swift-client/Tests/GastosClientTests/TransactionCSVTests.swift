import Foundation
import XCTest
@testable import GastosClient

final class TransactionCSVTests: XCTestCase {
    func testExportsHeadingsAndTransactionFields() {
        let transaction = Transacao(
            id: 7,
            descricao: "Mercado",
            valor: Decimal(string: "125.90")!,
            tipo: "DESPESA",
            pessoaId: 3,
            pessoaNome: "Ana",
            dataCriacao: "2026-11-07T14:35:00"
        )

        let csv = TransactionCSV.render([transaction])
        XCTAssertEqual(
            csv,
            "\"" + "id\",\"dataCriacao\",\"descricao\",\"valor\",\"tipo\",\"pessoaId\",\"pessoaNome\"" +
            "\r\n\"7\",\"2026-11-07T14:35:00\",\"Mercado\",\"125.9\",\"DESPESA\",\"3\",\"Ana\"\r\n"
        )
    }

    func testEscapesQuotesCommasNewlinesAndSpreadsheetFormulas() {
        let transaction = Transacao(
            id: 8,
            descricao: "   =1+1",
            valor: Decimal(string: "12.50")!,
            tipo: "DESPESA",
            pessoaId: 4,
            pessoaNome: "Ana \"Q\", Silva\nAtendimento",
            dataCriacao: "2026-11-07T00:00:00"
        )
        let csv = TransactionCSV.render([transaction])
        XCTAssertTrue(csv.contains("\"'   =1+1\""))
        XCTAssertTrue(csv.contains("\"Ana \"\"Q\"\", Silva\nAtendimento\""))
        XCTAssertFalse(csv.contains("\"   =1+1\""))
    }

    func testPrefixProtectsOtherFormulaTriggers() {
        for input in ["+SUM(1,1)", "-2+3", "@SUM(A1)", "\t=1+1", "\r=1+1"] {
            let transaction = Transacao(
                id: 9,
                descricao: input,
                valor: 1,
                tipo: "RECEITA",
                pessoaId: 1,
                pessoaNome: "Conta",
                dataCriacao: "2026-11-07"
            )
            let csv = TransactionCSV.render([transaction])
            XCTAssertTrue(csv.contains("\"'" + input + "\""), "Unsafe value: \(input)")
        }
    }

    func testEmptyResultStillHasHeaderAndTrailingCRLF() {
        let csv = TransactionCSV.render([])
        XCTAssertTrue(csv.hasPrefix("\"id\",\"dataCriacao\""))
        XCTAssertTrue(csv.hasSuffix("\r\n"))
        XCTAssertEqual(csv.filter { $0 == "\n" }.count, 1)
    }
}
