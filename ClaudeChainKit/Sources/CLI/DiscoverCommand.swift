import ArgumentParser
import Foundation

public struct DiscoverCommand: ParsableCommand {
    public static let configuration = CommandConfiguration(
        commandName: "discover",
        abstract: "Discover all projects in the repository"
    )
    
    public init() {}
    
    public func run() throws {
        print("🔍 Discovering projects...")
        
        // Simple project discovery - look for directories with spec.md files
        let fileManager = FileManager.default
        let currentPath = fileManager.currentDirectoryPath
        
        var projects: [String] = []
        
        if let enumerator = fileManager.enumerator(atPath: currentPath) {
            while let file = enumerator.nextObject() as? String {
                if file.hasSuffix("spec.md") && !file.contains(".git") {
                    let projectPath = URL(fileURLWithPath: file).deletingLastPathComponent().path
                    if !projectPath.isEmpty && projectPath != "." {
                        let projectName = URL(fileURLWithPath: projectPath).lastPathComponent
                        if !projects.contains(projectName) {
                            projects.append(projectName)
                        }
                    }
                }
            }
        }
        
        projects.sort()
        
        print("Found \(projects.count) project(s):")
        for project in projects {
            print("  - \(project)")
        }
        
        // Output JSON for GitHub Actions
        let projectsJson: String
        if projects.isEmpty {
            projectsJson = "[]"
        } else {
            let jsonData = try JSONSerialization.data(withJSONObject: projects, options: [])
            projectsJson = String(data: jsonData, encoding: .utf8) ?? "[]"
        }
        
        print("\nProjects JSON: \(projectsJson)")
    }
}