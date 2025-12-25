"""GitHub Actions environment integration"""

import os


class GitHubActionsHelper:
    """Handle GitHub Actions environment interactions"""

    def __init__(self):
        self.github_output_file = os.environ.get("GITHUB_OUTPUT")
        self.github_step_summary_file = os.environ.get("GITHUB_STEP_SUMMARY")

    def write_output(self, name: str, value: str) -> None:
        """Write to $GITHUB_OUTPUT for subsequent steps

        Args:
            name: Output variable name
            value: Output variable value
        """
        if not self.github_output_file:
            print(f"{name}={value}")
            return

        with open(self.github_output_file, "a") as f:
            f.write(f"{name}={value}\n")

    def write_step_summary(self, text: str) -> None:
        """Write to $GITHUB_STEP_SUMMARY for workflow summary

        Args:
            text: Markdown text to append to summary
        """
        if not self.github_step_summary_file:
            print(f"SUMMARY: {text}")
            return

        with open(self.github_step_summary_file, "a") as f:
            f.write(f"{text}\n")

    def set_error(self, message: str) -> None:
        """Set error annotation in workflow

        Args:
            message: Error message to display
        """
        print(f"::error::{message}")

    def set_notice(self, message: str) -> None:
        """Set notice annotation in workflow

        Args:
            message: Notice message to display
        """
        print(f"::notice::{message}")

    def set_warning(self, message: str) -> None:
        """Set warning annotation in workflow

        Args:
            message: Warning message to display
        """
        print(f"::warning::{message}")
