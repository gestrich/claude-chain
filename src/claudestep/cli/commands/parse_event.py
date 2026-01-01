"""Parse GitHub event and output action parameters.

This command handles event parsing for the simplified workflow, where users
pass the GitHub event context directly to the action. It parses the event,
determines if execution should be skipped, and outputs the appropriate
parameters for subsequent steps.
"""

import os
from typing import Optional

from claudestep.domain.github_event import GitHubEventContext
from claudestep.infrastructure.github.actions import GitHubActionsHelper


def cmd_parse_event(
    gh: GitHubActionsHelper,
    event_name: str,
    event_json: str,
    project_name: Optional[str] = None,
    default_base_branch: str = "main",
    pr_label: str = "claudestep",
) -> int:
    """Parse GitHub event and output action parameters.

    This command is invoked by the action.yml to handle the simplified workflow.
    It parses the GitHub event payload and determines:
    - Whether execution should be skipped (and why)
    - The git ref to checkout
    - The project name (from branch pattern or override)
    - The base branch for PR creation
    - The merged PR number (for pull_request events)

    Args:
        gh: GitHubActionsHelper for writing outputs
        event_name: GitHub event name (e.g., "pull_request", "push", "workflow_dispatch")
        event_json: JSON payload from ${{ toJson(github.event) }}
        project_name: Optional project name override (for workflow_dispatch)
        default_base_branch: Default base branch if not determined from event
        pr_label: Required label for pull_request events

    Returns:
        0 on success, 1 on error

    Outputs (via GITHUB_OUTPUT):
        skip: "true" or "false"
        skip_reason: Reason for skipping (if skip is true)
        checkout_ref: Git ref to checkout
        project_name: Resolved project name
        base_branch: Base branch for PR creation
        merged_pr_number: PR number (for pull_request events)
    """
    try:
        print("=== ClaudeStep Event Parsing ===")
        print(f"Event name: {event_name}")
        print(f"Project name override: {project_name or '(none)'}")
        print(f"Default base branch: {default_base_branch}")
        print(f"Required PR label: {pr_label}")

        # Parse the event
        context = GitHubEventContext.from_json(event_name, event_json)
        print(f"\nParsed event context:")
        print(f"  Event type: {context.event_name}")
        if context.pr_number:
            print(f"  PR number: {context.pr_number}")
            print(f"  PR merged: {context.pr_merged}")
            print(f"  PR labels: {context.pr_labels}")
        if context.head_ref:
            print(f"  Head ref: {context.head_ref}")
        if context.base_ref:
            print(f"  Base ref: {context.base_ref}")
        if context.ref_name:
            print(f"  Ref name: {context.ref_name}")

        # Check if should skip
        should_skip, reason = context.should_skip(required_label=pr_label)
        if should_skip:
            print(f"\n⏭️  Skipping: {reason}")
            gh.write_output("skip", "true")
            gh.write_output("skip_reason", reason)
            return 0

        # Determine project name
        resolved_project = project_name
        if not resolved_project:
            resolved_project = context.extract_project_from_branch()

        if not resolved_project:
            # For workflow_dispatch without project_name, this is an error
            # For other events, we may need the project from the branch pattern
            if event_name == "workflow_dispatch":
                reason = "No project_name provided for workflow_dispatch event"
            else:
                reason = "Could not determine project name from branch pattern"
            print(f"\n⏭️  Skipping: {reason}")
            gh.write_output("skip", "true")
            gh.write_output("skip_reason", reason)
            return 0

        # Determine checkout ref and base branch
        try:
            checkout_ref = context.get_checkout_ref()
        except ValueError as e:
            reason = f"Could not determine checkout ref: {e}"
            print(f"\n⏭️  Skipping: {reason}")
            gh.write_output("skip", "true")
            gh.write_output("skip_reason", reason)
            return 0

        try:
            base_branch = context.get_default_base_branch()
        except ValueError:
            base_branch = default_base_branch

        # Output results
        print(f"\n✓ Event parsing complete")
        print(f"  Skip: false")
        print(f"  Project: {resolved_project}")
        print(f"  Checkout ref: {checkout_ref}")
        print(f"  Base branch: {base_branch}")

        gh.write_output("skip", "false")
        gh.write_output("project_name", resolved_project)
        gh.write_output("checkout_ref", checkout_ref)
        gh.write_output("base_branch", base_branch)

        # For pull_request events, also output the PR number
        if context.pr_number:
            print(f"  Merged PR number: {context.pr_number}")
            gh.write_output("merged_pr_number", str(context.pr_number))

        return 0

    except Exception as e:
        error_msg = f"Event parsing failed: {e}"
        print(f"\n❌ {error_msg}")
        gh.set_error(error_msg)
        return 1


def main() -> int:
    """Entry point for parse-event command.

    Reads parameters from environment variables:
        EVENT_NAME: GitHub event name
        EVENT_JSON: GitHub event JSON payload
        PROJECT_NAME: Optional project name override
        DEFAULT_BASE_BRANCH: Default base branch (default: "main")
        PR_LABEL: Required label for PR events (default: "claudestep")
    """
    gh = GitHubActionsHelper()

    event_name = os.environ.get("EVENT_NAME", "")
    event_json = os.environ.get("EVENT_JSON", "{}")
    project_name = os.environ.get("PROJECT_NAME", "") or None
    default_base_branch = os.environ.get("DEFAULT_BASE_BRANCH", "main")
    pr_label = os.environ.get("PR_LABEL", "claudestep")

    return cmd_parse_event(
        gh=gh,
        event_name=event_name,
        event_json=event_json,
        project_name=project_name,
        default_base_branch=default_base_branch,
        pr_label=pr_label,
    )


if __name__ == "__main__":
    import sys
    sys.exit(main())
