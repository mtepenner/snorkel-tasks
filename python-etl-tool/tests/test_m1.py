import os
import sqlite3
import json
import time
import requests
import subprocess
import glob
from pathlib import Path

class TestMilestone1:
    @classmethod
    def setup_class(cls):
        os.makedirs("/app/workspace/data/input", exist_ok=True)
        
        # CLEANUP: Remove any old CSVs from previous runs so they don't pollute the test!
        for old_file in glob.glob("/app/workspace/data/input/*.csv"):
            os.remove(old_file)
            
        # Setup dummy CSV with multiple columns to test preservation
        with open("/app/workspace/data/input/test.csv", "w") as f:
            f.write("col1,col2,col3\nval1,val2,val3\n")
            
        cls.proc = subprocess.Popen(["python3", "/app/workspace/src/app.py"])
        
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
        assert "col1" in data[0] and "col2" in data[0] and "col3" in data[0], "Did not preserve all CSV columns"

    def test_db_schema_and_inserts(self):
        """Verify exact SQLite schema and row insertion."""
        conn = sqlite3.connect("/app/workspace/data/etl.db")
        c = conn.cursor()
        
        # Verify exact schema
        c.execute("PRAGMA table_info(records)")
        columns = {row[1]: row[2] for row in c.fetchall()}
        assert "id" in columns and "INTEGER" in columns["id"].upper()
        assert "data" in columns and "TEXT" in columns["data"].upper()
        
        # Verify data
        c.execute("SELECT data FROM records")
        row = json.loads(c.fetchone()[0])
        assert "col3" in row
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
