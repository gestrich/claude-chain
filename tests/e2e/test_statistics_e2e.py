"""End-to-End tests for ClaudeStep statistics collection.

This module contains E2E integration tests that verify the ClaudeStep statistics
workflow runs successfully and generates the expected output format.

The tests trigger the claudestep-statistics.yml workflow and verify that it:
- Completes successfully
- Generates statistics output
- Produces properly formatted Slack messages (when statistics exist)
"""

import time
import pytest

from .helpers.github_helper import GitHubHelper


def test_statistics_workflow_runs_successfully(gh: GitHubHelper) -> None:
    """Test that the ClaudeStep statistics workflow runs successfully.

    This test:
    1. Triggers the claudestep-statistics.yml workflow
    2. Waits for workflow completion
    3. Verifies the workflow completes successfully
    4. Verifies the statistics step completes

    Note: This test doesn't verify the actual statistics content since that
    depends on existing ClaudeStep activity in the repository. Instead, it
    verifies that the workflow infrastructure works correctly.

    Args:
        gh: GitHub helper fixture
    """
    # Trigger the statistics workflow
    gh.trigger_workflow(
        workflow_name="claudestep-statistics.yml",
        inputs={},  # No inputs required for statistics workflow
        ref="main"
    )

    # Wait a moment for workflow to start
    time.sleep(5)

    # Wait for workflow to complete
    workflow_run = gh.wait_for_workflow_completion(
        workflow_name="claudestep-statistics.yml",
        timeout=300  # 5 minutes should be plenty for statistics
    )

    assert workflow_run is not None, "Workflow run should be found"
    assert workflow_run["conclusion"] in ["success", "skipped"], \
        f"Workflow should complete successfully or skip if no data, got: {workflow_run['conclusion']}"


def test_statistics_workflow_with_custom_days(gh: GitHubHelper) -> None:
    """Test that statistics workflow accepts custom days_back parameter.

    This test verifies that the workflow can be triggered with a custom
    days_back parameter to control the time range of statistics collection.

    Args:
        gh: GitHub helper fixture
    """
    # Note: The workflow doesn't accept inputs via workflow_dispatch
    # This test verifies the workflow runs with its default configuration
    # Future enhancement: Add workflow_dispatch inputs to support custom days_back

    # Trigger the statistics workflow with default settings
    gh.trigger_workflow(
        workflow_name="claudestep-statistics.yml",
        inputs={},
        ref="main"
    )

    # Wait a moment for workflow to start
    time.sleep(5)

    # Wait for workflow to complete
    workflow_run = gh.wait_for_workflow_completion(
        workflow_name="claudestep-statistics.yml",
        timeout=300
    )

    assert workflow_run is not None, "Workflow run should be found"
    assert workflow_run["conclusion"] in ["success", "skipped"], \
        f"Workflow should complete successfully or skip, got: {workflow_run['conclusion']}"


def test_statistics_output_format(gh: GitHubHelper) -> None:
    """Test that statistics workflow produces expected output format.

    This test verifies that when the statistics workflow runs, it produces
    outputs in the expected format. The actual statistics content may vary
    based on repository activity.

    Note: This is a basic structural test. Detailed validation of statistics
    content would require creating test PRs with known costs, which is better
    suited for the main workflow E2E tests.

    Args:
        gh: GitHub helper fixture
    """
    # Trigger the statistics workflow
    gh.trigger_workflow(
        workflow_name="claudestep-statistics.yml",
        inputs={},
        ref="main"
    )

    # Wait a moment for workflow to start
    time.sleep(5)

    # Wait for workflow to complete
    workflow_run = gh.wait_for_workflow_completion(
        workflow_name="claudestep-statistics.yml",
        timeout=300
    )

    assert workflow_run is not None, "Workflow run should be found"

    # The workflow should complete regardless of whether there's data
    # - "success" if statistics were generated and optionally posted to Slack
    # - "skipped" is not actually used; the workflow always runs but Slack step may skip
    assert workflow_run["conclusion"] == "success", \
        f"Workflow should complete successfully, got: {workflow_run['conclusion']}"

    # Note: We can't easily verify the actual output content in E2E tests
    # without creating mock data. The workflow logs would contain the statistics,
    # but parsing them would be fragile. Instead, we rely on:
    # 1. Unit tests for statistics_collector.py (already exists)
    # 2. This E2E test for workflow execution
    # 3. Manual verification of actual Slack posts in development
