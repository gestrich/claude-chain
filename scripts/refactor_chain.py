#!/usr/bin/env python3
"""
ClaudeStep - GitHub Actions Helper Script

This script coordinates automated refactoring workflows by delegating to
modular components in the lib package.
"""

import argparse
import sys

from lib.commands.finalize import cmd_finalize
from lib.commands.prepare import cmd_prepare
from lib.github_actions import GitHubActionsHelper


def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(
        description="ClaudeStep - GitHub Actions Helper Script"
    )
    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    # Consolidated commands
    parser_prepare = subparsers.add_parser("prepare", help="Prepare everything for Claude Code execution")
    parser_finalize = subparsers.add_parser("finalize", help="Finalize after Claude Code execution (commit, PR, summary)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Initialize GitHub Actions helper
    gh = GitHubActionsHelper()

    # Route to appropriate command handler
    if args.command == "prepare":
        return cmd_prepare(args, gh)
    elif args.command == "finalize":
        return cmd_finalize(args, gh)
    else:
        gh.set_error(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
