"""Reviewer capacity checking and assignment"""

import json
import os
from typing import Any, Dict, List, Optional

from claudestep.exceptions import GitHubAPIError
from claudestep.github_operations import download_artifact_json, gh_api_call, run_gh_command
from claudestep.models import ReviewerCapacityResult


def find_available_reviewer(reviewers: List[Dict[str, Any]], label: str, project: str) -> tuple[Optional[str], ReviewerCapacityResult]:
    """Find first reviewer with capacity based on artifact metadata

    Args:
        reviewers: List of reviewer dicts with 'username' and 'maxOpenPRs'
        label: GitHub label to filter PRs
        project: Project name to match artifacts

    Returns:
        Tuple of (username or None, ReviewerCapacityResult)

    Raises:
        GitHubAPIError: If GitHub CLI command fails
    """
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    result = ReviewerCapacityResult()

    # Initialize reviewer PR lists
    reviewer_prs = {}
    for reviewer in reviewers:
        reviewer_prs[reviewer["username"]] = []

    # Get all open PRs with the label
    try:
        pr_output = run_gh_command([
            "pr", "list",
            "--repo", repo,
            "--label", label,
            "--state", "open",
            "--json", "number,headRefName"
        ])
        prs = json.loads(pr_output) if pr_output else []
    except (GitHubAPIError, json.JSONDecodeError) as e:
        print(f"Warning: Failed to list PRs: {e}")
        prs = []

    print(f"Found {len(prs)} open PR(s) with label '{label}'")

    # Build a map of PR numbers from all open PRs
    pr_numbers = {pr["number"] for pr in prs}

    # Get recent successful workflow runs (they run on default branch, not feature branches)
    # We'll check all recent runs and match artifacts to PRs by PR number in metadata
    try:
        api_response = gh_api_call(
            f"/repos/{repo}/actions/runs?status=completed&per_page=50"
        )
        runs = api_response.get("workflow_runs", [])
    except GitHubAPIError as e:
        print(f"Warning: Failed to get workflow runs: {e}")
        runs = []

    # Check artifacts from recent runs to find reviewer assignments
    for run in runs:
        if run.get("conclusion") != "success":
            continue

        try:
            artifacts_data = gh_api_call(
                f"/repos/{repo}/actions/runs/{run['id']}/artifacts"
            )
            artifacts = artifacts_data.get("artifacts", [])

            for artifact in artifacts:
                name = artifact["name"]
                if name.startswith(f"task-metadata-{project}-"):
                    # Download and parse the artifact JSON
                    artifact_id = artifact["id"]
                    metadata = download_artifact_json(repo, artifact_id)

                    if metadata and "pr_number" in metadata and "reviewer" in metadata:
                        pr_num = metadata["pr_number"]
                        # Only count if this PR is in our open PRs list
                        if pr_num in pr_numbers:
                            assigned_reviewer = metadata["reviewer"]
                            if assigned_reviewer in reviewer_prs:
                                # Store PR details
                                pr_info = {
                                    "pr_number": pr_num,
                                    "task_index": metadata.get("task_index", "?"),
                                    "task_description": metadata.get("task_description", "Unknown task")
                                }
                                reviewer_prs[assigned_reviewer].append(pr_info)
                                print(f"PR #{pr_num}: reviewer={assigned_reviewer} (from artifact)")
                            else:
                                print(f"Warning: PR #{pr_num} has unknown reviewer: {assigned_reviewer}")

        except GitHubAPIError as e:
            print(f"Warning: Failed to get artifacts for run {run['id']}: {e}")
            continue

    # Build result and find first available reviewer
    selected_reviewer = None
    for reviewer in reviewers:
        username = reviewer["username"]
        max_prs = reviewer["maxOpenPRs"]
        open_prs = reviewer_prs[username]
        has_capacity = len(open_prs) < max_prs

        # Add to result
        result.add_reviewer(username, max_prs, open_prs, has_capacity)

        print(f"Reviewer {username}: {len(open_prs)} open PRs (max: {max_prs})")

        # Select first available reviewer
        if has_capacity and selected_reviewer is None:
            selected_reviewer = username
            print(f"Selected reviewer: {username}")

    result.selected_reviewer = selected_reviewer
    result.all_at_capacity = (selected_reviewer is None)

    return selected_reviewer, result
