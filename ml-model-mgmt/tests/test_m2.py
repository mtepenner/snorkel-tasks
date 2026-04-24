import os

def test_m2_ui_files_exist():
    """1 pt: drop the main html into /app/workspace/src/templates/index.html."""
    assert os.path.exists('/app/workspace/src/templates/index.html'), "index.html missing"

def test_m2_ui_content():
    """1 pt: build a basic dashboard layout with config form and chart area."""
    with open('/app/workspace/src/templates/index.html', 'r') as f:
        content = f.read().lower()
    assert '<select' in content or '<input' in content, "Missing configuration form"
    assert 'chart' in content or '<canvas' in content or '<svg' in content, "Missing chart area"
