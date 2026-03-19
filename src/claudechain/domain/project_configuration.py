"""Domain models for project configuration"""

from dataclasses import dataclass, field
from typing import List, Optional

from claudechain.domain.constants import DEFAULT_STALE_PR_DAYS
from claudechain.domain.project import Project


@dataclass
class ProjectConfiguration:
    """Domain model for parsed project configuration

    ClaudeChain enforces a single open PR per project. The optional assignees
    are assigned to PRs when created. Use the `reviewers` list for people who
    review but should not be assigned.
    """

    project: Project
    base_branch: Optional[str] = None  # Optional override for target base branch
    allowed_tools: Optional[str] = None  # Optional override for Claude's allowed tools
    stale_pr_days: Optional[int] = None  # Days before a PR is considered stale
    labels: Optional[str] = None  # Optional comma-separated labels to apply to PRs
    max_open_prs: Optional[int] = None  # Max concurrent open PRs per project
    assignees: List[str] = field(default_factory=list)
    reviewers: List[str] = field(default_factory=list)

    @classmethod
    def default(cls, project: Project) -> 'ProjectConfiguration':
        """Factory: Create default configuration when no config file exists.

        Default configuration:
        - No assignee (PRs created without assignee)
        - No base branch override (uses workflow default)
        - No allowed tools override (uses workflow default)
        - No labels override (uses workflow default)

        Args:
            project: Project domain model

        Returns:
            ProjectConfiguration with sensible defaults
        """
        return cls(
            project=project,
            base_branch=None,
            allowed_tools=None,
            stale_pr_days=None,
            labels=None,
            max_open_prs=None,
        )

    @classmethod
    def from_yaml_string(cls, project: Project, yaml_content: str) -> 'ProjectConfiguration':
        """Factory: Parse configuration from YAML string

        Args:
            project: Project domain model
            yaml_content: YAML content as string

        Returns:
            ProjectConfiguration instance
        """
        from claudechain.domain.config import load_config_from_string

        config = load_config_from_string(yaml_content, project.config_path)
        base_branch = config.get("baseBranch")
        allowed_tools = config.get("allowedTools")
        stale_pr_days = config.get("stalePRDays")
        labels = config.get("labels")
        max_open_prs = config.get("maxOpenPRs")

        # `assignees` list takes precedence; legacy `assignee` is folded in here at parse time
        yaml_assignees = config.get("assignees")
        if yaml_assignees is not None:
            assignees = [str(a) for a in yaml_assignees]
        elif config.get("assignee"):
            assignees = [config["assignee"]]
        else:
            assignees = []

        yaml_reviewers = config.get("reviewers")
        reviewers = [str(r) for r in yaml_reviewers] if yaml_reviewers is not None else []

        return cls(
            project=project,
            base_branch=base_branch,
            allowed_tools=allowed_tools,
            stale_pr_days=stale_pr_days,
            labels=labels,
            max_open_prs=max_open_prs,
            assignees=assignees,
            reviewers=reviewers,
        )

    def get_base_branch(self, default_base_branch: str) -> str:
        """Resolve base branch from project config or fall back to default.

        Args:
            default_base_branch: Default from workflow/CLI (required, no default here)

        Returns:
            Project's baseBranch if set, otherwise the default
        """
        if self.base_branch:
            return self.base_branch
        return default_base_branch

    def get_allowed_tools(self, default_allowed_tools: str) -> str:
        """Resolve allowed tools from project config or fall back to default.

        Args:
            default_allowed_tools: Default from workflow/CLI (required, no default here)

        Returns:
            Project's allowedTools if set, otherwise the default
        """
        if self.allowed_tools:
            return self.allowed_tools
        return default_allowed_tools

    def get_stale_pr_days(self, default: int = DEFAULT_STALE_PR_DAYS) -> int:
        """Get the number of days before a PR is considered stale.

        Args:
            default: Default value if not configured (default: DEFAULT_STALE_PR_DAYS)

        Returns:
            stalePRDays from config if set, otherwise the default
        """
        if self.stale_pr_days is not None:
            return self.stale_pr_days
        return default

    def get_max_open_prs(self, default: int = 1) -> int:
        """Get the maximum number of concurrent open PRs allowed.

        Args:
            default: Default value if not configured (default: 1)

        Returns:
            maxOpenPRs from config if set, otherwise the default
        """
        if self.max_open_prs is not None:
            return self.max_open_prs
        return default

    def get_labels(self, default_labels: str) -> str:
        """Resolve labels from project config or fall back to default.

        Args:
            default_labels: Default from workflow/CLI (required, no default here)

        Returns:
            Project's labels if set, otherwise the default
        """
        if self.labels:
            return self.labels
        return default_labels

    def to_dict(self) -> dict:
        """Convert to dictionary representation

        Returns:
            Dictionary with project and configuration
        """
        result = {
            "project": self.project.name,
        }
        if self.assignees:
            result["assignees"] = self.assignees
        if self.reviewers:
            result["reviewers"] = self.reviewers
        if self.base_branch:
            result["baseBranch"] = self.base_branch
        if self.allowed_tools:
            result["allowedTools"] = self.allowed_tools
        if self.stale_pr_days is not None:
            result["stalePRDays"] = self.stale_pr_days
        if self.labels:
            result["labels"] = self.labels
        if self.max_open_prs is not None:
            result["maxOpenPRs"] = self.max_open_prs
        return result
