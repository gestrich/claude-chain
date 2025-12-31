# Guide for Claude Code

## Before Starting Any Tasks

**Important:** Before working on tasks in this project, please read the following documents once to understand the project structure, workflows, and conventions:

1. **README.md** - Understand what ClaudeStep is, how it works, and how users interact with it
2. **docs/README.md** - Navigate the documentation structure
3. **docs/feature-guides/** - User-facing guides for ClaudeStep features
4. **docs/feature-architecture/** - Technical documentation for specific features
5. **docs/general-architecture/** - General design patterns and coding conventions:
   - Testing philosophy and requirements
   - Service layer pattern
   - Domain model design
   - Python style guide

This context is crucial for making changes that align with the project's design and user expectations.

## Project Overview

ClaudeStep is a GitHub Action that automates code refactoring using AI. It:
- Reads task lists from spec.md files
- Creates incremental PRs for each task
- Manages reviewer assignments and capacity
- Tracks progress automatically

Understanding how users interact with this system will help ensure any changes maintain backward compatibility and improve the user experience.
