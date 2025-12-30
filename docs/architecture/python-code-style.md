# Python Code Style Guide

## Service Layer Organization

This document describes the organizational principles and patterns used for Python code in the ClaudeStep project, particularly for service classes.

## Method Organization Principles

All service classes follow a consistent organization pattern to improve readability and maintainability:

### 1. Public Before Private

Public methods (part of the API) appear before private/internal methods (prefixed with `_`). This allows developers to understand the public API of each service at a glance without scrolling through implementation details.

### 2. High-Level Before Low-Level

More abstract, higher-level operations come before detailed implementation helpers. This creates a natural reading flow from "what the service does" to "how it does it."

### 3. Logical Grouping

Related methods are grouped together with clear section comments. This helps developers quickly navigate to the functionality they need.

### 4. Standard Order

Methods follow this ordering:
1. Special methods (`__init__`, `__str__`, etc.)
2. Class methods (`@classmethod`)
3. Static methods (`@staticmethod`)
4. Instance methods (public, then private)

## Section Headers

Use clear section comments to separate different types of methods:

```python
class MyService:
    def __init__(self):
        """Constructor always comes first."""
        pass

    # Public API methods
    def high_level_operation(self):
        """Main public methods in order of abstraction level."""
        pass

    def mid_level_operation(self):
        """Supporting public methods."""
        pass

    # Static utility methods
    @staticmethod
    def utility_function():
        """Static utilities at the end."""
        pass

    # Private helper methods
    def _internal_helper(self):
        """Private implementation details last."""
        pass
```

For services with many methods, use more descriptive section headers with separators:

```python
class ComplexService:
    def __init__(self):
        pass

    # ============================================================
    # Core CRUD Operations
    # ============================================================

    def create_resource(self):
        pass

    def get_resource(self):
        pass

    # ============================================================
    # Query Operations
    # ============================================================

    def find_resources(self):
        pass

    # ============================================================
    # Utility Operations
    # ============================================================

    @staticmethod
    def parse_identifier(text: str):
        pass
```

## Environment Variables and Configuration

### Principle: Services Should Not Read Environment Variables

Service classes and their methods should **never** read environment variables directly using `os.environ.get()`. All environment variable access should happen at the **entry point layer** (CLI commands, web handlers, etc.) and be passed explicitly as constructor or method parameters.

### Anti-Pattern (❌ Avoid)

```python
# BAD: Service reads environment variables directly
class StatisticsService:
    def __init__(self, repo: str, metadata_service: MetadataService):
        self.repo = repo
        self.metadata_service = metadata_service

    def collect_all_statistics(self, config_path: Optional[str] = None):
        # ❌ Hidden dependency on environment
        base_branch = os.environ.get("BASE_BRANCH", "main")
        label = "claudestep"
        # ... rest of implementation
```

**Problems with this approach:**
- **Hidden dependencies**: Not obvious from the API what environment variables are needed
- **Poor testability**: Tests must mock environment variables
- **Tight coupling**: Service is coupled to the deployment environment
- **Hard to reuse**: Can't easily use the service in different contexts
- **Inconsistent**: Mixes explicit parameters with implicit environment access

### Recommended Pattern (✅ Use This)

```python
# GOOD: Service receives all configuration explicitly
class StatisticsService:
    def __init__(
        self,
        repo: str,
        metadata_service: MetadataService,
        base_branch: str = "main"
    ):
        """Initialize the statistics service

        Args:
            repo: GitHub repository (owner/name)
            metadata_service: MetadataService instance for accessing metadata
            base_branch: Base branch to fetch specs from (default: "main")
        """
        self.repo = repo
        self.metadata_service = metadata_service
        self.base_branch = base_branch  # ✅ Stored as instance variable

    def collect_all_statistics(
        self,
        config_path: Optional[str] = None,
        label: str = "claudestep"
    ):
        """Collect statistics for all projects

        Args:
            config_path: Optional path to specific config
            label: GitHub label for filtering (default: "claudestep")
        """
        # ✅ Uses instance variables, no environment access
        base_branch = self.base_branch
        # ... rest of implementation
```

**Adapter layer in `__main__.py` handles ALL environment variable reading:**

