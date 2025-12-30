# Metadata Synchronization Command

## Background

ClaudeStep follows a **metadata-first architecture** where the metadata configuration (`.claudestep/metadata.json`) serves as the single source of truth for all statistics and reporting. This metadata is kept up-to-date through merge triggers and workflow runs that automatically record PR information when tasks are finalized.

However, PRs can be modified outside the normal ClaudeStep workflow:
- Manual merges or closes via GitHub UI
- Direct git operations
- Bulk operations by administrators
- Historical PRs created before ClaudeStep adoption

When these actions occur, the metadata can drift from GitHub's actual state. The **synchronize command** will enable metadata validation, drift detection, and automatic correction by querying GitHub's API and comparing against stored metadata.

The infrastructure for GitHub PR queries already exists in `src/claudestep/infrastructure/github/operations.py` but is currently dormant, waiting for this synchronization feature to activate it. This proposal covers both the synchronization command itself and enhancements to the GitHub query operations that will power it.

## Phases

### Part A: GitHub PR Query Operations

These phases enhance the GitHub query infrastructure in `operations.py` to support robust synchronization.

- [ ] Phase 1: Add PR detail queries

Extend GitHub operations to fetch detailed information for individual PRs:
- PR comments and review threads
- PR check statuses and CI results
- PR file changes and diff statistics
- PR timeline events (labeled, assigned, etc.)

Files to modify:
- `src/claudestep/infrastructure/github/operations.py` - Add `get_pull_request_details()`
- `src/claudestep/domain/github_models.py` - Extend `GitHubPullRequest` with detail fields
- Add factory methods for parsing detailed PR JSON

Technical considerations:
- Use GitHub CLI's `gh pr view --json` with comprehensive field list
- Maintain type safety with domain model extensions
- Parse nested JSON structures (comments, reviews, checks)
- Handle PRs with large numbers of comments/files efficiently

Expected outcome: Ability to fetch complete PR information beyond basic metadata

- [ ] Phase 2: Implement caching layer

Add intelligent caching to reduce GitHub API calls and improve performance:
- Cache PR lists with TTL (time-to-live)
- Cache individual PR details
- Cache invalidation on known changes
- Respect GitHub rate limits

Files to create:
- `src/claudestep/infrastructure/github/cache.py` - Caching implementation
- Configuration for cache TTL and size limits

Files to modify:
- `operations.py` - Integrate caching into query functions
- Add cache statistics and monitoring

Technical considerations:
- Use in-memory cache with LRU eviction
- Store parsed domain models, not raw JSON
- Include cache-control headers from GitHub API
- Provide cache bypass option for synchronize command

Expected outcome: Faster queries with reduced API usage

- [ ] Phase 3: Add batch query operations

Implement efficient batch queries for multiple PRs:
- Fetch multiple PRs by number in single operation
- Parallel queries with controlled concurrency
- Aggregate results into cohesive response
- Progress reporting for large batches

Files to modify:
- `operations.py` - Add `get_pull_requests_batch(pr_numbers: List[int])`
- Implement concurrent query execution with thread pool
- Add rate limit awareness to prevent exhaustion

Technical considerations:
- Use `concurrent.futures` for parallel execution
- Respect GitHub rate limits (max 5000 requests/hour)
- Handle partial failures gracefully (some PRs succeed, others fail)
- Return results as soon as available (streaming)

Expected outcome: Efficient bulk PR queries for synchronization operations

- [ ] Phase 4: Enhanced filtering and search

Extend filtering capabilities beyond basic state and label:
- Filter by date ranges (created, updated, merged, closed)
- Filter by author, reviewer, assignee
- Full-text search in PR titles and bodies
- Combine multiple filter criteria

Files to modify:
- `operations.py` - Extend `list_pull_requests()` with additional filter parameters
- Add GitHub CLI search query construction
- Parse and validate filter combinations

Technical considerations:
- Use GitHub's search syntax for complex queries
- Validate filter combinations are supported by GitHub
- Handle search result pagination
- Return empty results gracefully when no matches

Expected outcome: Powerful PR discovery for audit and backfill operations

- [ ] Phase 5: Rate limit management

Implement comprehensive rate limit handling:
- Check current rate limit status before queries
- Automatic backoff when approaching limits
- Queue requests when limit exceeded
- Inform users of rate limit status

