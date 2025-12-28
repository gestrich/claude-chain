# Test Coverage Improvement Plan - Phase 2

This document outlines the remaining work to further enhance the testing infrastructure for ClaudeStep. All core testing work is complete (493 tests, 85% coverage). These are optional enhancements.

## Current State

- **493 tests passing** (0 failures)
- **85.03% code coverage** (exceeding 70% minimum)
- **All layers tested**: Domain, Infrastructure, Application, CLI
- **CI/CD integrated**: Tests run on every PR with automated coverage reports
- **Documentation complete**: Testing guide and coverage notes documented

## Remaining Work

The following phases outline optional enhancements to the testing infrastructure:

### Phase 1: Document Testing Architecture ⭐ HIGH PRIORITY

- [ ] **Create `docs/architecture/tests.md`** with comprehensive testing architecture documentation

**Purpose:** Provide architectural guidance for testing in the ClaudeStep codebase.

**Content to include:**
1. **Testing Principles**
   - Test isolation and independence
   - Mocking strategy (mock at system boundaries, not internal logic)
   - Arrange-Act-Assert pattern
   - One concept per test

2. **Test Architecture Overview**
   - Layer-based testing strategy (Domain → Infrastructure → Application → CLI)
   - Test directory structure mirrors `src/` structure
   - Fixture organization and reuse patterns
   - Integration vs unit test boundaries

3. **Testing by Layer**
   - **Domain Layer**: Direct testing, minimal mocking (business logic, models, config)
   - **Infrastructure Layer**: Mock external systems (subprocess, file I/O, HTTP)
   - **Application Layer**: Mock infrastructure, test business logic
   - **CLI Layer**: Mock everything below, test command orchestration

4. **What to Test vs What Not to Test**
   - Test behavior, not implementation
   - Don't test Python/framework features
   - Don't test third-party libraries
   - Focus on business logic and integration points

5. **Common Patterns**
   - Using conftest.py fixtures
   - Parametrized tests for boundary conditions
   - Error handling and edge cases
   - Async/sync testing patterns (if applicable)

6. **References**
   - Link to `docs/testing-guide.md` for detailed style guide
   - Link to `docs/testing-coverage-notes.md` for coverage rationale
   - Link to `docs/proposed/test-coverage-improvement-plan.md` for implementation history

**Dependencies:**
- Read existing test files to understand patterns
- Review `tests/conftest.py` for fixture patterns
- Review completed test modules for examples

**Acceptance Criteria:**
- Document explains WHY we test the way we do (architecture decisions)
- Clear guidance on how to approach testing new features
- Examples from existing codebase
- References to related documentation

---

### Phase 2: Dynamic Coverage Badge ✅

- [x] **Integrate Codecov or Coveralls for dynamic coverage badge**

**Purpose:** Automatically update coverage badge without manual edits.

**Implementation Notes (Completed 2025-12-27):**

Integrated Codecov for automatic coverage badge updates:

1. **Workflow Changes** (`.github/workflows/test.yml`):
   - Added `coverage xml` to generate coverage.xml file for Codecov
   - Added Codecov action step that uploads coverage data on every test run
   - Used `codecov/codecov-action@v4` with CODECOV_TOKEN secret
   - Set `fail_ci_if_error: false` to prevent CI failures on Codecov issues

2. **README Updates**:
   - Replaced static badge `![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen)`
   - With dynamic Codecov badge: `[![codecov](https://codecov.io/gh/gestrich/claude-step/branch/main/graph/badge.svg)](https://codecov.io/gh/gestrich/claude-step)`
   - Badge will auto-update on each commit once CODECOV_TOKEN is set

3. **Next Steps for Repo Owner**:
   - Sign up at codecov.io and link the gestrich/claude-step repository
   - Add `CODECOV_TOKEN` secret to GitHub repository settings
   - Configure Codecov project settings with 70% minimum threshold
   - Badge will start updating automatically once token is configured

