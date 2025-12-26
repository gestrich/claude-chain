"""Project detection logic"""

import glob
import json
import os
from typing import Optional, Tuple

from claudestep.config import load_json
from claudestep.github_operations import run_gh_command


def detect_project_from_pr(pr_number: str, repo: str) -> Optional[str]:
    """Detect project from merged PR artifact metadata

    Args:
        pr_number: PR number to check
        repo: GitHub repository (owner/name)

    Returns:
        Detected project name or None if not found
    """
    print(f"Detecting project from merged PR #{pr_number}...")
    try:
        # First get the branch name from the PR
        pr_output = run_gh_command([
            "pr", "view", pr_number,
            "--repo", repo,
            "--json", "headRefName"
        ])
        pr_data = json.loads(pr_output)
        branch_name = pr_data.get("headRefName")

        if not branch_name:
            print(f"Failed to get branch name for PR #{pr_number}")
            return None

        print(f"PR branch: {branch_name}")

        # Get workflow runs for this branch
        from claudestep.github_operations import gh_api_call, download_artifact_json

        api_response = gh_api_call(
            f"/repos/{repo}/actions/runs?branch={branch_name}&status=completed&per_page=10"
        )
        runs = api_response.get("workflow_runs", [])

        # Check most recent successful runs for artifact metadata
        for run in runs:
            if run.get("conclusion") == "success":
                try:
                    artifacts_data = gh_api_call(
                        f"/repos/{repo}/actions/runs/{run['id']}/artifacts"
                    )
                    artifacts = artifacts_data.get("artifacts", [])

                    # Look for task metadata artifacts
                    for artifact in artifacts:
                        name = artifact["name"]
                        if name.startswith("task-metadata-"):
                            # Download and parse the artifact
                            artifact_id = artifact["id"]
                            metadata = download_artifact_json(repo, artifact_id)

                            if metadata and "project" in metadata:
                                project = metadata["project"]
                                print(f"✅ Found project from artifact: {project}")
                                return project
                except Exception as e:
                    print(f"Warning: Failed to check artifacts for run {run['id']}: {e}")
                    continue

        print(f"No artifact metadata found for PR #{pr_number}")
        return None
    except Exception as e:
        print(f"Failed to detect project from PR: {str(e)}")
        return None


def detect_project_paths(project_name: str, config_path_input: str = "",
                        spec_path_input: str = "", pr_template_path_input: str = "") -> Tuple[str, str, str, str]:
    """Determine project paths from project name and optional overrides

    Args:
        project_name: Name of the project
        config_path_input: Optional override for config path
        spec_path_input: Optional override for spec path
        pr_template_path_input: Optional override for PR template path

    Returns:
        Tuple of (config_path, spec_path, pr_template_path, project_path)
    """
    config_path = config_path_input or f"refactor/{project_name}/configuration.json"
    spec_path = spec_path_input or f"refactor/{project_name}/spec.md"
    pr_template_path = pr_template_path_input or f"refactor/{project_name}/pr-template.md"
    project_path = f"refactor/{project_name}"

    print(f"Configuration paths:")
    print(f"  Project: {project_name}")
    print(f"  Config: {config_path}")
    print(f"  Spec: {spec_path}")
    print(f"  PR Template: {pr_template_path}")

    return config_path, spec_path, pr_template_path, project_path