Files to create:
- `src/claudestep/infrastructure/github/rate_limiter.py`

Files to modify:
- `operations.py` - Integrate rate limiter into all GitHub calls
- Add rate limit status to error messages

Technical considerations:
- Use `gh api rate_limit` to check current status
- Implement exponential backoff with jitter
- Respect rate limit reset timestamps
- Provide user feedback during rate limit waits
- Allow configuration of rate limit thresholds

Expected outcome: Reliable GitHub operations that never hit rate limits unexpectedly

- [ ] Phase 6: GitHub error handling and retries

Add sophisticated error handling for GitHub API operations:
- Distinguish transient vs permanent failures
- Automatic retries with exponential backoff
- Network timeout handling
- Graceful degradation on GitHub outages

Files to modify:
- `operations.py` - Wrap all GitHub calls with retry logic
- `src/claudestep/domain/exceptions.py` - Add GitHub-specific exception types

Technical considerations:
- Retry on 502, 503, 504 HTTP errors
- Don't retry on 401, 403, 404 (permanent failures)
- Use exponential backoff: 1s, 2s, 4s, 8s delays
- Log retry attempts for debugging
- Provide clear error messages with resolution guidance

Expected outcome: Robust GitHub operations that handle transient failures automatically

- [ ] Phase 7: Query result pagination

Implement proper pagination for large result sets:
- Handle GitHub's 100-item page limit
- Automatic page fetching with streaming results
- Configurable page size
- Total result count estimation

Files to modify:
- `operations.py` - Add pagination support to `list_pull_requests()`
- Yield results incrementally for memory efficiency
- Add `max_results` parameter to limit total items

Technical considerations:
- Use GitHub CLI's `--limit` parameter
- Detect when more pages are available
- Stream results to avoid loading thousands of PRs in memory
- Provide progress feedback for multi-page queries

Expected outcome: Efficient handling of repositories with hundreds/thousands of PRs

### Part B: Synchronization Command

These phases build the synchronization command that uses the enhanced GitHub query operations.

- [ ] Phase 8: Add synchronize command CLI interface

Create the command-line interface for the synchronize command with options:
- `--project <name>` - Synchronize specific project (default: all projects)
- `--dry-run` - Show what would be changed without modifying metadata
- `--backfill` - Import historical PRs not currently in metadata
- `--report` - Generate drift report without corrections

Files to modify:
- `src/claudestep/cli/commands/` - Add new `synchronize.py` command module
- `src/claudestep/cli/main.py` - Register synchronize command
- Update CLI documentation

Expected outcome: Users can invoke `claudestep synchronize` with appropriate flags

- [ ] Phase 9: Implement PR comparison logic

Create comparison service that detects differences between GitHub state and metadata:
- Missing PRs (in GitHub but not in metadata)
- Phantom PRs (in metadata but not in GitHub)
- Status mismatches (merged vs open)
- Metadata field differences (title, reviewer, timestamps)

Files to modify:
- Create `src/claudestep/application/services/sync_service.py`
- Define comparison result models in `src/claudestep/domain/models.py`
- Add drift detection algorithms

Technical considerations:
- Use existing `GitHubPullRequest` domain model from `github_models.py`
- Leverage `list_pull_requests()` function from `operations.py`
- Filter PRs by ClaudeStep label to identify relevant PRs
- Return structured comparison reports with actionable differences

Expected outcome: Service that can identify all discrepancies between GitHub and metadata

- [ ] Phase 10: Implement metadata update operations

Add functionality to update metadata based on GitHub state:
- Backfill missing PR entries
- Mark PRs as merged/closed when GitHub shows them merged/closed
- Update PR titles, reviewers, timestamps from GitHub
- Handle edge cases (duplicate PRs, invalid states)

Files to modify:
- Extend `src/claudestep/application/services/metadata_service.py` with update methods
- Add validation to prevent data corruption
- Implement atomic updates with rollback capability

Technical considerations:
- Preserve existing metadata that shouldn't be overwritten
- Maintain audit trail of synchronization changes
- Validate all changes before committing to storage
- Handle concurrent access safely

Expected outcome: Safe, reliable metadata updates based on GitHub truth

- [ ] Phase 11: Add drift reporting

Create human-readable reports showing metadata drift:
- Summary statistics (X PRs missing, Y status mismatches)
- Detailed line-by-line differences
- Recommendations for resolution
- Export formats (console, JSON, markdown)

