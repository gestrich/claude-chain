"""Builder for creating test configuration data"""

from typing import Dict, Any, List


class ConfigBuilder:
    """Fluent interface for creating test configuration dictionaries

    Provides a clean, readable way to create configuration data for tests
    with sensible defaults.

    Example:
        config = ConfigBuilder()
            .with_reviewer("alice", max_prs=2)
            .with_reviewer("bob", max_prs=3)
            .with_project("my-project")
            .build()
    """

    def __init__(self):
        """Initialize builder with default values"""
        self._reviewers: List[Dict[str, Any]] = []
        self._project: str = "sample-project"
        self._custom_fields: Dict[str, Any] = {}

    def with_reviewer(self, username: str, max_prs: int = 2) -> "ConfigBuilder":
        """Add a reviewer to the configuration

        Args:
            username: GitHub username of the reviewer
            max_prs: Maximum number of open PRs allowed (default: 2)

        Returns:
            Self for method chaining
        """
        self._reviewers.append({
            "username": username,
            "maxOpenPRs": max_prs
        })
        return self

    def with_reviewers(self, *reviewers: tuple) -> "ConfigBuilder":
        """Add multiple reviewers at once

        Args:
            *reviewers: Tuples of (username, max_prs)

        Returns:
            Self for method chaining

        Example:
            builder.with_reviewers(
                ("alice", 2),
                ("bob", 3),
                ("charlie", 1)
            )
        """
        for username, max_prs in reviewers:
            self.with_reviewer(username, max_prs)
        return self

    def with_project(self, project_name: str) -> "ConfigBuilder":
        """Set the project name

        Args:
            project_name: Name of the project

        Returns:
            Self for method chaining
        """
        self._project = project_name
        return self

    def with_field(self, key: str, value: Any) -> "ConfigBuilder":
        """Add a custom field to the configuration

        Useful for testing edge cases or new configuration options.

        Args:
            key: Field name
            value: Field value

        Returns:
            Self for method chaining
        """
        self._custom_fields[key] = value
        return self

    def with_no_reviewers(self) -> "ConfigBuilder":
        """Clear all reviewers (for testing empty reviewer list)

        Returns:
            Self for method chaining
        """
        self._reviewers = []
        return self

    def build(self) -> Dict[str, Any]:
        """Build and return the configuration dictionary

        Returns:
            Complete configuration dictionary ready for use in tests
        """
        config = {
            "reviewers": self._reviewers,
            "project": self._project
        }

        # Merge any custom fields
        config.update(self._custom_fields)

        return config

    @staticmethod
    def single_reviewer(username: str = "alice", max_prs: int = 2) -> Dict[str, Any]:
        """Quick helper for creating a config with a single reviewer

        Args:
            username: GitHub username (default: "alice")
            max_prs: Maximum open PRs (default: 2)

        Returns:
            Configuration dictionary with one reviewer
        """
        return ConfigBuilder().with_reviewer(username, max_prs).build()

    @staticmethod
    def default() -> Dict[str, Any]:
        """Quick helper for creating a default configuration

        Creates a configuration with three reviewers:
        - alice (max 2 PRs)
        - bob (max 3 PRs)
        - charlie (max 1 PR)

        Returns:
            Default configuration dictionary
        """
        return (ConfigBuilder()
                .with_reviewer("alice", 2)
                .with_reviewer("bob", 3)
                .with_reviewer("charlie", 1)
                .build())
