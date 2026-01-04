## Background

Currently there's a mismatch between which branch is checked out vs which branch the spec is loaded from:

- `checkout_ref` is derived from the event context (e.g., `main` for a PR merged to main)
- `base_branch` can be overridden by `default_base_branch` input or project config's `baseBranch`

This means if a user has `baseBranch: feature-branch` in their configuration.yml:
1. A PR merges to `main` → triggers workflow
2. Checkout happens on `main` (from event)
3. Spec is loaded from `feature-branch` (from config)
4. PR is created targeting `feature-branch`

Claude ends up refactoring code on `main` but using tasks from `feature-branch`'s spec - a mismatch.

**The fix**: Always checkout the resolved `base_branch`, not the event's ref. The triggering event (PR merge, push, workflow_dispatch) is just a trigger mechanism - all actual work should happen on the configured base branch.

## Phases

- [x] Phase 1: Unify checkout_ref and base_branch in parse_event.py

Currently `parse_event.py` outputs two separate values:
- `checkout_ref` - derived from event context
- `base_branch` - respects `default_base_branch` config

Change this so `checkout_ref` equals `base_branch`:

```python
# Current:
checkout_ref = context.get_checkout_ref()  # From event
base_branch = default_base_branch or context.get_checkout_ref()

# New:
# Determine base_branch first (respects config)
if default_base_branch:
    base_branch = default_base_branch
else:
    base_branch = context.get_checkout_ref()

# checkout_ref should match base_branch
checkout_ref = base_branch
```

**Files to modify:**
- `src/claudechain/cli/commands/parse_event.py`

- [x] Phase 2: Update tests

Update tests to reflect that `checkout_ref` now equals `base_branch`:

1. `tests/integration/cli/commands/test_parse_event.py`:
   - Update `test_workflow_dispatch_uses_configured_base_branch_not_trigger_branch` - now `checkout_ref` should also be `feature-branch`
   - Update any other tests that assert `checkout_ref` comes from event context

2. Review other tests that may depend on `checkout_ref` being different from `base_branch`

- [x] Phase 3: Validation

1. Run unit tests: `pytest tests/unit/ -v`
2. Run integration tests: `pytest tests/integration/ -v`
3. Verify the key scenario:
   - `default_base_branch` set to `feature-branch`
   - PR event targeting `main`
   - Both `checkout_ref` and `base_branch` should be `feature-branch`
