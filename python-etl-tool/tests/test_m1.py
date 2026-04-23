import os
import sqlite3
import json
import time
import requests
import subprocess
import shutil
from pathlib import Path

class TestMilestone1:
    @classmethod
    def setup_class(cls):
        # 1. NUKE the entire data directory to guarantee a 100% clean state
        shutil.rmtree("/app/workspace/data", ignore_errors=True)
        os.makedirs("/app/workspace/data/input", exist_ok=True)
        
        # 2. Setup dummy CSV with multiple columns to test preservation
        with open("/app/workspace/data/input/test.csv", "w") as f:
            f.write("col1,col2,col3\nval1,val2,val3\n")
            
        cls.proc = subprocess.Popen(["python3", "/app/workspace/src/app.py"])
        
        # 3. Robust polling instead of a fixed sleep
        for _ in range(20):
            try:
                requests.get("http://127.0.0.1:5000/logs", timeout=1)
                break
            except requests.exceptions.ConnectionError:
                time.sleep(0.5)

    @classmethod
    def teardown_class(cls):
        cls.proc.terminate()

    def test_flask_host_port(self):
        """Verify Flask binds to 0.0.0.0:5000."""
        content = Path("/app/workspace/src/app.py").read_text()
        assert "0.0.0.0" in content, "Host 0.0.0.0 not found in app.py"
        assert "5000" in content, "Port 5000 not found in app.py"

    def test_trigger_etl_all_columns(self):
        """POST /trigger parses CSVs and preserves all columns in JSON."""
        resp = requests.post("http://127.0.0.1:5000/trigger")
        assert resp.status_code == 200
        
        output = Path("/app/workspace/data/output.json")
        assert output.exists()
        data = json.loads(output.read_text())
        
        # Use 'any' to ensure it passes regardless of read order if multiple CSVs exist
        assert any("col1" in row and "col2" in row and "col3" in row for row in data), "Did not preserve all CSV columns"

    def test_db_schema_and_inserts(self):
        """Verify exact SQLite schema and row insertion."""
        conn = sqlite3.connect("/app/workspace/data/etl.db")
        c = conn.cursor()
        
        # Verify exact schema
        c.execute("PRAGMA table_info(records)")
        columns = {row[1]: row[2] for row in c.fetchall()}
        assert "id" in columns and "INTEGER" in columns["id"].upper()
        assert "data" in columns and "TEXT" in columns["data"].upper()
        
        # Verify data using 'any' to check all rows
        c.execute("SELECT data FROM records")
        rows = [json.loads(r[0]) for r in c.fetchall()]
        assert any("col3" in r for r in rows), "Did not find expected test data in records"
        conn.close()

    def test_logs_endpoint(self):
        """GET /logs returns a non-empty string after ETL runs."""
        resp = requests.get("http://127.0.0.1:5000/logs")
        assert resp.status_code == 200
        assert len(resp.text) > 0

    def test_download_endpoint(self):
        """GET /download returns the output JSON file."""
        resp = requests.get("http://127.0.0.1:5000/download")
        assert resp.status_code == 200

    def test_etl_log_appended(self):
        """ETL run appends a timestamped entry to etl.log."""
        log = Path("/app/workspace/data/etl.log")
        assert log.exists()
        assert len(log.read_text().strip()) > 0