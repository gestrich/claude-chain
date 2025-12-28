# Test Coverage Notes

This document explains intentionally untested code and coverage gaps in the ClaudeStep codebase.

**Overall Coverage: 85.03%** (1603 statements, 240 missed)
**Minimum Threshold: 70%**

## Intentionally Untested Code

The following modules have low or zero coverage by design:

### CLI Entry Points (0% coverage)

**`src/claudestep/__main__.py`** - 0% coverage (40 lines)
- **Reason:** CLI entry point that orchestrates the main workflow
- **Testing Strategy:** Tested via end-to-end integration tests in the demo repository
- **Why not unit tested:** This module primarily coordinates other components and relies on actual CLI invocation, which is better tested in integration tests
- **Location of tests:** `claude-step-demo/tests/integration/test_workflow_e2e.py`

**`src/claudestep/cli/parser.py`** - 0% coverage (14 lines)
- **Reason:** CLI argument parsing using argparse
- **Testing Strategy:** Tested via end-to-end integration tests in the demo repository
- **Why not unit tested:** Argparse behavior is well-tested by Python itself; our integration tests verify the complete CLI interface works correctly
- **Location of tests:** `claude-step-demo/tests/integration/test_workflow_e2e.py`

### Integration Logic (15% coverage)

**`src/claudestep/application/collectors/statistics_collector.py`** - 15.03% coverage (164/193 lines missed)
- **Reason:** Complex integration module that orchestrates multiple services
- **Testing Strategy:** Tested indirectly via CLI command tests
- **Why low coverage:** This module primarily coordinates calls to other services (task management, artifact operations, GitHub API). The individual services are well-tested, and the integration is verified via:
  - `tests/unit/cli/commands/test_statistics.py` (15 tests)
  - End-to-end integration tests
- **Uncovered lines:** Lines 32-33, 50-113, 129, 159-269, 286-322, 337-430
- **Note:** These are mostly integration glue code that calls well-tested service functions

## Minor Coverage Gaps (>90% coverage)

These modules have excellent coverage with small gaps that are difficult or not valuable to test:

### Near-Perfect Coverage (>95%)

- **`table_formatter.py`** - 98.44% (1 line missed: line 28)
  - Missing: Edge case in width calculation

- **`task_management.py`** - 97.44% (1 line missed: line 105)
  - Missing: Unreachable error path

- **`extract_cost.py`** - 96.43% (2 lines missed: lines 104-105)
  - Missing: Fallback error handling path

- **`finalize.py`** - 98.70% (2 lines missed: lines 165-166)
  - Missing: Default template path fallback (already tested via other paths)

- **`models.py`** - 98.35% (4 lines missed: lines 186, 267-268, 342)
  - Missing: String representation methods and property accessors

### Good Coverage (90-95%)

- **`artifact_operations.py`** - 92.98% (8 lines missed)
  - Missing lines: 97-98, 144-146, 213-215
  - Mostly error handling paths for rare edge cases

- **`pr_operations.py`** - 93.33% (2 lines missed: lines 63-64)
  - Missing: Error handling for malformed API responses

- **`filesystem/operations.py`** - 92.00% (2 lines missed: lines 75-76)
  - Missing: Permission error handling (difficult to test reliably)

## Coverage Improvement Opportunities

While not required (we exceed the 70% threshold), the following could increase coverage:

### High Value
1. Add more edge case tests to `artifact_operations.py` to cover error paths
2. Test error handling in `pr_operations.py` for malformed responses

### Lower Priority
1. Mock-heavy tests for `statistics_collector.py` (low ROI - integration tests cover this)
2. Unit tests for `__main__.py` and `parser.py` (low ROI - E2E tests cover this)
3. Edge case tests for the remaining 1-2 missed lines in near-perfect modules

## Testing Philosophy

Our testing strategy prioritizes:

1. **Unit tests for business logic** - All services, commands, and domain logic are thoroughly tested in isolation
2. **Integration tests for workflows** - Complex orchestration is tested via CLI commands and E2E tests
3. **Avoiding mock-heavy tests** - We don't test integration glue code with excessive mocking
4. **Focusing on value** - We don't chase 100% coverage by testing trivial code or reimplementing logic in tests

## Coverage by Layer

- **Domain Layer:** 99% average (exceptions, models, config)
- **Infrastructure Layer:** 97% average (git, github, filesystem)
- **Application Services:** 95% average (tasks, reviewers, artifacts, projects)
- **Application Collectors:** 15% (statistics_collector - tested via integration)
- **Application Formatters:** 98% average (table formatter)
- **CLI Commands:** 98% average (all 9 commands)
- **CLI Entry Points:** 0% (__main__, parser - tested via E2E)

**Total:** 85.03%

## Maintenance

When updating this document:
1. Run `pytest tests/unit/ --cov=src/claudestep --cov-report=term-missing`
2. Update coverage percentages and line numbers
3. Document any new intentionally untested code with rationale
4. Update the coverage badge in README.md if percentage changes significantly
