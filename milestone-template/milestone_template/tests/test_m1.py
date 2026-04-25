"""Tests for milestone 1. Run this file alone to verify only milestone 1: pytest tests/test_m1.py"""

from pathlib import Path


class TestMilestone1:
    """Tests for milestone 1: Description of milestone 1."""

    def test_milestone_1_requirement_one(self) -> None:
        """First requirement for milestone 1."""
        # Replace with real assertions for milestone 1
        hello_path = Path("/app/hello.txt")
        assert hello_path.exists(), f"File {hello_path} does not exist"

    def test_milestone_1_requirement_two(self) -> None:
        """Second requirement for milestone 1 (add or remove as needed)."""
        hello_path = Path("/app/hello.txt")
        assert hello_path.read_text().strip() == "Hello, world!", (
            f"Expected 'Hello, world!' but got '{hello_path.read_text().strip()}'"
        )
