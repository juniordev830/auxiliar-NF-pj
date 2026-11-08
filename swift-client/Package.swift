// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "GastosSwiftClient",
    products: [
        .library(name: "GastosClient", targets: ["GastosClient"]),
        .executable(name: "gastos-cli", targets: ["GastosCLI"]),
    ],
    targets: [
        .target(name: "GastosClient"),
        .executableTarget(name: "GastosCLI", dependencies: ["GastosClient"]),
        .testTarget(name: "GastosClientTests", dependencies: ["GastosClient"]),
    ]
)
