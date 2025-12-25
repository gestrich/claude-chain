"""Project detection logic"""

import glob
import json
import os
from typing import Optional, Tuple

from claudestep.config import load_json
from claudestep.github_operations import run_gh_command


def detect_project_from_pr(pr_number: str, repo: str) -> Optional[str]:
    """Detect project from merged PR labels

    Args:
        pr_number: PR number to check
        repo: GitHub repository (owner/name)

    Returns:
        Detected project name or None if not found
    """
    print(f"Detecting project from merged PR #{pr_number}...")
    try:
        pr_output = run_gh_command([
            "pr", "view", pr_number,
            "--repo", repo,
            "--json", "labels"
        ])
        pr_data = json.loads(pr_output)
        pr_labels = [label["name"] for label in pr_data.get("labels", [])]
        print(f"PR labels: {pr_labels}")

        # Search for matching refactor project
        for config_file in glob.glob("refactor/*/configuration.json"):
            if os.path.isfile(config_file):
                try:
                    config = load_json(config_file)
                    label = config.get("label")
                    if label in pr_labels:
                        detected_project = config_file.split("/")[1]
                        print(f"✅ Found matching project: {detected_project} (label: {label})")
                        return detected_project
                except Exception as e:
                    print(f"Warning: Failed to read {config_file}: {e}")

        print(f"No refactor project found with matching label for PR #{pr_number}")
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
