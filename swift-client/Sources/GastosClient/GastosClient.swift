import Foundation
#if canImport(FoundationNetworking)
import FoundationNetworking
#endif

/// Reject any redirect, including a redirect to a non-loopback host.
/// URLSession would otherwise follow it and might forward authentication data.
private final class NoRedirectDelegate: NSObject, URLSessionTaskDelegate, @unchecked Sendable {
    func urlSession(
        _ session: URLSession,
        task: URLSessionTask,
        willPerformHTTPRedirection response: HTTPURLResponse,
        newRequest request: URLRequest,
        completionHandler: @escaping (URLRequest?) -> Void
    ) {
        completionHandler(nil)
    }
}

public struct Health: Decodable {
    public let status: String
}

public struct Pessoa: Decodable {
    public let id: Int
    public let nome: String
    public let idade: Int
}

public struct Resumo: Decodable {
    public let totalReceitas: Decimal
    public let totalDespesas: Decimal
    public let saldoGeral: Decimal
}

public struct Transacao: Decodable {
    public let id: Int
    public let descricao: String
    public let valor: Decimal
    public let tipo: String
    public let pessoaId: Int
    public let pessoaNome: String
    public let dataCriacao: String
}

public enum GastosClientError: Error, Equatable {
    case invalidBaseURL
    case invalidPagination
    case invalidTransactionType
    case unexpectedResponse
    case httpStatus(Int)
}

/// Read-only client for the locally bound ASP.NET Core API.
/// It deliberately refuses non-loopback URLs to avoid leaking a bearer token.
public struct GastosClient {
    private let baseURL: URL
    private let token: String?

    public init(baseURL: URL = URL(string: "http://127.0.0.1:5000")!, token: String? = nil) throws {
        guard baseURL.scheme == "http",
              ["127.0.0.1", "localhost"].contains(baseURL.host ?? ""),
              baseURL.port == 5000,
              baseURL.user == nil, baseURL.password == nil,
              baseURL.query == nil, baseURL.fragment == nil,
              baseURL.path.isEmpty || baseURL.path == "/" else {
            throw GastosClientError.invalidBaseURL
        }
        self.baseURL = baseURL
        self.token = token
    }

    public func health() async throws -> Health {
        try await get("api/health")
    }

    public func pessoas() async throws -> [Pessoa] {
        try await get("api/pessoas")
    }

    public func resumo() async throws -> Resumo {
        try await get("api/transacoes/totais/resumo")
    }

    /// Mirrors the backend's limits and accepted transaction types before making HTTP requests.
    public static func transactionQuery(page: Int, limit: Int, tipo: String? = nil) throws -> [URLQueryItem] {
        guard (1...100_000).contains(page), (1...100).contains(limit) else {
            throw GastosClientError.invalidPagination
        }
        var items = [
            URLQueryItem(name: "page", value: String(page)),
            URLQueryItem(name: "limit", value: String(limit)),
        ]
        if let tipo {
            let normalized = tipo.trimmingCharacters(in: .whitespacesAndNewlines).uppercased()
            guard ["RECEITA", "DESPESA"].contains(normalized) else {
                throw GastosClientError.invalidTransactionType
            }
            items.append(URLQueryItem(name: "tipo", value: normalized))
        }
        return items
    }

    public func transacoes(page: Int = 1, limit: Int = 20, tipo: String? = nil) async throws -> [Transacao] {
        let query = try Self.transactionQuery(page: page, limit: limit, tipo: tipo)
        return try await get("api/transacoes", queryItems: query)
    }

    private func get<T: Decodable>(_ path: String, queryItems: [URLQueryItem] = []) async throws -> T {
        guard var components = URLComponents(
            url: baseURL.appendingPathComponent(path),
            resolvingAgainstBaseURL: false
        ) else {
            throw GastosClientError.invalidBaseURL
        }
        if !queryItems.isEmpty { components.queryItems = queryItems }
        guard let url = components.url else {
            throw GastosClientError.invalidBaseURL
        }
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.timeoutInterval = 10
        if let token, !token.isEmpty {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        let session = URLSession(configuration: .ephemeral, delegate: NoRedirectDelegate(), delegateQueue: nil)
        defer { session.invalidateAndCancel() }
        let (data, response) = try await session.data(for: request)
        guard let response = response as? HTTPURLResponse else {
            throw GastosClientError.unexpectedResponse
        }
        guard (200...299).contains(response.statusCode) else {
            throw GastosClientError.httpStatus(response.statusCode)
        }
        return try JSONDecoder().decode(T.self, from: data)
    }
}
