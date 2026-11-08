import Foundation
#if canImport(FoundationNetworking)
import FoundationNetworking
#endif

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

public enum GastosClientError: Error, Equatable {
    case invalidBaseURL
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

    private func get<T: Decodable>(_ path: String) async throws -> T {
        var request = URLRequest(url: baseURL.appendingPathComponent(path))
        request.httpMethod = "GET"
        request.timeoutInterval = 10
        if let token, !token.isEmpty {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        let (data, response) = try await URLSession.shared.data(for: request)
        guard let response = response as? HTTPURLResponse else {
            throw GastosClientError.unexpectedResponse
        }
        guard (200...299).contains(response.statusCode) else {
            throw GastosClientError.httpStatus(response.statusCode)
        }
        return try JSONDecoder().decode(T.self, from: data)
    }
}
