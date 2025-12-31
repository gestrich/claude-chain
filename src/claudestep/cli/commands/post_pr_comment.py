"""
Post unified PR comment with summary and cost breakdown.

This command combines the AI-generated summary and cost breakdown into a single
comment, using the reliable Python-based posting mechanism.
"""

import subprocess
import tempfile

from claudestep.domain.cost_breakdown import CostBreakdown
from claudestep.domain.summary_file import SummaryFile
from claudestep.infrastructure.github.actions import GitHubActionsHelper


def cmd_post_pr_comment(
    gh: GitHubActionsHelper,
    pr_number: str,
    summary_file_path: str,
    main_cost: float,
    summary_cost: float,
    total_cost: float,
    repo: str,
    run_id: str
) -> int:
    """
    Post a unified comment with PR summary and cost breakdown.

    All parameters passed explicitly, no environment variable access.

    Args:
        gh: GitHub Actions helper for outputs and errors
        pr_number: Pull request number
        summary_file_path: Path to file containing AI-generated summary
        main_cost: Cost of main refactoring task (USD)
        summary_cost: Cost of PR summary generation (USD)
        total_cost: Total cost (USD)
        repo: Repository in format owner/repo
        run_id: Workflow run ID

    Outputs:
        comment_posted: "true" if comment was posted, "false" otherwise

    Returns:
        0 on success, 1 on error
    """
    # If no PR number, skip gracefully
    if not pr_number or not pr_number.strip():
        print("::notice::No PR number provided, skipping PR comment")
        gh.write_output("comment_posted", "false")
        return 0

    if not repo:
        gh.set_error("GITHUB_REPOSITORY environment variable is required")
        return 1

    if not run_id:
        gh.set_error("GITHUB_RUN_ID environment variable is required")
        return 1

    try:
        # Use domain models for parsing and formatting
        summary = SummaryFile.from_file(summary_file_path)
        cost_breakdown = CostBreakdown(
            main_cost=main_cost,
            summary_cost=summary_cost
        )

        # Use domain model for formatting
        comment = summary.format_with_cost(cost_breakdown, repo, run_id)

        # Write comment to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(comment)
            temp_file = f.name

        try:
            # Post comment to PR using gh CLI
            print(f"Posting PR comment to PR #{pr_number}...")
            subprocess.run(
                ["gh", "pr", "comment", pr_number, "--body-file", temp_file],
                check=True,
                capture_output=True,
                text=True
            )

            print(f"✅ PR comment posted to PR #{pr_number}")
            if summary.has_content:
                print("   - AI-generated summary included")
            print(f"   - Main task: ${main_cost:.6f}")
            print(f"   - PR summary: ${summary_cost:.6f}")
            print(f"   - Total: ${total_cost:.6f}")

            gh.write_output("comment_posted", "true")
            return 0

        finally:
            # Clean up temp file
            import os
            os.unlink(temp_file)

    except subprocess.CalledProcessError as e:
        gh.set_error(f"Failed to post comment: {e.stderr}")
        return 1
    except Exception as e:
        gh.set_error(f"Error posting PR comment: {str(e)}")
        return 1
