"""Tests for Slack block limit and completed project filtering."""
import sys
from io import StringIO

from claudechain.domain.models import ProjectStats, StatisticsReport


def _make_project(name: str, total: int, completed: int) -> ProjectStats:
    """Helper to create a ProjectStats with given counts."""
    ps = ProjectStats(project_name=name, spec_path=f"projects/{name}/spec.md")
    ps.total_tasks = total
    ps.completed_tasks = completed
    return ps


class TestCompletedProjectsDefault:
    """By default, completed projects should be included."""

    def test_completed_project_included_by_default(self):
        report = StatisticsReport(repo="owner/repo")
        report.add_project(_make_project("done-project", total=5, completed=5))
        report.add_project(_make_project("active-project", total=5, completed=2))

        result = report.format_for_slack_blocks()
        blocks_text = str(result["blocks"])

        assert "active-project" in blocks_text
        assert "done-project" in blocks_text

    def test_completed_project_excluded_when_flag_false(self):
        report = StatisticsReport(repo="owner/repo")
        report.add_project(_make_project("done-project", total=5, completed=5))
        report.add_project(_make_project("active-project", total=5, completed=2))

        result = report.format_for_slack_blocks(hide_completed_projects=True)
        blocks_text = str(result["blocks"])

        assert "active-project" in blocks_text
        assert "done-project" not in blocks_text

    def test_all_completed_hidden_still_returns_valid_payload(self):
        report = StatisticsReport(repo="owner/repo")
        report.add_project(_make_project("done1", total=3, completed=3))
        report.add_project(_make_project("done2", total=2, completed=2))

        result = report.format_for_slack_blocks(hide_completed_projects=True)
        # Should still return a valid payload (header at minimum)
        assert "blocks" in result

    def test_partially_completed_project_always_included(self):
        report = StatisticsReport(repo="owner/repo")
        report.add_project(_make_project("partial", total=5, completed=4))

        result = report.format_for_slack_blocks(hide_completed_projects=True)
        blocks_text = str(result["blocks"])
        assert "partial" in blocks_text


class TestSlackBlockTruncation:
    """Blocks should be truncated to 50 with a stderr warning."""

    def test_many_projects_truncated_to_50_blocks(self):
        report = StatisticsReport(repo="owner/repo")
        # Each project generates multiple blocks; 30 projects should exceed 50
        for i in range(30):
            report.add_project(_make_project(f"project-{i:02d}", total=5, completed=i % 5))

        captured_stderr = StringIO()
        old_stderr = sys.stderr
        sys.stderr = captured_stderr
        try:
            result = report.format_for_slack_blocks()
        finally:
            sys.stderr = old_stderr

        assert len(result["blocks"]) <= 50
        assert len(result["blocks"]) == 50  # exactly 50 (49 real + 1 indicator)
        stderr_output = captured_stderr.getvalue()
        assert "truncated" in stderr_output.lower()

    def test_truncation_indicator_within_limit(self):
        """The truncation indicator block itself must be within the 50-block limit."""
        report = StatisticsReport(repo="owner/repo")
        for i in range(30):
            report.add_project(_make_project(f"project-{i:02d}", total=5, completed=i % 5))

        captured_stderr = StringIO()
        old_stderr = sys.stderr
        sys.stderr = captured_stderr
        try:
            result = report.format_for_slack_blocks()
        finally:
            sys.stderr = old_stderr

        # Last block should be the truncation indicator
        last_block = result["blocks"][-1]
        assert last_block["type"] == "context"
        assert "truncated" in str(last_block).lower()
        # Total must be exactly 50
        assert len(result["blocks"]) == 50

    def test_few_projects_not_truncated(self):
        report = StatisticsReport(repo="owner/repo")
        report.add_project(_make_project("small", total=3, completed=1))

        captured_stderr = StringIO()
        old_stderr = sys.stderr
        sys.stderr = captured_stderr
        try:
            result = report.format_for_slack_blocks()
        finally:
            sys.stderr = old_stderr

        assert len(result["blocks"]) <= 50
        assert "truncated" not in captured_stderr.getvalue().lower()
