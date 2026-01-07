## Background

The current Slack notification for ClaudeChain statistics uses Unicode box-drawing characters (┌─┬─┐, │, └─┴─┘) to render tables. While this works, the resulting output is visually unappealing in Slack because:

1. **Monospace dependency**: The table relies on fixed-width fonts, but Slack doesn't guarantee consistent monospace rendering
2. **Code block ugliness**: Tables are wrapped in triple backticks (```), creating a gray code block that looks out of place in a notification
3. **No native styling**: Inside code blocks, we lose all Slack formatting (bold, links, emojis render as text)
4. **Mobile issues**: Wide tables require horizontal scrolling on mobile devices

## Experiment Results

Tested both Table Block and Section Fields approaches with incoming webhooks on 2026-01-06:

- **Table Block**: Works with webhooks when placed in `attachments[].blocks`. Renders clean tabular data with proper column alignment. However, only supports `raw_text` (no mrkdwn formatting, emojis, or links).

- **Section Fields**: Works with webhooks in top-level `blocks`. Supports rich formatting including progress bars, clickable PR links, emojis, and flexible layouts.

**Decision**: Use Section Fields approach for richer formatting capabilities (progress bars, PR links with age indicators, conditional emojis).

## Target Format

The final Slack message structure:

```json
{
  "text": "ClaudeChain Statistics - Fallback",
  "blocks": [
    {
      "type": "header",
      "text": {"type": "plain_text", "text": "ClaudeChain Statistics", "emoji": true}
    },
    {
      "type": "context",
      "elements": [
        {"type": "mrkdwn", "text": "📅 2026-01-06  •  Branch: main"}
      ]
    },
    {"type": "divider"},
    {
      "type": "section",
      "text": {"type": "mrkdwn", "text": "*auth-migration*\n████████░░ 80%"}
    },
    {
      "type": "context",
      "elements": [
        {"type": "mrkdwn", "text": "4/5 merged  •  💰 $0.45"}
      ]
    },
    {
      "type": "section",
      "text": {"type": "mrkdwn", "text": "• <https://github.com/org/repo/pull/42|#42 Add OAuth support> (2d)"}
    },
    {"type": "divider"},
    {
      "type": "section",
      "text": {"type": "mrkdwn", "text": "*api-refactor* ✅\n██████████ 100%"}
    },
    {
      "type": "context",
      "elements": [
        {"type": "mrkdwn", "text": "5/5 merged  •  💰 $2.10"}
      ]
    },
    {"type": "divider"},
    {
      "type": "section",
      "text": {"type": "mrkdwn", "text": "*🏆 Leaderboard*"}
    },
    {
      "type": "section",
      "fields": [
        {"type": "mrkdwn", "text": "🥇 *alice*\n5 merged"},
        {"type": "mrkdwn", "text": "🥈 *bob*\n3 merged"}
      ]
    }
  ]
}
```

### Format Rules

1. **Project header**: `*project-name*` with ✅ only if 100% complete
2. **Progress bar**: Unicode blocks (████░░) with percentage on same line
3. **Stats context**: "X/Y merged • 💰 $cost" in smaller context text
4. **Open PRs**: Bullet list with clickable links, age in days, ⚠️ for stale (5d+)
5. **Completed projects**: No PR list (none open)
6. **Leaderboard**: 2-column fields with medal emojis, merged count only

## Phases

- [x] Phase 1: Experiment with Slack Block Kit in webhooks

Tested both Table Block and Section Fields approaches. Both work with incoming webhooks. Chose Section Fields for richer formatting support.

- [ ] Phase 2: Create Block Kit message builder

Create a new `SlackBlockKitFormatter` class that outputs Slack Block Kit JSON structures.

Files to create:
- `src/claudechain/domain/formatters/slack_block_kit_formatter.py`

The formatter should support:
- Header blocks for titles
- Context blocks for metadata (date, branch, stats)
- Section blocks for project info and PR lists
- Divider blocks between projects
- Section fields for leaderboard (2-column layout)

- [ ] Phase 3: Implement project progress blocks

Generate blocks for each project following the target format:

```python
def format_project_blocks(project: ProjectStats) -> list[dict]:
    """Generate Block Kit blocks for a single project."""
    blocks = []

    # Project name with optional checkmark
    name = f"*{project.name}*"
    if project.is_complete:
        name += " ✅"

    # Progress bar
    progress_bar = generate_progress_bar(project.percent_complete)

    blocks.append({
        "type": "section",
        "text": {"type": "mrkdwn", "text": f"{name}\n{progress_bar}"}
    })

    # Stats context
    blocks.append({
        "type": "context",
        "elements": [{
            "type": "mrkdwn",
            "text": f"{project.merged}/{project.total} merged  •  💰 ${project.cost:.2f}"
        }]
    })

    # Open PRs list (if any)
    if project.open_prs:
        pr_lines = []
        for pr in project.open_prs:
            line = f"• <{pr.url}|#{pr.number} {pr.title}> ({pr.age_days}d)"
            if pr.age_days >= 5:
                line += " ⚠️"
            pr_lines.append(line)

        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": "\n".join(pr_lines)}
        })

    blocks.append({"type": "divider"})
    return blocks
