from pathlib import Path

class TestMilestone2:
    def test_html_endpoints_and_logic(self):
        """Verify index.html contains correct endpoints, fetch calls, and disable logic."""
        content = Path("/app/workspace/src/templates/index.html").read_text()
        
        assert "/trigger" in content, "Missing /trigger endpoint in UI"
        assert "/logs" in content, "Missing /logs endpoint in UI"
        assert "/download" in content, "Missing /download endpoint in UI"
        
        assert "fetch" in content, "Missing fetch() API calls"
        assert "disabled" in content or ".disabled = true" in content, "Missing button disable logic"