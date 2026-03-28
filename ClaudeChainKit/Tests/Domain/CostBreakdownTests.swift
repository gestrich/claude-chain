/// Unit tests for CostBreakdown domain model
import XCTest
import Foundation
@testable import ClaudeChainDomain

final class TestCostBreakdownConstruction: XCTestCase {
    /// Test suite for CostBreakdown construction and basic properties
    
    func testCanCreateCostBreakdown() {
        /// Should be able to create CostBreakdown instance
        let breakdown = CostBreakdown(mainCost: 1.5, summaryCost: 0.5)
        
        XCTAssertEqual(breakdown.mainCost, 1.5)
        XCTAssertEqual(breakdown.summaryCost, 0.5)
    }
    
    func testTotalCostCalculation() {
        /// Should calculate total cost correctly
        let breakdown = CostBreakdown(mainCost: 1.234567, summaryCost: 0.654321)
        
        let total = breakdown.totalCost
        
        XCTAssertEqual(total, 1.888888, accuracy: 0.000001)
    }
    
    func testZeroCosts() {
        /// Should handle zero costs
        let breakdown = CostBreakdown(mainCost: 0.0, summaryCost: 0.0)
        
        let total = breakdown.totalCost
        
        XCTAssertEqual(total, 0.0)
    }
}

final class TestCostBreakdownFromExecutionFiles: XCTestCase {
    /// Test suite for CostBreakdown.fromExecutionFiles() class method
    
    func testFromExecutionFilesWithValidFiles() throws {
        /// Should parse and calculate costs from valid execution files
        let tempDir = FileManager.default.temporaryDirectory
        let mainFile = tempDir.appendingPathComponent("main_\(UUID()).json")
        let summaryFile = tempDir.appendingPathComponent("summary_\(UUID()).json")
        
        // Files with modelUsage so calculated_cost works
        // 1M input tokens at Haiku rate $0.25/MTok = $0.25
        let mainContent = [
            "total_cost_usd": 1.5,  // File cost (ignored)
            "modelUsage": [
                "claude-3-haiku-20240307": [
                    "inputTokens": 1_000_000
                ]
            ]
        ] as [String: Any]
        
        // 500k input tokens at Haiku rate = $0.125
        let summaryContent = [
            "total_cost_usd": 0.5,  // File cost (ignored)
            "modelUsage": [
                "claude-3-haiku-20240307": [
                    "inputTokens": 500_000
                ]
            ]
        ] as [String: Any]
        
        let mainData = try JSONSerialization.data(withJSONObject: mainContent)
        try mainData.write(to: mainFile)
        
        let summaryData = try JSONSerialization.data(withJSONObject: summaryContent)
        try summaryData.write(to: summaryFile)
        
        defer {
            try? FileManager.default.removeItem(at: mainFile)
            try? FileManager.default.removeItem(at: summaryFile)
        }
        
        // Act
        let breakdown = try CostBreakdown.fromExecutionFiles(
            mainExecutionFile: mainFile.path,
            summaryExecutionFile: summaryFile.path
        )
        
        // Assert - uses calculated_cost, not file's total_cost_usd
        XCTAssertEqual(breakdown.mainCost, 0.25, accuracy: 0.001)
        XCTAssertEqual(breakdown.summaryCost, 0.125, accuracy: 0.001)
        XCTAssertEqual(breakdown.totalCost, 0.375, accuracy: 0.001)
    }
    
    func testFromExecutionFilesRaisesOnMissingFiles() {
        /// Should raise FileNotFoundError when files don't exist
        XCTAssertThrowsError(try CostBreakdown.fromExecutionFiles(
            mainExecutionFile: "/nonexistent/main.json",
            summaryExecutionFile: "/nonexistent/summary.json"
        )) { error in
            XCTAssertTrue(error is FileNotFoundError)
        }
    }
    
    func testFromExecutionFilesRaisesOnEmptyPaths() {
        /// Should raise error for empty file paths
        XCTAssertThrowsError(try CostBreakdown.fromExecutionFiles(
            mainExecutionFile: "",
            summaryExecutionFile: ""
        )) { error in
            XCTAssertTrue(error is ConfigurationError)
            if let configError = error as? ConfigurationError {
                XCTAssertTrue(configError.message.contains("cannot be empty"))
            }
        }
    }
    