```python
# In __main__.py - Adapter layer reads environment variables and CLI args
elif args.command == "statistics":
    return cmd_statistics(
        gh=gh,
        repo=args.repo or os.environ.get("GITHUB_REPOSITORY", ""),
        base_branch=args.base_branch or os.environ.get("BASE_BRANCH", "main"),
        config_path=args.config_path or os.environ.get("CONFIG_PATH"),
        days_back=args.days_back or int(os.environ.get("STATS_DAYS_BACK", "30")),
        format_type=args.format or os.environ.get("STATS_FORMAT", "slack"),
        slack_webhook_url=os.environ.get("SLACK_WEBHOOK_URL", "")
    )

# In cli/commands/statistics.py - Command receives explicit parameters
def cmd_statistics(
    gh: GitHubActionsHelper,
    repo: str,
    base_branch: str = "main",
    config_path: Optional[str] = None,
    days_back: int = 30,
    format_type: str = "slack",
    slack_webhook_url: str = ""
) -> int:
    """Orchestrate statistics workflow."""
    # ✅ Passes everything explicitly to service
    metadata_store = GitHubMetadataStore(repo)
    metadata_service = MetadataService(metadata_store)
    statistics_service = StatisticsService(repo, metadata_service, base_branch)

    # ✅ Uses parameters directly - no environment access
    report = statistics_service.collect_all_statistics(
        config_path=config_path if config_path else None
    )
```

### Benefits

✅ **Explicit dependencies**: Constructor signature shows exactly what the service needs

✅ **Easy testing**: Just pass test values - no environment mocking needed
```python
# Testing is straightforward
service = StatisticsService("owner/repo", mock_metadata, base_branch="develop")
```

✅ **Separation of concerns**: CLI handles environment, service handles business logic

✅ **Reusability**: Service works in any context (CLI, web app, scripts, tests)

✅ **Type safety**: IDEs can autocomplete and type-check parameters

✅ **Self-documenting**: API clearly shows what configuration is needed

### When to Use Constructor vs Method Parameters

**Use constructor parameters for:**
- Configuration that applies to all operations (e.g., `repo`, `base_branch`)
- Dependencies/services that won't change (e.g., `metadata_service`)
- Settings that define the service's behavior globally

**Use method parameters for:**
- Operation-specific values that vary per call (e.g., `config_path`, `days_back`)
- Optional filters or constraints (e.g., `label`)
- Values that might differ between invocations

### Exception: Environment Variables in Infrastructure Layer

The **only** layer that should read environment variables is the **infrastructure layer** - specifically for connecting to external systems:

```python
# OK: Infrastructure layer for GitHub API connections
class GitHubMetadataStore:
    def __init__(self, repo: str, token: Optional[str] = None):
        self.repo = repo
        # ✅ OK here: Infrastructure layer connecting to external system
        self.token = token or os.environ.get("GITHUB_TOKEN")
```

Even here, prefer explicit parameters with environment variables as fallback defaults.

## CLI Command Pattern

### Principle: Commands Use Explicit Parameters, Not Environment Variables

CLI command functions should receive explicit parameters and never read environment variables directly. The adapter layer in `__main__.py` is responsible for translating CLI arguments and environment variables into parameters.

### Architecture Layers

```
GitHub Actions (env vars) → __main__.py (adapter) → commands (params) → services (params)
```

Only `__main__.py` reads environment variables in the CLI layer.

### Anti-Pattern (❌ Avoid)

```python
# BAD: Command reads environment variables
def cmd_statistics(args: argparse.Namespace, gh: GitHubActionsHelper) -> int:
    repo = os.environ.get("GITHUB_REPOSITORY", "")  # Don't do this!
    config_path = args.config_path  # Mixing args and env is confusing
```

**Problems:**
- Hidden dependencies on environment variables
- Awkward local usage (must set env vars)
- Poor type safety with Namespace
- Harder to test

### Recommended Pattern (✅ Use This)

