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

    def test_index_served_by_flask(self):
        """GET / returns 200 and Flask actually renders the index.html template."""
        resp = requests.get("http://127.0.0.1:5000/")
        assert resp.status_code == 200, "GET / did not return 200 — Flask route for index.html is missing"
        # Verify Flask serves real template content, not a blank or stub response.
        assert "/trigger" in resp.text, "Flask-served page is missing /trigger reference"
        assert "/download" in resp.text, "Flask-served page is missing /download reference"

    def test_trigger_button_and_post_method(self):
        """index.html has a button that sends a POST fetch to /trigger."""
        content = requests.get("http://127.0.0.1:5000/").text
        lowered = content.lower()
        assert "<button" in lowered, "Missing trigger button element"
        assert re.search(r"fetch\((['\"])\/trigger\1", content), "Missing fetch('/trigger') call"
        assert re.search(r"['\"]POST['\"]", content), "Missing POST method in /trigger fetch call"

    def test_button_disable_logic(self):
        """Button disables itself while /trigger is in flight and re-enables after."""
        content = requests.get("http://127.0.0.1:5000/").text
        # Strip JS single-line comments to avoid matching commented-out code.
        js_stripped = re.sub(r'//[^\n]*', '', content)
        assert re.search(
            r"\.disabled\s*=\s*true|\.setAttribute\s*\(\s*['\"]disabled['\"]",
            js_stripped
        ), "Missing button disable-while-running logic (must use .disabled = true or setAttribute)"
        assert re.search(
            r"\.disabled\s*=\s*false|\.removeAttribute\s*\(\s*['\"]disabled['\"]",
            js_stripped
        ), "Missing button re-enable logic (must use .disabled = false or removeAttribute)"

    def test_logs_fetched_on_page_load(self):
        """<pre> block fetches /logs on page load and populates the element."""
        content = requests.get("http://127.0.0.1:5000/").text
        lowered = content.lower()
        assert "<pre" in lowered, "Missing <pre> block for log display"
        assert "window.onload" in content or "DOMContentLoaded" in content, \
            "Missing window.onload or DOMContentLoaded handler for on-load log fetch"
        assert re.search(r"fetch\((['\"])\/logs\1", content), "Missing fetch('/logs') call"
        # Verify the fetch result is actually assigned to a DOM element (not silently discarded).
        assert re.search(
            r"\.(?:textContent|innerText|innerHTML)\s*=",
            content
        ), "Fetched /logs result does not appear to be assigned to any DOM element"

    def test_download_link(self):
        """index.html contains a standard anchor link to /download."""
        content = requests.get("http://127.0.0.1:5000/").text
        lowered = content.lower()
        assert re.search(r"<a[^>]+href=[\"']?/download[\"']?", lowered), \
            "Missing <a href='/download'> download link"
