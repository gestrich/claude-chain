# Guide for Claude Code

## Before Starting Any Tasks

**Important:** Before working on tasks in this project, please read the following documents once to understand the project structure, workflows, and conventions:

1. **README.md** - Understand what ClaudeStep is, how it works, and how users interact with it
2. **docs/architecture/** - Review all architecture documentation to understand:
   - How the system is designed
   - Testing approaches and requirements
   - Technical implementation details

This context is crucial for making changes that align with the project's design and user expectations.

## Project Overview

ClaudeStep is a GitHub Action that automates code refactoring using AI. It:
- Reads task lists from spec.md files
- Creates incremental PRs for each task
- Manages reviewer assignments and capacity
- Tracks progress automatically

Understanding how users interact with this system will help ensure any changes maintain backward compatibility and improve the user experience.