```python
# In cli/parser.py
parser_statistics.add_argument("--repo", help="GitHub repository (owner/name)")
parser_statistics.add_argument("--config-path", help="Path to configuration file")
parser_statistics.add_argument("--days-back", type=int, default=30)

# In cli/commands/statistics.py - Pure function with explicit parameters
def cmd_statistics(
    gh: GitHubActionsHelper,
    repo: str,
    config_path: Optional[str] = None,
    days_back: int = 30
) -> int:
    """Orchestrate statistics workflow.

    Args:
        gh: GitHub Actions helper instance
        repo: GitHub repository (owner/name)
        config_path: Optional path to configuration file
        days_back: Days to look back for statistics

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Use parameters directly - no environment access!
    metadata_store = GitHubMetadataStore(repo)
    ...

# In __main__.py - Adapter layer
elif args.command == "statistics":
    return cmd_statistics(
        gh=gh,
        repo=args.repo or os.environ.get("GITHUB_REPOSITORY", ""),
        config_path=args.config_path or os.environ.get("CONFIG_PATH"),
        days_back=args.days_back or int(os.environ.get("STATS_DAYS_BACK", "30"))
    )
```

**Benefits:**
- ✅ Explicit dependencies: Function signature shows exactly what's needed
- ✅ Type safety: IDEs can autocomplete and type-check
- ✅ Easy testing: Just pass parameters, no environment mocking
- ✅ Works for both GitHub Actions and local development
- ✅ Discoverable: `--help` shows all options

## Module-Level Code

For modules with functions rather than classes (like `artifact_operations_service.py`), use this order:

1. **Dataclasses and models** (public before private)
2. **Public API functions** (high-level to low-level)
3. **Module utilities** (helper functions used by the public API)
4. **Private helper functions** (prefixed with `_`)

Example:

```python
# Public models
@dataclass
class ProjectArtifact:
    """Public dataclass."""
    pass

# Public API functions
def find_artifacts():
    """Highest-level public function."""
    pass

def get_artifact_details():
    """Mid-level public function."""
    pass

# Module utilities
def parse_artifact_name(name: str):
    """Utility function."""
    pass

# Private helper functions
def _fetch_from_api():
    """Private implementation detail."""
    pass
```

## Benefits

This organizational approach provides:

- **Easier onboarding**: New developers can quickly understand what a service does by reading public methods first
- **Better maintainability**: Clear separation between public contracts and implementation details
- **Intuitive navigation**: Developers can find methods more quickly with consistent structure
- **Clearer API boundaries**: Public vs. private methods are visually distinct

## Examples

See the following services for reference implementations:

- [task_management_service.py](../../src/claudestep/application/services/task_management_service.py) - Simple service with public API and static utilities
- [metadata_service.py](../../src/claudestep/application/services/metadata_service.py) - Complex service with multiple logical sections
- [artifact_operations_service.py](../../src/claudestep/application/services/artifact_operations_service.py) - Module-level functions and dataclasses

## Domain Models and Data Parsing

### Principle: Parse Once Into Well-Formed Models

When working with structured data (YAML files, JSON responses, markdown files, etc.), **parse the data once into a well-formed domain model** rather than passing raw strings or dictionaries around and parsing them repeatedly.

### Anti-Pattern (❌ Avoid)

```python
# BAD: Services parse strings directly
class StatisticsService:
    def collect_project_stats(self, project_name: str):
        # String-based path construction
        config_path = f"claude-step/{project_name}/configuration.yml"
        spec_path = f"claude-step/{project_name}/spec.md"

        # Fetch raw strings from API
        config_content = get_file_from_branch(repo, branch, config_path)
        spec_content = get_file_from_branch(repo, branch, spec_path)

        # Parse YAML into raw dictionary
        config = yaml.safe_load(config_content)

        # String-based dictionary access (no type safety)
        reviewers_config = config.get("reviewers", [])
        reviewers = [r.get("username") for r in reviewers_config if "username" in r]

        # Regex parsing in service layer
        total = len(re.findall(r"^\s*- \[[xX \]]", spec_content, re.MULTILINE))
        completed = len(re.findall(r"^\s*- \[[xX]\]", spec_content, re.MULTILINE))

        # Return primitive types
        return (total, completed, reviewers)
```

**Problems with this approach:**
- **Parsing logic scattered**: Different services duplicate regex patterns and YAML parsing
- **No type safety**: Dictionary access with string keys can fail silently
- **Brittle**: Changes to file format require updates in multiple places
- **Wrong layer**: Business logic (parsing) mixed with orchestration (service layer)
- **Hard to test**: Must test parsing logic alongside business logic
- **Poor reusability**: Can't reuse parsing logic across services

