# Performance Benchmarking Guide

This document describes how to run and add performance benchmarks to ClaudeStep.

## Overview

ClaudeStep uses `pytest-benchmark` to track the performance of critical code paths. Benchmarks help detect performance regressions and ensure the test suite remains fast as the codebase grows.

## Running Benchmarks

### Run All Benchmarks

```bash
# Run only benchmarks (skips regular tests)
pytest tests/benchmarks/ --benchmark-only

# Run benchmarks with detailed output
pytest tests/benchmarks/ --benchmark-only -v

# Run benchmarks without garbage collection interference
pytest tests/benchmarks/ --benchmark-only --benchmark-disable-gc
```

### Run Regular Tests and Benchmarks

```bash
# Run all tests including benchmarks
pytest

# Skip benchmarks during regular test runs
pytest --benchmark-skip
```

### Benchmark Results

Benchmark results show:
- **Min/Max/Mean/Median**: Execution times in nanoseconds (ns)
- **StdDev**: Standard deviation (lower is more consistent)
- **IQR**: Interquartile range (measure of variability)
- **OPS**: Operations per second (higher is better)
- **Outliers**: Number of outlier measurements

Example output:
```
Name (time in ns)                Min          Max         Mean      StdDev       Median
test_format_branch_name      76.2497    372.9190     81.5984    4.3421     81.2497
test_parse_branch_name      332.9478  2,249.9589    390.6799   31.8644    375.0902
```

## What Gets Benchmarked

Current benchmarks track performance of:

1. **Config Parsing** - Loading YAML configuration files
2. **Spec Validation** - Validating spec.md checklist format
3. **Template Substitution** - Variable substitution in templates
4. **Branch Operations** - Branch name parsing and formatting
5. **Artifact Parsing** - Extracting task indexes from artifact names
6. **Large File Operations** - Performance with larger config/spec files

## Adding New Benchmarks

### Benchmark Structure

Benchmarks follow the same structure as regular pytest tests but use the `benchmark` fixture:

```python
def test_my_operation(benchmark):
    """Benchmark description"""
    result = benchmark(function_to_test, arg1, arg2)
    assert result == expected_value
```

### Benchmark Guidelines

**DO benchmark:**
- Functions called frequently (in loops, on every PR)
- File I/O operations (parsing, validation)
- Regex-heavy operations (branch/artifact name parsing)
- String manipulation at scale
- Operations that could degrade with larger inputs

**DON'T benchmark:**
- One-time setup operations
- External API calls (mock these instead)
- Operations that are already mocked in tests
- Trivial getters/setters

### Example: Adding a Benchmark

```python
# tests/benchmarks/test_my_feature.py
import pytest
from claudestep.application.services.my_module import my_function

class TestMyFeature:
    """Benchmark my feature"""

    def test_my_function_small_input(self, benchmark):
        """Benchmark with small input"""
        result = benchmark(my_function, "small input")
        assert result is not None

    def test_my_function_large_input(self, benchmark):
        """Benchmark with large input"""
        large_input = "x" * 10000
        result = benchmark(my_function, large_input)
        assert result is not None
```

### Using Fixtures

Benchmarks can use pytest fixtures for setup:

```python
@pytest.fixture
def sample_data(self, tmp_path):
    """Create test data"""
    data_file = tmp_path / "data.txt"
    data_file.write_text("test content")
    return str(data_file)

def test_process_file(self, benchmark, sample_data):
    """Benchmark file processing"""
    result = benchmark(process_file, sample_data)
    assert result is not None
```

## Performance Baselines

Current performance baselines (as of 2025-12-27):

| Operation | Mean Time | OPS |
|-----------|-----------|-----|
| Format branch name | ~81 ns | 12.2M ops/sec |
| Parse branch name | ~391 ns | 2.5M ops/sec |
| Simple template substitution | ~361 ns | 2.7M ops/sec |
| Parse artifact name | ~355 ns | 2.8M ops/sec |
| Validate spec format | ~15.6 μs | 64K ops/sec |
| Load YAML config | ~281 μs | 3.5K ops/sec |
| Load large config (50 reviewers) | ~4.6 ms | 216 ops/sec |

## CI Integration

Benchmarks run in CI on every commit to track performance over time. The workflow:

1. Benchmarks run as part of the test suite
2. Results are stored for comparison
3. Significant regressions trigger warnings (future enhancement)

## Performance Thresholds

While we don't currently enforce strict performance thresholds, the general guidelines are:

- **String operations**: < 1 μs
- **File parsing (small files)**: < 500 μs
- **File parsing (large files)**: < 10 ms
- **Overall test suite**: < 2 seconds for 500+ tests

If any operation consistently exceeds these thresholds, consider optimization.

## Troubleshooting

### High Variance in Results

If benchmarks show high variance (large StdDev):
1. Close unnecessary applications
2. Run with `--benchmark-disable-gc` to disable garbage collection
3. Increase warmup iterations: `--benchmark-warmup=on`
4. Run on a less loaded system

### Benchmarks Too Slow

If benchmarks take too long:
1. Use `--benchmark-only` to skip regular tests
2. Reduce the number of rounds with `--benchmark-min-rounds=1`
3. Set time limits with `--benchmark-max-time=1.0`

### Comparing Performance

To compare before/after performance:
```bash
# Save baseline
pytest tests/benchmarks/ --benchmark-only --benchmark-save=before

# Make changes...

# Compare against baseline
pytest tests/benchmarks/ --benchmark-only --benchmark-compare=before
```

## References

- [pytest-benchmark documentation](https://pytest-benchmark.readthedocs.io/)
- Test suite: `tests/benchmarks/`
- Existing benchmarks: `tests/benchmarks/test_parsing_performance.py`
