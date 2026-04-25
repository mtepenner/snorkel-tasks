import re
from pathlib import Path

class TestMilestone2:
    def test_html_endpoints_and_logic(self):
        """Verify index.html contains the required UI elements and endpoint wiring."""
        content = Path("/app/workspace/src/templates/index.html").read_text()
        lowered = content.lower()
        
        assert "/trigger" in content, "Missing /trigger endpoint in UI"
        assert "/logs" in content, "Missing /logs endpoint in UI"
        assert "/download" in content, "Missing /download endpoint in UI"
        
        assert "fetch" in content, "Missing fetch() API calls"
        assert "<pre" in lowered, "Missing <pre> block for log display"
        assert "<button" in lowered, "Missing trigger button"
        assert re.search(r"<a[^>]+href=[\"']?/download[\"']?", lowered), "Missing download link"
        assert re.search(r"fetch\((['\"])\/trigger\1", content), "Missing POST fetch to /trigger"
        assert re.search(r"fetch\((['\"])\/logs\1", content), "Missing fetch to /logs"
        assert "disabled = true" in content or ".disabled=true" in content.replace(" ", ""), "Missing button disable-while-running logic"
        assert "disabled = false" in content or ".disabled=false" in content.replace(" ", ""), "Missing button re-enable logic"
        assert "window.onload" in content or "DOMContentLoaded" in content, "Missing log fetch on page load"