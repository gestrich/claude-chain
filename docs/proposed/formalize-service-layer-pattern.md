# Formalize Service Layer Pattern

## Background

ClaudeStep currently has a well-organized layered architecture but lacks formal documentation of its architectural pattern. After analysis, the codebase closely aligns with Martin Fowler's **Service Layer pattern** from "Patterns of Enterprise Application Architecture" (2002).

### What is Service Layer?

From Fowler's catalog (https://martinfowler.com/eaaCatalog/serviceLayer.html):

> "Defines an application's boundary with a layer of services that establishes a set of available operations and coordinates the application's response in each operation."

The Service Layer pattern:
- **Encapsulates business logic** in service classes
- **Coordinates operations** across domain and infrastructure layers
- **Provides a unified API** for different client types (CLI, API, etc.)
- **Manages transactions** and orchestrates responses

### Current State

ClaudeStep already follows Service Layer principles:
- Service classes exist: `TaskManagementService`, `ReviewerManagementService`, `MetadataService`
- Some functionality still uses standalone functions instead of services
- Folder structure is close but not aligned with Fowler's organization
- No architectural documentation mentioning Service Layer

### User Requirements

1. **Lightweight approach** - No strict letter-of-the-law adherence, just rough alignment
2. **Folder reorganization** - Align with Service Layer structure (though Fowler doesn't prescribe specific folder names)
3. **Documentation** - Mention Martin Fowler's design in architecture docs
4. **Maintain simplicity** - Don't over-engineer for the sake of pattern compliance

### Goals

1. Document that ClaudeStep follows Service Layer pattern (referencing Fowler)
2. Convert remaining standalone functions to service classes for consistency
3. Reorganize folders to better reflect Service Layer responsibilities
4. Keep the architecture lightweight and pragmatic

## Phases

- [ ] Phase 1: Document Service Layer Pattern

**Purpose:** Update architecture documentation to formalize Service Layer as the official pattern.

**Tasks:**
1. Update `docs/architecture/architecture.md`:
   - Add new section: "Service Layer Pattern (Martin Fowler)"
   - Reference Fowler's PoEAA and the catalog URL
   - Explain how ClaudeStep implements Service Layer
   - Document the lightweight approach (pragmatic, not dogmatic)
   - Keep existing content about Python-first approach and layered structure

2. Add subsection explaining layer responsibilities:
   - **CLI Layer** - Thin orchestration, instantiates services
   - **Service Layer** - Business logic, coordinates domain and infrastructure
   - **Domain Layer** - Models, configuration, exceptions
   - **Infrastructure Layer** - External system integrations (Git, GitHub, filesystem)

3. Document service class conventions:
   - Services are classes with `__init__` taking dependencies
   - Services encapsulate related business operations
   - Services can depend on other services and infrastructure
   - Commands orchestrate services, don't implement business logic

**Files to modify:**
- `docs/architecture/architecture.md`

**Expected outcome:**
- Clear documentation that ClaudeStep follows Service Layer pattern
- Reference to Martin Fowler's work
- Developers understand the architectural approach

---

- [ ] Phase 2: Convert Standalone Functions to Services

**Purpose:** Standardize on service classes for all business logic (currently a mix of classes and functions).

**Current standalone functions to convert:**

1. **`application/services/project_detection.py`**
   - Functions: `detect_project_from_pr()`, `detect_project_paths()`
   - Convert to: `ProjectService` class

2. **`application/services/pr_operations.py`**
   - Functions: `format_branch_name()`, `parse_branch_name()`, `get_project_prs()`
   - Convert to: `PRService` class

**Implementation approach:**
```python
# Example: project_detection.py → ProjectService
class ProjectService:
    def __init__(self, repo: str):
        self.repo = repo

    def detect_from_pr(self, pr_number: str) -> Optional[str]:
        # Move detect_project_from_pr logic here
        pass

    def get_project_paths(self, project_name: str) -> Tuple[str, str, str, str]:
        # Move detect_project_paths logic here
        pass
```

**Tasks:**
1. Create `ProjectService` in `application/services/project_detection.py`
2. Create `PRService` in `application/services/pr_operations.py`
3. Update all CLI commands to instantiate and use these services
4. Update tests to test service classes instead of standalone functions
5. Keep backward compatibility during transition (optional: add deprecation notices)

**Files to modify:**
- `src/claudestep/application/services/project_detection.py`
- `src/claudestep/application/services/pr_operations.py`
- `src/claudestep/cli/commands/prepare.py`
- `src/claudestep/cli/commands/finalize.py`
- `src/claudestep/cli/commands/discover.py`
- All relevant test files

**Expected outcome:**
- All business logic in service classes
- No standalone business logic functions
- Consistent pattern across codebase

---

- [ ] Phase 3: Reorganize Folder Structure (Optional/Lightweight)

**Purpose:** Align folder structure with Service Layer responsibilities while keeping changes minimal.

**Note:** Fowler's Service Layer pattern doesn't prescribe specific folder names like "Interface/Service/Domain/Data". The user mentioned these but they're from other architectural patterns. We'll keep ClaudeStep's current structure which already reflects Service Layer well.

**Current structure (already good):**
```
src/claudestep/
├── domain/              # Domain models, config, exceptions
├── infrastructure/      # External system integrations
│   ├── git/
│   ├── github/
│   ├── filesystem/
│   └── metadata/
├── application/         # Service Layer
│   ├── services/       # Business logic services
│   └── formatters/     # Output formatting
└── cli/                # Presentation layer
    └── commands/
```

**Proposed minimal changes (if desired):**

Option A - No changes needed (RECOMMENDED):
- Current structure already reflects Service Layer well
- `application/services/` clearly houses the Service Layer
- No reorganization needed, just document current structure

Option B - Rename for clarity (optional):
- Rename `application/` → `service/` to be more explicit
- Keep subdirectories: `service/services/`, `service/formatters/`
- Update all imports

**Recommendation:** Stick with current structure (Option A). It already works well and renaming would require updating many imports for minimal benefit.

**Expected outcome:**
- If Option A: Document current structure as Service Layer implementation
- If Option B: Folder names explicitly show Service Layer

---

- [ ] Phase 4: Update Testing Documentation

**Purpose:** Ensure testing docs reflect Service Layer pattern terminology.

**Tasks:**
1. Update `docs/architecture/tests.md`:
   - Change "Application Layer tests" → "Service Layer tests"
   - Explain testing services (mock infrastructure, test business logic)
   - Update examples to show service class testing patterns

2. Update `docs/architecture/testing-guide.md`:
   - Reference Service Layer pattern in context
   - Show service instantiation in test examples
   - Document mocking service dependencies

**Files to modify:**
- `docs/architecture/tests.md`
- `docs/architecture/testing-guide.md`

**Expected outcome:**
- Testing docs use Service Layer terminology
- Clear guidance on testing service classes

---

- [ ] Phase 5: Add Architectural Decision Record (ADR)

**Purpose:** Document why we chose Service Layer pattern and how it guides future development.

**Tasks:**
1. Create `docs/architecture/decisions/001-service-layer-pattern.md`:
   - **Status**: Accepted
   - **Context**: Need consistent architectural pattern for business logic
   - **Decision**: Adopt Service Layer pattern (Martin Fowler, PoEAA)
   - **Consequences**:
     - All business logic in service classes
     - CLI commands orchestrate services
     - Infrastructure stays lightweight (no complex abstractions)
     - Pragmatic approach (not dogmatic adherence)
   - **References**: Link to Fowler's catalog

2. Update `docs/architecture/architecture.md` to reference ADR

**Files to create:**
- `docs/architecture/decisions/001-service-layer-pattern.md`

**Files to modify:**
- `docs/architecture/architecture.md`

**Expected outcome:**
- Clear record of architectural decision
- Guidance for future development
- Reference point for code reviews

---

- [ ] Phase 6: Update Code Comments and Docstrings

**Purpose:** Align code-level documentation with Service Layer pattern.

**Tasks:**
1. Update service class docstrings to mention Service Layer:
   ```python
   class TaskManagementService:
       """Service Layer class for task management operations.

       Follows Service Layer pattern (Fowler, PoEAA) - encapsulates
       business logic for task finding, marking, and tracking.
       """
   ```

2. Update CLI command docstrings to clarify orchestration role:
   ```python
   def cmd_prepare(args, gh):
       """Orchestrate preparation workflow using Service Layer classes.

       This command instantiates services and coordinates their
       operations but does not implement business logic directly.
       """
   ```

3. Add module-level docstrings where missing explaining layer role

**Files to modify:**
- All service class files in `application/services/`
- All command files in `cli/commands/`

**Expected outcome:**
- Code documentation reflects Service Layer pattern
- Clear service responsibilities in docstrings

---

- [ ] Phase 7: Validation

**Purpose:** Ensure all changes maintain functionality and improve code consistency.

**Validation approach:**

1. **Run unit tests:**
   ```bash
   PYTHONPATH=src:scripts pytest tests/unit/ -v
   ```
   - All tests should pass
   - Service class tests should cover business logic

2. **Run integration tests:**
   ```bash
   PYTHONPATH=src:scripts pytest tests/integration/ -v
   ```
   - Command orchestration tests should pass
   - Services should work together correctly

3. **Coverage check:**
   ```bash
   PYTHONPATH=src:scripts pytest tests/unit/ tests/integration/ --cov=src/claudestep --cov-report=term-missing
   ```
   - Maintain 85%+ coverage
   - New service classes should be tested

4. **Manual review:**
   - Review architecture.md for clarity and accuracy
   - Verify ADR explains decision rationale
   - Check that docstrings are consistent

5. **Code structure verification:**
   - All business logic in service classes (no standalone functions)
   - CLI commands are thin orchestrators
   - Infrastructure layer unchanged

**Success criteria:**
- All tests pass (493+ tests)
- Coverage remains ≥85%
- Architecture docs clearly explain Service Layer
- Service classes are consistent pattern
- Code is more maintainable (not more complex)

**Expected outcome:**
- Confidence that formalization improves codebase
- No functionality regressions
- Clear architectural direction for future work
