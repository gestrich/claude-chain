# V1 Improvements

Configuration and workflow improvements for V1 release.

## Tasks

- [ ] **Use YML for configuration**

This app currently uses json but YML would be preferred. No backwards compatibility needed. Just fix it. Will need to update /Users/bill/Developer/personal/claude-step-demo

- [ ] **Improve branch name options**

You can specify a branch prefix in the configuration per the README.md but I'm not sure it is actually working. We should support the following:

* Branch Prefix for that project. We'd use that prefix then append the index we've already been using
* YYYY/MM... schema we already use (default when no branch prefix given)
* Docs should be updated to explain this

- [ ] **Remove unnecessary action inputs**

We have inputs for config_path, spec_path, and pr_template_path. Let's get rid of that. Instead let's require the user uses claude-step/ for their projects and let's always assume they then have project folders in there with the appropriately named files.

- [ ] **Trigger action off of closed PRs, not just merged**

Our linked project at /Users/bill/Developer/personal/claude-step-demo triggers off merged PRs. But we need to assume PRs may be closed without merging too. Note this may trigger the same PR to be opened again so we may want to advise against closing PRs and instead updating the markdown to remove that step if not needed and merge that change first before closing the PR to avoid a cycle of it re-opening.

- [ ] **Run e2e tests to verify changes**

After completing all the above tasks:
1. Push changes to both claude-step and claude-step-demo repositories
2. Run the e2e tests: `./tests/integration/run_test.sh`
3. Verify the demo repo still works after all these changes
4. The tests rely on code being pushed to GitHub, so make sure both repos are pushed before running tests
