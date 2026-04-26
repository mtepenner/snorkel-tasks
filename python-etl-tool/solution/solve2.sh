#!/bin/bash
set -euo pipefail
# Oracle solution for milestone 2

cat << 'EOF' > /app/workspace/src/templates/index.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ETL Dashboard</title>
    <script>
        async function triggerETL() {
            const btn = document.getElementById('triggerBtn');
            btn.disabled = true;
            btn.innerText = "Processing...";
            
            const response = await fetch('/trigger', { method: 'POST' });
            const result = await response.json();
            
            btn.disabled = false;
            btn.innerText = "Trigger Processing";
            loadLogs();
        }

        async function loadLogs() {
            const response = await fetch('/logs');
            const text = await response.text();
            document.getElementById('logs').innerText = text;
        }
        
        window.onload = loadLogs;
    </script>
</head>
<body>
    <h1>Data Dashboard</h1>
    <button id="triggerBtn" onclick="triggerETL()">Trigger Processing</button>
    <a href="/download"><button>Download JSON</button></a>
    
    <h2>Logs</h2>
    <button onclick="loadLogs()">Refresh Logs</button>
    <pre id="logs"></pre>
</body>
</html>
EOF

sed -i "/if __name__ == '__main__':/i \\
@app.route('/')\\
def index():\\
    return render_template('index.html')\\
" /app/workspace/src/app.py