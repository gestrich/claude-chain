#!/bin/bash

# End-to-End Test Runner for ClaudeStep
#
# This script triggers the E2E integration tests for ClaudeStep remotely on GitHub.
# All test execution happens on GitHub's infrastructure, avoiding local git mutations.
#
# Prerequisites:
# - GitHub CLI (gh) installed and authenticated
# - Repository write access
# - ANTHROPIC_API_KEY configured as a repository secret
#
# Usage:
#   ./tests/e2e/run_test.sh
#
# The script will:
# - Trigger the e2e-test.yml workflow on GitHub
# - Run tests remotely using the current branch's code
# - Report the workflow run ID for tracking

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "ClaudeStep E2E Test Runner"
echo "========================================"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}ERROR: GitHub CLI (gh) is not installed${NC}"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi
echo -e "${GREEN}✓${NC} GitHub CLI (gh) is installed"

# Check if gh is authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}ERROR: GitHub CLI is not authenticated${NC}"
    echo "Run: gh auth login"
    exit 1
fi
echo -e "${GREEN}✓${NC} GitHub CLI is authenticated"

# Get current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo -e "${GREEN}✓${NC} Current branch: ${CURRENT_BRANCH}"

# Trigger the workflow
echo ""
echo "========================================"
echo "Triggering E2E Tests on GitHub"
echo "========================================"
echo ""
echo "Branch: ${CURRENT_BRANCH}"
echo "Workflow: e2e-test.yml"
echo ""

# Trigger the e2e-test.yml workflow on the current branch
echo "Triggering workflow..."
gh workflow run e2e-test.yml --ref "${CURRENT_BRANCH}"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓${NC} Workflow triggered successfully!"
    echo ""
    echo "The E2E tests are now running remotely on GitHub."
    echo "Your local git state will not be affected."
    echo ""
    echo "To view the workflow run:"
    echo "  gh run list --workflow=e2e-test.yml"
    echo "  gh run view <run-id>"
    echo ""
    echo "Or visit: https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/actions/workflows/e2e-test.yml"
    echo ""
    exit 0
else
    echo ""
    echo -e "${RED}✗${NC} Failed to trigger workflow"
    echo ""
    exit 1
fi