    func testFromExecutionFilesWithListFormat() throws {
        /// Should handle execution files with list format (multiple executions)
        let tempDir = FileManager.default.temporaryDirectory
        let mainFile = tempDir.appendingPathComponent("main_\(UUID()).json")
        let summaryFile = tempDir.appendingPathComponent("summary_\(UUID()).json")
        
        // List with multiple entries - should use the last one with cost
        let mainContent: [Any] = [
            [
                "total_cost_usd": 0.5,
                "modelUsage": [
                    "claude-3-haiku-20240307": ["inputTokens": 100_000]
                ]
            ],
            [
                "total_cost_usd": 1.5,  // Last one with cost is used
                "modelUsage": [
                    "claude-3-haiku-20240307": ["inputTokens": 1_000_000]  // $0.25
                ]
            ]
        ]
        
        let summaryContent: [Any] = [
            [
                "total_cost_usd": 0.3,
                "modelUsage": [
                    "claude-3-haiku-20240307": ["inputTokens": 100_000]
                ]
            ],
            [
                "total_cost_usd": 0.7,  // Last one with cost is used
                "modelUsage": [
                    "claude-3-haiku-20240307": ["inputTokens": 400_000]  // $0.10
                ]
            ]
        ]
        
        let mainData = try JSONSerialization.data(withJSONObject: mainContent)
        try mainData.write(to: mainFile)
        
        let summaryData = try JSONSerialization.data(withJSONObject: summaryContent)
        try summaryData.write(to: summaryFile)
        
        defer {
            try? FileManager.default.removeItem(at: mainFile)
            try? FileManager.default.removeItem(at: summaryFile)
        }
        
        // Act
        let breakdown = try CostBreakdown.fromExecutionFiles(
            mainExecutionFile: mainFile.path,
            summaryExecutionFile: summaryFile.path
        )
        
        // Assert - uses calculated_cost from modelUsage
        XCTAssertEqual(breakdown.mainCost, 0.25, accuracy: 0.001)
        XCTAssertEqual(breakdown.summaryCost, 0.10, accuracy: 0.001)
    }
}

final class TestModelUsage: XCTestCase {
    /// Test suite for ModelUsage struct
    
    func testCreateModelUsage() {
        /// Should be able to create ModelUsage instance
        let usage = ModelUsage(
            model: "claude-haiku",
            cost: 0.5,
            inputTokens: 100,
            outputTokens: 50,
            cacheReadTokens: 200,
            cacheWriteTokens: 30
        )
        
        XCTAssertEqual(usage.model, "claude-haiku")
        XCTAssertEqual(usage.cost, 0.5)
        XCTAssertEqual(usage.inputTokens, 100)
        XCTAssertEqual(usage.outputTokens, 50)
        XCTAssertEqual(usage.cacheReadTokens, 200)
        XCTAssertEqual(usage.cacheWriteTokens, 30)
    }
    
    func testModelUsageTotalTokens() {
        /// Should calculate total tokens correctly
        let usage = ModelUsage(
            model: "claude-haiku",
            inputTokens: 100,
            outputTokens: 50,
            cacheReadTokens: 200,
            cacheWriteTokens: 30
        )
        
        let total = usage.totalTokens
        
        XCTAssertEqual(total, 380)
    }
    
    func testModelUsageFromDict() throws {
        /// Should parse model usage from dict
        let data: [String: Any] = [
            "inputTokens": 4271,
            "outputTokens": 389,
            "cacheReadInputTokens": 90755,
            "cacheCreationInputTokens": 12299,
            "costUSD": 0.02158975
        ]
        
        let usage = try ModelUsage.fromDict(model: "claude-haiku-4-5", data: data)
        
        XCTAssertEqual(usage.model, "claude-haiku-4-5")
        XCTAssertEqual(usage.cost, 0.02158975, accuracy: 0.000001)
        XCTAssertEqual(usage.inputTokens, 4271)
        XCTAssertEqual(usage.outputTokens, 389)
        XCTAssertEqual(usage.cacheReadTokens, 90755)
        XCTAssertEqual(usage.cacheWriteTokens, 12299)
    }
    
    func testModelUsageFromDictHandlesMissingFields() throws {
        /// Should handle missing fields in dict
        let data: [String: Any] = ["inputTokens": 100]
        
        let usage = try ModelUsage.fromDict(model: "claude-haiku", data: data)
        
        XCTAssertEqual(usage.inputTokens, 100)
        XCTAssertEqual(usage.outputTokens, 0)
        XCTAssertEqual(usage.cacheReadTokens, 0)
        XCTAssertEqual(usage.cacheWriteTokens, 0)
        XCTAssertEqual(usage.cost, 0.0)
    }
    
    func testModelUsageFromDictHandlesNullValues() throws {
        /// Should handle null/nil values in dict
        let data: [String: Any?] = [
            "inputTokens": nil,
            "outputTokens": 50,
            "costUSD": nil
        ]
        
        let usage = try ModelUsage.fromDict(model: "claude-haiku", data: data as [String: Any])
        
        XCTAssertEqual(usage.inputTokens, 0)
        XCTAssertEqual(usage.outputTokens, 50)
        XCTAssertEqual(usage.cost, 0.0)
    }
}

