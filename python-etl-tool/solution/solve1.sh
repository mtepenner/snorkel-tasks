#!/bin/bash
# Oracle solution for milestone 1

mkdir -p /app/workspace/src/templates
mkdir -p /app/workspace/data/input

cat << 'EOF' > /app/workspace/src/app.py
from flask import Flask, render_template, jsonify, send_file
import os
import csv
import json
import sqlite3
import datetime

app = Flask(__name__)

# Constants
BASE_DIR = '/app/workspace'
DATA_DIR = os.path.join(BASE_DIR, 'data')
INPUT_DIR = os.path.join(DATA_DIR, 'input')
DB_PATH = os.path.join(DATA_DIR, 'etl.db')
LOG_FILE = os.path.join(DATA_DIR, 'etl.log')
OUTPUT_FILE = os.path.join(DATA_DIR, 'output.json')

def init_db():
    os.makedirs(INPUT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY, data TEXT)''')
    conn.commit()
    conn.close()

def log_event(msg):
    with open(LOG_FILE, 'a') as f:
        f.write(f"{datetime.datetime.now()}: {msg}\n")

@app.route('/trigger', methods=['POST'])
def trigger_etl():
    try:
        init_db()
        all_data = []
        for filename in os.listdir(INPUT_DIR):
            if filename.endswith('.csv'):
                with open(os.path.join(INPUT_DIR, filename), 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        all_data.append(row)
        
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(all_data, f)
            
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        for row in all_data:
            c.execute("INSERT INTO records (data) VALUES (?)", (json.dumps(row),))
        conn.commit()
        conn.close()
        log_event("Success")
        return jsonify({"status": "success"})
    except Exception as e:
        log_event(f"Error: {str(e)}")
        return jsonify({"status": "error"}), 500

@app.route('/logs', methods=['GET'])
def get_logs():
    return open(LOG_FILE, 'r').read() if os.path.exists(LOG_FILE) else ""

@app.route('/download', methods=['GET'])
def download():
    if os.path.exists(OUTPUT_FILE):
        return send_file(OUTPUT_FILE)
    else:
        return "Not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF