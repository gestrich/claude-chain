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

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}✗${NC} Failed to trigger workflow"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓${NC} Workflow triggered successfully!"
echo ""

# Wait a moment for the workflow run to be created
echo "Waiting for workflow run to start..."
sleep 5

# Get the most recent workflow run ID for this workflow and branch
RUN_ID=$(gh run list --workflow=e2e-test.yml --branch="${CURRENT_BRANCH}" --limit=1 --json databaseId --jq '.[0].databaseId')

if [ -z "$RUN_ID" ]; then
    echo -e "${YELLOW}Warning: Could not find workflow run ID${NC}"
    echo "The workflow may be queued. You can monitor it manually:"
    echo "  gh run list --workflow=e2e-test.yml"
    echo ""
    echo "Or visit: https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/actions/workflows/e2e-test.yml"
    echo ""
    exit 0
fi

echo "Workflow run ID: ${RUN_ID}"
echo ""
echo "========================================"
echo "Monitoring Workflow Execution"
echo "========================================"
echo ""
echo "Streaming logs from GitHub Actions..."
echo "Press Ctrl+C to stop monitoring (workflow will continue running)"
echo ""

# Watch the workflow run and stream logs
# The --exit-status flag makes gh run watch exit with the workflow's exit code
gh run watch "${RUN_ID}" --exit-status

WORKFLOW_EXIT_CODE=$?

echo ""
echo "========================================"
echo "Workflow Execution Complete"
echo "========================================"
echo ""

if [ $WORKFLOW_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ E2E Tests PASSED${NC}"
    echo ""
    echo "View detailed logs:"
    echo "  gh run view ${RUN_ID}"
    echo ""
    exit 0
else
    echo -e "${RED}✗ E2E Tests FAILED${NC}"
    echo ""
    echo "View detailed logs and errors:"
    echo "  gh run view ${RUN_ID}"
    echo ""
    echo "Or visit: https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/actions/runs/${RUN_ID}"
    echo ""
    exit 1
fi
