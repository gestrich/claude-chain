"""Data models for ClaudeStep operations"""

from typing import Any, Dict, List, Optional


class ReviewerCapacityResult:
    """Result of reviewer capacity check with detailed information"""

    def __init__(self):
        self.reviewers_status = []  # List of dicts with reviewer details
        self.selected_reviewer = None
        self.all_at_capacity = False

    def add_reviewer(self, username: str, max_prs: int, open_prs: List[Dict], has_capacity: bool):
        """Add reviewer status information"""
        self.reviewers_status.append({
            "username": username,
            "max_prs": max_prs,
            "open_prs": open_prs,  # List of {pr_number, task_index, task_description}
            "open_count": len(open_prs),
            "has_capacity": has_capacity
        })

    def format_summary(self) -> str:
        """Generate formatted summary for GitHub Actions output"""
        lines = ["## Reviewer Capacity Check", ""]

        for reviewer in self.reviewers_status:
            username = reviewer["username"]
            max_prs = reviewer["max_prs"]
            open_count = reviewer["open_count"]
            open_prs = reviewer["open_prs"]
            has_capacity = reviewer["has_capacity"]

            # Reviewer header with status emoji
            status_emoji = "✅" if has_capacity else "❌"
            lines.append(f"### {status_emoji} **{username}**")
            lines.append("")

            # Capacity info
            lines.append(f"**Max PRs Allowed:** {max_prs}")
            lines.append(f"**Currently Open:** {open_count}/{max_prs}")
            lines.append("")

            # List open PRs with details
            if open_prs:
                lines.append("**Open PRs:**")
                for pr_info in open_prs:
                    pr_num = pr_info.get("pr_number", "?")
                    task_idx = pr_info.get("task_index", "?")
                    task_desc = pr_info.get("task_description", "Unknown task")
                    lines.append(f"- PR #{pr_num}: Task {task_idx} - {task_desc}")
                lines.append("")
            else:
                lines.append("**Open PRs:** None")
                lines.append("")

            # Availability status
            if has_capacity:
                available_slots = max_prs - open_count
                lines.append(f"**Status:** ✅ Available ({available_slots} slot(s) remaining)")
            else:
                lines.append(f"**Status:** ❌ At capacity")

            lines.append("")

        # Final decision
        lines.append("---")
        lines.append("")
        if self.selected_reviewer:
            lines.append(f"**Decision:** ✅ Selected **{self.selected_reviewer}** for next PR")
        else:
            lines.append(f"**Decision:** ❌ All reviewers at capacity - skipping PR creation")

        return "\n".join(lines)