### Recommended Pattern (✅ Use This)

```python
# GOOD: Domain models encapsulate parsing and provide type-safe APIs

# 1. Domain Model (domain/project.py)
@dataclass
class Project:
    """Domain model representing a ClaudeStep project"""
    name: str

    @property
    def config_path(self) -> str:
        """Centralized path construction"""
        return f"claude-step/{self.name}/configuration.yml"

    @property
    def spec_path(self) -> str:
        return f"claude-step/{self.name}/spec.md"

# 2. Configuration Model (domain/project_configuration.py)
@dataclass
class Reviewer:
    """Type-safe reviewer model"""
    username: str
    max_open_prs: int = 2

@dataclass
class ProjectConfiguration:
    """Parsed configuration with validation"""
    project: Project
    reviewers: List[Reviewer]

    @classmethod
    def from_yaml_string(cls, project: Project, content: str) -> 'ProjectConfiguration':
        """Parse once, validate, return type-safe model"""
        config = yaml.safe_load(content)

        # Validate structure
        if "reviewers" not in config:
            raise ConfigurationError("Missing reviewers field")

        # Parse into typed objects
        reviewers = [
            Reviewer(
                username=r["username"],
                max_open_prs=r.get("maxOpenPRs", 2)
            )
            for r in config["reviewers"]
            if "username" in r
        ]

        return cls(project=project, reviewers=reviewers)

    def get_reviewer_usernames(self) -> List[str]:
        """Type-safe API for common operations"""
        return [r.username for r in self.reviewers]

# 3. Spec Model (domain/spec_content.py)
@dataclass
class SpecTask:
    """Parsed task from spec.md"""
    index: int
    description: str
    is_completed: bool

class SpecContent:
    """Parsed spec.md with task extraction"""

    def __init__(self, project: Project, content: str):
        self.project = project
        self.content = content
        self._tasks: Optional[List[SpecTask]] = None

    @property
    def tasks(self) -> List[SpecTask]:
        """Parse once, cache results"""
        if self._tasks is None:
            self._tasks = self._parse_tasks()
        return self._tasks

    def _parse_tasks(self) -> List[SpecTask]:
        """Centralized regex parsing logic"""
        tasks = []
        task_index = 1

        for line in self.content.split('\n'):
            match = re.match(r'^\s*- \[([xX ])\]\s*(.+)$', line)
            if match:
                tasks.append(SpecTask(
                    index=task_index,
                    description=match.group(2).strip(),
                    is_completed=match.group(1).lower() == 'x'
                ))
                task_index += 1

        return tasks

    @property
    def total_tasks(self) -> int:
        """Clean API for statistics"""
        return len(self.tasks)

    @property
    def completed_tasks(self) -> int:
        return sum(1 for task in self.tasks if task.is_completed)

# 4. Repository Pattern (infrastructure/repositories/project_repository.py)
class ProjectRepository:
    """Infrastructure layer: Fetch and parse into domain models"""

    def __init__(self, repo: str):
        self.repo = repo

    def load_configuration(
        self, project: Project, branch: str = "main"
    ) -> Optional[ProjectConfiguration]:
        """Fetch from API, parse into domain model"""
        content = get_file_from_branch(self.repo, branch, project.config_path)
        if not content:
            return None

        return ProjectConfiguration.from_yaml_string(project, content)

    def load_spec(
        self, project: Project, branch: str = "main"
    ) -> Optional[SpecContent]:
        """Fetch from API, parse into domain model"""
        content = get_file_from_branch(self.repo, branch, project.spec_path)
        if not content:
            return None

        return SpecContent(project, content)

# 5. Service Layer (services/statistics_service.py)
class StatisticsService:
    """Service uses domain models - no parsing logic"""

    def __init__(
        self,
        repo: str,
        metadata_service: MetadataService,
        project_repository: ProjectRepository
    ):
        self.repo = repo
        self.metadata_service = metadata_service
        self.project_repository = project_repository

    def collect_project_stats(self, project_name: str) -> ProjectStats:
        """Clean, type-safe service logic"""
        project = Project(project_name)

        # Load parsed domain models
        config = self.project_repository.load_configuration(project)
        spec = self.project_repository.load_spec(project)

        if not config or not spec:
            return None

        # Use type-safe APIs (no parsing, no string keys)
        stats = ProjectStats(project_name)
        stats.total_tasks = spec.total_tasks
        stats.completed_tasks = spec.completed_tasks
        stats.reviewers = config.get_reviewer_usernames()

        return stats
```

