import Foundation
import GastosClient

@main
struct GastosCLI {
    static func main() async {
        let command = CommandLine.arguments.dropFirst().first ?? "help"
        guard ["health", "pessoas", "resumo"].contains(command) else {
            print("Uso: swift run gastos-cli health|pessoas|resumo")
            return
        }
        do {
            // Optional only for the local operator; never print it in output.
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
            default:
                break
            }
        } catch {
            fputs("Falha ao consultar a API local: \(error)\n", stderr)
            exit(1)
        }
    }
}
