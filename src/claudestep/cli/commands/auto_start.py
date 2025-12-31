"""CLI command for auto-start workflow.

Orchestrates Service Layer classes to detect new projects and make
auto-trigger decisions. This command instantiates services and coordinates
their operations but does not implement business logic directly.
"""

import os
from typing import List

from claudestep.domain.auto_start import AutoStartProject
from claudestep.infrastructure.github.actions import GitHubActionsHelper
from claudestep.services.composite.auto_start_service import AutoStartService
from claudestep.services.core.pr_service import PRService


def cmd_auto_start(
    gh: GitHubActionsHelper,
    repo: str,
    base_branch: str,
    ref_before: str,
    ref_after: str
) -> int:
    """Detect new projects and determine which should be auto-triggered.

    This command uses AutoStartService to orchestrate the auto-start workflow:
    1. Detect changed spec.md files
    2. Determine which projects are new (no existing PRs)
    3. Make auto-trigger decisions based on business logic

    Args:
        gh: GitHub Actions helper instance
        repo: GitHub repository (owner/name)
        base_branch: Base branch name (e.g., "main")
        ref_before: Git reference before the push (commit SHA)
        ref_after: Git reference after the push (commit SHA)

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        print("=== ClaudeStep Auto-Start Detection ===\n")
        print(f"Repository: {repo}")
        print(f"Base branch: {base_branch}")
        print(f"Checking changes: {ref_before[:8]}...{ref_after[:8]}\n")

        # === Initialize services ===
        pr_service = PRService(repo)
        auto_start_service = AutoStartService(repo, pr_service)

        # === Step 1: Detect changed projects ===
        print("=== Step 1/3: Detecting changed projects ===")
        changed_projects = auto_start_service.detect_changed_projects(
            ref_before=ref_before,
            ref_after=ref_after,
            spec_pattern="claude-step/*/spec.md"
        )

        if not changed_projects:
            print("No spec.md changes detected\n")
            gh.write_output("projects_to_trigger", "")
            gh.write_output("project_count", "0")
            return 0

        print(f"Found {len(changed_projects)} changed project(s):")
        for project in changed_projects:
            print(f"  - {project.name} ({project.change_type.value})")
        print()

        # === Step 2: Determine new projects ===
        print("=== Step 2/3: Determining new projects ===")
        new_projects = auto_start_service.determine_new_projects(changed_projects)

        if not new_projects:
            print("\nNo new projects to trigger (all have existing PRs)\n")
            gh.write_output("projects_to_trigger", "")
            gh.write_output("project_count", "0")
            return 0

        print(f"\nFound {len(new_projects)} new project(s) to trigger\n")

        # === Step 3: Make auto-trigger decisions ===
        print("=== Step 3/3: Making auto-trigger decisions ===")
        projects_to_trigger: List[str] = []

        for project in new_projects:
            decision = auto_start_service.should_auto_trigger(project)

            if decision.should_trigger:
                projects_to_trigger.append(project.name)
                print(f"  ✓ {project.name}: TRIGGER - {decision.reason}")
            else:
                print(f"  ✗ {project.name}: SKIP - {decision.reason}")

        print()

        # === Write outputs ===
        if projects_to_trigger:
            # Format as space-separated list for GitHub Actions matrix
            projects_output = " ".join(projects_to_trigger)
            gh.write_output("projects_to_trigger", projects_output)
            gh.write_output("project_count", str(len(projects_to_trigger)))

            print(f"✅ Auto-start detection complete")
            print(f"   Projects to trigger: {projects_output}")
            print(f"   Total count: {len(projects_to_trigger)}")
        else:
            gh.write_output("projects_to_trigger", "")
            gh.write_output("project_count", "0")
            print("✅ Auto-start detection complete (no projects to trigger)")

        return 0

    except Exception as e:
        gh.set_error(f"Auto-start detection failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
