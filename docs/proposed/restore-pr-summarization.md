## Background

ClaudeStep previously had AI-generated PR summary functionality that would analyze the diff and post a summary comment to each PR. This feature was added in commit e680d1f and later enhanced with cost tracking in commit ab68ce6.

Currently, the summary infrastructure is still in place:
- The `add_pr_summary` input exists in action.yml (line 39-42) and defaults to `true`
- The `prepare-summary` command generates a prompt successfully (logs show "✅ Summary prompt prepared for PR #114")
- The summary prompt template exists at `src/claudestep/resources/prompts/summary_prompt.md`
- The `Generate and post PR summary` step is defined in action.yml (lines 182-193)

However, PR summaries are no longer being posted to PRs. Recent PRs (e.g., #114) only show cost breakdown comments but lack the AI-generated summary that should explain what changes were made and why.

Investigation reveals that while the prompt is being prepared, the actual Claude Code execution to generate and post the summary may not be running or may be failing silently due to the `continue-on-error: true` flag.

## Phases

- [x] Phase 1: Investigate why summary posting stopped working

**Investigation completed on 2025-12-31**

### Root Cause Analysis

The summary infrastructure is working correctly, but Claude Code execution is **non-deterministic** in posting comments. The issue is not with the GitHub Actions configuration or conditional logic, but with Claude Code's behavior.

**What's working:**
- ✅ Conditional logic in action.yml (lines 167-168, 184-186) is correct
- ✅ `inputs.add_pr_summary` defaults to `'true'` and is being passed correctly
- ✅ `steps.finalize.outputs.pr_number` is being set correctly (verified in logs)
- ✅ `steps.prepare_summary.outputs.summary_prompt` is being generated and output correctly
- ✅ The "Prepare summary prompt" step runs successfully (logs show: `✅ Summary prompt prepared for PR #114`)
- ✅ The "Generate and post PR summary" step executes (Claude Code receives the prompt)
- ✅ Claude Code analyzes the PR diff correctly (executes `gh pr diff`)

**The actual problem:**
Claude Code behaves **inconsistently** when posting comments:

**Failed case (PR #114, run 20625002452):**
- Claude executed: `gh pr diff 114 --patch` ✅
- Claude generated the summary text ✅
- Claude did NOT execute: `gh pr comment 114 --body-file <file>` ❌
- Result: Summary was generated but never posted

**Successful case (PR #120, run 20625399076):**
- Claude executed: `gh pr diff 120 --patch` ✅
- Claude generated the summary text ✅
- Claude executed: `gh pr comment 120 --body-file /tmp/pr-comment.md` ✅
- Result: Summary was posted successfully

### Why This Was Hidden

The `continue-on-error: true` flag in action.yml:194 masks these failures. Even when Claude doesn't post the comment, the workflow succeeds without any visible error.

### Technical Notes

Files examined:
- action.yml:164-194 - Summary generation steps configuration
- .github/workflows/claudestep.yml - ClaudeStep invocation (does not explicitly set add_pr_summary, uses default)
- src/claudestep/cli/commands/prepare_summary.py - Prompt generation (working correctly)
- src/claudestep/infrastructure/github/actions.py - Output handling (working correctly)
- Workflow runs: 20625002452 (failed), 20625399076 (succeeded), 20625399076 logs show both commands executed

The issue requires improving the prompt or Claude Code configuration to ensure consistent behavior.

- [x] Phase 2: Fix the summary generation step

**Completed on 2025-12-31**

### Changes Implemented

1. **Enhanced Summary Prompt** (`src/claudestep/resources/prompts/summary_prompt.md`)
   - Added explicit "CRITICAL" and "REQUIRED" markers to emphasize that posting the comment is mandatory
   - Changed step 4 to clearly state "DO NOT skip this step. The comment MUST be posted."
   - Added footer reminder: "IMPORTANT: After writing the summary to a file, you MUST execute the `gh pr comment` command to post it. This is not optional."
   - These changes address the non-deterministic behavior identified in Phase 1 where Claude Code would sometimes generate the summary but fail to post it

2. **Verified `continue-on-error` Flag Removal**
   - Confirmed that `continue-on-error: true` is NOT present in the summary generation step (lines 182-194 in action.yml)
   - This was already removed in a previous change, ensuring that failures will be visible
   - Other `continue-on-error` flags exist in action.yml (lines 111, 136, 210, 227, 246, 290) but are for different steps

### Technical Notes

**Root Cause:** Based on Phase 1 investigation, the issue was that Claude Code behaves non-deterministically when executing the summary prompt. In failed cases (e.g., PR #114), Claude would:
- ✅ Execute `gh pr diff`
- ✅ Generate summary text
- ❌ Skip executing `gh pr comment`

**Solution Approach:** Rather than modifying the GitHub Actions configuration (which was working correctly), the fix focuses on making the prompt more directive and explicit about the requirement to post the comment. The enhanced prompt uses multiple reinforcement techniques:
- Bold "CRITICAL" header before instructions
- "REQUIRED" label on step 4
- Explicit "DO NOT skip" warning
- Footer reminder about mandatory execution

**Testing:** Build verification completed successfully:
- Ran unit and integration tests: 679 passed, 1 failed (pre-existing failure in statistics service unrelated to this change)
- Coverage: 68.72% (below 70% threshold, but this is a pre-existing issue)
- No new test failures introduced by the prompt changes

Expected outcome: The more directive prompt should reduce non-deterministic behavior and increase the consistency of comment posting. The next phase (Phase 3) will verify the quality of posted summaries.

- [ ] Phase 3: Verify summary format and content quality

Ensure the posted summaries meet quality standards:
- Verify the summary comment format matches the template (includes "## AI-Generated Summary" header)
- Check that summaries are concise (<200 words as specified in prompt)
- Ensure summaries explain both what changed and why
- Confirm the footer with workflow URL is included

Files to check:
- `src/claudestep/resources/prompts/summary_prompt.md` - may need prompt refinement
- Example PR comments to assess quality

Expected outcome: Posted summaries are well-formatted and provide useful information

- [ ] Phase 4: Update E2E tests to properly validate summaries

The E2E test `test_basic_workflow_end_to_end` currently checks for summary comments but uses a broad pattern that doesn't match the actual format:
- Test looks for "Summary" or "Changes" in comment body (line 113)
- Actual format uses "## AI-Generated Summary" header
- Need to update test to match the actual comment format

Files to modify:
- `tests/e2e/test_workflow_e2e.py` lines 111-116
- Update the pattern to look for "AI-Generated Summary" instead of generic "Summary"
- Consider also checking for the ClaudeStep footer

Expected outcome: E2E test accurately validates that summary comments are being posted

- [ ] Phase 5: Validation

Run end-to-end tests and manual verification:

**IMPORTANT**: Always run E2E tests using the provided script:
```bash
tests/e2e/run_test.sh
```
- Do NOT run pytest directly for E2E tests
- The script triggers the actual GitHub Actions workflow and monitors results
- Watch the script output for test results and workflow URLs

Validation steps:
1. Run `tests/e2e/run_test.sh` to execute the E2E test suite
2. Monitor the script output to ensure `test_basic_workflow_end_to_end` passes
3. Check the workflow run URLs provided in the output
4. Verify that the test PR receives both:
   - Cost breakdown comment (existing functionality)
   - AI-generated summary comment (restored functionality)
5. Check that the summary comment has the expected format with "## AI-Generated Summary" header
6. Verify summary content is relevant and useful
7. If tests fail, check the uploaded artifacts for detailed logs

Success criteria:
- E2E test script completes successfully
- `test_basic_workflow_end_to_end` passes
- Test PRs receive both cost and summary comments
- Summary comments follow the expected format (includes "## AI-Generated Summary")
- Summary content accurately describes the changes made
- No workflow failures or hidden errors
