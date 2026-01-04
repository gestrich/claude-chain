"""Core service for project detection operations.

Follows Service Layer pattern (Fowler, PoEAA) - encapsulates business logic
for detecting projects from PRs and determining project paths.
"""

import json
import re
from typing import List, Optional, Tuple

from claudechain.infrastructure.github.operations import run_gh_command
from claudechain.services.core.pr_service import PRService
from claudechain.domain.project import Project


class ProjectService:
    """Core service for project detection operations.

    Coordinates project detection by orchestrating PR operations and path
    resolution. Implements business logic for identifying ClaudeChain projects
    from various inputs.
    """

    def __init__(self, repo: str):
        """Initialize project service

        Args:
            repo: GitHub repository (owner/name)
        """
        self.repo = repo

    # Public API methods

    def detect_project_from_pr(self, pr_number: str) -> Optional[str]:
        """Detect project from merged PR branch name

        Args:
            pr_number: PR number to check

        Returns:
            Detected project name or None if not found
        """
        print(f"Detecting project from merged PR #{pr_number}...")
        try:
            # Get the branch name from the PR
            pr_output = run_gh_command([
                "pr", "view", pr_number,
                "--repo", self.repo,
                "--json", "headRefName"
            ])
            pr_data = json.loads(pr_output)
            branch_name = pr_data.get("headRefName")

            if not branch_name:
                print(f"Failed to get branch name for PR #{pr_number}")
                return None

            print(f"PR branch: {branch_name}")

            # Extract project name from branch name using standard format
            # Expected format: claude-chain-{project}-{hash}
            result = PRService.parse_branch_name(branch_name)

            if result:
                print(f"✅ Detected project '{result.project_name}' from branch '{branch_name}'")
                return result.project_name
            else:
                print(f"Could not parse branch '{branch_name}' - not in expected format claude-chain-{{project}}-{{hash}}")
                return None

        except Exception as e:
            print(f"Failed to detect project from PR: {str(e)}")
            return None

    # Static utility methods

    @staticmethod
    def detect_project_paths(project_name: str) -> Tuple[str, str, str, str]:
        """Determine project paths from project name (DEPRECATED - use Project domain model)

        Projects must be located in the claude-chain/ directory with standard file names.

        Args:
            project_name: Name of the project

        Returns:
            Tuple of (config_path, spec_path, pr_template_path, project_path)

        Deprecated:
            Use Project(project_name) and access properties directly instead:
            - project.config_path
            - project.spec_path
            - project.pr_template_path
            - project.base_path
        """
        project = Project(project_name)

        print(f"Configuration paths:")
        print(f"  Project: {project_name}")
        print(f"  Config: {project.config_path}")
        print(f"  Spec: {project.spec_path}")
        print(f"  PR Template: {project.pr_template_path}")

        return project.config_path, project.spec_path, project.pr_template_path, project.base_path

    @staticmethod
    def detect_projects_from_merge(changed_files: List[str]) -> List[Project]:
        """Detect projects from changed spec.md files in a merge.

        This function is used to automatically trigger ClaudeChain when spec files
        are changed, regardless of branch naming conventions or labels. It enables
        the "changed files" triggering model where:
        - Initial spec merge: User creates PR with spec.md, merges it, workflow triggers
        - Subsequent merges: System-created PRs merge, workflow triggers same way

        Args:
            changed_files: List of file paths that changed in the merge

        Returns:
            List of Project objects for projects with changed spec.md files.
            Empty list if no spec files were changed.

        Examples:
            >>> files = ["claude-chain/my-project/spec.md", "README.md"]
            >>> projects = ProjectService.detect_projects_from_merge(files)
            >>> [p.name for p in projects]
            ['my-project']

            >>> files = ["claude-chain/project-a/spec.md", "claude-chain/project-b/spec.md"]
            >>> projects = ProjectService.detect_projects_from_merge(files)
            >>> sorted([p.name for p in projects])
            ['project-a', 'project-b']

            >>> files = ["src/main.py", "README.md"]
            >>> ProjectService.detect_projects_from_merge(files)
            []
        """
        spec_pattern = re.compile(r"^claude-chain/([^/]+)/spec\.md$")
        project_names = set()

        for file_path in changed_files:
            match = spec_pattern.match(file_path)
            if match:
                project_names.add(match.group(1))

        return [Project(name) for name in sorted(project_names)]
