# E2E Test Isolation Plan

## Problem

E2E tests pollute the main branch by:
- Creating test projects in `claude-step/` directory on main
- Causing git push conflicts during concurrent test runs
- Leaving test artifacts in repository history
- Creating merge conflicts with development work

## Solution

Use a dedicated `e2e-test` branch for all test operations, keeping main clean.

## Implementation Phases

- [ ] **Phase 1: Clean Main Branch**
  - Remove `claude-step/` directory from main
  - Commit: "Remove claude-step test directory - moving to e2e-test branch"
  - Push to main

- [ ] **Phase 2: Create Test Branch**
  - Create `e2e-test` branch from main
  - Add `claude-step/README.md` explaining test workspace
  - Push branch to remote

- [ ] **Phase 3: Update Workflows**
  - `.github/workflows/e2e-test.yml`: Check out `e2e-test` branch
  - `.github/workflows/claudestep-test.yml`: Add `base_branch` input parameter (default: `e2e-test`)
  - Pass `base_branch: e2e-test` to ClaudeStep action during tests

- [ ] **Phase 4: Update Test Code**
  - `tests/e2e/helpers/project_manager.py`: Change default branch from `main` to `e2e-test`
  - `tests/e2e/helpers/github_helper.py`: Change default ref from `main` to `e2e-test`
  - `tests/e2e/test_workflow_e2e.py`: Update all workflow triggers to use `e2e-test` branch

- [ ] **Phase 5: Test and Document**
  - Run E2E tests on `e2e-test` branch to verify everything works
  - Update README.md with E2E test isolation info
  - Verify main branch stays clean during test runs

## Detailed Steps

### Phase 1 Commands
```bash
git checkout main
git pull origin main
git rm -rf claude-step/
git commit -m "Remove claude-step test directory - moving to e2e-test branch"
git push origin main
```

### Phase 2 Commands
```bash
git checkout -b e2e-test
mkdir -p claude-step
cat > claude-step/README.md << 'EOF'
# E2E Test Workspace

This directory is used exclusively for E2E testing. Test projects are created
here during test runs and cleaned up afterwards.

**Do not manually create projects here.** All projects are managed by the E2E test framework.
EOF
git add claude-step/README.md
git commit -m "Set up e2e-test branch for isolated E2E testing"
git push -u origin e2e-test
```

### Phase 3 Files to Modify

**`.github/workflows/e2e-test.yml`**:
```yaml
- name: Checkout repository
  uses: actions/checkout@v4
  with:
    ref: e2e-test  # Always use test branch
```

**`.github/workflows/claudestep-test.yml`**:
```yaml
inputs:
  base_branch:
    description: 'Base branch for pull requests'
    required: false
    default: 'e2e-test'

# In the action step:
- name: Run ClaudeStep action
  uses: ./
  with:
    base_branch: ${{ github.event.inputs.base_branch || 'e2e-test' }}
```

### Phase 4 Code Changes

**`tests/e2e/helpers/project_manager.py`**:
```python
def commit_and_push_project(..., branch: str = "e2e-test")
def remove_and_commit_project(..., branch: str = "e2e-test")
```

**`tests/e2e/helpers/github_helper.py`**:
```python
def trigger_workflow(..., ref: str = "e2e-test")
```

**`tests/e2e/test_workflow_e2e.py`**:
Update all `ref="main"` to `ref="e2e-test"` in workflow triggers

## Benefits

- Clean main branch with no test pollution
- No git push conflicts during concurrent test runs
- Development work won't interfere with tests
- Consistent, predictable test environment
