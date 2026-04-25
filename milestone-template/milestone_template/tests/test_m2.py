"""Tests for milestone 2. Run this file alone to verify only milestone 2: pytest tests/test_m2.py"""

from pathlib import Path


class TestMilestone2:
    """Tests for milestone 2: Description of milestone 2."""

    def test_milestone_2_requirement_one(self) -> None:
        """First requirement for milestone 2."""
        # Replace with real assertions for milestone 2
        # Example: assert that a second file or behavior exists
        output_dir = Path("/app")
        assert output_dir.is_dir(), f"Expected directory {output_dir}"

    def test_milestone_2_requirement_two(self) -> None:
        """Second requirement for milestone 2 (add or remove as needed)."""
        # Replace with real assertions for milestone 2
        pass
