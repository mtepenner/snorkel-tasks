"""Tests for milestone 2."""

from pathlib import Path

class TestMilestone2:
    """Tests for milestone 2: Frontend UI implementation."""

    def test_milestone_2_html_exists(self) -> None:
        """Verify the index.html file exists in the correct template path."""
        html_path = Path("/app/workspace/src/templates/index.html")
        assert html_path.exists(), f"File {html_path} does not exist"

    def test_milestone_2_html_contents(self) -> None:
        """Verify the HTML file contains the correct endpoints and logic."""
        html_path = Path("/app/workspace/src/templates/index.html")
        content = html_path.read_text().lower()
        
        # Verify fetch calls to endpoints exist
        assert "fetch('/trigger" in content or 'fetch("/trigger' in content, "Missing fetch call to /trigger endpoint"
        assert "fetch('/logs" in content or 'fetch("/logs' in content, "Missing fetch call to /logs endpoint"
        assert "/download" in content, "Missing link to /download endpoint"
        
        # Verify UI disable logic
        assert "disabled" in content, "Missing logic to temporarily disable the trigger button"