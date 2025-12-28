"""Benchmark tests for parsing and string operations

These benchmarks track the performance of critical parsing operations
to detect performance regressions over time.
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from claudestep.domain.config import load_config, substitute_template, validate_spec_format
from claudestep.application.services.pr_operations import parse_branch_name, format_branch_name
from claudestep.application.services.artifact_operations import parse_task_index_from_name


class TestConfigParsing:
    """Benchmark configuration file parsing"""

    @pytest.fixture
    def sample_config(self, tmp_path):
        """Create a sample config file"""
        config_data = {
            "project": "test-project",
            "specFile": "spec.md",
            "reviewers": [
                {"username": "alice", "maxPRs": 3},
                {"username": "bob", "maxPRs": 2},
                {"username": "charlie", "maxPRs": 1},
            ],
            "labels": ["claudestep", "automated"],
        }
        config_file = tmp_path / "config.yml"
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)
        return str(config_file)

    def test_load_config_benchmark(self, benchmark, sample_config):
        """Benchmark loading a YAML config file"""
        result = benchmark(load_config, sample_config)
        assert result["project"] == "test-project"


class TestSpecValidation:
    """Benchmark spec.md file validation"""

    @pytest.fixture
    def sample_spec(self, tmp_path):
        """Create a sample spec.md file"""
        spec_file = tmp_path / "spec.md"
        spec_content = """# Refactoring Tasks

## Phase 1
- [ ] Task 1: Update authentication
- [ ] Task 2: Refactor database layer
- [x] Task 3: Add logging (completed)

## Phase 2
- [ ] Task 4: Improve error handling
- [ ] Task 5: Add metrics collection
"""
        spec_file.write_text(spec_content)
        return str(spec_file)

    def test_validate_spec_format_benchmark(self, benchmark, sample_spec):
        """Benchmark validating spec.md format"""
        result = benchmark(validate_spec_format, sample_spec)
        assert result is True


class TestTemplateSubstitution:
    """Benchmark template string substitution"""

    def test_simple_substitution(self, benchmark):
        """Benchmark simple template substitution"""
        template = "Project: {{project}}, Task: {{task}}"
        result = benchmark(substitute_template, template, project="test", task="1")
        assert result == "Project: test, Task: 1"

    def test_complex_substitution(self, benchmark):
        """Benchmark complex template with multiple variables"""
        template = """
        Project: {{project}}
        Task Index: {{index}}
        Branch: {{branch}}
        PR Title: {{title}}
        Description: {{description}}
        Reviewer: {{reviewer}}
        """
        result = benchmark(
            substitute_template,
            template,
            project="my-refactor",
            index="5",
            branch="claude-step-my-refactor-5",
            title="Task 5: Update authentication",
            description="This task updates the auth system",
            reviewer="alice",
        )
        assert "my-refactor" in result
        assert "alice" in result


class TestBranchNameOperations:
    """Benchmark branch name parsing and formatting"""

    def test_format_branch_name(self, benchmark):
        """Benchmark branch name formatting"""
        result = benchmark(format_branch_name, "my-refactor", 42)
        assert result == "claude-step-my-refactor-42"

    def test_parse_branch_name(self, benchmark):
        """Benchmark branch name parsing"""
        result = benchmark(parse_branch_name, "claude-step-my-refactor-42")
        assert result == ("my-refactor", 42)

    def test_parse_complex_branch_name(self, benchmark):
        """Benchmark parsing branch names with hyphens"""
        result = benchmark(
            parse_branch_name, "claude-step-swift-ios-migration-phase-2-99"
        )
        assert result == ("swift-ios-migration-phase-2", 99)


class TestArtifactParsing:
    """Benchmark artifact name parsing"""

    def test_parse_artifact_name(self, benchmark):
        """Benchmark parsing task index from artifact name"""
        result = benchmark(parse_task_index_from_name, "task-metadata-myproject-42.json")
        assert result == 42

    def test_parse_artifact_name_with_prefix(self, benchmark):
        """Benchmark parsing artifact name with project prefix"""
        result = benchmark(
            parse_task_index_from_name, "task-metadata-myproject-15.json"
        )
        assert result == 15


class TestLargeConfigFile:
    """Benchmark parsing larger config files"""

    @pytest.fixture
    def large_config(self, tmp_path):
        """Create a large config file with many reviewers"""
        config_data = {
            "project": "large-project",
            "specFile": "spec.md",
            "reviewers": [
                {"username": f"user{i}", "maxPRs": i % 5 + 1} for i in range(50)
            ],
            "labels": ["claudestep", "automated", "refactoring"],
            "metadata": {
                f"field{i}": f"value{i}" for i in range(100)
            },
        }
        config_file = tmp_path / "large_config.yml"
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)
        return str(config_file)

    def test_load_large_config(self, benchmark, large_config):
        """Benchmark loading a large config file"""
        result = benchmark(load_config, large_config)
        assert len(result["reviewers"]) == 50
        assert len(result["metadata"]) == 100


class TestLargeSpecFile:
    """Benchmark validating large spec files"""

    @pytest.fixture
    def large_spec(self, tmp_path):
        """Create a large spec.md file with many tasks"""
        spec_file = tmp_path / "large_spec.md"
        lines = ["# Large Refactoring Project\n\n"]
        for phase in range(10):
            lines.append(f"## Phase {phase + 1}\n\n")
            for task in range(20):
                task_num = phase * 20 + task + 1
                status = "x" if task_num % 3 == 0 else " "
                lines.append(
                    f"- [{status}] Task {task_num}: Refactor component {task_num}\n"
                )
            lines.append("\n")
        spec_file.write_text("".join(lines))
        return str(spec_file)

    def test_validate_large_spec(self, benchmark, large_spec):
        """Benchmark validating a large spec file"""
        result = benchmark(validate_spec_format, large_spec)
        assert result is True
