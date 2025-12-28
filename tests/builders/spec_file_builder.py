"""Builder for creating test spec.md file content"""

from typing import List, Optional
from pathlib import Path


class SpecFileBuilder:
    """Fluent interface for creating spec.md file content

    Provides a clean way to build spec.md files with various task states
    for testing.

    Example:
        spec = SpecFileBuilder()
            .with_title("My Project")
            .with_overview("This is a test project")
            .add_completed_task("Task 1")
            .add_completed_task("Task 2")
            .add_task("Task 3")
            .add_task("Task 4")
            .build()
    """

    def __init__(self):
        """Initialize builder with default values"""
        self._title: str = "Project Specification"
        self._overview: Optional[str] = None
        self._tasks: List[tuple[bool, str]] = []  # List of (completed, description)
        self._custom_sections: List[str] = []

    def with_title(self, title: str) -> "SpecFileBuilder":
        """Set the document title

        Args:
            title: Main heading text

        Returns:
            Self for method chaining
        """
        self._title = title
        return self

    def with_overview(self, overview: str) -> "SpecFileBuilder":
        """Add an overview section

        Args:
            overview: Overview text

        Returns:
            Self for method chaining
        """
        self._overview = overview
        return self

    def add_task(self, description: str, completed: bool = False) -> "SpecFileBuilder":
        """Add a task to the spec

        Args:
            description: Task description
            completed: Whether the task is completed (default: False)

        Returns:
            Self for method chaining
        """
        self._tasks.append((completed, description))
        return self

    def add_completed_task(self, description: str) -> "SpecFileBuilder":
        """Add a completed task

        Args:
            description: Task description

        Returns:
            Self for method chaining
        """
        return self.add_task(description, completed=True)

    def add_tasks(self, *descriptions: str, completed: bool = False) -> "SpecFileBuilder":
        """Add multiple tasks at once

        Args:
            *descriptions: Task descriptions
            completed: Whether all tasks are completed (default: False)

        Returns:
            Self for method chaining
        """
        for desc in descriptions:
            self.add_task(desc, completed)
        return self

    def add_section(self, section_markdown: str) -> "SpecFileBuilder":
        """Add a custom markdown section

        Args:
            section_markdown: Raw markdown content

        Returns:
            Self for method chaining
        """
        self._custom_sections.append(section_markdown)
        return self

    def build(self) -> str:
        """Build and return the spec.md content

        Returns:
            Complete spec.md file content as a string
        """
        lines = []

        # Title
        lines.append(f"# {self._title}")
        lines.append("")

        # Overview section
        if self._overview:
            lines.append("## Overview")
            lines.append(self._overview)
            lines.append("")

        # Tasks section
        if self._tasks:
            lines.append("## Tasks")
            lines.append("")
            for completed, description in self._tasks:
                checkbox = "[x]" if completed else "[ ]"
                lines.append(f"- {checkbox} {description}")
            lines.append("")

        # Custom sections
        for section in self._custom_sections:
            lines.append(section)
            if not section.endswith("\n"):
                lines.append("")

        return "\n".join(lines)

    def write_to(self, path: Path) -> Path:
        """Build and write the spec.md content to a file

        Args:
            path: Path to write the file (can be directory or file path)

        Returns:
            Path to the written file
        """
        if path.is_dir():
            file_path = path / "spec.md"
        else:
            file_path = path

        file_path.write_text(self.build())
        return file_path

    @staticmethod
    def empty() -> str:
        """Quick helper for an empty spec with no tasks

        Returns:
            Spec content with no tasks
        """
        return (SpecFileBuilder()
                .with_overview("This project has no tasks yet.")
                .build())

    @staticmethod
    def all_completed(num_tasks: int = 3) -> str:
        """Quick helper for a spec with all tasks completed

        Args:
            num_tasks: Number of completed tasks (default: 3)

        Returns:
            Spec content with all tasks completed
        """
        builder = SpecFileBuilder()
        for i in range(1, num_tasks + 1):
            builder.add_completed_task(f"Task {i}")
        return builder.build()

    @staticmethod
    def mixed_progress(completed: int = 2, pending: int = 3) -> str:
        """Quick helper for a spec with mixed task states

        Args:
            completed: Number of completed tasks (default: 2)
            pending: Number of pending tasks (default: 3)

        Returns:
            Spec content with mixed task states
        """
        builder = SpecFileBuilder()

        # Add completed tasks
        for i in range(1, completed + 1):
            builder.add_completed_task(f"Task {i}")

        # Add pending tasks
        for i in range(completed + 1, completed + pending + 1):
            builder.add_task(f"Task {i}")

        return builder.build()

    @staticmethod
    def default() -> str:
        """Quick helper for a default spec (matching conftest.py fixture)

        Creates a spec with:
        - 2 completed tasks
        - 3 pending tasks

        Returns:
            Default spec content matching sample_spec_file fixture
        """
        return SpecFileBuilder.mixed_progress(completed=2, pending=3)
