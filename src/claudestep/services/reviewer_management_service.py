"""Service Layer class for reviewer management operations.

Follows Service Layer pattern (Fowler, PoEAA) - encapsulates business logic
for reviewer capacity checking and assignment.
"""

from collections import defaultdict
from typing import Any, Dict, List, Optional

from claudestep.infrastructure.github.operations import list_open_pull_requests
from claudestep.services.pr_operations_service import PROperationsService
from claudestep.domain.models import ReviewerCapacityResult
from claudestep.domain.project_configuration import ProjectConfiguration


class ReviewerManagementService:
    """Service Layer class for reviewer management operations.

    Coordinates reviewer capacity checking and assignment by querying
    GitHub API for open PRs. Implements business logic for ClaudeStep's
    reviewer assignment workflow.
    """

    def __init__(self, repo: str):
        self.repo = repo

    # Public API methods

    def find_available_reviewer(
        self, config: ProjectConfiguration, label: str, project: str
    ) -> tuple[Optional[str], ReviewerCapacityResult]:
        """Find first reviewer with capacity based on GitHub API queries

        Args:
            config: ProjectConfiguration domain model with reviewers
            label: GitHub label to filter PRs
            project: Project name to match (used for filtering by branch name pattern)

        Returns:
            Tuple of (username or None, ReviewerCapacityResult)
        """
        result = ReviewerCapacityResult()

        # Initialize reviewer PR lists
        reviewer_prs = defaultdict(list)
        for reviewer in config.reviewers:
            reviewer_prs[reviewer.username] = []

        # Query open PRs for each reviewer from GitHub API
        for reviewer in config.reviewers:
            username = reviewer.username

            # Query GitHub for open PRs assigned to this reviewer with the label
            open_prs = list_open_pull_requests(
                repo=self.repo,
                label=label,
                assignee=username
            )

            # Filter by project name (extract from branch name)
            for pr in open_prs:
                if pr.head_ref_name:
                    # Parse branch name to get project
                    parsed = PROperationsService.parse_branch_name(pr.head_ref_name)
                    if parsed:
                        pr_project, task_index = parsed
                        if pr_project == project:
                            # Extract task description from PR title
                            # PR titles are in format "ClaudeStep: <task description>"
                            task_description = pr.title
                            if task_description.startswith("ClaudeStep: "):
                                task_description = task_description[len("ClaudeStep: "):]

                            pr_info = {
                                "pr_number": pr.number,
                                "task_index": task_index,
                                "task_description": task_description
                            }
                            reviewer_prs[username].append(pr_info)
                            print(f"PR #{pr.number}: reviewer={username}")

        # Build result and find first available reviewer
        selected_reviewer = None
        for reviewer in config.reviewers:
            username = reviewer.username
            max_prs = reviewer.max_open_prs
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