### Benefits

✅ **Parse once**: Data is parsed into models at the boundary (repository/infrastructure layer)

✅ **Type safety**: Domain models provide strongly-typed properties and methods
```python
# Autocomplete works, typos caught at runtime
reviewers = config.reviewers  # List[Reviewer]
username = reviewers[0].username  # str (typed!)
```

✅ **Centralized parsing**: Regex patterns and parsing logic in one place
```python
# All spec parsing happens in SpecContent
# Services just use the clean API
total = spec.total_tasks
pending = spec.pending_tasks
```

✅ **Clear layering**:
- **Infrastructure**: Fetches raw data from external systems
- **Domain**: Parses into validated, type-safe models
- **Service**: Orchestrates domain models (no parsing!)

✅ **Testability**: Test parsing separately from business logic
```python
# Test parsing independently
def test_spec_content_parsing():
    spec = SpecContent(project, "- [ ] Task 1\n- [x] Task 2")
    assert spec.total_tasks == 2
    assert spec.completed_tasks == 1

# Test service with mocked domain models
def test_statistics_service():
    mock_spec = Mock(total_tasks=10, completed_tasks=5)
    mock_repo.load_spec.return_value = mock_spec
    # Test service logic without parsing concerns
```

✅ **Validation at boundaries**: Models validate on construction
```python
@classmethod
def from_yaml_string(cls, project: Project, content: str):
    config = yaml.safe_load(content)

    # Validate early, fail fast
    if "reviewers" not in config:
        raise ConfigurationError("Missing reviewers")

    return cls(...)
```

✅ **Reusability**: Models can be used across different services
```python
# Multiple services can use the same parsed models
class StatisticsService:
    def collect_stats(self, project: Project):
        config = self.repo.load_configuration(project)

class ReviewerService:
    def assign_reviewer(self, project: Project):
        config = self.repo.load_configuration(project)  # Same model!
```

### Architecture Pattern

```
┌─────────────────────────────────────────────────────────────┐
│ External System (GitHub API, File System)                   │
│ - Returns: Raw strings (YAML, JSON, Markdown)              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ Infrastructure Layer (Repository Pattern)                   │
│ - Fetches raw data from external systems                   │
│ - Delegates parsing to domain model factories              │
│ - Returns: Fully-parsed domain models                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ Domain Layer (Models with Factory Methods)                 │
│ - Project, ProjectConfiguration, SpecContent               │
│ - Encapsulates parsing logic (regex, YAML, validation)    │
│ - Provides type-safe APIs                                  │
│ - Single source of truth for data structure                │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ Service Layer (Business Logic)                             │
│ - Receives parsed domain models                            │
│ - Uses type-safe model APIs                                │
│ - No string parsing or dictionary access                   │
│ - Focuses on orchestration and business rules              │
└─────────────────────────────────────────────────────────────┘
```

### Key Principles

1. **Parse at boundaries**: Convert raw data to domain models as soon as it enters your system
2. **Parse once**: Never re-parse the same data in multiple places
3. **Domain owns parsing**: Parsing logic belongs in domain models, not services
4. **Type-safe APIs**: Models expose strongly-typed properties and methods
5. **Validate early**: Domain model constructors/factories validate structure
6. **No leaky abstractions**: Services don't know about YAML, regex, or file formats

### Related Patterns

This approach aligns with:
- **Repository Pattern**: Infrastructure fetches, domain parses
- **Factory Pattern**: `from_yaml_string()`, `from_branch_name()` constructors
- **Domain-Driven Design**: Rich domain models with behavior
- **Dependency Inversion**: Services depend on domain abstractions, not infrastructure

## Related Documentation

- See [docs/completed/reorganize-service-methods.md](../completed/reorganize-service-methods.md) for the history of applying these principles to the codebase
- See [docs/proposed/project-domain-model-refactoring.md](../proposed/project-domain-model-refactoring.md) for the plan to introduce Project, ProjectConfiguration, and SpecContent domain models