final class TestExecutionUsage: XCTestCase {
    /// Test suite for ExecutionUsage
    
    func testCreateExecutionUsage() {
        /// Should be able to create ExecutionUsage instance
        let models = [
            ModelUsage(model: "haiku", cost: 0.5),
            ModelUsage(model: "sonnet", cost: 1.2)
        ]
        let usage = ExecutionUsage(models: models, totalCostUSD: 1.7)
        
        XCTAssertEqual(usage.models.count, 2)
        XCTAssertEqual(usage.totalCostUSD, 1.7)
        XCTAssertEqual(usage.cost, 1.7)  // cost property uses totalCostUSD
    }
    
    func testCalculatedCost() {
        /// Should calculate cost using model pricing
        let models = [
            ModelUsage(model: "claude-3-haiku", inputTokens: 1_000_000),  // $0.25
            ModelUsage(model: "claude-3-haiku", outputTokens: 100_000)    // $0.125
        ]
        let usage = ExecutionUsage(models: models, totalCostUSD: 999.0)  // Ignored
        
        let calculatedCost = usage.calculatedCost
        
        XCTAssertEqual(calculatedCost, 0.375, accuracy: 0.001)
    }
    
    func testTokenCountAggregation() {
        /// Should aggregate token counts across models
        let models = [
            ModelUsage(
                model: "haiku",
                inputTokens: 100,
                outputTokens: 50,
                cacheReadTokens: 200,
                cacheWriteTokens: 30
            ),
            ModelUsage(
                model: "sonnet",
                inputTokens: 200,
                outputTokens: 100,
                cacheReadTokens: 300,
                cacheWriteTokens: 50
            )
        ]
        let usage = ExecutionUsage(models: models)
        
        XCTAssertEqual(usage.inputTokens, 300)
        XCTAssertEqual(usage.outputTokens, 150)
        XCTAssertEqual(usage.cacheReadTokens, 500)
        XCTAssertEqual(usage.cacheWriteTokens, 80)
        XCTAssertEqual(usage.totalTokens, 1030)
    }
    
    func testExecutionUsageAddition() {
        /// Should combine two ExecutionUsage instances
        let usage1 = ExecutionUsage(
            models: [ModelUsage(model: "haiku", cost: 0.5)],
            totalCostUSD: 1.0
        )
        let usage2 = ExecutionUsage(
            models: [ModelUsage(model: "sonnet", cost: 1.2)],
            totalCostUSD: 2.0
        )
        
        let combined = usage1 + usage2
        
        XCTAssertEqual(combined.models.count, 2)
        XCTAssertEqual(combined.totalCostUSD, 3.0)
    }
}

final class TestClaudeModels: XCTestCase {
    /// Test suite for Claude model pricing
    
    func testGetModelForKnownModels() throws {
        /// Should find model configurations for known model names
        let testCases = [
            ("claude-3-haiku-20240307", "claude-3-haiku"),
            ("claude-haiku-4-5", "claude-haiku-4"),
            ("claude-3-5-sonnet-20241022", "claude-3-5-sonnet"),
            ("claude-sonnet-4-6", "claude-sonnet-4"),
            ("claude-opus-4-6", "claude-opus-4")
        ]
        
        for (modelName, expectedPattern) in testCases {
            let model = try getModel(modelName)
            XCTAssertEqual(model.pattern, expectedPattern)
        }
    }
    
    func testGetModelForUnknownModel() {
        /// Should raise UnknownModelError for unrecognized models
        XCTAssertThrowsError(try getModel("unknown-model")) { error in
            XCTAssertTrue(error is UnknownModelError)
        }
    }
    
    func testGetRateForModel() throws {
        /// Should return correct input rate for model
        let rate = try getRateForModel("claude-3-haiku-20240307")
        
        XCTAssertEqual(rate, 0.25)
    }
    
    func testClaudeModelCalculateCost() {
        /// Should calculate cost correctly for given token counts
        let model = ClaudeModel(
            pattern: "test-model",
            inputRate: 1.0,
            outputRate: 2.0,
            cacheWriteRate: 1.5,
            cacheReadRate: 0.1
        )
        
        let cost = model.calculateCost(
            inputTokens: 1_000_000,    // 1.0 * 1 = $1.0
            outputTokens: 500_000,     // 2.0 * 0.5 = $1.0
            cacheWriteTokens: 200_000, // 1.5 * 0.2 = $0.3
            cacheReadTokens: 1_000_000 // 0.1 * 1 = $0.1
        )
        
        XCTAssertEqual(cost, 2.4, accuracy: 0.001)
    }
}

final class TestCostBreakdownSerialization: XCTestCase {
    /// Test suite for JSON serialization/deserialization
    
