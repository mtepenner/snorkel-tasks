import re
import time
import requests
import subprocess
from pathlib import Path

class TestMilestone2:
    @classmethod
    def setup_class(cls):
        # Kill any leftover server from milestone 1 and start a fresh one.
        subprocess.run(["sh", "-c", "lsof -t -i:5000 | xargs -r kill -9"], capture_output=True)
        time.sleep(0.3)
        cls.proc = subprocess.Popen(["python3", "/app/workspace/src/app.py"])
        for _ in range(20):
            try:
                requests.get("http://127.0.0.1:5000/", timeout=1)
                break
            except requests.exceptions.ConnectionError:
                time.sleep(0.5)

    @classmethod
    def teardown_class(cls):
        cls.proc.terminate()

    def test_html_endpoints_and_logic(self):
        """Verify index.html is served by Flask and contains the required UI elements and endpoint wiring."""
        # Verify the page is actually served via Flask, not just present on disk.
        resp = requests.get("http://127.0.0.1:5000/")
        assert resp.status_code == 200, "GET / did not return 200 — Flask route for index.html is missing"

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
        # Accept both .disabled = true/false and setAttribute('disabled', ...) patterns.
        assert re.search(
            r"disabled\s*=\s*true|\.setAttribute\s*\(\s*['\"]disabled['\"]",
            content
        ), "Missing button disable-while-running logic"
        assert re.search(
            r"disabled\s*=\s*false|\.removeAttribute\s*\(\s*['\"]disabled['\"]",
            content
        ), "Missing button re-enable logic"
        assert "window.onload" in content or "DOMContentLoaded" in content, "Missing log fetch on page load"