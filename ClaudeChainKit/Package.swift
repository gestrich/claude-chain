// swift-tools-version: 5.9

import PackageDescription

let package = Package(
    name: "ClaudeChainKit",
    platforms: [
        .macOS(.v13),
    ],
    products: [
        .library(
            name: "ClaudeChainKit",
            targets: ["ClaudeChainDomain", "ClaudeChainInfrastructure", "ClaudeChainServices", "ClaudeChainCLI"]
        ),
        .executable(
            name: "claude-chain",
            targets: ["ClaudeChainMain"]
        ),
    ],
    dependencies: [
        .package(url: "https://github.com/jpsim/Yams.git", from: "5.0.0"),
        .package(url: "https://github.com/apple/swift-argument-parser.git", from: "1.2.0"),
    ],
    targets: [
        .target(
            name: "ClaudeChainDomain",
            dependencies: [
                .product(name: "Yams", package: "Yams"),
            ],
            path: "Sources/Domain"
        ),
        .target(
            name: "ClaudeChainInfrastructure",
            dependencies: ["ClaudeChainDomain"],
            path: "Sources/Infrastructure"
        ),
        .target(
            name: "ClaudeChainServices",
            dependencies: ["ClaudeChainDomain", "ClaudeChainInfrastructure"],
            path: "Sources/Services"
        ),
        .target(
            name: "ClaudeChainCLI",
            dependencies: [
                "ClaudeChainDomain",
                "ClaudeChainInfrastructure",
                "ClaudeChainServices",
                .product(name: "ArgumentParser", package: "swift-argument-parser"),
            ],
            path: "Sources/CLI"
        ),
        .executableTarget(
            name: "ClaudeChainMain",
            dependencies: ["ClaudeChainCLI"],
            path: "Sources/Main"
        ),
        .testTarget(
            name: "ClaudeChainDomainTests",
            dependencies: ["ClaudeChainDomain"],
            path: "Tests/Domain"
        ),
        .testTarget(
            name: "ClaudeChainInfrastructureTests",
            dependencies: ["ClaudeChainDomain", "ClaudeChainInfrastructure"],
            path: "Tests/Infrastructure"
        ),
        .testTarget(
            name: "ClaudeChainServicesTests",
            dependencies: ["ClaudeChainDomain", "ClaudeChainInfrastructure", "ClaudeChainServices"],
            path: "Tests/Services"
        ),
        .testTarget(
            name: "ClaudeChainCLITests",
            dependencies: ["ClaudeChainCLI"],
            path: "Tests/CLI"
        ),
    ]
)
