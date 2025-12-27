# Local Testing Setup

## End-to-End Testing

End-to-end integration tests are located in the demo project at `/Users/bill/Developer/personal/claude-step-demo/tests/integration/`.

### Purpose

The E2E tests validate the complete ClaudeStep workflow by:
- Creating test projects in the demo repository
- Triggering actual GitHub Actions workflows
- Verifying PRs are created correctly
- Testing reviewer capacity limits
- Testing merge trigger functionality
- Cleaning up all created resources

### Running E2E Tests

**Important:** Before running E2E tests, you must push changes to both repositories:

1. Push action changes to `claude-step` repository
2. Push demo project changes (if any) to `claude-step-demo` repository
3. Run tests from the demo project:

```bash
cd /Users/bill/Developer/personal/claude-step-demo
./tests/integration/run_test.sh
```

See `claude-step-demo/tests/integration/README.md` for detailed documentation.

### Testing Repository

The demo repository at `/Users/bill/Developer/personal/claude-step-demo` serves as the live testing environment for:
- Creating test projects and artifacts
- Validating application functionality
- Testing GitHub integrations

### GitHub Integration Testing

The tests interact with GitHub using the `gh` CLI APIs to:
- Monitor workflow runs
- Check CI/CD status
- Verify GitHub Actions execution
- Test pull request workflows

### Usage

This testing setup allows safe experimentation and validation of features without affecting production repositories. All GitHub API interactions are performed through the official `gh` CLI tool, ensuring consistent and reliable communication with GitHub services.