Files to create:
- `src/claudestep/application/reporting/drift_report.py`

Technical considerations:
- Clear, actionable output for users
- Highlight critical vs minor discrepancies
- Support both interactive and CI/CD usage
- Include timestamps and PR links

Expected outcome: Informative reports that help users understand and fix drift

- [ ] Phase 12: Implement backfill mode

Add ability to import historical ClaudeStep PRs created before metadata tracking:
- Query GitHub for all PRs with ClaudeStep label
- Filter to PRs not already in metadata
- Prompt user for confirmation before bulk import
- Preserve original PR metadata (creation date, merge date, reviewer)

Files to modify:
- Extend `src/claudestep/application/services/sync_service.py`
- Add interactive confirmation prompts
- Handle rate limiting for large PR sets

Technical considerations:
- GitHub API rate limits (use pagination, respect limits)
- Distinguish ClaudeStep PRs from other PRs using labels
- Handle incomplete metadata gracefully (missing reviewers, etc.)
- Provide progress feedback for long-running operations

Expected outcome: Ability to populate metadata from existing GitHub PRs

- [ ] Phase 13: Add dry-run mode

Implement preview mode that shows what would change without modifying anything:
- Display all proposed changes
- Show before/after states
- Calculate impact summary
- Exit without modifications

Files to modify:
- Update `sync_service.py` to support simulation mode
- Add preview output formatting
- Ensure no side effects in dry-run mode

Expected outcome: Safe preview of synchronization operations

- [ ] Phase 14: Synchronization error handling and recovery

Add robust error handling for synchronization-specific scenarios:
- Corrupted metadata files
- Partial update failures
- Synchronization conflicts (concurrent updates)

Files to modify:
- Add exception types in `src/claudestep/domain/exceptions.py`
- Implement rollback capability for failed updates
- Log errors with actionable context

Technical considerations:
- Clear error messages with resolution steps
- Preserve metadata integrity even on partial failures
- Support resumable operations

Expected outcome: Reliable synchronization even with corrupted or conflicting data

- [ ] Phase 15: Integration and documentation

Integrate synchronize command into existing workflows and document usage:
- Add synchronize to recommended maintenance procedures
- Update architecture documentation
- Create user guide with examples
- Add troubleshooting section

Files to modify:
- `README.md` - Add synchronize command to usage section
- `docs/architecture/architecture.md` - Update future plans to current implementation
- Create `docs/guides/synchronization.md` with detailed examples

Expected outcome: Well-documented feature ready for user adoption

- [ ] Phase 16: Validation

Test the complete synchronization system end-to-end:

GitHub Operations Tests:
- Unit tests for query construction, JSON parsing, domain model creation
- Integration tests with mock GitHub CLI responses
- Rate limit simulation tests
- Pagination tests with large result sets
- Error handling tests (network failures, API errors, rate limits)
- Cache correctness tests (TTL, invalidation, bypass)
- Batch query tests (concurrency, partial failures)

Synchronization Command Tests:
- Unit tests for comparison logic, update operations, reporting
- Integration tests with mock GitHub API responses
- E2E tests simulating real drift scenarios (manual merges, missing PRs)
- Test dry-run mode produces no side effects
- Test backfill with various PR histories
- Verify rate limit handling
- Test error recovery and rollback

Run all tests:
```bash
# GitHub operations tests
pytest tests/unit/infrastructure/github/test_operations.py
pytest tests/integration/infrastructure/github/test_github_queries.py
pytest tests/unit/infrastructure/github/test_cache.py
pytest tests/unit/infrastructure/github/test_rate_limiter.py

# Synchronization command tests
pytest tests/unit/services/test_sync_service.py
pytest tests/integration/test_synchronize_command.py
pytest tests/e2e/test_synchronize_workflows.py
```

Success criteria:
- All tests pass
- Rate limiter prevents API limit exhaustion
- Caching reduces redundant API calls
- Batch queries handle 100+ PRs efficiently
- GitHub error handling gracefully manages failures
- Pagination works with repositories of any size
- Domain models maintain type safety
- Dry-run mode makes no modifications
- Backfill correctly imports historical PRs
- Drift detection catches all discrepancies
- Synchronization error handling prevents data corruption
- Documentation is complete and accurate
