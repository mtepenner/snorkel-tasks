import os
import sqlite3
import json
import time
import re
import requests
import subprocess
import shutil
from pathlib import Path

class TestMilestone1:
    @classmethod
    def setup_class(cls):
        # Guarantee clean state
        shutil.rmtree("/app/workspace/data", ignore_errors=True)
        os.makedirs("/app/workspace/data/input", exist_ok=True)
        
        with open("/app/workspace/data/input/test.csv", "w") as f:
            f.write("col1,col2,col3\nval1,val2,val3\n")
        with open("/app/workspace/data/input/test_2.csv", "w") as f:
            f.write("col1,col2,col3\nval4,val5,val6\n")
            
        cls.proc = subprocess.Popen(["python3", "/app/workspace/src/app.py"])
        
        for _ in range(20):
            try:
                requests.get("http://127.0.0.1:5000/logs", timeout=1)
                break
            except requests.exceptions.ConnectionError:
                time.sleep(0.5)

        resp = requests.post("http://127.0.0.1:5000/trigger")
        assert resp.status_code == 200

    @classmethod
    def teardown_class(cls):
        cls.proc.terminate()

    def test_flask_host_port(self):
        """Verify Flask binds to 0.0.0.0:5000."""
        content = Path("/app/workspace/src/app.py").read_text()
        assert "0.0.0.0" in content, "Host 0.0.0.0 not found in app.py"
        assert "5000" in content, "Port 5000 not found in app.py"

    def test_trigger_etl_all_columns(self):
        """POST /trigger parses all CSVs, preserves all columns, and aggregates records."""
        resp = requests.post("http://127.0.0.1:5000/trigger")
        assert resp.status_code == 200
        
        output = Path("/app/workspace/data/output.json")
        assert output.exists()
        data = json.loads(output.read_text())
        assert len(data) == 2, "Expected the combined output to include rows from every CSV in /app/workspace/data/input/"
        assert any("col1" in row and "col2" in row and "col3" in row for row in data), "Did not preserve all CSV columns"
        values = {(row["col1"], row["col2"], row["col3"]) for row in data}
        assert ("val1", "val2", "val3") in values
        assert ("val4", "val5", "val6") in values

    def test_db_schema_and_inserts(self):
        """Verify exact SQLite schema and row insertion."""
        conn = sqlite3.connect("/app/workspace/data/etl.db")
        c = conn.cursor()
        
        c.execute("PRAGMA table_info(records)")
        columns = {row[1]: row[2] for row in c.fetchall()}
        assert "id" in columns and "INTEGER" in columns["id"].upper()
        assert "data" in columns and "TEXT" in columns["data"].upper()
        
        c.execute("SELECT data FROM records")
        rows = [json.loads(r[0]) for r in c.fetchall()]
        assert any("col3" in r for r in rows), "Did not find expected test data in records"
        conn.close()

    def test_logs_endpoint(self):
        """GET /logs returns the current etl.log contents."""
        resp = requests.get("http://127.0.0.1:5000/logs")
        assert resp.status_code == 200
        log_content = Path("/app/workspace/data/etl.log").read_text()
        assert resp.text == log_content

    def test_download_endpoint(self):
        """GET /download returns the generated output.json content."""
        resp = requests.get("http://127.0.0.1:5000/download")
        assert resp.status_code == 200
        expected = json.loads(Path("/app/workspace/data/output.json").read_text())
        assert json.loads(resp.text) == expected

    def test_etl_log_appended(self):
        """ETL run appends a timestamped success or error entry to etl.log."""
        log = Path("/app/workspace/data/etl.log")
        assert log.exists()
        text = log.read_text().strip()
        assert len(text) > 0
        assert re.search(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}", text), "No timestamp found in etl.log"
        assert re.search(r"(?i)success|error", text), "No success/error status found in etl.log"