```

Files to modify:
- `src/claudechain/domain/formatters/slack_block_kit_formatter.py`

- [ ] Phase 4: Implement leaderboard blocks

Generate leaderboard using Section fields for 2-column layout:

```python
def format_leaderboard_blocks(leaderboard: list[LeaderboardEntry]) -> list[dict]:
    """Generate Block Kit blocks for leaderboard."""
    medals = ["🥇", "🥈", "🥉"]

    blocks = [{
        "type": "section",
        "text": {"type": "mrkdwn", "text": "*🏆 Leaderboard*"}
    }]

    fields = []
    for i, entry in enumerate(leaderboard[:6]):  # Max 6 to stay under 10 fields
        medal = medals[i] if i < 3 else f"{i+1}."
        fields.append({
            "type": "mrkdwn",
            "text": f"{medal} *{entry.username}*\n{entry.merged} merged"
        })

    blocks.append({
        "type": "section",
        "fields": fields
    })

    return blocks
```

Files to modify:
- `src/claudechain/domain/formatters/slack_block_kit_formatter.py`

- [ ] Phase 5: Update format_for_slack to output Block Kit JSON

Modify `StatisticsReport.format_for_slack()` to return a JSON structure with `blocks` array instead of plain text.

Files to modify:
- `src/claudechain/domain/models.py` - Update `format_for_slack()` to return dict with blocks
- `src/claudechain/cli/commands/statistics.py` - Handle JSON output for Slack webhook

Key change: The webhook payload structure changes from:
```json
{"text": "plain text message"}
```
to:
```json
{
  "text": "Fallback text for notifications",
  "blocks": [...]
}
```

- [ ] Phase 6: Update tests

Update existing tests to verify the new Block Kit output structure.

Files to modify:
- `tests/unit/domain/test_models.py` - Update tests for new block methods
- `tests/integration/cli/commands/test_statistics.py` - Verify Block Kit JSON output
- Create `tests/unit/domain/formatters/test_slack_block_kit_formatter.py`

Test requirements:
- Verify blocks array structure is valid
- Verify header blocks use plain_text (required by Slack)
- Verify section fields are limited to 10 per section
- Verify mrkdwn text uses correct syntax
- Verify fallback text is included for notification previews
- Verify ✅ only appears on 100% complete projects
- Verify ⚠️ appears on PRs older than 5 days

- [ ] Phase 7: Validation

Run full test suite and verify output:

```bash
export PYTHONPATH=src:scripts
pytest tests/unit/ tests/integration/ -v --cov=src/claudechain --cov-report=term-missing
```

Manual verification:
- Run statistics command locally and inspect JSON output
- Validate Block Kit JSON using Slack's Block Kit Builder (https://app.slack.com/block-kit-builder)
- Test with a real Slack webhook to verify rendering
