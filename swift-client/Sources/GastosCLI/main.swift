import Foundation
import GastosClient

@main
struct GastosCLI {
    private static let usage = """
    Uso:
      swift run gastos-cli health
      swift run gastos-cli pessoas
      swift run gastos-cli resumo
      swift run gastos-cli transacoes [pagina] [limite] [RECEITA|DESPESA]

    A API deve estar executando na mesma maquina em 127.0.0.1:5000.
    """

    static func main() async {
        let arguments = Array(CommandLine.arguments.dropFirst())
        guard let command = arguments.first, ["health", "pessoas", "resumo", "transacoes"].contains(command) else {
            print(usage)
            return
        }
        do {
            // Optional read-only token for a local operator. Never print it.
            let token = ProcessInfo.processInfo.environment["GASTOS_READ_TOKEN"]
            let client = try GastosClient(token: token)
            switch command {
            case "health":
                print("API: \(try await client.health().status)")
            case "pessoas":
                let pessoas = try await client.pessoas()
                for pessoa in pessoas {
                    print("#\(pessoa.id) \(pessoa.nome) (\(pessoa.idade) anos)")
                }
                if pessoas.isEmpty { print("Nenhuma pessoa cadastrada.") }
            case "resumo":
                let resumo = try await client.resumo()
                print("Receitas: \(resumo.totalReceitas)")
                print("Despesas: \(resumo.totalDespesas)")
                print("Saldo: \(resumo.saldoGeral)")
            case "transacoes":
                guard arguments.count <= 4,
                      let page = Int(arguments.count > 1 ? arguments[1] : "1"),
                      let limit = Int(arguments.count > 2 ? arguments[2] : "20") else {
                    fputs("Argumentos invalidos.\n\(usage)\n", stderr)
                    exit(2)
                }
                let tipo = arguments.count > 3 ? arguments[3] : nil
                let transacoes = try await client.transacoes(page: page, limit: limit, tipo: tipo)
                for transaction in transacoes {
                    print("#\(transaction.id) [\(transaction.tipo)] \(transaction.descricao): \(transaction.valor) (\(transaction.pessoaNome))")
                }
                if transacoes.isEmpty { print("Nenhuma transacao encontrada.") }
            default:
                break
            }
        } catch {
            fputs("Falha ao consultar a API local: \(error)\n", stderr)
            exit(1)
        }
    }
}