**Technical Details:**
- Coverage data is uploaded on every test run (including PRs)
- XML format is the standard Codecov input format
- Existing HTML and text coverage reports remain unchanged
- All 493 tests pass with the new configuration

**Acceptance Criteria Met:**
- ✅ Badge will update automatically on each commit (once token configured)
- ✅ Badge shows current coverage percentage
- ✅ Ready for 70% minimum threshold configuration in Codecov settings

---

### Phase 6: Test Performance Monitoring

- [ ] **Add pytest-benchmark for performance-critical code**

**Purpose:** Ensure tests remain fast as codebase grows.

**Tasks:**
1. Add `pytest-benchmark` to test dependencies
2. Identify slow tests (if any) using `pytest --durations=10`
3. Add benchmarks for:
   - File parsing operations (spec.md, config.yml)
   - Task searching algorithms
   - Large fixture setup
4. Set performance thresholds
5. Track performance over time in CI

**Dependencies:**
- None (optional enhancement)

**Estimated Effort:** 2-3 hours

**Acceptance Criteria:**
- Benchmark suite runs in CI
- Performance regressions detected
- Documentation for adding benchmarks

---

### Phase 7: Coverage Improvement for Integration Code

- [ ] **Increase coverage of `statistics_collector.py` to 50%+**

**Purpose:** Reduce large coverage gap (currently 15%).

**Current State:**
- 164/193 lines missed
- Tested via integration but not unit tests
- Complex orchestration module

**Approach:**
1. Review `tests/unit/cli/commands/test_statistics.py` (already mocks the collector)
2. Add direct unit tests for `statistics_collector.py` functions:
   - `collect_project_statistics()`
   - `collect_team_member_statistics()`
   - `collect_all_statistics()`
3. Mock dependencies: `get_project_prs()`, `find_project_artifacts()`, etc.
4. Test edge cases: empty data, API failures, parsing errors

**Dependencies:**
- Understanding of statistics collection workflow
- Review `docs/testing-coverage-notes.md` for why this is currently low

**Estimated Effort:** 4-6 hours

**Acceptance Criteria:**
- statistics_collector.py coverage > 50%
- Edge cases tested
- Integration tests still pass

---

### Phase 9: Test Data Builders

- [ ] **Create builder pattern helpers for complex test data**

**Purpose:** Simplify test setup and improve readability.

**Tasks:**
1. Create `tests/builders/` directory with builder classes:
   - `ConfigBuilder` - Fluent interface for creating test configs
   - `PRDataBuilder` - Build PR data with defaults
   - `ArtifactBuilder` - Build artifact metadata
   - `SpecFileBuilder` - Build spec.md content

2. Example:
   ```python
   config = ConfigBuilder()
       .with_reviewer("alice", max_prs=2)
       .with_reviewer("bob", max_prs=1)
       .build()
   ```

3. Refactor existing tests to use builders
4. Document builder pattern in architecture docs

**Dependencies:**
- Phase 1 (architecture docs should mention builders)

**Estimated Effort:** 6-8 hours

**Acceptance Criteria:**
- Builder classes created for main data types
- At least 20% of tests refactored to use builders
- Tests are more readable
- Documentation updated


## Prioritization

**High Priority (Do First):**
1. ✅ Phase 1: Document Testing Architecture (provides foundation for other work)
2. ✅ Phase 2: Dynamic Coverage Badge (professional polish)

**Medium Priority (Good to Have):**
6. Phase 7: Coverage Improvement (addresses known gap)

**Low Priority (Nice to Have):**
7. Phase 6: Test Performance Monitoring (suite is already fast)
8. Phase 9: Test Data Builders (refactoring, not new tests)


## Notes

- All phases are optional enhancements
- Core testing work is complete (85% coverage, 493 tests)
- Focus on phases that provide most value for effort
- Document decisions as you go

## References

- Current test documentation: `docs/testing-guide.md`
- Coverage analysis: `docs/testing-coverage-notes.md`
- Implementation history: `docs/proposed/test-coverage-improvement-plan.md`
- Test fixtures: `tests/conftest.py`
