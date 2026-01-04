## Background

Currently, the ClaudeChain workflow configuration requires users to explicitly list target branches in the workflow file:

```yaml
on:
  pull_request:
    types: [closed]
    branches:
      - main
      - main-e2e
```

This creates problems when using ClaudeChain with feature branches:

1. **Feature branch workflow changes don't activate**: If a user wants to run ClaudeChain against a feature branch, they need to add that branch to the `branches:` filter. But the workflow file on the feature branch isn't the one GitHub uses - GitHub uses the workflow from the **target** branch.

2. **Chicken-and-egg problem**: To make ClaudeChain work with a feature branch, users must either:
   - Merge workflow changes to main first (mixing feature work with main)
   - Or accept that ClaudeChain won't work until their branch config changes land on main

3. **Stale branch names**: If users add feature branch names to the workflow on main, those become stale after the feature merges.

**Proposed solution**: Remove the `branches:` filter entirely and rely solely on the `claudechain` label for filtering. The action already checks for this label in the `should_skip()` logic.

**Key concern**: For high-volume repositories, this means every merged PR triggers the workflow, even if it's not ClaudeChain-related. However:
- GitHub Actions [does not support native label filtering](https://github.com/orgs/community/discussions/4679) on pull_request triggers
- The current workflow already triggers on all `claude-chain/**` path changes
- The skip happens very early (parse-event step) before any expensive operations
- The action's first step checks for the label and exits immediately if missing

**CI cost analysis**:
- Workflow trigger: ~1-2 seconds to start the job
- Parse-event step (skip path): ~3-5 seconds (Python startup + JSON parse + label check)
- Total waste per non-ClaudeChain PR: ~5-10 seconds of CI time
- This is minimal compared to typical CI workflows

## Phases

- [ ] Phase 1: Update example workflow configuration

Update the recommended workflow configuration to remove branch filtering:

**Files to modify:**
- `README.md` - Update the example workflow in the installation section
- `.github/workflows/claudechain.yml` - Update our own workflow as the reference implementation

**Changes to workflow:**
```yaml
# Before
on:
  pull_request:
    types: [closed]
    branches:
      - main
      - main-e2e
    paths:
      - 'claude-chain/**'

# After
on:
  pull_request:
    types: [closed]
    # No branches filter - all PRs with claudechain label are processed
    # Label filtering happens inside the action (GitHub doesn't support label triggers)
```

**Note**: We should also consider removing the `paths:` filter since that also limits flexibility. With label-based filtering, any PR with the `claudechain` label should trigger processing regardless of which files changed.

- [ ] Phase 2: Add job-level condition for early skip

Add a job-level `if` condition to skip the job entirely for non-labeled PRs, avoiding job startup overhead:

**Files to modify:**
- `README.md` - Update example workflow
- `.github/workflows/claudechain.yml` - Update our workflow

**Changes:**
```yaml
jobs:
  run-claudechain:
    runs-on: ubuntu-latest
    # Skip job entirely if PR doesn't have claudechain label (saves ~5s job startup)
    if: |
      github.event_name == 'workflow_dispatch' ||
      (github.event_name == 'pull_request' &&
       github.event.pull_request.merged == true &&
       contains(github.event.pull_request.labels.*.name, 'claudechain'))
    steps:
      ...
```

This provides the "filter at workflow level" behavior the user requested, using the only mechanism GitHub supports (job-level `if` conditions).

- [ ] Phase 3: Update documentation

Update feature guides to explain the flexible branch approach:

**Files to check and update:**
- `docs/feature-guides/` - Any guides that mention workflow configuration
- `README.md` - Ensure the "how it works" section explains label-based filtering

**Documentation should explain:**
- Why we use label filtering instead of branch filtering
- How this enables feature branch workflows
- That the label check happens at job-level (minimal CI waste)
- Users can optionally add branch/path filters if they want stricter control

- [ ] Phase 4: Validation

**Automated testing:**
1. Run existing unit tests: `pytest tests/unit/ -v`
2. Run integration tests: `pytest tests/integration/ -v`

**Manual validation:**
1. Merge a PR without the `claudechain` label - verify workflow skips at job level
2. Merge a PR with `claudechain` label on a non-main branch - verify it processes correctly
3. Run workflow_dispatch - verify it still works

**Success criteria:**
- Non-ClaudeChain PRs skip immediately at job level
- ClaudeChain-labeled PRs work regardless of target branch
- Existing workflow_dispatch functionality unchanged
