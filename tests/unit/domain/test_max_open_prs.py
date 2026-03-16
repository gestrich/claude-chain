"""Tests for maxOpenPRs configuration and capacity checking."""

from claudechain.domain.models import CapacityResult
from claudechain.domain.project import Project
from claudechain.domain.project_configuration import ProjectConfiguration


class TestProjectConfigurationMaxOpenPRs:
    """Test maxOpenPRs in ProjectConfiguration"""

    def test_default_max_open_prs_is_none(self):
        """Should default to None when not specified"""
        project = Project("test-project")
        config = ProjectConfiguration.default(project)
        assert config.max_open_prs is None

    def test_get_max_open_prs_returns_default_when_not_set(self):
        """Should return default of 1 when not configured"""
        project = Project("test-project")
        config = ProjectConfiguration.default(project)
        assert config.get_max_open_prs() == 1

    def test_get_max_open_prs_returns_configured_value(self):
        """Should return configured value when set"""
        project = Project("test-project")
        config = ProjectConfiguration(project=project, max_open_prs=3)
        assert config.get_max_open_prs() == 3

    def test_get_max_open_prs_custom_default(self):
        """Should use custom default when not configured"""
        project = Project("test-project")
        config = ProjectConfiguration.default(project)
        assert config.get_max_open_prs(default=5) == 5

    def test_from_yaml_string_with_max_open_prs(self):
        """Should parse maxOpenPRs from YAML configuration"""
        project = Project("test-project")
        yaml_content = """
assignee: alice
maxOpenPRs: 3
"""
        config = ProjectConfiguration.from_yaml_string(project, yaml_content)
        assert config.max_open_prs == 3
        assert config.get_max_open_prs() == 3

    def test_from_yaml_string_without_max_open_prs(self):
        """Should have None maxOpenPRs when not specified in YAML"""
        project = Project("test-project")
        yaml_content = """
assignee: alice
"""
        config = ProjectConfiguration.from_yaml_string(project, yaml_content)
        assert config.max_open_prs is None
        assert config.get_max_open_prs() == 1

    def test_to_dict_includes_max_open_prs(self):
        """Should include maxOpenPRs in dict when set"""
        project = Project("test-project")
        config = ProjectConfiguration(project=project, max_open_prs=3)
        result = config.to_dict()
        assert result["maxOpenPRs"] == 3

    def test_to_dict_excludes_max_open_prs_when_none(self):
        """Should not include maxOpenPRs in dict when not set"""
        project = Project("test-project")
        config = ProjectConfiguration.default(project)
        result = config.to_dict()
        assert "maxOpenPRs" not in result


class TestCapacityResultMaxOpenPRs:
    """Test CapacityResult with maxOpenPRs"""

    def test_default_max_open_prs_is_one(self):
        """Should default max_open_prs to 1"""
        result = CapacityResult(
            has_capacity=True,
            assignee=None,
            open_prs=[],
            project_name="test"
        )
        assert result.max_open_prs == 1

    def test_format_summary_shows_configured_max(self):
        """Should display configured max in summary"""
        result = CapacityResult(
            has_capacity=True,
            assignee="alice",
            open_prs=[{"pr_number": 1, "task_description": "task"}],
            project_name="test",
            max_open_prs=3
        )
        summary = result.format_summary()
        assert "**Max PRs Allowed:** 3" in summary
        assert "**Currently Open:** 1/3" in summary

    def test_format_summary_shows_default_max(self):
        """Should display default max of 1 in summary"""
        result = CapacityResult(
            has_capacity=False,
            assignee=None,
            open_prs=[{"pr_number": 1, "task_description": "task"}],
            project_name="test"
        )
        summary = result.format_summary()
        assert "**Max PRs Allowed:** 1" in summary
        assert "**Currently Open:** 1/1" in summary