    func testToJSON() throws {
        /// Should serialize to JSON correctly
        let breakdown = CostBreakdown(
            mainCost: 1.5,
            summaryCost: 0.5,
            inputTokens: 1000,
            outputTokens: 500,
            cacheReadTokens: 200,
            cacheWriteTokens: 100
        )
        
        let json = try breakdown.toJSON()
        
        XCTAssertTrue(json.contains("\"main_cost\":1.5"))
        XCTAssertTrue(json.contains("\"summary_cost\":0.5"))
        XCTAssertTrue(json.contains("\"input_tokens\":1000"))
        XCTAssertTrue(json.contains("\"output_tokens\":500"))
    }
    
    func testFromJSON() throws {
        /// Should deserialize from JSON correctly
        let json = """
        {
            "main_cost": 1.5,
            "summary_cost": 0.5,
            "input_tokens": 1000,
            "output_tokens": 500,
            "cache_read_tokens": 200,
            "cache_write_tokens": 100,
            "models": []
        }
        """
        
        let breakdown = try CostBreakdown.fromJSON(json)
        
        XCTAssertEqual(breakdown.mainCost, 1.5)
        XCTAssertEqual(breakdown.summaryCost, 0.5)
        XCTAssertEqual(breakdown.inputTokens, 1000)
        XCTAssertEqual(breakdown.outputTokens, 500)
        XCTAssertEqual(breakdown.cacheReadTokens, 200)
        XCTAssertEqual(breakdown.cacheWriteTokens, 100)
    }
    
    func testRoundTripSerialization() throws {
        /// Should maintain data integrity through serialize/deserialize cycle
        let original = CostBreakdown(
            mainCost: 1.234,
            summaryCost: 0.567,
            inputTokens: 1000,
            outputTokens: 500,
            cacheReadTokens: 200,
            cacheWriteTokens: 100
        )
        
        let json = try original.toJSON()
        let restored = try CostBreakdown.fromJSON(json)
        
        XCTAssertEqual(restored.mainCost, original.mainCost)
        XCTAssertEqual(restored.summaryCost, original.summaryCost)
        XCTAssertEqual(restored.inputTokens, original.inputTokens)
        XCTAssertEqual(restored.outputTokens, original.outputTokens)
        XCTAssertEqual(restored.cacheReadTokens, original.cacheReadTokens)
        XCTAssertEqual(restored.cacheWriteTokens, original.cacheWriteTokens)
    }
}

final class TestCostBreakdownUtilities: XCTestCase {
    /// Test suite for utility methods
    
    func testTotalTokensCalculation() {
        /// Should calculate total tokens correctly
        let breakdown = CostBreakdown(
            mainCost: 0.0,
            summaryCost: 0.0,
            inputTokens: 1000,
            outputTokens: 500,
            cacheReadTokens: 200,
            cacheWriteTokens: 100
        )
        
        XCTAssertEqual(breakdown.totalTokens, 1800)
    }
    
    func testGetAggregatedModels() {
        /// Should aggregate models with same names
        let mainModels = [
            ModelUsage(model: "claude-haiku", inputTokens: 100, outputTokens: 50),
            ModelUsage(model: "claude-sonnet", inputTokens: 200, outputTokens: 100)
        ]
        let summaryModels = [
            ModelUsage(model: "claude-haiku", inputTokens: 50, outputTokens: 25),  // Same model
            ModelUsage(model: "claude-opus", inputTokens: 300, outputTokens: 150)
        ]
        
        let breakdown = CostBreakdown(
            mainCost: 0.0,
            summaryCost: 0.0,
            mainModels: mainModels,
            summaryModels: summaryModels
        )
        
        let aggregated = breakdown.getAggregatedModels()
        
        XCTAssertEqual(aggregated.count, 3)
        
        // Find the aggregated haiku model
        if let haikuModel = aggregated.first(where: { $0.model == "claude-haiku" }) {
            XCTAssertEqual(haikuModel.inputTokens, 150)  // 100 + 50
            XCTAssertEqual(haikuModel.outputTokens, 75)  // 50 + 25
        } else {
            XCTFail("Should have aggregated claude-haiku model")
        }
    }
    
    func testToModelBreakdownJSON() throws {
        /// Should convert to JSON format for model breakdown
        let models = [
            ModelUsage(model: "claude-3-haiku", cost: 0.25, inputTokens: 1_000_000)
        ]
        let breakdown = CostBreakdown(
            mainCost: 0.0,
            summaryCost: 0.0,
            mainModels: models
        )
        
        let json = breakdown.toModelBreakdownJSON()
        
        XCTAssertEqual(json.count, 1)
        let modelJson = json[0]
        XCTAssertEqual(modelJson["model"] as? String, "claude-3-haiku")
        XCTAssertEqual(modelJson["input_tokens"] as? Int, 1_000_000)
    }
}