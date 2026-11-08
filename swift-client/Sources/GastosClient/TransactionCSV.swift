import Foundation

/// Convert read-only API transactions into spreadsheet-compatible CSV.
/// All fields are quoted; leading formula triggers in user-controlled values
/// are prefixed with a single quote to prevent spreadsheet formula execution.
public enum TransactionCSV {
    private static let header = [
        "id", "dataCriacao", "descricao", "valor", "tipo", "pessoaId", "pessoaNome",
    ]

    public static func render(_ transactions: [Transacao]) -> String {
        let rows = transactions.map { transaction in
            [
                String(transaction.id),
                transaction.dataCriacao,
                transaction.descricao,
                NSDecimalNumber(decimal: transaction.valor).stringValue,
                transaction.tipo,
                String(transaction.pessoaId),
                transaction.pessoaNome,
            ].map(escape).joined(separator: ",")
        }
        // CRLF supports common spreadsheet importers; also terminate empty results.
        return ([header.map(escape).joined(separator: ",")] + rows)
            .joined(separator: "\r\n") + "\r\n"
    }

    private static func escape(_ original: String) -> String {
        // Treat these characters as potential spreadsheet formulas, even if
        // preceded by whitespace. Fields may contain untrusted user input.
        let trimmed = original.drop(while: { $0.isWhitespace })
        let dangerous = "=+-@".contains(trimmed.first ?? " ")
        let controlPrefix = original.first == "\t" || original.first == "\r"
            || original.first == "\n"
        let safe = (dangerous || controlPrefix ? "'" : "") + original
        return "\"" + safe.replacingOccurrences(of: "\"", with: "\"\"") + "\""
    }
}
